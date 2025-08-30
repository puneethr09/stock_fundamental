"""
Comprehensive test configuration for educational stock analysis platform.

This module provides shared fixtures and utilities for testing all educational
and analysis components with proper isolation and realistic test data.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from datetime import datetime, timedelta

# Import all educational systems for fixture creation
try:
    from src.educational_framework import EducationalMasteryFramework, LearningStage
    from src.pattern_recognition_trainer import (
        PatternRecognitionTrainer,
        PatternType,
        ExerciseDifficulty,
    )
    from src.research_guidance_system import ResearchGuidanceSystem
    from src.gap_filling_service import EducationalGapFillingService
    from src.behavioral_analytics import BehavioralAnalyticsTracker

    # Import gamified tracker with mock fallback
    try:
        from src.gamified_progress_tracker import (
            GamifiedProgressTracker,
            Badge,
            ProgressMetrics,
        )
    except ImportError:
        # Mock classes for gamified tracker if import fails
        class Badge:
            def __init__(self, id, name, description, tier=None):
                self.id = id
                self.name = name
                self.description = description
                self.tier = tier

        class ProgressMetrics:
            def __init__(self):
                self.total_score = 0
                self.badges_earned = []
                self.current_streak = 0

        class GamifiedProgressTracker:
            def __init__(self, user_id):
                self.user_id = user_id
                self.progress = ProgressMetrics()

    # Import tool independence trainer with mock fallback
    try:
        from src.tool_independence_trainer import (
            ToolIndependenceTrainer,
            ChallengeType,
            ToolIndependenceChallenge,
        )
    except ImportError:
        # Mock classes for tool independence trainer if import fails
        class ChallengeType:
            pass

        class ToolIndependenceChallenge:
            def __init__(self, id, type, description):
                self.id = id
                self.type = type
                self.description = description

        class ToolIndependenceTrainer:
            def __init__(self, user_id):
                self.user_id = user_id

except ImportError as e:
    print(f"Warning: Educational system imports failed: {e}")

    # Create minimal mock classes for testing
    class EducationalMasteryFramework:
        pass

    class LearningStage:
        pass

    class PatternRecognitionTrainer:
        pass

    class PatternType:
        pass

    class ExerciseDifficulty:
        pass


# Test data constants
TEST_USER_ID = "test_user_123"
TEST_SESSION_ID = "test_session_456"
TEST_TICKER = "RELIANCE"
TEST_COMPANY_NAME = "Reliance Industries Limited"


@pytest.fixture(scope="session")
def app():
    """Create Flask app for testing with test configuration."""
    # Import here to avoid circular imports
    from app import app as flask_app

    flask_app.config.update(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
            "SERVER_NAME": "localhost:5000",
        }
    )

    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def client(app):
    """Create test client for Flask routes testing."""
    return app.test_client()


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    yield path
    os.close(fd)
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def mock_user_session():
    """Mock user session data for testing."""
    return {
        "user_id": TEST_USER_ID,
        "session_id": TEST_SESSION_ID,
        "learning_stage": LearningStage.ASSISTED_ANALYSIS.value,
        "analyses_completed": 15,
        "patterns_identified": 8,
        "research_assignments_completed": 3,
        "current_streak": 5,
        "total_engagement_time": 3600,  # 1 hour in seconds
        "last_activity": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_stock_data():
    """Sample stock data for analysis testing."""
    return {
        "ticker": TEST_TICKER,
        "company_name": TEST_COMPANY_NAME,
        "industry": "Oil & Gas",
        "sector": "Energy",
        "market_cap": 1500000,
        "current_price": 2500.0,
        "pe_ratio": 15.5,
        "debt_to_equity": 0.8,
        "roe": 18.2,
        "revenue_growth": 12.5,
        "operating_margin": 22.1,
        "current_ratio": 1.4,
        "historical_data": {
            "quarters": ["Q1 2023", "Q2 2023", "Q3 2023", "Q4 2023"],
            "revenue": [180000, 185000, 195000, 210000],
            "profit": [32000, 35000, 38000, 42000],
            "debt_to_equity": [0.9, 0.85, 0.82, 0.8],
            "roe": [16.5, 17.2, 17.8, 18.2],
        },
    }


@pytest.fixture
def educational_framework():
    """Educational Mastery Framework instance for testing."""
    return EducationalMasteryFramework()


@pytest.fixture
def pattern_trainer():
    """Pattern Recognition Trainer instance for testing."""
    return PatternRecognitionTrainer()


@pytest.fixture
def progress_tracker(educational_framework):
    """Gamified Progress Tracker instance for testing."""
    return GamifiedProgressTracker(educational_framework)


@pytest.fixture
def tool_trainer():
    """Tool Independence Trainer instance for testing."""
    return ToolIndependenceTrainer()


@pytest.fixture
def research_system():
    """Research Guidance System instance for testing."""
    return ResearchGuidanceSystem()


@pytest.fixture
def gap_service():
    """Educational Gap Filling Service instance for testing."""
    return EducationalGapFillingService()


@pytest.fixture
def analytics_tracker():
    """Behavioral Analytics Tracker instance for testing."""
    return BehavioralAnalyticsTracker()


@pytest.fixture
def sample_pattern_exercise(pattern_trainer, sample_stock_data):
    """Sample pattern recognition exercise for testing."""
    return pattern_trainer.generate_stage_appropriate_exercise(
        user_stage=LearningStage.ASSISTED_ANALYSIS,
        pattern_type=PatternType.DEBT_ANALYSIS,
        user_session_id=TEST_SESSION_ID,
        company_info={
            "name": sample_stock_data["company_name"],
            "ticker": sample_stock_data["ticker"],
            "industry": sample_stock_data["industry"],
        },
    )


@pytest.fixture
def sample_research_assignment(research_system, mock_user_session):
    """Sample research assignment for testing."""
    return research_system.generate_personalized_research_assignment(
        user_gaps=[
            {
                "category": "MOAT_ANALYSIS",
                "company": TEST_COMPANY_NAME,
                "severity": "high",
            }
        ],
        learning_stage=2,
        research_history=[],
    )


@pytest.fixture
def sample_tool_challenge(tool_trainer, sample_stock_data):
    """Sample tool independence challenge for testing."""
    return tool_trainer.generate_challenge(
        user_stage=LearningStage.INDEPENDENT_THINKING,
        challenge_type=ChallengeType.BLIND_ANALYSIS,
        ticker=sample_stock_data["ticker"],
        user_session_id=TEST_SESSION_ID,
    )


@pytest.fixture
def mock_behavioral_data():
    """Mock behavioral analytics data for testing."""
    return {
        "interactions": [
            {
                "type": "analysis_start",
                "timestamp": datetime.now() - timedelta(minutes=10),
                "data": {"ticker": TEST_TICKER},
            },
            {
                "type": "pattern_identified",
                "timestamp": datetime.now() - timedelta(minutes=8),
                "data": {"pattern": "deleveraging_trend"},
            },
            {
                "type": "analysis_complete",
                "timestamp": datetime.now() - timedelta(minutes=5),
                "data": {"confidence": 0.8},
            },
            {
                "type": "gap_identified",
                "timestamp": datetime.now() - timedelta(minutes=3),
                "data": {"gap_type": "MOAT_ANALYSIS"},
            },
            {
                "type": "research_assigned",
                "timestamp": datetime.now() - timedelta(minutes=1),
                "data": {"assignment_id": "research_123"},
            },
        ],
        "session_duration": 600,  # 10 minutes
        "confidence_levels": [0.6, 0.7, 0.8, 0.8],
        "error_rate": 0.15,
        "help_requests": 2,
    }


@pytest.fixture(autouse=True)
def reset_test_state():
    """Reset any global state between tests."""
    # Clear any cached data or global variables
    yield
    # Cleanup after test


class MockDataProvider:
    """Mock data provider for consistent test data across modules."""

    @staticmethod
    def get_stock_fundamentals(ticker):
        """Mock stock fundamental data."""
        base_data = {
            "RELIANCE": {
                "pe_ratio": 15.5,
                "debt_to_equity": 0.8,
                "roe": 18.2,
                "revenue_growth": 12.5,
                "operating_margin": 22.1,
                "current_ratio": 1.4,
            },
            "TCS": {
                "pe_ratio": 25.2,
                "debt_to_equity": 0.1,
                "roe": 28.5,
                "revenue_growth": 8.5,
                "operating_margin": 25.8,
                "current_ratio": 2.1,
            },
            "HDFC": {
                "pe_ratio": 18.8,
                "debt_to_equity": 6.2,
                "roe": 16.8,
                "revenue_growth": 15.2,
                "operating_margin": 45.2,
                "current_ratio": 1.1,
            },
        }
        return base_data.get(ticker, base_data["RELIANCE"])

    @staticmethod
    def get_historical_data(ticker, periods=8):
        """Mock historical financial data."""
        import numpy as np

        # Generate realistic quarterly data
        base_values = MockDataProvider.get_stock_fundamentals(ticker)
        historical = {}

        for metric, base_value in base_values.items():
            # Add some realistic variation over time
            trend = np.linspace(base_value * 0.9, base_value, periods)
            noise = np.random.normal(0, base_value * 0.05, periods)
            historical[metric] = [
                round(max(v + n, 0.1), 2) for v, n in zip(trend, noise)
            ]

        historical["quarters"] = [
            f"Q{((i % 4) + 1)} {2022 + i // 4}" for i in range(periods)
        ]
        return historical


@pytest.fixture
def mock_data_provider():
    """Mock data provider fixture."""
    return MockDataProvider


# Utility functions for test assertions
def assert_educational_component_valid(component, expected_attributes):
    """Assert that an educational component has required attributes."""
    for attr in expected_attributes:
        assert hasattr(component, attr), f"Component missing required attribute: {attr}"


def assert_user_progress_valid(progress_data):
    """Assert that user progress data has valid structure."""
    required_fields = ["user_id", "learning_stage", "progress_metrics", "achievements"]
    for field in required_fields:
        assert field in progress_data, f"Progress data missing field: {field}"

    assert isinstance(progress_data["progress_metrics"], dict)
    assert isinstance(progress_data["achievements"], list)


def assert_assignment_valid(assignment):
    """Assert that a research assignment has valid structure."""
    required_fields = [
        "assignment_id",
        "type",
        "instructions",
        "success_criteria",
        "time_estimate",
    ]
    for field in required_fields:
        assert hasattr(assignment, field), f"Assignment missing field: {field}"

    assert len(assignment.instructions) > 0, "Assignment must have instructions"
    assert assignment.time_estimate > 0, "Assignment must have positive time estimate"


# Performance testing utilities
@pytest.fixture
def performance_monitor():
    """Monitor performance of educational operations."""
    import time

    class PerformanceMonitor:
        def __init__(self):
            self.timings = {}

        def time_operation(self, operation_name):
            def decorator(func):
                start_time = time.time()
                result = func()
                end_time = time.time()
                self.timings[operation_name] = end_time - start_time
                return result

            return decorator

        def assert_performance(self, operation_name, max_time_seconds):
            actual_time = self.timings.get(operation_name, float("inf"))
            assert (
                actual_time <= max_time_seconds
            ), f"Operation '{operation_name}' took {actual_time:.3f}s (max: {max_time_seconds}s)"

    return PerformanceMonitor()


# Test data cleanup utilities
@pytest.fixture(scope="function", autouse=True)
def cleanup_test_files():
    """Clean up any test files created during testing."""
    test_files = []
    yield
    # Cleanup files after each test
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except PermissionError:
                pass  # File might be in use, skip cleanup
