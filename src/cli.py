import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.basic_analysis import get_financial_ratios, analyze_ratios


def main():
    ticker = input("Enter the stock ticker symbol: ").upper() + ".NS"
    ratios_df = get_financial_ratios(ticker)
    analyze_ratios(ratios_df)


if __name__ == "__main__":
    main()
