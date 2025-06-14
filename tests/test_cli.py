import builtins
import pytest

from src import cli

def test_main_calls_analysis(monkeypatch):
    # Mock input to provide a ticker symbol
    monkeypatch.setattr(builtins, "input", lambda _: "TCS")
    # Mock get_financial_ratios to return a dummy DataFrame
    called = {}

    def fake_get_financial_ratios(ticker):
        called["ticker"] = ticker
        import pandas as pd
        return pd.DataFrame({"ROE": [10]})

    def fake_analyze_ratios(df):
        called["analyze"] = True
        return [], [], None

    monkeypatch.setattr(cli, "get_financial_ratios", fake_get_financial_ratios)
    monkeypatch.setattr(cli, "analyze_ratios", fake_analyze_ratios)

    cli.main()
    assert called["ticker"] == "TCS.NS"
    assert called.get("analyze") is True