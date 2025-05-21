# live_tracking/dashboard/app.py

import streamlit as st
import pandas as pd
import os
import sys
import time
import altair as alt

# Add parent directory to path to import tracker
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tracker import track_all_stocks

# --- Page config ---
st.set_page_config(page_title="📊 Stock Prediction Dashboard", layout="wide")

# --- Custom Theme ---
st.markdown("""
    <style>
        body {
            background-color: #ffffff;
        }
        .main {
            background-color: #f0f8ff;
        }
        h1, h2, h3 {
            color: #004d40;
        }
        .css-18e3th9 {
            background-color: #f0f8ff;
            padding: 2rem;
            border-radius: 12px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Stock Prediction Dashboard")

# --- Sidebar Options ---
st.sidebar.header("🔎 Filter & Options")
refresh_rate = st.sidebar.slider("Auto-refresh every N seconds", 10, 300, 60)
show_signal = st.sidebar.multiselect("Filter by Signal", ['🔼 BUY', '🔽 SELL', '⚖️ HOLD'], default=['🔼 BUY', '🔽 SELL', '⚖️ HOLD'])

# Fetch live stock predictions
results = track_all_stocks()

# Prepare dropdown options
stock_options = [item for item in results if 'error' not in item]
stock_names = [item['stock'] for item in stock_options]
selected_stock = st.sidebar.selectbox("Select Stock for Chart", stock_names if stock_names else ["No data"])

# --- Live Predictions Table ---
st.markdown("### 📈 Live Model Predictions")

filtered_results = [res for res in results if res.get('signal') in show_signal and 'error' not in res]
df = pd.DataFrame(filtered_results)

if not df.empty:
    df_display = df[['stock', 'ticker', 'current_price', 'predicted_price', 'signal']]
    df_display.columns = ['Stock', 'Ticker', 'Current Price (₹)', 'Predicted Price (₹)', 'Signal']
    
    df_display = df_display.style.applymap(
        lambda x: "background-color: #d4edda; color: green;" if x == '🔼 BUY'
        else ("background-color: #f8d7da; color: red;" if x == '🔽 SELL'
        else "background-color: #fff3cd; color: orange;"),
        subset=['Signal']
    )
    st.dataframe(df_display, use_container_width=True)
else:
    st.warning("No valid stock data to display.")

# --- Price Movement Chart ---
st.markdown("### 📊 Price Movement Chart")

valid_results = [r for r in results if 'error' not in r and r.get('current_price') is not None and r.get('predicted_price') is not None]

if valid_results:
    df_chart = pd.DataFrame(valid_results)[['stock', 'current_price', 'predicted_price']]
    chart_data = df_chart.melt(id_vars='stock', value_vars=['current_price', 'predicted_price'],
                                var_name='Price Type', value_name='Price')

    chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('stock:N', title='Stock'),
        y=alt.Y('Price:Q', title='Price (₹)'),
        color=alt.Color('Price Type:N', legend=alt.Legend(title="")),
        tooltip=['stock', 'Price Type', 'Price']
    ).properties(
        width=700,
        height=400,
        title="📉 Current vs Predicted Stock Prices"
    )

    st.altair_chart(chart, use_container_width=True)
else:
    st.warning("⚠️ No valid price data available to show the chart.")

# --- Model Accuracy Chart (Mockup) ---
st.markdown(" 🎯 Model Accuracy Chart")
accuracy_data = pd.DataFrame(get_model_accuracies())
st.bar_chart(accuracy_data.set_index('Stock'))

# --- Alert History ---
st.markdown("### 📨 Alert History (Last 20 Entries)")
log_path = "../logs/email_alerts.log"

if os.path.exists(log_path):
    with open(log_path, "r") as file:
        logs = file.readlines()[-20:]
        for line in logs:
            st.text(line.strip())
else:
    st.info("No alert log history found yet.")

# --- Auto Refresh ---
with st.spinner(f"Refreshing in {refresh_rate} seconds..."):
    time.sleep(refresh_rate)

# Use safe rerun
try:
    st.experimental_rerun()
except AttributeError:
    st.warning("Streamlit rerun function not found.")
