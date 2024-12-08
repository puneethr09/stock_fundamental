import yfinance as yf
import pandas as pd

import matplotlib

matplotlib.use("Agg")  # Use a non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime


def get_financial_ratios(ticker):
    stock = yf.Ticker(ticker)
    company_name = stock.info.get("longName", "Unknown Company")

    # Get historical data for the maximum available period
    historical_data = stock.history(period="max")  # Use "max" to get all available data
    if historical_data.empty:
        print(f"No historical data available for {ticker}.")
        return None

    # Check if the index is timezone-naive and localize if necessary
    if historical_data.index.tz is not None:
        historical_data.index = historical_data.index.tz_localize(None)

    # Check how many years of data are available
    available_years = historical_data.index.year.unique()
    num_years = len(available_years)

    if num_years < 1:
        print(f"No historical data available for {ticker}.")
        return None  # Or handle as needed

    # Proceed with data retrieval and calculations
    balance_sheet = stock.balance_sheet / 1000000  # Convert to millions
    cash_flow = stock.cashflow / 1000000  # Convert to millions
    income_stmt = stock.financials / 1000000  # Convert to millions

    # Convert to numeric, coercing errors to NaN
    balance_sheet = balance_sheet.apply(pd.to_numeric, errors="coerce")
    cash_flow = cash_flow.apply(pd.to_numeric, errors="coerce")
    income_stmt = income_stmt.apply(pd.to_numeric, errors="coerce")

    # Calculate financial ratios
    try:
        roe = (
            income_stmt.loc["Net Income", income_stmt.columns]
            / balance_sheet.loc["Common Stock Equity", balance_sheet.columns]
        )
    except:
        # Handle the case where the calculation fails roe should be NaN for all  years
        roe = pd.Series(np.nan, index=income_stmt.columns)

    try:
        roa = (
            income_stmt.loc["Net Income", income_stmt.columns]
            / balance_sheet.loc["Total Assets", balance_sheet.columns]
        )
    except:
        # Handle the case where the calculation fails roa should be NaN for all  years
        roa = pd.Series(np.nan, index=income_stmt.columns)

    try:
        roic = (
            cash_flow.loc["Operating Cash Flow", cash_flow.columns]
            / income_stmt.loc["Total Revenue", income_stmt.columns]
        )
    except:
        # Handle the case where the calculation fails roic should be NaN for all  years
        roic = pd.Series(np.nan, index=cash_flow.columns)

    try:
        quick_ratio = (
            balance_sheet.loc["Current Assets", balance_sheet.columns]
            - (
                balance_sheet.loc["Inventory", balance_sheet.columns]
                if "Inventory" in balance_sheet.index
                else pd.Series(0, index=balance_sheet.columns)
            )
            - balance_sheet.loc["Prepaid Assets", balance_sheet.columns]
        ) / balance_sheet.loc["Current Liabilities", balance_sheet.columns]
    except:
        # Handle the case where the calculation fails quick_ratio should be NaN for all  years
        quick_ratio = pd.Series(np.nan, index=balance_sheet.columns)

    try:
        current_ratio = (
            balance_sheet.loc["Current Assets", balance_sheet.columns]
            / balance_sheet.loc["Current Liabilities", balance_sheet.columns]
        )
    except:
        # Handle the case where the calculation fails current_ratio should be NaN for all  years
        current_ratio = pd.Series(np.nan, index=balance_sheet.columns)

    try:
        debt_to_equity = (
            balance_sheet.loc["Total Debt", balance_sheet.columns]
            / balance_sheet.loc["Common Stock Equity", balance_sheet.columns]
        )
    except:
        # Handle the case where the calculation fails debt_to_equity should be NaN for all  years
        debt_to_equity = pd.Series(np.nan, index=balance_sheet.columns)

    try:
        eps = (
            income_stmt.loc["Diluted EPS", income_stmt.columns] * 1000000
        )  # Convert to millions
        eps.index = eps.index.tz_localize(None)  # Make EPS index timezone-naive
    except:
        # Handle the case where the calculation fails eps should be NaN for all  years
        eps = pd.Series(np.nan, index=income_stmt.columns)

    try:
        pe_ratios = (
            historical_data["Close"].reindex(eps.index) / eps
        )  # Calculate P/E for each year
    except:
        # Handle the case where the calculation fails pe_ratios should be NaN for all  years
        pe_ratios = pd.Series(np.nan, index=eps.index)

    # Earnings Before Interest and Taxes (EBIT)
    try:
        ebit = (
            income_stmt.loc["Total Revenue", income_stmt.columns]
            - income_stmt.loc["Operating Expense", income_stmt.columns]
        )
    except:
        # Handle the case where the calculation fails ebit should be NaN for all  years
        ebit = pd.Series(np.nan, index=income_stmt.columns)

    # EBIT Margin
    try:
        ebit_margin = (
            ebit / income_stmt.loc["Total Revenue", income_stmt.columns]
        ) * 100
    except:
        # Handle the case where the calculation fails ebit_margin should be NaN for all  years
        ebit_margin = pd.Series(np.nan, index=income_stmt.columns)

    # Return on Investment (ROI)
    try:
        roi = (
            income_stmt.loc["Net Income", income_stmt.columns]
            / balance_sheet.loc["Total Assets", balance_sheet.columns]
        ) * 100
    except:
        # Handle the case where the calculation fails roi should be NaN for all  years
        roi = pd.Series(np.nan, index=income_stmt.columns)

    # Set the index to be the years
    roe.index = pd.to_datetime(roe.index, format="%Y-%m-%d").year
    roa.index = pd.to_datetime(roa.index, format="%Y-%m-%d").year
    roic.index = pd.to_datetime(roic.index, format="%Y-%m-%d").year
    quick_ratio.index = pd.to_datetime(quick_ratio.index, format="%Y-%m-%d").year
    current_ratio.index = pd.to_datetime(current_ratio.index, format="%Y-%m-%d").year
    debt_to_equity.index = pd.to_datetime(debt_to_equity.index, format="%Y-%m-%d").year
    pe_ratios.index = pd.to_datetime(pe_ratios.index, format="%Y-%m-%d").year
    ebit_margin.index = pd.to_datetime(ebit_margin.index, format="%Y-%m-%d").year
    roi.index = pd.to_datetime(roi.index, format="%Y-%m-%d").year

    # Change to percentages
    roe = roe * 100
    roa = roa * 100
    roic = roic * 100

    # Create a DataFrame to store the financial ratios
    ratios_df = pd.DataFrame(
        {
            "Year": available_years,
            "ROE": roe.reindex(available_years).values,
            "ROA": roa.reindex(available_years).values,
            "ROIC": roic.reindex(available_years).values,
            "Quick Ratio": quick_ratio.reindex(available_years).values,
            "Current Ratio": current_ratio.reindex(available_years).values,
            "Debt to Equity": debt_to_equity.reindex(available_years).values,
            "P/E Ratio": pe_ratios.reindex(available_years).values,
            "EBIT Margin": ebit_margin.reindex(available_years).values,
            "ROI": roi.reindex(available_years).values,
            "Company": [company_name] * len(available_years),
        }
    )
    # Drop years with all NaN values
    ratios_df = ratios_df.dropna(
        how="all", subset=ratios_df.columns[1:-1]
    )  # Exclude 'Year' and 'Company' columns

    return ratios_df


def normalize_data(ratios_df):
    normalized_df = ratios_df.copy()
    for column in normalized_df.columns[1:-1]:  # Skip 'Year' and 'Company'
        mean_val = normalized_df[column].mean()
        std_dev = normalized_df[column].std()
        normalized_df[column] = (normalized_df[column] - mean_val) / std_dev
    return normalized_df


import os


def analyze_ratios(ratios_df):
    if ratios_df is None or len(ratios_df) == 0:
        print("No financial ratios available for analysis.")
        return [], []

    company_name = ratios_df["Company"].unique()[0]
    warnings = []
    explanations = []

    # Print all financial ratios for the last three years
    print(f"\nFinancial Ratios for '{company_name}' :")
    print(ratios_df)

    # Get the latest financial ratios
    latest_ratios = ratios_df.iloc[-1]
    print(f"\nLatest Financial Ratios for '{company_name}' :")
    print(latest_ratios)

    # Simple Risk Assessment
    if latest_ratios["ROE"] < 10:
        warnings.append("Warning: Low Return on Equity (ROE) indicates potential underperformance.")

    if latest_ratios["Current Ratio"] < 1:
        warnings.append("Warning: Current Ratio below 1 indicates potential liquidity issues.")
        explanations.append("Explanation: A current ratio below 1 suggests that the company may not have enough short-term assets to cover its short-term liabilities, which could lead to liquidity problems.")

    if latest_ratios["Debt to Equity"] > 1:
        warnings.append("Warning: High Debt to Equity ratio indicates higher financial risk.")
        explanations.append("Explanation: A debt to equity ratio greater than 1 means that the company is financing more of its operations with debt than with equity, which can increase financial risk.")

    # Create a static directory if it doesn't exist
    static_folder = os.path.join(os.getcwd(), "static")
    os.makedirs(static_folder, exist_ok=True)

    # Normalize the data using Z-Score normalization
    normalized_ratios_df = normalize_data(ratios_df)

    # Prepare data for plotting
    years = normalized_ratios_df["Year"]
    normalized_ratios_df.set_index("Year", inplace=True)

    # Plotting all normalized financial ratios
    plt.figure(figsize=(14, 8))
    normalized_ratios_df = normalized_ratios_df.drop("Company", axis=1)

    for column in normalized_ratios_df.columns:
        plt.plot(
            normalized_ratios_df.index,
            normalized_ratios_df[column],
            marker="o",
            label=column,
        )

    plt.title(f"Normalized Financial Ratios for {company_name} Over the Years")
    plt.xlabel("Year")
    plt.ylabel("Z-Score Normalized Value")
    plt.xticks(rotation=45)
    plt.ylim(-2, 2)  # Adjust based on expected Z-score range
    plt.grid(which="both", linestyle="--", linewidth=0.5)
    plt.minorticks_on()
    plt.grid(which="minor", linestyle=":", linewidth="0.5", color="gray")
    plt.legend()
    plt.tight_layout()

    # Save the plot in the static folder
    plot_filename = os.path.join(
        static_folder,
        f"{company_name.replace(' ', '_')}_normalized_financial_ratios_line_plot.png",
    )
    plt.savefig(plot_filename)
    plt.close()

    return warnings, explanations, plot_filename  # Return the path to the saved plot

def main():
    ticker = input("Enter the stock ticker symbol: ").upper() + ".NS"
    ratios_df = get_financial_ratios(ticker)

    analyze_ratios(ratios_df)


if __name__ == "__main__":
    main()

pd.set_option("future.no_silent_downcasting", True)
