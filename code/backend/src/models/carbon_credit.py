"""
Carbon Credit models for CarbonXchange Backend
Implements comprehensive carbon credit and project management
"""
from datetime import datetime, timezone
from enum import Enum
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import uuid

db = SQLAlchemy()

class ProjectType(Enum):
    """Carbon project type enumeration"""
    RENEWABLE_ENERGY = "renewable_energy"
    REFORESTATION = "reforestation"
    AFFORESTATION = "afforestation"
    METHANE_CAPTURE = "methane_capture"
    ENERGY_EFFICIENCY = "energy_efficiency"
    INDUSTRIAL_PROCESS = "industrial_process"
    TRANSPORTATION = "transportation"
    AGRICULTURE = "agriculture"
    WASTE_MANAGEMENT = "waste_management"
    BLUE_CARBON = "blue_carbon"
    DIRECT_AIR_CAPTURE = "direct_air_capture"
    BIOCHAR = "biochar"

class ProjectStatus(Enum):
    """Carbon project status enumeration"""
    DEVELOPMENT = "development"
    VALIDATION = "validation"
    REGISTERED = "registered"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CreditStatus(Enum):
    """Carbon credit status enumeration"""
    PENDING = "pending"
    VERIFIED = "verified"
    ISSUED = "issued"
    AVAILABLE = "available"
    RESERVED = "reserved"
    TRADED = "traded"
    RETIRED = "retired"
    CANCELLED = "cancelled"

class CreditStandard(Enum):
    """Carbon credit standard enumeration"""
    VCS = "vcs"  # Verified Carbon Standard
    CDM = "cdm"  # Clean Development Mechanism
    GOLD_STANDARD = "gold_standard"
    CAR = "car"  # Climate Action Reserve
    ACR = "acr"  # American Carbon Registry
    PLAN_VIVO = "plan_vivo"
    CCBS = "ccbs"  # Climate, Community & Biodiversity Standards
    REDD_PLUS = "redd_plus"

class CarbonProject(db.Model):
    """Carbon project model representing emission reduction projects"""
    __tablename__ = 'carbon_projects'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Basic project information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    project_type = Column(SQLEnum(ProjectType), nullable=False)
    status = Column(SQLEnum(ProjectStatus), nullable=False, default=ProjectStatus.DEVELOPMENT)
    
    # Project identification
    project_id = Column(String(100), unique=True, nullable=False)  # External project ID
    registry_id = Column(String(100), nullable=True)  # Registry-specific ID
    standard = Column(SQLEnum(CreditStandard), nullable=False)
    
    # Location information
    country = Column(String(3), nullable=False)  # ISO 3166-1 alpha-3
    region = Column(String(100), nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    
    # Project details
    methodology = Column(String(100), nullable=True)
    baseline_scenario = Column(Text, nullable=True)
    additionality_test = Column(Text, nullable=True)
    
    # Capacity and timeline
    annual_emission_reductions = Column(Numeric(15, 4), nullable=True)  # tCO2e per year
    total_emission_reductions = Column(Numeric(15, 4), nullable=True)  # Total tCO2e
    project_start_date = Column(DateTime, nullable=True)
    project_end_date = Column(DateTime, nullable=True)
    crediting_period_start = Column(DateTime, nullable=True)
    crediting_period_end = Column(DateTime, nullable=True)
    
    # Validation and verification
    validation_date = Column(DateTime, nullable=True)
    validator = Column(String(255), nullable=True)
    last_verification_date = Column(DateTime, nullable=True)
    verifier = Column(String(255), nullable=True)
    next_verification_due = Column(DateTime, nullable=True)
    
    # Project developer information
    developer_name = Column(String(255), nullable=False)
    developer_contact = Column(String(255), nullable=True)
    developer_website = Column(String(500), nullable=True)
    
    # Financial information
    project_cost = Column(Numeric(15, 2), nullable=True)
    project_currency = Column(String(3), nullable=False, default='USD')
    
    # Documentation
    project_document_url = Column(String(500), nullable=True)
    monitoring_report_url = Column(String(500), nullable=True)
    validation_report_url = Column(String(500), nullable=True)
    
    # Sustainability metrics
    sdg_contributions = Column(Text, nullable=True)  # JSON array of SDG goals
    co_benefits = Column(Text, nullable=True)  # JSON array of co-benefits
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    credits = relationship("CarbonCredit", back_populates="project", cascade="all, delete-orphan")
    certificates = relationship("CreditCertificate", back_populates="project", cascade="all, delete-orphan")
    
    @hybrid_property
    def is_active(self):
        """Check if project is active"""
        return self.status == ProjectStatus.ACTIVE
    
    @hybrid_property
    def total_credits_issued(self):
        """Get total credits issued for this project"""
        return sum(credit.quantity for credit in self.credits if credit.status in [CreditStatus.ISSUED, CreditStatus.AVAILABLE, CreditStatus.TRADED, CreditStatus.RETIRED])
    
    @hybrid_property
    def available_credits(self):
        """Get available credits for trading"""
        return sum(credit.quantity for credit in self.credits if credit.status == CreditStatus.AVAILABLE)
    
    def to_dict(self, include_sensitive=False):
        """Convert project to dictionary"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'project_type': self.project_type.value,
            'status': self.status.value,
            'project_id': self.project_id,
            'standard': self.standard.value,
            'country': self.country,
            'region': self.region,
            'methodology': self.methodology,
            'annual_emission_reductions': float(self.annual_emission_reductions) if self.annual_emission_reductions else None,
            'total_emission_reductions': float(self.total_emission_reductions) if self.total_emission_reductions else None,
            'project_start_date': self.project_start_date.isoformat() if self.project_start_date else None,
            'project_end_date': self.project_end_date.isoformat() if self.project_end_date else None,
            'developer_name': self.developer_name,
            'total_credits_issued': float(self.total_credits_issued) if self.total_credits_issued else 0,
            'available_credits': float(self.available_credits) if self.available_credits else 0,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_sensitive:
            data.update({
                'project_cost': float(self.project_cost) if self.project_cost else None,
                'developer_contact': self.developer_contact,
                'validation_date': self.validation_date.isoformat() if self.validation_date else None,
                'validator': self.validator,
                'last_verification_date': self.last_verification_date.isoformat() if self.last_verification_date else None,
                'verifier': self.verifier
            })
        
        return data
    
    def __repr__(self):
        return f'<CarbonProject {self.name}>'

class CarbonCredit(db.Model):
    """Carbon credit model representing individual credit units"""
    __tablename__ = 'carbon_credits'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Credit identification
    serial_number = Column(String(100), unique=True, nullable=False)
    batch_id = Column(String(100), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey('carbon_projects.id'), nullable=False)
    
    # Credit details
    quantity = Column(Numeric(15, 4), nullable=False)  # tCO2e
    vintage_year = Column(Integer, nullable=False)  # Year of emission reduction
    status = Column(SQLEnum(CreditStatus), nullable=False, default=CreditStatus.PENDING)
    
    # Issuance information
    issued_date = Column(DateTime, nullable=True)
    issued_to = Column(String(255), nullable=True)  # Initial owner
    registry_account = Column(String(100), nullable=True)
    
    # Current ownership
    current_owner = Column(String(255), nullable=True)
    owner_wallet_address = Column(String(42), nullable=True, index=True)
    
    # Trading information
    last_trade_date = Column(DateTime, nullable=True)
    last_trade_price = Column(Numeric(10, 4), nullable=True)
    last_trade_currency = Column(String(3), nullable=False, default='USD')
    
    # Retirement information
    retired_date = Column(DateTime, nullable=True)
    retired_by = Column(String(255), nullable=True)
    retirement_reason = Column(String(255), nullable=True)
    retirement_certificate = Column(String(500), nullable=True)
    
    # Blockchain integration
    token_id = Column(String(100), nullable=True, unique=True)
    blockchain_tx_hash = Column(String(66), nullable=True)
    smart_contract_address = Column(String(42), nullable=True)
    
    # Quality attributes
    buffer_pool_percentage = Column(Numeric(5, 2), nullable=True)  # Risk buffer percentage
    leakage_percentage = Column(Numeric(5, 2), nullable=True)
    permanence_risk = Column(String(20), nullable=True)  # low, medium, high
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    project = relationship("CarbonProject", back_populates="credits")
    certificates = relationship("CreditCertificate", back_populates="credit", cascade="all, delete-orphan")
    
    @hybrid_property
    def is_available(self):
        """Check if credit is available for trading"""
        return self.status == CreditStatus.AVAILABLE
    
    @hybrid_property
    def is_retired(self):
        """Check if credit is retired"""
        return self.status == CreditStatus.RETIRED
    
    @hybrid_property
    def age_in_years(self):
        """Get age of credit in years"""
        current_year = datetime.now(timezone.utc).year
        return current_year - self.vintage_year
    
    def retire(self, retired_by, reason=None):
        """Retire the carbon credit"""
        self.status = CreditStatus.RETIRED
        self.retired_date = datetime.now(timezone.utc)
        self.retired_by = retired_by
        self.retirement_reason = reason
    
    def transfer_ownership(self, new_owner, wallet_address=None):
        """Transfer ownership of the credit"""
        self.current_owner = new_owner
        self.owner_wallet_address = wallet_address
        self.updated_at = datetime.now(timezone.utc)
    
    def to_dict(self, include_sensitive=False):
        """Convert credit to dictionary"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'serial_number': self.serial_number,
            'batch_id': self.batch_id,
            'quantity': float(self.quantity),
            'vintage_year': self.vintage_year,
            'status': self.status.value,
            'current_owner': self.current_owner,
            'last_trade_price': float(self.last_trade_price) if self.last_trade_price else None,
            'last_trade_currency': self.last_trade_currency,
            'age_in_years': self.age_in_years,
            'permanence_risk': self.permanence_risk,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_sensitive:
            data.update({
                'owner_wallet_address': self.owner_wallet_address,
                'token_id': self.token_id,
                'blockchain_tx_hash': self.blockchain_tx_hash,
                'smart_contract_address': self.smart_contract_address,
                'buffer_pool_percentage': float(self.buffer_pool_percentage) if self.buffer_pool_percentage else None,
                'leakage_percentage': float(self.leakage_percentage) if self.leakage_percentage else None
            })
        
        return data
    
    def __repr__(self):
        return f'<CarbonCredit {self.serial_number}>'

class CreditCertificate(db.Model):
    """Certificate model for carbon credit verification and compliance"""
    __tablename__ = 'credit_certificates'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Certificate identification
    certificate_number = Column(String(100), unique=True, nullable=False)
    certificate_type = Column(String(50), nullable=False)  # verification, validation, issuance, retirement
    
    # Associated entities
    project_id = Column(Integer, ForeignKey('carbon_projects.id'), nullable=True)
    credit_id = Column(Integer, ForeignKey('carbon_credits.id'), nullable=True)
    
    # Certificate details
    issuer = Column(String(255), nullable=False)
    issued_date = Column(DateTime, nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=True)
    
    # Certificate content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scope = Column(Text, nullable=True)
    methodology_used = Column(String(100), nullable=True)
    
    # Verification details
    verifier_name = Column(String(255), nullable=True)
    verifier_accreditation = Column(String(100), nullable=True)
    verification_date = Column(DateTime, nullable=True)
    verification_standard = Column(String(100), nullable=True)
    
    # Document storage
    certificate_document_url = Column(String(500), nullable=True)
    certificate_hash = Column(String(64), nullable=True)  # SHA-256 hash
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    revoked_date = Column(DateTime, nullable=True)
    revocation_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    project = relationship("CarbonProject", back_populates="certificates")
    credit = relationship("CarbonCredit", back_populates="certificates")
    
    @hybrid_property
    def is_valid(self):
        """Check if certificate is currently valid"""
        now = datetime.now(timezone.utc)
        if not self.is_active or self.revoked_date:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return now >= self.valid_from
    
    @hybrid_property
    def days_until_expiry(self):
        """Get days until certificate expires"""
        if self.valid_until is None:
            return None
        delta = self.valid_until - datetime.now(timezone.utc)
        return delta.days if delta.days > 0 else 0
    
    def revoke(self, reason):
        """Revoke the certificate"""
        self.is_active = False
        self.revoked_date = datetime.now(timezone.utc)
        self.revocation_reason = reason
    
    def to_dict(self):
        """Convert certificate to dictionary"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'certificate_number': self.certificate_number,
            'certificate_type': self.certificate_type,
            'issuer': self.issuer,
            'title': self.title,
            'description': self.description,
            'issued_date': self.issued_date.isoformat(),
            'valid_from': self.valid_from.isoformat(),
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'is_valid': self.is_valid,
            'days_until_expiry': self.days_until_expiry,
            'verifier_name': self.verifier_name,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<CreditCertificate {self.certificate_number}>'

