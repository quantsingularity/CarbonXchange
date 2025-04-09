from flask import Flask, jsonify, request
import joblib
import pandas as pd
import json
import os
import random
from config import Config

app = Flask(__name__)

# Try to load model, use a dummy model if it fails
try:
    model = joblib.load(Config.MODEL_PATH)
except Exception as e:
    print(f"Warning: Could not load model: {e}")
    # Create a simple dummy model that returns random predictions
    class DummyModel:
        def predict(self, features):
            return [0.58 + (random.random() - 0.5) * 0.1]
    
    model = DummyModel()
    print("Using dummy model for predictions")

# Load contract ABIs
try:
    with open('../blockchain/contracts/CarbonCreditToken.sol', 'r') as f:
        token_contract_source = f.read()

    with open('../blockchain/contracts/Marketplace.sol', 'r') as f:
        marketplace_contract_source = f.read()
except Exception as e:
    print(f"Warning: Could not load contract sources: {e}")
    token_contract_source = ""
    marketplace_contract_source = ""

@app.route('/api/forecast', methods=['POST'])
def forecast_demand():
    data = request.json
    features = pd.DataFrame([data])
    prediction = model.predict(features)
    return jsonify({'forecast': prediction[0]})

@app.route('/api/listings', methods=['GET'])
def get_listings():
    # Return mock data for testing
    sample_listings = [
        {"id": 1, "seller": "0x1234...5678", "amount": 100, "pricePerToken": 0.5, "project": "Solar Farm - California"},
        {"id": 2, "seller": "0x5678...9012", "amount": 200, "pricePerToken": 0.4, "project": "Wind Farm - Texas"},
        {"id": 3, "seller": "0x9876...1234", "amount": 150, "pricePerToken": 0.6, "project": "Reforestation - Amazon"}
    ]
    return jsonify(sample_listings)

@app.route('/api/credit-distribution', methods=['GET'])
def get_credit_distribution():
    # Sample data for credit distribution
    distribution = [
        {"name": "Renewable Energy", "value": 45},
        {"name": "Reforestation", "value": 30},
        {"name": "Methane Capture", "value": 25}
    ]
    return jsonify(distribution)

@app.route('/api/user/<wallet_address>', methods=['GET'])
def get_user(wallet_address):
    # Return mock user data
    return jsonify({
        "wallet_address": wallet_address,
        "credit_balance": 250
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
