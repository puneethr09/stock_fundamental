# code to find nearest ticker
import yfinance as yf
from difflib import get_close_matches


def find_nearest_ticker(input_ticker):
    """
    Finds the nearest matching Indian stock ticker to the input ticker.

    Args:
        input_ticker (str): The ticker symbol to search for.

    Returns:
        str: The nearest matching ticker symbol, or None if no match is found.
    """
    # List of Indian stock tickers (you may need to update this list)
    indian_tickers = yf.Ticker("^NSEI").info["components"]

    print(indian_tickers)

    # Find close matches
    matches = get_close_matches(input_ticker.upper(), indian_tickers, n=3, cutoff=0.6)

    print(matches)

    if matches:
        print("Ticker not found. Did you mean one of these?")
        for i, match in enumerate(matches, 1):
            company_name = yf.Ticker(match).info.get("longName", "Unknown Company")
            print(f"{i}. {match} ({company_name})")

        choice = input("Enter the number of your choice (or press Enter to exit): ")
        if choice.isdigit() and 1 <= int(choice) <= len(matches):
            return matches[int(choice) - 1]

    return None


if __name__ == "__main__":
    ticker = input("Enter the stock ticker symbol: ")

    ticker = ticker.upper() + ".NS"
    try:
        nearest_ticker = yf.Ticker(ticker).info
        print(nearest_ticker.get("longName", "Unknown Company"))
    except:
        nearest_ticker = find_nearest_ticker(ticker[:-3])
        if nearest_ticker:
            print(
                f"Nearest ticker found: {nearest_ticker.get('longName', 'Unknown Company')}"
            )
        else:
            print("No matching ticker found.")
