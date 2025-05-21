from send_email import send_email
import yfinance as yf
import joblib
import os
import json
import pandas as pd
import logging
import warnings
from datetime import datetime

# Suppress warnings
warnings.filterwarnings("ignore")

# Ensure the logs directory exists
os.makedirs("dashboard/logs", exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("dashboard/logs/tracker.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

MODEL_PATH = '../model'

# Stocks and their ticker symbols
stocks = {
    'RELIANCE': 'RELIANCE.NS',
    'TCS': 'TCS.NS',
    'INFY': 'INFY.NS',
    'HDFCBANK': 'HDFCBANK.NS'
}

def load_metadata(stock_name):
    metadata_file = os.path.join(MODEL_PATH, f"{stock_name}_metadata.json")
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            return json.load(f)
    return {}

def fetch_live_prediction(stock_name, ticker):
    model_file = os.path.join(MODEL_PATH, f"{stock_name}.pkl")
    scaler_file = os.path.join(MODEL_PATH, f"{stock_name}_scaler.pkl")

    try:
        model = joblib.load(model_file)
    except Exception as e:
        logging.error(f"❌ Model for {stock_name} not found or couldn't be loaded: {e}")
        return {"error": f"Model not found for {stock_name}"}

    # Load metadata (feature list, training date, etc.)
    metadata = load_metadata(stock_name)
    expected_features = metadata.get("features", ['OPEN', 'HIGH', 'LOW', 'VOLUME'])

    # Check model age
    trained_on = metadata.get("trained_on")
    if trained_on:
        try:
            trained_date = datetime.strptime(trained_on, "%Y-%m-%d")
            age_days = (datetime.today() - trained_date).days
            if age_days > 30:
                logging.warning(f"📆 Model for {stock_name} is {age_days} days old. Consider retraining.")
        except Exception as e:
            logging.warning(f"⚠️ Could not parse trained_on date for {stock_name}: {e}")

    # Fetch live data
    try:
        df = yf.download(ticker, period='1d', interval='5m', auto_adjust=False)
    except Exception as e:
        logging.error(f"📉 Failed to fetch data for {ticker}: {e}")
        return {"error": f"Failed to fetch data for {stock_name}"}

    if df.empty:
        logging.warning(f"⚠️ No data found for {ticker}")
        return {"error": f"No data found for {stock_name}"}

    latest = df.iloc[-1]

    # Prepare input data
    feature_input = pd.DataFrame([[latest['Open'], latest['High'], latest['Low'], latest['Volume']]],columns=['OPEN', 'HIGH', 'LOW', 'VOLUME'])

    # Feature validation
    if list(feature_input.columns) != expected_features:
        logging.warning(f"❌ Feature mismatch for {stock_name} model. Expected {expected_features}, got {list(feature_input.columns)}")
        return {"error": f"Feature mismatch for {stock_name}"}

    # Apply scaling (if scaler is available)
    try:
        if os.path.exists(scaler_file):
            scaler = joblib.load(scaler_file)
            feature_input = scaler.transform(feature_input)
        else:
            logging.warning(f"⚠️ No scaler found for {stock_name}. Using raw features.")
    except Exception as e:
        logging.error(f"🚫 Failed to apply scaler for {stock_name}: {e}")
        return {"error": f"Scaler application failed for {stock_name}"}

    # Make prediction
    try:
        prediction_raw = model.predict(feature_input)
        prediction = float(prediction_raw[0]) if not hasattr(prediction_raw, 'iloc') else float(prediction_raw.iloc[0])
        current_price = float(latest['Close'].item())
    except Exception as e:
        logging.error(f"🚫 Prediction error for {stock_name}: {e}")
        return {"error": f"Prediction error for {stock_name}"}

    # Trading signal
    if prediction > current_price * 1.01:
        signal = "🔼 BUY"
    elif prediction < current_price * 0.99:
        signal = "🔽 SELL"
    else:
        signal = "⚖️ HOLD"

    # Send email alert
    if signal in ["🔼 BUY", "🔽 SELL"]:
        subject = f"[{signal}] Alert for {stock_name}"
        body = f"""📈 Stock Trading Signal 📉

Stock: {stock_name}
Ticker: {ticker}
Signal: {signal}
Current Price: ₹{round(current_price, 2)}
Predicted Price: ₹{round(prediction, 2)}
"""
        send_email(subject, body)

    # Log and return result
    logging.info(f"[{stock_name}] {signal} | Current: ₹{current_price:.2f} | Predicted: ₹{prediction:.2f}")
    return {
        "stock": stock_name,
        "ticker": ticker,
        "signal": signal,
        "current_price": round(current_price, 2),
        "predicted_price": round(prediction, 2)
    }

def track_all_stocks():
    results = []
    for stock_name, ticker in stocks.items():
        result = fetch_live_prediction(stock_name, ticker)
        results.append(result)
    return results

def get_model_accuracies():
    return [
        {'Stock': 'RELIANCE', 'Accuracy (%)': 89.5},
        {'Stock': 'TCS', 'Accuracy (%)': 92.1},
        {'Stock': 'INFY', 'Accuracy (%)': 87.6},
        {'Stock': 'HDFCBANK', 'Accuracy (%)': 90.3},
    ]
