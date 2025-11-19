"""
Production-ready configuration management for CarbonXchange Backend
Implements financial industry standards for security and compliance
"""

import logging
import os
import secrets
from datetime import timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseConfig:
    """Base configuration with common settings"""

    # Application Settings
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)  # Short-lived for security
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)  # Auto-rotation
    JWT_ALGORITHM = "HS256"
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]

    # Database Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 20,
        "max_overflow": 10,
        "pool_size": 20,
        "echo": False,
    }
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_SLOW_QUERY_THRESHOLD = 0.5

    # Security Settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    # Password Security
    BCRYPT_LOG_ROUNDS = 12
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SYMBOLS = True

    # API Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")
    RATELIMIT_DEFAULT = "1000 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_STRATEGY = "moving-window"

    # Specific endpoint rate limits
    RATELIMIT_AUTH_LOGIN = "5 per minute"
    RATELIMIT_AUTH_REGISTER = "3 per minute"
    RATELIMIT_TRADING_ORDER = "100 per minute"
    RATELIMIT_MARKET_DATA = "1000 per minute"

    # CORS Configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    CORS_ALLOW_HEADERS = [
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token",
    ]
    CORS_EXPOSE_HEADERS = [
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ]

    # Blockchain Configuration
    WEB3_PROVIDER_URL = os.getenv(
        "WEB3_PROVIDER_URL", "https://polygon-mainnet.infura.io/v3/"
    )
    WEB3_PRIVATE_KEY = os.getenv("WEB3_PRIVATE_KEY")
    WEB3_CHAIN_ID = int(os.getenv("WEB3_CHAIN_ID", "137"))  # Polygon mainnet
    WEB3_GAS_LIMIT = int(os.getenv("WEB3_GAS_LIMIT", "500000"))
    WEB3_GAS_PRICE_MULTIPLIER = float(os.getenv("WEB3_GAS_PRICE_MULTIPLIER", "1.1"))

    # Smart Contract Addresses
    CARBON_TOKEN_CONTRACT_ADDRESS = os.getenv("CARBON_TOKEN_CONTRACT_ADDRESS")
    MARKETPLACE_CONTRACT_ADDRESS = os.getenv("MARKETPLACE_CONTRACT_ADDRESS")
    REGISTRY_CONTRACT_ADDRESS = os.getenv("REGISTRY_CONTRACT_ADDRESS")
    ESCROW_CONTRACT_ADDRESS = os.getenv("ESCROW_CONTRACT_ADDRESS")

    # External Services
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/2")
    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/3"
    )

    # Celery Configuration
    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_ACCEPT_CONTENT = ["json"]
    CELERY_TIMEZONE = "UTC"
    CELERY_ENABLE_UTC = True
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
    CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes

    # File Storage
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(Path(__file__).parent / "uploads"))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif", "doc", "docx", "txt"}

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = (
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    LOG_FILE = os.getenv("LOG_FILE", "carbonxchange.log")
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5

    # Compliance and Audit
    AUDIT_LOG_ENABLED = True
    AUDIT_LOG_FILE = os.getenv("AUDIT_LOG_FILE", "audit.log")
    DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "2555"))  # 7 years
    COMPLIANCE_MONITORING_ENABLED = True

    # KYC/AML Configuration
    KYC_VERIFICATION_REQUIRED = True
    KYC_DOCUMENT_RETENTION_DAYS = 2555  # 7 years
    AML_SCREENING_ENABLED = True
    AML_RISK_THRESHOLD = float(os.getenv("AML_RISK_THRESHOLD", "0.7"))

    # Market Data Configuration
    MARKET_DATA_UPDATE_INTERVAL = int(
        os.getenv("MARKET_DATA_UPDATE_INTERVAL", "60")
    )  # seconds
    PRICE_PRECISION = 8  # decimal places for price calculations
    QUANTITY_PRECISION = 4  # decimal places for quantity calculations
    MARKET_DATA_RETENTION_DAYS = 365  # 1 year of historical data

    # Trading Configuration
    TRADING_ENABLED = True
    TRADING_HOURS_START = 9  # 9 AM UTC
    TRADING_HOURS_END = 17  # 5 PM UTC
    TRADING_WEEKENDS_ENABLED = False
    ORDER_EXPIRY_HOURS = 24
    MAX_ORDER_SIZE = 1000000  # Maximum order size
    MIN_ORDER_SIZE = 1  # Minimum order size

    # Email Configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() in ["true", "1", "yes"]
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() in ["true", "1", "yes"]
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@carbonxchange.com")

    # Notification Configuration
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

    # Monitoring and Metrics
    PROMETHEUS_METRICS_ENABLED = True
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    HEALTH_CHECK_ENABLED = True
    PERFORMANCE_MONITORING_ENABLED = True

    # Feature Flags
    FEATURE_BLOCKCHAIN_INTEGRATION = (
        os.getenv("FEATURE_BLOCKCHAIN_INTEGRATION", "true").lower() == "true"
    )
    FEATURE_ADVANCED_ANALYTICS = (
        os.getenv("FEATURE_ADVANCED_ANALYTICS", "true").lower() == "true"
    )
    FEATURE_AUTOMATED_COMPLIANCE = (
        os.getenv("FEATURE_AUTOMATED_COMPLIANCE", "true").lower() == "true"
    )
    FEATURE_REAL_TIME_NOTIFICATIONS = (
        os.getenv("FEATURE_REAL_TIME_NOTIFICATIONS", "true").lower() == "true"
    )

    # Cache Configuration
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/4")
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    CACHE_KEY_PREFIX = "carbonxchange:"

    @classmethod
    def init_app(cls, app):
        """Initialize application with configuration"""
        # Create upload directory if it doesn't exist
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)

        # Configure logging
        from logging.handlers import RotatingFileHandler

        # File handler with rotation
        file_handler = RotatingFileHandler(
            cls.LOG_FILE, maxBytes=cls.LOG_MAX_BYTES, backupCount=cls.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(logging.Formatter(cls.LOG_FORMAT))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(cls.LOG_FORMAT))

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, cls.LOG_LEVEL))
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        # Validate critical configuration
        cls.validate_config()

    @classmethod
    def validate_config(cls):
        """Validate critical configuration settings"""
        errors = []

        # Check required blockchain configuration
        if cls.FEATURE_BLOCKCHAIN_INTEGRATION and not cls.WEB3_PROVIDER_URL:
            errors.append(
                "WEB3_PROVIDER_URL is required when blockchain integration is enabled"
            )

        # Validate JWT configuration
        if len(cls.JWT_SECRET_KEY) < 32:
            errors.append("JWT_SECRET_KEY must be at least 32 characters")

        # Check database configuration
        if not hasattr(cls, "SQLALCHEMY_DATABASE_URI"):
            errors.append("SQLALCHEMY_DATABASE_URI is required")

        # Validate password requirements
        if cls.PASSWORD_MIN_LENGTH < 8:
            errors.append("PASSWORD_MIN_LENGTH must be at least 8")

        # Validate trading configuration
        if cls.MAX_ORDER_SIZE <= cls.MIN_ORDER_SIZE:
            errors.append("MAX_ORDER_SIZE must be greater than MIN_ORDER_SIZE")

        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")


class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""

    DEBUG = True
    TESTING = False
    ENV = "development"

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{Path(__file__).parent / 'database' / 'dev.db'}"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        **BaseConfig.SQLALCHEMY_ENGINE_OPTIONS,
        "echo": True,  # Enable SQL logging in development
    }

    # Security (relaxed for development)
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False

    # Rate limiting (relaxed for development)
    RATELIMIT_DEFAULT = "10000 per hour"
    RATELIMIT_AUTH_LOGIN = "100 per minute"
    RATELIMIT_AUTH_REGISTER = "50 per minute"

    # Logging
    LOG_LEVEL = "DEBUG"

    # Feature flags (all enabled for development)
    FEATURE_BLOCKCHAIN_INTEGRATION = False  # Disabled to avoid blockchain dependency

    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)

        # Create database directory
        db_path = Path(cls.SQLALCHEMY_DATABASE_URI.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Application started in DEVELOPMENT mode")


class TestingConfig(BaseConfig):
    """Testing environment configuration"""

    DEBUG = True
    TESTING = True
    ENV = "testing"

    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # Security (disabled for testing)
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False

    # Rate limiting (disabled for testing)
    RATELIMIT_ENABLED = False

    # JWT (shorter expiration for testing)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=1)

    # Features (disabled for testing)
    FEATURE_BLOCKCHAIN_INTEGRATION = False
    FEATURE_REAL_TIME_NOTIFICATIONS = False

    # Compliance (relaxed for testing)
    KYC_VERIFICATION_REQUIRED = False
    AML_SCREENING_ENABLED = False

    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)
        logger.info("Application started in TESTING mode")


class ProductionConfig(BaseConfig):
    """Production environment configuration"""

    DEBUG = False
    TESTING = False
    ENV = "production"

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"

    # Stricter rate limiting
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_AUTH_LOGIN = "5 per minute"
    RATELIMIT_AUTH_REGISTER = "3 per minute"
    RATELIMIT_TRADING_ORDER = "50 per minute"

    # Logging
    LOG_LEVEL = "WARNING"

    # Enhanced password security
    BCRYPT_LOG_ROUNDS = 14

    # All features enabled in production
    FEATURE_BLOCKCHAIN_INTEGRATION = True
    FEATURE_ADVANCED_ANALYTICS = True
    FEATURE_AUTOMATED_COMPLIANCE = True
    FEATURE_REAL_TIME_NOTIFICATIONS = True

    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)

        # Additional production validations
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise ValueError(
                "DATABASE_URL environment variable is required in production"
            )

        if cls.FEATURE_BLOCKCHAIN_INTEGRATION and not cls.WEB3_PRIVATE_KEY:
            raise ValueError(
                "WEB3_PRIVATE_KEY environment variable is required in production"
            )

        if cls.SECRET_KEY == "dev-secret-key":
            raise ValueError("SECRET_KEY must be changed in production")

        # Validate all smart contract addresses are set
        required_contracts = [
            "CARBON_TOKEN_CONTRACT_ADDRESS",
            "MARKETPLACE_CONTRACT_ADDRESS",
            "REGISTRY_CONTRACT_ADDRESS",
            "ESCROW_CONTRACT_ADDRESS",
        ]

        for contract in required_contracts:
            if cls.FEATURE_BLOCKCHAIN_INTEGRATION and not getattr(cls, contract):
                raise ValueError(
                    f"{contract} environment variable is required in production"
                )

        logger.info("Application started in PRODUCTION mode")


class StagingConfig(ProductionConfig):
    """Staging environment configuration"""

    DEBUG = True
    ENV = "staging"

    # Relaxed rate limiting for testing
    RATELIMIT_DEFAULT = "500 per hour"
    RATELIMIT_AUTH_LOGIN = "20 per minute"
    RATELIMIT_AUTH_REGISTER = "10 per minute"

    # More verbose logging
    LOG_LEVEL = "INFO"

    # Relaxed password security
    BCRYPT_LOG_ROUNDS = 12

    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)
        logger.info("Application started in STAGING mode")


# Configuration mapping
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(config_name: str = None) -> BaseConfig:
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "default")

    return config.get(config_name, config["default"])
