import pandas as pd
import yfinance as yf
import os

# Function to select the file
def select_file():
    print("Select the dataset:")
    print("1. Indian_stocks_nifty_200.csv")
    print("2. Indian_stocks_nifty_500.csv")
    print("3. Indian_stocks_nifty_50.csv")
    print("4. Indian_stocks_nifty_large_midcap_250.csv")
    print("5. Indian_stocks_nifty_midcap_100.csv")
    print("6. Indian_stocks_nifty_smallcap_250.csv")
    print("7. All files")
    choice = input("Enter 1, 2, 3, 4, 5, 6, or 7: ")
    
    if choice == '1':
        return ["D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_200.csv"]
    elif choice == '2':
        return ["D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_500.csv"]
    elif choice == '3':
        return ["D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_50.csv"]
    elif choice == '4':
        return ["D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_large_midcap_250.csv"]
    elif choice == '5':
        return ["D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_midcap_100.csv"]
    elif choice == '6':
        return ["D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_smallcap_250.csv"]
    elif choice == '7':
        return [
            "D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_200.csv",
            "D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_500.csv",
            "D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_50.csv",
            "D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_large_midcap_250.csv",
            "D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_midcap_100.csv",
            "D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_smallcap_250.csv"
        ]
    else:
        print("Invalid choice")
        return select_file()

# Select the files
csv_paths = select_file()

# Create a common output directory
output_dir = "D:\\repo\\stock_fundamental\\output"
os.makedirs(output_dir, exist_ok=True)

def fetch_and_analyze(csv_path):
    # Read the CSV file
    df = pd.read_csv(csv_path)

    # Function to fetch financial data
    def fetch_stock_data(ticker):
        stock = yf.Ticker(ticker)
        info = stock.info

        # Fetch additional data if needed
        if 'regularMarketPrice' in info:
            market_price = info['regularMarketPrice']
        else:
            hist = stock.history(period="1d")
            if not hist.empty:
                market_price = hist['Close'].iloc[0]
            else:
                market_price = None

        eps = info.get('trailingEps', None)
        book_value = info.get('bookValue', None)
        pe_ratio = info.get('trailingPE', None)
        pb_ratio = info.get('priceToBook', None)

        return {
            "ticker": ticker,
            "market_price": market_price,
            "eps": eps,
            "book_value": book_value,
            "pe_ratio": pe_ratio,
            "pb_ratio": pb_ratio
        }

    # Fetch financial data for all tickers
    print(f"Analyzing stocks from {csv_path}...")
    financial_data = []
    for idx, row in df.iterrows():
        ticker = row['Ticker']
        company_name = row['Company Name']
        data = fetch_stock_data(ticker + ".NS")
        if data["market_price"] is not None and data["eps"] is not None and data["book_value"] is not None and data["pe_ratio"] is not None and data["pb_ratio"] is not None:
            data["company_name"] = company_name
            data["sector"] = row['Industry']
            financial_data.append(data)
        else:
            print(f"Missing or incomplete data for {ticker}")
    print(f"Analysis done for {csv_path}.")

    # Convert financial data to DataFrame
    financial_df = pd.DataFrame(financial_data)

    # Calculate industry averages
    industry_averages = financial_df.groupby('sector').agg({
        'pe_ratio': 'mean',
        'pb_ratio': 'mean',
        'eps': 'mean',
    }).rename(columns={
        'pe_ratio': 'industry_pe_ratio',
        'pb_ratio': 'industry_pb_ratio',
        'eps': 'industry_eps',
    }).reset_index()

    # Merge industry averages back into the main dataframe
    financial_df = financial_df.merge(industry_averages, on='sector')

    # Define weights for scoring
    weights = {
        "pe_ratio": -0.5,  # Negative weight for P/E ratio (lower is better)
        "pb_ratio": -0.5,  # Negative weight for P/B ratio (lower is better)
        "eps": 1.0,        # Positive weight for EPS (higher is better)
    }

    # Ensure the DataFrame contains the expected columns
    required_columns = ['pe_ratio', 'pb_ratio', 'eps']
    missing_columns = [col for col in required_columns if col not in financial_df.columns]

    if missing_columns:
        print(f"Missing columns in the DataFrame: {missing_columns}")
    else:
        # Calculate score for each stock
        financial_df['score'] = (
            financial_df['pe_ratio'] * weights['pe_ratio'] +
            financial_df['pb_ratio'] * weights['pb_ratio'] +
            financial_df['eps'] * weights['eps']
        )

        # Normalize score to a 0-100 rating within each sector
        financial_df['rating'] = financial_df.groupby('sector')['score'].transform(lambda x: (x - x.min()) / (x.max() - x.min()) * 100)

        # Sort stocks by rating within each sector and get top 10 for each sector
        top_stocks = financial_df.groupby('sector', group_keys=False).apply(lambda x: x.sort_values(by='rating', ascending=False).head(10)).reset_index(drop=True)

        # Create output filenames
        base_filename = os.path.splitext(os.path.basename(csv_path))[0]
        txt_output_path = os.path.join(output_dir, f"{base_filename}_analyzed.txt")
        csv_output_path = os.path.join(output_dir, f"{base_filename}_analyzed.csv")

        # Save the sorted data to a text file with descriptions
        with open(txt_output_path, "w") as file:
            file.write("Sorted Stocks Analysis\n")
            file.write("=======================\n\n")
            file.write("Scoring Weights:\n")
            file.write(f"P/E Ratio Weight: {weights['pe_ratio']} (Lower is better)\n")
            file.write(f"P/B Ratio Weight: {weights['pb_ratio']} (Lower is better)\n")
            file.write(f"EPS Weight: {weights['eps']} (Higher is better)\n\n")
            file.write("Top Stocks:\n")
            file.write("============\n")
            
            for idx, row in top_stocks.iterrows():
                file.write(f"Company: {row['company_name']} (Ticker: {row['ticker']})\n")
                file.write(f"Sector: {row['sector']}\n")
                file.write(f"Market Price: {row['market_price']}\n")
                file.write(f"EPS: {row['eps']}  |  Industry EPS: {row['industry_eps']}\n")
                file.write(f"Book Value: {row['book_value']}\n")
                file.write(f"P/E Ratio: {row['pe_ratio']}  |  Industry P/E: {row['industry_pe_ratio']}\n")
                file.write(f"P/B Ratio: {row['pb_ratio']}  |  Industry P/B: {row['industry_pb_ratio']}\n")
                file.write(f"Rating: {row['rating']:.2f}/100\n")
                file.write("\n")

        # Save the sorted data to a CSV file with values
        try:
            top_stocks[['company_name', 'sector', 'ticker', 'market_price', 'eps', 'book_value', 'pe_ratio', 'pb_ratio', 'rating']].to_csv(csv_output_path, index=False)
        except PermissionError:
            print(f"Permission denied: {csv_output_path}. Please close the file if it's open and try again.")
            csv_output_path = os.path.join(output_dir, f"{base_filename}_analyzed_new.csv")
            top_stocks[['company_name', 'sector', 'ticker', 'market_price', 'eps', 'book_value', 'pe_ratio', 'pb_ratio', 'rating']].to_csv(csv_output_path, index=False)
            print(f"Saved to {csv_output_path} instead.")

for path in csv_paths:
    fetch_and_analyze(path)
