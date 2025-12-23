from typing import Any
from flask import Blueprint, jsonify, request
from src.models.user import User, db

user_bp = Blueprint("user", __name__)


@user_bp.route("/users", methods=["GET"])
def get_users() -> Any:
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@user_bp.route("/users", methods=["POST"])
def create_user() -> Any:
    data = request.json
    if not data:
        return (jsonify({"error": "No data provided"}), 400)

    # Extract required fields
    email = data.get("email")
    password = data.get("password")
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    if not all([email, password, first_name, last_name]):
        return (jsonify({"error": "Missing required fields"}), 400)

    user = User(
        email=email, password=password, first_name=first_name, last_name=last_name
    )
    db.session.add(user)
    db.session.commit()
    return (jsonify(user.to_dict()), 201)


@user_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id: Any) -> Any:
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


@user_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id: Any) -> Any:
    user = User.query.get_or_404(user_id)
    data = request.json
    if not data:
        return (jsonify({"error": "No data provided"}), 400)

    # Update allowed fields
    if "first_name" in data:
        user.first_name = data["first_name"]
    if "last_name" in data:
        user.last_name = data["last_name"]
    if "phone_number" in data:
        user.phone_number = data["phone_number"]

    db.session.commit()
    return jsonify(user.to_dict())


@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: Any) -> Any:
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return ("", 204)
