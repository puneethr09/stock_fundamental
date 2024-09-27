import yfinance as yf
import pandas as pd
from datetime import datetime
from difflib import get_close_matches
import os
import logging
import csv


pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)


def to_crores(value):
    """
    Converts a given value to crores.

    Args:
        value: The value to be converted. It can be an integer, float, or string.

    Returns:
        The converted value in crores. If the input value is NaN, returns "-" if it's a number or "N/A" if it's not. If the input value is not a number, returns the original value.
    """
    if pd.isna(value):
        return "-" if isinstance(value, (int, float)) else "N/A"
    if isinstance(value, (int, float)) or (isinstance(value, str)):
        try:
            float_value = float(value)
            if abs(float_value) < 1e-6:
                return 0
            return float_value / 10000000
        except ValueError:
            return value
    return value


def format_date(date):
    """
    Formats a given date into a human-readable string.

    Args:
        date: The date to be formatted. It can be a string in the format "%Y-%m-%d" or a pandas Timestamp object.

    Returns:
        A string representing the formatted date in the format "%b %d, %Y". If the input date is not a string or a pandas Timestamp object, returns its string representation.
    """
    if isinstance(date, str):
        return datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y")
    elif isinstance(date, pd.Timestamp):
        return date.strftime("%b %d, %Y")
    else:
        return str(date)


def calculate_advanced_ratios(income_stmt, balance_sheet, cash_flow):
    """
    Calculate advanced ratios based on income statement, balance sheet, and cash flow data.

    Args:
        income_stmt (pandas.DataFrame): Income statement data.
        balance_sheet (pandas.DataFrame): Balance sheet data.
        cash_flow (pandas.DataFrame): Cash flow data.

    Returns:
        dict: A dictionary containing the calculated ratios. The keys are the ratio names and the values are the calculated ratios.

    Raises:
        None

    Notes:
        - The function calculates the following ratios:
            - ROA (Return on Assets)
            - ROE (Return on Equity)
            - Current Ratio
            - Quick Ratio
            - Debt to Equity
        - The function uses the first column of each DataFrame as the index.
        - If any exception occurs during the calculation, the function catches the exception and continues without raising an error.

    """
    ratios = {}
    try:
        ratios["ROA"] = (
            income_stmt.loc["Net Income", income_stmt.columns[0]]
            / balance_sheet.loc["Total Assets", balance_sheet.columns[0]]
        )
        ratios["ROE"] = (
            income_stmt.loc["Net Income", income_stmt.columns[0]]
            / balance_sheet.loc["Total Stockholder Equity", balance_sheet.columns[0]]
        )
        ratios["Current Ratio"] = (
            balance_sheet.loc["Current Assets", balance_sheet.columns[0]]
            / balance_sheet.loc["Current Liabilities", balance_sheet.columns[0]]
        )
        ratios["Quick Ratio"] = (
            balance_sheet.loc["Current Assets", balance_sheet.columns[0]]
            - balance_sheet.loc["Inventory", balance_sheet.columns[0]]
        ) / balance_sheet.loc["Current Liabilities", balance_sheet.columns[0]]
        ratios["Debt to Equity"] = (
            balance_sheet.loc[
                "Total Liabilities Net Minority Interest", balance_sheet.columns[0]
            ]
            / balance_sheet.loc["Total Stockholder Equity", balance_sheet.columns[0]]
        )
    except:
        pass
    return ratios


def analyze_trends(income_stmt, balance_sheet, cash_flow):
    """
    Analyzes financial trends based on income statement, balance sheet, and cash flow data.

    Args:
        income_stmt (pandas.DataFrame): Income statement data.
        balance_sheet (pandas.DataFrame): Balance sheet data.
        cash_flow (pandas.DataFrame): Cash flow data.

    Returns:
        dict: A dictionary containing the calculated trends. The keys are the trend names and the values are the calculated trends.

    Notes:
        - The function calculates the following trends:
            - Revenue Growth
            - Net Income Growth
            - Operating Cash Flow Growth
        - The function uses the first and last columns of each DataFrame as the index and the most recent data respectively.
        - If any exception occurs during the calculation, the function catches the exception and continues without raising an error.
    """
    trends = {}
    try:
        trends["Revenue Growth"] = (
            income_stmt.loc["Total Revenue", income_stmt.columns[0]]
            / income_stmt.loc["Total Revenue", income_stmt.columns[-1]]
        ) - 1
        trends["Net Income Growth"] = (
            income_stmt.loc["Net Income", income_stmt.columns[0]]
            / income_stmt.loc["Net Income", income_stmt.columns[-1]]
        ) - 1
        trends["Operating Cash Flow Growth"] = (
            cash_flow.loc["Operating Cash Flow", cash_flow.columns[0]]
            / cash_flow.loc["Operating Cash Flow", cash_flow.columns[-1]]
        ) - 1
    except:
        pass
    return trends


def generate_insights(ratios, trends):
    """
    Generates financial insights based on the provided ratios and trends.

    Args:
        ratios (dict): A dictionary containing financial ratios.
        trends (dict): A dictionary containing financial trends.

    Returns:
        str: A string containing the generated financial insights.
    """
    insights = "Financial Analysis Insights:\n\n"

    if "ROA" in ratios:
        insights += f"Return on Assets (ROA): {ratios['ROA']:.2%}\n"
        insights += "This indicates how efficiently the company is using its assets to generate profit.\n\n"

    if "ROE" in ratios:
        insights += f"Return on Equity (ROE): {ratios['ROE']:.2%}\n"
        insights += "This shows how effectively the company is using shareholders' investments.\n\n"

    if "Current Ratio" in ratios:
        insights += f"Current Ratio: {ratios['Current Ratio']:.2f}\n"
        insights += (
            "This indicates the company's ability to pay short-term obligations.\n\n"
        )

    if "Revenue Growth" in trends:
        insights += f"Revenue Growth: {trends['Revenue Growth']:.2%}\n"
        insights += (
            "This shows the company's sales growth over the analyzed period.\n\n"
        )

    if "Net Income Growth" in trends:
        insights += f"Net Income Growth: {trends['Net Income Growth']:.2%}\n"
        insights += "This indicates the growth in the company's profitability.\n\n"

    return insights


def extract_financials(ticker):
    """
    Extracts financial data for a given stock ticker and generates annual and quarterly reports.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        None
    """
    stock = yf.Ticker(ticker)
    company_name = stock.info.get("longName", "Unknown Company")

    # Create financials directory if it doesn't exist
    os.makedirs("financials", exist_ok=True)

    # Create directoriy of company name seperate inside financials directory
    os.makedirs(os.path.join("financials", company_name), exist_ok=True)

    # Generate annual report inside the company directory
    annual_filename = os.path.join(
        "financials", company_name, generate_filename("annual")
    )
    generate_annual_report(stock, annual_filename)

    # Generate quarterly report
    quarterly_filename = os.path.join(
        "financials", company_name, generate_filename("quarterly")
    )
    generate_quarterly_report(stock, quarterly_filename)

    print(f"\nFinancial analysis for {company_name} is complete.")


def generate_annual_report(stock, filepath):
    """
    Generates an annual financial report for a given stock and saves it to a CSV file.

    Args:
        stock: A stock object containing financial data.
        filepath: The path to save the annual report CSV file.

    Returns:
        None
    """
    income_stmt = stock.financials.iloc[:, :3]
    balance_sheet = stock.balance_sheet.iloc[:, :3]
    cash_flow = stock.cashflow.iloc[:, :3]

    formatted_dates = [f"MARCH {date.year}" for date in income_stmt.columns]

    advanced_ratios = calculate_advanced_ratios(income_stmt, balance_sheet, cash_flow)
    trends = analyze_trends(income_stmt, balance_sheet, cash_flow)
    insights = generate_insights(advanced_ratios, trends)

    with open(filepath, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(["ANNUAL FINANCIAL ANALYSIS"] + [stock.info["longName"]])

        # Write Income Statement
        writer.writerow(["-" * 30])
        writer.writerow(["INCOME STATEMENT (LAST 3 YEARS)"] + ["all figures in Cr."])
        writer.writerow(["-" * 30])
        writer.writerow(["YEAR"] + [f"{date}" for date in formatted_dates])
        income_stmt_csv = income_stmt.map(to_crores).reset_index()
        writer.writerows(income_stmt_csv.values)
        writer.writerow([])

        # Write Balance Sheet
        writer.writerow(["-" * 30])
        writer.writerow(["BALANCE SHEET (LAST 3 YEARS)"] + ["all figures in Cr."])
        writer.writerow(["-" * 30])
        writer.writerow(["YEAR"] + [f"{date}" for date in formatted_dates])
        balance_sheet_csv = balance_sheet.map(to_crores).reset_index()
        writer.writerows(balance_sheet_csv.values)
        writer.writerow([])

        # Write Cash Flow Statement
        writer.writerow(["-" * 30])
        writer.writerow(["CASH FLOW STATEMENT (LAST 3 YEARS)"] + ["all figures in Cr."])
        writer.writerow(["-" * 30])
        writer.writerow(["YEAR"] + [f"{date}" for date in formatted_dates])
        cash_flow_csv = cash_flow.map(to_crores).reset_index()
        writer.writerows(cash_flow_csv.values)
        writer.writerow([])

        # Write Advanced Analysis
        writer.writerow(["-" * 30])
        writer.writerow(["ADVANCED FINANCIAL ANALYSIS"])
        writer.writerow(["-" * 30])

        writer.writerow(["Advanced Ratios"])
        for ratio, value in advanced_ratios.items():
            writer.writerow([ratio, value])
        writer.writerow([])

        writer.writerow(["Trends"])
        for trend, value in trends.items():
            writer.writerow([trend, value])
        writer.writerow([])

        writer.writerow(["Insights"])
        writer.writerow([insights])


def generate_quarterly_report(stock, filepath):
    """
    Generates a quarterly financial report for a given stock and saves it to a CSV file.

    Args:
        stock: A stock object containing quarterly financial data.
        filepath: The path to save the quarterly report CSV file.

    Returns:
        None
    """
    income_stmt = stock.quarterly_financials.iloc[:, :4]
    balance_sheet = stock.quarterly_balance_sheet.iloc[:, :4]
    cash_flow = stock.quarterly_cashflow.iloc[:, :4]

    advanced_ratios = calculate_advanced_ratios(income_stmt, balance_sheet, cash_flow)
    trends = analyze_trends(income_stmt, balance_sheet, cash_flow)
    insights = generate_insights(advanced_ratios, trends)

    with open(filepath, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(["QUARTERLY FINANCIAL ANALYSIS"] + [stock.info["longName"]])

        # Get the dates for each quarter
        quarter_dates = income_stmt.columns

        # Format the dates as month-year in caps
        formatted_dates = [date.strftime("%b %Y").upper() for date in quarter_dates]

        # Write Income Statement
        writer.writerow(["-" * 30])
        writer.writerow(["INCOME STATEMENT (LAST 4 QUARTERS)"] + ["all figures in Cr."])
        writer.writerow(["-" * 30])
        writer.writerow(["QUARTER"] + [f"{date}" for date in formatted_dates])
        income_stmt_csv = income_stmt.map(to_crores).reset_index()
        writer.writerows(income_stmt_csv.values)
        writer.writerow([])

        # Write Balance Sheet
        writer.writerow(["-" * 30])
        writer.writerow(["BALANCE SHEET (LAST 4 QUARTERS)"] + ["all figures in Cr."])
        writer.writerow(["-" * 30])
        writer.writerow(["QUARTER"] + [f"{date}" for date in formatted_dates])
        balance_sheet_csv = balance_sheet.map(to_crores).reset_index()
        writer.writerows(balance_sheet_csv.values)
        writer.writerow([])

        # Write Cash Flow Statement
        writer.writerow(["-" * 30])
        writer.writerow(
            ["CASH FLOW STATEMENT (LAST 4 QUARTERS)"] + ["all figures in Cr."]
        )
        writer.writerow(["-" * 30])
        writer.writerow(["QUARTER"] + [f"{date}" for date in formatted_dates])
        cash_flow_csv = cash_flow.map(to_crores).reset_index()
        writer.writerows(cash_flow_csv.values)
        writer.writerow([])

        # Write Advanced Analysis
        writer.writerow(["-" * 30])
        writer.writerow(["ADVANCED FINANCIAL ANALYSIS"])
        writer.writerow(["-" * 30])

        writer.writerow(["Advanced Ratios"])
        for ratio, value in advanced_ratios.items():
            writer.writerow([ratio, value])
        writer.writerow([])

        writer.writerow(["Trends"])
        for trend, value in trends.items():
            writer.writerow([trend, value])
        writer.writerow([])

        writer.writerow(["Insights"])
        writer.writerow([insights])
        writer.writerow([])


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


def generate_filename(company_name):
    """
    Generates a filename for a company's financial reports based on its name.

    Args:
        company_name (str): The name of the company.

    Returns:
        str: A filename in the format "{company_name}_reports.csv".
    """
    clean_name = "".join(c for c in company_name if c.isalnum() or c.isspace())
    filename = clean_name.replace(" ", "_").lower()
    return f"{filename}_reports.csv"


def select_input_file():
    """
    Selects a dataset from a list of available input files.

    Args:
        None

    Returns:
        list: A list of selected file paths or a single file path if only one file is selected.
    """
    input_files = [
        "/Users/puneeth/Documents/repo/stock_fundamental/input/Indian_stocks_nifty_200.csv",
        "/Users/puneeth/Documents/repo/stock_fundamental/input/Indian_stocks_nifty_500.csv",
        "/Users/puneeth/Documents/repo/stock_fundamental/input/Indian_stocks_nifty_50.csv",
        "/Users/puneeth/Documents/repo/stock_fundamental/input/Indian_stocks_nifty_large_midcap_250.csv",
        "/Users/puneeth/Documents/repo/stock_fundamental/input/Indian_stocks_nifty_midcap_100.csv",
        "/Users/puneeth/Documents/repo/stock_fundamental/input/Indian_stocks_nifty_smallcap_250.csv",
    ]

    print("Select the dataset:")
    for idx, file in enumerate(input_files, start=1):
        print(f"{idx}. {os.path.basename(file)}")
    print("7. All files")

    choice = input("Enter your choice (1-7): ")
    if choice == "7":
        return input_files
    else:
        return [input_files[int(choice) - 1]]


def extract_tickers(file_path):
    """
    Reads a CSV file at the given file path and extracts the values in the "Ticker" column.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list: A list of the values in the "Ticker" column.
    """
    df = pd.read_csv(file_path)
    return df["Ticker"].tolist()


def main():
    """
    The main function that serves as the entry point for the financial analysis application.

    It sets up logging, prompts the user to choose between analyzing a single company or multiple companies from input files,
    and then extracts financial data for the selected companies.

    Parameters:
        None

    Returns:
        None
    """
    # Set up logging
    log_file = "financials_log.txt"
    # Clean the file if it exists
    if os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("")
            print("Log file cleaned.")

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    print("Choose the type of analysis:")
    print("1. Analyze a single company (default)")
    print("2. Automated analysis from input files")

    choice = input("Enter your choice (press Enter for default): ")

    if choice == "" or choice == "1":
        ticker = input(
            "Enter the stock ticker symbol (e.g., reliance for Reliance Industries): "
        )
        ticker = ticker.upper() + ".NS"

        try:
            yf.Ticker(ticker).info
        except:
            nearest_ticker = find_nearest_ticker(ticker[:-3])
            if nearest_ticker:
                ticker = nearest_ticker + ".NS"
            else:
                print("No matching ticker found.")
                return

        extract_financials(ticker)

    elif choice == "2":
        selected_files = select_input_file()
        all_tickers = set()

        for file in selected_files:
            tickers = extract_tickers(file)
            all_tickers.update(tickers)

        logging.info("Generating reports for %d unique stocks...", len(all_tickers))
        for ticker in all_tickers:
            try:
                extract_financials(ticker + ".NS")
            except Exception as e:
                logging.error("Error processing %s: %s", ticker, str(e))

        print("All reports generated successfully.")

    else:
        print("Invalid choice. Defaulting to single company analysis.")
        main()


if __name__ == "__main__":
    main()
