"""
Transaction and Audit models for CarbonXchange Backend
Implements comprehensive transaction tracking and audit logging for financial compliance
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

class TransactionType(Enum):
    """Transaction type enumeration"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRADE_BUY = "trade_buy"
    TRADE_SELL = "trade_sell"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    FEE = "fee"
    REFUND = "refund"
    RETIREMENT = "retirement"
    ISSUANCE = "issuance"
    CANCELLATION = "cancellation"

class TransactionStatus(Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"

class PaymentMethod(Enum):
    """Payment method enumeration"""
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    CRYPTO = "crypto"
    WALLET = "wallet"
    INTERNAL = "internal"

class AuditAction(Enum):
    """Audit action enumeration"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    APPROVE = "approve"
    REJECT = "reject"
    SUSPEND = "suspend"
    ACTIVATE = "activate"
    TRANSFER = "transfer"
    TRADE = "trade"
    RETIRE = "retire"

class Transaction(db.Model):
    """Transaction model for all financial transactions"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Transaction identification
    transaction_id = Column(String(50), unique=True, nullable=False)
    reference_id = Column(String(100), nullable=True)  # External reference
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Transaction details
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    status = Column(SQLEnum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    
    # Financial details
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='USD')
    fee_amount = Column(Numeric(10, 2), nullable=False, default=0)
    net_amount = Column(Numeric(15, 2), nullable=False)
    
    # Carbon credit details (if applicable)
    credit_quantity = Column(Numeric(15, 4), nullable=True)  # tCO2e
    credit_price = Column(Numeric(10, 4), nullable=True)  # Price per tCO2e
    project_id = Column(Integer, ForeignKey('carbon_projects.id'), nullable=True)
    vintage_year = Column(Integer, nullable=True)
    
    # Payment details
    payment_method = Column(SQLEnum(PaymentMethod), nullable=True)
    payment_reference = Column(String(100), nullable=True)
    payment_processor = Column(String(100), nullable=True)
    
    # Counterparty information
    counterparty_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    counterparty_name = Column(String(255), nullable=True)
    counterparty_account = Column(String(100), nullable=True)
    
    # Related entities
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=True)
    trade_id = Column(Integer, ForeignKey('trades.id'), nullable=True)
    
    # Blockchain integration
    blockchain_network = Column(String(50), nullable=True)
    blockchain_tx_hash = Column(String(66), nullable=True)
    block_number = Column(Integer, nullable=True)
    gas_used = Column(Integer, nullable=True)
    gas_price = Column(Numeric(20, 0), nullable=True)
    
    # Settlement details
    settlement_date = Column(DateTime, nullable=True)
    settlement_reference = Column(String(100), nullable=True)
    clearing_house = Column(String(100), nullable=True)
    
    # Risk and compliance
    risk_score = Column(Integer, nullable=True)  # 0-100
    compliance_checked = Column(Boolean, nullable=False, default=False)
    aml_checked = Column(Boolean, nullable=False, default=False)
    sanctions_checked = Column(Boolean, nullable=False, default=False)
    
    # Transaction metadata
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON metadata
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="transactions")
    counterparty = relationship("User", foreign_keys=[counterparty_id])
    project = relationship("CarbonProject")
    order = relationship("Order")
    trade = relationship("Trade")
    logs = relationship("TransactionLog", back_populates="transaction", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.transaction_id:
            self.transaction_id = f"TXN-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        self.net_amount = self.amount - self.fee_amount
    
    @hybrid_property
    def is_completed(self):
        """Check if transaction is completed"""
        return self.status == TransactionStatus.COMPLETED
    
    @hybrid_property
    def is_pending(self):
        """Check if transaction is pending"""
        return self.status == TransactionStatus.PENDING
    
    @hybrid_property
    def is_failed(self):
        """Check if transaction is failed"""
        return self.status == TransactionStatus.FAILED
    
    @hybrid_property
    def involves_carbon_credits(self):
        """Check if transaction involves carbon credits"""
        return self.credit_quantity is not None and self.credit_quantity > 0
    
    @hybrid_property
    def processing_time_minutes(self):
        """Get processing time in minutes"""
        if self.processed_at and self.created_at:
            delta = self.processed_at - self.created_at
            return delta.total_seconds() / 60
        return None
    
    def complete(self, settlement_reference=None):
        """Mark transaction as completed"""
        self.status = TransactionStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        if settlement_reference:
            self.settlement_reference = settlement_reference
    
    def fail(self, reason=None):
        """Mark transaction as failed"""
        self.status = TransactionStatus.FAILED
        self.processed_at = datetime.now(timezone.utc)
        if reason:
            self.notes = f"{self.notes or ''}\nFailed: {reason}".strip()
    
    def add_metadata(self, key, value):
        """Add metadata to transaction"""
        metadata = json.loads(self.metadata) if self.metadata else {}
        metadata[key] = value
        self.metadata = json.dumps(metadata)
    
    def get_metadata(self, key, default=None):
        """Get metadata value"""
        if not self.metadata:
            return default
        metadata = json.loads(self.metadata)
        return metadata.get(key, default)
    
    def to_dict(self, include_sensitive=False):
        """Convert transaction to dictionary"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'transaction_id': self.transaction_id,
            'transaction_type': self.transaction_type.value,
            'status': self.status.value,
            'amount': float(self.amount),
            'currency': self.currency,
            'fee_amount': float(self.fee_amount),
            'net_amount': float(self.net_amount),
            'credit_quantity': float(self.credit_quantity) if self.credit_quantity else None,
            'credit_price': float(self.credit_price) if self.credit_price else None,
            'vintage_year': self.vintage_year,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'processing_time_minutes': self.processing_time_minutes
        }
        
        if include_sensitive:
            data.update({
                'user_id': self.user_id,
                'reference_id': self.reference_id,
                'payment_method': self.payment_method.value if self.payment_method else None,
                'payment_reference': self.payment_reference,
                'counterparty_id': self.counterparty_id,
                'counterparty_name': self.counterparty_name,
                'blockchain_tx_hash': self.blockchain_tx_hash,
                'risk_score': self.risk_score,
                'compliance_checked': self.compliance_checked,
                'aml_checked': self.aml_checked,
                'sanctions_checked': self.sanctions_checked,
                'notes': self.notes,
                'metadata': self.metadata
            })
        
        return data
    
    def __repr__(self):
        return f'<Transaction {self.transaction_id} - {self.transaction_type.value} {self.amount} {self.currency}>'

class TransactionLog(db.Model):
    """Transaction log model for audit trail of transaction changes"""
    __tablename__ = 'transaction_logs'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Log identification
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # User who made the change
    
    # Log details
    action = Column(String(50), nullable=False)  # created, updated, status_changed, etc.
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=True)
    
    # Change details
    field_changes = Column(Text, nullable=True)  # JSON of field changes
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # System information
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    system_info = Column(Text, nullable=True)  # JSON system information
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    transaction = relationship("Transaction", back_populates="logs")
    user = relationship("User")
    
    def add_field_change(self, field_name, old_value, new_value):
        """Add field change to log"""
        changes = json.loads(self.field_changes) if self.field_changes else {}
        changes[field_name] = {
            'old': old_value,
            'new': new_value
        }
        self.field_changes = json.dumps(changes)
    
    def to_dict(self):
        """Convert log to dictionary"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'action': self.action,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'reason': self.reason,
            'notes': self.notes,
            'field_changes': json.loads(self.field_changes) if self.field_changes else None,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<TransactionLog {self.transaction_id} - {self.action}>'

class AuditLog(db.Model):
    """Audit log model for comprehensive system activity tracking"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Audit identification
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    session_id = Column(String(100), nullable=True)
    
    # Action details
    action = Column(SQLEnum(AuditAction), nullable=False)
    resource_type = Column(String(100), nullable=False)  # user, order, trade, etc.
    resource_id = Column(String(100), nullable=True)
    
    # Event details
    event_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    outcome = Column(String(20), nullable=False)  # success, failure, error
    
    # Request information
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    request_method = Column(String(10), nullable=True)  # GET, POST, etc.
    request_url = Column(String(500), nullable=True)
    request_headers = Column(Text, nullable=True)  # JSON
    
    # Response information
    response_status = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    # Data changes
    old_values = Column(Text, nullable=True)  # JSON of old values
    new_values = Column(Text, nullable=True)  # JSON of new values
    
    # Risk and compliance
    risk_level = Column(String(20), nullable=False, default='low')  # low, medium, high, critical
    compliance_flags = Column(Text, nullable=True)  # JSON array of flags
    
    # Geolocation
    country = Column(String(3), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    
    # Additional metadata
    metadata = Column(Text, nullable=True)  # JSON metadata
    tags = Column(Text, nullable=True)  # JSON array of tags
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User")
    
    @hybrid_property
    def is_high_risk(self):
        """Check if this is a high-risk event"""
        return self.risk_level in ['high', 'critical']
    
    @hybrid_property
    def is_successful(self):
        """Check if the action was successful"""
        return self.outcome == 'success'
    
    def add_compliance_flag(self, flag):
        """Add compliance flag"""
        flags = json.loads(self.compliance_flags) if self.compliance_flags else []
        if flag not in flags:
            flags.append(flag)
            self.compliance_flags = json.dumps(flags)
    
    def add_tag(self, tag):
        """Add tag to audit log"""
        tags = json.loads(self.tags) if self.tags else []
        if tag not in tags:
            tags.append(tag)
            self.tags = json.dumps(tags)
    
    def add_metadata(self, key, value):
        """Add metadata to audit log"""
        metadata = json.loads(self.metadata) if self.metadata else {}
        metadata[key] = value
        self.metadata = json.dumps(metadata)
    
    def to_dict(self, include_sensitive=False):
        """Convert audit log to dictionary"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'action': self.action.value,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'event_name': self.event_name,
            'description': self.description,
            'outcome': self.outcome,
            'risk_level': self.risk_level,
            'created_at': self.created_at.isoformat()
        }
        
        if include_sensitive:
            data.update({
                'user_id': self.user_id,
                'session_id': self.session_id,
                'ip_address': self.ip_address,
                'request_method': self.request_method,
                'request_url': self.request_url,
                'response_status': self.response_status,
                'response_time_ms': self.response_time_ms,
                'old_values': json.loads(self.old_values) if self.old_values else None,
                'new_values': json.loads(self.new_values) if self.new_values else None,
                'compliance_flags': json.loads(self.compliance_flags) if self.compliance_flags else None,
                'metadata': json.loads(self.metadata) if self.metadata else None,
                'tags': json.loads(self.tags) if self.tags else None
            })
        
        return data
    
    @classmethod
    def log_event(cls, user_id, action, resource_type, event_name, 
                  resource_id=None, description=None, outcome='success',
                  risk_level='low', ip_address=None, **kwargs):
        """Create audit log entry"""
        log = cls(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            event_name=event_name,
            description=description,
            outcome=outcome,
            risk_level=risk_level,
            ip_address=ip_address
        )
        
        # Add any additional metadata
        for key, value in kwargs.items():
            if hasattr(log, key):
                setattr(log, key, value)
            else:
                log.add_metadata(key, value)
        
        return log
    
    def __repr__(self):
        return f'<AuditLog {self.event_name} - {self.action.value} {self.resource_type}>'

