import pandas as pd
from sklearn.preprocessing import StandardScaler


def preprocess_data(filepath: Any) -> Any:
    df = pd.read_csv(filepath)
    df = df.fillna(df.mean())
    df["price_volume_ratio"] = df["historical_price"] / df["trading_volume"]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(
        df[["historical_price", "trading_volume", "price_volume_ratio"]]
    )
    return pd.DataFrame(scaled_features, columns=["price", "volume", "ratio"])
