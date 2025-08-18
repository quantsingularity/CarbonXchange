"""
Database models package for CarbonXchange Backend
Implements comprehensive data models for carbon credit trading
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

# Import all models to ensure they are registered with SQLAlchemy
from .user import User, UserProfile, UserKYC
from .carbon_credit import CarbonCredit, CarbonProject, CreditCertificate
from .trading import Order, Trade, Portfolio, PortfolioHolding
from .transaction import Transaction, TransactionLog, AuditLog
from .market import MarketData, PriceHistory
from .compliance import ComplianceRecord, RegulatoryReport

__all__ = [
    'db', 'migrate',
    'User', 'UserProfile', 'UserKYC',
    'CarbonCredit', 'CarbonProject', 'CreditCertificate',
    'Order', 'Trade', 'Portfolio', 'PortfolioHolding',
    'Transaction', 'TransactionLog', 'AuditLog',
    'MarketData', 'PriceHistory',
    'ComplianceRecord', 'RegulatoryReport'
]

