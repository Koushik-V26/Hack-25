import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import smtplib
import os
import time

# Load API Key securely
API_KEY = os.getenv("LF2I00FT4XHT2WE3")  # Set this in your environment variables

# Email Notification Settings
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  # Sender email
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # App password
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")  # Receiver email

def send_email_notification(subject, message):
    """Send email notifications for stock alerts."""
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            email_message = f"Subject: {subject}\n\n{message}"
            server.sendmail(EMAIL_ADDRESS, RECEIVER_EMAIL, email_message)
    except Exception as e:
        st.error(f"⚠ Email notification failed: {e}")

# List of stock symbols
companies = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Google (GOOGL)": "GOOGL",
    "Amazon (AMZN)": "AMZN",
    "Tesla (TSLA)": "TSLA",
}

# Streamlit UI
st.set_page_config(page_title="📊 Live Stock Predictor", layout="wide")
st.title("📈 Live Stock Market Predictor")

selected_company = st.selectbox("Select a Company", list(companies.keys()))
symbol = companies[selected_company]

investment_amount = st.number_input("Enter Investment Amount ($)", min_value=10, max_value=10000, step=10)

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

            st.metric(label="📌 Open Price", value=f"${open_price:.2f}")
            st.metric(label="📌 Current Price", value=f"${current_price:.2f}")

            shares_to_buy = investment_amount / current_price
            st.info(f"📊 With ${investment_amount}, you can buy approximately {shares_to_buy:.2f} shares.")

            df["Minutes"] = np.arange(len(df))
            X = df["Minutes"].values.reshape(-1, 1)
            y = df["Close"].values.reshape(-1, 1)
            
            model = LinearRegression()
            model.fit(X, y)
            
            future_minutes = np.array(range(df["Minutes"].max() + 1, df["Minutes"].max() + 10)).reshape(-1, 1)
            predicted_prices = model.predict(future_minutes)
            
            predicted_high = max(predicted_prices)[0]
            predicted_low = min(predicted_prices)[0]

            profit_amount = (predicted_high - current_price) * shares_to_buy
            loss_amount = (predicted_low - current_price) * shares_to_buy

            # Send notification based on profit/loss
            if profit_amount > 0:
                st.success(f"✅ Potential Profit: ${profit_amount:.2f} if stock reaches predicted high of ${predicted_high:.2f}")
                send_email_notification("Stock Gain Alert!", f"Your selected stock {symbol} may reach ${predicted_high:.2f}, potential profit: ${profit_amount:.2f}.")
            else:
                st.info("⚖ Neutral trend detected. No significant profit expected.")

            if loss_amount < 0:
                st.error(f"⚠ Potential Loss: ${abs(loss_amount):.2f} if stock drops to predicted low of ${predicted_low:.2f}")
                send_email_notification("Stock Loss Alert!", f"Warning! {symbol} may drop to ${predicted_low:.2f}, potential loss: ${abs(loss_amount):.2f}.")
            
            # Live updating graph
            st.subheader("📊 Live Stock Price Movement")
            live_chart = st.line_chart(df["Close"])

            for _ in range(10):  # Simulate real-time updates
                time.sleep(2)
                stock_data = get_intraday_data(symbol)
                if stock_data:
                    df = pd.DataFrame.from_dict(stock_data, orient="index", dtype=float)
                    df.index = pd.to_datetime(df.index)
                    df = df.sort_index()
                    df.columns = ["Open", "High", "Low", "Close", "Volume"]
                    live_chart.line_chart(df["Close"])

        except Exception as e:
            st.error(f"⚠ An error occurred while processing data: {e}")
    else:
        st.error("⚠ Could not fetch stock data. API limit may have been reached or invalid API key.")
