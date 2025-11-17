"""
Admin routes for CarbonXchange Backend
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    """Get all users (admin only)"""
    return (
        jsonify({"message": "Admin users endpoint - implementation in progress"}),
        200,
    )


@admin_bp.route("/system", methods=["GET"])
@jwt_required()
def get_system_info():
    """Get system information"""
    return (
        jsonify({"message": "System info endpoint - implementation in progress"}),
        200,
    )
