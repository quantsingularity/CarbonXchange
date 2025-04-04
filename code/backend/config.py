import os

class Config:
    DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql://user:pass@localhost/carbon_market')
    WEB3_PROVIDER = os.getenv('WEB3_PROVIDER', 'http://localhost:8545')
    MODEL_PATH = os.getenv('MODEL_PATH', '../ai_models/demand_forecasting_model.pkl')