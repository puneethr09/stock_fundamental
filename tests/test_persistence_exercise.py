import os
from src.pattern_recognition_trainer import (
    PatternRecognitionTrainer,
    PatternExercise,
    PatternType,
    ExerciseDifficulty,
)


def test_persist_and_load_exercise(tmp_path):
    trainer = PatternRecognitionTrainer()

    # Create a small company example
    company = {
        "ticker": "TESTCO",
        "company": "Test Company",
        "sector": "Testing",
        "pattern_period": "2020-2021",
        "description": "A test company for persistence",
    }

    exercise = trainer._create_exercise(
        pattern_type=PatternType.DEBT_ANALYSIS,
        difficulty=ExerciseDifficulty.GUIDED,
        company_example=company,
        user_session_id="unit",
    )

    # Ensure it was persisted
    loaded = trainer._load_exercise_from_db(exercise.exercise_id)
    assert loaded is not None
    assert loaded.exercise_id == exercise.exercise_id
    assert isinstance(loaded.expected_patterns, list)
