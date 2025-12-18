"""
User Service for CarbonXchange Backend
Handles user management and operations
"""

import logging
from typing import Any, Dict, Optional
from ..models import db
from ..models.user import User, UserProfile, UserStatus
from .audit_service import AuditService

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management"""

    def __init__(self) -> None:
        self.audit_service = AuditService()

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return User.query.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return User.query.filter_by(email=email).first()

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        try:
            user = User(**user_data)
            db.session.add(user)
            db.session.commit()

            # Create user profile
            profile = UserProfile(user_id=user.id)
            db.session.add(profile)
            db.session.commit()

            self.audit_service.log_event(
                user_id=user.id,
                event_type="user_created",
                event_category="user",
                event_description="User account created",
                success=True,
            )

            return {"user_id": user.id, "email": user.email}
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            db.session.rollback()
            return {"error": str(e)}

    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user information"""
        try:
            user = self.get_user(user_id)
            if not user:
                return {"error": "User not found"}

            for key, value in update_data.items():
                if hasattr(user, key) and key not in ["id", "uuid", "created_at"]:
                    setattr(user, key, value)

            db.session.commit()

            self.audit_service.log_event(
                user_id=user_id,
                event_type="user_updated",
                event_category="user",
                event_description="User information updated",
                success=True,
            )

            return {"user_id": user_id, "updated": True}
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            db.session.rollback()
            return {"error": str(e)}

    def update_profile(
        self, user_id: int, profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user profile"""
        try:
            profile = UserProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                profile = UserProfile(user_id=user_id)
                db.session.add(profile)

            for key, value in profile_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)

            db.session.commit()

            return {"user_id": user_id, "profile_updated": True}
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            db.session.rollback()
            return {"error": str(e)}

    def deactivate_user(self, user_id: int, reason: str = "") -> Dict[str, Any]:
        """Deactivate user account"""
        try:
            user = self.get_user(user_id)
            if not user:
                return {"error": "User not found"}

            user.status = UserStatus.INACTIVE
            db.session.commit()

            self.audit_service.log_event(
                user_id=user_id,
                event_type="user_deactivated",
                event_category="user",
                event_description=f"User deactivated: {reason}",
                success=True,
            )

            return {"user_id": user_id, "status": "deactivated"}
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            db.session.rollback()
            return {"error": str(e)}

    def activate_user(self, user_id: int) -> Dict[str, Any]:
        """Activate user account"""
        try:
            user = self.get_user(user_id)
            if not user:
                return {"error": "User not found"}

            user.status = UserStatus.ACTIVE
            db.session.commit()

            self.audit_service.log_event(
                user_id=user_id,
                event_type="user_activated",
                event_category="user",
                event_description="User activated",
                success=True,
            )

            return {"user_id": user_id, "status": "active"}
        except Exception as e:
            logger.error(f"Error activating user: {e}")
            db.session.rollback()
            return {"error": str(e)}

    def list_users(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Dict[str, Any]:
        """List users with pagination"""
        try:
            query = User.query

            if filters:
                if "status" in filters:
                    query = query.filter_by(status=filters["status"])
                if "role" in filters:
                    query = query.filter_by(role=filters["role"])

            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            return {
                "users": [u.to_dict() for u in pagination.items],
                "total": pagination.total,
                "page": page,
                "per_page": per_page,
                "pages": pagination.pages,
            }
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return {"error": str(e)}
