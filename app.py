import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
from plyer import notification  # For Desktop Notifications
import smtplib  # For Email Notifications

# Load API Key
API_KEY = "1SH0HBPJU2F96JMV"  # Replace with your Alpha Vantage API Key

# List of stock symbols
companies = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Google (GOOGL)": "GOOGL",
    "Amazon (AMZN)": "AMZN",
    "Tesla (TSLA)": "TSLA",
}

# Streamlit UI
st.set_page_config(page_title="📊 Stock Notification System", layout="wide")
st.title("📈 Stock Market Profit/Loss Alerts")

selected_company = st.selectbox("Select a Company", list(companies.keys()))
symbol = companies[selected_company]

investment_amount = st.number_input("Enter Investment Amount ($)", min_value=10, max_value=10000, step=10)

email = st.text_input("Enter Email for Alerts (Optional)")

# Function to fetch stock data
def get_stock_price(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=compact"
    time.sleep(12)  # Avoid API rate limits
    response = requests.get(url)
    data = response.json()

    if "Time Series (5min)" not in data:
        return None

    df = pd.DataFrame.from_dict(data["Time Series (5min)"], orient="index", dtype=float)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    
    return df

# Function to send desktop notification
def send_desktop_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )

# Function to send email notification
def send_email_notification(subject, message, receiver_email):
    sender_email = "your_email@gmail.com"  # Replace with your email
    sender_password = "your_password"  # Replace with your email password

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        email_message = f"Subject: {subject}\n\n{message}"
        server.sendmail(sender_email, receiver_email, email_message)
        server.quit()
    except Exception as e:
        st.error(f"⚠ Email notification failed: {e}")

if st.button("🔍 Start Tracking Stock"):
    df = get_stock_price(symbol)

    if df is not None:
        current_price = df.iloc[-1]["Close"]
        open_price = df.iloc[0]["Open"]
        
        st.metric(label="📌 Open Price", value=f"${open_price:.2f}")
        st.metric(label="📌 Current Price", value=f"${current_price:.2f}")
        
        shares_to_buy = investment_amount / current_price
        st.info(f"📊 You can buy approximately {shares_to_buy:.2f} shares.")

        profit_loss = (current_price - open_price) * shares_to_buy
        profit_loss_percentage = (current_price - open_price) / open_price * 100
        
        if profit_loss > 0:
            st.success(f"✅ Profit: ${profit_loss:.2f} (+{profit_loss_percentage:.2f}%)")
            send_desktop_notification("📈 Stock Profit Alert", f"You gained ${profit_loss:.2f} on {selected_company}!")
            if email:
                send_email_notification("📈 Stock Profit Alert", f"You gained ${profit_loss:.2f} on {selected_company}!", email)
        
        elif profit_loss < 0:
            st.error(f"⚠ Loss: ${profit_loss:.2f} ({profit_loss_percentage:.2f}%)")
            send_desktop_notification("📉 Stock Loss Alert", f"You lost ${abs(profit_loss):.2f} on {selected_company}!")
            if email:
                send_email_notification("📉 Stock Loss Alert", f"You lost ${abs(profit_loss):.2f} on {selected_company}!", email)

    else:
        st.error("⚠ Could not fetch stock data. API limit may have been reached.")
