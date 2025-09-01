import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pytest
from basic_analysis import (
    get_financial_ratios,
    calculate_quick_ratio,
    calculate_eps,
    calculate_pe_ratio,
    analyze_ratios,
)


def test_get_financial_ratios_valid():
    """Unit test with mocked yfinance data"""
    df = get_financial_ratios("TCS.NS")
    assert df is not None
    assert "ROE" in df.columns
    assert len(df) > 0  # Should have data from mock


@pytest.mark.integration
def test_get_financial_ratios_valid_integration():
    """Integration test that actually calls external APIs"""
    df = get_financial_ratios("TCS.NS")
    assert df is not None
    assert "ROE" in df.columns


def test_get_financial_ratios_invalid():
    df = get_financial_ratios("INVALIDTICKER.NS")
    assert df is None
    """Integration test that actually calls external APIs"""
    df = get_financial_ratios("TCS.NS")
    assert df is not None
    assert "ROE" in df.columns


def test_get_financial_ratios_invalid():
    df = get_financial_ratios("INVALIDTICKER.NS")
    assert df is None


def test_analyze_ratios_empty():
    result = analyze_ratios(None)
    # New signature returns 6 values: warnings, explanations, plot_html, gaps, research_guides, confidence_score
    assert len(result) == 6
    warnings, explanations, plot_html, gaps, research_guides, confidence_score = result
    assert warnings == []
    assert explanations == []
    assert plot_html is None
    assert isinstance(gaps, list)
    assert isinstance(research_guides, list)
    assert isinstance(confidence_score, float)
    assert 0.0 <= confidence_score <= 1.0


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


def test_calculate_eps():
    data = {"Diluted EPS": [2.0]}
    income_stmt = pd.DataFrame(data, index=[pd.Timestamp("2023-03-31")]).T
    eps = calculate_eps(income_stmt)
    assert isinstance(eps, pd.Series)
    assert np.isclose(eps["2023-03-31"], 2.0 * 1_000_000)


def test_calculate_pe_ratio():
    historical_data = pd.DataFrame({"Close": [100]}, index=[pd.Timestamp("2023-03-31")])
    eps = pd.Series([5], index=[pd.Timestamp("2023-03-31")])
    pe_ratio = calculate_pe_ratio(historical_data, eps)
    assert isinstance(pe_ratio, pd.Series)
    assert np.isclose(pe_ratio.iloc[0], 20.0)
