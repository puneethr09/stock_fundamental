import pandas as pd
import numpy as np
import pytest

from src.growth import calculate_cagr, calculate_yoy_growth, summarize_growth

def test_calculate_cagr_basic():
    series = pd.Series([100, 200, 400], index=[2020, 2021, 2022])
    cagr = calculate_cagr(series)
    # CAGR from 100 to 400 over 2 years: ((400/100)^(1/2) - 1) * 100 = 100%
    assert np.isclose(cagr, 100.0)

def test_calculate_cagr_nan_for_short_series():
    series = pd.Series([100], index=[2020])
    assert np.isnan(calculate_cagr(series))

def test_calculate_cagr_nan_for_zero_start():
    series = pd.Series([0, 100], index=[2020, 2021])
    assert np.isnan(calculate_cagr(series))

def test_calculate_cagr_nan_for_zero_years():
    series = pd.Series([100, 200], index=[2020, 2020])
    assert np.isnan(calculate_cagr(series))

def test_calculate_yoy_growth_basic():
    series = pd.Series([100, 110, 121], index=[2020, 2021, 2022])
    yoy = calculate_yoy_growth(series)
    assert np.isclose(yoy.iloc[1], 10.0)
    assert np.isclose(yoy.iloc[2], 10.0)

def test_calculate_yoy_growth_with_nan():
    series = pd.Series([100, np.nan, 121], index=[2020, 2021, 2022])
    yoy = calculate_yoy_growth(series)
    assert np.isnan(yoy.iloc[1])
    assert np.isnan(yoy.iloc[2])  # Should be nan, not 21.0

def test_summarize_growth_all_metrics():
    data = {
        "Year": [2020, 2021, 2022],
        "ROE": [10, 20, 40],
        "ROA": [5, 10, 20],
        "Net Profit Margin": [2, 4, 8],
        "Operating Margin": [1, 2, 4],
    }
    df = pd.DataFrame(data)
    summary = summarize_growth(df)
    assert "ROE CAGR (%)" in summary
    assert "ROE YoY Growth (%)" in summary
    assert np.isclose(summary["ROE CAGR (%)"], 100.0)
    assert np.isclose(summary["ROE YoY Growth (%)"], 100.0)

def test_summarize_growth_missing_metric():
    data = {
        "Year": [2020, 2021, 2022],
        "ROE": [10, 20, 40],
    }
    df = pd.DataFrame(data)
    summary = summarize_growth(df)
    assert "ROE CAGR (%)" in summary
    assert "ROA CAGR (%)" not in summary