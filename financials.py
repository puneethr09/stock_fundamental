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


def extract_financials(ticker):
    stock = yf.Ticker(ticker)
    company_name = stock.info.get("longName", "Unknown Company")

    os.makedirs("financials", exist_ok=True)

    filename = generate_filename(company_name)
    filepath = os.path.join("financials", filename)

    with open(filepath, "w") as f:
        f.write(f"Financial Analysis for {company_name} ({ticker})\n")
        f.write("=" * 50 + "\n\n")

        # Extract Income Statement
        income_stmt = stock.financials.iloc[:, :3]  # Last 3 years
        income_stmt.columns = income_stmt.columns.map(format_date)
        f.write("Income Statement (Last 3 Years):\n")
        f.write(trim_df(income_stmt.map(to_crores)).to_string() + "\n\n")

        # Extract Balance Sheet
        balance_sheet = stock.balance_sheet.iloc[:, :3]  # Last 3 years
        balance_sheet.columns = balance_sheet.columns.map(format_date)
        f.write("Balance Sheet (Last 3 Years):\n")
        f.write(trim_df(balance_sheet.map(to_crores)).to_string() + "\n\n")

        # Extract Cash Flow Statement
        cash_flow = stock.cashflow.iloc[:, :3]  # Last 3 years
        cash_flow.columns = cash_flow.columns.map(format_date)
        f.write("Cash Flow Statement (Last 3 Years):\n")
        f.write(trim_df(cash_flow.map(to_crores)).to_string() + "\n\n")

        f.write("Key Insights (Income Statement):\n")
        for year in income_stmt.columns:
            revenue = to_crores(
                income_stmt.loc["Total Revenue", year]
                if "Total Revenue" in income_stmt.index
                else None
            )
            net_income = to_crores(
                income_stmt.loc["Net Income", year]
                if "Net Income" in income_stmt.index
                else None
            )
            gross_profit = to_crores(
                income_stmt.loc["Gross Profit", year]
                if "Gross Profit" in income_stmt.index
                else None
            )

            f.write(f"\n{year}:\n")
            f.write(f"Revenue: {format_crores(revenue)}\n")
            f.write(f"Net Income: {format_crores(net_income)}\n")

            if revenue and gross_profit:
                gross_profit_margin = (gross_profit / revenue) * 100
                f.write(f"Gross Profit Margin: {gross_profit_margin:.2f}%\n")
            else:
                f.write("Gross Profit Margin: Not available\n")

        f.write("\nKey Insights (Balance Sheet):\n")
        for year in balance_sheet.columns:
            total_assets = to_crores(
                balance_sheet.loc["Total Assets", year]
                if "Total Assets" in balance_sheet.index
                else None
            )
            total_liabilities = to_crores(
                balance_sheet.loc["Total Liabilities Net Minority Interest", year]
                if "Total Liabilities Net Minority Interest" in balance_sheet.index
                else None
            )
            total_equity = to_crores(
                balance_sheet.loc["Total Stockholder Equity", year]
                if "Total Stockholder Equity" in balance_sheet.index
                else None
            )

            f.write(f"\n{year}:\n")
            f.write(f"Total Assets: {format_crores(total_assets)}\n")
            f.write(f"Total Liabilities: {format_crores(total_liabilities)}\n")

            if total_liabilities and total_equity and total_equity != 0:
                debt_to_equity = total_liabilities / total_equity
                f.write(f"Debt to Equity Ratio: {debt_to_equity:.2f}\n")
            else:
                f.write("Debt to Equity Ratio: Not available\n")

        f.write("\nKey Insights (Cash Flow):\n")
        for year in cash_flow.columns:
            operating_cash_flow = to_crores(
                cash_flow.loc["Operating Cash Flow", year]
                if "Operating Cash Flow" in cash_flow.index
                else None
            )
            capital_expenditures = to_crores(
                cash_flow.loc["Capital Expenditures", year]
                if "Capital Expenditures" in cash_flow.index
                else None
            )
            free_cash_flow = to_crores(
                cash_flow.loc["Free Cash Flow", year]
                if "Free Cash Flow" in cash_flow.index
                else None
            )

            f.write(f"\n{year}:\n")
            f.write(f"Operating Cash Flow: {format_crores(operating_cash_flow)}\n")
            f.write(f"Capital Expenditures: {format_crores(capital_expenditures)}\n")
            f.write(f"Free Cash Flow: {format_crores(free_cash_flow)}\n")

        advanced_ratios = calculate_advanced_ratios(income_stmt, balance_sheet, cash_flow)
        trends = analyze_trends(income_stmt, balance_sheet, cash_flow)
        insights = generate_insights(advanced_ratios, trends)

        f.write("\n\nDetailed Analysis and Insights:\n")
        f.write("=" * 30 + "\n")
        f.write(insights)

    print(f"Enhanced financial analysis saved to {filepath}")

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
    return f"{filename}_financials.txt"


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
