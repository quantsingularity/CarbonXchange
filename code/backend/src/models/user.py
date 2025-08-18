"""
User models for CarbonXchange Backend
Implements comprehensive user management with KYC and compliance features
"""
from datetime import datetime, timezone, timedelta
from enum import Enum
from decimal import Decimal
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import uuid

db = SQLAlchemy()

class UserStatus(Enum):
    """User account status enumeration"""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"
    UNDER_REVIEW = "under_review"

class KYCStatus(Enum):
    """KYC verification status enumeration"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class UserRole(Enum):
    """User role enumeration for RBAC"""
    INDIVIDUAL = "individual"
    CORPORATE = "corporate"
    BROKER = "broker"
    MARKET_MAKER = "market_maker"
    ADMIN = "admin"
    COMPLIANCE_OFFICER = "compliance_officer"

class User(db.Model):
    """Core user model with authentication and basic information"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    wallet_address = Column(String(42), unique=True, nullable=True, index=True)
    
    # Account status and role
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.PENDING)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.INDIVIDUAL)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime, nullable=True)
    email_verified_at = Column(DateTime, nullable=True)
    
    # Security fields
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    # Two-factor authentication
    two_factor_enabled = Column(Boolean, nullable=False, default=False)
    two_factor_secret = Column(String(32), nullable=True)
    backup_codes = Column(Text, nullable=True)  # JSON array of backup codes
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    kyc = relationship("UserKYC", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __init__(self, email, password, **kwargs):
        self.email = email.lower().strip()
        self.set_password(password)
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
        self.password_changed_at = datetime.now(timezone.utc)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    @hybrid_property
    def is_active(self):
        """Check if user account is active"""
        return self.status == UserStatus.ACTIVE
    
    @hybrid_property
    def is_locked(self):
        """Check if user account is locked"""
        if self.locked_until is None:
            return False
        return datetime.now(timezone.utc) < self.locked_until
    
    @hybrid_property
    def is_email_verified(self):
        """Check if email is verified"""
        return self.email_verified_at is not None
    
    @hybrid_property
    def is_kyc_approved(self):
        """Check if KYC is approved"""
        return self.kyc and self.kyc.status == KYCStatus.APPROVED
    
    def lock_account(self, duration_minutes=30):
        """Lock user account for specified duration"""
        self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
        self.failed_login_attempts = 0
    
    def unlock_account(self):
        """Unlock user account"""
        self.locked_until = None
        self.failed_login_attempts = 0
    
    def increment_failed_login(self):
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.lock_account()
    
    def reset_failed_login(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'email': self.email,
            'wallet_address': self.wallet_address,
            'status': self.status.value,
            'role': self.role.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'email_verified': self.is_email_verified,
            'kyc_approved': self.is_kyc_approved,
            'two_factor_enabled': self.two_factor_enabled
        }
        
        if include_sensitive:
            data.update({
                'failed_login_attempts': self.failed_login_attempts,
                'locked_until': self.locked_until.isoformat() if self.locked_until else None,
                'password_changed_at': self.password_changed_at.isoformat()
            })
        
        return data
    
    def __repr__(self):
        return f'<User {self.email}>'

class UserProfile(db.Model):
    """Extended user profile information"""
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    # Personal information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    middle_name = Column(String(100), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    nationality = Column(String(3), nullable=True)  # ISO 3166-1 alpha-3
    
    # Contact information
    phone_number = Column(String(20), nullable=True)
    phone_verified_at = Column(DateTime, nullable=True)
    
    # Address information
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state_province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(3), nullable=True)  # ISO 3166-1 alpha-3
    
    # Corporate information (for corporate users)
    company_name = Column(String(255), nullable=True)
    company_registration_number = Column(String(100), nullable=True)
    tax_id = Column(String(50), nullable=True)
    
    # Preferences
    timezone = Column(String(50), nullable=False, default='UTC')
    language = Column(String(5), nullable=False, default='en')
    currency = Column(String(3), nullable=False, default='USD')
    
    # Marketing preferences
    marketing_emails_enabled = Column(Boolean, nullable=False, default=True)
    trading_notifications_enabled = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    @hybrid_property
    def full_name(self):
        """Get full name"""
        parts = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(filter(None, parts))
    
    @hybrid_property
    def is_phone_verified(self):
        """Check if phone is verified"""
        return self.phone_verified_at is not None
    
    def to_dict(self):
        """Convert profile to dictionary"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'nationality': self.nationality,
            'phone_number': self.phone_number,
            'phone_verified': self.is_phone_verified,
            'company_name': self.company_name,
            'timezone': self.timezone,
            'language': self.language,
            'currency': self.currency,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<UserProfile {self.full_name}>'

class UserKYC(db.Model):
    """KYC (Know Your Customer) verification information"""
    __tablename__ = 'user_kyc'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    # KYC status and verification
    status = Column(SQLEnum(KYCStatus), nullable=False, default=KYCStatus.NOT_STARTED)
    verification_level = Column(Integer, nullable=False, default=0)  # 0-3 levels
    
    # Document information
    document_type = Column(String(50), nullable=True)  # passport, driver_license, national_id
    document_number = Column(String(100), nullable=True)
    document_country = Column(String(3), nullable=True)
    document_expiry_date = Column(DateTime, nullable=True)
    
    # Verification details
    submitted_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Review information
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Risk assessment
    risk_score = Column(Integer, nullable=True)  # 0-100
    risk_level = Column(String(20), nullable=True)  # low, medium, high
    
    # PEP (Politically Exposed Person) and sanctions screening
    pep_status = Column(Boolean, nullable=False, default=False)
    sanctions_status = Column(Boolean, nullable=False, default=False)
    screening_date = Column(DateTime, nullable=True)
    
    # Document storage (file paths or external IDs)
    identity_document_path = Column(String(500), nullable=True)
    proof_of_address_path = Column(String(500), nullable=True)
    additional_documents = Column(Text, nullable=True)  # JSON array
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="kyc", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    @hybrid_property
    def is_approved(self):
        """Check if KYC is approved"""
        return self.status == KYCStatus.APPROVED
    
    @hybrid_property
    def is_expired(self):
        """Check if KYC is expired"""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    @hybrid_property
    def days_until_expiry(self):
        """Get days until KYC expires"""
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.now(timezone.utc)
        return delta.days if delta.days > 0 else 0
    
    def approve(self, reviewer_id, verification_level=1, expires_in_days=365):
        """Approve KYC verification"""
        self.status = KYCStatus.APPROVED
        self.verification_level = verification_level
        self.reviewed_by = reviewer_id
        self.approved_at = datetime.now(timezone.utc)
        self.reviewed_at = datetime.now(timezone.utc)
        self.expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        self.rejection_reason = None
    
    def reject(self, reviewer_id, reason):
        """Reject KYC verification"""
        self.status = KYCStatus.REJECTED
        self.reviewed_by = reviewer_id
        self.rejected_at = datetime.now(timezone.utc)
        self.reviewed_at = datetime.now(timezone.utc)
        self.rejection_reason = reason
    
    def submit_for_review(self):
        """Submit KYC for review"""
        self.status = KYCStatus.PENDING_REVIEW
        self.submitted_at = datetime.now(timezone.utc)
    
    def to_dict(self, include_sensitive=False):
        """Convert KYC to dictionary"""
        data = {
            'id': self.id,
            'status': self.status.value,
            'verification_level': self.verification_level,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'days_until_expiry': self.days_until_expiry,
            'risk_level': self.risk_level,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_sensitive:
            data.update({
                'document_type': self.document_type,
                'document_country': self.document_country,
                'risk_score': self.risk_score,
                'pep_status': self.pep_status,
                'sanctions_status': self.sanctions_status,
                'rejection_reason': self.rejection_reason,
                'notes': self.notes
            })
        
        return data
    
    def __repr__(self):
        return f'<UserKYC {self.user_id} - {self.status.value}>'
