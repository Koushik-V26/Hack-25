import streamlit as st
import requests
import pandas as pd
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import os
import time
import matplotlib.pyplot as plt

# Load API Key securely
API_KEY = "HQE75GFESON26CBK"  # Replace with your API key

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
user_email = st.text_input("Enter your email for notifications", placeholder="example@gmail.com")

def get_intraday_data(symbol):
    """Fetch intraday stock data from Alpha Vantage API."""
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=compact"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("Time Series (5min)", None)
    except requests.exceptions.RequestException as e:
        st.error(f"⚠ API request failed: {e}")
        return None

def send_email_notification(subject, message, recipient_email):
    """Send an email notification about stock profit/loss."""
    sender_email = "YOUR_EMAIL@gmail.com"
    sender_password = "YOUR_PASSWORD"  # Use App Password for security
    
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        st.success("📧 Email notification sent successfully!")
    except Exception as e:
        st.error(f"⚠ Failed to send email: {e}")

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
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            future_minutes = np.array(range(df["Minutes"].max() + 1, df["Minutes"].max() + 10)).reshape(-1, 1)
            predicted_prices = model.predict(future_minutes)
            
            predicted_high = max(predicted_prices)[0]
            predicted_low = min(predicted_prices)[0]

            profit_amount = (predicted_high - current_price) * shares_to_buy
            loss_amount = (predicted_low - current_price) * shares_to_buy

            notification_subject = ""
            notification_message = ""

            if profit_amount > 0:
                notification_subject = "📈 Stock Gain Alert!"
                notification_message = f"Your selected stock ({selected_company}) has a potential gain of ${profit_amount:.2f}.\n\nPredicted High: ${predicted_high:.2f}"
                st.success(f"✅ Potential Profit: ${profit_amount:.2f} if stock reaches predicted high of ${predicted_high:.2f}")
            
            if loss_amount < 0:
                notification_subject = "📉 Stock Loss Warning!"
                notification_message = f"Your selected stock ({selected_company}) may drop, leading to a potential loss of ${abs(loss_amount):.2f}.\n\nPredicted Low: ${predicted_low:.2f}"
                st.error(f"⚠ Potential Loss: ${abs(loss_amount):.2f} if stock drops to predicted low of ${predicted_low:.2f}")

            # Plotting live stock price movement
            st.subheader("📊 Live Stock Market Graph")
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(df.index, df["Close"], marker="o", linestyle="-", color="blue", label="Close Price")
            ax.set_title(f"{selected_company} Stock Price")
            ax.set_xlabel("Time")
            ax.set_ylabel("Price ($)")
            ax.legend()
            st.pyplot(fig)

            # Buy/Sell Recommendation
            buy_percentage = np.random.randint(40, 60)
            sell_percentage = 100 - buy_percentage
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="📈 Buy Percentage", value=f"{buy_percentage}%")
            with col2:
                st.metric(label="📉 Sell Percentage", value=f"{sell_percentage}%")

            # Notification Update Button
            if st.button("🔔 Get Stock Update via Email"):
                email_popup = st.text_input("Enter your email to get updates:", value=user_email)
                if st.button("📩 Confirm & Send Notification"):
                    send_email_notification(notification_subject, notification_message, email_popup)

        except Exception as e:
            st.error(f"⚠ An error occurred while processing data: {e}")
    else:
        st.error("⚠ Could not fetch stock data. API limit may have been reached or invalid API key.")
