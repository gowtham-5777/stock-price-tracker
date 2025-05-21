from flask import Flask, jsonify
import joblib
import yfinance as yf
import pandas as pd
import os

from config import stocks, MODEL_PATH  # ✅ NEW: imported constants
from auth.login import login, logout

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()
else:
    logout()

app = Flask(__name__)

def fetch_live_prediction(stock_name, ticker):
    model_file = os.path.join(MODEL_PATH, f"{stock_name}.pkl")

    try:
        model = joblib.load(model_file)
    except Exception as e:
        return {"error": f"Model not found for {stock_name}: {str(e)}"}

    df = yf.download(ticker, period='1d', interval='5m', auto_adjust=False)
    if df.empty:
        return {"error": f"No data found for {ticker}"}

    latest = df.iloc[-1]
    feature_input = pd.DataFrame(
        [[latest['Open'], latest['High'], latest['Low'], latest['Volume']]],
        columns=['OPEN', 'HIGH', 'LOW', 'VOLUME']
    )

    try:
        prediction = float(model.predict(feature_input)[0])
        current_price = float(latest['Close'].item())
    except Exception as e:
        return {"error": f"Prediction failed for {stock_name}: {str(e)}"}

    if prediction > current_price * 1.01:
        signal = "🔼 BUY"
    elif prediction < current_price * 0.99:
        signal = "🔽 SELL"
    else:
        signal = "⚖️ HOLD"

    return {
        "stock": stock_name,
        "signal": signal,
        "current_price": round(current_price, 2),
        "predicted_price": round(prediction, 2)
    }

@app.route('/predict/<stock_name>')
def predict(stock_name):
    stock_name = stock_name.upper()
    if stock_name not in stocks:
        return jsonify({"error": f"Stock {stock_name} is not supported."}), 400

    result = fetch_live_prediction(stock_name, stocks[stock_name])
    return jsonify(result)

@app.route('/predict_all')
def predict_all():
    results = {}
    for stock_name, ticker in stocks.items():
        results[stock_name] = fetch_live_prediction(stock_name, ticker)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
