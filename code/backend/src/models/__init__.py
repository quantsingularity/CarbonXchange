"""
Database models package for CarbonXchange Backend
Implements comprehensive data models for carbon credit trading with financial industry standards
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

# Import all models to ensure they are registered with SQLAlchemy
from .user import User, UserProfile, UserKYC, UserSession, UserAuditLog, KYCDocument
from .carbon_credit import CarbonCredit, CarbonProject, CreditCertificate
from .trading import Order, Trade, Portfolio, PortfolioHolding
from .transaction import Transaction, TransactionLog, AuditLog
from .market import MarketData, PriceHistory
from .compliance import ComplianceRecord, RegulatoryReport

# Import enums for external use
from .user import UserStatus, KYCStatus, UserRole, RiskLevel, DocumentType
from .carbon_credit import ProjectType, ProjectStatus, CreditStatus, CreditStandard, VerificationStatus
from .trading import OrderType, OrderSide, OrderStatus, TradeStatus, PortfolioType

# Model registry for dynamic access
MODEL_REGISTRY = {
    'User': User,
    'UserProfile': UserProfile,
    'UserKYC': UserKYC,
    'UserSession': UserSession,
    'UserAuditLog': UserAuditLog,
    'KYCDocument': KYCDocument,
    'CarbonProject': CarbonProject,
    'CarbonCredit': CarbonCredit,
    'CreditCertificate': CreditCertificate,
    'Order': Order,
    'Trade': Trade,
    'Portfolio': Portfolio,
    'PortfolioHolding': PortfolioHolding,
    'Transaction': Transaction,
    'TransactionLog': TransactionLog,
    'AuditLog': AuditLog,
    'MarketData': MarketData,
    'PriceHistory': PriceHistory,
    'ComplianceRecord': ComplianceRecord,
    'RegulatoryReport': RegulatoryReport
}

def get_model(model_name: str):
    """Get model class by name"""
    return MODEL_REGISTRY.get(model_name)

def get_all_models():
    """Get all registered models"""
    return MODEL_REGISTRY.values()

def setup_model_relationships():
    """Setup additional model relationships and constraints"""
    # Additional relationships can be defined here if needed
    pass

def create_all_tables(app):
    """Create all database tables"""
    with app.app_context():
        db.create_all()
        setup_model_relationships()

def drop_all_tables(app):
    """Drop all database tables"""
    with app.app_context():
        db.drop_all()

def init_db(app):
    """Initialize database with app"""
    db.init_app(app)
    migrate.init_app(app, db)
    setup_model_relationships()

__all__ = [
    'db', 'migrate',
    'User', 'UserProfile', 'UserKYC', 'UserSession', 'UserAuditLog', 'KYCDocument',
    'CarbonCredit', 'CarbonProject', 'CreditCertificate',
    'Order', 'Trade', 'Portfolio', 'PortfolioHolding',
    'Transaction', 'TransactionLog', 'AuditLog',
    'MarketData', 'PriceHistory',
    'ComplianceRecord', 'RegulatoryReport',
    'UserStatus', 'KYCStatus', 'UserRole', 'RiskLevel', 'DocumentType',
    'ProjectType', 'ProjectStatus', 'CreditStatus', 'CreditStandard', 'VerificationStatus',
    'OrderType', 'OrderSide', 'OrderStatus', 'TradeStatus', 'PortfolioType',
    'MODEL_REGISTRY', 'get_model', 'get_all_models',
    'create_all_tables', 'drop_all_tables', 'init_db', 'setup_model_relationships'
]

