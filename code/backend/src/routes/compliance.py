"""
Compliance routes for CarbonXchange Backend
"""

import logging
from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..models.compliance import ComplianceRecord, RegulatoryReport
from ..models.user import User, UserRole
from ..security import require_roles

logger = logging.getLogger(__name__)
compliance_bp = Blueprint("compliance", __name__)


@compliance_bp.route("/records", methods=["GET"])
@jwt_required()
def get_compliance_records() -> Any:
    """Get compliance records"""
    current_user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=current_user_uuid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)

    query = ComplianceRecord.query.filter_by(user_id=user.id)
    pagination = query.order_by(ComplianceRecord.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify(
        {
            "records": [r.to_dict() for r in pagination.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
        }
    )


@compliance_bp.route("/records/<int:record_id>", methods=["GET"])
@jwt_required()
def get_compliance_record(record_id: int) -> Any:
    """Get a specific compliance record"""
    current_user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=current_user_uuid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    record = ComplianceRecord.query.get_or_404(record_id)
    if record.user_id != user.id and user.role not in [
        UserRole.ADMIN,
        UserRole.COMPLIANCE_OFFICER,
    ]:
        return jsonify({"error": "Access denied"}), 403

    return jsonify(record.to_dict())


@compliance_bp.route("/reports", methods=["GET"])
@jwt_required()
@require_roles(UserRole.ADMIN, UserRole.COMPLIANCE_OFFICER, UserRole.AUDITOR)
def get_reports() -> Any:
    """Get regulatory compliance reports"""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)

    pagination = RegulatoryReport.query.order_by(
        RegulatoryReport.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(
        {
            "reports": [r.to_dict() for r in pagination.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
        }
    )


@compliance_bp.route("/status", methods=["GET"])
@jwt_required()
def get_compliance_status() -> Any:
    """Get current user's compliance status"""
    current_user_uuid = get_jwt_identity()
    user = User.query.filter_by(uuid=current_user_uuid).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(
        {
            "user_id": user.id,
            "kyc_status": (
                user.kyc_records[-1].status.value if user.kyc_records else "not_started"
            ),
            "is_kyc_approved": user.is_kyc_approved,
            "risk_level": user.risk_level.value,
            "trading_enabled": user.is_verified and user.status.value == "active",
        }
    )
