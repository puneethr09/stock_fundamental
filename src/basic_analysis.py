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

    # Calculate new ratios individually
    try:
        asset_turnover = (
            income_stmt.loc["Total Revenue", income_stmt.columns]
            / balance_sheet.loc["Total Assets", balance_sheet.columns]
        )
        # ratios_df["Asset Turnover"] = asset_turnover.reindex(available_years).values
    except Exception as e:
        print(f"Could not calculate Asset Turnover: {e}")
        asset_turnover = pd.Series(np.nan, index=income_stmt.columns)

    try:
        operating_margin = (
            income_stmt.loc["Operating Income", income_stmt.columns]
            / income_stmt.loc["Total Revenue", income_stmt.columns]
        ) * 100
        # ratios_df["Operating Margin"] = operating_margin.reindex(available_years).values
    except Exception as e:
        print(f"Could not calculate Operating Margin: {e}")
        operating_margin = pd.Series(np.nan, index=income_stmt.columns)

    try:
        net_profit_margin = (
            income_stmt.loc["Net Income", income_stmt.columns]
            / income_stmt.loc["Total Revenue", income_stmt.columns]
        ) * 100
        # ratios_df["Net Profit Margin"] = net_profit_margin.reindex(
    #     available_years
    #  ).values
    except Exception as e:
        print(f"Could not calculate Net Profit Margin: {e}")
        net_profit_margin = pd.Series(np.nan, index=income_stmt.columns)

    try:
        working_capital_ratio = (
            balance_sheet.loc["Current Assets", balance_sheet.columns]
            / balance_sheet.loc["Current Liabilities", balance_sheet.columns]
        )
        # ratios_df["Working Capital Ratio"] = working_capital_ratio.reindex(
        #     available_years
        # ).values
    except Exception as e:
        print(f"Could not calculate Working Capital Ratio: {e}")
        working_capital_ratio = pd.Series(np.nan, index=income_stmt.columns)

    try:
        interest_coverage = (
            income_stmt.loc["Operating Income", income_stmt.columns]
            / income_stmt.loc["Interest Expense", income_stmt.columns]
        )
        # ratios_df["Interest Coverage"] = interest_coverage.reindex(
        #     available_years
        # ).values
    except Exception as e:
        print(f"Could not calculate Interest Coverage: {e}")
        interest_coverage = pd.Series(np.nan, index=income_stmt.columns)

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
    asset_turnover.index = pd.to_datetime(asset_turnover.index, format="%Y-%m-%d").year
    operating_margin.index = pd.to_datetime(
        operating_margin.index, format="%Y-%m-%d"
    ).year
    net_profit_margin.index = pd.to_datetime(
        net_profit_margin.index, format="%Y-%m-%d"
    ).year
    working_capital_ratio.index = pd.to_datetime(
        working_capital_ratio.index, format="%Y-%m-%d"
    ).year
    interest_coverage.index = pd.to_datetime(
        interest_coverage.index, format="%Y-%m-%d"
    ).year

    # Change to percentages
    roe = roe * 100
    roa = roa * 100
    roic = roic * 100
    # Convert to percentages where applicable
    operating_margin = operating_margin * 100
    net_profit_margin = net_profit_margin * 100

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
            "Asset Turnover": asset_turnover.reindex(available_years).values,
            "Operating Margin": operating_margin.reindex(available_years).values,
            "Net Profit Margin": net_profit_margin.reindex(available_years).values,
            "Working Capital Ratio": working_capital_ratio.reindex(
                available_years
            ).values,
            "Interest Coverage": interest_coverage.reindex(available_years).values,
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
        warnings.append(
            "Warning: Low Return on Equity (ROE) indicates potential underperformance."
        )

    if latest_ratios["Current Ratio"] < 1:
        warnings.append(
            "Warning: Current Ratio below 1 indicates potential liquidity issues."
        )
        explanations.append(
            "Explanation: A current ratio below 1 suggests that the company may not have enough short-term assets to cover its short-term liabilities, which could lead to liquidity problems."
        )

    if latest_ratios["Debt to Equity"] > 1:
        warnings.append(
            "Warning: High Debt to Equity ratio indicates higher financial risk."
        )
        explanations.append(
            "Explanation: A debt to equity ratio greater than 1 means that the company is financing more of its operations with debt than with equity, which can increase financial risk."
        )

    # Add new ratio analysis
    if latest_ratios["Operating Margin"] < 15:
        warnings.append(
            "Warning: Low Operating Margin indicates potential operational inefficiency."
        )
        explanations.append(
            "Explanation: An operating margin below 15% suggests the company may need to improve its operational efficiency or pricing strategy."
        )

    if latest_ratios["Net Profit Margin"] < 10:
        warnings.append(
            "Warning: Low Net Profit Margin indicates reduced profitability."
        )
        explanations.append(
            "Explanation: A net profit margin below 10% indicates the company might need to control costs or improve revenue generation."
        )

    if latest_ratios["Asset Turnover"] < 0.5:
        warnings.append(
            "Warning: Low Asset Turnover indicates inefficient use of assets."
        )
        explanations.append(
            "Explanation: An asset turnover ratio below 0.5 suggests the company might not be using its assets efficiently to generate revenue."
        )

    if latest_ratios["Interest Coverage"] < 2:
        warnings.append(
            "Warning: Low Interest Coverage Ratio indicates potential debt servicing issues."
        )
        explanations.append(
            "Explanation: An interest coverage ratio below 2 suggests the company might have difficulty meeting its interest payment obligations."
        )

    # Create a static directory if it doesn't exist
    static_folder = os.path.join(os.getcwd(), "static")
    os.makedirs(static_folder, exist_ok=True)

    # Create plots with new ratios included
    plots = plot_ratios(ratios_df, company_name)

    return warnings, explanations, plots


def plot_ratios(ratios_df, company_name):
    static_folder = os.path.join(os.getcwd(), "static")
    os.makedirs(static_folder, exist_ok=True)

    # Create a single figure with 3x2 subplots (increased from 2x2)
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))

    # Original Plot 1: ROE, ROA, ROIC, ROI (top-left)
    axes[0, 0].plot(ratios_df["Year"], ratios_df["ROE"], marker="o", label="ROE")
    axes[0, 0].plot(ratios_df["Year"], ratios_df["ROA"], marker="o", label="ROA")
    axes[0, 0].plot(ratios_df["Year"], ratios_df["ROIC"], marker="o", label="ROIC")
    axes[0, 0].plot(ratios_df["Year"], ratios_df["ROI"], marker="o", label="ROI")
    axes[0, 0].set_title(f"Return Ratios for {company_name}")
    axes[0, 0].set_xlabel("Year")
    axes[0, 0].set_ylabel("Percentage")
    axes[0, 0].legend()
    axes[0, 0].grid()

    # Original Plot 2: Quick Ratio and Current Ratio (top-right)
    axes[0, 1].plot(
        ratios_df["Year"], ratios_df["Quick Ratio"], marker="o", label="Quick Ratio"
    )
    axes[0, 1].plot(
        ratios_df["Year"], ratios_df["Current Ratio"], marker="o", label="Current Ratio"
    )
    axes[0, 1].set_title(f"Liquidity Ratios for {company_name}")
    axes[0, 1].set_xlabel("Year")
    axes[0, 1].set_ylabel("Ratio")
    axes[0, 1].legend()
    axes[0, 1].grid()

    # Original Plot 3: P/E Ratio, EBIT Margin (middle-left)
    axes[1, 0].plot(
        ratios_df["Year"], ratios_df["P/E Ratio"], marker="o", label="P/E Ratio"
    )
    axes[1, 0].plot(
        ratios_df["Year"], ratios_df["EBIT Margin"], marker="o", label="EBIT Margin"
    )
    axes[1, 0].set_title(f"Market and Profitability Metrics for {company_name}")
    axes[1, 0].set_xlabel("Year")
    axes[1, 0].set_ylabel("Ratio")
    axes[1, 0].legend()
    axes[1, 0].grid()

    # Original Plot 4: Debt to Equity (middle-right)
    axes[1, 1].plot(
        ratios_df["Year"],
        ratios_df["Debt to Equity"],
        marker="o",
        label="Debt to Equity",
    )
    axes[1, 1].set_title(f"Leverage Ratio for {company_name}")
    axes[1, 1].set_xlabel("Year")
    axes[1, 1].set_ylabel("Ratio")
    axes[1, 1].legend()
    axes[1, 1].grid()

    # New Plot 5: Operating and Net Profit Margins (bottom-left)
    axes[2, 0].plot(
        ratios_df["Year"],
        ratios_df["Operating Margin"],
        marker="o",
        label="Operating Margin",
    )
    axes[2, 0].plot(
        ratios_df["Year"],
        ratios_df["Net Profit Margin"],
        marker="o",
        label="Net Profit Margin",
    )
    axes[2, 0].set_title(f"Margin Analysis for {company_name}")
    axes[2, 0].set_xlabel("Year")
    axes[2, 0].set_ylabel("Percentage")
    axes[2, 0].legend()
    axes[2, 0].grid()

    # New Plot 6: Asset Turnover and Interest Coverage (bottom-right)
    axes[2, 1].plot(
        ratios_df["Year"],
        ratios_df["Asset Turnover"],
        marker="o",
        label="Asset Turnover",
    )
    axes[2, 1].plot(
        ratios_df["Year"],
        ratios_df["Interest Coverage"],
        marker="o",
        label="Interest Coverage",
    )
    axes[2, 1].set_title(f"Efficiency Metrics for {company_name}")
    axes[2, 1].set_xlabel("Year")
    axes[2, 1].set_ylabel("Ratio")
    axes[2, 1].legend()
    axes[2, 1].grid()

    plt.tight_layout()
    plt.savefig(os.path.join(static_folder, f"{company_name}_all_ratios.png"))
    plt.close()

    # Plot normalized ratios (including new ones)
    normalized_df = normalize_data(ratios_df)
    plt.figure(figsize=(14, 8))
    for column in normalized_df.columns[1:-1]:  # Skip Year and Company columns
        plt.plot(normalized_df["Year"], normalized_df[column], marker="o", label=column)
    plt.title(f"Normalized Financial Ratios for {company_name}")
    plt.xlabel("Year")
    plt.ylabel("Z-Score Normalized Value")
    plt.xticks(rotation=45)
    plt.ylim(-2, 2)
    plt.grid(which="both", linestyle="--", linewidth=0.5)
    plt.minorticks_on()
    plt.grid(which="minor", linestyle=":", linewidth="0.5", color="gray")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(static_folder, f"{company_name}_normalized_ratios.png"))
    plt.close()

    return [
        f"{company_name}_normalized_ratios.png",
        f"{company_name}_all_ratios.png",
    ]


def main():
    ticker = input("Enter the stock ticker symbol: ").upper() + ".NS"
    ratios_df = get_financial_ratios(ticker)

    analyze_ratios(ratios_df)


if __name__ == "__main__":
    main()

pd.set_option("future.no_silent_downcasting", True)
