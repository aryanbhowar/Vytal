# Models

Trained model artifacts used by the backend. They are small (a few KB) and committed so the app works straight after cloning; the training data is not committed.

| File | Contents |
|---|---|
| `heart/heart_logreg_v1.joblib` | Heart model: scikit-learn pipeline (encoders + logistic regression) and isotonic calibrator |
| `heart/heart_logreg_v1_metadata.json` | Everything else: SHA-256 of the `.joblib`, features and categories, training data provenance, dependency versions, coefficients and training means (for explanations), training score quantiles and band cut-offs, all evaluation results |
| `respiratory/respiratory_logreg_v1.joblib` | COPD model (no calibrator needed) |
| `respiratory/respiratory_logreg_v1_metadata.json` | Same structure |

## Safety

`.joblib` files are Python pickles, which can run code when loaded. The backend therefore checks each file's SHA-256 against its metadata **before** loading it, and refuses (reports the model unavailable) on a mismatch. Only load artifacts produced by this repository's training scripts.

They load reliably only with the scikit-learn version recorded in the metadata (`dependencies.scikit-learn`, currently 1.9.1, pinned in `backend/requirements.txt`).

## Recreate

See `datasets/README.md` steps 1–6. Human-readable results: `docs/model_evaluation/`.
