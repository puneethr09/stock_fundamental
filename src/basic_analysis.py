import yfinance as yf
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime
from utils import calculate_ratio, calculate_margin, normalize_financial_data
import plotly.graph_objects as go
from plotly.subplots import make_subplots

matplotlib.use("Agg")  # Use a non-interactive backend for plotting


def get_financial_ratios(ticker):
    stock = yf.Ticker(ticker)
    try:
        company_name = stock.info.get("longName", "Unknown Company")
        print(f"Retrieved data for: {company_name}")
    except:
        print(f"Failed to retrieve data for ticker: {ticker}")
        return None

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
    pb_ratio = calculate_pb_ratio(historical_data, balance_sheet, stock)

    roe.index = pd.to_datetime(roe.index, format="%Y-%m-%d").year
    roa.index = pd.to_datetime(roa.index, format="%Y-%m-%d").year
    roic.index = pd.to_datetime(roic.index, format="%Y-%m-%d").year
    quick_ratio.index = pd.to_datetime(quick_ratio.index, format="%Y-%m-%d").year
    current_ratio.index = pd.to_datetime(current_ratio.index, format="%Y-%m-%d").year
    debt_to_equity.index = pd.to_datetime(debt_to_equity.index, format="%Y-%m-%d").year
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
            "P/B Ratio": pb_ratio.reindex(available_years).values,
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


def calculate_eps(income_stmt):
    try:
        if isinstance(income_stmt, pd.Series):
            eps = income_stmt["Diluted EPS"] * 1000000
        else:
            eps = income_stmt.loc["Diluted EPS"] * 1000000
        return eps
    except:
        print("EPS calculation failed")
        return pd.Series(np.nan, index=income_stmt.index)


def calculate_pe_ratio(historical_data, eps):
    try:
        # Get year-end closing prices
        year_end_prices = historical_data.groupby(historical_data.index.year)[
            "Close"
        ].last()
        # Convert EPS index to years
        eps.index = eps.index.year
        matching_years = eps.index
        aligned_prices = year_end_prices[matching_years]
        pe_ratios = aligned_prices / eps
        return pe_ratios
    except Exception as e:
        print(f"\nPE Ratio calculation error: {e}")
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


def calculate_pb_ratio(historical_data, balance_sheet, stock):
    try:
        # Get shares outstanding from stock info
        shares_outstanding = stock.info.get("sharesOutstanding")
        # Get year-end closing prices
        year_end_prices = historical_data.groupby(historical_data.index.year)[
            "Close"
        ].last()
        # Get total equity and calculate book value per share
        total_equity = balance_sheet.loc["Common Stock Equity"] * 1e6
        book_value_per_share = total_equity / shares_outstanding
        # Extract years from the datetime index
        years = [int(str(idx)[:4]) for idx in total_equity.index]
        book_value_per_share.index = years
        # Calculate P/B ratio
        pb_ratios = year_end_prices[years] / book_value_per_share
        return pb_ratios
    except Exception as e:
        print(f"\nP/B Ratio calculation error: {e}")
        return pd.Series(np.nan, index=balance_sheet.columns)


def calculate_roi(income_statement, balance_sheet):
    try:
        return (
            income_statement.loc["Operating Income"] / balance_sheet.loc["Total Assets"]
        ) * 100
    except KeyError:
        return pd.Series(np.nan, index=income_statement.columns)


def analyze_ratios(ratios_df):
    if ratios_df is None or len(ratios_df) == 0:
        print("No financial ratios available for analysis.")
        return [], [], None

    company_name = ratios_df["Company"].unique()[0]
    warnings = []
    explanations = []

    latest_ratios = ratios_df.iloc[-1]

    if latest_ratios["ROE"] < 10:
        warnings.append(
            "Low Return on Equity (ROE) indicates potential underperformance."
        )

    if latest_ratios["Current Ratio"] < 1:
        warnings.append("Current Ratio below 1 indicates potential liquidity issues.")
        explanations.append(
            "A current ratio below 1 suggests that the company may not have enough short-term assets to cover its short-term liabilities, which could lead to liquidity problems."
        )

    if latest_ratios["Debt to Equity"] > 1:
        warnings.append("High Debt to Equity ratio indicates higher financial risk.")
        explanations.append(
            "A debt to equity ratio greater than 1 means that the company is financing more of its operations with debt than with equity, which can increase financial risk."
        )

    if latest_ratios["Operating Margin"] < 15:
        warnings.append(
            "Low Operating Margin indicates potential operational inefficiency."
        )
        explanations.append(
            "An operating margin below 15% suggests the company may need to improve its operational efficiency or pricing strategy."
        )

    if latest_ratios["Net Profit Margin"] < 10:
        warnings.append("Low Net Profit Margin indicates reduced profitability.")
        explanations.append(
            "A net profit margin below 10% indicates the company might need to control costs or improve revenue generation."
        )

    if latest_ratios["Asset Turnover"] < 0.5:
        warnings.append("Low Asset Turnover indicates inefficient use of assets.")
        explanations.append(
            "An asset turnover ratio below 0.5 suggests the company might not be using its assets efficiently to generate revenue."
        )

    if latest_ratios["Interest Coverage"] < 2:
        warnings.append(
            "Low Interest Coverage Ratio indicates potential debt servicing issues."
        )
        explanations.append(
            "An interest coverage ratio below 2 suggests the company might have difficulty meeting its interest payment obligations."
        )

    plot_html = create_plotly_visualization(ratios_df, company_name)

    return warnings, explanations, plot_html


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

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_plotly_visualization(ratios_df, company_name):
    # Define a set of dark colors
    dark_colors = ["blue", "red", "green", "darkorange"]

    # Assign dark colors to each metric, repeating if necessary
    color_mapping = {
        "ROE": dark_colors[0],
        "ROA": dark_colors[1],
        "ROIC": dark_colors[2],
        "ROI": dark_colors[3],
        "Quick Ratio": dark_colors[1],
        "Current Ratio": dark_colors[0],
        "P/E Ratio": dark_colors[1],
        "P/B Ratio": dark_colors[2],
        "EBIT Margin": dark_colors[0],
        "Debt to Equity": dark_colors[0],
        "Operating Margin": dark_colors[0],
        "Net Profit Margin": dark_colors[1],
        "Asset Turnover": dark_colors[1],
        "Interest Coverage": dark_colors[0],  # Repeat colors if needed
    }

    fig = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=(
            f"Return Ratios {{<span style='color:{color_mapping['ROE']}'>ROE</span>, "
            f"<span style='color:{color_mapping['ROA']}'>ROA</span>, "
            f"<span style='color:{color_mapping['ROIC']}'>ROIC</span>, "
            f"<span style='color:{color_mapping['ROI']}'>ROI</span>}}",
            f"Liquidity Ratios {{<span style='color:{color_mapping['Current Ratio']}'>Current Ratio</span>, "
            f"<span style='color:{color_mapping['Quick Ratio']}'>Quick Ratio</span>}}",
            f"Market & Profitability {{<span style='color:{color_mapping['EBIT Margin']}'>EBIT Margin</span>, "
            f"<span style='color:{color_mapping['P/E Ratio']}'>P/E Ratio</span>, "
            f"<span style='color:{color_mapping['P/B Ratio']}'>P/B Ratio</span>}}",
            f"Leverage Ratio {{<span style='color:{color_mapping['Debt to Equity']}'>Debt to Equity</span>}}",
            f"Margin Analysis {{<span style='color:{color_mapping['Operating Margin']}'>Operating Margin</span>, "
            f"<span style='color:{color_mapping['Net Profit Margin']}'>Net Profit Margin</span>}}",
            f"Efficiency Metrics {{<span style='color:{color_mapping['Interest Coverage']}'>Interest Coverage</span>, "
            f"<span style='color:{color_mapping['Asset Turnover']}'>Asset Turnover</span>}}",
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    # Return Ratios (1,1)
    for metric in ["ROE", "ROA", "ROIC", "ROI"]:
        if metric in ratios_df.columns:
            color = color_mapping.get(metric, "black")  # Default to black if not found
            fig.add_trace(
                go.Scatter(
                    x=ratios_df["Year"],
                    y=ratios_df[metric],
                    mode="lines+markers",
                    name=metric,
                    hovertemplate=f"{metric}: %{{y}}<extra></extra>",
                    line=dict(color=color, width=2),
                ),
                row=1,
                col=1,
            )

    # Liquidity Ratios (1,2)
    for metric in ["Quick Ratio", "Current Ratio"]:
        color = color_mapping.get(metric, "black")
        fig.add_trace(
            go.Scatter(
                x=ratios_df["Year"],
                y=ratios_df[metric],
                name=metric,
                hovertemplate=f"{metric}: %{{y}}<extra></extra>",
                line=dict(color=color, width=2),
            ),
            row=1,
            col=2,
        )

    # Market & Profitability (2,1)
    for metric in ["P/E Ratio", "P/B Ratio", "EBIT Margin"]:
        color = color_mapping.get(metric, "black")
        fig.add_trace(
            go.Scatter(
                x=ratios_df["Year"],
                y=ratios_df[metric],
                name=metric,
                hovertemplate=f"{metric}: %{{y}}<extra></extra>",
                line=dict(color=color, width=2),
            ),
            row=2,
            col=1,
        )

    # Leverage Ratio (2,2)
    color = color_mapping.get("Debt to Equity", "black")
    fig.add_trace(
        go.Scatter(
            x=ratios_df["Year"],
            y=ratios_df["Debt to Equity"],
            name="Debt to Equity",
            hovertemplate="Debt to Equity: %{y}<extra></extra>",
            line=dict(color=color, width=2),
        ),
        row=2,
        col=2,
    )

    # Margin Analysis (3,1)
    for metric in ["Operating Margin", "Net Profit Margin"]:
        color = color_mapping.get(metric, "black")
        fig.add_trace(
            go.Scatter(
                x=ratios_df["Year"],
                y=ratios_df[metric],
                name=metric,
                hovertemplate=f"{metric}: %{{y}}<extra></extra>",
                line=dict(color=color, width=2),
            ),
            row=3,
            col=1,
        )

    # Efficiency Metrics (3,2)
    for metric in ["Asset Turnover", "Interest Coverage"]:
        color = color_mapping.get(metric, "black")
        fig.add_trace(
            go.Scatter(
                x=ratios_df["Year"],
                y=ratios_df[metric],
                name=metric,
                hovertemplate=f"{metric}: %{{y}}<extra></extra>",
                line=dict(color=color, width=2),
            ),
            row=3,
            col=2,
        )

    fig.update_layout(
        height=1200,
        width=1600,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=True,
        legend=dict(
            yanchor="middle",
            y=0.5,
            xanchor="right",
            x=1.15,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1,
        ),
        margin=dict(l=50, r=150, t=80, b=50),
    )

    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="lightgrey",
        automargin=True,
        tickformat="d",
        dtick=1,
    )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="lightgrey", automargin=True)

    return fig.to_html(full_html=False, include_plotlyjs=True)
