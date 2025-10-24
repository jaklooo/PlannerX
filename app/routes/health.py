"""Health check and version endpoint."""
from flask import Blueprint, jsonify
from app.version import get_version_info

bp = Blueprint("health", __name__)


@bp.route("/health")
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "PlannerX",
        **get_version_info()
    })


@bp.route("/version")
def version():
    """Version information endpoint."""
    return jsonify(get_version_info())
