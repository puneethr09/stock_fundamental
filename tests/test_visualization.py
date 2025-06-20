import os
import pandas as pd
import numpy as np
from src.visualization import plot_financial_ratios, create_plotly_visualization


def sample_ratios_df():
    # Create a DataFrame with all required columns and 3 years of data
    data = {
        "Year": [2020, 2021, 2022],
        "ROE": [10, 12, 14],
        "ROA": [5, 6, 7],
        "ROIC": [8, 9, 10],
        "ROI": [7, 8, 9],
        "Quick Ratio": [1.1, 1.2, 1.3],
        "Current Ratio": [1.5, 1.6, 1.7],
        "P/E Ratio": [20, 22, 24],
        "P/B Ratio": [3, 3.2, 3.4],
        "EBIT Margin": [15, 16, 17],
        "Debt to Equity": [0.5, 0.6, 0.7],
        "Operating Margin": [18, 19, 20],
        "Net Profit Margin": [12, 13, 14],
        "Asset Turnover": [1.2, 1.3, 1.4],
        "Interest Coverage": [4, 5, 6],
        "Company": ["TestCo", "TestCo", "TestCo"],
    }
    return pd.DataFrame(data)


def test_plot_financial_ratios_creates_files(tmp_path, monkeypatch):
    df = sample_ratios_df()
    company_name = "TestCo"
    # Patch os.getcwd to use tmp_path for file output
    monkeypatch.setattr(os, "getcwd", lambda: str(tmp_path))
    files = plot_financial_ratios(df, company_name)
    static_dir = tmp_path / "static"
    assert isinstance(files, list)
    assert len(files) == 2
    for fname in files:
        assert (static_dir / fname).exists()


def test_create_plotly_visualization_html():
    df = sample_ratios_df()
    company_name = "TestCo"
    html = create_plotly_visualization(df, company_name)
    assert isinstance(html, str)
    assert "<html" not in html  # Should be partial HTML
    assert "plotly" in html.lower()
    # At least some content is present
    assert len(html) > 100
