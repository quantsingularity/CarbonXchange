import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from joblib import dump

def train_model():
    data = pd.read_csv('../../resources/datasets/market_demand.csv')
    X = data[['historical_price', 'trading_volume', 'season']]
    y = data['demand']
    
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)
    
    dump(model, '../../demand_forecasting_model.pkl')

if __name__ == "__main__":
    train_model()