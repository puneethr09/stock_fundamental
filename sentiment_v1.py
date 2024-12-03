import requests
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer


def get_news_headlines(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all relevant tags
    tags = soup.find_all(["h1", "h2", "h3", "a"])

    # Filter headlines: assuming headlines are longer and contain ̦
    headlines = [
        tag.get_text(strip=True) for tag in tags if len(tag.get_text(strip=True)) > 50
    ]

    unique_headlines = list(set(headlines))

    # Remove non-headline items (e.g., navigation or language options)
    filtered_headlines = [
        headline
        for headline in unique_headlines
        if not any(
            keyword in headline.lower()
            for keyword in [
                "language",
                "facebook",
                "twitter",
                "linkedin",
                "home",
                "market",
            ]
        )
        # and not headline.isupper()
    ]

    return filtered_headlines


def analyze_sentiment(headlines):
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = []
    for headline in headlines:
        sentiment_score = sia.polarity_scores(headline)
        sentiment_scores.append(sentiment_score)
    return sentiment_scores


def main():

    try:
        choice = int(
            input(
                "Enter 1 for World Market, 2 for combined India and World Market else default is Indian Market: "
            )
        )
    except ValueError:
        print("Defaulting to Indian Market.")
        choice = 0

    if choice == 0:
        # url = "https://www.businesstoday.in/markets/stocks"
        url = "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=6&ssid=25&smid=0"
        headlines = get_news_headlines(url)
    elif choice == 1:
        url = "https://www.financialexpress.com/market/"
        headlines = get_news_headlines(url)
    else:  # combine both the url and add both india and world
        url = "https://www.cnbc.com/markets/"
        headlines = get_news_headlines(url)
        url = "https://www.financialexpress.com/market/"
        headlines.extend(get_news_headlines(url))

    # headlines = get_news_headlines(url)
    print(f"Total Headlines Found: {len(headlines)}")

    print("\nNews Headlines:")
    if not headlines:
        print("No relevant headlines found.")
    else:
        for i, headline in enumerate(headlines, start=1):
            print(f"{i}. {headline}")

    sentiment_scores = analyze_sentiment(headlines)
    overall_sentiment = (
        sum(s["compound"] for s in sentiment_scores) / len(sentiment_scores)
        if sentiment_scores
        else 0
    )

    print("\nSentiment Scores:")
    for i, sentiment_score in enumerate(sentiment_scores, start=1):
        print(f"{i}. {sentiment_score}")

    print("\nOverall Sentiment Score:", overall_sentiment)


if __name__ == "__main__":
    nltk.download("vader_lexicon")
    main()
