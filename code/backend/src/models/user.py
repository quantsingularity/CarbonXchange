"""
User models for CarbonXchange Backend
Implements comprehensive user management with KYC and compliance features
"""
from datetime import datetime, timezone, timedelta
from enum import Enum
from decimal import Decimal
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Numeric, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID
import uuid
import re

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
    __tablename__ = 'users'
    
    # Primary identification
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Basic information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True, index=True)
    date_of_birth = Column(DateTime, nullable=True)
    
    # Account management
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.PENDING, index=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.INDIVIDUAL, index=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Security and authentication
    failed_login_attempts = Column(Integer, nullable=False, default=0)
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # IPv6 support
    password_changed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    mfa_enabled = Column(Boolean, nullable=False, default=False)
    mfa_secret = Column(String(32), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_at = Column(DateTime, nullable=True, index=True)
    
    # Compliance and risk
    risk_level = Column(SQLEnum(RiskLevel), nullable=False, default=RiskLevel.MEDIUM, index=True)
    risk_score = Column(Numeric(5, 2), nullable=True)  # 0.00 to 999.99
    risk_last_assessed = Column(DateTime, nullable=True)
    
    # Account lockout and suspension
    locked_until = Column(DateTime, nullable=True)
    suspension_reason = Column(Text, nullable=True)
    suspension_until = Column(DateTime, nullable=True)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    kyc_records = relationship("UserKYC", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("UserAuditLog", back_populates="user", cascade="all, delete-orphan")
    
    def __init__(self, email, password, first_name, last_name, **kwargs):
        self.email = email.lower().strip()
        self.set_password(password)
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password):
        """Set password with security validation"""
        if not self._validate_password(password):
            raise ValueError("Password does not meet security requirements")
        
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256:150000')
        self.password_changed_at = datetime.utcnow()
    
    def check_password(self, password):
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
    
    def _validate_password(self, password):
        """Validate password against security requirements"""
        if len(password) < 8:
            return False
        
        # Check for uppercase, lowercase, digit, and special character
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        
        return True
    
    @hybrid_property
    def is_locked(self):
        """Check if account is currently locked"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    @hybrid_property
    def is_suspended(self):
        """Check if account is currently suspended"""
        if self.suspension_until is None:
            return self.status == UserStatus.SUSPENDED
        return datetime.utcnow() < self.suspension_until
    
    @hybrid_property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @hybrid_property
    def is_kyc_approved(self):
        """Check if user has approved KYC"""
        if not self.kyc_records:
            return False
        latest_kyc = max(self.kyc_records, key=lambda x: x.created_at)
        return latest_kyc.status == KYCStatus.APPROVED
    
    def lock_account(self, duration_minutes=30):
        """Lock account for specified duration"""
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.status = UserStatus.LOCKED
    
    def unlock_account(self):
        """Unlock account"""
        self.locked_until = None
        self.failed_login_attempts = 0
        if self.status == UserStatus.LOCKED:
            self.status = UserStatus.ACTIVE
    
    def suspend_account(self, reason, duration_days=None):
        """Suspend account with reason"""
        self.status = UserStatus.SUSPENDED
        self.suspension_reason = reason
        if duration_days:
            self.suspension_until = datetime.utcnow() + timedelta(days=duration_days)
    
    def activate_account(self):
        """Activate account"""
        self.status = UserStatus.ACTIVE
        self.suspension_reason = None
        self.suspension_until = None
        self.locked_until = None
    
    def update_risk_assessment(self, risk_level, risk_score=None):
        """Update user risk assessment"""
        self.risk_level = risk_level
        if risk_score is not None:
            self.risk_score = Decimal(str(risk_score))
        self.risk_last_assessed = datetime.utcnow()
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'status': self.status.value,
            'role': self.role.value,
            'is_verified': self.is_verified,
            'is_active': self.is_active,
            'is_kyc_approved': self.is_kyc_approved,
            'risk_level': self.risk_level.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'mfa_enabled': self.mfa_enabled
        }
        
        if include_sensitive:
            data.update({
                'risk_score': float(self.risk_score) if self.risk_score else None,
                'failed_login_attempts': self.failed_login_attempts,
                'is_locked': self.is_locked,
                'is_suspended': self.is_suspended,
                'last_login_ip': self.last_login_ip
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
    middle_name = Column(String(100), nullable=True)
    nationality = Column(String(3), nullable=True)  # ISO 3166-1 alpha-3
    country_of_residence = Column(String(3), nullable=True)  # ISO 3166-1 alpha-3
    
    # Address information
    address_line_1 = Column(String(255), nullable=True)
    address_line_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state_province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(3), nullable=True)  # ISO 3166-1 alpha-3
    
    # Professional information
    occupation = Column(String(100), nullable=True)
    employer = Column(String(255), nullable=True)
    annual_income = Column(Numeric(15, 2), nullable=True)
    source_of_funds = Column(String(255), nullable=True)
    
    # Corporate information (for corporate accounts)
    company_name = Column(String(255), nullable=True)
    company_registration_number = Column(String(100), nullable=True)
    company_tax_id = Column(String(100), nullable=True)
    company_incorporation_country = Column(String(3), nullable=True)
    company_business_type = Column(String(100), nullable=True)
    
    # Trading preferences
    trading_experience = Column(String(50), nullable=True)  # beginner, intermediate, advanced
    investment_objectives = Column(Text, nullable=True)
    risk_tolerance = Column(String(20), nullable=True)  # conservative, moderate, aggressive
    
    # Communication preferences
    preferred_language = Column(String(5), nullable=True, default='en')  # ISO 639-1
    timezone = Column(String(50), nullable=True, default='UTC')
    marketing_consent = Column(Boolean, nullable=False, default=False)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    def to_dict(self):
        """Convert profile to dictionary"""
        return {
            'middle_name': self.middle_name,
            'nationality': self.nationality,
            'country_of_residence': self.country_of_residence,
            'address': {
                'line_1': self.address_line_1,
                'line_2': self.address_line_2,
                'city': self.city,
                'state_province': self.state_province,
                'postal_code': self.postal_code,
                'country': self.country
            },
            'occupation': self.occupation,
            'employer': self.employer,
            'annual_income': float(self.annual_income) if self.annual_income else None,
            'source_of_funds': self.source_of_funds,
            'company': {
                'name': self.company_name,
                'registration_number': self.company_registration_number,
                'tax_id': self.company_tax_id,
                'incorporation_country': self.company_incorporation_country,
                'business_type': self.company_business_type
            } if self.company_name else None,
            'trading': {
                'experience': self.trading_experience,
                'objectives': self.investment_objectives,
                'risk_tolerance': self.risk_tolerance
            },
            'preferences': {
                'language': self.preferred_language,
                'timezone': self.timezone,
                'marketing_consent': self.marketing_consent
            }
        }

class UserKYC(db.Model):
    """KYC verification records"""
    __tablename__ = 'user_kyc'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # KYC status and workflow
    status = Column(SQLEnum(KYCStatus), nullable=False, default=KYCStatus.NOT_STARTED, index=True)
    verification_level = Column(Integer, nullable=False, default=1)  # 1=basic, 2=enhanced, 3=premium
    
    # Document verification
    documents_submitted = Column(JSON, nullable=True)  # List of submitted document types
    documents_verified = Column(JSON, nullable=True)   # List of verified document types
    
    # Identity verification
    identity_verified = Column(Boolean, nullable=False, default=False)
    address_verified = Column(Boolean, nullable=False, default=False)
    phone_verified = Column(Boolean, nullable=False, default=False)
    email_verified = Column(Boolean, nullable=False, default=False)
    
    # Verification details
    verification_method = Column(String(50), nullable=True)  # manual, automated, third_party
    verified_by = Column(String(255), nullable=True)  # Staff member or system
    verification_notes = Column(Text, nullable=True)
    
    # Risk assessment
    aml_screening_status = Column(String(20), nullable=True)  # clear, flagged, under_review
    pep_status = Column(Boolean, nullable=False, default=False)  # Politically Exposed Person
    sanctions_screening = Column(String(20), nullable=True)  # clear, flagged, under_review
    
    # Dates and expiry
    submitted_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Rejection details
    rejection_reason = Column(Text, nullable=True)
    rejection_date = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="kyc_records")
    documents = relationship("KYCDocument", back_populates="kyc_record", cascade="all, delete-orphan")
    
    def is_expired(self):
        """Check if KYC verification has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def days_until_expiry(self):
        """Get days until KYC expiry"""
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.utcnow()
        return delta.days if delta.days > 0 else 0
    
    def to_dict(self):
        """Convert KYC record to dictionary"""
        return {
            'id': self.id,
            'status': self.status.value,
            'verification_level': self.verification_level,
            'identity_verified': self.identity_verified,
            'address_verified': self.address_verified,
            'phone_verified': self.phone_verified,
            'email_verified': self.email_verified,
            'aml_screening_status': self.aml_screening_status,
            'pep_status': self.pep_status,
            'sanctions_screening': self.sanctions_screening,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired(),
            'days_until_expiry': self.days_until_expiry(),
            'documents_count': len(self.documents) if self.documents else 0
        }

class KYCDocument(db.Model):
    """KYC document storage and verification"""
    __tablename__ = 'kyc_documents'
    
    id = Column(Integer, primary_key=True)
    kyc_record_id = Column(Integer, ForeignKey('user_kyc.id'), nullable=False, index=True)
    
    # Document information
    document_type = Column(SQLEnum(DocumentType), nullable=False, index=True)
    document_number = Column(String(100), nullable=True)
    issuing_country = Column(String(3), nullable=True)  # ISO 3166-1 alpha-3
    issuing_authority = Column(String(255), nullable=True)
    issue_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    
    # File information
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False)  # SHA-256 hash
    mime_type = Column(String(100), nullable=False)
    
    # Verification status
    verification_status = Column(String(20), nullable=False, default='pending')  # pending, verified, rejected
    verification_notes = Column(Text, nullable=True)
    verified_by = Column(String(255), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Metadata
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    kyc_record = relationship("UserKYC", back_populates="documents")
    
    def is_expired(self):
        """Check if document has expired"""
        if self.expiry_date is None:
            return False
        return datetime.utcnow().date() > self.expiry_date.date()
    
    def to_dict(self):
        """Convert document to dictionary"""
        return {
            'id': self.id,
            'document_type': self.document_type.value,
            'document_number': self.document_number,
            'issuing_country': self.issuing_country,
            'issuing_authority': self.issuing_authority,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'verification_status': self.verification_status,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'uploaded_at': self.uploaded_at.isoformat(),
            'is_expired': self.is_expired()
        }

class UserSession(db.Model):
    """User session tracking for security"""
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Session information
    session_token = Column(String(255), nullable=False, unique=True, index=True)
    refresh_token = Column(String(255), nullable=True, unique=True, index=True)
    device_fingerprint = Column(String(255), nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=False)  # IPv6 support
    
    # Session status
    is_active = Column(Boolean, nullable=False, default=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    last_activity_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    terminated_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def is_expired(self):
        """Check if session has expired"""
        return datetime.utcnow() > self.expires_at
    
    def terminate(self):
        """Terminate session"""
        self.is_active = False
        self.terminated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'device_fingerprint': self.device_fingerprint,
            'user_agent': self.user_agent,
            'ip_address': self.ip_address,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_activity_at': self.last_activity_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_expired': self.is_expired()
        }

class UserAuditLog(db.Model):
    """Comprehensive audit logging for user activities"""
    __tablename__ = 'user_audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # Nullable for system events
    
    # Event information
    event_type = Column(String(50), nullable=False, index=True)  # login, logout, password_change, etc.
    event_category = Column(String(30), nullable=False, index=True)  # authentication, profile, trading, etc.
    event_description = Column(Text, nullable=False)
    
    # Request context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True)
    
    # Event details
    old_values = Column(JSON, nullable=True)  # Previous values for changes
    new_values = Column(JSON, nullable=True)  # New values for changes
    metadata = Column(JSON, nullable=True)    # Additional event metadata
    
    # Status and outcome
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'event_type': self.event_type,
            'event_category': self.event_category,
            'event_description': self.event_description,
            'ip_address': self.ip_address,
            'success': self.success,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }
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
