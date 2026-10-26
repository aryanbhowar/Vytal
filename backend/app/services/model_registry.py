"""Load the saved models once at startup and report whether each one is usable.

A model that is missing, fails its integrity check or cannot be loaded is marked
unavailable with a short public reason. The API then says so honestly instead of
returning a made-up estimate. Internal paths and error details are logged for
the operator only, never sent to users.
"""

import logging
from dataclasses import dataclass, field

from app.core.config import MODEL_ARTIFACTS, Settings
from ml.feature_definitions.feature_schema import load_schema, model_features
from ml.inference.risk_model import LoadedRiskModel, ModelIntegrityError, load_risk_model

logger = logging.getLogger("vytal.models")

MODEL_TITLES = {
    "heart": "Heart: coronary heart disease or heart attack",
    "respiratory": "Lungs: COPD, emphysema or chronic bronchitis",
}


@dataclass
class ModelSlot:
    model_id: str
    model: LoadedRiskModel | None = None
    unavailable_reason: str | None = None

    @property
    def available(self) -> bool:
        return self.model is not None


@dataclass
class ModelRegistry:
    slots: dict[str, ModelSlot] = field(default_factory=dict)

    def get(self, model_id: str) -> ModelSlot:
        return self.slots[model_id]

    @property
    def all_available(self) -> bool:
        return all(slot.available for slot in self.slots.values())

    @property
    def any_available(self) -> bool:
        return any(slot.available for slot in self.slots.values())


def _load_slot(model_id: str, settings: Settings) -> ModelSlot:
    path = settings.models_dir / MODEL_ARTIFACTS[model_id]
    try:
        model = load_risk_model(path)
    except FileNotFoundError:
        logger.error("Model %s not found at %s", model_id, path)
        return ModelSlot(model_id, unavailable_reason="The model file is not installed on this server.")
    except ModelIntegrityError:
        logger.error("Model %s failed its integrity check (%s)", model_id, path)
        return ModelSlot(model_id, unavailable_reason="The model file failed its integrity check and was not loaded.")
    except Exception:  # corrupt file, incompatible library version, etc.
        logger.exception("Model %s could not be loaded from %s", model_id, path)
        return ModelSlot(model_id, unavailable_reason="The model could not be loaded on this server.")

    if model.features != model_features(model_id) or model.metadata["feature_schema_version"] != load_schema()["schema_version"]:
        logger.error("Model %s was trained with a different feature schema", model_id)
        return ModelSlot(model_id, unavailable_reason="The installed model does not match this version of the app.")
    logger.info("Loaded model %s v%s", model_id, model.metadata["model_version"])
    return ModelSlot(model_id, model=model)


def load_registry(settings: Settings) -> ModelRegistry:
    return ModelRegistry({model_id: _load_slot(model_id, settings) for model_id in MODEL_ARTIFACTS})
