import pandas as pd
import numpy as np


def calculate_quick_ratio(balance_sheet):
    try:
        current_assets = balance_sheet.loc["Current Assets"]
        inventory = (
            balance_sheet.loc["Inventory"]
            if "Inventory" in balance_sheet.index
            else pd.Series(0, index=balance_sheet.columns)
        )
        prepaid_assets = (
            balance_sheet.loc["Prepaid Assets"].fillna(0)
            if "Prepaid Assets" in balance_sheet.index
            else pd.Series(0, index=balance_sheet.columns)
        )
        current_liabilities = balance_sheet.loc["Current Liabilities"]
        return (current_assets - inventory - prepaid_assets) / current_liabilities
    except KeyError as e:
        print(f"Missing key in balance sheet: {e}")
        return pd.Series(np.nan, index=balance_sheet.columns)


def calculate_eps(income_stmt):
    try:
        if "Diluted EPS" in income_stmt.index:
            eps = income_stmt.loc["Diluted EPS"] * 1_000_000
        elif (
            "Net Income" in income_stmt.index
            and "Weighted Average Shares Outstanding" in income_stmt.index
        ):
            eps = (
                income_stmt.loc["Net Income"]
                / income_stmt.loc["Weighted Average Shares Outstanding"]
            )
        else:
            eps = pd.Series(np.nan, index=income_stmt.columns)
        return eps
    except Exception:
        print("EPS calculation failed")
        return pd.Series(np.nan, index=income_stmt.columns)


def calculate_pe_ratio(historical_data, eps):
    try:
        year_end_prices = historical_data.groupby(historical_data.index.year)[
            "Close"
        ].last()
        eps.index = pd.to_datetime(eps.index).year
        aligned_prices = year_end_prices.reindex(eps.index)
        pe_ratios = aligned_prices / eps
        return pe_ratios
    except Exception as e:
        print(f"\nPE Ratio calculation error: {e}")
        return pd.Series(np.nan, index=eps.index)


def calculate_ebit_margin(income_statement):
    try:
        if (
            "Total Revenue" in income_statement.index
            and "Operating Expense" in income_statement.index
        ):
            ebit = (
                income_statement.loc["Total Revenue"]
                - income_statement.loc["Operating Expense"]
            )
            return (ebit / income_statement.loc["Total Revenue"]) * 100
        else:
            return pd.Series(np.nan, index=income_statement.columns)
    except KeyError:
        return pd.Series(np.nan, index=income_statement.columns)


def calculate_pb_ratio(historical_data, balance_sheet, stock):
    try:
        shares_outstanding = stock.info.get("sharesOutstanding")
        year_end_prices = historical_data.groupby(historical_data.index.year)[
            "Close"
        ].last()
        total_equity = balance_sheet.loc["Common Stock Equity"] * 1e6
        book_value_per_share = total_equity / shares_outstanding
        years = pd.to_datetime(total_equity.index).year
        book_value_per_share.index = years
        pb_ratios = year_end_prices.reindex(years) / book_value_per_share
        return pb_ratios
    except Exception as e:
        print(f"\nP/B Ratio calculation error: {e}")
        return pd.Series(np.nan, index=balance_sheet.columns)


def calculate_roi(income_statement, balance_sheet):
    try:
        if (
            "Operating Income" in income_statement.index
            and "Total Assets" in balance_sheet.index
        ):
            return (
                income_statement.loc["Operating Income"]
                / balance_sheet.loc["Total Assets"]
            ) * 100
        else:
            return pd.Series(np.nan, index=income_statement.columns)
    except KeyError:
        return pd.Series(np.nan, index=income_statement.columns)


def calculate_ratio(df1, df2, numerator, denominator):
    try:
        num = (
            df1.loc[numerator]
            if numerator in df1.index
            else pd.Series(0, index=df1.columns)
        )
        denom = (
            df2.loc[denominator]
            if denominator in df2.index
            else pd.Series(1, index=df2.columns)
        )
        return num / denom
    except KeyError:
        return pd.Series(np.nan, index=df1.columns)


def calculate_margin(df, numerator, denominator):
    try:
        num = (
            df.loc[numerator]
            if numerator in df.index
            else pd.Series(0, index=df.columns)
        )
        denom = (
            df.loc[denominator]
            if denominator in df.index
            else pd.Series(1, index=df.columns)
        )
        return (num / denom) * 100
    except KeyError:
        return pd.Series(np.nan, index=df.columns)
