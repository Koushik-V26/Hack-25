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
}

# Login System
def login():
    st.title("🔐 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "password":
            st.session_state["logged_in"] = True
            st.experimental_rerun()
        else:
            st.error("Invalid Credentials")

# Fetch live stock data
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=compact"
    response = requests.get(url).json()
    return response.get("Time Series (5min)", {})

# Live News Section
def show_live_news():
    st.subheader("📢 Live Stock Market News")
    st.write("(Fetching real-time stock market news...)")
    # Placeholder: Replace with actual news API integration
    st.info("🚀 Stock Market is showing bullish trends today!")

# Stock Predictor
def stock_predictor():
    st.subheader("📈 Stock Market Predictor")
    selected_company = st.selectbox("Select a Company", list(companies.keys()))
    symbol = companies[selected_company]
    stock_data = get_stock_data(symbol)
    
    if stock_data:
        df = pd.DataFrame.from_dict(stock_data, orient="index", dtype=float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.columns = ["Open", "High", "Low", "Close", "Volume"]
        
        # Plot stock price
        fig = px.line(df, x=df.index, y="Close", title=f"{selected_company} Stock Price")
        st.plotly_chart(fig)
        
        # Buy/Sell Recommendation
        buy_percentage = np.random.randint(40, 60)
        sell_percentage = 100 - buy_percentage
        st.metric(label="📈 Buy Percentage", value=f"{buy_percentage}%")
        st.metric(label="📉 Sell Percentage", value=f"{sell_percentage}%")
    else:
        st.error("Failed to fetch stock data.")

# Top Gainers & Losers
def show_top_gainers_losers():
    st.subheader("📊 Top Gainers & Losers")
    if st.button("📈 Show Gainers"):
        st.success("(Displaying top-performing stocks of the day...)")
    if st.button("📉 Show Losers"):
        st.error("(Displaying worst-performing stocks of the day...)")

# Stock Comparison
def stock_comparison():
    st.subheader("📊 Stock Comparison")
    stock1, stock2 = st.selectbox("Select Stock 1", list(companies.keys())), st.selectbox("Select Stock 2", list(companies.keys()))
    symbol1, symbol2 = companies[stock1], companies[stock2]
    
    st.info(f"Comparing {stock1} vs {stock2}")
    # Placeholder for graph comparison
    st.write("(Comparison Graph Coming Soon...)")

# Navigation Bar
menu = st.sidebar.radio("Navigation", ["Login", "Live News", "Stock Predictor", "Top Gainers & Losers", "Stock Comparison"])
if "logged_in" not in st.session_state:
    login()
else:
    if menu == "Live News":
        show_live_news()
    elif menu == "Stock Predictor":
        stock_predictor()
    elif menu == "Top Gainers & Losers":
        show_top_gainers_losers()
    elif menu == "Stock Comparison":
        stock_comparison()
