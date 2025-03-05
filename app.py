import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
import os

# Load API Key securely
API_KEY = os.getenv("LF2I00FT4XHT2WE3")  # Set this in your environment variables

# List of stock symbols
companies = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Google (GOOGL)": "GOOGL",
    "Amazon (AMZN)": "AMZN",
    "Tesla (TSLA)": "TSLA",
    "Meta (META)": "META",
    "NVIDIA (NVDA)": "NVDA",
    "Netflix (NFLX)": "NFLX",
    "Intel (INTC)": "INTC",
    "IBM (IBM)": "IBM"
}

# Streamlit UI decorations
st.set_page_config(page_title="📊 Live Stock Predictor", layout="wide")
st.markdown("""
    <style>
        body {
            background-color: #f5f5f5;
        }
        .main {
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #007bff;
        }
        .stButton button {
            background-color: #28a745;
            color: white;
        }
        .stButton button:hover {
            background-color: #218838;
        }
        .stMetric {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Header and instructions
st.title("📈 Live Stock Market Predictor")

# Select Company
selected_company = st.selectbox("Select a Company", list(companies.keys()))
symbol = companies[selected_company]

# Input for investment amount
investment_amount = st.number_input("Enter Investment Amount ($)", min_value=10, max_value=10000, step=10)

# Function to get stock data
def get_intraday_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=compact"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "Time Series (5min)" not in data:
            return None
        return data["Time Series (5min)"]
    except requests.exceptions.RequestException as e:
        st.error(f"⚠ API request failed: {e}")
        return None

if st.button("🔍 Predict Intraday Profit/Loss"):
    stock_data = get_intraday_data(symbol)
    if stock_data:
        try:
            df = pd.DataFrame.from_dict(stock_data, orient="index", dtype=float)
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df.columns = ["Open", "High", "Low", "Close", "Volume"]

            current_price = df.iloc[-1]["Close"]
            open_price = df.iloc[0]["Open"]

            # Display stock data
            st.metric(label="📌 Open Price", value=f"${open_price:.2f}")
            st.metric(label="📌 Current Price", value=f"${current_price:.2f}")
            
            shares_to_buy = investment_amount / current_price
            st.info(f"📊 With ${investment_amount}, you can buy approximately {shares_to_buy:.2f} shares.")

            # Chart and prediction logic
            df["Minutes"] = np.arange(len(df))
            X = df["Minutes"].values.reshape(-1, 1)
            y = df["Close"].values.reshape(-1, 1)
            
            # Live stock price chart
            st.subheader("📊 Live Stock Price Movement")
            st.line_chart(df["Close"])

        except Exception as e:
            st.error(f"⚠ An error occurred while processing data: {e}")
    else:
        st.error("⚠ Could not fetch stock data. API limit may have been reached or invalid API key.")
