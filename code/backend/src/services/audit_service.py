"""
Audit Service for CarbonXchange Backend
Implements comprehensive audit logging for financial industry compliance
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from flask import current_app, request
from sqlalchemy import and_, desc, or_

from ..models import db
from ..models.user import UserAuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """
    Comprehensive audit service for regulatory compliance and security monitoring
    """

    def __init__(self):
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
        """
        Log audit event with comprehensive context

        Args:
            event_type: Type of event (e.g., 'login', 'trade_executed', 'kyc_approved')
            event_category: Category of event (e.g., 'authentication', 'trading', 'compliance')
            event_description: Human-readable description of the event
            user_id: ID of the user who performed the action (optional for system events)
            ip_address: IP address of the client
            session_id: Session identifier
            old_values: Previous values for change events
            new_values: New values for change events
            metadata: Additional event metadata
            success: Whether the event was successful
            error_message: Error message if event failed

        Returns:
            True if audit log created successfully
        """
        if not self.enabled:
            return True

        try:
            # Get IP address from request if not provided
            if ip_address is None and request:
                ip_address = request.environ.get(
                    "HTTP_X_FORWARDED_FOR", request.remote_addr
                )

            # Get user agent from request
            user_agent = request.headers.get("User-Agent", "") if request else ""

            # Create audit log entry
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
                metadata=metadata,
                success=success,
                error_message=error_message,
            )

            db.session.add(audit_log)
            db.session.commit()

            # Log to application logger for immediate visibility
            log_level = logging.INFO if success else logging.WARNING
            logger.log(
                log_level,
                f"AUDIT: {event_category}.{event_type} - {event_description} "
                f"(User: {user_id}, IP: {ip_address}, Success: {success})",
            )

            return True

        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")
            # Don't raise exception to avoid breaking the main operation
            return False

    def log_authentication_event(
        self,
        event_type: str,
        user_id: Optional[int] = None,
        email: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """
        Log authentication-related events

        Args:
            event_type: Type of authentication event
            user_id: User ID (if available)
            email: User email (for failed attempts where user_id might not be available)
            success: Whether the authentication was successful
            error_message: Error message for failed attempts
            metadata: Additional metadata

        Returns:
            True if audit log created successfully
        """
        description = f"Authentication event: {event_type}"
        if email:
            description += f" for {email}"

        event_metadata = metadata or {}
        if email and not user_id:
            event_metadata["email"] = email

        return self.log_event(
            event_type=event_type,
            event_category="authentication",
            event_description=description,
            user_id=user_id,
            success=success,
            error_message=error_message,
            metadata=event_metadata,
        )

    def log_trading_event(
        self,
        event_type: str,
        user_id: int,
        trade_data: Dict,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        Log trading-related events

        Args:
            event_type: Type of trading event
            user_id: User ID who performed the trade
            trade_data: Trading data (order details, execution details, etc.)
            success: Whether the trading operation was successful
            error_message: Error message for failed operations

        Returns:
            True if audit log created successfully
        """
        # Sanitize sensitive data
        sanitized_data = self._sanitize_trading_data(trade_data)

        description = f"Trading event: {event_type}"
        if "order_id" in sanitized_data:
            description += f" (Order: {sanitized_data['order_id']})"

        return self.log_event(
            event_type=event_type,
            event_category="trading",
            event_description=description,
            user_id=user_id,
            success=success,
            error_message=error_message,
            metadata=sanitized_data,
        )

    def log_compliance_event(
        self,
        event_type: str,
        user_id: Optional[int] = None,
        compliance_data: Optional[Dict] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        Log compliance-related events

        Args:
            event_type: Type of compliance event
            user_id: User ID (if applicable)
            compliance_data: Compliance-related data
            success: Whether the compliance check was successful
            error_message: Error message for failed checks

        Returns:
            True if audit log created successfully
        """
        description = f"Compliance event: {event_type}"

        return self.log_event(
            event_type=event_type,
            event_category="compliance",
            event_description=description,
            user_id=user_id,
            success=success,
            error_message=error_message,
            metadata=compliance_data,
        )

    def log_kyc_event(
        self,
        event_type: str,
        user_id: int,
        kyc_data: Dict,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        Log KYC-related events

        Args:
            event_type: Type of KYC event
            user_id: User ID
            kyc_data: KYC-related data
            success: Whether the KYC operation was successful
            error_message: Error message for failed operations

        Returns:
            True if audit log created successfully
        """
        # Sanitize sensitive KYC data
        sanitized_data = self._sanitize_kyc_data(kyc_data)

        description = f"KYC event: {event_type}"
        if "verification_level" in sanitized_data:
            description += f" (Level: {sanitized_data['verification_level']})"

        return self.log_event(
            event_type=event_type,
            event_category="kyc",
            event_description=description,
            user_id=user_id,
            success=success,
            error_message=error_message,
            metadata=sanitized_data,
        )

    def log_data_change(
        self,
        event_type: str,
        user_id: int,
        table_name: str,
        record_id: int,
        old_values: Dict,
        new_values: Dict,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        Log data change events for audit trail

        Args:
            event_type: Type of data change event
            user_id: User ID who made the change
            table_name: Name of the database table
            record_id: ID of the record that was changed
            old_values: Previous values
            new_values: New values
            success: Whether the change was successful
            error_message: Error message for failed changes

        Returns:
            True if audit log created successfully
        """
        description = f"Data change: {event_type} in {table_name} (ID: {record_id})"

        # Sanitize sensitive data
        sanitized_old = self._sanitize_data_values(old_values)
        sanitized_new = self._sanitize_data_values(new_values)

        metadata = {"table_name": table_name, "record_id": record_id}

        return self.log_event(
            event_type=event_type,
            event_category="data_change",
            event_description=description,
            user_id=user_id,
            old_values=sanitized_old,
            new_values=sanitized_new,
            metadata=metadata,
            success=success,
            error_message=error_message,
        )

    def log_system_event(
        self,
        event_type: str,
        event_description: str,
        metadata: Optional[Dict] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        Log system-level events

        Args:
            event_type: Type of system event
            event_description: Description of the system event
            metadata: Additional metadata
            success: Whether the system operation was successful
            error_message: Error message for failed operations

        Returns:
            True if audit log created successfully
        """
        return self.log_event(
            event_type=event_type,
            event_category="system",
            event_description=event_description,
            user_id=None,  # System events don't have a user
            metadata=metadata,
            success=success,
            error_message=error_message,
        )

    def get_audit_logs(
        self,
        user_id: Optional[int] = None,
        event_category: Optional[str] = None,
        event_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        success: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict]:
        """
        Retrieve audit logs with filtering

        Args:
            user_id: Filter by user ID
            event_category: Filter by event category
            event_type: Filter by event type
            start_date: Filter by start date
            end_date: Filter by end date
            success: Filter by success status
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of audit log dictionaries
        """
        try:
            query = UserAuditLog.query

            # Apply filters
            if user_id is not None:
                query = query.filter(UserAuditLog.user_id == user_id)

            if event_category:
                query = query.filter(UserAuditLog.event_category == event_category)

            if event_type:
                query = query.filter(UserAuditLog.event_type == event_type)

            if start_date:
                query = query.filter(UserAuditLog.created_at >= start_date)

            if end_date:
                query = query.filter(UserAuditLog.created_at <= end_date)

            if success is not None:
                query = query.filter(UserAuditLog.success == success)

            # Order by most recent first
            query = query.order_by(desc(UserAuditLog.created_at))

            # Apply pagination
            audit_logs = query.offset(offset).limit(limit).all()

            return [log.to_dict() for log in audit_logs]

        except Exception as e:
            logger.error(f"Failed to retrieve audit logs: {str(e)}")
            return []

    def get_user_activity_summary(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get user activity summary for the specified period

        Args:
            user_id: User ID
            days: Number of days to look back

        Returns:
            Dictionary containing activity summary
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            # Get total events
            total_events = UserAuditLog.query.filter(
                and_(
                    UserAuditLog.user_id == user_id,
                    UserAuditLog.created_at >= start_date,
                )
            ).count()

            # Get events by category
            category_query = (
                db.session.query(
                    UserAuditLog.event_category,
                    db.func.count(UserAuditLog.id).label("count"),
                )
                .filter(
                    and_(
                        UserAuditLog.user_id == user_id,
                        UserAuditLog.created_at >= start_date,
                    )
                )
                .group_by(UserAuditLog.event_category)
                .all()
            )

            events_by_category = {
                row.event_category: row.count for row in category_query
            }

            # Get failed events
            failed_events = UserAuditLog.query.filter(
                and_(
                    UserAuditLog.user_id == user_id,
                    UserAuditLog.created_at >= start_date,
                    UserAuditLog.success == False,
                )
            ).count()

            # Get recent events
            recent_events = (
                UserAuditLog.query.filter(
                    and_(
                        UserAuditLog.user_id == user_id,
                        UserAuditLog.created_at >= start_date,
                    )
                )
                .order_by(desc(UserAuditLog.created_at))
                .limit(10)
                .all()
            )

            return {
                "user_id": user_id,
                "period_days": days,
                "total_events": total_events,
                "failed_events": failed_events,
                "success_rate": (
                    (total_events - failed_events) / total_events
                    if total_events > 0
                    else 1.0
                ),
                "events_by_category": events_by_category,
                "recent_events": [event.to_dict() for event in recent_events],
            }

        except Exception as e:
            logger.error(f"Failed to get user activity summary: {str(e)}")
            return {
                "user_id": user_id,
                "period_days": days,
                "total_events": 0,
                "failed_events": 0,
                "success_rate": 0.0,
                "events_by_category": {},
                "recent_events": [],
            }

    def get_security_events(
        self, user_id: Optional[int] = None, hours: int = 24
    ) -> List[Dict]:
        """
        Get security-related events for monitoring

        Args:
            user_id: Filter by user ID (optional)
            hours: Number of hours to look back

        Returns:
            List of security event dictionaries
        """
        try:
            start_date = datetime.utcnow() - timedelta(hours=hours)

            security_categories = ["authentication", "security", "compliance"]
            security_event_types = [
                "login_failed",
                "login_blocked",
                "mfa_failed",
                "password_change_failed",
                "suspicious_activity",
                "account_locked",
                "unauthorized_access",
            ]

            query = UserAuditLog.query.filter(
                and_(
                    UserAuditLog.created_at >= start_date,
                    or_(
                        UserAuditLog.event_category.in_(security_categories),
                        UserAuditLog.event_type.in_(security_event_types),
                        UserAuditLog.success == False,
                    ),
                )
            )

            if user_id is not None:
                query = query.filter(UserAuditLog.user_id == user_id)

            security_events = (
                query.order_by(desc(UserAuditLog.created_at)).limit(100).all()
            )

            return [event.to_dict() for event in security_events]

        except Exception as e:
            logger.error(f"Failed to get security events: {str(e)}")
            return []

    def cleanup_old_logs(self, retention_days: Optional[int] = None) -> int:
        """
        Clean up old audit logs based on retention policy

        Args:
            retention_days: Number of days to retain logs (uses config if not provided)

        Returns:
            Number of logs deleted
        """
        try:
            if retention_days is None:
                retention_days = current_app.config.get(
                    "DATA_RETENTION_DAYS", 2555
                )  # 7 years default

            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

            # Delete old logs
            deleted_count = UserAuditLog.query.filter(
                UserAuditLog.created_at < cutoff_date
            ).delete()

            db.session.commit()

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old audit logs")

                # Log the cleanup operation
                self.log_system_event(
                    event_type="audit_cleanup",
                    event_description=f"Cleaned up {deleted_count} audit logs older than {retention_days} days",
                    metadata={
                        "deleted_count": deleted_count,
                        "retention_days": retention_days,
                    },
                )

            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup old audit logs: {str(e)}")
            return 0

    def _sanitize_trading_data(self, data: Dict) -> Dict:
        """Sanitize trading data to remove sensitive information"""
        sensitive_fields = ["api_key", "private_key", "password", "secret"]
        sanitized = data.copy()

        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = "[REDACTED]"

        return sanitized

    def _sanitize_kyc_data(self, data: Dict) -> Dict:
        """Sanitize KYC data to remove sensitive personal information"""
        sensitive_fields = [
            "document_number",
            "ssn",
            "tax_id",
            "passport_number",
            "drivers_license_number",
            "bank_account_number",
        ]
        sanitized = data.copy()

        for field in sensitive_fields:
            if field in sanitized:
                # Keep only last 4 characters for identification
                value = str(sanitized[field])
                if len(value) > 4:
                    sanitized[field] = "*" * (len(value) - 4) + value[-4:]
                else:
                    sanitized[field] = "[REDACTED]"

        return sanitized

    def _sanitize_data_values(self, data: Dict) -> Dict:
        """Sanitize data values to remove sensitive information"""
        sensitive_fields = [
            "password",
            "password_hash",
            "mfa_secret",
            "api_key",
            "private_key",
            "secret",
            "token",
            "ssn",
            "tax_id",
            "bank_account_number",
        ]
        sanitized = data.copy()

        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = "[REDACTED]"

        return sanitized
