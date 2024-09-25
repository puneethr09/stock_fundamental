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
stock_tickers = ["RELIANCE.NS"]


# Define sentiment analysis function (You'll need to fetch news data here)
def sentiment_analysis(text_data):
    """
    Analyzes the sentiment of a given list of text data.

    Parameters:
        text_data (list): A list of text strings to be analyzed.

    Returns:
        list: A list of dictionaries containing the sentiment scores for each text.
    """
    sia = SentimentIntensityAnalyzer()
    sentiments = []
    for text in text_data:
        sentiment = sia.polarity_scores(text)
        sentiments.append(sentiment)
    return sentiments


def technical_indicator(data):
    """
    Calculates technical indicators for a given stock data.

    Parameters:
        data (pandas DataFrame): A DataFrame containing stock data with 'Adj Close' column.

    Returns:
        pandas DataFrame: The input DataFrame with additional columns for 50-day and 200-day moving averages, and Relative Strength Index (RSI).
    """
    # For single stock case
    close_col = "Adj Close"

    # Calculate moving averages
    data["MA_50"] = data[close_col].rolling(50).mean()
    data["MA_200"] = data[close_col].rolling(200).mean()

    # Calculate RSI
    delta = data[close_col].diff(1)
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    roll_up = up.rolling(window=14).mean()
    roll_down = down.rolling(window=14).mean().abs()
    RS = roll_up / roll_down
    RSI = 100.0 - (100.0 / (1.0 + RS))
    data["RSI"] = RSI

    return data


# Define machine learning model function
def machine_learning_model(data):
    """
    Trains a random forest classifier on the given data and evaluates its performance.

    Parameters:
        data (pandas.DataFrame): The input data containing features and target variable.

    Returns:
        tuple: A tuple containing the accuracy score, classification report, and confusion matrix.
    """
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


def predict_future(model, latest_data, days=30):
    future_data = latest_data.copy()
    predictions = []
    future_sentiments = []
    for i in range(days):
        # Update technical indicators
        future_data = technical_indicator(future_data)
        # Generate new sentiment score
        new_sentiment = np.random.random()
        future_sentiments.append(new_sentiment)
        # Prepare features
        features = ["Adj Close", "MA_50", "MA_200", "RSI", "Sentiment"]
        X = future_data[features].iloc[-1:]
        X["Sentiment"] = new_sentiment
        # Make prediction
        pred = model.predict(X)[0]
        predictions.append(pred)
        # Update data for next prediction
        new_row = future_data.iloc[-1].copy()
        new_row.name = future_data.index[-1] + i + 1
        new_row["Adj Close"] *= 1 + np.random.normal(0, 0.01)  # Random price change
        new_row["Sentiment"] = new_sentiment
        future_data = pd.concat([future_data, pd.DataFrame([new_row])])
    return predictions, future_sentiments


def main():
    # Get today's date
    end_date = datetime.date.today().strftime("%Y-%m-%d")

    # Download data up to the latest date
    data = yf.download(tickers=stock_tickers, start="2022-01-01", end=end_date)

    # Calculate technical indicators
    data = technical_indicator(data)

    # Now calculate the target variable
    data["Target"] = np.where(data["Adj Close"] > data["MA_50"], 1, 0)

    # For single stock, we don't need to stack
    df = data.reset_index()

    # Add a 'Ticker' column with the stock symbol
    df["Ticker"] = stock_tickers[0]

    print(df)

    # Here you would add code to fetch news data and calculate sentiment
    # For now, we'll use dummy data
    df["Sentiment"] = np.random.random(len(df))

    # Print sentiment scores
    print("\nSample of Sentiment Scores:")
    print(df[["Date", "Adj Close", "Sentiment"]].head(10))
    print("\n")

    # Train the model on all data
    features = ["Adj Close", "MA_50", "MA_200", "RSI", "Sentiment"]
    X = df[features]
    y = df["Target"]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Predict future values
    future_predictions, future_sentiments = predict_future(model, df)

    print("Future predictions (1: above 50-day MA, 0: below):")
    for i, (pred, sentiment) in enumerate(zip(future_predictions, future_sentiments)):
        print(
            f"Day {i+1}: {'Above' if pred == 1 else 'Below'} 50-day MA, Sentiment: {sentiment:.2f}"
        )


if __name__ == "__main__":
    main()
