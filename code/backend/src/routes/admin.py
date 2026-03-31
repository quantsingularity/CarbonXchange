"""
Admin routes for CarbonXchange Backend
"""

import logging
from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..models import db
from ..models.user import User, UserRole, UserStatus
from ..security import require_roles

logger = logging.getLogger(__name__)
admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@require_roles(UserRole.ADMIN, UserRole.COMPLIANCE_OFFICER)
def get_all_users() -> Any:
    """Get all users with sensitive data (admin only)"""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    status_filter = request.args.get("status")
    role_filter = request.args.get("role")

    query = User.query
    if status_filter:
        try:
            query = query.filter(User.status == UserStatus(status_filter))
        except ValueError:
            return jsonify({"error": f"Invalid status: {status_filter}"}), 400
    if role_filter:
        try:
            query = query.filter(User.role == UserRole(role_filter))
        except ValueError:
            return jsonify({"error": f"Invalid role: {role_filter}"}), 400

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify(
        {
            "users": [u.to_dict(include_sensitive=True) for u in pagination.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
            "per_page": per_page,
        }
    )


@admin_bp.route("/users/<int:user_id>/status", methods=["PUT"])
@jwt_required()
@require_roles(UserRole.ADMIN)
def update_user_status(user_id: int) -> Any:
    """Update user account status"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if not data or "status" not in data:
        return jsonify({"error": "status field is required"}), 400

    try:
        new_status = UserStatus(data["status"])
    except ValueError:
        return jsonify({"error": f"Invalid status: {data['status']}"}), 400

    if new_status == UserStatus.SUSPENDED:
        user.suspend_account(reason=data.get("reason", "Admin action"))
    elif new_status == UserStatus.ACTIVE:
        user.activate_account()
    elif new_status == UserStatus.LOCKED:
        user.lock_account(duration_minutes=data.get("duration_minutes", 30))
    else:
        user.status = new_status

    db.session.commit()
    return jsonify(
        {
            "message": f"User status updated to {new_status.value}",
            "user": user.to_dict(include_sensitive=True),
        }
    )


@admin_bp.route("/system", methods=["GET"])
@jwt_required()
@require_roles(UserRole.ADMIN)
def get_system_info() -> Any:
    """Get system statistics"""
    from ..models.carbon_credit import CarbonCredit, CarbonProject
    from ..models.trading import Order, Trade

    total_users = User.query.count()
    active_users = User.query.filter_by(status=UserStatus.ACTIVE).count()
    total_orders = Order.query.count()
    total_trades = Trade.query.count()
    total_projects = CarbonProject.query.count()
    total_credits = CarbonCredit.query.count()

    return jsonify(
        {
            "users": {"total": total_users, "active": active_users},
            "trading": {"orders": total_orders, "trades": total_trades},
            "carbon": {"projects": total_projects, "credits": total_credits},
        }
    )


@admin_bp.route("/users/<int:user_id>/unlock", methods=["POST"])
@jwt_required()
@require_roles(UserRole.ADMIN)
def unlock_user(user_id: int) -> Any:
    """Unlock a user account"""
    user = User.query.get_or_404(user_id)
    user.unlock_account()
    db.session.commit()
    return jsonify(
        {
            "message": "User account unlocked",
            "user": user.to_dict(include_sensitive=True),
        }
    )
