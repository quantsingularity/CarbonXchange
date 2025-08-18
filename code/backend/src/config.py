"""
Production-ready configuration management for CarbonXchange Backend
Implements financial industry standards for security and compliance
"""
import os
import secrets
from datetime import timedelta
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseConfig:
    """Base configuration with common settings"""
    
    # Application Settings
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(32))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
    
    # Security Settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # API Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
    RATELIMIT_DEFAULT = "1000 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'X-Requested-With']
    
    # Blockchain Configuration
    WEB3_PROVIDER_URL = os.getenv('WEB3_PROVIDER_URL', 'https://polygon-mainnet.infura.io/v3/')
    WEB3_PRIVATE_KEY = os.getenv('WEB3_PRIVATE_KEY')
    CARBON_TOKEN_CONTRACT_ADDRESS = os.getenv('CARBON_TOKEN_CONTRACT_ADDRESS')
    MARKETPLACE_CONTRACT_ADDRESS = os.getenv('MARKETPLACE_CONTRACT_ADDRESS')
    
    # External Services
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/2')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/3')
    
    # File Storage
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(Path(__file__).parent / 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.getenv('LOG_FILE', 'carbonxchange.log')
    
    # Compliance and Audit
    AUDIT_LOG_ENABLED = True
    AUDIT_LOG_FILE = os.getenv('AUDIT_LOG_FILE', 'audit.log')
    DATA_RETENTION_DAYS = int(os.getenv('DATA_RETENTION_DAYS', '2555'))  # 7 years
    
    # Market Data Configuration
    MARKET_DATA_UPDATE_INTERVAL = int(os.getenv('MARKET_DATA_UPDATE_INTERVAL', '60'))  # seconds
    PRICE_PRECISION = 8  # decimal places for price calculations
    QUANTITY_PRECISION = 4  # decimal places for quantity calculations
    
    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@carbonxchange.com')
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with configuration"""
        # Create upload directory if it doesn't exist
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format=cls.LOG_FORMAT,
            handlers=[
                logging.FileHandler(cls.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        
        # Validate critical configuration
        cls.validate_config()
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration settings"""
        errors = []
        
        # Check required blockchain configuration
        if not cls.WEB3_PROVIDER_URL:
            errors.append("WEB3_PROVIDER_URL is required")
        
        # Validate JWT configuration
        if len(cls.JWT_SECRET_KEY) < 32:
            errors.append("JWT_SECRET_KEY must be at least 32 characters")
        
        # Check database configuration
        if not hasattr(cls, 'SQLALCHEMY_DATABASE_URI'):
            errors.append("SQLALCHEMY_DATABASE_URI is required")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")

class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f"sqlite:///{Path(__file__).parent / 'database' / 'dev.db'}"
    )
    
    # Security (relaxed for development)
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    
    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)
        logger.info("Application started in DEVELOPMENT mode")

class TestingConfig(BaseConfig):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Security (disabled for testing)
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    
    # Rate limiting (disabled for testing)
    RATELIMIT_ENABLED = False
    
    # JWT (shorter expiration for testing)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=1)
    
    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)
        logger.info("Application started in TESTING mode")

class ProductionConfig(BaseConfig):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Stricter rate limiting
    RATELIMIT_DEFAULT = "100 per hour"
    
    # Logging
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)
        
        # Additional production validations
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise ValueError("DATABASE_URL environment variable is required in production")
        
        if not cls.WEB3_PRIVATE_KEY:
            raise ValueError("WEB3_PRIVATE_KEY environment variable is required in production")
        
        if cls.SECRET_KEY == 'dev-secret-key':
            raise ValueError("SECRET_KEY must be changed in production")
        
        logger.info("Application started in PRODUCTION mode")

class StagingConfig(ProductionConfig):
    """Staging environment configuration"""
    DEBUG = True
    
    # Relaxed rate limiting for testing
    RATELIMIT_DEFAULT = "500 per hour"
    
    # More verbose logging
    LOG_LEVEL = 'INFO'
    
    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)
        logger.info("Application started in STAGING mode")

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: str = None) -> BaseConfig:
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])

