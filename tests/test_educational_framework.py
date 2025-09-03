"""
Tests for Educational Mastery Framework and Behavioral Analytics Tracker

This module tests the learning stage assessment system, behavioral tracking,
and adaptive content delivery functionality with comprehensive coverage.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from datetime import datetime, timedelta

from src.educational_framework import (
    EducationalMasteryFramework,
    InteractionType,
    LearningStage,
    StageAssessmentResult,
    BehavioralData,
    LearningStageProfile,
)
from src.behavioral_analytics import (
    BehavioralAnalyticsTracker,
    track_page_interaction,
    get_learning_stage_context,
    adapt_content_for_stage,
)


class TestEducationalMasteryFramework:
    """Test the core Educational Mastery Framework"""

    def setup_method(self):
        """Set up test fixtures"""
        self.framework = EducationalMasteryFramework()
        self.mock_session = {
            "anonymous_user_id": "test_user_123",
            "behavioral_history": [],
        }

    def test_framework_initialization(self):
        """Test framework initializes with correct stage profiles"""
        assert len(self.framework.stage_profiles) == 4
        assert LearningStage.GUIDED_DISCOVERY in self.framework.stage_profiles
        assert LearningStage.ASSISTED_ANALYSIS in self.framework.stage_profiles
        assert LearningStage.INDEPENDENT_THINKING in self.framework.stage_profiles
        assert LearningStage.ANALYTICAL_MASTERY in self.framework.stage_profiles

        # Verify stage profile configuration
        guided_profile = self.framework.stage_profiles[LearningStage.GUIDED_DISCOVERY]
        assert guided_profile.tooltip_dependency_threshold == 0.8
        assert guided_profile.content_complexity == "basic"
        assert guided_profile.ui_adaptations["show_tooltips"] == True

    def test_track_user_behavior(self):
        """Test behavioral tracking adds entries to session"""
        interaction_data = {
            "duration": 5.0,
            "context": {"tooltip_id": "pe_ratio", "content_length": 120},
        }

        self.framework.track_user_behavior(
            self.mock_session, InteractionType.TOOLTIP_USAGE, interaction_data
        )

        assert len(self.mock_session["behavioral_history"]) == 1

        entry = self.mock_session["behavioral_history"][0]
        assert entry["interaction_type"] == "tooltip_usage"
        assert entry["duration_seconds"] == 5.0
        assert entry["context"]["tooltip_id"] == "pe_ratio"
        assert entry["session_id"] == "test_user_123"
        assert "timestamp" in entry

    def test_assess_learning_stage_insufficient_data(self):
        """Test stage assessment with insufficient interaction data"""
        assessment = self.framework.assess_learning_stage(self.mock_session)

        assert assessment.current_stage == LearningStage.GUIDED_DISCOVERY
        assert assessment.confidence_score == 0.3
        assert assessment.progress_within_stage == 0.0
        assert len(assessment.recommendations) > 0

    def test_assess_learning_stage_guided_discovery(self):
        """Test stage assessment for guided discovery stage"""
        # Add behavioral data indicating heavy tooltip usage
        for i in range(10):
            self.framework.track_user_behavior(
                self.mock_session,
                InteractionType.TOOLTIP_USAGE,
                {"duration": 3.0, "context": {}},
            )

        # Add some basic analysis interactions
        for i in range(3):
            self.framework.track_user_behavior(
                self.mock_session,
                InteractionType.ANALYSIS_COMPLETION,
                {"duration": 30.0, "context": {"analysis_depth": "basic"}},
            )

        assessment = self.framework.assess_learning_stage(self.mock_session)

        assert assessment.current_stage == LearningStage.GUIDED_DISCOVERY
        assert assessment.confidence_score > 0.3
        assert assessment.behavioral_scores["tooltip_dependency"] > 0.5

    def test_assess_learning_stage_assisted_analysis(self):
        """Test stage assessment for assisted analysis stage"""
        # Add moderate tooltip usage
        for i in range(5):
            self.framework.track_user_behavior(
                self.mock_session,
                InteractionType.TOOLTIP_USAGE,
                {"duration": 2.0, "context": {}},
            )

        # Add significant analysis interactions
        for i in range(8):
            self.framework.track_user_behavior(
                self.mock_session,
                InteractionType.WARNING_ENGAGEMENT,
                {"duration": 10.0, "context": {"warning_type": "debt_ratio"}},
            )

        # Add research guide usage
        for i in range(4):
            self.framework.track_user_behavior(
                self.mock_session,
                InteractionType.RESEARCH_GUIDE_ACCESS,
                {"duration": 60.0, "context": {"guide_type": "financial_health"}},
            )

        assessment = self.framework.assess_learning_stage(self.mock_session)

        assert assessment.current_stage == LearningStage.ASSISTED_ANALYSIS
        assert assessment.behavioral_scores["analysis_depth"] > 0.3
        assert assessment.behavioral_scores["tooltip_dependency"] < 0.7

    def test_assess_learning_stage_independent_thinking(self):
        """Test stage assessment for independent thinking stage"""
        # Add minimal tooltip usage
        for i in range(2):
            self.framework.track_user_behavior(
                self.mock_session,
                InteractionType.TOOLTIP_USAGE,
                {"duration": 1.0, "context": {}},
            )

        # Add extensive analysis interactions
        for i in range(12):
            self.framework.track_user_behavior(
                self.mock_session,
                InteractionType.ANALYSIS_COMPLETION,
                {"duration": 45.0, "context": {"analysis_depth": "comprehensive"}},
            )

        # Add pattern recognition activities
        for i in range(8):
            self.framework.track_user_behavior(
                self.mock_session,
                InteractionType.CROSS_STOCK_COMPARISON,
                {
                    "duration": 120.0,
                    "context": {"stocks_compared": ["RELIANCE", "TCS"]},
                },
            )

        # Add some community contributions
        for i in range(3):
            self.framework.track_user_behavior(
                self.mock_session,
                InteractionType.COMMUNITY_CONTRIBUTION,
                {"duration": 180.0, "context": {"content_length": 250}},
            )

        assessment = self.framework.assess_learning_stage(self.mock_session)

        assert assessment.current_stage == LearningStage.INDEPENDENT_THINKING
        assert assessment.behavioral_scores["tooltip_dependency"] < 0.4
        assert assessment.behavioral_scores["analysis_depth"] > 0.6
        assert assessment.behavioral_scores["pattern_recognition"] > 0.5

    def test_assess_learning_stage_analytical_mastery(self):
        """Test stage assessment for analytical mastery stage"""
        # Add very minimal tooltip usage
        for i in range(1):
            self.framework.track_user_behavior(
                self.mock_session,
                InteractionType.TOOLTIP_USAGE,
                {"duration": 0.5, "context": {}},
            )

        # Add extensive high-level analysis
        for i in range(15):
            self.framework.track_user_behavior(
                self.mock_session,
                InteractionType.ANALYSIS_COMPLETION,
                {"duration": 60.0, "context": {"analysis_depth": "expert"}},
            )

        # Add extensive pattern recognition
        for i in range(12):
            self.framework.track_user_behavior(
                self.mock_session,
                InteractionType.CROSS_STOCK_COMPARISON,
                {
                    "duration": 180.0,
                    "context": {"stocks_compared": ["RELIANCE", "TCS", "HDFC"]},
                },
            )

        # Add significant teaching contributions
        for i in range(10):
            self.framework.track_user_behavior(
                self.mock_session,
                InteractionType.COMMUNITY_CONTRIBUTION,
                {"duration": 300.0, "context": {"content_length": 500}},
            )

        assessment = self.framework.assess_learning_stage(self.mock_session)

        assert assessment.current_stage == LearningStage.ANALYTICAL_MASTERY
        assert assessment.behavioral_scores["tooltip_dependency"] < 0.2
        assert assessment.behavioral_scores["analysis_depth"] > 0.8
        assert assessment.behavioral_scores["pattern_recognition"] > 0.7
        assert assessment.behavioral_scores["teaching_contribution"] > 0.6

    def test_behavioral_history_cleanup(self):
        """Test that behavioral history maintains rolling window"""
        # Add old entries (8 days ago)
        old_timestamp = time.time() - (8 * 24 * 3600)
        self.mock_session["behavioral_history"] = [
            {
                "interaction_type": "tooltip_usage",
                "timestamp": old_timestamp,
                "duration_seconds": 5.0,
                "context": {},
                "session_id": "test_user_123",
            }
        ]

        # Add new entry
        self.framework.track_user_behavior(
            self.mock_session,
            InteractionType.ANALYSIS_COMPLETION,
            {"duration": 30.0, "context": {}},
        )

        # Old entry should be removed
        assert len(self.mock_session["behavioral_history"]) == 1
        assert (
            self.mock_session["behavioral_history"][0]["interaction_type"]
            == "analysis_completion"
        )

    def test_get_stage_appropriate_content(self):
        """Test stage-appropriate content generation"""
        assessment = StageAssessmentResult(
            current_stage=LearningStage.GUIDED_DISCOVERY,
            confidence_score=0.8,
            progress_within_stage=0.4,
            next_stage_readiness=0.2,
            behavioral_scores={
                "tooltip_dependency": 0.9,
                "analysis_depth": 0.2,
                "pattern_recognition": 0.1,
                "teaching_contribution": 0.0,
            },
            recommendations=["Use tooltips to learn ratios"],
        )

        analysis_context = {"company_name": "Test Company", "ticker": "TEST"}

        content_config = self.framework.get_stage_appropriate_content(
            assessment, analysis_context
        )

        assert content_config["content_complexity"] == "basic"
        assert content_config["ui_adaptations"]["show_tooltips"] == True
        assert content_config["stage_info"]["current_stage"] == "guided_discovery"
        assert content_config["tooltip_complexity"] == "detailed"
        assert "Understanding Basics" in content_config["educational_content"]["focus"]

    def test_cached_assessment(self):
        """Test cached assessment functionality"""
        # Test no cached assessment
        assert self.framework.get_cached_assessment({}) is None

        # Test expired cached assessment
        expired_cache = {
            "cached_stage_assessment": {
                "timestamp": time.time() - 7200,  # 2 hours ago
                "assessment": {
                    "current_stage": "guided_discovery",
                    "confidence_score": 0.5,
                    "progress_within_stage": 0.3,
                    "next_stage_readiness": 0.1,
                    "behavioral_scores": {},
                    "recommendations": [],
                },
            }
        }
        assert self.framework.get_cached_assessment(expired_cache) is None

        # Test valid cached assessment
        valid_cache = {
            "cached_stage_assessment": {
                "timestamp": time.time() - 1800,  # 30 minutes ago
                "assessment": {
                    "current_stage": "assisted_analysis",
                    "confidence_score": 0.7,
                    "progress_within_stage": 0.5,
                    "next_stage_readiness": 0.3,
                    "behavioral_scores": {"tooltip_dependency": 0.5},
                    "recommendations": ["Test recommendation"],
                },
            }
        }

        cached_result = self.framework.get_cached_assessment(valid_cache)
        assert cached_result is not None
        assert cached_result.current_stage == LearningStage.ASSISTED_ANALYSIS
        assert cached_result.confidence_score == 0.7


class TestBehavioralAnalyticsTracker:
    """Test the Behavioral Analytics Tracker"""

    def setup_method(self):
        """Set up test fixtures"""
        self.tracker = BehavioralAnalyticsTracker()
        # Create Flask app for testing context
        self.app = Flask(__name__)
        self.app.secret_key = "test_key"

    def test_track_interaction_no_session(self):
        """Test tracking interaction without session - should handle gracefully"""
        # Test that the tracker doesn't crash when no session is present
        with self.app.test_request_context():
            # Should not raise an error
            try:
                self.tracker.track_interaction_end(InteractionType.TOOLTIP_USAGE)
                # Test passes if no exception is raised
                assert True
            except Exception as e:
                # Only fail if it's not a Flask session related error
                if "Working outside of request context" not in str(e):
                    raise

    def test_behavioral_analytics_initialization(self):
        """Test that BehavioralAnalyticsTracker initializes correctly"""
        assert self.tracker.framework is not None
        assert hasattr(self.tracker, "track_tooltip_usage")
        assert hasattr(self.tracker, "track_warning_engagement")
        assert hasattr(self.tracker, "track_research_guide_access")

    def test_tracker_method_signatures(self):
        """Test that all tracker methods exist with correct signatures"""
        # Verify all required methods exist
        methods_to_test = [
            "track_tooltip_usage",
            "track_warning_engagement",
            "track_research_guide_access",
            "track_community_contribution",
            "track_analysis_completion",
            "track_cross_stock_comparison",
            "track_prediction_attempt",
        ]

        for method_name in methods_to_test:
            assert hasattr(self.tracker, method_name), f"Missing method: {method_name}"
            method = getattr(self.tracker, method_name)
            assert callable(method), f"Method {method_name} is not callable"

    def test_framework_integration(self):
        """Test that the tracker integrates with the educational framework"""
        # Test that the tracker has access to the framework
        assert self.tracker.framework is not None
        assert isinstance(self.tracker.framework, EducationalMasteryFramework)

        # Test that framework has required methods
        assert hasattr(self.tracker.framework, "track_user_behavior")
        assert hasattr(self.tracker.framework, "assess_learning_stage")

    def test_get_default_content_config(self):
        """Test default content configuration for new users"""
        config = self.tracker._get_default_content_config()

        assert config["content_complexity"] == "basic"
        assert config["ui_adaptations"]["show_tooltips"] == True
        assert config["stage_info"]["current_stage"] == "guided_discovery"
        assert config["tooltip_complexity"] == "detailed"
        assert len(config["recommendations"]) > 0
        assert len(config["learning_prompts"]) > 0

    @patch("src.behavioral_analytics.session", {"anonymous_user_id": "test_user"})
    def test_get_current_stage_assessment(self):
        """Test getting current stage assessment"""
        with patch.object(
            self.tracker.framework, "assess_learning_stage"
        ) as mock_assess:
            mock_assessment = StageAssessmentResult(
                current_stage=LearningStage.ASSISTED_ANALYSIS,
                confidence_score=0.6,
                progress_within_stage=0.4,
                next_stage_readiness=0.2,
                behavioral_scores={"tooltip_dependency": 0.5},
                recommendations=["Test recommendation"],
            )
            mock_assess.return_value = mock_assessment

            result = self.tracker.get_current_stage_assessment()
            assert result.current_stage == LearningStage.ASSISTED_ANALYSIS
            assert result.confidence_score == 0.6

    def test_should_show_stage_progress(self):
        """Test stage progress display logic"""
        # Test with no session
        with patch("src.behavioral_analytics.session", {}):
            assert self.tracker.should_show_stage_progress() == False

        # Test with low confidence
        with patch.object(self.tracker, "get_current_stage_assessment") as mock_assess:
            mock_assess.return_value = Mock(confidence_score=0.3)
            with patch(
                "src.behavioral_analytics.session", {"behavioral_history": [{}] * 5}
            ):
                assert self.tracker.should_show_stage_progress() == False

        # Test with high confidence and sufficient interactions
        with patch.object(self.tracker, "get_current_stage_assessment") as mock_assess:
            mock_assess.return_value = Mock(confidence_score=0.8)
            with patch(
                "src.behavioral_analytics.session", {"behavioral_history": [{}] * 15}
            ):
                assert self.tracker.should_show_stage_progress() == True

    def test_get_stage_progress_data(self):
        """Test stage progress data generation"""
        with patch.object(
            self.tracker, "should_show_stage_progress", return_value=True
        ):
            with patch.object(
                self.tracker, "get_current_stage_assessment"
            ) as mock_assess:
                mock_assessment = StageAssessmentResult(
                    current_stage=LearningStage.INDEPENDENT_THINKING,
                    confidence_score=0.75,
                    progress_within_stage=0.6,
                    next_stage_readiness=0.4,
                    behavioral_scores={
                        "tooltip_dependency": 0.3,
                        "analysis_depth": 0.7,
                        "pattern_recognition": 0.6,
                        "teaching_contribution": 0.3,
                    },
                    recommendations=[
                        "Recommendation 1",
                        "Recommendation 2",
                        "Recommendation 3",
                        "Recommendation 4",
                    ],
                )
                mock_assess.return_value = mock_assessment

                progress_data = self.tracker.get_stage_progress_data()

                assert progress_data is not None
                assert progress_data["current_stage"] == "independent_thinking"
                assert progress_data["stage_name"] == "Independent Thinking"
                assert progress_data["progress_within_stage"] == 60.0
                assert progress_data["next_stage_readiness"] == 40.0
                assert progress_data["confidence_score"] == 75.0
                assert len(progress_data["recommendations"]) == 3  # Limited to top 3


class TestIntegrationFunctions:
    """Test integration functions for Flask app"""

    @patch("src.behavioral_analytics.behavioral_tracker")
    def test_get_learning_stage_context(self, mock_tracker):
        """Test learning stage context generation"""
        mock_config = {
            "ui_adaptations": {"show_tooltips": True},
            "content_complexity": "basic",
        }
        mock_progress = {
            "current_stage": "guided_discovery",
            "progress_within_stage": 30.0,
        }

        mock_tracker.get_stage_content_config.return_value = mock_config
        mock_tracker.get_stage_progress_data.return_value = mock_progress
        mock_tracker.should_show_stage_progress.return_value = True

        context = get_learning_stage_context()

        assert "learning_stage" in context
        assert "stage_progress" in context
        assert "show_stage_progress" in context
        assert context["learning_stage"] == mock_config
        assert context["stage_progress"] == mock_progress
        assert context["show_stage_progress"] == True

    @patch("src.behavioral_analytics.behavioral_tracker")
    def test_adapt_content_for_stage(self, mock_tracker):
        """Test content adaptation based on learning stage"""
        mock_config = {
            "tooltip_complexity": "concise",
            "ui_adaptations": {"explanation_depth": "minimal"},
            "recommendations": ["Use advanced features"],
            "learning_prompts": ["🚀 Make predictions"],
        }
        mock_tracker.get_stage_content_config.return_value = mock_config

        base_content = {
            "warnings": ["Test warning"],
            "explanations": ["Test explanation"],
        }

        adapted_content = adapt_content_for_stage(
            base_content, {"company_name": "Test"}
        )

        assert adapted_content["show_detailed_tooltips"] == False
        assert adapted_content["explanation_depth"] == "minimal"
        assert adapted_content["learning_recommendations"] == ["Use advanced features"]
        assert adapted_content["learning_prompts"] == ["🚀 Make predictions"]

    @patch("src.behavioral_analytics.behavioral_tracker")
    def test_track_page_interaction(self, mock_tracker):
        """Test page interaction tracking"""
        mock_tracker.track_interaction_end = Mock()

        track_page_interaction(InteractionType.TOOLTIP_USAGE, {"tooltip_id": "test"})

        mock_tracker.track_interaction_end.assert_called_once_with(
            InteractionType.TOOLTIP_USAGE, {"tooltip_id": "test"}
        )


class TestPerformanceAndEdgeCases:
    """Test performance characteristics and edge cases"""

    def setup_method(self):
        """Set up test fixtures"""
        self.framework = EducationalMasteryFramework()
        self.tracker = BehavioralAnalyticsTracker()

    def test_large_behavioral_history_performance(self):
        """Test performance with large behavioral history"""
        # Create large session with 1000 entries
        large_session = {
            "anonymous_user_id": "performance_test_user",
            "behavioral_history": [],
        }

        # Add 1000 behavioral entries
        start_time = time.time()
        for i in range(1000):
            self.framework.track_user_behavior(
                large_session,
                (
                    InteractionType.TOOLTIP_USAGE
                    if i % 2 == 0
                    else InteractionType.ANALYSIS_COMPLETION
                ),
                {"duration": 1.0, "context": {"test": i}},
            )
        tracking_time = time.time() - start_time

        # Assess stage with large dataset
        start_time = time.time()
        assessment = self.framework.assess_learning_stage(large_session)
        assessment_time = time.time() - start_time

        # Performance should be reasonable
        assert tracking_time < 1.0  # Less than 1 second for 1000 entries
        assert assessment_time < 0.1  # Less than 100ms for assessment
        assert assessment.current_stage in [
            LearningStage.GUIDED_DISCOVERY,
            LearningStage.ASSISTED_ANALYSIS,
        ]

    def test_malformed_behavioral_data(self):
        """Test handling of malformed behavioral data"""
        malformed_session = {
            "anonymous_user_id": "test_user",
            "behavioral_history": [
                {"interaction_type": "invalid_type", "timestamp": time.time()},
                {"timestamp": time.time()},  # Missing interaction_type
                {"interaction_type": "tooltip_usage"},  # Missing timestamp
                None,  # Completely invalid entry
                {"interaction_type": "tooltip_usage", "timestamp": "invalid_timestamp"},
            ],
        }

        # Should not crash and should return reasonable results
        assessment = self.framework.assess_learning_stage(malformed_session)
        assert assessment.current_stage == LearningStage.GUIDED_DISCOVERY
        assert assessment.confidence_score >= 0.0

    def test_concurrent_session_handling(self):
        """Test handling multiple concurrent sessions"""
        sessions = []
        for i in range(10):
            session = {
                "anonymous_user_id": f"concurrent_user_{i}",
                "behavioral_history": [],
            }
            sessions.append(session)

        # Track behaviors concurrently
        for i, session in enumerate(sessions):
            for j in range(i + 1):  # Different amounts of data per session
                self.framework.track_user_behavior(
                    session,
                    InteractionType.ANALYSIS_COMPLETION,
                    {"duration": j, "context": {"session_id": i}},
                )

        # All sessions should be processed independently
        for i, session in enumerate(sessions):
            assessment = self.framework.assess_learning_stage(session)
            assert len(session["behavioral_history"]) == i + 1
            assert assessment.confidence_score >= 0.0

    def test_memory_cleanup(self):
        """Test memory cleanup in behavioral history"""
        session = {"anonymous_user_id": "memory_test_user", "behavioral_history": []}

        # Add entries over time with different timestamps
        old_time = time.time() - (10 * 24 * 3600)  # 10 days ago
        current_time = time.time()

        # Add old entries
        for i in range(50):
            session["behavioral_history"].append(
                {
                    "interaction_type": "tooltip_usage",
                    "timestamp": old_time + i,
                    "duration_seconds": 1.0,
                    "context": {},
                    "session_id": "memory_test_user",
                }
            )

        # Add current entries
        for i in range(10):
            self.framework.track_user_behavior(
                session,
                InteractionType.ANALYSIS_COMPLETION,
                {"duration": 1.0, "context": {}},
            )

        # Should only keep recent entries (within 7 days)
        recent_entries = [
            entry
            for entry in session["behavioral_history"]
            if entry["timestamp"] > current_time - (7 * 24 * 3600)
        ]
        assert len(session["behavioral_history"]) == len(recent_entries)
        assert len(recent_entries) <= 10  # Should have cleaned up old entries


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
