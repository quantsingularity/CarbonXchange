import os

class Config:
    # Use SQLite for testing instead of PostgreSQL
    DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///carbon_market.db')
    WEB3_PROVIDER = os.getenv('WEB3_PROVIDER', 'http://localhost:8545')
    MODEL_PATH = os.getenv('MODEL_PATH', '../ai_models/demand_forecasting_model.pkl')