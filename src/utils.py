import os
import pandas as pd
import numpy as np


def load_company_data(input_dir="input"):
    company_data = pd.DataFrame()

    for file in os.listdir(input_dir):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(input_dir, file))
            company_data = pd.concat([company_data, df], ignore_index=True)

    return company_data[["Company Name", "Ticker"]]


def calculate_ratio(numerator_df, denominator_df, numerator_label, denominator_label):
    try:
        return numerator_df.loc[numerator_label] / denominator_df.loc[denominator_label]
    except KeyError:
        return pd.Series(np.nan, index=numerator_df.columns)


def calculate_margin(income_statement, numerator_label, denominator_label):
    try:
        return (
            income_statement.loc[numerator_label]
            / income_statement.loc[denominator_label]
        ) * 100
    except KeyError:
        return pd.Series(np.nan, index=income_statement.columns)


def normalize_financial_data(ratios_df):
    normalized_df = ratios_df.copy()
    for column in normalized_df.columns[1:-1]:  # Skip 'Year' and 'Company'
        mean_val = normalized_df[column].mean()
        std_dev = normalized_df[column].std()
        normalized_df[column] = (normalized_df[column] - mean_val) / std_dev
    return normalized_df


def get_stock_data(ticker: str):
    """Compatibility shim used by some integration tests.

    This is a lightweight fallback that looks for the ticker in the CSV
    input files and returns a dict with basic fields. Tests generally
    patch this function, so this implementation is intentionally small
    and best-effort.
    """
    try:
        companies = load_company_data()
        match = companies[companies["Ticker"].str.contains(ticker, na=False)]
        if not match.empty:
            row = match.iloc[0]
            return {"Company Name": row["Company Name"], "Ticker": row["Ticker"]}
    except Exception:
        pass

    # Fallback minimal structure
    return {"Company Name": f"{ticker}", "Ticker": ticker}
