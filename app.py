import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Set Page Configuration
st.set_page_config(page_title="Stock Market App", layout="wide")

# Load API Key securely
API_KEY = "LF2I00FT4XHT2WE3"  # Replace with your API key

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

# Sidebar Navigation
with st.sidebar:
    st.title("📊 Stock Market Dashboard")
    st.markdown("<div style='background-color: lightblue; padding: 10px; border-radius: 10px;'>🔑 API Key: YOUR_ALPHA_VANTAGE_API_KEY</div>", unsafe_allow_html=True)
    st.markdown("<div style='background-color: lightblue; padding: 10px; border-radius: 10px;'>📞 Contact: support@stockpredictor.com</div>", unsafe_allow_html=True)
    
    if st.button("📡 Live News", use_container_width=True):
        st.session_state.page = "Live News"
        st.rerun()

    if st.button("📈 Stock Predictor", use_container_width=True):
        st.session_state.page = "Stock Predictor"
        st.rerun()

    if st.button("📊 Top Gainers & Losers", use_container_width=True):
        st.session_state.page = "Top Gainers & Losers"
        st.rerun()
    
    if st.button("📉 Stock Comparison", use_container_width=True):
        st.session_state.page = "Stock Comparison"
        st.rerun()
    
    if st.button("📈 Top Gainer & Loser", use_container_width=True):
        st.session_state.page = "Top Gainer & Loser"
        st.rerun()
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, help="Click to log out"):
        st.session_state.logged_in = False
        st.rerun()

# Function to fetch stock data
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=full"
    response = requests.get(url)
    return response.json()

# Top Gainer & Loser Section
if st.session_state.get("page") == "Top Gainer & Loser":
    st.title("📈 Top Gainer & Loser")

    gainers = {}
    losers = {}
    for company, symbol in companies.items():
        stock_data = get_stock_data(symbol)
        if stock_data:
            df = pd.DataFrame.from_dict(stock_data["Time Series (5min)"], orient="index", dtype=float)
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df.columns = ["Open", "High", "Low", "Close", "Volume"]

            open_price = df.iloc[0]["Open"]
            close_price = df.iloc[-1]["Close"]
            change = close_price - open_price

            if change > 0:
                gainers[company] = change
            else:
                losers[company] = change

    # Display Top Gainer
    if gainers:
        top_gainer = max(gainers, key=gainers.get)
        st.subheader(f"📈 Top Gainer: {top_gainer}")
        symbol = companies[top_gainer]
        df = pd.DataFrame.from_dict(get_stock_data(symbol)["Time Series (5min)"], orient="index", dtype=float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.columns = ["Open", "High", "Low", "Close", "Volume"]

        st.metric(label="📈 Open Price", value=f"${df.iloc[0]['Open']:.2f}")
        fig_gainer = px.line(df, x=df.index, y="Close", title=f"{top_gainer} Stock Price")
        st.plotly_chart(fig_gainer)

    # Display Top Loser
    if losers:
        top_loser = min(losers, key=losers.get)
        st.subheader(f"📉 Top Loser: {top_loser}")
        symbol = companies[top_loser]
        df = pd.DataFrame.from_dict(get_stock_data(symbol)["Time Series (5min)"], orient="index", dtype=float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.columns = ["Open", "High", "Low", "Close", "Volume"]

        st.metric(label="📉 Open Price", value=f"${df.iloc[0]['Open']:.2f}")
        fig_loser = px.line(df, x=df.index, y="Close", title=f"{top_loser} Stock Price")
        st.plotly_chart(fig_loser)
