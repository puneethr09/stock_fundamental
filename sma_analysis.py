import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np
import pandas as pd
from difflib import get_close_matches
import os


def find_nearest_ticker(input_ticker):
    """
    Finds the nearest matching Indian stock ticker to the input ticker.

    Args:
        input_ticker (str): The ticker symbol to search for.

    Returns:
        str: The nearest matching ticker symbol, or None if no match is found.
    """
    # List of Indian stock tickers (you may need to update this list)
    indian_tickers = yf.Ticker("^NSEI").info["components"]

    # Find close matches
    matches = get_close_matches(input_ticker.upper(), indian_tickers, n=3, cutoff=0.6)

    if matches:
        print("Ticker not found. Did you mean one of these?")
        for i, match in enumerate(matches, 1):
            company_name = yf.Ticker(match).info.get("longName", "Unknown Company")
            print(f"{i}. {match} ({company_name})")

        choice = input("Enter the number of your choice (or press Enter to exit): ")
        if choice.isdigit() and 1 <= int(choice) <= len(matches):
            return matches[int(choice) - 1]

    return None


def fetch_stock_data(ticker, period):
    try:
        ticker = ticker.upper() + ".NS"
        yf.Ticker(ticker).info
        df = yf.download(ticker, period=period)
        if df.empty:
            nearest_ticker = find_nearest_ticker(ticker)
            print(
                f"No data found for {ticker}. Trying nearest ticker: {nearest_ticker}"
            )
            df = yf.download(nearest_ticker, period=period)
            print("Fetched data for", nearest_ticker)
            if df.empty:
                raise ValueError(
                    f"No data found for {nearest_ticker} for period {period}"
                )
        return df
    except ValueError as ve:
        print(ve)
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()


def generate_signals(df, short_window, long_window):
    df["Short_Moving_Avg"] = (
        df["Close"].rolling(window=short_window, min_periods=1).mean()
    )
    df["Long_Moving_Avg"] = (
        df["Close"].rolling(window=long_window, min_periods=1).mean()
    )

    # Initialize the 'Signal' column with zeros
    df["Signal"] = 0.0

    # Use .loc to avoid SettingWithCopyWarning and ensure correct assignment
    df.loc[df.index[short_window:], "Signal"] = np.where(
        df["Short_Moving_Avg"].iloc[short_window:]
        > df["Long_Moving_Avg"].iloc[short_window:],
        1.0,
        0.0,
    )

    return df


def plot_data(df, ticker, period_name):
    plt.figure(figsize=(14, 7))
    plt.plot(df["Close"], label=f"{ticker} Close Price")
    plt.plot(df["Short_Moving_Avg"], label="Short-term SMA")
    plt.plot(df["Long_Moving_Avg"], label="Long-term SMA")
    plt.title(f"{ticker} Stock Price and Moving Averages ({period_name})")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()

    ticker = ticker.upper() + ".NS"
    stock = yf.Ticker(ticker)
    company_name = stock.info.get("longName", "Unknown Company")

    # Create directory if it doesn't exist
    directory = f"charts/{company_name}"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Save the plot as a PNG file
    plt.savefig(f"{directory}/{period_name}.png")
    plt.close()


def main():
    ticker = input(
        "Enter the stock ticker symbol (e.g., reliance for Reliance Industries): "
    )
    short_window = 20
    long_window = 50

    periods = {"last_5_days": "5d", "last_month": "1mo", "last_3_months": "3mo", "year_to_date": "ytd"}

    for period_name, period in periods.items():
        print(f"Fetching data for {period_name}...")
        df = fetch_stock_data(ticker, period)

        if df.empty:
            print(f"No data found for {ticker} for {period_name}")
            continue

        try:
            df = generate_signals(df, short_window, long_window)
        except Exception as e:
            print(f"Error generating signals for {period_name}: {e}")
            continue

        try:
            plot_data(df, ticker, period_name)
        except Exception as e:
            print(f"Error plotting data for {period_name}: {e}")


if __name__ == "__main__":
    main()
