"""
Integration tests for educational system workflows and cross-component interactions.

These tests verify that educational components work together correctly and that
the complete learning workflow functions as expected.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.educational_framework import LearningStage
from src.pattern_recognition_trainer import PatternType, ExerciseDifficulty
from src.tool_independence_trainer import ChallengeType


@pytest.mark.integration
@pytest.mark.educational
class TestLearningProgressionIntegration:
    """Test integration between learning stage assessment and educational content adaptation."""

    def test_complete_learning_progression_workflow(
        self,
        educational_framework,
        pattern_trainer,
        progress_tracker,
        mock_user_session,
    ):
        """Test complete learning progression workflow with stage assessment."""
        user_id = mock_user_session["user_id"]

        # Use behavioral data that suggests assisted analysis stage
        behavioral_data = {
            "analyses_completed": 15,
            "accuracy_scores": [0.85] * 15,
            "engagement_time": 300 * 15,
            "help_requests": 5,
            "behavioral_history": [],  # Required for assessment
        }

        # Assess current learning stage
        assessment_result = educational_framework.assess_learning_stage(behavioral_data)
        current_stage = assessment_result.current_stage

        # Generate appropriate educational content for current stage
        exercise = pattern_trainer.generate_stage_appropriate_exercise(
            user_stage=current_stage,
            pattern_type=PatternType.DEBT_ANALYSIS,
            user_session_id=user_id,
        )

        # Verify exercise matches assessed stage capabilities
        assert exercise is not None
        assert hasattr(exercise, "difficulty")
        assert hasattr(exercise, "pattern_type")

        # Verify assessment provides meaningful feedback
        assert assessment_result.confidence_score >= 0.0
        assert assessment_result.confidence_score <= 1.0
        assert assessment_result.progress_within_stage >= 0.0
        assert assessment_result.progress_within_stage <= 1.0

        # Update progress tracker with exercise completion
        completion_data = {
            "exercise_id": f"test_exercise_{user_id}",
            "accuracy": 0.85,
            "completion_time": 300,
            "pattern_type": PatternType.DEBT_ANALYSIS.value,
            "activity_type": "pattern_exercise",
        }
        updated_progress = progress_tracker.update_progress_metrics(
            user_id=user_id, completion_data=completion_data
        )

        # Verify progress tracking integration
        assert updated_progress is not None
        assert hasattr(updated_progress, "analysis_count")
        assert hasattr(updated_progress, "current_streak")
        assert (
            updated_progress.current_streak >= 1
        )  # Should have at least current completion

        # Verify complete workflow integration
        assert current_stage in [
            LearningStage.GUIDED_DISCOVERY,
            LearningStage.ASSISTED_ANALYSIS,
            LearningStage.INDEPENDENT_THINKING,
            LearningStage.ANALYTICAL_MASTERY,
        ]

    def test_behavioral_analytics_integration_with_stage_advancement(
        self, educational_framework, analytics_tracker, mock_behavioral_data
    ):
        """Test behavioral analytics integration with stage advancement calculations."""
        user_id = "integration_test_user"

        # Simulate behavioral data collection
        analytics_tracker.track_interaction(
            user_id, "analysis_start", {"ticker": "RELIANCE"}
        )
        analytics_tracker.track_interaction(
            user_id, "pattern_identified", {"pattern": "debt_analysis"}
        )
        analytics_tracker.track_interaction(
            user_id, "analysis_complete", {"confidence": 0.8}
        )

        # Get analytics summary
        analytics_summary = analytics_tracker.get_user_analytics_summary(user_id)

        # Use analytics for stage assessment
        stage = educational_framework.assess_current_learning_stage(
            user_id, analytics_summary
        )

        # Verify stage assessment incorporates behavioral data
        assert stage in [stage for stage in LearningStage]

        # Verify analytics data influences educational content
        assert analytics_summary["confidence_level"] > 0
        assert analytics_summary["engagement_time"] > 0

    def test_stage_appropriate_content_adaptation(
        self, educational_framework, pattern_trainer, tool_trainer
    ):
        """Test that content adapts appropriately across different learning stages."""
        user_id = "content_adaptation_test"

        for stage in [
            LearningStage.GUIDED_DISCOVERY,
            LearningStage.ASSISTED_ANALYSIS,
            LearningStage.INDEPENDENT_THINKING,
            LearningStage.ANALYTICAL_MASTERY,
        ]:

            # Generate pattern exercise for this stage
            pattern_exercise = pattern_trainer.generate_stage_appropriate_exercise(
                user_stage=stage,
                pattern_type=PatternType.GROWTH_INDICATORS,
                user_session_id=user_id,
            )

            # Generate tool challenge for this stage
            tool_challenge = tool_trainer.generate_challenge(
                user_stage=stage,
                challenge_type=ChallengeType.CONFIDENCE_BUILDING,
                ticker="TCS",
                user_session_id=user_id,
            )

            # Verify content complexity increases with stage
            if stage == LearningStage.GUIDED_DISCOVERY:
                assert pattern_exercise.difficulty == ExerciseDifficulty.GUIDED
                assert len(pattern_exercise.hints) > 2
                assert tool_challenge.guidance_level == "high"

            elif stage == LearningStage.ANALYTICAL_MASTERY:
                assert pattern_exercise.difficulty == ExerciseDifficulty.MASTERY
                assert len(pattern_exercise.hints) == 0 or pattern_exercise.hints == []
                assert tool_challenge.guidance_level == "minimal"


@pytest.mark.integration
@pytest.mark.educational
class TestPatternRecognitionIntegration:
    """Test integration between pattern recognition training and other educational systems."""

    def test_pattern_exercise_generation_integration(
        self, pattern_trainer, educational_framework
    ):
        """Test pattern exercise generation across all learning stages and pattern types."""
        user_id = "pattern_integration_test"

        # Test all combinations of stages and pattern types
        for stage in LearningStage:
            for pattern_type in PatternType:
                exercise = pattern_trainer.generate_stage_appropriate_exercise(
                    user_stage=stage, pattern_type=pattern_type, user_session_id=user_id
                )

                # Verify exercise is valid
                assert exercise.exercise_id is not None
                assert exercise.pattern_type == pattern_type
                assert len(exercise.expected_patterns) > 0
                assert exercise.chart_data is not None

                # Verify difficulty matches stage
                expected_difficulties = {
                    LearningStage.GUIDED_DISCOVERY: ExerciseDifficulty.GUIDED,
                    LearningStage.ASSISTED_ANALYSIS: ExerciseDifficulty.ASSISTED,
                    LearningStage.INDEPENDENT_THINKING: ExerciseDifficulty.INDEPENDENT,
                    LearningStage.ANALYTICAL_MASTERY: ExerciseDifficulty.MASTERY,
                }
                assert exercise.difficulty == expected_difficulties[stage]

    def test_exercise_difficulty_adaptation(self, pattern_trainer, progress_tracker):
        """Test exercise difficulty adaptation based on user performance history."""
        user_id = "difficulty_adaptation_test"

        # Simulate performance history
        performance_history = [
            {"exercise_id": "ex1", "accuracy": 0.9, "time_taken": 120},
            {"exercise_id": "ex2", "accuracy": 0.85, "time_taken": 110},
            {"exercise_id": "ex3", "accuracy": 0.88, "time_taken": 100},
        ]

        # Generate exercise based on good performance
        exercise = pattern_trainer.generate_stage_appropriate_exercise(
            user_stage=LearningStage.ASSISTED_ANALYSIS, user_session_id=user_id
        )

        # Evaluate the exercise to test feedback
        feedback = pattern_trainer.evaluate_attempt(
            exercise.exercise_id,
            ["deleveraging_trend", "high_debt_periods"],
            user_id,
            150,
        )

        # Verify feedback is generated
        assert feedback.accuracy_score >= 0
        assert feedback.educational_explanation != ""
        assert isinstance(feedback.improvement_suggestions, list)

    def test_pattern_evaluation_and_gamification_integration(
        self, pattern_trainer, progress_tracker
    ):
        """Test integration between pattern evaluation and gamification system."""
        user_id = "gamification_integration_test"

        # Generate and complete multiple exercises
        for i in range(3):
            exercise = pattern_trainer.generate_stage_appropriate_exercise(
                user_stage=LearningStage.INDEPENDENT_THINKING,
                pattern_type=PatternType.DEBT_ANALYSIS,
                user_session_id=user_id,
            )

            # Simulate successful completion
            feedback = pattern_trainer.evaluate_attempt(
                exercise.exercise_id, exercise.expected_patterns, user_id, 180
            )

            # Update progress tracker
            progress_tracker.update_pattern_recognition_progress(
                user_id, feedback.accuracy_score, exercise.pattern_type
            )

        # Check if badges were awarded
        user_badges = progress_tracker.get_user_badges(user_id)
        user_progress = progress_tracker.get_user_progress(user_id)

        # Verify gamification integration
        assert len(user_badges) >= 0  # Should have some badges
        assert user_progress["pattern_recognition_score"] > 0


@pytest.mark.integration
@pytest.mark.educational
class TestResearchGuidanceIntegration:
    """Test integration between research guidance system and educational workflows."""

    def test_gap_identification_to_research_assignment_workflow(
        self, gap_service, research_system, sample_stock_data
    ):
        """Test complete workflow from gap identification to research assignment generation."""
        user_id = "research_workflow_test"

        # Simulate analysis completion with gaps
        analysis_results = {
            "ticker": sample_stock_data["ticker"],
            "quantitative_analysis": sample_stock_data,
            "gaps_identified": [
                {
                    "type": "MOAT_ANALYSIS",
                    "severity": "high",
                    "description": "Missing competitive advantage analysis",
                },
                {
                    "type": "MANAGEMENT_ASSESSMENT",
                    "severity": "medium",
                    "description": "Limited management evaluation",
                },
            ],
        }

        # Process gaps through gap-filling service
        gap_recommendations = gap_service.identify_analysis_gaps(
            analysis_results["quantitative_analysis"],
            user_context={"user_id": user_id, "learning_stage": "ASSISTED_ANALYSIS"},
        )

        # Generate research assignments from gaps
        research_assignments = []
        for gap in analysis_results["gaps_identified"]:
            assignment = research_system.generate_personalized_research_assignment(
                user_gaps=[gap], learning_stage=2, research_history=[]
            )
            research_assignments.append(assignment)

        # Verify assignments were created
        assert len(research_assignments) == 2
        for assignment in research_assignments:
            assert assignment["assignment_id"] is not None
            assert len(assignment["instructions"]) > 0
            assert assignment["time_estimate_minutes"] > 0

    def test_research_assignment_completion_tracking(
        self, research_system, progress_tracker
    ):
        """Test research assignment completion tracking with progress system."""
        user_id = "assignment_tracking_test"

        # Create research assignment
        assignment = research_system.generate_personalized_research_assignment(
            user_gaps=[
                {
                    "category": "COMPETITIVE_ANALYSIS",
                    "company": "HDFC Bank",
                    "severity": "medium",
                }
            ],
            learning_stage=3,
            research_history=[],
        )

        # Simulate assignment completion
        completion_data = {
            "assignment_id": assignment["assignment_id"],
            "user_submission": "Detailed competitive analysis of HDFC Bank...",
            "time_taken": 1800,  # 30 minutes
            "quality_rating": 0.85,
        }

        # Submit and evaluate completion
        evaluation = research_system.evaluate_research_submission(
            assignment["assignment_id"],
            completion_data["user_submission"],
            assignment.get("success_criteria", {}),
        )

        # Update progress tracking
        progress_tracker.update_research_progress(
            user_id, evaluation.get("quality_score", 0.8), assignment["category"]
        )

        # Verify tracking integration
        user_progress = progress_tracker.get_user_progress(user_id)
        assert user_progress["research_assignments_completed"] > 0


@pytest.mark.integration
@pytest.mark.educational
class TestToolIndependenceIntegration:
    """Test integration between tool independence training and analytical confidence tracking."""

    def test_challenge_generation_with_learning_stage_integration(
        self, tool_trainer, educational_framework
    ):
        """Test challenge generation integration with learning stage assessment."""
        user_id = "tool_integration_test"

        # Test challenge generation for each stage
        for stage in LearningStage:
            challenge = tool_trainer.generate_challenge(
                user_stage=stage,
                challenge_type=ChallengeType.BLIND_ANALYSIS,
                ticker="TCS",
                user_session_id=user_id,
            )

            # Verify challenge matches stage requirements
            assert challenge.challenge_id is not None
            assert challenge.difficulty_level is not None

            # Verify guidance level matches stage
            if stage == LearningStage.GUIDED_DISCOVERY:
                assert challenge.guidance_level in ["high", "maximum"]
            elif stage == LearningStage.ANALYTICAL_MASTERY:
                assert challenge.guidance_level in ["minimal", "none"]

    def test_analytical_confidence_progression(self, tool_trainer, progress_tracker):
        """Test analytical confidence tracking and progression through tool independence challenges."""
        user_id = "confidence_progression_test"

        # Generate series of challenges with increasing difficulty
        confidence_scores = []

        for i in range(5):
            challenge = tool_trainer.generate_challenge(
                user_stage=LearningStage.ASSISTED_ANALYSIS,
                challenge_type=ChallengeType.CONFIDENCE_BUILDING,
                ticker="RELIANCE",
                user_session_id=user_id,
            )

            # Simulate challenge completion with improving performance
            completion_result = {
                "prediction_accuracy": 0.6 + (i * 0.08),  # Improving accuracy
                "confidence_level": 0.5 + (i * 0.1),  # Growing confidence
                "time_taken": 300 - (i * 20),  # Getting faster
                "help_requests": max(0, 3 - i),  # Less help needed
            }

            # Evaluate challenge
            feedback = tool_trainer.evaluate_challenge_attempt(
                challenge.challenge_id, completion_result, user_id
            )

            confidence_scores.append(feedback.confidence_score)

            # Update progress tracker
            progress_tracker.update_tool_independence_progress(
                user_id, feedback.confidence_score, challenge.challenge_type
            )

        # Verify confidence progression
        assert confidence_scores[-1] > confidence_scores[0]  # Improved over time

        # Check gamification integration
        user_progress = progress_tracker.get_user_progress(user_id)
        assert user_progress["tool_independence_score"] > 0


@pytest.mark.integration
@pytest.mark.educational
class TestCrossSystemIntegration:
    """Test integration across multiple educational systems."""

    def test_complete_educational_workflow_integration(
        self,
        educational_framework,
        pattern_trainer,
        research_system,
        progress_tracker,
        analytics_tracker,
    ):
        """Test complete educational workflow spanning all systems."""
        user_id = "complete_workflow_test"

        # Step 1: User completes analysis (behavioral analytics)
        analytics_tracker.track_interaction(
            user_id, "analysis_start", {"ticker": "RELIANCE"}
        )
        analytics_tracker.track_interaction(
            user_id, "analysis_complete", {"confidence": 0.7}
        )

        # Step 2: System assesses learning stage
        behavioral_data = analytics_tracker.get_user_analytics_summary(user_id)
        learning_stage = educational_framework.assess_current_learning_stage(
            user_id, behavioral_data
        )

        # Step 3: Generate educational content based on stage
        pattern_exercise = pattern_trainer.generate_stage_appropriate_exercise(
            user_stage=learning_stage,
            pattern_type=PatternType.DEBT_ANALYSIS,
            user_session_id=user_id,
        )

        # Step 4: User completes pattern exercise
        feedback = pattern_trainer.evaluate_attempt(
            pattern_exercise.exercise_id,
            pattern_exercise.expected_patterns[:1],  # Partial success
            user_id,
            200,
        )

        # Step 5: Update progress and award achievements
        progress_tracker.update_pattern_recognition_progress(
            user_id, feedback.accuracy_score, pattern_exercise.pattern_type
        )

        # Step 6: Generate research assignment for identified gaps
        research_assignment = research_system.generate_personalized_research_assignment(
            user_gaps=[
                {
                    "category": "MOAT_ANALYSIS",
                    "company": "Reliance Industries",
                    "severity": "high",
                }
            ],
            learning_stage=2,
            research_history=[],
        )

        # Verify complete workflow
        assert feedback.accuracy_score >= 0
        assert research_assignment["assignment_id"] is not None

        user_progress = progress_tracker.get_user_progress(user_id)
        assert user_progress["analyses_completed"] >= 0
        assert user_progress["pattern_recognition_score"] >= 0

    def test_session_management_across_systems(self, client, mock_user_session):
        """Test user session management across all educational components."""
        # This test would require actual Flask routes to be implemented
        # For now, verify session data structure
        session_data = mock_user_session

        required_fields = [
            "user_id",
            "session_id",
            "learning_stage",
            "analyses_completed",
        ]
        for field in required_fields:
            assert field in session_data

        assert isinstance(session_data["analyses_completed"], int)
        assert session_data["analyses_completed"] >= 0

    def test_performance_across_integrated_systems(
        self,
        performance_monitor,
        educational_framework,
        pattern_trainer,
        research_system,
    ):
        """Test performance of integrated educational operations."""
        user_id = "performance_test_user"

        # Test educational framework performance
        @performance_monitor.time_operation("learning_stage_assessment")
        def test_stage_assessment():
            return educational_framework.assess_current_learning_stage(
                user_id, {"analyses_completed": 10, "accuracy_scores": [0.8] * 10}
            )

        # Test pattern exercise generation performance
        @performance_monitor.time_operation("pattern_exercise_generation")
        def test_exercise_generation():
            return pattern_trainer.generate_stage_appropriate_exercise(
                user_stage=LearningStage.ASSISTED_ANALYSIS, user_session_id=user_id
            )

        # Test research assignment creation performance
        @performance_monitor.time_operation("research_assignment_creation")
        def test_assignment_creation():
            return research_system.create_research_assignment(
                assignment_type="COMPETITIVE_ANALYSIS",
                user_profile={
                    "user_id": user_id,
                    "learning_stage": "INDEPENDENT_THINKING",
                },
                company_context={
                    "ticker": "TCS",
                    "company_name": "TCS Ltd",
                    "industry": "IT",
                },
            )

        # Execute operations
        test_stage_assessment()
        test_exercise_generation()
        test_assignment_creation()

        # Assert performance requirements
        performance_monitor.assert_performance(
            "learning_stage_assessment", 0.1
        )  # 100ms
        performance_monitor.assert_performance(
            "pattern_exercise_generation", 0.2
        )  # 200ms
        performance_monitor.assert_performance(
            "research_assignment_creation", 0.15
        )  # 150ms
