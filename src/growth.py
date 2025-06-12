import pandas as pd
import numpy as np


def calculate_cagr(series):
    """
    Calculate CAGR (Compound Annual Growth Rate) for a pandas Series.
    Series index should be years (int or str convertible to int).
    """
    series = series.dropna()
    if len(series) < 2:
        return np.nan
    start_value = series.iloc[0]
    end_value = series.iloc[-1]
    n_years = int(series.index[-1]) - int(series.index[0])
    if start_value <= 0 or n_years == 0:
        return np.nan
    cagr = (end_value / start_value) ** (1 / n_years) - 1
    return cagr * 100  # Return as percentage


def calculate_yoy_growth(series):
    """
    Calculate Year-over-Year growth for a pandas Series.
    Returns a Series of YoY growth percentages.
    """
    series = series.sort_index()
    yoy_growth = series.pct_change() * 100
    return yoy_growth


def summarize_growth(ratios_df):
    """
    Summarize CAGR and YoY growth for key metrics.
    """
    summary = {}
    for metric in ["ROE", "ROA", "Net Profit Margin", "Operating Margin"]:
        if metric in ratios_df.columns:
            series = pd.Series(ratios_df[metric].values, index=ratios_df["Year"])
            summary[f"{metric} CAGR (%)"] = calculate_cagr(series)
            summary[f"{metric} YoY Growth (%)"] = calculate_yoy_growth(series).iloc[
                -1
            ]  # Most recent YoY
    return summary
