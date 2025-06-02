import sys
import os
import pandas as pd
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from basic_analysis import (
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
    data = {
        "Cash And Cash Equivalents": [100],
        "Short Term Investments": [50],
        "Current Receivables": [30],
        "Current Liabilities": [90]
    }
    balance_sheet = pd.DataFrame(data, index=[pd.Timestamp("2023-03-31")])
    quick_ratio = calculate_quick_ratio(balance_sheet)
    assert isinstance(quick_ratio, pd.Series)
    assert np.isclose(quick_ratio.iloc[0], (100+50+30)/90)

def test_calculate_eps():
    data = {
        "Net Income": [200],
        "Weighted Average Shares Outstanding": [100]
    }
    income_stmt = pd.DataFrame(data, index=[pd.Timestamp("2023-03-31")])
    eps = calculate_eps(income_stmt)
    assert isinstance(eps, pd.Series)
    assert np.isclose(eps.iloc[0], 2.0)

def test_calculate_pe_ratio():
    historical_data = pd.DataFrame({"Close": [100]}, index=[pd.Timestamp("2023-03-31")])
    eps = pd.Series([5], index=[pd.Timestamp("2023-03-31")])
    pe_ratio = calculate_pe_ratio(historical_data, eps)
    assert isinstance(pe_ratio, pd.Series)
    assert np.isclose(pe_ratio.iloc[0], 20.0)