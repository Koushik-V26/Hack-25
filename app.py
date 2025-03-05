import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import time

# Load API Key
API_KEY = "1SH0HBPJU2F96JMV"  # Replace with your actual Alpha Vantage API key

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

# Streamlit UI
st.set_page_config(page_title="📊 Live Stock Predictor", layout="wide")

st.title("📈 Live Stock Market Predictor")

selected_company = st.selectbox("Select a Company", list(companies.keys()))
symbol = companies[selected_company]

investment_amount = st.number_input("Enter Investment Amount ($)", min_value=10, max_value=10000, step=10)

# Function to fetch stock data with API rate limit handling
def get_intraday_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=compact"
    time.sleep(12)  # Prevent hitting API limit

    response = requests.get(url)
    data = response.json()

    if "Time Series (5min)" not in data:
        st.error("⚠ API Limit reached or unexpected response. Trying daily data...")
        return get_daily_data(symbol)

    return data["Time Series (5min)"]

# Alternative: Fetch daily data if intraday fails
def get_daily_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
    time.sleep(12)

    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        st.error("❌ API Error: Could not fetch stock data. Try again later.")
        return None

    return data["Time Series (Daily)"]

if st.button("🔍 Predict Stock Performance"):
    stock_data = get_intraday_data(symbol)
    if stock_data:
        try:
            df = pd.DataFrame.from_dict(stock_data, orient="index", dtype=float)
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df.columns = ["Open", "High", "Low", "Close", "Volume"]

            current_price = df.iloc[-1]["Close"]
            open_price = df.iloc[0]["Open"]
            
            st.metric(label="📌 Open Price", value=f"${open_price:.2f}")
            st.metric(label="📌 Current Price", value=f"${current_price:.2f}")
            
            shares_to_buy = investment_amount / current_price
            st.info(f"📊 With ${investment_amount}, you can buy approximately {shares_to_buy:.2f} shares.")

            df["Minutes"] = np.arange(len(df))
            X = df["Minutes"].values.reshape(-1, 1)
            y = df["Close"].values.reshape(-1, 1)
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            future_minutes = np.array(range(df["Minutes"].max() + 1, df["Minutes"].max() + 10)).reshape(-1, 1)
            predicted_prices = model.predict(future_minutes)
            
            future_df = pd.DataFrame({"Minutes": future_minutes.flatten(), "Predicted Price": predicted_prices.flatten()})
            future_df["Time"] = pd.date_range(start=df.index.max(), periods=len(future_df), freq="5min")

            predicted_high = max(predicted_prices)[0]
            predicted_low = min(predicted_prices)[0]

            profit_amount = (predicted_high - current_price) * shares_to_buy
            loss_amount = (predicted_low - current_price) * shares_to_buy

            if profit_amount > 0:
                st.success(f"✅ Potential Profit: ${profit_amount:.2f} if stock reaches predicted high of ${predicted_high:.2f}")

            if loss_amount < 0:
                st.error(f"⚠ Potential Loss: ${abs(loss_amount):.2f} if stock drops to predicted low of ${predicted_low:.2f}")
            
            best_sell_time = future_df.loc[future_df["Predicted Price"].idxmax(), "Time"]
            worst_sell_time = future_df.loc[future_df["Predicted Price"].idxmin(), "Time"]
            
            st.write(f"🕒 Best Time to Sell: {best_sell_time.strftime('%H:%M %p')}")
            st.write(f"⏳ Risky Time to Hold: {worst_sell_time.strftime('%H:%M %p')}")

            # Live updating graph
            st.subheader("📊 Live Stock Price Movement")
            live_chart = st.line_chart(df["Close"])

        except Exception as e:
            st.error(f"⚠ An error occurred while processing data: {e}")
    else:
        st.error("⚠ Could not fetch stock data. API limit may have been reached or invalid API key.")
