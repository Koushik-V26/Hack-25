import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

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

# Authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login_page():
    st.title("🔑 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "password":  # Dummy login
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Invalid credentials. Try again.")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# Streamlit App Main Page
st.set_page_config(page_title="📊 Stock Market Prediction", layout="wide")

# Sidebar Navigation
with st.sidebar:
    st.title("📊 Stock Market Navigation")
    page = st.radio("Go to:", ["Live News", "Stock Predictor", "Top Gainers & Losers", "Stock Comparison"])
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# Function to fetch stock data
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=compact"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("Time Series (5min)", None)
    except requests.exceptions.RequestException as e:
        st.error(f"⚠ API request failed: {e}")
        return None

# Live News Section (Placeholder)
if page == "Live News":
    st.title("📰 Live Stock Market News")
    st.write("Fetching real-time stock news...")

# Stock Market Predictor
elif page == "Stock Predictor":
    st.title("📈 Stock Market Predictor")
    selected_company = st.selectbox("Select a Company", list(companies.keys()))
    symbol = companies[selected_company]
    stock_data = get_stock_data(symbol)
    if stock_data:
        df = pd.DataFrame.from_dict(stock_data, orient="index", dtype=float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.columns = ["Open", "High", "Low", "Close", "Volume"]
        
        st.subheader("📊 Stock Price Movement")
        fig = px.line(df, x=df.index, y="Close", title=f"{selected_company} Stock Price")
        st.plotly_chart(fig)

# Top Gainers & Losers
elif page == "Top Gainers & Losers":
    st.title("📊 Top Gainers & Losers")
    gainers = {}
    losers = {}
    for company, symbol in companies.items():
        stock_data = get_stock_data(symbol)
        if stock_data:
            df = pd.DataFrame.from_dict(stock_data, orient="index", dtype=float)
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
    
    if gainers:
        top_gainer = max(gainers, key=gainers.get)
        st.subheader(f"📈 Top Gainer: {top_gainer}")
        symbol = companies[top_gainer]
        df = pd.DataFrame.from_dict(get_stock_data(symbol), orient="index", dtype=float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.columns = ["Open", "High", "Low", "Close", "Volume"]
        fig = px.line(df, x=df.index, y="Close", title=f"{top_gainer} Stock Price")
        st.plotly_chart(fig)
    
    if losers:
        top_loser = min(losers, key=losers.get)
        st.subheader(f"📉 Top Loser: {top_loser}")
        symbol = companies[top_loser]
        df = pd.DataFrame.from_dict(get_stock_data(symbol), orient="index", dtype=float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.columns = ["Open", "High", "Low", "Close", "Volume"]
        fig = px.line(df, x=df.index, y="Close", title=f"{top_loser} Stock Price")
        st.plotly_chart(fig)

# Stock Comparison (Placeholder)
elif page == "Stock Comparison":
    st.title("📊 Stock Comparison")
    st.write("Compare two stocks on their profit/loss and plot their graphs.")
