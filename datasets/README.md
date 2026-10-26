# Datasets

Where Vytal's data lives and how to recreate it. Source details and terms of use: [`DATA_SOURCES.md`](DATA_SOURCES.md).

## Folders

| Folder | Contents | In Git? |
|---|---|---|
| `raw/` | BRFSS zips, extracted `.XPT` files (about 1.1 GB each), `documentation/` (codebooks and SAS format files) | **No** (ignored) |
| `interim/` | Selected columns extracted from the raw files (Task 3) | No |
| `processed/` | Model-ready tables (`*.csv`, not committed) and small summary files (`*_summary.json`, committed: aggregate counts only, no individual records) | Summaries only |

## Recreate the data (from the project root)

```powershell
# 1. Install the ML packages (once)
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt -r ml\requirements.txt

# 2. Download BRFSS 2022-2024 and their codebooks (about 260 MB download, 3.5 GB unzipped)
.venv\Scripts\python.exe -m ml.preprocessing.download_brfss_data

# 3. Check the files and every candidate variable against the official codebooks
.venv\Scripts\python.exe -m ml.preprocessing.inspect_brfss_variables
```

Step 2 tries cdc.gov first, then the Internet Archive copy of the same official URL. If both fail it prints browser download links; save the zips into `datasets/raw/` and run it again.

Step 3 writes `processed/brfss_variable_inspection_summary.json` and the report `docs/datasets/brfss_variable_availability.md`, and uses about 1 GB of RAM because it reads only the needed columns.

Then build the model datasets and train the models:

```powershell
# 4. Extract the needed columns (about 15 MB of Parquet in interim/)
.venv\Scripts\python.exe -m ml.preprocessing.brfss_data_extraction

# 5. Recode, exclude unusable answers, split 70/15/15 (writes processed/*.csv and *_summary.json)
.venv\Scripts\python.exe -m ml.preprocessing.build_model_dataset

# 6. Train, calibrate, evaluate and save each model (about 5 minutes each on a laptop CPU)
.venv\Scripts\python.exe -m ml.training.heart_model_training
.venv\Scripts\python.exe -m ml.training.respiratory_model_training
```

Step 6 writes `models/<model>/` (artifact and metadata) and `docs/model_evaluation/` (report, model card, figures). The same inputs always give the same split and the same model (fixed seed 42).
