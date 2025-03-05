import streamlit as st
import requests
import pandas as pd
import plotly.express as px

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
            st.rerun()
        else:
            st.error("Invalid credentials. Try again.")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# Streamlit App Main Page
st.set_page_config(page_title="📊 Stock Market Prediction", layout="wide")

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

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, help="Click to log out"):
        st.session_state.logged_in = False
        st.rerun()

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

# Stock Predictor Section
if st.session_state.get("page") == "Stock Predictor":
    st.title("📈 Stock Predictor")
    company = st.selectbox("Select a Stock", list(companies.keys()))
    symbol = companies[company]
    stock_data = get_stock_data(symbol)
    
    if stock_data:
        df = pd.DataFrame.from_dict(stock_data, orient="index", dtype=float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.columns = ["Open", "High", "Low", "Close", "Volume"]
        
        st.metric(label="📈 Open Price", value=f"${df.iloc[0]['Open']:.2f}")
        st.metric(label="📈 Current Price", value=f"${df.iloc[-1]['Close']:.2f}")
        
        fig = px.line(df, x=df.index, y="Close", title=f"{company} Stock Price")
        st.plotly_chart(fig)
        
        st.button("📉 Sell", use_container_width=True)
        st.button("📈 Buy", use_container_width=True)

# Stock Comparison Section
if st.session_state.get("page") == "Stock Comparison":
    st.title("📊 Stock Comparison")
    col1, col2 = st.columns(2)
    
    with col1:
        company1 = st.selectbox("Select First Company", list(companies.keys()), key="company1")
        symbol1 = companies[company1]
    
    with col2:
        company2 = st.selectbox("Select Second Company", list(companies.keys()), key="company2")
        symbol2 = companies[company2]
    
    stock_data1 = get_stock_data(symbol1)
    stock_data2 = get_stock_data(symbol2)
    
    if stock_data1 and stock_data2:
        df1 = pd.DataFrame.from_dict(stock_data1, orient="index", dtype=float)
        df2 = pd.DataFrame.from_dict(stock_data2, orient="index", dtype=float)
        df1.index = pd.to_datetime(df1.index)
        df2.index = pd.to_datetime(df2.index)
        df1 = df1.sort_index()
        df2 = df2.sort_index()
        df1.columns = ["Open", "High", "Low", "Close", "Volume"]
        df2.columns = ["Open", "High", "Low", "Close", "Volume"]
        
        fig_comparison = px.line(title=f"{company1} vs {company2} Stock Price")
        fig_comparison.add_scatter(x=df1.index, y=df1["Close"], mode="lines", name=company1)
        fig_comparison.add_scatter(x=df2.index, y=df2["Close"], mode="lines", name=company2)
        
        st.plotly_chart(fig_comparison)
        st.metric(label=f"📊 {company1} Stock Price", value=f"${df1.iloc[-1]['Close']:.2f}")
        st.metric(label=f"📊 {company2} Stock Price", value=f"${df2.iloc[-1]['Close']:.2f}")
