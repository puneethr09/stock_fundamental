import builtins
import pytest

from src import ticker_finder

def test_find_nearest_ticker_found(monkeypatch):
    # Mock yfinance Ticker and get_close_matches
    class DummyTicker:
        def __init__(self, symbol):
            self.symbol = symbol
        @property
        def info(self):
            if self.symbol == "^NSEI":
                return {"components": ["RELIANCE", "TCS", "INFY"]}
            return {"longName": f"{self.symbol} Ltd"}

    monkeypatch.setattr(ticker_finder.yf, "Ticker", DummyTicker)
    monkeypatch.setattr(ticker_finder, "get_close_matches", lambda x, y, n, cutoff: ["TCS", "RELIANCE"])

    # Simulate user selecting the first match
    monkeypatch.setattr(builtins, "input", lambda _: "1")
    result = ticker_finder.find_nearest_ticker("TSS")
    assert result == "TCS"

def test_find_nearest_ticker_not_found(monkeypatch):
    class DummyTicker:
        def __init__(self, symbol):
            self.symbol = symbol
        @property
        def info(self):
            if self.symbol == "^NSEI":
                return {"components": ["RELIANCE", "TCS", "INFY"]}
            return {"longName": f"{self.symbol} Ltd"}

    monkeypatch.setattr(ticker_finder.yf, "Ticker", DummyTicker)
    monkeypatch.setattr(ticker_finder, "get_close_matches", lambda x, y, n, cutoff: [])
    result = ticker_finder.find_nearest_ticker("ZZZZ")
    assert result is None