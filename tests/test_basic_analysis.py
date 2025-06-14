import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pytest
from src.basic_analysis import (
    get_financial_ratios,
    calculate_quick_ratio,
    calculate_eps,
    calculate_pe_ratio,
    analyze_ratios,
)


def test_get_financial_ratios_valid():
    df = get_financial_ratios("TCS.NS")
    assert df is not None
    assert "ROE" in df.columns


def test_get_financial_ratios_invalid():
    df = get_financial_ratios("INVALIDTICKER.NS")
    assert df is None


def test_analyze_ratios_empty():
    warnings, explanations, plot_html = analyze_ratios(None)
    assert warnings == []
    assert explanations == []
    assert plot_html is None


def test_calculate_quick_ratio():
    # Rows: items, Columns: periods
    data = {
        "Current Assets": [180],
        "Inventory": [20],
        "Prepaid Assets": [10],
        "Current Liabilities": [90],
    }
    balance_sheet = pd.DataFrame(data, index=["2023-03-31"]).T
    quick_ratio = calculate_quick_ratio(balance_sheet)
    assert isinstance(quick_ratio, pd.Series)
    assert np.isclose(quick_ratio["2023-03-31"], (180 - 20 - 10) / 90)


def test_calculate_quick_ratio_missing_prepaid():
    data = {
        "Current Assets": [180],
        "Inventory": [20],
        "Current Liabilities": [90],
    }
    balance_sheet = pd.DataFrame(data, index=["2023-03-31"]).T
    quick_ratio = calculate_quick_ratio(balance_sheet)
    assert np.isclose(quick_ratio["2023-03-31"], (180 - 20 - 0) / 90)


def test_calculate_quick_ratio_missing_inventory_and_prepaid():
    data = {
        "Current Assets": [180],
        "Current Liabilities": [90],
    }
    balance_sheet = pd.DataFrame(data, index=["2023-03-31"]).T
    quick_ratio = calculate_quick_ratio(balance_sheet)
    assert np.isclose(quick_ratio["2023-03-31"], (180 - 0 - 0) / 90)


def test_calculate_quick_ratio_missing_current_assets():
    data = {
        "Inventory": [20],
        "Prepaid Assets": [10],
        "Current Liabilities": [90],
    }
    balance_sheet = pd.DataFrame(data, index=["2023-03-31"]).T
    quick_ratio = calculate_quick_ratio(balance_sheet)
    assert np.isnan(quick_ratio["2023-03-31"])


def test_calculate_quick_ratio_missing_current_liabilities():
    data = {
        "Current Assets": [180],
        "Inventory": [20],
        "Prepaid Assets": [10],
    }
    balance_sheet = pd.DataFrame(data, index=["2023-03-31"]).T
    quick_ratio = calculate_quick_ratio(balance_sheet)
    assert np.isnan(quick_ratio["2023-03-31"])


def test_calculate_eps_with_net_income_and_shares():
    data = {
        "Net Income": [1000],
        "Weighted Average Shares Outstanding": [100],
    }
    income_stmt = pd.DataFrame(data, index=["2023-03-31"]).T
    eps = calculate_eps(income_stmt)
    assert np.isclose(eps["2023-03-31"], 10.0)


def test_calculate_eps_missing_all():
    income_stmt = pd.DataFrame({}, index=["2023-03-31"]).T
    eps = calculate_eps(income_stmt)
    assert np.isnan(eps["2023-03-31"])


def test_calculate_pe_ratio_multiple_periods():
    historical_data = pd.DataFrame(
        {"Close": [100, 200]}, index=[pd.Timestamp("2023-03-31"), pd.Timestamp("2024-03-31")]
    )
    eps = pd.Series([5, 10], index=[pd.Timestamp("2023-03-31"), pd.Timestamp("2024-03-31")])
    pe_ratio = calculate_pe_ratio(historical_data, eps)
    assert np.isclose(pe_ratio.iloc[0], 20.0)
    assert np.isclose(pe_ratio.iloc[1], 20.0)


def test_calculate_pe_ratio_with_zero_eps():
    historical_data = pd.DataFrame(
        {"Close": [100]}, index=[pd.Timestamp("2023-03-31")]
    )
    eps = pd.Series([0], index=[pd.Timestamp("2023-03-31")])
    pe_ratio = calculate_pe_ratio(historical_data, eps)
    assert np.isinf(pe_ratio.iloc[0]) or np.isnan(pe_ratio.iloc[0])


def test_analyze_ratios_logic():
    # Simulate a ratios_df with all expected columns
    data = {
        "Year": [2023],
        "ROE": [5],
        "Current Ratio": [0.5],
        "Debt to Equity": [2],
        "Interest Coverage": [1],
        "Operating Margin": [10],
        "Net Profit Margin": [5],
        "EBIT Margin": [8],
        "Asset Turnover": [0.4],
        "Working Capital Ratio": [0.8],
        "Quick Ratio": [0.7],
        "P/E Ratio": [15],
        "P/B Ratio": [2],
        "Company": ["TestCo"],
    }
    ratios_df = pd.DataFrame(data)
    warnings, explanations, plot_html = analyze_ratios(ratios_df)
    assert any("ROE" in w for w in warnings)
    assert any("Current Ratio" in w for w in warnings)
    assert any("Debt to Equity" in w for w in warnings)
    assert any("Interest Coverage" in w for w in warnings)
    assert plot_html is not None


def test_get_financial_ratios_handles_missing_data():
    # Should not raise, even if ticker is nonsense
    df = get_financial_ratios("FAKETICKER.NS")
    assert df is None or isinstance(df, pd.DataFrame)
