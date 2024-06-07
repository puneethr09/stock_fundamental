import pandas as pd
import yfinance as yf
import os

# Function to select the file
def select_file():
    input_files = [
        "D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_200.csv",
        "D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_500.csv",
        "D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_50.csv",
        "D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_large_midcap_250.csv",
        "D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_midcap_100.csv",
        "D:\\repo\\stock_fundamental\\input\\Indian_stocks_nifty_smallcap_250.csv"
    ]

    # Sort input files by size (ascending order)
    input_files = sorted(input_files, key=os.path.getsize)

    print("Select the dataset:")
    for idx, file in enumerate(input_files, start=1):
        print(f"{idx}. {os.path.basename(file)}")
    print("7. All files")

    choice = input("Enter your choice: ")

    if choice == '7':
        return input_files
    else:
        try:
            choice = int(choice)
            if 1 <= choice <= 6:
                return [input_files[choice - 1]]
            else:
                raise ValueError
        except ValueError:
            print("Invalid choice")
            return select_file()

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

# Function to process a chunk of data
def process_chunk(df_chunk):
    financial_data = []
    for idx, row in df_chunk.iterrows():
        ticker = str(row['Ticker']).strip()
        company_name = row['Company Name']
        if ticker and ticker.lower() != "nan":  # Ensure ticker is not NaN
            data = fetch_stock_data(ticker + ".NS")
            if all(value is not None for value in data.values()):
                data["company_name"] = company_name
                data["sector"] = row['Industry']
                financial_data.append(data)
            else:
                print(f"Missing or incomplete data for {ticker}")
        else:
            print(f"Invalid ticker format for row {idx}: {ticker}")
    return pd.DataFrame(financial_data)

# Function to analyze the entire CSV file in chunks
def analyze_csv_in_chunks(csv_path, chunk_size=100):
    output_dir = "D:\\repo\\stock_fundamental\\output"
    os.makedirs(output_dir, exist_ok=True)
    
    financial_data = []
    for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
        chunk_df = process_chunk(chunk)
        financial_data.append(chunk_df)
    
    combined_df = pd.concat(financial_data, ignore_index=True)
    return combined_df

# Function to perform rating and save results
def rate_and_save_results(combined_df, csv_path):
    if combined_df.empty:
        print("No data to analyze.")
        return

    # Calculate industry averages
    industry_averages = combined_df.groupby('sector').agg({
        'pe_ratio': 'mean',
        'pb_ratio': 'mean',
        'eps': 'mean',
    }).rename(columns={
        'pe_ratio': 'industry_pe_ratio',
        'pb_ratio': 'industry_pb_ratio',
        'eps': 'industry_eps',
    }).reset_index()

    # Merge industry averages back into the main dataframe
    combined_df = combined_df.merge(industry_averages, on='sector')

    # Define weights for scoring
    weights = {
        "pe_ratio": -0.5,  # Negative weight for P/E ratio (lower is better)
        "pb_ratio": -0.5,  # Negative weight for P/B ratio (lower is better)
        "eps": 1.0,        # Positive weight for EPS (higher is better)
    }

    # Ensure the DataFrame contains the expected columns
    required_columns = ['pe_ratio', 'pb_ratio', 'eps']
    missing_columns = [col for col in required_columns if col not in combined_df.columns]

    if missing_columns:
        print(f"Missing columns in the DataFrame: {missing_columns}")
    else:
        # Calculate score for each stock
        combined_df['score'] = (
            combined_df['pe_ratio'] * weights['pe_ratio'] +
            combined_df['pb_ratio'] * weights['pb_ratio'] +
            combined_df['eps'] * weights['eps']
        )

        # Normalize score to a 0-100 rating within each sector
        combined_df['rating'] = combined_df.groupby('sector')['score'].transform(lambda x: (x - x.min()) / (x.max() - x.min()) * 100)

        # Sort stocks by rating within each sector and get top 10 for each sector
        top_stocks = combined_df.groupby('sector', group_keys=False).apply(lambda x: x.sort_values(by='rating', ascending=False).head(10)).reset_index(drop=True)

        # Create output filenames
        base_filename = os.path.splitext(os.path.basename(csv_path))[0]
        txt_output_path = os.path.join("D:\\repo\\stock_fundamental\\output", f"{base_filename}_analyzed.txt")
        csv_output_path = os.path.join("D:\\repo\\stock_fundamental\\output", f"{base_filename}_analyzed.csv")

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
            print(f"Data successfully saved to {csv_output_path} and {txt_output_path}")
        except PermissionError:
            print(f"Permission denied: {csv_output_path}. Please close the file if it's open and try again.")
            csv_output_path = os.path.join("D:\\repo\\stock_fundamental\\output", f"{base_filename}_analyzed_new.csv")
            top_stocks[['company_name', 'sector', 'ticker', 'market_price', 'eps', 'book_value', 'pe_ratio', 'pb_ratio', 'rating']].to_csv(csv_output_path, index=False)
            print(f"Saved to {csv_output_path} instead.")

# Main function to run the analysis
def main():
    csv_files = select_file()
    for csv_file in csv_files:
        print(f"Processing {csv_file}...")
        combined_df = analyze_csv_in_chunks(csv_file)
        rate_and_save_results(combined_df, csv_file)

if __name__ == "__main__":
    main()
