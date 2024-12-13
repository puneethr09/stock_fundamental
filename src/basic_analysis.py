import yfinance as yf
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime
from utils import calculate_ratio, calculate_margin, normalize_financial_data

matplotlib.use("Agg")  # Use a non-interactive backend for plotting


def get_financial_ratios(ticker):
    stock = yf.Ticker(ticker)
    company_name = stock.info.get("longName", "Unknown Company")

    historical_data = stock.history(period="max")
    if historical_data.empty:
        print(f"No historical data available for {ticker}.")
        return None

    if historical_data.index.tz is not None:
        historical_data.index = historical_data.index.tz_localize(None)

    available_years = historical_data.index.year.unique()
    if len(available_years) < 1:
        print(f"No historical data available for {ticker}.")
        return None

    balance_sheet = stock.balance_sheet / 1e6
    cash_flow = stock.cashflow / 1e6
    income_statement = stock.financials / 1e6

    balance_sheet = balance_sheet.apply(pd.to_numeric, errors="coerce")
    cash_flow = cash_flow.apply(pd.to_numeric, errors="coerce")
    income_statement = income_statement.apply(pd.to_numeric, errors="coerce")

    roe = calculate_ratio(
        income_statement, balance_sheet, "Net Income", "Common Stock Equity"
    )
    roa = calculate_ratio(income_statement, balance_sheet, "Net Income", "Total Assets")
    roic = calculate_ratio(
        cash_flow, income_statement, "Operating Cash Flow", "Total Revenue"
    )
    quick_ratio = calculate_quick_ratio(balance_sheet)
    current_ratio = calculate_ratio(
        balance_sheet, balance_sheet, "Current Assets", "Current Liabilities"
    )
    debt_to_equity = calculate_ratio(
        balance_sheet, balance_sheet, "Total Debt", "Common Stock Equity"
    )
    eps = calculate_eps(income_statement)
    pe_ratios = calculate_pe_ratio(historical_data, eps)
    ebit_margin = calculate_ebit_margin(income_statement)
    roi = calculate_roi(income_statement, balance_sheet)
    asset_turnover = calculate_ratio(
        income_statement, balance_sheet, "Total Revenue", "Total Assets"
    )
    operating_margin = calculate_margin(
        income_statement, "Operating Income", "Total Revenue"
    )
    net_profit_margin = calculate_margin(
        income_statement, "Net Income", "Total Revenue"
    )
    working_capital_ratio = calculate_ratio(
        balance_sheet, balance_sheet, "Current Assets", "Current Liabilities"
    )
    interest_coverage = calculate_ratio(
        income_statement, income_statement, "Operating Income", "Interest Expense"
    )

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

    roe *= 100
    roa *= 100
    roic *= 100
    operating_margin *= 100
    net_profit_margin *= 100

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

    ratios_df = ratios_df.dropna(how="all", subset=ratios_df.columns[1:-1])
    return ratios_df


def calculate_quick_ratio(balance_sheet):
    try:
        current_assets = balance_sheet.loc["Current Assets"]
        inventory = balance_sheet.get(
            "Inventory", pd.Series(0, index=balance_sheet.columns)
        )
        prepaid_assets = balance_sheet.loc["Prepaid Assets"]
        current_liabilities = balance_sheet.loc["Current Liabilities"]
        return (current_assets - inventory - prepaid_assets) / current_liabilities
    except KeyError:
        return pd.Series(np.nan, index=balance_sheet.columns)


def calculate_eps(income_statement):
    try:
        eps = income_statement.loc["Diluted EPS"] * 1e6
        eps.index = eps.index.tz_localize(None)
        return eps
    except KeyError:
        return pd.Series(np.nan, index=income_statement.columns)


def calculate_pe_ratio(historical_data, eps):
    try:
        return historical_data["Close"].reindex(eps.index) / eps
    except KeyError:
        return pd.Series(np.nan, index=eps.index)


def calculate_ebit_margin(income_statement):
    try:
        ebit = (
            income_statement.loc["Total Revenue"]
            - income_statement.loc["Operating Expense"]
        )
        return (ebit / income_statement.loc["Total Revenue"]) * 100
    except KeyError:
        return pd.Series(np.nan, index=income_statement.columns)


def calculate_roi(income_statement, balance_sheet):
    try:
        return (
            income_statement.loc["Net Income"] / balance_sheet.loc["Total Assets"]
        ) * 100
    except KeyError:
        return pd.Series(np.nan, index=income_statement.columns)


def analyze_ratios(ratios_df):
    if ratios_df is None or len(ratios_df) == 0:
        print("No financial ratios available for analysis.")
        return [], []

    company_name = ratios_df["Company"].unique()[0]
    warnings = []
    explanations = []

    latest_ratios = ratios_df.iloc[-1]

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

    static_folder = os.path.join(os.getcwd(), "static")
    os.makedirs(static_folder, exist_ok=True)

    plots = plot_financial_ratios(ratios_df, company_name)

    return warnings, explanations, plots


def plot_financial_ratios(ratios_df, company_name):
    static_folder = os.path.join(os.getcwd(), "static")
    os.makedirs(static_folder, exist_ok=True)

    fig, axes = plt.subplots(3, 2, figsize=(16, 12))

    axes[0, 0].plot(ratios_df["Year"], ratios_df["ROE"], marker="o", label="ROE")
    axes[0, 0].plot(ratios_df["Year"], ratios_df["ROA"], marker="o", label="ROA")
    axes[0, 0].plot(ratios_df["Year"], ratios_df["ROIC"], marker="o", label="ROIC")
    axes[0, 0].plot(ratios_df["Year"], ratios_df["ROI"], marker="o", label="ROI")
    axes[0, 0].set_title(f"Return Ratios for {company_name}")
    axes[0, 0].set_xlabel("Year")
    axes[0, 0].set_ylabel("Percentage")
    axes[0, 0].legend()
    axes[0, 0].grid()

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

    normalized_df = normalize_financial_data(ratios_df)
    plt.figure(figsize=(14, 8))
    for column in normalized_df.columns[1:-1]:
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
