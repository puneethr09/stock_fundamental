import pandas as pd
import numpy as np
import yfinance as yf
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import datetime


# Download required NLTK data
nltk.download("vader_lexicon")

# Define stock ticker symbols
stock_tickers = ["AAPL", "GOOG", "MSFT", "AMZN", "META"]  # Changed FB to META


# Define sentiment analysis function (You'll need to fetch news data here)
def sentiment_analysis(text_data):
    sia = SentimentIntensityAnalyzer()
    sentiments = []
    for text in text_data:
        sentiment = sia.polarity_scores(text)
        sentiments.append(sentiment)
    return sentiments


def technical_indicator(data):
    # Get all 'Adj Close' columns
    close_columns = data.loc[:, "Adj Close"].columns

    for ticker in close_columns:
        # Calculate moving averages
        data[("MA_50", ticker)] = data[("Adj Close", ticker)].rolling(50).mean()
        data[("MA_200", ticker)] = data[("Adj Close", ticker)].rolling(200).mean()

        # Calculate RSI
        delta = data[("Adj Close", ticker)].diff(1)
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        roll_up = up.rolling(window=14).mean()
        roll_down = down.rolling(window=14).mean().abs()
        RS = roll_up / roll_down
        RSI = 100.0 - (100.0 / (1.0 + RS))
        data[("RSI", ticker)] = RSI

    return data


# Define machine learning model function
def machine_learning_model(data):
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        data.drop("Target", axis=1), data["Target"], test_size=0.2, random_state=42
    )

    # Train random forest classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Make predictions
    predictions = model.predict(X_test)

    # Evaluate model performance
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions)
    matrix = confusion_matrix(y_test, predictions)

    return accuracy, report, matrix


def main():
    # Get today's date
    end_date = datetime.date.today().strftime("%Y-%m-%d")

    # Download data up to the latest date
    data = yf.download(tickers=stock_tickers, start="2020-01-01", end=end_date)

    # Calculate technical indicators
    data = technical_indicator(data)

    # Now calculate the target variable
    for ticker in data["Adj Close"].columns:
        data[("Target", ticker)] = np.where(
            data[("Adj Close", ticker)] > data[("MA_50", ticker)], 1, 0
        )

    # Create a DataFrame for all the data
    df = data.stack(level="Ticker", future_stack=True).reset_index()

    print(df.head())

    # Here you would add code to fetch news data and calculate sentiment
    # For now, we'll use dummy data
    df["Sentiment"] = np.random.random(len(df))

    # Prepare data for machine learning
    features = ["Adj Close", "MA_50", "MA_200", "RSI", "Sentiment"]
    X = df[features]
    y = df["Target"]

    # Run machine learning model
    accuracy, report, matrix = machine_learning_model(pd.concat([X, y], axis=1))

    print(f"Model Accuracy: {accuracy}")
    print("Classification Report:")
    print(report)
    print("Confusion Matrix:")
    print(matrix)


if __name__ == "__main__":
    main()
