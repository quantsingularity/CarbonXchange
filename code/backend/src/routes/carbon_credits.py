"""
Carbon Credits routes for CarbonXchange Backend
"""

import logging
from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..models.carbon_credit import (
    CarbonCredit,
    CarbonProject,
    CreditStatus,
    ProjectStatus,
    ProjectType,
)

logger = logging.getLogger(__name__)
carbon_credits_bp = Blueprint("carbon_credits", __name__)


@carbon_credits_bp.route("/", methods=["GET"])
@jwt_required()
def get_carbon_credits() -> Any:
    """Get carbon credits with filtering and pagination"""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    status_filter = request.args.get("status")
    project_id = request.args.get("project_id", type=int)
    vintage_year = request.args.get("vintage_year", type=int)

    query = CarbonCredit.query
    if status_filter:
        try:
            query = query.filter(CarbonCredit.status == CreditStatus(status_filter))
        except ValueError:
            return jsonify({"error": f"Invalid status: {status_filter}"}), 400
    if project_id:
        query = query.filter_by(project_id=project_id)
    if vintage_year:
        query = query.filter_by(vintage_year=vintage_year)

    pagination = query.order_by(CarbonCredit.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify(
        {
            "credits": [c.to_dict() for c in pagination.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
        }
    )


@carbon_credits_bp.route("/<int:credit_id>", methods=["GET"])
@jwt_required()
def get_carbon_credit(credit_id: int) -> Any:
    """Get a specific carbon credit"""
    credit = CarbonCredit.query.get_or_404(credit_id)
    return jsonify(credit.to_dict())


@carbon_credits_bp.route("/projects", methods=["GET"])
def get_projects() -> Any:
    """Get carbon projects"""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    project_type = request.args.get("type")
    status_filter = request.args.get("status")
    country = request.args.get("country")

    query = CarbonProject.query
    if project_type:
        try:
            query = query.filter(
                CarbonProject.project_type == ProjectType(project_type)
            )
        except ValueError:
            return jsonify({"error": f"Invalid project type: {project_type}"}), 400
    if status_filter:
        try:
            query = query.filter(CarbonProject.status == ProjectStatus(status_filter))
        except ValueError:
            return jsonify({"error": f"Invalid status: {status_filter}"}), 400
    if country:
        query = query.filter(CarbonProject.country == country)

    pagination = query.order_by(CarbonProject.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify(
        {
            "projects": [p.to_dict() for p in pagination.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
        }
    )


@carbon_credits_bp.route("/projects/<int:project_id>", methods=["GET"])
def get_project(project_id: int) -> Any:
    """Get a specific carbon project"""
    project = CarbonProject.query.get_or_404(project_id)
    return jsonify(project.to_dict())


@carbon_credits_bp.route("/projects/<int:project_id>/credits", methods=["GET"])
@jwt_required()
def get_project_credits(project_id: int) -> Any:
    """Get all credits for a project"""
    project = CarbonProject.query.get_or_404(project_id)
    credits = CarbonCredit.query.filter_by(project_id=project_id).all()
    return jsonify(
        {
            "project": project.to_dict(),
            "credits": [c.to_dict() for c in credits],
            "total": len(credits),
        }
    )
