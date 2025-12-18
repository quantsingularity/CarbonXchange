"""
Compliance routes for CarbonXchange Backend
"""

from typing import Any
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

compliance_bp = Blueprint("compliance", __name__)


@compliance_bp.route("/records", methods=["GET"])
@jwt_required()
def get_compliance_records() -> Any:
    """Get compliance records"""
    return (
        jsonify(
            {"message": "Compliance records endpoint - implementation in progress"}
        ),
        200,
    )


@compliance_bp.route("/reports", methods=["GET"])
@jwt_required()
def get_reports() -> Any:
    """Get compliance reports"""
    return (
        jsonify(
            {"message": "Compliance reports endpoint - implementation in progress"}
        ),
        200,
    )
