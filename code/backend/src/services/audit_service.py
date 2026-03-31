"""
Audit Service for CarbonXchange Backend
Implements comprehensive audit logging for financial industry compliance
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from flask import current_app, request
from sqlalchemy import and_, desc

from ..models import db
from ..models.user import UserAuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """
    Comprehensive audit service for regulatory compliance and security monitoring
    """

    def __init__(self) -> None:
        self.enabled = (
            current_app.config.get("AUDIT_LOG_ENABLED", True) if current_app else True
        )

    def log_event(
        self,
        event_type: str,
        event_category: str,
        event_description: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> bool:
        """Log audit event with comprehensive context"""
        if not self.enabled:
            return True
        try:
            if ip_address is None and request:
                ip_address = request.environ.get(
                    "HTTP_X_FORWARDED_FOR", request.remote_addr
                )
            user_agent = request.headers.get("User-Agent", "") if request else ""
            audit_log = UserAuditLog(
                user_id=user_id,
                event_type=event_type,
                event_category=event_category,
                event_description=event_description,
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                old_values=old_values,
                new_values=new_values,
                event_metadata=metadata,
                success=success,
                error_message=error_message,
            )
            db.session.add(audit_log)
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            db.session.rollback()
            return False

    def log_authentication(
        self,
        email: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_id: Optional[int] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """Log authentication events"""
        event_metadata = metadata or {}
        if email:
            event_metadata["email"] = email
        return self.log_event(
            event_type="authentication",
            event_category="security",
            event_description=f"Authentication {'successful' if success else 'failed'} for {email}",
            user_id=user_id,
            ip_address=ip_address,
            metadata=event_metadata,
            success=success,
            error_message=error_message,
        )

    def log_data_access(
        self,
        table_name: str,
        record_id: Any,
        action: str,
        user_id: Optional[int] = None,
        sanitized_data: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """Log data access events"""
        return self.log_event(
            event_type=f"data_{action}",
            event_category="data_access",
            event_description=f"{action.capitalize()} operation on {table_name} record {record_id}",
            user_id=user_id,
            metadata={
                "table_name": table_name,
                "record_id": record_id,
                **(metadata or {}),
            },
            new_values=sanitized_data,
        )

    def log_compliance_event(
        self,
        event_type: str,
        description: str,
        user_id: Optional[int] = None,
        compliance_data: Optional[Dict] = None,
    ) -> bool:
        """Log compliance-related events"""
        return self.log_event(
            event_type=event_type,
            event_category="compliance",
            event_description=description,
            user_id=user_id,
            metadata=compliance_data,
        )

    def get_user_audit_trail(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0,
        event_category: Optional[str] = None,
    ) -> List[Dict]:
        """Get audit trail for a specific user"""
        try:
            query = UserAuditLog.query.filter_by(user_id=user_id)
            if event_category:
                query = query.filter_by(event_category=event_category)
            logs = (
                query.order_by(desc(UserAuditLog.created_at))
                .limit(limit)
                .offset(offset)
                .all()
            )
            return [log.to_dict() for log in logs]
        except Exception as e:
            logger.error(f"Failed to get audit trail: {e}")
            return []

    def get_security_events(
        self,
        hours: int = 24,
        event_type: Optional[str] = None,
    ) -> List[Dict]:
        """Get security events within timeframe"""
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            query = UserAuditLog.query.filter(
                and_(
                    UserAuditLog.event_category == "security",
                    UserAuditLog.created_at >= cutoff,
                )
            )
            if event_type:
                query = query.filter_by(event_type=event_type)
            logs = query.order_by(desc(UserAuditLog.created_at)).all()
            return [log.to_dict() for log in logs]
        except Exception as e:
            logger.error(f"Failed to get security events: {e}")
            return []
