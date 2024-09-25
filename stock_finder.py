import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sentiment import sentiment_analysis
from tabulate import tabulate

def predict_prices(data, days_to_predict=20):
    X = np.array(range(len(data))).reshape(-1, 1)
    y = data.values

    model = LinearRegression()
    model.fit(X, y)

    last_date = data.index[-1]
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_to_predict)
    future_X = np.array(range(len(data), len(data) + days_to_predict)).reshape(-1, 1)

    future_prices = model.predict(future_X)
    return pd.Series(future_prices, index=future_dates)

def get_top_indian_stocks():
    # Manually defined list of Nifty 50 stocks (as of 2023)
    nifty50_components = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
        "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
        "LT.NS", "HCLTECH.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS",
        "BAJFINANCE.NS", "SUNPHARMA.NS", "TITAN.NS", "WIPRO.NS", "NESTLEIND.NS",
        "ULTRACEMCO.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "ADANIENT.NS",
        "JSWSTEEL.NS", "TATAMOTORS.NS", "BAJAJFINSV.NS", "M&M.NS", "TECHM.NS",
        "COALINDIA.NS", "HINDALCO.NS", "ADANIPORTS.NS", "GRASIM.NS", "HDFCLIFE.NS",
        "TATASTEEL.NS", "SBILIFE.NS", "INDUSINDBK.NS", "BRITANNIA.NS", "CIPLA.NS",
        "DRREDDY.NS", "EICHERMOT.NS", "APOLLOHOSP.NS", "DIVISLAB.NS", "BAJAJ-AUTO.NS",
        "UPL.NS", "HEROMOTOCO.NS", "BPCL.NS", "TATACONSUM.NS", "LTIM.NS"
    ]

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    data = yf.download(nifty50_components, start=start_date, end=end_date)['Adj Close']
    returns = data.pct_change().iloc[-1].sort_values(ascending=False)

    top_10 = returns.head(50)

    result = pd.DataFrame({
        'Stock': top_10.index,
        'Current Price': data.iloc[-1][top_10.index].round(2),
        'Previous Price': data.iloc[0][top_10.index].round(2)
    })

    result['Yearly Return (%)'] = ((result['Current Price'] / result['Previous Price'] - 1) * 100).round(2)
    result = result.sort_values('Yearly Return (%)', ascending=False)
    result = result.reset_index(drop=True)
    # Predict future prices and analyze sentiment
    for stock in result['Stock']:
        future_prices = predict_prices(data[stock])
        result.loc[result['Stock'] == stock, 'Predicted Price (30 days)'] = future_prices.iloc[-1].round(2)

        # Use dummy text data for sentiment analysis
        dummy_text_data = [f"News about {stock}" for _ in range(5)]
        sentiment_scores = sentiment_analysis(dummy_text_data)
        avg_sentiment = sum(score['compound'] for score in sentiment_scores) / len(sentiment_scores)
        result.loc[result['Stock'] == stock, 'Sentiment Score'] = round(avg_sentiment, 2)

    result = result[['Stock', 'Yearly Return (%)', 'Current Price', 'Previous Price', 'Predicted Price (30 days)', 'Sentiment Score']]
    return result

if __name__ == "__main__":
    top_stocks = get_top_indian_stocks()
    print("Top 10 performing Indian stocks with analysis:")
    print(tabulate(top_stocks, headers='keys', tablefmt='pretty', floatfmt='.2f'))
    
    print("\nStock Names, Current Prices, and Predicted Prices:")
    price_comparison = top_stocks[['Stock', 'Current Price', 'Predicted Price (30 days)']].set_index('Stock')
    print(tabulate(price_comparison, headers='keys', tablefmt='pretty', floatfmt='.2f'))
    print(top_stocks)