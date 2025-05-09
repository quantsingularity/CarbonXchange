import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Config:
    # Environment
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = ENV == 'development'
    
    # Database
    DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///carbon_market.db')
    
    # Web3
    WEB3_PROVIDER = os.getenv('WEB3_PROVIDER', 'http://localhost:8545')
    
    # Model
    MODEL_PATH = os.getenv('MODEL_PATH', str(Path(__file__).parent.parent / 'ai_models' / 'demand_forecasting_model.pkl'))
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    
    # API Settings
    API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', '100'))  # requests per minute
    
    @classmethod
    def validate(cls):
        """Validate configuration settings."""
        issues = []
        
        # Check if model file exists
        if not os.path.exists(cls.MODEL_PATH):
            issues.append(f"Model file not found at {cls.MODEL_PATH}")
        
        # Validate database URI
        if not cls.DATABASE_URI:
            issues.append("DATABASE_URI is not set")
        
        # Validate Web3 provider
        if not cls.WEB3_PROVIDER:
            issues.append("WEB3_PROVIDER is not set")
        
        # Validate security keys in production
        if cls.ENV == 'production':
            if cls.SECRET_KEY == 'dev-secret-key':
                issues.append("SECRET_KEY should be changed in production")
            if cls.JWT_SECRET_KEY == 'dev-jwt-secret-key':
                issues.append("JWT_SECRET_KEY should be changed in production")
        
        if issues:
            for issue in issues:
                logger.warning(issue)
            if cls.ENV == 'production':
                raise ValueError("Configuration validation failed in production environment")
        
        return True

# Validate configuration on import
Config.validate()