"""REST API Blueprint for AIML Dash.

Provides JSON endpoints for programmatic access to datasets and application state.
Authenticated via API key header: X-API-Key (configurable via AIML_DASH_API_KEY env var).
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from aiml_dash.utils.data_manager import data_manager

logger = logging.getLogger(__name__)

api_blueprint = Blueprint("api", __name__, url_prefix="/api/v1")


def _check_auth():
    """Check API key authentication.

    Returns None when the request is authorised (or auth is disabled).
    Returns a Flask response tuple with a 401 status when authentication fails.
    """
    api_key = os.environ.get("AIML_DASH_API_KEY", "")
    if not api_key:
        return None
    provided = request.headers.get("X-API-Key", "")
    if provided != api_key:
        return jsonify({"error": "Unauthorized"}), 401
    return None


@api_blueprint.route("/health", methods=["GET"])
def health():
    """Return application health status (no auth required)."""
    return jsonify(
        {
            "status": "ok",
            "version": "0.1.0",
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }
    )


@api_blueprint.route("/datasets", methods=["GET"])
def list_datasets():
    """Return a list of all loaded datasets."""
    auth_error = _check_auth()
    if auth_error is not None:
        return auth_error

    names = data_manager.get_dataset_names()
    datasets = []
    for name in names:
        info = data_manager.get_dataset_info(name)
        datasets.append(
            {
                "name": name,
                "rows": info.get("rows", 0),
                "columns": info.get("columns", 0),
                "description": info.get("description", ""),
            }
        )
    return jsonify({"datasets": datasets, "count": len(datasets)})


@api_blueprint.route("/datasets/<name>", methods=["GET"])
def get_dataset(name):
    """Return the first 100 rows of a named dataset."""
    auth_error = _check_auth()
    if auth_error is not None:
        return auth_error

    if name not in data_manager.datasets:
        return jsonify({"error": "Dataset not found"}), 404

    df = data_manager.datasets[name]
    sample = df.head(100)
    return jsonify(
        {
            "name": name,
            "data": sample.to_dict(orient="records"),
            "columns": list(df.columns),
            "rows": len(df),
            "sample_size": len(sample),
        }
    )


@api_blueprint.route("/datasets/<name>/info", methods=["GET"])
def get_dataset_info(name):
    """Return full metadata for a named dataset."""
    auth_error = _check_auth()
    if auth_error is not None:
        return auth_error

    info = data_manager.get_dataset_info(name)
    if not info:
        return jsonify({"error": "Dataset not found"}), 404
    return jsonify(info)


@api_blueprint.route("/datasets/<name>/quality", methods=["GET"])
def get_dataset_quality(name):
    """Return data quality metrics for a named dataset."""
    auth_error = _check_auth()
    if auth_error is not None:
        return auth_error

    quality = data_manager.get_data_quality(name)
    if not quality:
        return jsonify({"error": "Dataset not found"}), 404
    return jsonify(quality)


@api_blueprint.route("/datasets/<name>/persist", methods=["POST"])
def persist_dataset(name):
    """Persist a named dataset to disk."""
    auth_error = _check_auth()
    if auth_error is not None:
        return auth_error

    success, message = data_manager.persist_to_disk(name)
    if success:
        return jsonify({"success": True, "message": f"Dataset '{name}' persisted successfully."})
    # Log the full message internally but don't expose internal paths to callers.
    logger.warning("persist_dataset API failed for '%s': %s", name, message)
    return jsonify({"success": False, "error": f"Failed to persist dataset '{name}'."})
