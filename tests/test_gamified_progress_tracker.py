"""
Tests for the Gamified Progress Tracking System

This module tests the comprehensive badge award system, achievement logic,
progress tracking, and UI integration components.
"""

import unittest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Import the modules we're testing
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # Import Flask app for context
from src.gamified_progress_tracker import (
    GamifiedProgressTracker,
    BadgeType,
    Badge,
    ProgressMetrics,
    AchievementContext,
)
from src.educational_framework import (
    LearningStage,
    InteractionType,
    EducationalMasteryFramework,
)
from src.behavioral_analytics import BehavioralAnalyticsTracker


class TestGamifiedProgressTracker(unittest.TestCase):
    """Test cases for the GamifiedProgressTracker class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_framework = Mock(spec=EducationalMasteryFramework)
        self.tracker = GamifiedProgressTracker(self.mock_framework)

        # Create a sample achievement context
        self.sample_context = AchievementContext(
            session_id="test_session_123",
            user_id="test_user_123",
            current_stage=LearningStage.GUIDED_DISCOVERY,
            behavioral_data={"test": "data"},
            session_history=[],
            interaction_counts={
                interaction_type: 0 for interaction_type in InteractionType
            },
        )

    def test_badge_definitions_completeness(self):
        """Test that all badge types have proper definitions"""
        # Get all badge types
        all_badge_types = set(BadgeType)
        defined_badge_types = set(self.tracker.badge_definitions.keys())

        # Check that we have definitions for analysis milestones
        analysis_badges = {
            BadgeType.FIRST_ANALYSIS,
            BadgeType.BRONZE_ANALYST,
            BadgeType.SILVER_ANALYST,
            BadgeType.GOLD_ANALYST,
            BadgeType.PLATINUM_ANALYST,
        }

        for badge_type in analysis_badges:
            self.assertIn(badge_type, defined_badge_types)
            definition = self.tracker.badge_definitions[badge_type]
            self.assertIn("display_name", definition)
            self.assertIn("description", definition)
            self.assertIn("achievement_value", definition)
            self.assertIn("criteria", definition)

    def test_analysis_milestone_achievement_detection(self):
        """Test detection of analysis milestone achievements"""
        # Mock progress with different analysis counts
        test_cases = [
            (1, [BadgeType.FIRST_ANALYSIS]),
            (10, [BadgeType.BRONZE_ANALYST]),
            (50, [BadgeType.SILVER_ANALYST]),
            (100, [BadgeType.GOLD_ANALYST]),
            (500, [BadgeType.PLATINUM_ANALYST]),
        ]

        for analysis_count, expected_badges in test_cases:
            with self.subTest(analysis_count=analysis_count):
                # Mock both methods in the same context
                with patch.object(
                    self.tracker, "_get_progress_metrics"
                ) as mock_progress, patch.object(
                    self.tracker, "_get_earned_badges"
                ) as mock_badges:
                    mock_progress.return_value = ProgressMetrics(
                        analysis_count=analysis_count,
                        skill_competencies={
                            "debt_analysis": 0.0,
                            "growth_indicators": 0.0,
                            "value_assessment": 0.0,
                        },
                    )
                    mock_badges.return_value = []  # No earned badges yet

                    earned = self.tracker.check_achievement_conditions(
                        self.sample_context
                    )

                    # Should earn all badges up to this level
                    expected_all = []
                    if analysis_count >= 1:
                        expected_all.append(BadgeType.FIRST_ANALYSIS)
                    if analysis_count >= 10:
                        expected_all.append(BadgeType.BRONZE_ANALYST)
                    if analysis_count >= 50:
                        expected_all.append(BadgeType.SILVER_ANALYST)
                    if analysis_count >= 100:
                        expected_all.append(BadgeType.GOLD_ANALYST)
                    if analysis_count >= 500:
                        expected_all.append(BadgeType.PLATINUM_ANALYST)

                    for badge in expected_all:
                        self.assertIn(badge, earned)

    def test_pattern_recognition_achievement_detection(self):
        """Test detection of pattern recognition achievements"""
        # Test debt detective badge
        with patch.object(
            self.tracker, "_get_progress_metrics"
        ) as mock_progress, patch.object(
            self.tracker, "_get_earned_badges"
        ) as mock_badges:
            mock_progress.return_value = ProgressMetrics(
                skill_competencies={
                    "debt_analysis": 0.85,  # Above threshold
                    "growth_indicators": 0.6,
                    "value_assessment": 0.7,
                }
            )
            mock_badges.return_value = []

            earned = self.tracker.check_achievement_conditions(self.sample_context)
            self.assertIn(BadgeType.DEBT_DETECTIVE, earned)

        # Test growth spotter badge
        with patch.object(
            self.tracker, "_get_progress_metrics"
        ) as mock_progress, patch.object(
            self.tracker, "_get_earned_badges"
        ) as mock_badges:
            mock_progress.return_value = ProgressMetrics(
                skill_competencies={
                    "debt_analysis": 0.6,
                    "growth_indicators": 0.85,  # Above threshold
                    "value_assessment": 0.7,
                }
            )
            mock_badges.return_value = []

            earned = self.tracker.check_achievement_conditions(self.sample_context)
            self.assertIn(BadgeType.GROWTH_SPOTTER, earned)

    def test_pattern_master_badge_requires_all_patterns(self):
        """Test that Pattern Master badge requires all pattern badges"""
        # Mock having two of three pattern badges
        existing_badges = [
            Badge(
                badge_type=BadgeType.DEBT_DETECTIVE,
                earned_timestamp=time.time(),
                context={},
                display_name="Debt Detective",
                description="Test",
                achievement_value=75,
            ),
            Badge(
                badge_type=BadgeType.GROWTH_SPOTTER,
                earned_timestamp=time.time(),
                context={},
                display_name="Growth Spotter",
                description="Test",
                achievement_value=75,
            ),
        ]

        with patch.object(
            self.tracker, "_get_progress_metrics"
        ) as mock_progress, patch.object(
            self.tracker, "_get_earned_badges"
        ) as mock_badges:
            mock_progress.return_value = ProgressMetrics(
                skill_competencies={
                    "debt_analysis": 0.85,
                    "growth_indicators": 0.85,
                    "value_assessment": 0.85,  # All above threshold
                }
            )
            mock_badges.return_value = existing_badges

            earned = self.tracker.check_achievement_conditions(self.sample_context)

            # Should earn Value Hunter and Pattern Master
            self.assertIn(BadgeType.VALUE_HUNTER, earned)
            self.assertIn(BadgeType.PATTERN_MASTER, earned)

    def test_learning_streak_achievement_detection(self):
        """Test detection of learning streak achievements"""
        streak_tests = [
            (7, BadgeType.CONSISTENT_LEARNER),
            (30, BadgeType.DEDICATED_STUDENT),
            (90, BadgeType.LEARNING_CHAMPION),
        ]

        for streak_days, expected_badge in streak_tests:
            with self.subTest(streak_days=streak_days):
                with patch.object(
                    self.tracker, "_get_progress_metrics"
                ) as mock_progress, patch.object(
                    self.tracker, "_get_earned_badges"
                ) as mock_badges:
                    mock_progress.return_value = ProgressMetrics(
                        current_streak=streak_days,
                        skill_competencies={
                            "debt_analysis": 0.0,
                            "growth_indicators": 0.0,
                            "value_assessment": 0.0,
                        },
                    )
                    mock_badges.return_value = []

                    earned = self.tracker.check_achievement_conditions(
                        self.sample_context
                    )
                    self.assertIn(expected_badge, earned)

    def test_badge_award_process(self):
        """Test the badge awarding process"""
        badge_type = BadgeType.FIRST_ANALYSIS

        with patch.object(self.tracker, "_store_badge") as mock_store:
            with patch.object(
                self.tracker, "_update_stage_progression_points"
            ) as mock_points:
                badge = self.tracker.award_badge(badge_type, self.sample_context)

                # Verify badge properties
                self.assertEqual(badge.badge_type, badge_type)
                self.assertEqual(badge.display_name, "First Steps")
                self.assertEqual(
                    badge.description, "Completed your first stock analysis"
                )
                self.assertEqual(badge.achievement_value, 10)
                self.assertIsNotNone(badge.earned_timestamp)

                # Verify storage calls
                mock_store.assert_called_once_with(self.sample_context.user_id, badge)
                mock_points.assert_called_once_with(self.sample_context.user_id, 10)

    def test_progress_metrics_update(self):
        """Test updating progress metrics based on completion data"""
        user_id = "test_user_123"

        # Mock existing progress
        initial_progress = ProgressMetrics(
            analysis_count=5,
            skill_competencies={
                "debt_analysis": 0.5,
                "growth_indicators": 0.6,
                "value_assessment": 0.4,
            },
            current_streak=0,
            best_streak=3,
        )

        completion_data = {
            "analysis_completed": True,
            "skill_improvements": {"debt_analysis": 0.1, "growth_indicators": 0.05},
            "pattern_performance": 0.8,
            "session_duration": 1200,  # 20 minutes
        }

        with patch.object(self.tracker, "_get_progress_metrics") as mock_get:
            mock_get.return_value = initial_progress

            with patch.object(self.tracker, "_store_progress_metrics") as mock_store:
                updated = self.tracker.update_progress_metrics(user_id, completion_data)

                # Verify updates
                self.assertEqual(updated.analysis_count, 6)  # Incremented
                self.assertGreater(updated.skill_competencies["debt_analysis"], 0.5)
                self.assertEqual(updated.total_session_time, 1200)
                self.assertEqual(updated.current_streak, 1)  # New streak started

                mock_store.assert_called_once()

    def test_learning_streak_calculation(self):
        """Test learning streak calculation from session history"""
        user_id = "test_user_123"

        # Create session history with consecutive days
        base_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        session_history = []

        for i in range(5):  # 5 consecutive days
            session_time = base_time - timedelta(days=4 - i)  # Most recent first
            session_history.append(
                {
                    "timestamp": session_time.timestamp(),
                    "duration": 1800,
                    "interactions": 5,
                }
            )

        current_streak, best_streak = self.tracker.calculate_learning_streak(
            user_id, session_history
        )

        self.assertEqual(current_streak, 5)
        self.assertEqual(best_streak, 5)

    def test_learning_streak_with_gaps(self):
        """Test learning streak calculation with gaps in activity"""
        user_id = "test_user_123"

        # Create session history with gaps
        base_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        session_history = []

        # 3 days, then gap, then 2 days
        streak_days = [0, 1, 2, 5, 6]  # Days ago

        for day_offset in streak_days:
            session_time = base_time - timedelta(days=day_offset)
            session_history.append(
                {
                    "timestamp": session_time.timestamp(),
                    "duration": 1800,
                    "interactions": 5,
                }
            )

        current_streak, best_streak = self.tracker.calculate_learning_streak(
            user_id, session_history
        )

        # Current streak should be 3 (most recent consecutive days: 0,1,2)
        # Best streak should be 3 (the longest consecutive period)
        self.assertEqual(current_streak, 3)
        self.assertEqual(best_streak, 3)

    def test_personalized_goals_generation(self):
        """Test generation of personalized learning goals"""
        user_id = "test_user_123"
        stage = LearningStage.ASSISTED_ANALYSIS
        recent_activity = {"analyses_this_week": 3}

        with patch.object(self.tracker, "_get_progress_metrics") as mock_progress:
            mock_progress.return_value = ProgressMetrics(
                analysis_count=15,
                skill_competencies={
                    "debt_analysis": 0.8,
                    "growth_indicators": 0.4,  # Needs improvement
                    "value_assessment": 0.6,
                },
            )

        with patch.object(self.tracker, "_get_earned_badges") as mock_badges:
            mock_badges.return_value = []

        goals = self.tracker.get_personalized_goals(user_id, stage, recent_activity)

        # Verify goal structure
        self.assertIn("daily_target", goals)
        self.assertIn("weekly_focus", goals)
        self.assertIn("skill_priorities", goals)
        self.assertIn("next_badge", goals)
        self.assertIn("encouragement", goals)

        # Check that growth_indicators is prioritized (lowest score)
        self.assertIn("growth_indicators", goals["skill_priorities"])

    def test_achievement_showcase_display_data(self):
        """Test generation of achievement showcase display data"""
        user_id = "test_user_123"

        # Mock earned badges
        sample_badges = [
            Badge(
                badge_type=BadgeType.FIRST_ANALYSIS,
                earned_timestamp=time.time() - 86400,  # Yesterday
                context={},
                display_name="First Steps",
                description="Completed your first stock analysis",
                achievement_value=10,
            ),
            Badge(
                badge_type=BadgeType.DEBT_DETECTIVE,
                earned_timestamp=time.time() - 43200,  # 12 hours ago
                context={},
                display_name="Debt Detective",
                description="Mastered debt analysis patterns",
                achievement_value=75,
            ),
        ]

        sample_progress = ProgressMetrics(
            analysis_count=25,
            current_streak=5,
            best_streak=12,
            total_session_time=18000,  # 5 hours
            skill_competencies={
                "debt_analysis": 0.8,
                "growth_indicators": 0.6,
                "value_assessment": 0.7,
            },
            stage_progression_points=85,
        )

        with patch.object(self.tracker, "_get_earned_badges") as mock_badges:
            mock_badges.return_value = sample_badges

            with patch.object(self.tracker, "_get_progress_metrics") as mock_progress:
                mock_progress.return_value = sample_progress

                with patch.object(self.tracker, "_calculate_days_active") as mock_days:
                    mock_days.return_value = 15

                showcase = self.tracker.display_achievement_showcase(user_id)

                # Verify structure
                self.assertIn("badges", showcase)
                self.assertIn("progress", showcase)
                self.assertIn("statistics", showcase)

                # Check badge categorization
                self.assertIn("analysis_milestones", showcase["badges"])
                self.assertIn("pattern_mastery", showcase["badges"])

                # Verify statistics calculation
                self.assertEqual(showcase["statistics"]["total_badges"], 2)
                self.assertEqual(showcase["statistics"]["total_achievement_points"], 85)


class TestBehavioralAnalyticsGamificationIntegration(unittest.TestCase):
    """Test cases for gamification integration in BehavioralAnalyticsTracker"""

    def setUp(self):
        """Set up test fixtures"""
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create a test client for request context
        self.client = self.app.test_client()

        self.tracker = BehavioralAnalyticsTracker()

        # Mock Flask session
        self.mock_session = {"anonymous_user_id": "test_session_123"}

    def tearDown(self):
        """Clean up test fixtures"""
        self.app_context.pop()

    def test_gamification_processing_on_analysis_completion(self):
        """Test gamification processing when analysis is completed"""
        with self.app.test_request_context():
            # Set up session data in Flask session directly
            from flask import session

            session["anonymous_user_id"] = "test_session_123"

            # Mock gamification methods
            with patch.object(
                self.tracker.gamification, "update_progress_metrics"
            ) as mock_update:
                with patch.object(
                    self.tracker.gamification, "check_achievement_conditions"
                ) as mock_check:
                    with patch.object(
                        self.tracker.gamification, "award_badge"
                    ) as mock_award:
                        mock_check.return_value = [BadgeType.FIRST_ANALYSIS]

                        # Simulate analysis completion
                        self.tracker.track_analysis_completion("AAPL", "comprehensive")

                        # Verify gamification methods were called
                        mock_update.assert_called_once()
                        mock_check.assert_called_once()
                        mock_award.assert_called_once()

    def test_skill_improvement_extraction(self):
        """Test extraction of skill improvements from analysis context"""
        with self.app.test_request_context():
            with patch("src.behavioral_analytics.session") as mock_session:
                mock_session.configure_mock(**self.mock_session)

                context = {"analysis_depth": "comprehensive"}
                improvements = self.tracker._extract_skill_improvements(context)

                # Should have improvements for all skills
                expected_skills = [
                    "debt_analysis",
                    "growth_indicators",
                    "value_assessment",
                ]
                for skill in expected_skills:
                    self.assertIn(skill, improvements)
                    self.assertGreater(improvements[skill], 0)

    def test_community_contribution_quality_calculation(self):
        """Test calculation of community contribution quality scores"""
        with self.app.test_request_context():
            with patch("src.behavioral_analytics.session") as mock_session:
                mock_session.configure_mock(**self.mock_session)

                # Test high-quality contribution
                high_quality_context = {"content_length": 250}
                high_score = self.tracker._calculate_contribution_quality(
                    high_quality_context
                )
                self.assertGreaterEqual(high_score, 0.8)

                # Test medium-quality contribution
                medium_quality_context = {"content_length": 120}
                medium_score = self.tracker._calculate_contribution_quality(
                    medium_quality_context
                )
                self.assertGreaterEqual(medium_score, 0.5)
                self.assertLess(medium_score, 0.8)
        medium_score = self.tracker._calculate_contribution_quality(
            medium_quality_context
        )
        self.assertGreaterEqual(medium_score, 0.5)
        self.assertLess(medium_score, 0.8)

    def test_error_handling_in_gamification_processing(self):
        """Test that gamification errors don't break main tracking"""
        # Mock a gamification error
        with patch.object(
            self.tracker.gamification, "update_progress_metrics"
        ) as mock_update:
            mock_update.side_effect = Exception("Test gamification error")

            # This should not raise an exception
            try:
                self.tracker._process_gamification_achievements(
                    "test_session", InteractionType.ANALYSIS_COMPLETION, 30.0, {}
                )
            except Exception as e:
                self.fail(f"Gamification error should not propagate: {e}")


class TestProgressMetricsDataStructure(unittest.TestCase):
    """Test cases for ProgressMetrics data structure"""

    def test_progress_metrics_initialization(self):
        """Test ProgressMetrics initialization with defaults"""
        metrics = ProgressMetrics()

        self.assertEqual(metrics.analysis_count, 0)
        self.assertEqual(metrics.pattern_recognition_score, 0.0)
        self.assertEqual(metrics.current_streak, 0)
        self.assertEqual(metrics.best_streak, 0)
        self.assertIsNotNone(metrics.skill_competencies)

    def test_progress_metrics_with_custom_values(self):
        """Test ProgressMetrics with custom initialization values"""
        custom_competencies = {
            "debt_analysis": 0.75,
            "growth_indicators": 0.60,
            "value_assessment": 0.85,
        }

        metrics = ProgressMetrics(
            analysis_count=50, current_streak=15, skill_competencies=custom_competencies
        )

        self.assertEqual(metrics.analysis_count, 50)
        self.assertEqual(metrics.current_streak, 15)
        self.assertEqual(metrics.skill_competencies["debt_analysis"], 0.75)


class TestBadgeDataStructure(unittest.TestCase):
    """Test cases for Badge data structure"""

    def test_badge_creation(self):
        """Test Badge creation with all required fields"""
        badge = Badge(
            badge_type=BadgeType.FIRST_ANALYSIS,
            earned_timestamp=time.time(),
            context={"test": "context"},
            display_name="First Steps",
            description="Completed your first stock analysis",
            achievement_value=10,
        )

        self.assertEqual(badge.badge_type, BadgeType.FIRST_ANALYSIS)
        self.assertEqual(badge.display_name, "First Steps")
        self.assertEqual(badge.achievement_value, 10)
        self.assertIsInstance(badge.earned_timestamp, float)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
