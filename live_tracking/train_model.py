import yfinance as yf
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
import json
from datetime import datetime

MODEL_PATH = "model"

os.makedirs(MODEL_PATH, exist_ok=True)

# Stock list
stocks = {
    'RELIANCE': 'RELIANCE.NS',
    'TCS': 'TCS.NS',
    'INFY': 'INFY.NS',
    'HDFCBANK': 'HDFCBANK.NS'
}

# Features and target
features = ['Open', 'High', 'Low', 'Volume']
target = 'Close'

def train_and_save_model(stock_name, ticker):
    print(f"📥 Fetching data for {stock_name} ({ticker})")
    df = yf.download(ticker, period="60d", interval="1d", auto_adjust=False)

    if df.empty:
        print(f"❌ No data for {stock_name}")
        return

    df = df.dropna()
    X = df[features]
    y = df[target]

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    model = LinearRegression()
    model.fit(X_scaled, y)

    # Save model
    model_file = os.path.join(MODEL_PATH, f"{stock_name}.pkl")
    joblib.dump(model, model_file)

    # Save scaler
    scaler_file = os.path.join(MODEL_PATH, f"{stock_name}_scaler.pkl")
    joblib.dump(scaler, scaler_file)

    # Save metadata
    metadata = {
        "features": [f.upper() for f in features],  # Ensure consistency with tracker.py
        "trained_on": datetime.today().strftime("%Y-%m-%d")
    }
    metadata_file = os.path.join(MODEL_PATH, f"{stock_name}_metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=4)

    print(f"✅ Model, scaler, and metadata saved for {stock_name}")

# Train all
for stock, ticker in stocks.items():
    train_and_save_model(stock, ticker)
