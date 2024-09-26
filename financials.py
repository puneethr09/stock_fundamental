import yfinance as yf
import pandas as pd
from datetime import datetime
from difflib import get_close_matches
import os


pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)


def to_crores(value):
    return value / 10000000 if isinstance(value, (int, float)) else value


def format_crores(value):
    return f"₹{value:.2f} cr." if isinstance(value, (int, float)) else value


def trim_df(df):
    return df.map(lambda x: round(x, 2) if isinstance(x, (int, float)) else x)


def format_date(date):
    if isinstance(date, str):
        return datetime.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y")
    elif isinstance(date, pd.Timestamp):
        return date.strftime("%b %d, %Y")
    else:
        return str(date)


def calculate_advanced_ratios(income_stmt, balance_sheet, cash_flow):
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


import csv


def extract_financials(ticker):
    stock = yf.Ticker(ticker)
    company_name = stock.info.get("longName", "Unknown Company")

    # Create financials directory if it doesn't exist
    os.makedirs("financials", exist_ok=True)

    # Generate annual report
    annual_filename = os.path.join(
        "financials", generate_filename(company_name + "_annual")
    )
    generate_annual_report(stock, annual_filename)

    # Generate quarterly report
    quarterly_filename = os.path.join(
        "financials", generate_filename(company_name + "_quarterly")
    )
    generate_quarterly_report(stock, quarterly_filename)


def generate_annual_report(stock, filepath):
    # Existing code for annual report generation
    income_stmt = stock.financials.iloc[:, :3]
    balance_sheet = stock.balance_sheet.iloc[:, :3]
    cash_flow = stock.cashflow.iloc[:, :3]

    with open(filepath, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(
            [
                "FINANCIAL ANALYSIS FOR",
                stock.info.get("longName", "Unknown Company").upper(),
                stock.ticker.upper(),
            ]
        )
        writer.writerow([])
        # Write Income Statement with all column headers
        writer.writerow(["-" * 50])
        writer.writerow(["INCOME STATEMENT (LAST 3 YEARS)"])
        writer.writerow(["-" * 50])
        writer.writerow(["YEAR"] + list(income_stmt.columns))
        income_stmt_csv = income_stmt.map(to_crores).reset_index()
        writer.writerows(income_stmt_csv.values)
        writer.writerow([])

        # Write Balance Sheet with all column headers
        writer.writerow(["-" * 50])
        writer.writerow(["BALANCE SHEET (LAST 3 YEARS)"])
        writer.writerow(["-" * 50])
        writer.writerow(["YEAR"] + list(balance_sheet.columns))
        balance_sheet_csv = balance_sheet.map(to_crores).reset_index()
        writer.writerows(balance_sheet_csv.values)
        writer.writerow([])
        writer.writerow([])

        # Write Cash Flow Statement with all column headers
        writer.writerow(["-" * 50])
        writer.writerow(["CASH FLOW STATEMENT (LAST 3 YEARS)"])
        writer.writerow(["-" * 50])
        writer.writerow(["YEAR"] + list(cash_flow.columns))
        cash_flow_csv = cash_flow.map(to_crores).reset_index()
        writer.writerows(cash_flow_csv.values)
        writer.writerow([])
        writer.writerow([])
        # Write Key Insights with caps and underline
        writer.writerow(["-" * 20])
        writer.writerow(["KEY INSIGHTS"])
        writer.writerow(["-" * 20])
        advanced_ratios = calculate_advanced_ratios(
            income_stmt, balance_sheet, cash_flow
        )
        trends = analyze_trends(income_stmt, balance_sheet, cash_flow)

        for key, value in advanced_ratios.items():
            writer.writerow([key, value])

        for key, value in trends.items():
            writer.writerow([key, value])

    print(f"Enhanced financial analysis saved to {filepath}")


def generate_quarterly_report(stock, filepath):
    income_stmt = stock.quarterly_financials.iloc[:, :4]
    balance_sheet = stock.quarterly_balance_sheet.iloc[:, :4]
    cash_flow = stock.quarterly_cashflow.iloc[:, :4]

    with open(filepath, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(["QUARTERLY FINANCIAL ANALYSIS"])
        writer.writerow(["-" * 30])

        # Write Income Statement
        writer.writerow(["INCOME STATEMENT (LAST 4 QUARTERS)"])
        writer.writerow(["-" * 30])
        writer.writerow(
            ["Year"] + [f"<b>Q{i+1}</b>" for i in range(len(income_stmt.columns))]
        )
        income_stmt_csv = income_stmt.map(to_crores).reset_index()
        writer.writerows(income_stmt_csv.values)
        writer.writerow([])

        # Write Balance Sheet
        writer.writerow(["BALANCE SHEET (LAST 4 QUARTERS)"])
        writer.writerow(["-" * 30])
        writer.writerow(
            ["Year"] + [f"<b>Q{i+1}</b>" for i in range(len(balance_sheet.columns))]
        )
        balance_sheet_csv = balance_sheet.map(to_crores).reset_index()
        writer.writerows(balance_sheet_csv.values)
        writer.writerow([])

        # Write Cash Flow Statement
        writer.writerow(["CASH FLOW STATEMENT (LAST 4 QUARTERS)"])
        writer.writerow(["-" * 30])
        writer.writerow(
            ["Year"] + [f"<b>Q{i+1}</b>" for i in range(len(cash_flow.columns))]
        )
        cash_flow_csv = cash_flow.map(to_crores).reset_index()
        writer.writerows(cash_flow_csv.values)
        writer.writerow([])


def find_nearest_ticker(input_ticker):
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
    clean_name = "".join(c for c in company_name if c.isalnum() or c.isspace())
    filename = clean_name.replace(" ", "_").lower()
    return f"{filename}_financials.csv"


def main():
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


if __name__ == "__main__":
    main()
