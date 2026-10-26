"""Read the official BRFSS HTML codebooks into Python objects.

Each codebook (USCODEyy_LLCP_*.HTML, from CDC's codebook zip) has one table per
variable: a header with the label, SAS variable name and question text, then one
row per answer code with its label, frequency, percentage and weighted percentage.
"""

import html
import re
from dataclasses import dataclass, field
from pathlib import Path

from ml.preprocessing.brfss_sources import DOCUMENTATION_DIR

CODEBOOK_DIR = DOCUMENTATION_DIR

_TAG = re.compile(r"<[^>]+>")
_ROW = re.compile(r"<tr>(.*?)</tr>", re.S)
_CELL = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
_HEADER = re.compile(r'<td class="l m linecontent"[^>]*>(.*?)</td>', re.S)


@dataclass(frozen=True)
class CodebookValue:
    code: str  # e.g. "1", "7", "BLANK", "1 - 30"
    label: str
    frequency: int | None
    notes: str = ""  # CDC's derivation notes for calculated variables


@dataclass
class CodebookVariable:
    name: str
    label: str
    section: str
    question: str
    values: list[CodebookValue] = field(default_factory=list)

    def code_map(self) -> dict[str, str]:
        return {value.code: value.label for value in self.values}


def _clean(fragment: str) -> str:
    text = fragment.replace("<br>", "\n").replace("<br/>", "\n")
    text = html.unescape(_TAG.sub("", text)).replace("\xa0", " ")
    return "\n".join(" ".join(line.split()) for line in text.splitlines()).strip()


def _header_fields(header_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in header_text.splitlines():
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip()
    return fields


def _parse_frequency(text: str) -> int | None:
    digits = text.replace(",", "").strip()
    return int(digits) if digits.isdigit() else None


def find_codebook_file(year: int) -> Path:
    matches = sorted(CODEBOOK_DIR.glob(f"codebook{year % 100:02d}_*/USCODE{year % 100:02d}_*.HTML"))
    if not matches:
        raise FileNotFoundError(f"No codebook for {year} under {CODEBOOK_DIR}")
    return matches[0]


def load_codebook(year: int) -> dict[str, CodebookVariable]:
    """Return {SAS variable name: CodebookVariable} for one survey year."""
    # CDC's SAS-generated HTML uses Windows-1252 (e.g. curly quotes, en dashes).
    text = find_codebook_file(year).read_text(encoding="cp1252", errors="strict")
    variables: dict[str, CodebookVariable] = {}
    for block in text.split('<div class="branch">')[1:]:
        header_match = _HEADER.search(block)
        if not header_match:
            continue
        fields = _header_fields(_clean(header_match.group(1)))
        name = fields.get("SAS Variable Name")
        if not name:
            continue
        variable = CodebookVariable(
            name=name,
            label=fields.get("Label", ""),
            section=fields.get("Section Name", ""),
            question=fields.get("Question", ""),
        )
        body = block[block.find("<tbody>"):]
        for row in _ROW.findall(body):
            cells = [_clean(cell) for cell in _CELL.findall(row)]
            # Rows with an empty code are the table's total line, not an answer.
            if len(cells) >= 3 and cells[0]:
                label, _, notes = cells[1].partition("\nNotes:")
                variable.values.append(
                    CodebookValue(cells[0], label.strip(), _parse_frequency(cells[2]), " ".join(notes.split()))
                )
        variables[name] = variable
    return variables
