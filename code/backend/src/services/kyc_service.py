"""
KYC Service for CarbonXchange Backend
Handles Know Your Customer verification processes
"""

import logging
from typing import Any, Dict
from ..models import db
from ..models.user import User, UserKYC, KYCStatus
from .audit_service import AuditService

logger = logging.getLogger(__name__)


class KYCService:
    """Service for KYC verification management"""

    def __init__(self) -> None:
        self.audit_service = AuditService()

    def submit_kyc(self, user_id: int, kyc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit KYC information for verification"""
        try:
            kyc = UserKYC.query.filter_by(user_id=user_id).first()
            if not kyc:
                kyc = UserKYC(user_id=user_id, status=KYCStatus.PENDING)
                db.session.add(kyc)

            # Update KYC data
            for key, value in kyc_data.items():
                if hasattr(kyc, key):
                    setattr(kyc, key, value)

            kyc.status = KYCStatus.PENDING
            db.session.commit()

            self.audit_service.log_event(
                user_id=user_id,
                event_type="kyc_submitted",
                event_category="kyc",
                event_description="KYC information submitted",
                success=True,
            )

            return {"status": "submitted", "kyc_id": kyc.id}
        except Exception as e:
            logger.error(f"Error submitting KYC: {e}")
            db.session.rollback()
            return {"error": str(e)}

    def verify_kyc(
        self, user_id: int, verified_by: str, notes: str = ""
    ) -> Dict[str, Any]:
        """Verify user KYC"""
        try:
            kyc = UserKYC.query.filter_by(user_id=user_id).first()
            if not kyc:
                return {"error": "KYC record not found"}

            kyc.status = KYCStatus.APPROVED
            kyc.verified_by = verified_by
            kyc.verification_notes = notes
            kyc.identity_verified = True

            user = User.query.get(user_id)
            if user:
                user.kyc_verified = True

            db.session.commit()

            self.audit_service.log_event(
                user_id=user_id,
                event_type="kyc_verified",
                event_category="kyc",
                event_description=f"KYC verified by {verified_by}",
                success=True,
            )

            return {"status": "verified", "kyc_id": kyc.id}
        except Exception as e:
            logger.error(f"Error verifying KYC: {e}")
            db.session.rollback()
            return {"error": str(e)}

    def reject_kyc(self, user_id: int, reason: str) -> Dict[str, Any]:
        """Reject user KYC"""
        try:
            kyc = UserKYC.query.filter_by(user_id=user_id).first()
            if not kyc:
                return {"error": "KYC record not found"}

            kyc.status = KYCStatus.REJECTED
            kyc.verification_notes = reason
            db.session.commit()

            self.audit_service.log_event(
                user_id=user_id,
                event_type="kyc_rejected",
                event_category="kyc",
                event_description=f"KYC rejected: {reason}",
                success=True,
            )

            return {"status": "rejected", "reason": reason}
        except Exception as e:
            logger.error(f"Error rejecting KYC: {e}")
            db.session.rollback()
            return {"error": str(e)}

    def get_kyc_status(self, user_id: int) -> Dict[str, Any]:
        """Get KYC status for user"""
        try:
            kyc = UserKYC.query.filter_by(user_id=user_id).first()
            if not kyc:
                return {"status": KYCStatus.NOT_STARTED.value}

            return {
                "status": kyc.status.value,
                "verification_level": kyc.verification_level,
                "identity_verified": kyc.identity_verified,
                "address_verified": kyc.address_verified,
            }
        except Exception as e:
            logger.error(f"Error getting KYC status: {e}")
            return {"error": str(e)}
