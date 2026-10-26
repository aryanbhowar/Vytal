"""All training settings and thresholds in one place (no magic numbers in the code)."""

from ml.preprocessing.brfss_sources import PROJECT_ROOT
from ml.preprocessing.dataset_split import RANDOM_SEED

MODEL_VERSION = "1.0.0"
MODELS_DIR = PROJECT_ROOT / "models"
EVALUATION_DOCS_DIR = PROJECT_ROOT / "docs" / "model_evaluation"
FIGURES_DIR = EVALUATION_DOCS_DIR / "figures"

SEED = RANDOM_SEED

# Logistic regression. With ~765,000 training rows regularisation barely matters;
# C=1.0 is scikit-learn's default and is kept for transparency.
LOGISTIC_REGRESSION_PARAMS = {"C": 1.0, "max_iter": 2000, "solver": "lbfgs"}

# BMI can enter the model as a straight line or as a smooth curve (cubic spline),
# which lets very low and very high BMI both raise the estimate. The choice is
# made on the VALIDATION set by log loss, never on the test set.
BMI_SPLINE_PARAMS = {"n_knots": 5, "degree": 3, "knots": "quantile"}

# Comparison model (reported only, never deployed: D-008).
GRADIENT_BOOSTING_PARAMS = {"max_iter": 300, "learning_rate": 0.1, "early_stopping": True, "random_state": SEED}

# Calibration: probabilities are shown to users only if they are well calibrated
# on the validation set (D-007). "Well calibrated" means expected calibration error
# (10 equal-size bins) at most 0.5 percentage points and calibration slope 0.9-1.1.
# Otherwise isotonic calibration is fitted on the validation set.
CALIBRATION_BINS = 10
MAX_ACCEPTABLE_ECE = 0.005
CALIBRATION_SLOPE_RANGE = (0.9, 1.1)

# Presentation bands (D-010): a user's percentile among TRAINING-set scores.
# They describe position relative to survey respondents, not clinical risk.
BAND_CUTOFF_PERCENTILES = {"moderate": 50, "elevated": 75, "high": 90}
BAND_ORDER = ["low", "moderate", "elevated", "high"]
SCORE_QUANTILE_POINTS = 1001  # 0.0, 0.1, ..., 100.0 percentiles

# Subgroups for the bias check.
AGE_SUBGROUPS = {
    "18-44": ["18-24", "25-29", "30-34", "35-39", "40-44"],
    "45-64": ["45-49", "50-54", "55-59", "60-64"],
    "65+": ["65-69", "70-74", "75-79", "80+"],
}
