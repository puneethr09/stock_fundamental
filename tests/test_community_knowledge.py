"""
Tests for Community Knowledge Base System

This module provides comprehensive unit and integration tests for the community
insights functionality including contribution management, voting, spam prevention,
and database operations.
"""

import sys
import os
import pytest
import tempfile
import sqlite3
from datetime import datetime, timedelta

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from community_knowledge import (
    CommunityKnowledgeBase,
    InsightCategory,
    CommunityInsight,
    InsightVote,
)


class TestCommunityKnowledgeBase:
    """Test suite for CommunityKnowledgeBase class"""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        fd, path = tempfile.mkstemp()
        os.close(fd)
        yield path
        os.unlink(path)

    @pytest.fixture
    def kb(self, temp_db):
        """Create a CommunityKnowledgeBase instance with temp database"""
        return CommunityKnowledgeBase(db_path=temp_db)

    @pytest.fixture
    def sample_user_id(self, kb):
        """Generate a sample anonymous user ID"""
        return kb.generate_anonymous_user_id("test_session_data")

    def test_database_initialization(self, kb):
        """Test that database tables are created properly"""
        with sqlite3.connect(kb.db_path) as conn:
            cursor = conn.cursor()

            # Check insights table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='insights'"
            )
            assert cursor.fetchone() is not None

            # Check votes table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='insight_votes'"
            )
            assert cursor.fetchone() is not None

            # Check tracking table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='contribution_tracking'"
            )
            assert cursor.fetchone() is not None

    def test_generate_anonymous_user_id(self, kb):
        """Test anonymous user ID generation"""
        session_data = "test_session_data"
        user_id = kb.generate_anonymous_user_id(session_data)

        assert isinstance(user_id, str)
        assert len(user_id) == 16  # Should be truncated to 16 characters

        # Should be consistent
        user_id2 = kb.generate_anonymous_user_id(session_data)
        assert user_id == user_id2

        # Should be different for different session data
        user_id3 = kb.generate_anonymous_user_id("different_session_data")
        assert user_id != user_id3

    def test_content_validation(self, kb):
        """Test content validation logic"""
        # Valid content
        valid, msg = kb._validate_content(
            "This is a valid insight about the company's moat."
        )
        assert valid is True
        assert msg == ""

        # Too short content
        valid, msg = kb._validate_content("Short")
        assert valid is False
        assert "at least 10 characters" in msg

        # Empty content
        valid, msg = kb._validate_content("")
        assert valid is False

        # Too long content
        valid, msg = kb._validate_content("x" * 2001)
        assert valid is False
        assert "less than 2000 characters" in msg

        # Spam content
        valid, msg = kb._validate_content("Click here for guaranteed profit!")
        assert valid is False
        assert "spam" in msg.lower()

    def test_contribute_insight_success(self, kb, sample_user_id):
        """Test successful insight contribution"""
        ticker = "TCS"
        category = InsightCategory.MOAT_ANALYSIS
        content = (
            "This company has a strong competitive moat due to its brand recognition."
        )

        success, message = kb.contribute_insight(
            ticker, category, content, sample_user_id
        )

        assert success is True
        assert "successfully" in message

        # Verify insight was stored
        insights = kb.get_insights_for_ticker(ticker)
        assert len(insights) == 1
        assert insights[0].ticker == ticker
        assert insights[0].category == category
        assert insights[0].content == content
        assert insights[0].anonymous_user_id == sample_user_id

    def test_contribute_insight_invalid_content(self, kb, sample_user_id):
        """Test insight contribution with invalid content"""
        ticker = "TCS"
        category = InsightCategory.MOAT_ANALYSIS
        content = "Short"  # Too short

        success, message = kb.contribute_insight(
            ticker, category, content, sample_user_id
        )

        assert success is False
        assert "10 characters" in message

    def test_spam_detection_duplicate_content(self, kb, sample_user_id):
        """Test spam detection for duplicate content"""
        ticker = "TCS"
        category = InsightCategory.MOAT_ANALYSIS
        content = "This company has a strong competitive moat."

        # First contribution should succeed
        success1, _ = kb.contribute_insight(ticker, category, content, sample_user_id)
        assert success1 is True

        # Second identical contribution should be detected as spam
        success2, message2 = kb.contribute_insight(
            ticker, category, content, sample_user_id
        )
        assert success2 is False
        assert "similar contributions detected" in message2

    def test_spam_detection_rate_limiting(self, kb, sample_user_id):
        """Test spam detection for rate limiting"""
        ticker = "TCS"
        category = InsightCategory.MOAT_ANALYSIS

        # Submit 5 different contributions (should be allowed)
        for i in range(5):
            content = f"This is insight number {i} about the company's strategy."
            success, _ = kb.contribute_insight(
                ticker, category, content, sample_user_id
            )
            assert success is True

        # 6th contribution should be rate limited
        content = "This is the 6th insight which should be blocked."
        success, message = kb.contribute_insight(
            ticker, category, content, sample_user_id
        )
        assert success is False
        assert "similar contributions detected" in message

    def test_get_insights_for_ticker(self, kb, sample_user_id):
        """Test retrieving insights for a specific ticker"""
        ticker = "TCS"
        category = InsightCategory.MOAT_ANALYSIS

        # Add multiple insights
        insights_data = [
            "First insight about competitive advantages.",
            "Second insight about market position.",
            "Third insight about brand strength.",
        ]

        for content in insights_data:
            kb.contribute_insight(ticker, category, content, sample_user_id)

        # Add insight for different ticker
        kb.contribute_insight("INFY", category, "INFY insight", sample_user_id)

        # Retrieve insights for TCS
        insights = kb.get_insights_for_ticker(ticker)
        assert len(insights) == 3

        # Should only return TCS insights
        for insight in insights:
            assert insight.ticker == ticker
            assert insight.content in insights_data

    def test_vote_on_insight(self, kb, sample_user_id):
        """Test voting functionality"""
        # Create an insight first
        ticker = "TCS"
        category = InsightCategory.MOAT_ANALYSIS
        content = "Great competitive moat analysis."

        kb.contribute_insight(ticker, category, content, sample_user_id)
        insights = kb.get_insights_for_ticker(ticker)
        insight_id = insights[0].id

        # Different user for voting
        voter_id = kb.generate_anonymous_user_id("different_session")

        # Test upvote
        success, message = kb.vote_on_insight(insight_id, voter_id, "up")
        assert success is True
        assert "successfully" in message

        # Verify vote counts
        insights = kb.get_insights_for_ticker(ticker)
        assert insights[0].votes_up == 1
        assert insights[0].votes_down == 0

        # Test changing vote to downvote
        success, message = kb.vote_on_insight(insight_id, voter_id, "down")
        assert success is True
        assert "updated" in message

        # Verify updated vote counts
        insights = kb.get_insights_for_ticker(ticker)
        assert insights[0].votes_up == 0
        assert insights[0].votes_down == 1

    def test_vote_same_vote_twice(self, kb, sample_user_id):
        """Test voting with the same vote type twice"""
        # Create insight
        ticker = "TCS"
        category = InsightCategory.MOAT_ANALYSIS
        content = "Analysis content."

        kb.contribute_insight(ticker, category, content, sample_user_id)
        insights = kb.get_insights_for_ticker(ticker)
        insight_id = insights[0].id

        voter_id = kb.generate_anonymous_user_id("voter_session")

        # First upvote
        success1, _ = kb.vote_on_insight(insight_id, voter_id, "up")
        assert success1 is True

        # Second upvote should fail
        success2, message2 = kb.vote_on_insight(insight_id, voter_id, "up")
        assert success2 is False
        assert "already voted" in message2

    def test_vote_invalid_vote_type(self, kb, sample_user_id):
        """Test voting with invalid vote type"""
        # Create insight
        ticker = "TCS"
        category = InsightCategory.MOAT_ANALYSIS
        content = "Analysis content."

        kb.contribute_insight(ticker, category, content, sample_user_id)
        insights = kb.get_insights_for_ticker(ticker)
        insight_id = insights[0].id

        voter_id = kb.generate_anonymous_user_id("voter_session")

        # Invalid vote type
        success, message = kb.vote_on_insight(insight_id, voter_id, "invalid")
        assert success is False
        assert "Invalid vote type" in message

    def test_flag_insight(self, kb, sample_user_id):
        """Test flagging insights"""
        # Create insight
        ticker = "TCS"
        category = InsightCategory.MOAT_ANALYSIS
        content = "Analysis content."

        kb.contribute_insight(ticker, category, content, sample_user_id)
        insights = kb.get_insights_for_ticker(ticker)
        insight_id = insights[0].id

        flagger_id = kb.generate_anonymous_user_id("flagger_session")

        # Flag the insight
        success, message = kb.flag_insight(insight_id, flagger_id)
        assert success is True
        assert "flagged" in message

        # Flagged insights should not appear in regular queries
        insights_after_flag = kb.get_insights_for_ticker(ticker)
        assert len(insights_after_flag) == 0

    def test_get_insights_by_category(self, kb, sample_user_id):
        """Test retrieving insights by category"""
        # Add insights for different categories and tickers
        kb.contribute_insight(
            "TCS", InsightCategory.MOAT_ANALYSIS, "TCS moat analysis", sample_user_id
        )
        kb.contribute_insight(
            "INFY", InsightCategory.MOAT_ANALYSIS, "INFY moat analysis", sample_user_id
        )
        kb.contribute_insight(
            "TCS", InsightCategory.MANAGEMENT, "TCS management analysis", sample_user_id
        )

        # Get all moat analysis insights
        moat_insights = kb.get_insights_by_category(InsightCategory.MOAT_ANALYSIS)
        assert len(moat_insights) == 2

        for insight in moat_insights:
            assert insight.category == InsightCategory.MOAT_ANALYSIS

        # Get management insights
        mgmt_insights = kb.get_insights_by_category(InsightCategory.MANAGEMENT)
        assert len(mgmt_insights) == 1
        assert mgmt_insights[0].category == InsightCategory.MANAGEMENT

    def test_get_contribution_stats(self, kb, sample_user_id):
        """Test getting contribution statistics"""
        # Initially no contributions
        stats = kb.get_contribution_stats(sample_user_id)
        assert stats["total_contributions"] == 0
        assert stats["total_up_votes"] == 0
        assert stats["total_down_votes"] == 0
        assert stats["net_votes"] == 0

        # Add some contributions
        kb.contribute_insight(
            "TCS", InsightCategory.MOAT_ANALYSIS, "First analysis", sample_user_id
        )
        kb.contribute_insight(
            "INFY", InsightCategory.MANAGEMENT, "Second analysis", sample_user_id
        )

        # Add votes to the insights
        insights = kb.get_insights_for_ticker("TCS")
        voter_id = kb.generate_anonymous_user_id("voter")
        kb.vote_on_insight(insights[0].id, voter_id, "up")

        # Check updated stats
        stats = kb.get_contribution_stats(sample_user_id)
        assert stats["total_contributions"] == 2
        assert stats["total_up_votes"] == 1
        assert stats["net_votes"] == 1

    def test_insights_ordering(self, kb, sample_user_id):
        """Test that insights are ordered by votes and recency"""
        ticker = "TCS"
        category = InsightCategory.MOAT_ANALYSIS

        # Add multiple insights
        kb.contribute_insight(ticker, category, "First insight", sample_user_id)
        kb.contribute_insight(ticker, category, "Second insight", sample_user_id)
        kb.contribute_insight(ticker, category, "Third insight", sample_user_id)

        insights = kb.get_insights_for_ticker(ticker)

        # Add votes to second insight to make it highest rated
        voter_id = kb.generate_anonymous_user_id("voter")
        kb.vote_on_insight(insights[1].id, voter_id, "up")
        kb.vote_on_insight(
            insights[1].id, kb.generate_anonymous_user_id("voter2"), "up"
        )

        # Retrieve insights again - should be ordered by votes
        ordered_insights = kb.get_insights_for_ticker(ticker)
        assert len(ordered_insights) == 3

        # Second insight (now with 2 upvotes) should be first
        assert ordered_insights[0].content == "Second insight"
        assert ordered_insights[0].votes_up == 2


class TestIntegration:
    """Integration tests for community knowledge base with Flask app"""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        fd, path = tempfile.mkstemp()
        os.close(fd)
        yield path
        os.unlink(path)

    def test_insight_categories_enum(self):
        """Test InsightCategory enum values"""
        assert InsightCategory.MOAT_ANALYSIS.value == "moat_analysis"
        assert InsightCategory.MANAGEMENT.value == "management"
        assert InsightCategory.COMPETITIVE_ANALYSIS.value == "competitive_analysis"
        assert InsightCategory.INDUSTRY_ANALYSIS.value == "industry_analysis"

    def test_community_insight_dataclass(self):
        """Test CommunityInsight dataclass"""
        insight = CommunityInsight(
            id=1,
            ticker="TCS",
            category=InsightCategory.MOAT_ANALYSIS,
            content="Test content",
            anonymous_user_id="test_user",
            created_at=datetime.now(),
            votes_up=5,
            votes_down=1,
            is_flagged=False,
        )

        assert insight.ticker == "TCS"
        assert insight.category == InsightCategory.MOAT_ANALYSIS
        assert insight.votes_up == 5
        assert insight.votes_down == 1
        assert insight.is_flagged is False

    def test_performance_with_many_insights(self, temp_db):
        """Test performance with larger dataset"""
        kb = CommunityKnowledgeBase(db_path=temp_db)

        # Add 50 insights with different user IDs to avoid rate limiting
        tickers = ["TCS", "INFY", "HCLTECH", "WIPRO", "TECHM"]
        categories = list(InsightCategory)

        for i in range(50):
            # Use different user ID for each contribution to avoid spam detection
            user_id = kb.generate_anonymous_user_id(f"test_user_{i}")
            ticker = tickers[i % len(tickers)]
            category = categories[i % len(categories)]
            content = f"Performance test insight number {i} with detailed analysis."

            success, _ = kb.contribute_insight(ticker, category, content, user_id)
            assert success is True

        # Test retrieval performance
        import time

        start_time = time.time()
        insights = kb.get_insights_for_ticker("TCS")
        end_time = time.time()

        # Should retrieve insights quickly (less than 100ms as per requirements)
        assert (end_time - start_time) < 0.1
        assert len(insights) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
