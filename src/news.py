import pytz
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

def get_news_categories():
    """
    Returns a dictionary of news categories and their corresponding keywords.
    """
    NEWS_CATEGORIES = {
        "Market": [
            "stock",
            "shares",
            "equity",
            "trading",
            "price target",
            "market",
            "market cap",
            "sebi",
            "nse",
            "bse",
        ],
        "IPO": ["ipo", "public offering", "listing", "subscription", "issue price"],
        "Economy": ["gdp", "inflation", "rbi", "monetary policy", "fiscal", "economy"],
        "Corporate": [
            "earnings",
            "results",
            "profit",
            "revenue",
            "merger",
            "acquisition",
        ],
        "Sector": [
            "banking",
            "finance",
            "insurance",
            "energy",
            "technology",
            "healthcare",
        ],
        "Politics": ["election", "government", "policy", "legislation", "politics"],
        "Regulation": [
            "regulation",
            "compliance",
            "regulatory",
            "ban",
        ],
        "GlobalMarkets": [
            "global",
            "international",
            "foreign",
            "overseas",
            "world markets",
            "Japan",
            "US",
            "Europe",
            "China",
            "Dow Jones",
            "Nikkei",
            "Hang Seng",
        ],
        "Geopolitics": ["war", "crisis", "conflict", "geopolitics", "international"],
        "Environment": [
            "climate",
            "environment",
            "sustainability",
            "environmental",
            "climate change",
        ],
        "Social": ["social", "social media", "social impact", "social responsibility"],
        "Technology": ["tech", "technology", "innovation", "digital", "software"],
        "Media": ["media", "press", "journalism", "publication", "news"],
        "Entertainment": ["entertainment", "movie", "music", "sports", "celebrity"],
        "Health": ["health", "medicine", "medical", "pharmaceutical", "healthcare"],
        "Education": ["education", "school", "university", "student", "teacher"],
        "RealEstate": [
            "real estate",
            "property",
            "housing",
            "construction",
            "real estate",
        ],
        "Transportation": [
            "transportation",
            "transport",
            "logistics",
            "shipping",
            "railway",
        ],
        "Retail": ["retail", "shopping", "e-commerce", "consumer", "retailer"],
        "Agriculture": ["agriculture", "farming", "farm", "crop", "livestock"],
        "Tourism": ["tourism", "travel", "hospitality", "hotel", "tourism"],
        "Commodities": ["gold", "crude", "oil", "commodity", "metal", "agricultural"],
        "Others": [],  # Default category for uncategorized news
    }
    return NEWS_CATEGORIES


def categorize_news(title, description):
    """
    Categorize news into multiple relevant categories based on keywords
    Returns a list of applicable categories
    """
    combined_text = (title + " " + description).lower()
    categories = []

    for category, keywords in get_news_categories().items():
        for keyword in keywords:
            if keyword in combined_text:
                categories.append(category)
                break  # Break after first keyword match for each category

    # If no categories matched, add to 'Others'
    if not categories:
        categories.append("Others")

    return categories


def get_market_news():
    """
    Fetches comprehensive Indian financial news from multiple trusted sources,
    rates them based on importance using keyword relevance and recency, and returns the top 500.
    """
    rss_feeds = [
        # Economic Times Feeds
        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
        "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms",
        "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",
        # Business Standard Feeds
        "https://www.business-standard.com/rss/markets-106.rss",
        "https://www.business-standard.com/rss/finance-103.rss",
        "https://www.business-standard.com/rss/companies-101.rss",
        # LiveMint Feeds
        "https://www.livemint.com/rss/markets",
        "https://www.livemint.com/rss/companies",
        "https://www.livemint.com/rss/money",
        # the hindu
        "https://www.thehindubusinessline.com/markets/feeder/default.rss",
    ]

    important_keywords = [
        "crash",
        "bankruptcy",
        "RBI",
        "SEBI",
        "budget",
        "inflation",
        "interest rate",
        "GDP",
        "policy",
        "merger",
        "acquisition",
        "IPO",
        "earnings",
        "bear",
        "bull",
        "recession",
    ]

    all_news = []
    seen_titles = set()  # Set to track unique news titles
    ist = pytz.timezone("Asia/Kolkata")
    current_time = datetime.now(ist)
    cutoff_date = current_time - timedelta(days=2)  # Two days ago

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/rss+xml",
        "Referer": "https://economictimes.indiatimes.com",
    }

    for feed_url in rss_feeds:
        try:
            response = requests.get(feed_url, headers=headers, timeout=15)
            response.raise_for_status()

            root = ET.fromstring(response.content)

            for item in root.findall(".//item"):
                try:
                    pub_date = datetime.strptime(
                        item.find("pubDate").text, "%a, %d %b %Y %H:%M:%S %z"
                    ).astimezone(ist)
                except ValueError:
                    try:
                        pub_date = (
                            datetime.strptime(
                                item.find("pubDate").text, "%a, %d %b %Y %H:%M:%S GMT"
                            )
                            .replace(tzinfo=pytz.UTC)
                            .astimezone(ist)
                        )
                    except:
                        continue

                # Check if the news item is within the last two days
                if pub_date >= cutoff_date:
                    title = item.find("title").text
                    description = (
                        item.find("description").text
                        if item.find("description") is not None
                        else ""
                    )
                    publisher = (
                        feed_url.split("/")[2].replace("www.", "").split(".")[0].title()
                    )

                    # Check for duplicate titles
                    if title not in seen_titles:
                        seen_titles.add(title)

                        # Calculate score
                        score = 0
                        # Keyword relevance
                        for keyword in important_keywords:
                            if (
                                keyword.lower() in title.lower()
                                or keyword.lower() in description.lower()
                            ):
                                score += 10
                        # Recency
                        days_old = (current_time - pub_date).days
                        score += max(
                            0, 2 - days_old
                        )  # More recent articles get higher scores

                        # Inside your get_market_news function, modify the news_item creation:
                        news_item = {
                            "title": title,
                            "link": item.find("link").text,
                            "publisher": publisher,
                            "published_at": pub_date.strftime("%Y-%m-%d %H:%M:%S"),
                            "description": (
                                description[:200] + "..."
                                if len(description) > 200
                                else description
                            ),
                            "score": score,
                            "categories": categorize_news(
                                title, description
                            ),  # Now returns a list
                        }

                        all_news.append(news_item)
        except Exception as e:
            print(f"Error fetching feed {feed_url}: {e}")
            continue

    # Sort news by score in descending order and return the top 500
    all_news.sort(key=lambda x: x["score"], reverse=True)
    return all_news[:5000]
