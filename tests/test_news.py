import pytest
from src.news import get_news_categories, categorize_news, get_market_news

def test_get_news_categories_structure():
    categories = get_news_categories()
    assert isinstance(categories, dict)
    assert "Market" in categories
    assert "IPO" in categories
    assert isinstance(categories["Market"], list)

def test_categorize_news_single_category():
    title = "Company announces new IPO"
    description = "The public offering is expected to raise funds."
    categories = categorize_news(title, description)
    assert "IPO" in categories

def test_categorize_news_multiple_categories():
    title = "RBI policy impacts stock market and banking sector"
    description = "The new monetary policy by RBI affects trading and banking."
    categories = categorize_news(title, description)
    assert "Market" in categories
    assert "Economy" in categories
    assert "Sector" in categories

def test_categorize_news_no_match():
    title = "Completely unrelated headline"
    description = "No keywords here."
    categories = categorize_news(title, description)
    assert categories == ["Others"]

def test_categorize_news_case_insensitivity():
    title = "IPO LAUNCH"
    description = "Public offering details."
    categories = categorize_news(title, description)
    assert "IPO" in categories

def test_categorize_news_partial_keyword():
    title = "The company is innovative"
    description = "They focus on new tech."
    categories = categorize_news(title, description)
    assert "Technology" in categories

def test_get_market_news_structure(monkeypatch):
    # Mock requests.get to avoid real HTTP requests
    import types

    class MockResponse:
        def __init__(self, content):
            self.content = content
        def raise_for_status(self):
            pass

    # Minimal valid RSS feed with one item
    fake_rss = b"""
    <rss>
      <channel>
        <item>
          <title>Test Market News</title>
          <link>http://example.com/news1</link>
          <pubDate>Fri, 13 Jun 2025 10:00:00 +0530</pubDate>
          <description>Stock market hits new high.</description>
        </item>
      </channel>
    </rss>
    """

    def mock_get(*args, **kwargs):
        return MockResponse(fake_rss)

    import src.news
    monkeypatch.setattr(src.news.requests, "get", mock_get)

    news = get_market_news()
    assert isinstance(news, list)
    assert len(news) >= 1
    item = news[0]
    assert "title" in item
    assert "link" in item
    assert "publisher" in item
    assert "published_at" in item
    assert "description" in item
    assert "score" in item
    assert "categories" in item
    assert isinstance(item["categories"], list)