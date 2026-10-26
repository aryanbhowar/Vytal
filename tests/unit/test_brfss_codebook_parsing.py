"""Unit tests for the codebook parser and the cross-year comparison rules.

The HTML below is a SYNTHETIC fragment written for this test in the same layout
as CDC's codebook files. It is not real survey data.
"""

from ml.preprocessing import brfss_codebook
from ml.preprocessing.inspect_brfss_variables import compare_with_codebook, normalised

SYNTHETIC_CODEBOOK_HTML = """
<html><body>
<div class="branch">
<table><thead><tr>
<td class="l m linecontent" colspan="5">Label:&nbsp;Ever&nbsp;had&nbsp;CHD&nbsp;or&nbsp;MI<br>Section&nbsp;Name:&nbsp;Calculated&nbsp;Variables<br>SAS&nbsp;Variable&nbsp;Name:&nbsp;_MICHD<br>Question:&nbsp;Ever&nbsp;reported&nbsp;CHD&nbsp;or&nbsp;MI</td>
</tr></thead>
<tbody>
<tr><td class="c data">1</td><td class="l data">Reported having MI or CHD<br>Notes: CVDINFR4=1 OR CVDCRHD4=1</td><td class="c data"> 1,200</td><td>8</td><td>6</td></tr>
<tr><td class="c data">2</td><td class="l data">Did not report having MI or CHD</td><td class="c data">13,800</td><td>92</td><td>94</td></tr>
<tr><td class="c data">BLANK</td><td class="l data">Not asked or Missing</td><td class="c data">50</td><td>.</td><td>.</td></tr>
</tbody></table>
</div>
</body></html>
"""


def test_parser_reads_header_codes_frequencies_and_notes(tmp_path, monkeypatch):
    folder = tmp_path / "codebook23_synthetic"
    folder.mkdir()
    (folder / "USCODE23_SYNTHETIC.HTML").write_text(SYNTHETIC_CODEBOOK_HTML, encoding="cp1252")
    monkeypatch.setattr(brfss_codebook, "CODEBOOK_DIR", tmp_path)

    codebook = brfss_codebook.load_codebook(2023)

    variable = codebook["_MICHD"]
    assert variable.label == "Ever had CHD or MI"
    assert variable.section == "Calculated Variables"
    assert [v.code for v in variable.values] == ["1", "2", "BLANK"]
    assert [v.frequency for v in variable.values] == [1200, 13800, 50]
    assert variable.values[0].notes == "CVDINFR4=1 OR CVDCRHD4=1"
    assert variable.values[0].label == "Reported having MI or CHD"


def test_normalised_ignores_encoding_punctuation_and_skip_instructions():
    # The same answer as printed in different years' codebooks.
    assert normalised("Don\u2019t know/Not Sure\u2014Go to Section 08.01 AGE") == normalised(
        "Don't know/Not Sure - Go to Section 07.01 AGE"
    )
    assert normalised("Male\u2014Code=1 if LANDSEX1=1") == normalised("Male - Code=1 if LANDSEX3=1")


def test_normalised_still_detects_a_real_change_in_meaning():
    # ECIGNOW code 4 was reworded between 2023 and 2024; the comparison must flag it.
    assert normalised("Not at all (right now)") != normalised(
        "Used them in the past but do not currently use them at all"
    )


def test_compare_with_codebook_reports_count_mismatches():
    entry = brfss_codebook.CodebookVariable("X", "", "", "", [
        brfss_codebook.CodebookValue("1", "Yes", 10),
        brfss_codebook.CodebookValue("2", "No", 20),
        brfss_codebook.CodebookValue("1 - 30", "Days", 5),  # ranges are skipped
    ])
    assert compare_with_codebook({"1": 10, "2": 20}, entry) == []
    assert compare_with_codebook({"1": 9, "2": 20}, entry) == ["code 1: codebook 10, file 9"]
