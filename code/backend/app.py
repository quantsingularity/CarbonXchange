from flask import Flask, jsonify
from web3 import Web3
import joblib
import pandas as pd

app = Flask(__name__)
w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
model = joblib.load('../ai_models/demand_forecasting_model.pkl')

# Load contract ABIs
with open('../blockchain/build/contracts/CarbonCreditToken.json') as f:
    token_abi = json.load(f)['abi']

@app.route('/api/forecast', methods=['POST'])
def forecast_demand():
    data = request.json
    features = pd.DataFrame([data])
    prediction = model.predict(features)
    return jsonify({'forecast': prediction[0]})

@app.route('/api/listings', methods=['GET'])
def get_listings():
    contract = w3.eth.contract(
        address='0x...', 
        abi=Marketplace_ABI
    )
    listings = contract.functions.getAllListings().call()
    return jsonify(listings)

if __name__ == '__main__':
    app.run(port=5000)