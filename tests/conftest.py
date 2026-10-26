"""Shared test fixtures.

`client` runs the real app with the real saved models (startup included).
`make_client` builds an app with changed settings, e.g. a models folder that
is missing a model, to test honest failure states.
"""

import dataclasses

import pytest
from fastapi.testclient import TestClient

from app.core.config import load_settings
from app.main import create_app

# SYNTHETIC example answers used across API tests (not a real person).
VALID_ASSESSMENT = {
    "age_years": 62,
    "sex": "male",
    "height_cm": 175,
    "weight_kg": 92,
    "smoking_status": "current_daily",
    "ecigarette_current_use": "no",
    "physical_activity_past_30_days": "no",
    "diabetes_status": "yes",
    "stroke_history": "no",
    "kidney_disease_history": "no",
    "asthma_status": "never",
}


@pytest.fixture
def valid_assessment() -> dict:
    return dict(VALID_ASSESSMENT)


@pytest.fixture
def make_client():
    clients = []

    def _make(**overrides) -> TestClient:
        settings = dataclasses.replace(load_settings(), **overrides)
        client = TestClient(create_app(settings), raise_server_exceptions=False)
        client.__enter__()  # runs startup (model loading)
        clients.append(client)
        return client

    yield _make
    for client in clients:
        client.__exit__(None, None, None)


@pytest.fixture
def client(make_client) -> TestClient:
    return make_client()
