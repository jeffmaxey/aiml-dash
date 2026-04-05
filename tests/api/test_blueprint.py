"""Tests for the REST API blueprint."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from flask import Flask

from aiml_dash.api.blueprint import api_blueprint


@pytest.fixture()
def client():
    """Provide a test client for the API blueprint."""
    app = Flask(__name__)
    app.register_blueprint(api_blueprint)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


def test_health_no_auth(client):
    """GET /health returns 200 with expected keys regardless of auth."""
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data


# ---------------------------------------------------------------------------
# Datasets (dev mode — no API key required)
# ---------------------------------------------------------------------------


def test_datasets_no_key_required_in_dev_mode(client):
    """Without AIML_DASH_API_KEY set, requests succeed without a key."""
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("AIML_DASH_API_KEY", None)
        resp = client.get("/api/v1/datasets")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "datasets" in data
    assert "count" in data


def test_datasets_with_wrong_key(client):
    """When AIML_DASH_API_KEY is set, wrong key returns 401."""
    with patch.dict(os.environ, {"AIML_DASH_API_KEY": "secret"}, clear=False):
        resp = client.get("/api/v1/datasets", headers={"X-API-Key": "wrong"})
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "Unauthorized"


def test_datasets_with_correct_key(client):
    """Correct API key returns 200 with datasets list."""
    with patch.dict(os.environ, {"AIML_DASH_API_KEY": "secret"}, clear=False):
        resp = client.get("/api/v1/datasets", headers={"X-API-Key": "secret"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "datasets" in data
    assert isinstance(data["datasets"], list)


# ---------------------------------------------------------------------------
# Dataset by name
# ---------------------------------------------------------------------------


def test_dataset_by_name_found(client):
    """GET /datasets/<name> returns data for a known dataset."""
    # data_manager loads sample datasets (diamonds, titanic) by default
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("AIML_DASH_API_KEY", None)
        resp = client.get("/api/v1/datasets/diamonds")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "diamonds"
    assert "data" in data
    assert "columns" in data
    assert "rows" in data
    assert "sample_size" in data


def test_dataset_by_name_not_found(client):
    """GET /datasets/<name> returns 404 for unknown dataset."""
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("AIML_DASH_API_KEY", None)
        resp = client.get("/api/v1/datasets/nonexistent_dataset_xyz")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


# ---------------------------------------------------------------------------
# Dataset info
# ---------------------------------------------------------------------------


def test_dataset_info(client):
    """GET /datasets/<name>/info returns an info dict."""
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("AIML_DASH_API_KEY", None)
        resp = client.get("/api/v1/datasets/diamonds/info")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "diamonds"
    assert "rows" in data
    assert "columns" in data


# ---------------------------------------------------------------------------
# Dataset quality
# ---------------------------------------------------------------------------


def test_dataset_quality(client):
    """GET /datasets/<name>/quality returns quality metrics."""
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("AIML_DASH_API_KEY", None)
        resp = client.get("/api/v1/datasets/diamonds/quality")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "row_count" in data
    assert "col_count" in data
