"""
User routes for CarbonXchange Backend
"""

import logging
from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..models import db
from ..models.user import User, UserProfile

logger = logging.getLogger(__name__)
user_bp = Blueprint("user", __name__)


@user_bp.route("/", methods=["GET"])
@jwt_required()
def get_users() -> Any:
    """Get all users (admin endpoint)"""
    users = User.query.all()
    return jsonify({"users": [user.to_dict() for user in users], "total": len(users)})


@user_bp.route("/", methods=["POST"])
def create_user() -> Any:
    """Create a new user"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email")
    password = data.get("password")
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    if not all([email, password, first_name, last_name]):
        return (
            jsonify(
                {
                    "error": "Missing required fields: email, password, first_name, last_name"
                }
            ),
            400,
        )

    try:
        existing = User.query.filter_by(email=email.lower().strip()).first()
        if existing:
            return jsonify({"error": "User with this email already exists"}), 409

        user = User(
            email=email, password=password, first_name=first_name, last_name=last_name
        )
        profile = UserProfile(user=user)
        db.session.add(user)
        db.session.add(profile)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create user error: {e}")
        return jsonify({"error": "Failed to create user"}), 500


@user_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id: int) -> Any:
    """Get user by ID"""
    user = User.query.get_or_404(user_id)
    user_data = user.to_dict()
    if user.profile:
        user_data["profile"] = user.profile.to_dict()
    return jsonify(user_data)


@user_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id: int) -> Any:
    """Update user"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "first_name" in data:
        user.first_name = data["first_name"].strip()
    if "last_name" in data:
        user.last_name = data["last_name"].strip()
    if "phone_number" in data:
        user.phone_number = data["phone_number"]

    if user.profile:
        profile_fields = [
            "middle_name",
            "nationality",
            "country_of_residence",
            "address_line_1",
            "address_line_2",
            "city",
            "state_province",
            "postal_code",
            "country",
            "occupation",
            "employer",
            "source_of_funds",
            "company_name",
            "trading_experience",
            "risk_tolerance",
            "preferred_language",
            "timezone",
        ]
        for field in profile_fields:
            if field in data:
                setattr(user.profile, field, data[field])

    db.session.commit()
    return jsonify(user.to_dict())


@user_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id: int) -> Any:
    """Delete user"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return "", 204


@user_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me() -> Any:
    """Get current user profile"""
    current_user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=current_user_uuid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    user_data = user.to_dict()
    if user.profile:
        user_data["profile"] = user.profile.to_dict()
    return jsonify({"user": user_data})


@user_bp.route("/me/profile", methods=["PUT"])
@jwt_required()
def update_my_profile() -> Any:
    """Update current user's profile"""
    current_user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=current_user_uuid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "first_name" in data:
        user.first_name = data["first_name"].strip()
    if "last_name" in data:
        user.last_name = data["last_name"].strip()
    if "phone_number" in data:
        user.phone_number = data["phone_number"]

    if not user.profile:
        user.profile = UserProfile(user=user)
        db.session.add(user.profile)

    profile_fields = [
        "middle_name",
        "nationality",
        "country_of_residence",
        "address_line_1",
        "address_line_2",
        "city",
        "state_province",
        "postal_code",
        "country",
        "occupation",
        "employer",
        "source_of_funds",
        "company_name",
        "trading_experience",
        "risk_tolerance",
        "preferred_language",
        "timezone",
        "marketing_consent",
    ]
    for field in profile_fields:
        if field in data:
            setattr(user.profile, field, data[field])

    db.session.commit()
    user_data = user.to_dict()
    user_data["profile"] = user.profile.to_dict()
    return jsonify({"user": user_data})
