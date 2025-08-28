"""
Community Knowledge Base System for Stock Fundamental Analysis Platform

This module implements the community-driven qualitative analysis and stock insights system
that enables users to contribute and access community insights for stocks.

Follows existing Flask patterns and integrates with the current architecture.
"""

import sqlite3
import hashlib
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import os


class InsightCategory(Enum):
    """Categories for community insights"""

    MOAT_ANALYSIS = "moat_analysis"
    MANAGEMENT = "management"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    INDUSTRY_ANALYSIS = "industry_analysis"


@dataclass
class CommunityInsight:
    """Data class for community insights"""

    id: Optional[int]
    ticker: str
    category: InsightCategory
    content: str
    anonymous_user_id: str
    created_at: datetime
    votes_up: int = 0
    votes_down: int = 0
    is_flagged: bool = False


@dataclass
class InsightVote:
    """Data class for insight votes"""

    id: Optional[int]
    insight_id: int
    anonymous_user_id: str
    vote_type: str  # 'up' or 'down'
    created_at: datetime


class CommunityKnowledgeBase:
    """
    Community Knowledge Base system for managing stock insights and contributions.

    Features:
    - Anonymous contribution tracking with spam prevention
    - Insight categories for different types of analysis
    - Simple voting system for quality validation
    - Content moderation and spam detection
    """

    def __init__(self, db_path: str = "data/community_insights.db"):
        """Initialize the community knowledge base with database connection"""
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize database tables for community insights system"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create insights table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    anonymous_user_id TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    votes_up INTEGER DEFAULT 0,
                    votes_down INTEGER DEFAULT 0,
                    is_flagged BOOLEAN DEFAULT FALSE
                )
            """
            )

            # Create indexes for better performance
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_insights_ticker ON insights (ticker)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_insights_category ON insights (category)
            """
            )

            # Create votes table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS insight_votes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight_id INTEGER NOT NULL,
                    anonymous_user_id TEXT NOT NULL,
                    vote_type TEXT NOT NULL CHECK (vote_type IN ('up', 'down')),
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (insight_id) REFERENCES insights (id),
                    UNIQUE(insight_id, anonymous_user_id)
                )
            """
            )

            # Create spam prevention table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS contribution_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anonymous_user_id TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
            """
            )

            # Create indexes for spam prevention table
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_tracking_user ON contribution_tracking (anonymous_user_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_tracking_created ON contribution_tracking (created_at)
            """
            )

            conn.commit()

    def generate_anonymous_user_id(self, session_data: str) -> str:
        """Generate anonymous user ID from session data for tracking"""
        return hashlib.sha256(session_data.encode()).hexdigest()[:16]

    def _content_hash(self, content: str) -> str:
        """Generate hash of content for spam detection"""
        return hashlib.md5(content.strip().lower().encode()).hexdigest()

    def _is_spam(self, anonymous_user_id: str, ticker: str, content: str) -> bool:
        """
        Check if contribution appears to be spam

        Spam detection rules:
        - Duplicate content from same user in last 24 hours
        - More than 5 contributions from same user in 30 minutes
        """
        content_hash = self._content_hash(content)
        cutoff_time = datetime.now() - timedelta(hours=24)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check for duplicate content from same user in last 24 hours
            cursor.execute(
                """
                SELECT COUNT(*) FROM contribution_tracking 
                WHERE anonymous_user_id = ? AND content_hash = ? AND created_at > ?
            """,
                (anonymous_user_id, content_hash, cutoff_time),
            )

            if cursor.fetchone()[0] > 0:
                return True

            # Check for too many contributions from same user in short time
            cursor.execute(
                """
                SELECT COUNT(*) FROM contribution_tracking 
                WHERE anonymous_user_id = ? AND created_at > ?
            """,
                (anonymous_user_id, datetime.now() - timedelta(minutes=30)),
            )

            if cursor.fetchone()[0] >= 5:  # Max 5 contributions per 30 minutes
                return True

            return False

    def _validate_content(self, content: str) -> Tuple[bool, str]:
        """
        Validate content for basic quality standards

        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        if not content or len(content.strip()) < 10:
            return False, "Content must be at least 10 characters long"
        if len(content) > 2000:
            return False, "Content must be less than 2000 characters"

        # Basic content quality checks
        content_lower = content.lower()
        spam_patterns = ["click here", "buy now", "guaranteed profit", "spam", "scam"]
        for pattern in spam_patterns:
            if pattern in content_lower:
                return False, "Content appears to contain spam or promotional material"

        return True, ""

    def contribute_insight(
        self,
        ticker: str,
        category: InsightCategory,
        content: str,
        anonymous_user_id: str,
    ) -> Tuple[bool, str]:
        """
        Submit a new community insight for a stock

        Args:
            ticker: Stock ticker symbol (without .NS suffix)
            category: Type of insight (moat, management, etc.)
            content: The insight content
            anonymous_user_id: Anonymous user identifier

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Validate input
        is_valid, error_msg = self._validate_content(content)
        if not is_valid:
            return False, error_msg

        # Check for spam
        if self._is_spam(anonymous_user_id, ticker, content):
            return (
                False,
                "Too many similar contributions detected. Please try again later.",
            )

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Insert insight
                cursor.execute(
                    """
                    INSERT INTO insights 
                    (ticker, category, content, anonymous_user_id, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        ticker,
                        category.value,
                        content,
                        anonymous_user_id,
                        datetime.now(),
                    ),
                )

                # Track contribution for spam prevention
                content_hash = self._content_hash(content)
                cursor.execute(
                    """
                    INSERT INTO contribution_tracking
                    (anonymous_user_id, ticker, content_hash, created_at)
                    VALUES (?, ?, ?, ?)
                """,
                    (anonymous_user_id, ticker, content_hash, datetime.now()),
                )

                conn.commit()
                return True, "Insight contributed successfully"

        except Exception as e:
            return False, f"Error contributing insight: {str(e)}"

    def get_insights_for_ticker(
        self, ticker: str, limit: int = 10
    ) -> List[CommunityInsight]:
        """
        Retrieve community insights for a specific ticker

        Args:
            ticker: Stock ticker symbol (without .NS suffix)
            limit: Maximum number of insights to return

        Returns:
            List of CommunityInsight objects sorted by quality (votes) and recency
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, ticker, category, content, anonymous_user_id, created_at,
                       votes_up, votes_down, is_flagged
                FROM insights 
                WHERE ticker = ? AND is_flagged = 0
                ORDER BY (votes_up - votes_down) DESC, created_at DESC
                LIMIT ?
            """,
                (ticker, limit),
            )

            insights = []
            for row in cursor.fetchall():
                insights.append(
                    CommunityInsight(
                        id=row[0],
                        ticker=row[1],
                        category=InsightCategory(row[2]),
                        content=row[3],
                        anonymous_user_id=row[4],
                        created_at=datetime.fromisoformat(str(row[5])),
                        votes_up=row[6],
                        votes_down=row[7],
                        is_flagged=bool(row[8]),
                    )
                )

            return insights

    def vote_on_insight(
        self, insight_id: int, anonymous_user_id: str, vote_type: str
    ) -> Tuple[bool, str]:
        """
        Vote on an insight's quality

        Args:
            insight_id: ID of the insight to vote on
            anonymous_user_id: Anonymous user identifier
            vote_type: 'up' or 'down'

        Returns:
            Tuple of (success: bool, message: str)
        """
        if vote_type not in ["up", "down"]:
            return False, "Invalid vote type. Must be 'up' or 'down'"

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if insight exists and is not flagged
                cursor.execute(
                    """
                    SELECT id FROM insights WHERE id = ? AND is_flagged = 0
                """,
                    (insight_id,),
                )
                if not cursor.fetchone():
                    return False, "Insight not found or has been flagged"

                # Check if user already voted
                cursor.execute(
                    """
                    SELECT vote_type FROM insight_votes 
                    WHERE insight_id = ? AND anonymous_user_id = ?
                """,
                    (insight_id, anonymous_user_id),
                )

                existing_vote = cursor.fetchone()

                if existing_vote:
                    # Update existing vote if different
                    if existing_vote[0] != vote_type:
                        cursor.execute(
                            """
                            UPDATE insight_votes 
                            SET vote_type = ?, created_at = ?
                            WHERE insight_id = ? AND anonymous_user_id = ?
                        """,
                            (vote_type, datetime.now(), insight_id, anonymous_user_id),
                        )

                        # Update vote counts
                        self._update_vote_counts(cursor, insight_id)
                        conn.commit()
                        return True, "Vote updated successfully"
                    else:
                        return False, "You have already voted this way on this insight"
                else:
                    # Insert new vote
                    cursor.execute(
                        """
                        INSERT INTO insight_votes 
                        (insight_id, anonymous_user_id, vote_type, created_at)
                        VALUES (?, ?, ?, ?)
                    """,
                        (insight_id, anonymous_user_id, vote_type, datetime.now()),
                    )

                    # Update vote counts
                    self._update_vote_counts(cursor, insight_id)
                    conn.commit()
                    return True, "Vote recorded successfully"

        except Exception as e:
            return False, f"Error recording vote: {str(e)}"

    def _update_vote_counts(self, cursor, insight_id: int):
        """Update vote counts for an insight"""
        cursor.execute(
            """
            SELECT 
                COUNT(CASE WHEN vote_type = 'up' THEN 1 END) as up_votes,
                COUNT(CASE WHEN vote_type = 'down' THEN 1 END) as down_votes
            FROM insight_votes WHERE insight_id = ?
        """,
            (insight_id,),
        )

        result = cursor.fetchone()
        up_votes, down_votes = result if result else (0, 0)

        cursor.execute(
            """
            UPDATE insights 
            SET votes_up = ?, votes_down = ?
            WHERE id = ?
        """,
            (up_votes, down_votes, insight_id),
        )

    def flag_insight(self, insight_id: int, anonymous_user_id: str) -> Tuple[bool, str]:
        """
        Flag an insight for moderation

        Args:
            insight_id: ID of the insight to flag
            anonymous_user_id: Anonymous user identifier

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if insight exists
                cursor.execute("SELECT id FROM insights WHERE id = ?", (insight_id,))
                if not cursor.fetchone():
                    return False, "Insight not found"

                cursor.execute(
                    """
                    UPDATE insights SET is_flagged = 1 WHERE id = ?
                """,
                    (insight_id,),
                )

                conn.commit()
                return True, "Insight flagged for review"
        except Exception as e:
            return False, f"Error flagging insight: {str(e)}"

    def get_insights_by_category(
        self, category: InsightCategory, limit: int = 20
    ) -> List[CommunityInsight]:
        """
        Get insights by category across all tickers

        Args:
            category: The insight category to filter by
            limit: Maximum number of insights to return

        Returns:
            List of CommunityInsight objects
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, ticker, category, content, anonymous_user_id, created_at,
                       votes_up, votes_down, is_flagged
                FROM insights 
                WHERE category = ? AND is_flagged = 0
                ORDER BY (votes_up - votes_down) DESC, created_at DESC
                LIMIT ?
            """,
                (category.value, limit),
            )

            insights = []
            for row in cursor.fetchall():
                insights.append(
                    CommunityInsight(
                        id=row[0],
                        ticker=row[1],
                        category=InsightCategory(row[2]),
                        content=row[3],
                        anonymous_user_id=row[4],
                        created_at=datetime.fromisoformat(str(row[5])),
                        votes_up=row[6],
                        votes_down=row[7],
                        is_flagged=bool(row[8]),
                    )
                )

            return insights

    def get_contribution_stats(self, anonymous_user_id: str) -> Dict[str, int]:
        """
        Get contribution statistics for a user

        Args:
            anonymous_user_id: Anonymous user identifier

        Returns:
            Dictionary with contribution statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get total contributions
            cursor.execute(
                """
                SELECT COUNT(*) FROM insights WHERE anonymous_user_id = ?
            """,
                (anonymous_user_id,),
            )
            total_contributions = cursor.fetchone()[0]

            # Get total votes received
            cursor.execute(
                """
                SELECT SUM(votes_up), SUM(votes_down) FROM insights 
                WHERE anonymous_user_id = ?
            """,
                (anonymous_user_id,),
            )
            result = cursor.fetchone()
            total_up_votes = result[0] if result[0] else 0
            total_down_votes = result[1] if result[1] else 0

            return {
                "total_contributions": total_contributions,
                "total_up_votes": total_up_votes,
                "total_down_votes": total_down_votes,
                "net_votes": total_up_votes - total_down_votes,
            }
