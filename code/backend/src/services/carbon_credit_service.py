"""
Carbon Credit Service for CarbonXchange Backend
Handles carbon credit management and operations
"""

import logging
from decimal import Decimal
from typing import Any, Dict, Optional
from ..models import db
from ..models.carbon_credit import CarbonCredit, CarbonProject
from .audit_service import AuditService

logger = logging.getLogger(__name__)


class CarbonCreditService:
    """
    Service for carbon credit management
    """

    def __init__(self) -> None:
        self.audit_service = AuditService()

    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new carbon project

        Args:
            project_data: Project information

        Returns:
            Created project details
        """
        try:
            project = CarbonProject(**project_data)
            db.session.add(project)
            db.session.commit()

            logger.info(f"Created carbon project: {project.id}")
            return {"project_id": project.id, "name": project.name}
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            db.session.rollback()
            return {"error": str(e)}

    def get_project(self, project_id: int) -> Optional[CarbonProject]:
        """
        Get project by ID

        Args:
            project_id: Project ID

        Returns:
            Project object or None
        """
        return CarbonProject.query.get(project_id)

    def list_projects(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Dict[str, Any]:
        """
        List carbon projects with pagination

        Args:
            filters: Optional filters
            page: Page number
            per_page: Items per page

        Returns:
            Paginated projects list
        """
        try:
            query = CarbonProject.query

            if filters:
                if "project_type" in filters:
                    query = query.filter_by(project_type=filters["project_type"])
                if "country" in filters:
                    query = query.filter_by(country=filters["country"])

            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            return {
                "projects": [p.to_dict() for p in pagination.items],
                "total": pagination.total,
                "page": page,
                "per_page": per_page,
                "pages": pagination.pages,
            }
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return {"error": str(e)}

    def issue_credits(
        self,
        project_id: int,
        quantity: Decimal,
        vintage_year: int,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Issue carbon credits for a project

        Args:
            project_id: Project ID
            quantity: Quantity of credits to issue
            vintage_year: Vintage year
            metadata: Credit metadata

        Returns:
            Issued credit details
        """
        try:
            project = self.get_project(project_id)
            if not project:
                return {"error": "Project not found"}

            credit = CarbonCredit(
                project_id=project_id,
                quantity=quantity,
                vintage_year=vintage_year,
                **metadata,
            )
            db.session.add(credit)
            db.session.commit()

            logger.info(f"Issued {quantity} credits for project {project_id}")
            return {"credit_id": credit.id, "quantity": float(quantity)}
        except Exception as e:
            logger.error(f"Error issuing credits: {e}")
            db.session.rollback()
            return {"error": str(e)}

    def get_credit(self, credit_id: int) -> Optional[CarbonCredit]:
        """
        Get carbon credit by ID

        Args:
            credit_id: Credit ID

        Returns:
            Credit object or None
        """
        return CarbonCredit.query.get(credit_id)

    def list_credits(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Dict[str, Any]:
        """
        List carbon credits with pagination

        Args:
            filters: Optional filters
            page: Page number
            per_page: Items per page

        Returns:
            Paginated credits list
        """
        try:
            query = CarbonCredit.query

            if filters:
                if "project_id" in filters:
                    query = query.filter_by(project_id=filters["project_id"])
                if "vintage_year" in filters:
                    query = query.filter_by(vintage_year=filters["vintage_year"])
                if "credit_type" in filters:
                    query = query.filter_by(credit_type=filters["credit_type"])

            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            return {
                "credits": [c.to_dict() for c in pagination.items],
                "total": pagination.total,
                "page": page,
                "per_page": per_page,
                "pages": pagination.pages,
            }
        except Exception as e:
            logger.error(f"Error listing credits: {e}")
            return {"error": str(e)}
