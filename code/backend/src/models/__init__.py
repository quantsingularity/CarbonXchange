"""
Database models package for CarbonXchange Backend
Implements comprehensive data models for carbon credit trading with financial industry standards
"""

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
from .carbon_credit import (
    CarbonCredit,
    CarbonProject,
    CreditCertificate,
    CreditStandard,
    CreditStatus,
    ProjectStatus,
    ProjectType,
    VerificationStatus,
)
from .compliance import ComplianceRecord, RegulatoryReport
from .market import MarketData, PriceHistory
from .trading import (
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    Portfolio,
    PortfolioHolding,
    PortfolioType,
    Trade,
    TradeStatus,
)
from .transaction import AuditLog, Transaction, TransactionLog
from .user import (
    DocumentType,
    KYCDocument,
    KYCStatus,
    RiskLevel,
    User,
    UserAuditLog,
    UserKYC,
    UserProfile,
    UserRole,
    UserSession,
    UserStatus,
)

MODEL_REGISTRY = {
    "User": User,
    "UserProfile": UserProfile,
    "UserKYC": UserKYC,
    "UserSession": UserSession,
    "UserAuditLog": UserAuditLog,
    "KYCDocument": KYCDocument,
    "CarbonProject": CarbonProject,
    "CarbonCredit": CarbonCredit,
    "CreditCertificate": CreditCertificate,
    "Order": Order,
    "Trade": Trade,
    "Portfolio": Portfolio,
    "PortfolioHolding": PortfolioHolding,
    "Transaction": Transaction,
    "TransactionLog": TransactionLog,
    "AuditLog": AuditLog,
    "MarketData": MarketData,
    "PriceHistory": PriceHistory,
    "ComplianceRecord": ComplianceRecord,
    "RegulatoryReport": RegulatoryReport,
}


def get_model(model_name: str) -> Any:
    """Get model class by name"""
    return MODEL_REGISTRY.get(model_name)


def get_all_models() -> Any:
    """Get all registered models"""
    return MODEL_REGISTRY.values()


def setup_model_relationships() -> Any:
    """Setup additional model relationships and constraints"""


def create_all_tables(app: Any) -> Any:
    """Create all database tables"""
    with app.app_context():
        db.create_all()
        setup_model_relationships()


def drop_all_tables(app: Any) -> Any:
    """Drop all database tables"""
    with app.app_context():
        db.drop_all()


def init_db(app: Any) -> Any:
    """Initialize database with app"""
    db.init_app(app)
    migrate.init_app(app, db)
    setup_model_relationships()


__all__ = [
    "db",
    "migrate",
    "User",
    "UserProfile",
    "UserKYC",
    "UserSession",
    "UserAuditLog",
    "KYCDocument",
    "CarbonCredit",
    "CarbonProject",
    "CreditCertificate",
    "Order",
    "Trade",
    "Portfolio",
    "PortfolioHolding",
    "Transaction",
    "TransactionLog",
    "AuditLog",
    "MarketData",
    "PriceHistory",
    "ComplianceRecord",
    "RegulatoryReport",
    "UserStatus",
    "KYCStatus",
    "UserRole",
    "RiskLevel",
    "DocumentType",
    "ProjectType",
    "ProjectStatus",
    "CreditStatus",
    "CreditStandard",
    "VerificationStatus",
    "OrderType",
    "OrderSide",
    "OrderStatus",
    "TradeStatus",
    "PortfolioType",
    "MODEL_REGISTRY",
    "get_model",
    "get_all_models",
    "create_all_tables",
    "drop_all_tables",
    "init_db",
    "setup_model_relationships",
]
