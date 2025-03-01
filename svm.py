import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression  # Linear and Logistic regression
from sklearn.svm import SVR  # Support Vector Regression

# Fetching data from the API
url = "https://disease.sh/v3/covid-19/countries/uk"
r = requests.get(url)
data = r.json()

# Extract relevant fields
covid_data = {
    "cases": data["cases"],
    "todayCases": data["todayCases"],
    "deaths": data["deaths"],
    "todayDeaths": data["todayDeaths"],
    "recovered": data["recovered"],
    "active": data["active"],
    "critical": data["critical"],
    "casesPerMillion": data["casesPerOneMillion"],
    "deathsPerMillion": data["deathsPerOneMillion"],
}

# Convert to Pandas DataFrame
df = pd.DataFrame([covid_data])
print(df)

# Plotting bar chart
labels = ["Total Cases", "Active Cases", "Recovered", "Deaths"]
values = [data["cases"], data["active"], data["recovered"], data["deaths"]]

plt.figure(figsize=(8,5))
plt.bar(labels, values, color=['blue', 'orange', 'green', 'red'])
plt.xlabel("Category")
plt.ylabel("Count")
plt.title("COVID-19 Data for UK")  # Updated to reflect UK
plt.show()

# Generate random historical data for demonstration purposes
np.random.seed(42)
historical_cases = np.random.randint(30000, 70000, size=30)  # Last 30 days cases
historical_deaths = np.random.randint(500, 2000, size=30)

df_historical = pd.DataFrame({"cases": historical_cases, "deaths": historical_deaths})
df_historical["day"] = range(1, 31)

print(df_historical.head())

# Prepare data for training
X = df_historical[["day"]]  # Day number as feature
y = df_historical["cases"]  # Cases as target variable

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 1. Linear Regression Model
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)

# 2. Logistic Regression Model (using it for regression purposes, not classification)
logistic_model = LogisticRegression()
logistic_model.fit(X_train, y_train)

# 3. Support Vector Machine (SVM) Model
svm_model = SVR(kernel='rbf')  # 'rbf' is a popular choice for SVM regression
svm_model.fit(X_train, y_train)

# Predict for the next 30 days using all three models
days = np.array([[i] for i in range(1, 31)])  # Days 1 to 30

predicted_cases_linear = linear_model.predict(days)
predicted_cases_logistic = logistic_model.predict(days)
predicted_cases_svm = svm_model.predict(days)

# Plotting the predictions of all three models
plt.figure(figsize=(10,6))

# Plot Linear Regression
plt.plot(days, predicted_cases_linear, label="Linear Regression", color="blue", marker='o')

# Plot Logistic Regression
plt.plot(days, predicted_cases_logistic, label="Logistic Regression", color="green", marker='s')

# Plot SVM
plt.plot(days, predicted_cases_svm, label="SVM", color="red", marker='^')

plt.title("Predicted COVID-19 Cases for the Next 30 Days (UK)")
plt.xlabel("Day")
plt.ylabel("Predicted Cases")
plt.legend()
plt.grid(True)
plt.show()

# Streamlit app
st.title("COVID-19 Cases Prediction in UK")
st.write("Predicting COVID-19 cases for the next day based on historical data.")

# User Input for Day Prediction
day_input = st.number_input("Enter day number (e.g., 31 for prediction)", min_value=1, max_value=100)

if st.button("Predict"):
    prediction_linear = linear_model.predict([[day_input]])
    prediction_logistic = logistic_model.predict([[day_input]])
    prediction_svm = svm_model.predict([[day_input]])

    st.write(f"Predicted cases for day {day_input} using Linear Regression: {int(prediction_linear[0])}")
    st.write(f"Predicted cases for day {day_input} using Logistic Regression: {int(prediction_logistic[0])}")
    st.write(f"Predicted cases for day {day_input} using SVM: {int(prediction_svm[0])}")

    # Plot the predictions for the user input day
    st.subheader("Prediction for the Next 30 Days")
    
    # Plot the predictions for Linear, Logistic, and SVM
    plt.figure(figsize=(10,6))

    plt.plot(days, predicted_cases_linear, label="Linear Regression", color="blue", marker='o')
    plt.plot(days, predicted_cases_logistic, label="Logistic Regression", color="green", marker='s')
    plt.plot(days, predicted_cases_svm, label="SVM", color="red", marker='^')

    st.pyplot(plt)
