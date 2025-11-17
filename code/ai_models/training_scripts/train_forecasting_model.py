import os

import pandas as pd
from joblib import dump
from sklearn.ensemble import RandomForestRegressor


def train_model():
    # Use absolute path or relative path from execution directory
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "resources",
        "datasets",
        "market_demand.csv",
    )
    data = pd.read_csv(data_path)
    X = data[["historical_price", "trading_volume", "season"]]
    y = data["demand"]

    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)

    # Save model to the correct location
    model_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "demand_forecasting_model.pkl",
    )
    dump(model, model_path)
    print(f"Model saved to {model_path}")


if __name__ == "__main__":
    train_model()
