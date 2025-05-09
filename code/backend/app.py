from flask import Flask, jsonify, request
import joblib
import pandas as pd
import json
import os
import random
import logging
from config import Config
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Try to load model, use a dummy model if it fails
try:
    model = joblib.load(Config.MODEL_PATH)
    logger.info("Successfully loaded ML model")
except Exception as e:
    logger.warning(f"Could not load model: {e}")
    # Create a simple dummy model that returns random predictions
    class DummyModel:
        def predict(self, features):
            return [0.58 + (random.random() - 0.5) * 0.1]
    
    model = DummyModel()
    logger.info("Using dummy model for predictions")

# Load contract ABIs
try:
    with open('../blockchain/contracts/CarbonCreditToken.sol', 'r') as f:
        token_contract_source = f.read()
    with open('../blockchain/contracts/Marketplace.sol', 'r') as f:
        marketplace_contract_source = f.read()
    logger.info("Successfully loaded contract sources")
except Exception as e:
    logger.error(f"Could not load contract sources: {e}")
    token_contract_source = ""
    marketplace_contract_source = ""

@app.route('/api/forecast', methods=['POST'])
def forecast_demand():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['historical_price', 'trading_volume', 'season']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            if not isinstance(data[field], (int, float)):
                return jsonify({'error': f'Invalid data type for {field}'}), 400
                
        features = pd.DataFrame([data])
        prediction = model.predict(features)
        return jsonify({'forecast': float(prediction[0])})
    except Exception as e:
        logger.error(f'Forecast error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/listings', methods=['GET'])
def get_listings():
    try:
        # Return mock data for testing
        sample_listings = [
            {"id": 1, "seller": "0x1234...5678", "amount": 100, "pricePerToken": 0.5, "project": "Solar Farm - California"},
            {"id": 2, "seller": "0x5678...9012", "amount": 200, "pricePerToken": 0.4, "project": "Wind Farm - Texas"},
            {"id": 3, "seller": "0x9876...1234", "amount": 150, "pricePerToken": 0.6, "project": "Reforestation - Amazon"}
        ]
        return jsonify(sample_listings)
    except Exception as e:
        logger.error(f'Error fetching listings: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/credit-distribution', methods=['GET'])
def get_credit_distribution():
    try:
        # Sample data for credit distribution
        distribution = [
            {"name": "Renewable Energy", "value": 45},
            {"name": "Reforestation", "value": 30},
            {"name": "Methane Capture", "value": 25}
        ]
        return jsonify(distribution)
    except Exception as e:
        logger.error(f'Error fetching credit distribution: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/user/<wallet_address>', methods=['GET'])
def get_user(wallet_address):
    try:
        if not wallet_address or not isinstance(wallet_address, str) or len(wallet_address) != 42:
            return jsonify({'error': 'Invalid wallet address'}), 400
            
        # Return mock user data
        return jsonify({
            "wallet_address": wallet_address,
            "credit_balance": 250
        })
    except Exception as e:
        logger.error(f'Error fetching user data: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Check if model is loaded
        model_status = "healthy" if not isinstance(model, DummyModel) else "using_dummy"
        
        # Check if contract sources are loaded
        contract_status = "healthy" if token_contract_source and marketplace_contract_source else "missing"
        
        return jsonify({
            "status": "healthy",
            "model": model_status,
            "contracts": contract_status,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f'Health check error: {str(e)}')
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
