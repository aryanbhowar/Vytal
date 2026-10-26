# Data sources

## 1. What Vytal uses

| Item | Value |
|---|---|
| Dataset | Behavioral Risk Factor Surveillance System (BRFSS), combined landline and cell-phone data (LLCP) |
| Publisher | U.S. Centers for Disease Control and Prevention (CDC), Division of Population Health |
| Years | 2022 (November 2023 release), 2023 (February 2025 release), 2024 (August 2025 release) |
| Official pages | https://www.cdc.gov/brfss/annual_data/annual_2022.html, `annual_2023.html`, `annual_2024.html` |
| Files | `LLCP2022XPT.zip`, `LLCP2023XPT.zip`, `LLCP2024XPT.zip` (SAS transport format) plus each year's codebook (`codebookYY_llcp-v2-508.zip`) and SAS format file |
| Records | 445,132 (2022), 433,323 (2023), 457,670 (2024) |
| Population | Non-institutionalized US adults (18+) in participating states and territories, interviewed by telephone. 2023 excludes Kentucky and Pennsylvania; 2024 excludes Tennessee (too few interviews to meet CDC's minimum) |
| Design | Cross-sectional: different people are interviewed each year. Complex sample with weights (`_LLCPWT`), strata (`_STSTR`) and clusters (`_PSU`) |

### How the files were obtained

`cdc.gov` returned **HTTP 403 (Access Denied)** to every scripted request from this machine, including the plain HTML pages, so the download script falls back to the **Internet Archive's stored copy of the same official URLs** (`web.archive.org/web/<snapshot>id_/https://www.cdc.gov/...`; `id_` returns the original bytes).

Because the files did not come straight from CDC, they were checked against CDC's own published figures:

1. Each file's record count equals the count on CDC's page for that year (all three match exactly).
2. For every inspected variable, the number of respondents giving each answer in the file equals the frequency printed in CDC's official codebook for that year (all match exactly).

| Year | Zip SHA-256 (verified copy) |
|---|---|
| 2022 | `b6319c949b7289f8020fc903c3c2d38fe7e0b28ad703dcd81547f5cd0c0dcfeb` |
| 2023 | `d1ab80e4806a1d07bd3e40ec78c971ad9ff920f3ea5f6049780aeaa41ff31f43` |
| 2024 | `d33de91a584e866f657d29b1d5b51b5672467286ed22d021e36ee3c7b4d712a4` |

If you download the files in a browser from CDC instead, the script uses them; if the hash differs (CDC can publish corrections) it warns, and the inspection re-checks counts.

### Terms of use

CDC states that most material on its websites is not subject to copyright and is in the public domain ([CDC: Using agency materials](https://www.cdc.gov/other/agencymaterials.html)). Its conditions, which Vytal follows:

- **Attribution:** "Source: CDC, Behavioral Risk Factor Surveillance System 2022–2024."
- **No endorsement:** Vytal's use of BRFSS data does not imply endorsement by CDC, HHS or the U.S. Government. This statement appears in the app.
- **No change to substantive content:** Vytal derives models from the data; it does not republish altered CDC material.
- **Availability:** the original data is available free of charge from CDC's website.

The raw files are **not** redistributed in this repository (size and good practice); they are downloaded by script.

Recommended citation: Centers for Disease Control and Prevention (CDC). *Behavioral Risk Factor Surveillance System Survey Data*, 2022, 2023, 2024. Atlanta, Georgia: U.S. Department of Health and Human Services, Centers for Disease Control and Prevention.

## 2. Outcomes (targets)

| Model | Variable | Exact definition (from the codebook) | Same in all three years? |
|---|---|---|---|
| Heart | `_MICHD` (calculated by CDC) | 1 = reported having myocardial infarction or coronary heart disease (`CVDINFR4`=1 **or** `CVDCRHD4`=1); 2 = reported neither (both = 2); blank = don't know, refused or missing on either question | Yes: same wording, codes and derivation |
| Respiratory | `CHCCOPD3` | "(Ever told) (you had) C.O.P.D. (chronic obstructive pulmonary disease), emphysema or chronic bronchitis?" 1 = yes, 2 = no, 7 = don't know, 9 = refused | Yes |

**What these targets mean.** Both record whether a respondent says a doctor, nurse or other health professional has *ever* told them they had the condition. The models therefore learn which answer patterns go with *having reported* the condition. They do **not** predict whether someone will develop it in future, and they are not a diagnosis. COPD, emphysema and chronic bronchitis are grouped in one question by CDC; asthma and lung cancer are separate questions and are **not** part of the respiratory target.

## 3. Features

Selected by the rules in the master plan: available in all three years with the same question and answer codes; collectable by a plain question; a risk factor or health history, not a current-symptom or general-health question (D-005); not the other model's target. Race, income and education are excluded (D-006).

| Feature | BRFSS source (2022 / 2023 / 2024) | Values used | Heart | Respiratory |
|---|---|---|---|---|
| Age group | `_AGEG5YR` | 13 five-year groups, 18–24 … 80+ | ✓ | ✓ |
| Sex | `SEXVAR` | male, female | ✓ | ✓ |
| BMI | `_BMI5` ÷ 100 (CDC: weight kg / height m²) | continuous | ✓ | ✓ |
| Smoking status | `_SMOKER3` | every day, some days, former, never | ✓ | ✓ |
| Current e-cigarette use | `_CURECI2` / `_CURECI2` / `_CURECI3` | yes, no | – | ✓ |
| Exercise in past 30 days | `EXERANY2` | yes, no | ✓ | ✓ |
| Heavy drinking | `_RFDRHV8` / `_RFDRHV8` / `_RFDRHV9` | yes, no (men >14, women >7 drinks/week) | ✓ | – |
| Diabetes | `DIABETE4` | yes; yes, only during pregnancy; no; prediabetes/borderline | ✓ | ✓ |
| Stroke ever | `CVDSTRK3` | yes, no | ✓ | – |
| Kidney disease ever | `CHCKDNY2` | yes, no | ✓ | – |
| Asthma status | `_ASTHMS1` | current, former, never | – | ✓ |

**Year-specific transformations.** The e-cigarette and heavy-drinking variables have different names in 2024 because CDC renamed their inputs. Their definitions are the same in all three years (checked from the codebook derivation notes), so they are renamed to one canonical name. The underlying e-cigarette question `ECIGNOW` changed the wording of answer 4 in 2024 ("Not at all (right now)" became "Used them in the past but do not currently use them at all"); both count as "not current", so the calculated current-user variable is unaffected. No other year-specific changes are needed.

**Not used, and why:**

| Variable | Reason |
|---|---|
| High blood pressure (`BPHIGH6`), cholesterol checked (`CHOLCHK3`), high cholesterol (`TOLDHI3`) | Asked **only in 2023**; absent from the 2022 and 2024 files and codebooks. Cannot be used in models pooled across 2022–2024 (D-025). |
| General health, difficulty walking, unhealthy days | Partly measure the disease itself (D-005) |
| Race, income, education | Fairness and scope (D-006) |
| Survey weight, stratum, PSU | Survey design, not personal characteristics; used only for weighted prevalence |

## 4. Missing and unusable answers

Codes meaning "don't know", "refused", "not asked" or "missing" are listed per variable in `ml/feature_definitions/brfss_candidate_variables.py` (`INVALID_CODES`), taken from the codebooks. Rows with such a code in the target or any of the model's features are **excluded** (complete-case analysis). They are never recoded to "no".

Sample sizes after exclusions (complete cases):

| Model | 2022 | 2023 | 2024 | Pooled | Prevalence in complete cases | Weighted US prevalence |
|---|---|---|---|---|---|---|
| Heart | 356,785 | 362,732 | 373,678 | 1,093,195 | 8.6–9.5% | 6.5–6.9% |
| Respiratory | 369,476 | 371,689 | 386,690 | 1,127,855 | 7.7–8.1% | 6.2–6.8% |

Exclusions remove 15–19% of rows with a valid target, mostly because BMI (about 9–11%), heavy drinking (8–11%, heart only) or smoking status (5–8%) is unusable. The excluded rows reported the condition slightly less often than the kept rows (heart: 7.7–8.6% vs 8.6–9.5%; respiratory: 7.4–7.9% vs 7.7–8.1%), so complete-case analysis shifts prevalence by under one percentage point. This is recorded as a limitation. Full per-variable tables: [`docs/datasets/brfss_variable_availability.md`](../docs/datasets/brfss_variable_availability.md).

## 5. Survey design and weighting

- The sample is not a simple random sample: some groups (e.g. older adults) are over-represented. This is why the **unweighted** prevalence in the sample (about 9%) is higher than CDC's **weighted** estimate for US adults (about 6.5–6.9% for heart disease).
- Models are trained **unweighted** (D-009): the goal is a pattern-learning model, not a population estimate. The "survey average" shown to users is the **weighted** prevalence (D-021).
- Pooling three years: CDC's guidance for combined years is to divide each year's weight by the number of years combined; Vytal does this for pooled weighted figures.
- Standard errors that account for strata and clusters are not computed; reported metrics treat respondents as independent. Recorded as a limitation.

## 6. Considered and rejected

**Zenodo "BRFSS 2020 Heart Disease Dataset (Cleaned Version)"**, record 15364962 (a re-upload of the Kaggle `heart_2020_cleaned.csv`, 23.3 MB). Rejected (D-002): it is 2020 data; its description defines the target as CHD **or** MI while its variable table maps it only to `CVDINFR4` (heart attack); it attributes the continuous BMI column to the categorical `_BMI5CAT`; its recoding cannot be verified; and it has no COPD target.

## 7. Limitations

- Self-reported answers (possible recall and reporting error; undiagnosed people report "no").
- "Ever told" outcomes mix long-standing and recent diagnoses; risk factors are measured now, possibly after diagnosis (e.g. people may stop smoking after a heart attack). Associations are not causes.
- US adults only; telephone survey; three states missing in some years.
- Complete-case exclusions (section 4).
- Blood pressure and cholesterol, strong heart risk factors, are not available across the pooled years.
- COPD target groups three conditions and may include people with misdiagnosed asthma.
