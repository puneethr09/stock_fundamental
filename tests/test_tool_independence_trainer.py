"""
Test suite for Tool Independence Trainer system
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from tool_independence_trainer import (
    ToolIndependenceTrainer,
    ChallengeType,
    ToolIndependenceChallenge,
    ChallengeResult,
    PredictionCategory,
    UserPrediction,
)

# Import from src.educational_framework like the trainer does
from src.educational_framework import LearningStage


class TestToolIndependenceTrainer:

    def setup_method(self):
        """Setup test instance"""
        self.trainer = ToolIndependenceTrainer()
        self.test_session_id = "test_user_123"
        self.test_ticker = "RELIANCE"

    def test_trainer_initialization(self):
        """Test that ToolIndependenceTrainer initializes correctly"""
        trainer = ToolIndependenceTrainer()
        assert trainer is not None
        assert hasattr(trainer, "challenge_history")
        assert hasattr(trainer, "performance_history")
        assert hasattr(trainer, "confidence_progression")
        assert hasattr(trainer, "challenge_templates")
        assert hasattr(trainer, "educational_framework")

    def test_challenge_generation_guided_discovery(self):
        """Test challenge generation for guided discovery stage"""
        challenge = self.trainer.generate_stage_appropriate_challenge(
            self.test_session_id, LearningStage.GUIDED_DISCOVERY, self.test_ticker
        )

        assert isinstance(challenge, ToolIndependenceChallenge)
        assert challenge.challenge_id is not None
        assert challenge.company_symbol == self.test_ticker
        assert challenge.difficulty_level == 1
        assert len(challenge.prediction_prompts) > 0

    def test_challenge_generation_assisted_analysis(self):
        """Test challenge generation for assisted analysis stage"""
        challenge = self.trainer.generate_stage_appropriate_challenge(
            self.test_session_id, LearningStage.ASSISTED_ANALYSIS, self.test_ticker
        )

        assert isinstance(challenge, ToolIndependenceChallenge)
        assert challenge.difficulty_level == 2
        assert challenge.company_symbol == self.test_ticker

    def test_challenge_generation_independent_thinking(self):
        """Test challenge generation for independent thinking stage"""
        challenge = self.trainer.generate_stage_appropriate_challenge(
            self.test_session_id, LearningStage.INDEPENDENT_THINKING, self.test_ticker
        )

        assert isinstance(challenge, ToolIndependenceChallenge)
        assert challenge.difficulty_level == 3
        assert challenge.company_symbol == self.test_ticker

    def test_challenge_generation_analytical_mastery(self):
        """Test challenge generation for analytical mastery stage"""
        challenge = self.trainer.generate_stage_appropriate_challenge(
            self.test_session_id, LearningStage.ANALYTICAL_MASTERY, self.test_ticker
        )

        assert isinstance(challenge, ToolIndependenceChallenge)
        assert challenge.difficulty_level == 4
        assert challenge.company_symbol == self.test_ticker

    def test_challenge_generation_with_company_dict(self):
        """Test challenge generation with company data as dictionary"""
        company_data = {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"}

        challenge = self.trainer.generate_stage_appropriate_challenge(
            self.test_session_id, LearningStage.GUIDED_DISCOVERY, company_data
        )

        assert isinstance(challenge, ToolIndependenceChallenge)
        assert challenge.company_symbol == "AAPL"

    def test_challenge_types_exist(self):
        """Test that all challenge types are properly defined"""
        for challenge_type in ChallengeType:
            assert challenge_type is not None

    def test_prediction_evaluation_basic(self):
        """Test basic prediction evaluation functionality"""
        # Generate a challenge first
        challenge = self.trainer.generate_stage_appropriate_challenge(
            self.test_session_id, LearningStage.GUIDED_DISCOVERY, self.test_ticker
        )

        # Create sample prediction data (matching Flask form data)
        prediction_data = {
            "ticker": self.test_ticker,
            "challenge_id": challenge.challenge_id,
            "financial_health": "good",
            "growth_potential": "moderate",
            "risk_factors": "low",
            "investment_decision": "buy",
            "reasoning": "Test reasoning",
            "confidence_level": 3,
        }

        # Evaluate prediction
        result = self.trainer.evaluate_prediction_accuracy(
            self.test_session_id, prediction_data
        )

        assert isinstance(result, dict)
        assert "overall_accuracy" in result
        assert "prediction_breakdown" in result
        assert "learning_insights" in result

    def test_analytical_confidence_tracking(self):
        """Test analytical confidence progress tracking"""
        # Create sample evaluation result
        sample_result = {
            "overall_accuracy": 0.75,
            "prediction_breakdown": {
                "financial_health": {"accuracy": 0.8},
                "growth_potential": {"accuracy": 0.7},
            },
            "confidence_level": 3,
        }

        # Track progress
        progress = self.trainer.track_analytical_confidence_progress(
            self.test_session_id, sample_result
        )

        # Verify progress was tracked
        assert isinstance(progress, dict)
        assert "current_confidence" in progress
        assert self.test_session_id in self.trainer.confidence_progression

    def test_difficulty_adaptation(self):
        """Test that challenge difficulty adapts based on performance"""
        # Simulate multiple challenges with good performance
        for i in range(3):
            challenge = self.trainer.generate_stage_appropriate_challenge(
                self.test_session_id, LearningStage.GUIDED_DISCOVERY, f"TEST{i}"
            )

            # Simulate high-accuracy evaluation
            sample_result = {
                "overall_accuracy": 0.9,
                "prediction_breakdown": {},
                "confidence_level": 4,
            }

            self.trainer.track_analytical_confidence_progress(
                self.test_session_id, sample_result
            )

        # Check that progress was tracked
        assert self.test_session_id in self.trainer.confidence_progression
        assert len(self.trainer.confidence_progression[self.test_session_id]) == 3

    def test_challenge_id_uniqueness(self):
        """Test that challenge IDs are unique"""
        challenge1 = self.trainer.generate_stage_appropriate_challenge(
            self.test_session_id, LearningStage.GUIDED_DISCOVERY, self.test_ticker
        )

        challenge2 = self.trainer.generate_stage_appropriate_challenge(
            self.test_session_id, LearningStage.GUIDED_DISCOVERY, self.test_ticker
        )

        assert challenge1.challenge_id != challenge2.challenge_id

    def test_learning_stage_progression(self):
        """Test that challenge difficulty progresses with learning stages"""
        stages = [
            LearningStage.GUIDED_DISCOVERY,
            LearningStage.ASSISTED_ANALYSIS,
            LearningStage.INDEPENDENT_THINKING,
            LearningStage.ANALYTICAL_MASTERY,
        ]

        difficulties = []
        for stage in stages:
            challenge = self.trainer.generate_stage_appropriate_challenge(
                self.test_session_id, stage, self.test_ticker
            )
            difficulties.append(challenge.difficulty_level)

        # Verify difficulty increases with stage progression
        assert difficulties == [1, 2, 3, 4]

    def test_challenge_data_structure(self):
        """Test that challenge data structure contains required fields"""
        challenge = self.trainer.generate_stage_appropriate_challenge(
            self.test_session_id, LearningStage.GUIDED_DISCOVERY, self.test_ticker
        )

        # Check required fields
        required_fields = [
            "challenge_id",
            "challenge_type",
            "difficulty_level",
            "title",
            "description",
            "company_symbol",
            "company_basic_info",
            "prediction_prompts",
        ]

        for field in required_fields:
            assert hasattr(challenge, field)
            assert getattr(challenge, field) is not None

    def test_prediction_prompts_structure(self):
        """Test that prediction prompts have proper structure"""
        challenge = self.trainer.generate_stage_appropriate_challenge(
            self.test_session_id, LearningStage.GUIDED_DISCOVERY, self.test_ticker
        )

        assert len(challenge.prediction_prompts) > 0

        for prompt in challenge.prediction_prompts:
            assert isinstance(prompt, dict)
            assert "category" in prompt
            assert "prompt" in prompt


if __name__ == "__main__":
    pytest.main([__file__])
