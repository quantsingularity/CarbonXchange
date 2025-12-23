"""
User models for CarbonXchange Backend
Implements comprehensive user management with KYC and compliance features
"""

from typing import Any
import re
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON, Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class UserStatus(Enum):
    """User account status enumeration"""

    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"
    UNDER_REVIEW = "under_review"
    LOCKED = "locked"
    DORMANT = "dormant"


class KYCStatus(Enum):
    """KYC verification status enumeration"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REQUIRES_UPDATE = "requires_update"


class UserRole(Enum):
    """User role enumeration for RBAC"""

    INDIVIDUAL = "individual"
    CORPORATE = "corporate"
    INSTITUTIONAL = "institutional"
    BROKER = "broker"
    MARKET_MAKER = "market_maker"
    ADMIN = "admin"
    COMPLIANCE_OFFICER = "compliance_officer"
    AUDITOR = "auditor"
    SYSTEM = "system"


class RiskLevel(Enum):
    """Risk assessment levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    PROHIBITED = "prohibited"


class DocumentType(Enum):
    """KYC document types"""

    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    NATIONAL_ID = "national_id"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    ARTICLES_OF_INCORPORATION = "articles_of_incorporation"
    CERTIFICATE_OF_INCORPORATION = "certificate_of_incorporation"
    MEMORANDUM_OF_ASSOCIATION = "memorandum_of_association"
    BOARD_RESOLUTION = "board_resolution"
    BENEFICIAL_OWNERSHIP = "beneficial_ownership"
    TAX_CERTIFICATE = "tax_certificate"
    REGULATORY_LICENSE = "regulatory_license"


class User(db.Model):
    """Core user model with authentication and basic information"""

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    uuid = Column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True, index=True)
    date_of_birth = Column(DateTime, nullable=True)
    status = Column(
        SQLEnum(UserStatus), nullable=False, default=UserStatus.PENDING, index=True
    )
    role = Column(
        SQLEnum(UserRole), nullable=False, default=UserRole.INDIVIDUAL, index=True
    )
    is_verified = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)
    password_changed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    mfa_enabled = Column(Boolean, nullable=False, default=False)
    mfa_secret = Column(String(32), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_activity_at = Column(DateTime, nullable=True, index=True)
    risk_level = Column(
        SQLEnum(RiskLevel), nullable=False, default=RiskLevel.MEDIUM, index=True
    )
    risk_score = Column(Numeric(5, 2), nullable=True)
    risk_last_assessed = Column(DateTime, nullable=True)
    locked_until = Column(DateTime, nullable=True)
    suspension_reason = Column(Text, nullable=True)
    suspension_until = Column(DateTime, nullable=True)
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    kyc_records = relationship(
        "UserKYC", back_populates="user", cascade="all, delete-orphan"
    )
    sessions = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs = relationship(
        "UserAuditLog", back_populates="user", cascade="all, delete-orphan"
    )

    def __init__(
        self, email: Any, password: Any, first_name: Any, last_name: Any, **kwargs
    ) -> Any:
        self.email = email.lower().strip()
        self.set_password(password)
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def set_password(self, password: Any) -> Any:
        """Set password with security validation"""
        if not self._validate_password(password):
            raise ValueError("Password does not meet security requirements")
        self.password_hash = generate_password_hash(
            password, method="pbkdf2:sha256:150000"
        )
        self.password_changed_at = datetime.utcnow()

    def check_password(self, password: Any) -> Any:
        """Check password and handle failed attempts"""
        if self.is_locked:
            return False
        is_valid = check_password_hash(self.password_hash, password)
        if not is_valid:
            self.failed_login_attempts += 1
            if self.failed_login_attempts >= 5:
                self.lock_account(duration_minutes=30)
        else:
            self.failed_login_attempts = 0
            self.last_login_at = datetime.utcnow()
        return is_valid

    def _validate_password(self, password: Any) -> Any:
        """Validate password against security requirements"""
        if len(password) < 8:
            return False
        if not re.search("[A-Z]", password):
            return False
        if not re.search("[a-z]", password):
            return False
        if not re.search("\\d", password):
            return False
        if not re.search('[!@#$%^&*(),.?":{}|<>]', password):
            return False
        return True

    @hybrid_property
    def is_locked(self) -> Any:
        """Check if account is currently locked"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until

    @hybrid_property
    def is_suspended(self) -> Any:
        """Check if account is currently suspended"""
        if self.suspension_until is None:
            return self.status == UserStatus.SUSPENDED
        return datetime.utcnow() < self.suspension_until

    @hybrid_property
    def full_name(self) -> Any:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"

    @hybrid_property
    def is_kyc_approved(self) -> Any:
        """Check if user has approved KYC"""
        if not self.kyc_records:
            return False
        latest_kyc = max(self.kyc_records, key=lambda x: x.created_at)
        return latest_kyc.status == KYCStatus.APPROVED

    def lock_account(self, duration_minutes: Any = 30) -> Any:
        """Lock account for specified duration"""
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.status = UserStatus.LOCKED

    def unlock_account(self) -> Any:
        """Unlock account"""
        self.locked_until = None
        self.failed_login_attempts = 0
        if self.status == UserStatus.LOCKED:
            self.status = UserStatus.ACTIVE

    def suspend_account(self, reason: Any, duration_days: Any = None) -> Any:
        """Suspend account with reason"""
        self.status = UserStatus.SUSPENDED
        self.suspension_reason = reason
        if duration_days:
            self.suspension_until = datetime.utcnow() + timedelta(days=duration_days)

    def activate_account(self) -> Any:
        """Activate account"""
        self.status = UserStatus.ACTIVE
        self.suspension_reason = None
        self.suspension_until = None
        self.locked_until = None

    def update_risk_assessment(self, risk_level: Any, risk_score: Any = None) -> Any:
        """Update user risk assessment"""
        self.risk_level = risk_level
        if risk_score is not None:
            self.risk_score = Decimal(str(risk_score))
        self.risk_last_assessed = datetime.utcnow()

    def to_dict(self, include_sensitive: Any = False) -> Any:
        """Convert user to dictionary"""
        data = {
            "id": self.id,
            "uuid": self.uuid,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "status": self.status.value,
            "role": self.role.value,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "is_kyc_approved": self.is_kyc_approved,
            "risk_level": self.risk_level.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": (
                self.last_login_at.isoformat() if self.last_login_at else None
            ),
            "mfa_enabled": self.mfa_enabled,
        }
        if include_sensitive:
            data.update(
                {
                    "risk_score": float(self.risk_score) if self.risk_score else None,
                    "failed_login_attempts": self.failed_login_attempts,
                    "is_locked": self.is_locked,
                    "is_suspended": self.is_suspended,
                    "last_login_ip": self.last_login_ip,
                }
            )
        return data

    def __repr__(self) -> Any:
        return f"<User {self.email}>"


class UserProfile(db.Model):
    """Extended user profile information"""

    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    middle_name = Column(String(100), nullable=True)
    nationality = Column(String(3), nullable=True)
    country_of_residence = Column(String(3), nullable=True)
    address_line_1 = Column(String(255), nullable=True)
    address_line_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state_province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(3), nullable=True)
    occupation = Column(String(100), nullable=True)
    employer = Column(String(255), nullable=True)
    annual_income = Column(Numeric(15, 2), nullable=True)
    source_of_funds = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)
    company_registration_number = Column(String(100), nullable=True)
    company_tax_id = Column(String(100), nullable=True)
    company_incorporation_country = Column(String(3), nullable=True)
    company_business_type = Column(String(100), nullable=True)
    trading_experience = Column(String(50), nullable=True)
    investment_objectives = Column(Text, nullable=True)
    risk_tolerance = Column(String(20), nullable=True)
    preferred_language = Column(String(5), nullable=True, default="en")
    timezone = Column(String(50), nullable=True, default="UTC")
    marketing_consent = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    user = relationship("User", back_populates="profile")

    def to_dict(self) -> Any:
        """Convert profile to dictionary"""
        return {
            "middle_name": self.middle_name,
            "nationality": self.nationality,
            "country_of_residence": self.country_of_residence,
            "address": {
                "line_1": self.address_line_1,
                "line_2": self.address_line_2,
                "city": self.city,
                "state_province": self.state_province,
                "postal_code": self.postal_code,
                "country": self.country,
            },
            "occupation": self.occupation,
            "employer": self.employer,
            "annual_income": float(self.annual_income) if self.annual_income else None,
            "source_of_funds": self.source_of_funds,
            "company": (
                {
                    "name": self.company_name,
                    "registration_number": self.company_registration_number,
                    "tax_id": self.company_tax_id,
                    "incorporation_country": self.company_incorporation_country,
                    "business_type": self.company_business_type,
                }
                if self.company_name
                else None
            ),
            "trading": {
                "experience": self.trading_experience,
                "objectives": self.investment_objectives,
                "risk_tolerance": self.risk_tolerance,
            },
            "preferences": {
                "language": self.preferred_language,
                "timezone": self.timezone,
                "marketing_consent": self.marketing_consent,
            },
        }


class UserKYC(db.Model):
    """KYC verification records"""

    __tablename__ = "user_kyc"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(
        SQLEnum(KYCStatus), nullable=False, default=KYCStatus.NOT_STARTED, index=True
    )
    verification_level = Column(Integer, nullable=False, default=1)
    documents_submitted = Column(JSON, nullable=True)
    documents_verified = Column(JSON, nullable=True)
    identity_verified = Column(Boolean, nullable=False, default=False)
    address_verified = Column(Boolean, nullable=False, default=False)
    phone_verified = Column(Boolean, nullable=False, default=False)
    email_verified = Column(Boolean, nullable=False, default=False)
    verification_method = Column(String(50), nullable=True)
    verified_by = Column(String(255), nullable=True)
    verification_notes = Column(Text, nullable=True)
    aml_screening_status = Column(String(20), nullable=True)
    pep_status = Column(Boolean, nullable=False, default=False)
    sanctions_screening = Column(String(20), nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    rejection_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    user = relationship("User", back_populates="kyc_records")
    documents = relationship(
        "KYCDocument", back_populates="kyc_record", cascade="all, delete-orphan"
    )

    def is_expired(self) -> Any:
        """Check if KYC verification has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def days_until_expiry(self) -> Any:
        """Get days until KYC expiry"""
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.utcnow()
        return delta.days if delta.days > 0 else 0

    def to_dict(self) -> Any:
        """Convert KYC record to dictionary"""
        return {
            "id": self.id,
            "status": self.status.value,
            "verification_level": self.verification_level,
            "identity_verified": self.identity_verified,
            "address_verified": self.address_verified,
            "phone_verified": self.phone_verified,
            "email_verified": self.email_verified,
            "aml_screening_status": self.aml_screening_status,
            "pep_status": self.pep_status,
            "sanctions_screening": self.sanctions_screening,
            "submitted_at": (
                self.submitted_at.isoformat() if self.submitted_at else None
            ),
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_expired": self.is_expired(),
            "days_until_expiry": self.days_until_expiry(),
            "documents_count": len(self.documents) if self.documents else 0,
        }


class KYCDocument(db.Model):
    """KYC document storage and verification"""

    __tablename__ = "kyc_documents"
    id = Column(Integer, primary_key=True)
    kyc_record_id = Column(
        Integer, ForeignKey("user_kyc.id"), nullable=False, index=True
    )
    document_type: "Column[Any]" = Column(
        SQLEnum(DocumentType), nullable=False, index=True
    )
    document_number = Column(String(100), nullable=True)
    issuing_country = Column(String(3), nullable=True)
    issuing_authority = Column(String(255), nullable=True)
    issue_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False)
    mime_type = Column(String(100), nullable=False)
    verification_status = Column(String(20), nullable=False, default="pending")
    verification_notes = Column(Text, nullable=True)
    verified_by = Column(String(255), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    kyc_record = relationship("UserKYC", back_populates="documents")

    def is_expired(self) -> Any:
        """Check if document has expired"""
        if self.expiry_date is None:
            return False
        return datetime.utcnow().date() > self.expiry_date.date()

    def to_dict(self) -> Any:
        """Convert document to dictionary"""
        return {
            "id": self.id,
            "document_type": self.document_type.value,
            "document_number": self.document_number,
            "issuing_country": self.issuing_country,
            "issuing_authority": self.issuing_authority,
            "issue_date": self.issue_date.isoformat() if self.issue_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "verification_status": self.verification_status,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "uploaded_at": self.uploaded_at.isoformat(),
            "is_expired": self.is_expired(),
        }


class UserSession(db.Model):
    """User session tracking for security"""

    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_token = Column(String(255), nullable=False, unique=True, index=True)
    refresh_token = Column(String(255), nullable=True, unique=True, index=True)
    device_fingerprint = Column(String(255), nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    last_activity_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    terminated_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="sessions")

    def is_expired(self) -> Any:
        """Check if session has expired"""
        return datetime.utcnow() > self.expires_at

    def terminate(self) -> Any:
        """Terminate session"""
        self.is_active = False
        self.terminated_at = datetime.utcnow()

    def to_dict(self) -> Any:
        """Convert session to dictionary"""
        return {
            "id": self.id,
            "device_fingerprint": self.device_fingerprint,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_activity_at": self.last_activity_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_expired": self.is_expired(),
        }


class UserAuditLog(db.Model):
    """Comprehensive audit logging for user activities"""

    __tablename__ = "user_audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    event_category = Column(String(30), nullable=False, index=True)
    event_description = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    event_metadata = Column(JSON, nullable=True)
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    user = relationship("User", back_populates="audit_logs")

    def to_dict(self) -> Any:
        """Convert audit log to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_type": self.event_type,
            "event_category": self.event_category,
            "event_description": self.event_description,
            "ip_address": self.ip_address,
            "success": self.success,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "metadata": self.event_metadata,
        }
