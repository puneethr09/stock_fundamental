#!/usr/bin/env python3
"""
Unit tests for ticker_finder module
"""

import pytest
from unittest.mock import patch, MagicMock
from src.ticker_finder import find_nearest_ticker


class TestTickerFinder:
    """Test cases for ticker finder functionality"""

    @patch("src.ticker_finder.yf.Ticker")
    def test_find_nearest_ticker_exact_match(self, mock_ticker):
        """Test finding exact ticker match"""
        # Mock the NSE index components
        mock_index = MagicMock()
        mock_index.info = {"components": ["RELIANCE.NS", "TCS.NS", "INFY.NS"]}

        # Mock individual ticker info
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {"longName": "Reliance Industries Ltd"}

        mock_ticker.side_effect = [mock_index, mock_ticker_instance]

        # Mock user input to select first match
        with patch("builtins.input", return_value="1"):
            with patch("builtins.print"):  # Suppress print statements
                result = find_nearest_ticker("RELIANCE")

        assert result == "RELIANCE.NS"

    @patch("src.ticker_finder.yf.Ticker")
    def test_find_nearest_ticker_close_match(self, mock_ticker):
        """Test finding close ticker match"""
        # Mock the NSE index components
        mock_index = MagicMock()
        mock_index.info = {"components": ["RELIANCE.NS", "TCS.NS", "INFY.NS"]}

        # Mock ticker info for matches
        mock_match1 = MagicMock()
        mock_match1.info = {"longName": "Tata Consultancy Services Ltd"}

        # Set up mock to return different objects for different calls
        mock_ticker.side_effect = [mock_index, mock_match1]

        # Mock user input to select first match
        with patch("builtins.input", return_value="1"):
            with patch("builtins.print"):
                result = find_nearest_ticker("TCS")

        assert result == "TCS.NS"

    @patch("src.ticker_finder.yf.Ticker")
    def test_find_nearest_ticker_no_match(self, mock_ticker):
        """Test when no close match is found"""
        # Mock the NSE index components
        mock_index = MagicMock()
        mock_index.info = {"components": ["RELIANCE.NS", "TCS.NS", "INFY.NS"]}

        mock_ticker.return_value = mock_index

        # Mock user input to exit without selection
        with patch("builtins.input", return_value=""):
            with patch("builtins.print"):
                result = find_nearest_ticker("NONEXISTENT")

        assert result is None

    @patch("src.ticker_finder.yf.Ticker")
    def test_find_nearest_ticker_invalid_choice(self, mock_ticker):
        """Test invalid user choice handling"""
        # Mock the NSE index components
        mock_index = MagicMock()
        mock_index.info = {"components": ["RELIANCE.NS", "TCS.NS", "INFY.NS"]}

        # Mock ticker info
        mock_match = MagicMock()
        mock_match.info = {"longName": "Reliance Industries Ltd"}

        mock_ticker.side_effect = [mock_index, mock_match]

        # Mock invalid user input
        with patch("builtins.input", return_value="invalid"):
            with patch("builtins.print"):
                result = find_nearest_ticker("RELIANCE")

        assert result is None

    @patch("src.ticker_finder.yf.Ticker")
    def test_find_nearest_ticker_case_insensitive(self, mock_ticker):
        """Test case insensitive matching"""
        # Mock the NSE index components
        mock_index = MagicMock()
        mock_index.info = {"components": ["RELIANCE.NS", "TCS.NS", "INFY.NS"]}

        # Mock ticker info
        mock_match = MagicMock()
        mock_match.info = {"longName": "Reliance Industries Ltd"}

        mock_ticker.side_effect = [mock_index, mock_match]

        # Test with lowercase input
        with patch("builtins.input", return_value="1"):
            with patch("builtins.print"):
                result = find_nearest_ticker("reliance")

        assert result == "RELIANCE.NS"

    @patch("src.ticker_finder.yf.Ticker")
    def test_find_nearest_ticker_empty_components(self, mock_ticker):
        """Test handling of empty components list"""
        # Mock empty components list
        mock_index = MagicMock()
        mock_index.info = {"components": []}

        mock_ticker.return_value = mock_index

        with patch("builtins.print"):
            result = find_nearest_ticker("ANYTICKER")

        assert result is None

    @patch("src.ticker_finder.yf.Ticker")
    def test_find_nearest_ticker_api_error(self, mock_ticker):
        """Test handling of API errors"""
        # Mock API failure for NSE index
        mock_ticker.side_effect = Exception("API Error")

        with patch("builtins.print"):
            # The function should handle the exception gracefully
            with pytest.raises(Exception):
                result = find_nearest_ticker("ANYTICKER")
