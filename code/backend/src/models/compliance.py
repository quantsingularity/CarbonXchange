"""
Compliance models for CarbonXchange Backend
Implements comprehensive compliance tracking and regulatory reporting
"""
from datetime import datetime, timezone
from enum import Enum
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import uuid
import json

db = SQLAlchemy()

class ComplianceStatus(Enum):
    """Compliance status enumeration"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    UNDER_INVESTIGATION = "under_investigation"
    REMEDIATED = "remediated"
    WAIVED = "waived"

class RegulatoryFramework(Enum):
    """Regulatory framework enumeration"""
    EU_ETS = "eu_ets"  # EU Emissions Trading System
    CORSIA = "corsia"  # Carbon Offsetting and Reduction Scheme for International Aviation
    CALIFORNIA_CAP_TRADE = "california_cap_trade"
    RGGI = "rggi"  # Regional Greenhouse Gas Initiative
    MIFID_II = "mifid_ii"
    SOX = "sox"  # Sarbanes-Oxley Act
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    AML_CTF = "aml_ctf"  # Anti-Money Laundering / Counter-Terrorism Financing
    KYC = "kyc"  # Know Your Customer

class ReportType(Enum):
    """Report type enumeration"""
    TRANSACTION_REPORT = "transaction_report"
    POSITION_REPORT = "position_report"
    TRADE_REPORT = "trade_report"
    RISK_REPORT = "risk_report"
    AML_REPORT = "aml_report"
    KYC_REPORT = "kyc_report"
    AUDIT_REPORT = "audit_report"
    COMPLIANCE_REPORT = "compliance_report"
    REGULATORY_FILING = "regulatory_filing"

class ReportStatus(Enum):
    """Report status enumeration"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    REJECTED = "rejected"
    AMENDED = "amended"

class ComplianceRecord(db.Model):
    """Compliance record model for tracking compliance status and violations"""
    __tablename__ = 'compliance_records'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Record identification
    record_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    entity_type = Column(String(50), nullable=False)  # user, transaction, order, trade
    entity_id = Column(String(100), nullable=False)
    
    # Compliance details
    framework = Column(SQLEnum(RegulatoryFramework), nullable=False)
    rule_reference = Column(String(100), nullable=False)
    rule_description = Column(Text, nullable=False)
    
    # Status and assessment
    status = Column(SQLEnum(ComplianceStatus), nullable=False)
    risk_level = Column(String(20), nullable=False, default='low')  # low, medium, high, critical
    severity = Column(String(20), nullable=False, default='minor')  # minor, major, critical
    
    # Violation details (if applicable)
    violation_type = Column(String(100), nullable=True)
    violation_description = Column(Text, nullable=True)
    violation_date = Column(DateTime, nullable=True)
    
    # Assessment details
    assessed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    assessment_date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    assessment_notes = Column(Text, nullable=True)
    
    # Remediation
    remediation_required = Column(Boolean, nullable=False, default=False)
    remediation_plan = Column(Text, nullable=True)
    remediation_deadline = Column(DateTime, nullable=True)
    remediation_completed_date = Column(DateTime, nullable=True)
    remediation_notes = Column(Text, nullable=True)
    
    # Review and approval
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    review_date = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    
    # External references
    external_case_id = Column(String(100), nullable=True)
    regulator_reference = Column(String(100), nullable=True)
    
    # Supporting documentation
    evidence_documents = Column(Text, nullable=True)  # JSON array of document paths
    correspondence = Column(Text, nullable=True)  # JSON array of correspondence
    
    # Financial impact
    financial_impact = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), nullable=False, default='USD')
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    due_date = Column(DateTime, nullable=True)
    closed_date = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    assessor = relationship("User", foreign_keys=[assessed_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    approver = relationship("User", foreign_keys=[approved_by])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.record_id:
            self.record_id = f"COMP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    @hybrid_property
    def is_compliant(self):
        """Check if record shows compliance"""
        return self.status == ComplianceStatus.COMPLIANT
    
    @hybrid_property
    def is_violation(self):
        """Check if record represents a violation"""
        return self.status == ComplianceStatus.NON_COMPLIANT
    
    @hybrid_property
    def is_overdue(self):
        """Check if remediation is overdue"""
        if not self.remediation_deadline:
            return False
        return datetime.now(timezone.utc) > self.remediation_deadline and not self.remediation_completed_date
    
    @hybrid_property
    def days_until_due(self):
        """Get days until due date"""
        if not self.due_date:
            return None
        delta = self.due_date - datetime.now(timezone.utc)
        return delta.days if delta.days > 0 else 0
    
    def add_evidence_document(self, document_path, description=None):
        """Add evidence document"""
        documents = json.loads(self.evidence_documents) if self.evidence_documents else []
        document = {
            'path': document_path,
            'description': description,
            'added_at': datetime.now(timezone.utc).isoformat()
        }
        documents.append(document)
        self.evidence_documents = json.dumps(documents)
    
    def add_correspondence(self, correspondent, subject, content, direction='outbound'):
        """Add correspondence record"""
        correspondence = json.loads(self.correspondence) if self.correspondence else []
        record = {
            'correspondent': correspondent,
            'subject': subject,
            'content': content,
            'direction': direction,  # inbound, outbound
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        correspondence.append(record)
        self.correspondence = json.dumps(correspondence)
    
    def complete_remediation(self, notes=None):
        """Mark remediation as completed"""
        self.remediation_completed_date = datetime.now(timezone.utc)
        if notes:
            self.remediation_notes = notes
        if self.status == ComplianceStatus.NON_COMPLIANT:
            self.status = ComplianceStatus.REMEDIATED
    
    def close_record(self, notes=None):
        """Close compliance record"""
        self.closed_date = datetime.now(timezone.utc)
        if notes:
            self.assessment_notes = f"{self.assessment_notes or ''}\nClosed: {notes}".strip()
    
    def to_dict(self, include_sensitive=False):
        """Convert compliance record to dictionary"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'record_id': self.record_id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'framework': self.framework.value,
            'rule_reference': self.rule_reference,
            'rule_description': self.rule_description,
            'status': self.status.value,
            'risk_level': self.risk_level,
            'severity': self.severity,
            'violation_type': self.violation_type,
            'violation_description': self.violation_description,
            'remediation_required': self.remediation_required,
            'is_overdue': self.is_overdue,
            'days_until_due': self.days_until_due,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'closed_date': self.closed_date.isoformat() if self.closed_date else None
        }
        
        if include_sensitive:
            data.update({
                'user_id': self.user_id,
                'assessed_by': self.assessed_by,
                'assessment_notes': self.assessment_notes,
                'remediation_plan': self.remediation_plan,
                'financial_impact': float(self.financial_impact) if self.financial_impact else None,
                'external_case_id': self.external_case_id,
                'regulator_reference': self.regulator_reference,
                'evidence_documents': json.loads(self.evidence_documents) if self.evidence_documents else None,
                'correspondence': json.loads(self.correspondence) if self.correspondence else None
            })
        
        return data
    
    def __repr__(self):
        return f'<ComplianceRecord {self.record_id} - {self.framework.value} {self.status.value}>'

class RegulatoryReport(db.Model):
    """Regulatory report model for compliance reporting and filings"""
    __tablename__ = 'regulatory_reports'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Report identification
    report_id = Column(String(50), unique=True, nullable=False)
    report_type = Column(SQLEnum(ReportType), nullable=False)
    framework = Column(SQLEnum(RegulatoryFramework), nullable=False)
    
    # Report details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    reporting_period_start = Column(DateTime, nullable=False)
    reporting_period_end = Column(DateTime, nullable=False)
    
    # Status and workflow
    status = Column(SQLEnum(ReportStatus), nullable=False, default=ReportStatus.DRAFT)
    version = Column(Integer, nullable=False, default=1)
    
    # Content and data
    report_data = Column(Text, nullable=True)  # JSON report data
    summary_statistics = Column(Text, nullable=True)  # JSON summary
    
    # File attachments
    report_file_path = Column(String(500), nullable=True)
    supporting_documents = Column(Text, nullable=True)  # JSON array
    
    # Submission details
    regulator = Column(String(255), nullable=True)
    submission_method = Column(String(100), nullable=True)  # email, portal, api
    submission_reference = Column(String(100), nullable=True)
    
    # Workflow tracking
    prepared_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    submitted_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Important dates
    due_date = Column(DateTime, nullable=False)
    review_date = Column(DateTime, nullable=True)
    approval_date = Column(DateTime, nullable=True)
    submission_date = Column(DateTime, nullable=True)
    acknowledgment_date = Column(DateTime, nullable=True)
    
    # Quality and validation
    validation_errors = Column(Text, nullable=True)  # JSON array of errors
    validation_warnings = Column(Text, nullable=True)  # JSON array of warnings
    data_quality_score = Column(Numeric(5, 2), nullable=True)  # 0-100
    
    # External references
    external_report_id = Column(String(100), nullable=True)
    regulator_case_id = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    preparer = relationship("User", foreign_keys=[prepared_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    approver = relationship("User", foreign_keys=[approved_by])
    submitter = relationship("User", foreign_keys=[submitted_by])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.report_id:
            self.report_id = f"RPT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    @hybrid_property
    def is_overdue(self):
        """Check if report is overdue"""
        return datetime.now(timezone.utc) > self.due_date and self.status not in [ReportStatus.SUBMITTED, ReportStatus.ACKNOWLEDGED]
    
    @hybrid_property
    def days_until_due(self):
        """Get days until due date"""
        delta = self.due_date - datetime.now(timezone.utc)
        return delta.days if delta.days > 0 else 0
    
    @hybrid_property
    def is_submitted(self):
        """Check if report is submitted"""
        return self.status in [ReportStatus.SUBMITTED, ReportStatus.ACKNOWLEDGED]
    
    @hybrid_property
    def has_validation_errors(self):
        """Check if report has validation errors"""
        if not self.validation_errors:
            return False
        errors = json.loads(self.validation_errors)
        return len(errors) > 0
    
    def add_validation_error(self, field, message, severity='error'):
        """Add validation error"""
        errors = json.loads(self.validation_errors) if self.validation_errors else []
        error = {
            'field': field,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        errors.append(error)
        self.validation_errors = json.dumps(errors)
    
    def add_supporting_document(self, document_path, document_type, description=None):
        """Add supporting document"""
        documents = json.loads(self.supporting_documents) if self.supporting_documents else []
        document = {
            'path': document_path,
            'type': document_type,
            'description': description,
            'added_at': datetime.now(timezone.utc).isoformat()
        }
        documents.append(document)
        self.supporting_documents = json.dumps(documents)
    
    def submit(self, submitted_by_id, submission_reference=None):
        """Submit report to regulator"""
        self.status = ReportStatus.SUBMITTED
        self.submitted_by = submitted_by_id
        self.submission_date = datetime.now(timezone.utc)
        if submission_reference:
            self.submission_reference = submission_reference
    
    def acknowledge(self, acknowledgment_reference=None):
        """Mark report as acknowledged by regulator"""
        self.status = ReportStatus.ACKNOWLEDGED
        self.acknowledgment_date = datetime.now(timezone.utc)
        if acknowledgment_reference:
            self.regulator_case_id = acknowledgment_reference
    
    def reject(self, reason=None):
        """Mark report as rejected"""
        self.status = ReportStatus.REJECTED
        if reason:
            self.add_validation_error('general', f"Report rejected: {reason}", 'error')
    
    def to_dict(self, include_sensitive=False):
        """Convert report to dictionary"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'report_id': self.report_id,
            'report_type': self.report_type.value,
            'framework': self.framework.value,
            'title': self.title,
            'description': self.description,
            'reporting_period_start': self.reporting_period_start.isoformat(),
            'reporting_period_end': self.reporting_period_end.isoformat(),
            'status': self.status.value,
            'version': self.version,
            'due_date': self.due_date.isoformat(),
            'days_until_due': self.days_until_due,
            'is_overdue': self.is_overdue,
            'is_submitted': self.is_submitted,
            'has_validation_errors': self.has_validation_errors,
            'data_quality_score': float(self.data_quality_score) if self.data_quality_score else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'submission_date': self.submission_date.isoformat() if self.submission_date else None,
            'acknowledgment_date': self.acknowledgment_date.isoformat() if self.acknowledgment_date else None
        }
        
        if include_sensitive:
            data.update({
                'prepared_by': self.prepared_by,
                'reviewed_by': self.reviewed_by,
                'approved_by': self.approved_by,
                'submitted_by': self.submitted_by,
                'report_data': json.loads(self.report_data) if self.report_data else None,
                'summary_statistics': json.loads(self.summary_statistics) if self.summary_statistics else None,
                'validation_errors': json.loads(self.validation_errors) if self.validation_errors else None,
                'validation_warnings': json.loads(self.validation_warnings) if self.validation_warnings else None,
                'supporting_documents': json.loads(self.supporting_documents) if self.supporting_documents else None,
                'submission_reference': self.submission_reference,
                'external_report_id': self.external_report_id,
                'regulator_case_id': self.regulator_case_id
            })
        
        return data
    
    def __repr__(self):
        return f'<RegulatoryReport {self.report_id} - {self.report_type.value} {self.status.value}>'

