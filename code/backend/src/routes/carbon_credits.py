"""
Carbon Credits routes for CarbonXchange Backend
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

carbon_credits_bp = Blueprint("carbon_credits", __name__)


@carbon_credits_bp.route("/", methods=["GET"])
@jwt_required()
def get_carbon_credits() -> Any:
    """Get carbon credits"""
    return (
        jsonify({"message": "Carbon credits endpoint - implementation in progress"}),
        200,
    )


@carbon_credits_bp.route("/projects", methods=["GET"])
@jwt_required()
def get_projects() -> Any:
    """Get carbon projects"""
    return (
        jsonify({"message": "Carbon projects endpoint - implementation in progress"}),
        200,
    )
