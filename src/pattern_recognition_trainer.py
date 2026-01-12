"""
Pattern Recognition Training System for Stock Fundamental Analysis Platform

This module implements interactive pattern recognition exercises that adapt to the user's
learning stage, providing hands-on training for identifying financial patterns in Indian
stock market data.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.utils
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
import random
from datetime import datetime, timedelta, timezone
import sqlite3
import os

from src.educational_framework import EducationalMasteryFramework, LearningStage


class PatternType(Enum):
    """Types of financial patterns for recognition training"""

    DEBT_ANALYSIS = "debt_analysis"
    GROWTH_INDICATORS = "growth_indicators"
    VALUE_TRAPS = "value_traps"
    TREND_REVERSAL = "trend_reversal"
    QUALITY_DETERIORATION = "quality_deterioration"


class ExerciseDifficulty(Enum):
    """Difficulty levels for pattern recognition exercises"""

    GUIDED = "guided"  # Stage 1: Heavy guidance with highlights
    ASSISTED = "assisted"  # Stage 2: Some hints and comparisons
    INDEPENDENT = "independent"  # Stage 3: Minimal guidance
    MASTERY = "mastery"  # Stage 4: Teaching and validation


@dataclass
class PatternExercise:
    """Data class representing a pattern recognition exercise"""

    exercise_id: str
    pattern_type: PatternType
    difficulty: ExerciseDifficulty
    title: str
    description: str
    ticker: str
    company_name: str
    chart_data: Dict[str, Any]
    pattern_zones: List[Dict[str, Any]]  # Interactive clickable zones
    expected_patterns: List[str]
    hints: List[str]
    educational_context: str
    success_criteria: Dict[str, Any]
    time_limit_seconds: Optional[int] = None


@dataclass
class PatternAttempt:
    """User attempt at pattern recognition"""

    exercise_id: str
    user_session_id: str
    identified_patterns: List[str]
    pattern_coordinates: List[Dict[str, float]]  # Click/touch coordinates
    attempt_time_seconds: float
    confidence_level: str  # "low", "medium", "high"
    timestamp: datetime


@dataclass
@dataclass
class PatternFeedback:
    """Feedback provided after pattern recognition attempt"""

    attempt_id: str
    accuracy_score: float  # 0.0 to 1.0
    correct_patterns: List[str]
    missed_patterns: List[str]
    false_positives: List[str]
    educational_explanation: str
    improvement_suggestions: List[str]
    stage_progression_impact: float
    next_exercise_recommendation: Optional[str] = None

    @property
    def score(self) -> float:
        """Alias for accuracy_score for backward compatibility"""
        return self.accuracy_score


class PatternRecognitionTrainer:
    """
    Main class for generating and managing pattern recognition exercises

    This system creates interactive exercises that teach users to identify
    financial patterns in Indian market data, with difficulty adapting to
    the user's learning stage from the Educational Mastery Framework.
    """

    def __init__(self):
        self.educational_framework = EducationalMasteryFramework()
        self.indian_companies = self._load_indian_company_examples()
        self.pattern_templates = self._initialize_pattern_templates()
        self.exercise_cache = {}
        # Simple on-disk persistence for exercises (SQLite)
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        # normalize path
        self.data_dir = os.path.abspath(self.data_dir)
        self.db_path = os.path.join(self.data_dir, "exercises.db")
        self._ensure_db()

    def _ensure_db(self):
        """Create data directory and exercises table if missing"""
        os.makedirs(self.data_dir, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS exercises (
                exercise_id TEXT PRIMARY KEY,
                payload TEXT,
                created_at TIMESTAMP
            )
            """
        )
        conn.commit()
        conn.close()

    def _persist_exercise(self, exercise: PatternExercise):
        """Persist a PatternExercise to the local SQLite store (JSON payload)."""
        payload = asdict(exercise)
        # Serialize enums to their values for JSON compatibility
        if isinstance(payload.get("pattern_type"), Enum):
            payload["pattern_type"] = exercise.pattern_type.value
        if isinstance(payload.get("difficulty"), Enum):
            payload["difficulty"] = exercise.difficulty.value

        payload_json = json.dumps(payload, default=str)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO exercises (exercise_id, payload, created_at) VALUES (?, ?, ?)",
            (exercise.exercise_id, payload_json, datetime.now(timezone.utc)),
        )
        conn.commit()
        conn.close()

    def _load_exercise_from_db(self, exercise_id: str) -> Optional[PatternExercise]:
        """Load a persisted exercise and reconstruct a PatternExercise, or None if missing."""
        if not os.path.exists(self.db_path):
            return None
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT payload FROM exercises WHERE exercise_id = ?", (exercise_id,))
        row = c.fetchone()
        conn.close()
        if not row:
            return None

        try:
            payload = json.loads(row[0])
        except Exception:
            return None

        # Convert enums back
        pattern_type = (
            PatternType(payload["pattern_type"])
            if payload.get("pattern_type")
            else None
        )
        difficulty = (
            ExerciseDifficulty(payload["difficulty"])
            if payload.get("difficulty")
            else None
        )

        return PatternExercise(
            exercise_id=payload.get("exercise_id"),
            pattern_type=pattern_type,
            difficulty=difficulty,
            title=payload.get("title", ""),
            description=payload.get("description", ""),
            ticker=payload.get("ticker", ""),
            company_name=payload.get("company_name", ""),
            chart_data=payload.get("chart_data", {}),
            pattern_zones=payload.get("pattern_zones", []),
            expected_patterns=payload.get("expected_patterns", []),
            hints=payload.get("hints", []),
            educational_context=payload.get("educational_context", ""),
            success_criteria=payload.get("success_criteria", {}),
            time_limit_seconds=payload.get("time_limit_seconds"),
        )

    def _load_indian_company_examples(self) -> Dict[PatternType, List[Dict]]:
        """Load curated Indian company examples for each pattern type"""
        return {
            PatternType.DEBT_ANALYSIS: [
                {
                    "ticker": "RELIANCE",
                    "company": "Reliance Industries Limited",
                    "sector": "Oil & Gas",
                    "pattern_period": "2018-2020",
                    "description": "Deleveraging journey post-Jio investments",
                },
                {
                    "ticker": "BHARTIARTL",
                    "company": "Bharti Airtel Limited",
                    "sector": "Telecommunications",
                    "pattern_period": "2019-2021",
                    "description": "AGR stress leading to debt consolidation",
                },
                {
                    "ticker": "ADANIPORTS",
                    "company": "Adani Ports and SEZ Limited",
                    "sector": "Infrastructure",
                    "pattern_period": "2020-2022",
                    "description": "Infrastructure expansion debt patterns",
                },
            ],
            PatternType.GROWTH_INDICATORS: [
                {
                    "ticker": "TCS",
                    "company": "Tata Consultancy Services Limited",
                    "sector": "IT Services",
                    "pattern_period": "2016-2021",
                    "description": "Consistent ROE expansion with margin stability",
                },
                {
                    "ticker": "HDFC",
                    "company": "Housing Development Finance Corporation",
                    "sector": "Financial Services",
                    "pattern_period": "2015-2020",
                    "description": "Asset quality improvement with growth",
                },
                {
                    "ticker": "ASIANPAINT",
                    "company": "Asian Paints Limited",
                    "sector": "Consumer Goods",
                    "pattern_period": "2017-2022",
                    "description": "Market share gains with margin expansion",
                },
            ],
            PatternType.VALUE_TRAPS: [
                {
                    "ticker": "YESBANK",
                    "company": "Yes Bank Limited",
                    "sector": "Banking",
                    "pattern_period": "2018-2020",
                    "description": "Low valuation masking asset quality issues",
                },
                {
                    "ticker": "SUZLON",
                    "company": "Suzlon Energy Limited",
                    "sector": "Renewable Energy",
                    "pattern_period": "2015-2019",
                    "description": "Cyclical downturn with structural challenges",
                },
                {
                    "ticker": "JETAIRWAYS",
                    "company": "Jet Airways (India) Limited",
                    "sector": "Aviation",
                    "pattern_period": "2017-2019",
                    "description": "Operational decline despite low P/E",
                },
            ],
        }

    def _initialize_pattern_templates(self) -> Dict[PatternType, Dict]:
        """Initialize pattern recognition templates for each type"""
        return {
            PatternType.DEBT_ANALYSIS: {
                "metrics": ["debt_to_equity", "interest_coverage", "current_ratio"],
                "thresholds": {
                    "concerning_debt_equity": 1.5,
                    "poor_interest_coverage": 2.0,
                    "weak_current_ratio": 1.2,
                },
                "pattern_indicators": {
                    "debt_spiral": "Increasing D/E ratio with declining interest coverage",
                    "deleveraging": "Decreasing D/E ratio with improving coverage",
                    "liquidity_stress": "Declining current ratio below 1.2",
                },
            },
            PatternType.GROWTH_INDICATORS: {
                "metrics": ["roe", "revenue_growth", "operating_margin", "roce"],
                "thresholds": {
                    "strong_roe": 15.0,
                    "healthy_growth": 10.0,
                    "expanding_margins": 0.02,  # 2% year-over-year improvement
                },
                "pattern_indicators": {
                    "quality_growth": "ROE >15% with consistent revenue growth",
                    "margin_expansion": "Operating margins improving over time",
                    "capital_efficiency": "ROCE consistently above cost of capital",
                },
            },
            PatternType.VALUE_TRAPS: {
                "metrics": ["pe_ratio", "pb_ratio", "roe", "debt_to_equity"],
                "thresholds": {
                    "low_pe": 10.0,
                    "low_pb": 1.0,
                    "declining_roe": -2.0,  # 2% annual decline
                    "high_debt": 2.0,
                },
                "pattern_indicators": {
                    "value_trap": "Low P/E but deteriorating fundamentals",
                    "quality_discount": "Low valuation with strong fundamentals",
                    "cyclical_trough": "Temporary low earnings affecting ratios",
                },
            },
        }

    def generate_stage_appropriate_exercise(
        self,
        user_stage: LearningStage,
        pattern_type: Optional[PatternType] = None,
        user_session_id: str = "anonymous",
        company_info: Optional[Dict[str, str]] = None,
    ) -> PatternExercise:
        """
        Generate a pattern recognition exercise appropriate for user's learning stage

        Args:
            user_stage: Current learning stage from EducationalMasteryFramework
            pattern_type: Specific pattern type to focus on (optional)
            user_session_id: User identifier for progress tracking
            company_info: Optional company information for specific stock selection

        Returns:
            PatternExercise configured for the user's learning level
        """
        # Map learning stage to exercise difficulty
        stage_to_difficulty = {
            LearningStage.GUIDED_DISCOVERY: ExerciseDifficulty.GUIDED,
            LearningStage.ASSISTED_ANALYSIS: ExerciseDifficulty.ASSISTED,
            LearningStage.INDEPENDENT_THINKING: ExerciseDifficulty.INDEPENDENT,
            LearningStage.ANALYTICAL_MASTERY: ExerciseDifficulty.MASTERY,
        }

        difficulty = stage_to_difficulty.get(user_stage, ExerciseDifficulty.GUIDED)

        # Select pattern type if not specified
        if pattern_type is None:
            # Bias toward simpler patterns for early stages
            if user_stage in [
                LearningStage.GUIDED_DISCOVERY,
                LearningStage.ASSISTED_ANALYSIS,
            ]:
                pattern_type = random.choice(
                    [PatternType.DEBT_ANALYSIS, PatternType.GROWTH_INDICATORS]
                )
            else:
                pattern_type = random.choice(list(PatternType))

        # Select company example (use provided company_info or random selection)
        if company_info:
            # Validate and clean company_info fields
            company_name = (company_info.get("name") or "").strip()
            company_ticker = (company_info.get("ticker") or "").strip()
            company_industry = (company_info.get("industry") or "").strip()

            # Use fallbacks for empty/invalid fields
            if not company_name:
                company_name = company_ticker if company_ticker else "Unknown Company"
            if not company_ticker:
                company_ticker = "N/A"
            if not company_industry:
                company_industry = "General"

            # Use provided company info and add missing fields for compatibility
            company_example = {
                "company": company_name,
                "ticker": company_ticker,
                "industry": company_industry,
                "sector": company_info.get(
                    "sector", company_industry
                ),  # Use industry as sector if not provided
                "description": f"Analysis of {company_name} from the {company_industry} sector",  # Clean description
                "pattern_description": f"Analyzing {company_name} financial patterns",
                "pattern_period": "2019-2025",  # Default period for our updated date range
                "context": f"Real-time analysis of {company_name} from the {company_industry} sector",
            }
        else:
            # Select appropriate company example from predefined list
            company_example = random.choice(self.indian_companies[pattern_type])

        # Generate exercise based on difficulty and pattern type
        exercise = self._create_exercise(
            pattern_type=pattern_type,
            difficulty=difficulty,
            company_example=company_example,
            user_session_id=user_session_id,
        )

        return exercise

    def _create_exercise(
        self,
        pattern_type: PatternType,
        difficulty: ExerciseDifficulty,
        company_example: Dict[str, str],
        user_session_id: str,
    ) -> PatternExercise:
        """Create a specific pattern recognition exercise"""

        exercise_id = f"{pattern_type.value}_{difficulty.value}_{company_example['ticker']}_{user_session_id[:8]}"

        # Generate synthetic but realistic data for the exercise
        chart_data = self._generate_pattern_chart_data(pattern_type, company_example)

        # Create interactive pattern zones based on difficulty
        pattern_zones = self._create_interactive_zones(
            chart_data, pattern_type, difficulty
        )

        # Determine expected patterns for the exercise
        expected_patterns = self._identify_expected_patterns(chart_data, pattern_type)

        # Generate stage-appropriate hints and context
        hints = self._generate_stage_appropriate_hints(pattern_type, difficulty)
        educational_context = self._create_educational_context(
            pattern_type, company_example, difficulty
        )

        # Set success criteria based on difficulty
        success_criteria = self._define_success_criteria(difficulty, expected_patterns)

        # Create exercise object
        exercise = PatternExercise(
            exercise_id=exercise_id,
            pattern_type=pattern_type,
            difficulty=difficulty,
            title=self._generate_exercise_title(
                pattern_type, company_example, difficulty
            ),
            description=self._generate_exercise_description(pattern_type, difficulty),
            ticker=company_example["ticker"],
            company_name=company_example["company"],
            chart_data=chart_data,
            pattern_zones=pattern_zones,
            expected_patterns=expected_patterns,
            hints=hints,
            educational_context=educational_context,
            success_criteria=success_criteria,
            time_limit_seconds=self._calculate_time_limit(difficulty),
        )

        # Cache exercise for later evaluation
        self.exercise_cache[exercise_id] = exercise

        # Persist exercise to local SQLite store for durability
        try:
            self._persist_exercise(exercise)
        except Exception:
            # Persistence failure should not break in-memory flow; log silently
            pass

        return exercise

    def _generate_pattern_chart_data(
        self, pattern_type: PatternType, company_example: Dict
    ) -> Dict[str, Any]:
        """Generate realistic chart data showing the specified pattern"""

        # Create base time series (quarterly data over N periods - default 6 years)
        periods = 24

        # Calculate end_date as the end of the current quarter and start_date accordingly
        end_date = pd.Timestamp(datetime.now(timezone.utc)).to_period("Q").end_time
        # start_date such that the final quarter is the current quarter
        start_date = end_date - pd.offsets.QuarterEnd(periods - 1)
        quarters = pd.date_range(start=start_date, periods=periods, freq="QE")

        base_data = {
            "dates": [q.strftime("%Y-%m-%d") for q in quarters],
            "quarters": [f"Q{q.quarter} {q.year}" for q in quarters],
        }

        if pattern_type == PatternType.DEBT_ANALYSIS:
            # Generate debt analysis pattern data
            debt_to_equity = self._generate_debt_pattern(
                periods, company_example.get("pattern_description", "")
            )
            interest_coverage = self._generate_coverage_pattern(periods, debt_to_equity)
            current_ratio = self._generate_liquidity_pattern(periods)

            base_data.update(
                {
                    "debt_to_equity": debt_to_equity,
                    "interest_coverage": interest_coverage,
                    "current_ratio": current_ratio,
                    "metrics": ["Debt-to-Equity", "Interest Coverage", "Current Ratio"],
                }
            )

        elif pattern_type == PatternType.GROWTH_INDICATORS:
            # Generate growth pattern data
            roe = self._generate_roe_pattern(
                periods, company_example.get("pattern_description", "")
            )
            revenue_growth = self._generate_revenue_growth_pattern(periods)
            operating_margin = self._generate_margin_pattern(periods)

            base_data.update(
                {
                    "roe": roe,
                    "revenue_growth": revenue_growth,
                    "operating_margin": operating_margin,
                    "metrics": [
                        "Return on Equity (%)",
                        "Revenue Growth (%)",
                        "Operating Margin (%)",
                    ],
                }
            )

        elif pattern_type == PatternType.VALUE_TRAPS:
            # Generate value trap pattern data
            pe_ratio = self._generate_pe_pattern(
                periods, company_example.get("pattern_description", "")
            )
            pb_ratio = self._generate_pb_pattern(periods, pe_ratio)
            roe_declining = self._generate_declining_roe_pattern(periods)

            base_data.update(
                {
                    "pe_ratio": pe_ratio,
                    "pb_ratio": pb_ratio,
                    "roe": roe_declining,
                    "metrics": ["P/E Ratio", "P/B Ratio", "ROE (%)"],
                }
            )

        return base_data

    def _generate_debt_pattern(self, periods: int, description: str) -> List[float]:
        """Generate realistic debt-to-equity pattern data"""
        base_de = 0.8
        noise_factor = 0.1

        if "deleveraging" in description.lower():
            # Decreasing debt pattern
            trend = np.linspace(1.2, 0.6, periods)
        elif "expansion" in description.lower():
            # Increasing debt pattern
            trend = np.linspace(0.5, 1.5, periods)
        else:
            # Stable with fluctuations
            trend = np.ones(periods) * base_de

        # Add realistic noise
        noise = np.random.normal(0, noise_factor, periods)
        pattern = np.maximum(trend + noise, 0.1)  # Ensure positive values

        return [round(val, 2) for val in pattern]

    def _generate_coverage_pattern(
        self, periods: int, debt_to_equity: List[float]
    ) -> List[float]:
        """Generate interest coverage pattern inversely related to debt"""
        # Interest coverage typically inversely related to debt levels
        base_coverage = 8.0
        coverage_pattern = []

        for de_ratio in debt_to_equity:
            # Higher debt typically means lower coverage
            coverage = base_coverage * (1.5 / (de_ratio + 0.5))
            # Add some noise
            coverage += np.random.normal(0, 0.5)
            coverage_pattern.append(max(coverage, 0.5))  # Minimum coverage

        return [round(val, 1) for val in coverage_pattern]

    def _generate_liquidity_pattern(self, periods: int) -> List[float]:
        """Generate current ratio pattern"""
        base_ratio = 1.5
        trend = np.random.normal(base_ratio, 0.2, periods)
        # Add some cyclical component
        cyclical = 0.3 * np.sin(np.linspace(0, 4 * np.pi, periods))
        pattern = np.maximum(trend + cyclical, 0.8)

        return [round(val, 2) for val in pattern]

    def _generate_roe_pattern(self, periods: int, description: str) -> List[float]:
        """Generate ROE pattern based on company description"""
        base_roe = 15.0

        if "expansion" in description.lower() or "improving" in description.lower():
            # Improving ROE trend
            trend = np.linspace(12.0, 20.0, periods)
        elif "consistent" in description.lower():
            # Stable ROE with minor fluctuations
            trend = np.ones(periods) * base_roe
        else:
            # Mixed pattern
            trend = base_roe + 3 * np.sin(np.linspace(0, 2 * np.pi, periods))

        # Add noise
        noise = np.random.normal(0, 1.0, periods)
        pattern = np.maximum(trend + noise, 2.0)  # Minimum ROE

        return [round(val, 1) for val in pattern]

    def _generate_revenue_growth_pattern(self, periods: int) -> List[float]:
        """Generate revenue growth pattern"""
        base_growth = 12.0
        # Create variable growth with some cyclicality
        cyclical = 5.0 * np.cos(np.linspace(0, 3 * np.pi, periods))
        trend = np.ones(periods) * base_growth + cyclical
        noise = np.random.normal(0, 2.0, periods)
        pattern = trend + noise

        return [round(val, 1) for val in pattern]

    def _generate_margin_pattern(self, periods: int) -> List[float]:
        """Generate operating margin pattern"""
        base_margin = 18.0
        # Slight improving trend with fluctuations
        trend = np.linspace(15.0, 21.0, periods)
        noise = np.random.normal(0, 1.5, periods)
        pattern = np.maximum(trend + noise, 8.0)

        return [round(val, 1) for val in pattern]

    def _generate_pe_pattern(self, periods: int, description: str) -> List[float]:
        """Generate P/E ratio pattern for value trap scenarios"""

        if "low valuation" in description.lower():
            # Low P/E that stays low (potential value trap)
            base_pe = 8.0
            trend = np.ones(periods) * base_pe
            noise = np.random.normal(0, 1.5, periods)
            pattern = np.maximum(trend + noise, 3.0)
        else:
            # Normal P/E with fluctuations
            base_pe = 15.0
            trend = base_pe + 3 * np.sin(np.linspace(0, 2 * np.pi, periods))
            noise = np.random.normal(0, 2.0, periods)
            pattern = np.maximum(trend + noise, 5.0)

        return [round(val, 1) for val in pattern]

    def _generate_pb_pattern(self, periods: int, pe_ratio: List[float]) -> List[float]:
        """Generate P/B ratio pattern correlated with P/E"""
        # P/B typically correlated with P/E but with different scaling
        pb_pattern = []

        for pe in pe_ratio:
            # Rough correlation between P/E and P/B
            pb = 0.8 + (pe / 20.0) * 1.5
            pb += np.random.normal(0, 0.2)
            pb_pattern.append(max(pb, 0.3))

        return [round(val, 2) for val in pb_pattern]

    def _generate_declining_roe_pattern(self, periods: int) -> List[float]:
        """Generate declining ROE pattern for value trap scenario"""
        # Start high and decline (fundamentals deteriorating)
        trend = np.linspace(18.0, 8.0, periods)
        noise = np.random.normal(0, 1.0, periods)
        pattern = np.maximum(trend + noise, 2.0)

        return [round(val, 1) for val in pattern]

    def _create_interactive_zones(
        self,
        chart_data: Dict[str, Any],
        pattern_type: PatternType,
        difficulty: ExerciseDifficulty,
    ) -> List[Dict[str, Any]]:
        """Create interactive clickable zones for pattern identification"""

        zones = []
        periods = len(chart_data["dates"])

        if pattern_type == PatternType.DEBT_ANALYSIS:
            # Create zones for debt pattern identification
            if difficulty == ExerciseDifficulty.GUIDED:
                # Highlight obvious problem areas
                for i in range(periods):
                    if chart_data["debt_to_equity"][i] > 1.5:
                        zones.append(
                            {
                                "type": "debt_concern",
                                "period_index": i,
                                "coordinates": {
                                    "x": i,
                                    "y": chart_data["debt_to_equity"][i],
                                },
                                "hint": "High debt-to-equity ratio detected",
                                "pattern_strength": "strong",
                            }
                        )
            else:
                # Create broader zones for user identification
                zones.append(
                    {
                        "type": "debt_trend",
                        "period_range": [0, periods - 1],
                        "hint": (
                            "Analyze the debt trajectory over time"
                            if difficulty == ExerciseDifficulty.ASSISTED
                            else ""
                        ),
                        "pattern_strength": "moderate",
                    }
                )

        elif pattern_type == PatternType.GROWTH_INDICATORS:
            # Create zones for growth pattern identification
            if difficulty == ExerciseDifficulty.GUIDED:
                # Highlight strong performance periods
                for i in range(periods):
                    if chart_data["roe"][i] > 18.0:
                        zones.append(
                            {
                                "type": "strong_performance",
                                "period_index": i,
                                "coordinates": {"x": i, "y": chart_data["roe"][i]},
                                "hint": "Strong ROE performance period",
                                "pattern_strength": "strong",
                            }
                        )
            else:
                # Create zones for trend analysis
                zones.append(
                    {
                        "type": "growth_trend",
                        "period_range": [periods // 2, periods - 1],
                        "hint": (
                            "Focus on recent growth trajectory"
                            if difficulty == ExerciseDifficulty.ASSISTED
                            else ""
                        ),
                        "pattern_strength": "moderate",
                    }
                )

        elif pattern_type == PatternType.VALUE_TRAPS:
            # Create zones for value trap identification
            if difficulty == ExerciseDifficulty.GUIDED:
                # Highlight disconnect between valuation and fundamentals
                for i in range(periods):
                    if chart_data["pe_ratio"][i] < 10.0 and chart_data["roe"][i] < 12.0:
                        zones.append(
                            {
                                "type": "value_trap_signal",
                                "period_index": i,
                                "coordinates": {"x": i, "y": chart_data["pe_ratio"][i]},
                                "hint": "Low P/E but check fundamentals",
                                "pattern_strength": "strong",
                            }
                        )
            else:
                # Create zones for comprehensive analysis
                zones.append(
                    {
                        "type": "valuation_analysis",
                        "period_range": [0, periods - 1],
                        "hint": (
                            "Analyze relationship between valuation and quality"
                            if difficulty == ExerciseDifficulty.ASSISTED
                            else ""
                        ),
                        "pattern_strength": "complex",
                    }
                )

        return zones

    def _identify_expected_patterns(
        self, chart_data: Dict[str, Any], pattern_type: PatternType
    ) -> List[str]:
        """Identify the patterns that should be recognizable in the chart data"""

        expected = []

        if pattern_type == PatternType.DEBT_ANALYSIS:
            # Analyze debt patterns
            debt_ratios = chart_data["debt_to_equity"]
            coverage_ratios = chart_data["interest_coverage"]

            # Check for deleveraging or increasing debt trends
            debt_change = debt_ratios[-1] - debt_ratios[0]
            if abs(debt_change) > 0.3:  # Significant change
                if debt_change < 0:
                    expected.append("deleveraging_trend")
                else:
                    expected.append("increasing_debt_trend")

            # Check for high debt periods
            if any(ratio > 1.2 for ratio in debt_ratios):
                expected.append("high_debt_periods")

            # Check for interest coverage concerns
            if any(cov < 4.0 for cov in coverage_ratios):
                expected.append("interest_coverage_concern")

            # Ensure at least one pattern is identifiable
            if not expected:
                expected.append("debt_analysis_required")

        elif pattern_type == PatternType.GROWTH_INDICATORS:
            # Analyze growth patterns
            roe_values = chart_data["roe"]
            revenue_growth = chart_data["revenue_growth"]

            # Check for consistent strong ROE
            recent_roe = roe_values[-4:]  # Last 4 quarters
            if sum(roe > 15.0 for roe in recent_roe) >= 3:
                expected.append("consistent_strong_roe")

            # Check for ROE improvement trend
            roe_change = roe_values[-1] - roe_values[0]
            if roe_change > 2.0:
                expected.append("roe_improvement_trend")

            # Check for healthy revenue growth
            recent_growth = revenue_growth[-4:]
            avg_growth = sum(recent_growth) / len(recent_growth)
            if avg_growth > 8.0:
                expected.append("healthy_revenue_growth")

            # Ensure at least one pattern is identifiable
            if not expected:
                expected.append("growth_analysis_required")

        elif pattern_type == PatternType.VALUE_TRAPS:
            # Analyze value trap patterns
            pe_ratios = chart_data["pe_ratio"]
            roe_values = chart_data["roe"]

            # Check for consistently low valuation
            avg_pe = sum(pe_ratios) / len(pe_ratios)
            if avg_pe < 12.0:
                expected.append("low_valuation")

            # Check for deteriorating fundamentals
            roe_change = roe_values[-1] - roe_values[0]
            if roe_change < -2.0:
                expected.append("deteriorating_fundamentals")

            # Check for potential value trap (low PE + poor fundamentals)
            if avg_pe < 10.0 and sum(roe_values[-4:]) / 4 < 10.0:
                expected.append("potential_value_trap")

            # Ensure at least one pattern is identifiable
            if not expected:
                expected.append("valuation_analysis_required")

        return expected

    def _generate_stage_appropriate_hints(
        self, pattern_type: PatternType, difficulty: ExerciseDifficulty
    ) -> List[str]:
        """Generate hints appropriate for the user's learning stage"""

        base_hints = {
            PatternType.DEBT_ANALYSIS: [
                "Look for debt-to-equity ratio trends over time",
                "Check if interest coverage is declining with debt increases",
                "Consider liquidity ratios alongside debt levels",
                "Indian infrastructure companies often show cyclical debt patterns",
            ],
            PatternType.GROWTH_INDICATORS: [
                "Focus on ROE consistency and trend direction",
                "Look for correlation between revenue growth and margin expansion",
                "Strong companies maintain >15% ROE consistently",
                "Indian IT companies typically show different patterns than manufacturing",
            ],
            PatternType.VALUE_TRAPS: [
                "Low P/E doesn't always mean good value",
                "Check if fundamentals are deteriorating behind low valuations",
                "Look for disconnect between price ratios and quality metrics",
                "Cyclical companies can show misleading valuations at cycle peaks",
            ],
        }

        hints = base_hints.get(pattern_type, [])

        if difficulty == ExerciseDifficulty.GUIDED:
            # Return all hints for maximum guidance
            return hints
        elif difficulty == ExerciseDifficulty.ASSISTED:
            # Return subset of hints
            return hints[:2]
        elif difficulty == ExerciseDifficulty.INDEPENDENT:
            # Return minimal hints
            return hints[:1] if hints else []
        else:  # MASTERY
            # No hints - they should teach others
            return []

    def _create_educational_context(
        self,
        pattern_type: PatternType,
        company_example: Dict,
        difficulty: ExerciseDifficulty,
    ) -> str:
        """Create educational context for the exercise"""

        base_context = {
            PatternType.DEBT_ANALYSIS: f"""
            You are analyzing the debt patterns of {company_example['company']} ({company_example['ticker']}) 
            from the {company_example['sector']} sector during {company_example['pattern_period']}.
            
            {company_example['description']}
            
            Focus on identifying debt trends, liquidity concerns, and deleveraging patterns.
            """,
            PatternType.GROWTH_INDICATORS: f"""
            Examine the growth quality indicators for {company_example['company']} ({company_example['ticker']}) 
            in the {company_example['sector']} sector during {company_example['pattern_period']}.
            
            {company_example['description']}
            
            Look for sustainable growth patterns, margin trends, and capital efficiency indicators.
            """,
            PatternType.VALUE_TRAPS: f"""
            Analyze potential value opportunities in {company_example['company']} ({company_example['ticker']}) 
            from the {company_example['sector']} sector during {company_example['pattern_period']}.
            
            {company_example['description']}
            
            Distinguish between genuine value opportunities and potential value traps.
            """,
        }

        context = base_context.get(pattern_type, "")

        if difficulty == ExerciseDifficulty.MASTERY:
            context += "\n\nAfter completing this exercise, prepare to explain your analysis to help other users learn."

        return context.strip()

    def _define_success_criteria(
        self, difficulty: ExerciseDifficulty, expected_patterns: List[str]
    ) -> Dict[str, Any]:
        """Define success criteria based on difficulty level"""

        criteria = {
            ExerciseDifficulty.GUIDED: {
                "minimum_accuracy": 0.6,
                "required_patterns": min(1, len(expected_patterns)),
                "allow_false_positives": True,
                "time_bonus_threshold": None,
            },
            ExerciseDifficulty.ASSISTED: {
                "minimum_accuracy": 0.7,
                "required_patterns": min(2, len(expected_patterns)),
                "allow_false_positives": True,
                "time_bonus_threshold": 300,  # 5 minutes
            },
            ExerciseDifficulty.INDEPENDENT: {
                "minimum_accuracy": 0.8,
                "required_patterns": max(1, len(expected_patterns) - 1),
                "allow_false_positives": False,
                "time_bonus_threshold": 180,  # 3 minutes
            },
            ExerciseDifficulty.MASTERY: {
                "minimum_accuracy": 0.9,
                "required_patterns": len(expected_patterns),
                "allow_false_positives": False,
                "time_bonus_threshold": 120,  # 2 minutes
                "teaching_component_required": True,
            },
        }

        return criteria.get(difficulty, criteria[ExerciseDifficulty.GUIDED])

    def _generate_exercise_title(
        self,
        pattern_type: PatternType,
        company_example: Dict,
        difficulty: ExerciseDifficulty,
    ) -> str:
        """Generate descriptive title for the exercise"""

        pattern_names = {
            PatternType.DEBT_ANALYSIS: "Debt Analysis",
            PatternType.GROWTH_INDICATORS: "Growth Quality",
            PatternType.VALUE_TRAPS: "Value Assessment",
        }

        difficulty_prefixes = {
            ExerciseDifficulty.GUIDED: "Guided",
            ExerciseDifficulty.ASSISTED: "Assisted",
            ExerciseDifficulty.INDEPENDENT: "Independent",
            ExerciseDifficulty.MASTERY: "Master",
        }

        pattern_name = pattern_names.get(pattern_type, "Pattern")
        difficulty_prefix = difficulty_prefixes.get(difficulty, "")

        return f"{difficulty_prefix} {pattern_name}: {company_example['company']} ({company_example['ticker']})"

    def _generate_exercise_description(
        self, pattern_type: PatternType, difficulty: ExerciseDifficulty
    ) -> str:
        """Generate description for the exercise"""

        descriptions = {
            PatternType.DEBT_ANALYSIS: "Identify debt patterns, liquidity concerns, and deleveraging trends in the financial data.",
            PatternType.GROWTH_INDICATORS: "Recognize sustainable growth patterns, margin trends, and capital efficiency indicators.",
            PatternType.VALUE_TRAPS: "Distinguish between genuine value opportunities and potential value traps in the valuation metrics.",
        }

        base_description = descriptions.get(
            pattern_type, "Analyze the financial patterns in the given data."
        )

        if difficulty == ExerciseDifficulty.MASTERY:
            base_description += " Prepare to teach your findings to other users."

        return base_description

    def _calculate_time_limit(self, difficulty: ExerciseDifficulty) -> int:
        """Calculate appropriate time limit based on difficulty"""

        time_limits = {
            ExerciseDifficulty.GUIDED: 600,  # 10 minutes
            ExerciseDifficulty.ASSISTED: 450,  # 7.5 minutes
            ExerciseDifficulty.INDEPENDENT: 300,  # 5 minutes
            ExerciseDifficulty.MASTERY: 240,  # 4 minutes
        }

        return time_limits.get(difficulty, 600)

    def evaluate_pattern_recognition_attempt(
        self, exercise_id: str, attempt: PatternAttempt
    ) -> PatternFeedback:
        """
        Evaluate a user's pattern recognition attempt and provide feedback

        Args:
            exercise_id: ID of the exercise being attempted
            attempt: User's pattern recognition attempt

        Returns:
            PatternFeedback with detailed evaluation and recommendations
        """
        if exercise_id not in self.exercise_cache:
            raise ValueError(f"Exercise {exercise_id} not found in cache")

        exercise = self.exercise_cache[exercise_id]

        # Calculate accuracy score
        accuracy_score = self._calculate_accuracy(exercise, attempt)

        # Identify correct, missed, and false positive patterns
        correct_patterns = []
        missed_patterns = []
        false_positives = []

        for pattern in exercise.expected_patterns:
            if pattern in attempt.identified_patterns:
                correct_patterns.append(pattern)
            else:
                missed_patterns.append(pattern)

        for pattern in attempt.identified_patterns:
            if pattern not in exercise.expected_patterns:
                false_positives.append(pattern)

        # Generate educational explanation
        educational_explanation = self._generate_educational_explanation(
            exercise, attempt, correct_patterns, missed_patterns
        )

        # Generate improvement suggestions
        improvement_suggestions = self._generate_improvement_suggestions(
            exercise, missed_patterns, false_positives
        )

        # Calculate stage progression impact
        stage_progression_impact = self._calculate_stage_progression_impact(
            accuracy_score, exercise.difficulty, attempt.attempt_time_seconds
        )

        # Recommend next exercise
        next_exercise_recommendation = self._recommend_next_exercise(
            accuracy_score, exercise.difficulty, exercise.pattern_type
        )

        feedback = PatternFeedback(
            attempt_id=f"{exercise_id}_{attempt.user_session_id}_{datetime.now(timezone.utc).timestamp()}",
            accuracy_score=accuracy_score,
            correct_patterns=correct_patterns,
            missed_patterns=missed_patterns,
            false_positives=false_positives,
            educational_explanation=educational_explanation,
            improvement_suggestions=improvement_suggestions,
            stage_progression_impact=stage_progression_impact,
            next_exercise_recommendation=next_exercise_recommendation,
        )

        return feedback

    def _calculate_accuracy(
        self, exercise: PatternExercise, attempt: PatternAttempt
    ) -> float:
        """Calculate accuracy score for the pattern recognition attempt"""

        if not exercise.expected_patterns:
            return 0.0

        # Calculate precision and recall
        true_positives = len(
            set(attempt.identified_patterns) & set(exercise.expected_patterns)
        )
        false_positives = len(
            set(attempt.identified_patterns) - set(exercise.expected_patterns)
        )
        false_negatives = len(
            set(exercise.expected_patterns) - set(attempt.identified_patterns)
        )

        if true_positives == 0 and false_positives == 0 and false_negatives == 0:
            return 0.0

        # Calculate F1 score as accuracy measure
        precision = (
            true_positives / (true_positives + false_positives)
            if (true_positives + false_positives) > 0
            else 0
        )
        recall = (
            true_positives / (true_positives + false_negatives)
            if (true_positives + false_negatives) > 0
            else 0
        )

        if precision + recall == 0:
            return 0.0

        f1_score = 2 * (precision * recall) / (precision + recall)

        # Apply time bonus/penalty
        time_factor = 1.0
        if exercise.time_limit_seconds:
            time_ratio = attempt.attempt_time_seconds / exercise.time_limit_seconds
            if time_ratio < 0.5:  # Completed quickly
                time_factor = 1.1
            elif time_ratio > 1.0:  # Over time limit
                time_factor = 0.9

        return min(f1_score * time_factor, 1.0)

    def _generate_educational_explanation(
        self,
        exercise: PatternExercise,
        attempt: PatternAttempt,
        correct_patterns: List[str],
        missed_patterns: List[str],
    ) -> str:
        """Generate educational explanation based on the attempt"""

        explanations = []

        if correct_patterns:
            explanations.append(
                f"✅ Well done! You correctly identified: {', '.join(correct_patterns)}"
            )

        if missed_patterns:
            explanations.append(
                f"📚 Learning opportunity - You missed: {', '.join(missed_patterns)}"
            )

            # Add specific explanations for missed patterns
            pattern_explanations = {
                "deleveraging_trend": "The debt-to-equity ratio showed a declining trend, indicating the company was reducing its debt burden over time.",
                "increasing_debt_trend": "The debt levels were rising, which could indicate expansion phase or potential overleveraging.",
                "high_debt_periods": "There were periods where debt-to-equity exceeded 1.5x, indicating high leverage.",
                "interest_coverage_concern": "Interest coverage fell below 3x, suggesting potential difficulty in servicing debt.",
                "consistent_strong_roe": "The company maintained ROE above 15% consistently, indicating strong profitability.",
                "roe_improvement_trend": "ROE showed an improving trend over time, suggesting increasing efficiency.",
                "healthy_revenue_growth": "Revenue growth averaged above 10%, indicating strong business momentum.",
                "low_valuation": "P/E ratios were consistently below 12x, suggesting the stock was trading at low multiples.",
                "deteriorating_fundamentals": "ROE was declining significantly, indicating weakening business fundamentals.",
                "potential_value_trap": "The combination of low valuation and deteriorating fundamentals suggests a potential value trap.",
            }

            for pattern in missed_patterns:
                if pattern in pattern_explanations:
                    explanations.append(f"💡 {pattern_explanations[pattern]}")

        # Add sector-specific context
        if exercise.ticker in ["RELIANCE", "BHARTIARTL", "ADANIPORTS"]:
            explanations.append(
                "🏭 Remember: Infrastructure and telecom companies often have different debt patterns due to capital intensity."
            )
        elif exercise.ticker in ["TCS", "HDFC", "ASIANPAINT"]:
            explanations.append(
                "💼 Context: These are typically high-quality companies with strong fundamental patterns."
            )
        elif exercise.ticker in ["YESBANK", "SUZLON", "JETAIRWAYS"]:
            explanations.append(
                "⚠️ Important: These examples show how attractive valuations can mask underlying problems."
            )

        return " ".join(explanations)

    def _generate_improvement_suggestions(
        self,
        exercise: PatternExercise,
        missed_patterns: List[str],
        false_positives: List[str],
    ) -> List[str]:
        """Generate specific suggestions for improvement"""

        suggestions = []

        if missed_patterns:
            if exercise.pattern_type == PatternType.DEBT_ANALYSIS:
                suggestions.extend(
                    [
                        "Focus on the relationship between debt levels and interest coverage",
                        "Look for consistent trends rather than single-quarter fluctuations",
                        "Consider the sector context when evaluating debt levels",
                    ]
                )
            elif exercise.pattern_type == PatternType.GROWTH_INDICATORS:
                suggestions.extend(
                    [
                        "Pay attention to consistency of performance metrics",
                        "Look for correlation between different growth metrics",
                        "Consider sustainability of growth patterns",
                    ]
                )
            elif exercise.pattern_type == PatternType.VALUE_TRAPS:
                suggestions.extend(
                    [
                        "Always check fundamentals when you see low valuations",
                        "Look for declining trends in quality metrics",
                        "Consider whether low multiples reflect temporary or permanent issues",
                    ]
                )

        if false_positives:
            suggestions.append(
                "Review the data more carefully to avoid identifying patterns that aren't clearly present"
            )

        if exercise.difficulty == ExerciseDifficulty.GUIDED and (
            missed_patterns or false_positives
        ):
            suggestions.append(
                "Take advantage of the hints and highlighted areas to guide your analysis"
            )
        elif exercise.difficulty == ExerciseDifficulty.MASTERY:
            suggestions.append(
                "At the mastery level, focus on subtle patterns and prepare to explain your reasoning to others"
            )

        return suggestions[:3]  # Limit to top 3 suggestions

    def _calculate_stage_progression_impact(
        self, accuracy_score: float, difficulty: ExerciseDifficulty, attempt_time: float
    ) -> float:
        """Calculate impact on learning stage progression"""

        # Base impact from accuracy
        base_impact = accuracy_score * 0.1

        # Bonus for difficulty level
        difficulty_multipliers = {
            ExerciseDifficulty.GUIDED: 1.0,
            ExerciseDifficulty.ASSISTED: 1.2,
            ExerciseDifficulty.INDEPENDENT: 1.5,
            ExerciseDifficulty.MASTERY: 2.0,
        }

        difficulty_bonus = difficulty_multipliers.get(difficulty, 1.0)

        # Time efficiency bonus
        time_bonus = 1.0
        if attempt_time < 120:  # Very quick
            time_bonus = 1.1
        elif attempt_time > 600:  # Very slow
            time_bonus = 0.9

        total_impact = base_impact * difficulty_bonus * time_bonus

        return min(total_impact, 0.3)  # Cap at 0.3 points per exercise

    def _recommend_next_exercise(
        self,
        accuracy_score: float,
        current_difficulty: ExerciseDifficulty,
        current_pattern_type: PatternType,
    ) -> Optional[str]:
        """Recommend next exercise based on performance"""

        if accuracy_score >= 0.8:
            # Good performance - can progress
            if current_difficulty == ExerciseDifficulty.GUIDED:
                return f"Try an assisted {current_pattern_type.value} exercise"
            elif current_difficulty == ExerciseDifficulty.ASSISTED:
                return f"Ready for independent {current_pattern_type.value} exercises"
            elif current_difficulty == ExerciseDifficulty.INDEPENDENT:
                return "Consider mastery level exercises or try different pattern types"
            else:
                return "Explore different pattern types or help teach other users"

        elif accuracy_score >= 0.6:
            # Moderate performance - same level or different pattern
            other_patterns = [pt for pt in PatternType if pt != current_pattern_type]
            if other_patterns:
                return f"Try {random.choice(other_patterns).value} exercises at the same difficulty level"
            else:
                return "Practice more exercises at the current difficulty level"

        else:
            # Poor performance - step back or get more guidance
            if current_difficulty != ExerciseDifficulty.GUIDED:
                return "Consider trying guided exercises to build fundamentals"
            else:
                return "Review the educational materials and try similar exercises"

        return None

    def create_interactive_chart_overlay(
        self, exercise: PatternExercise
    ) -> Dict[str, Any]:
        """
        Create Plotly chart with interactive pattern recognition overlay

        Args:
            exercise: PatternExercise object containing chart data and zones

        Returns:
            Dictionary containing Plotly figure configuration and interaction zones
        """

        # Create base Plotly figure
        fig = go.Figure()

        chart_data = exercise.chart_data

        # Add traces based on pattern type
        if exercise.pattern_type == PatternType.DEBT_ANALYSIS:
            self._add_debt_analysis_traces(fig, chart_data)
        elif exercise.pattern_type == PatternType.GROWTH_INDICATORS:
            self._add_growth_indicator_traces(fig, chart_data)
        elif exercise.pattern_type == PatternType.VALUE_TRAPS:
            self._add_value_trap_traces(fig, chart_data)

        # Add interactive zones based on difficulty
        if exercise.difficulty == ExerciseDifficulty.GUIDED:
            self._add_guided_overlays(fig, exercise.pattern_zones, chart_data)
        elif exercise.difficulty == ExerciseDifficulty.ASSISTED:
            self._add_assisted_overlays(fig, exercise.pattern_zones, chart_data)

        # Configure layout
        fig.update_layout(
            title=f"{exercise.title} - Click to Identify Patterns",
            xaxis_title="Time Period",
            yaxis_title="Metric Value",
            hovermode="x unified",
            showlegend=True,
            height=500,
            margin=dict(t=60, b=40, l=60, r=40),
        )

        # Convert to JSON for frontend
        chart_json = plotly.utils.PlotlyJSONEncoder().encode(fig)

        return {
            "chart_json": chart_json,
            "exercise_id": exercise.exercise_id,
            "pattern_zones": exercise.pattern_zones,
            "expected_patterns": exercise.expected_patterns,
            "hints": exercise.hints,
            "time_limit": exercise.time_limit_seconds,
        }

    def _add_debt_analysis_traces(self, fig: go.Figure, chart_data: Dict[str, Any]):
        """Add debt analysis traces to the figure"""

        # Debt-to-Equity ratio
        fig.add_trace(
            go.Scatter(
                x=chart_data["quarters"],
                y=chart_data["debt_to_equity"],
                mode="lines+markers",
                name="Debt-to-Equity Ratio",
                line=dict(color="red", width=3),
                marker=dict(size=8),
            )
        )

        # Interest Coverage
        fig.add_trace(
            go.Scatter(
                x=chart_data["quarters"],
                y=chart_data["interest_coverage"],
                mode="lines+markers",
                name="Interest Coverage",
                line=dict(color="blue", width=3),
                marker=dict(size=8),
                yaxis="y2",
            )
        )

        # Current Ratio
        fig.add_trace(
            go.Scatter(
                x=chart_data["quarters"],
                y=chart_data["current_ratio"],
                mode="lines+markers",
                name="Current Ratio",
                line=dict(color="green", width=3),
                marker=dict(size=8),
                yaxis="y3",
            )
        )

        # Add reference lines
        fig.add_hline(
            y=1.5,
            line_dash="dash",
            line_color="red",
            annotation_text="Debt-to-Equity: 1.5 (Concern Level)",
        )

        # Configure multiple y-axes
        fig.update_layout(
            yaxis=dict(title="Debt-to-Equity Ratio", side="left"),
            yaxis2=dict(
                title="Interest Coverage", side="right", overlaying="y", position=0.95
            ),
            yaxis3=dict(
                title="Current Ratio", side="right", overlaying="y", position=1.0
            ),
        )

    def _add_growth_indicator_traces(self, fig: go.Figure, chart_data: Dict[str, Any]):
        """Add growth indicator traces to the figure"""

        # ROE
        fig.add_trace(
            go.Scatter(
                x=chart_data["quarters"],
                y=chart_data["roe"],
                mode="lines+markers",
                name="Return on Equity (%)",
                line=dict(color="darkgreen", width=3),
                marker=dict(size=8),
            )
        )

        # Revenue Growth
        fig.add_trace(
            go.Scatter(
                x=chart_data["quarters"],
                y=chart_data["revenue_growth"],
                mode="lines+markers",
                name="Revenue Growth (%)",
                line=dict(color="blue", width=3),
                marker=dict(size=8),
            )
        )

        # Operating Margin
        fig.add_trace(
            go.Scatter(
                x=chart_data["quarters"],
                y=chart_data["operating_margin"],
                mode="lines+markers",
                name="Operating Margin (%)",
                line=dict(color="purple", width=3),
                marker=dict(size=8),
            )
        )

        # Add reference lines
        fig.add_hline(
            y=15.0,
            line_dash="dash",
            line_color="green",
            annotation_text="ROE: 15% (Strong Performance)",
        )
        fig.add_hline(
            y=10.0,
            line_dash="dash",
            line_color="blue",
            annotation_text="Revenue Growth: 10% (Healthy)",
        )

    def _add_value_trap_traces(self, fig: go.Figure, chart_data: Dict[str, Any]):
        """Add value trap analysis traces to the figure"""

        # P/E Ratio
        fig.add_trace(
            go.Scatter(
                x=chart_data["quarters"],
                y=chart_data["pe_ratio"],
                mode="lines+markers",
                name="P/E Ratio",
                line=dict(color="orange", width=3),
                marker=dict(size=8),
            )
        )

        # P/B Ratio
        fig.add_trace(
            go.Scatter(
                x=chart_data["quarters"],
                y=chart_data["pb_ratio"],
                mode="lines+markers",
                name="P/B Ratio",
                line=dict(color="red", width=3),
                marker=dict(size=8),
                yaxis="y2",
            )
        )

        # ROE for quality assessment
        fig.add_trace(
            go.Scatter(
                x=chart_data["quarters"],
                y=chart_data["roe"],
                mode="lines+markers",
                name="ROE (%)",
                line=dict(color="green", width=3),
                marker=dict(size=8),
                yaxis="y3",
            )
        )

        # Add reference lines
        fig.add_hline(
            y=10.0,
            line_dash="dash",
            line_color="orange",
            annotation_text="P/E: 10x (Low Valuation)",
        )

        # Configure multiple y-axes
        fig.update_layout(
            yaxis=dict(title="P/E Ratio", side="left"),
            yaxis2=dict(title="P/B Ratio", side="right", overlaying="y", position=0.95),
            yaxis3=dict(title="ROE (%)", side="right", overlaying="y", position=1.0),
        )

    def _add_guided_overlays(
        self,
        fig: go.Figure,
        pattern_zones: List[Dict[str, Any]],
        chart_data: Dict[str, Any],
    ):
        """Add overlays for guided difficulty level with enhanced visual cues"""
        
        # Color map for different pattern types
        pattern_colors = {
            "debt_concern": "rgba(255, 99, 71, 0.15)",      # Tomato red
            "strong_performance": "rgba(50, 205, 50, 0.15)", # Lime green
            "value_trap_signal": "rgba(255, 165, 0, 0.15)", # Orange
            "default": "rgba(100, 149, 237, 0.15)"          # Cornflower blue
        }

        for zone in pattern_zones:
            if zone.get("pattern_strength") == "strong":
                # Add highlighting for obvious patterns
                if "period_index" in zone:
                    period_idx = zone["period_index"]
                    zone_type = zone.get("type", "default")
                    fill_color = pattern_colors.get(zone_type, pattern_colors["default"])
                    
                    # Add shaded region around the pattern period (±1 period)
                    fig.add_vrect(
                        x0=max(0, period_idx - 1),
                        x1=min(len(chart_data.get("quarters", [])) - 1, period_idx + 1),
                        fillcolor=fill_color,
                        layer="below",
                        line_width=0,
                        annotation_text="📍",
                        annotation_position="top",
                    )

                    # Highlight specific point with bright color and hover text
                    fig.add_vline(
                        x=period_idx,
                        line_dash="dot",
                        line_color="rgba(255, 165, 0, 0.8)",  # Bright orange
                        line_width=3,
                    )

                    # Calculate proper y position based on first available data series
                    y_position = 0
                    if "debt_to_equity" in chart_data:
                        y_position = chart_data["debt_to_equity"][
                            min(period_idx, len(chart_data["debt_to_equity"]) - 1)
                        ]
                    elif "roe" in chart_data:
                        y_position = chart_data["roe"][
                            min(period_idx, len(chart_data["roe"]) - 1)
                        ]
                    elif "pe_ratio" in chart_data:
                        y_position = chart_data["pe_ratio"][
                            min(period_idx, len(chart_data["pe_ratio"]) - 1)
                        ]

                    # Add a pulsing marker for the hint (stylized as target)
                    fig.add_trace(
                        go.Scatter(
                            x=[
                                chart_data["quarters"][
                                    min(period_idx, len(chart_data["quarters"]) - 1)
                                ]
                            ],
                            y=[y_position],
                            mode="markers",
                            marker=dict(
                                size=20,
                                color="rgba(255, 165, 0, 0.6)",
                                symbol="circle",
                                line=dict(width=2, color="orange")
                            ),
                            name="💡 Pattern Zone",
                            hovertemplate=f"<b>🎯 Pattern Hint:</b><br>{zone.get('hint', 'Important pattern area')}<extra></extra>",
                            showlegend=True,
                        )
                    )

    def _add_assisted_overlays(
        self,
        fig: go.Figure,
        pattern_zones: List[Dict[str, Any]],
        chart_data: Dict[str, Any],
    ):
        """Add overlays for assisted difficulty level"""

        for i, zone in enumerate(pattern_zones):
            if "period_range" in zone:
                # Add shaded regions for pattern identification
                start_idx, end_idx = zone["period_range"]
                fig.add_vrect(
                    x0=(
                        chart_data["quarters"][start_idx]
                        if start_idx < len(chart_data["quarters"])
                        else start_idx
                    ),
                    x1=(
                        chart_data["quarters"][end_idx]
                        if end_idx < len(chart_data["quarters"])
                        else end_idx
                    ),
                    fillcolor="rgba(135, 206, 250, 0.3)",  # Light blue with transparency
                    opacity=0.4,
                    line_width=2,
                    line_color="rgba(70, 130, 180, 0.8)",
                    # Remove immediate annotation to prevent overlap
                )

                # Add hover indicator in the middle of the zone
                mid_idx = (start_idx + end_idx) // 2
                mid_idx = min(mid_idx, len(chart_data["quarters"]) - 1)

                # Calculate proper y position based on first available data series
                y_position = 0
                if "debt_to_equity" in chart_data:
                    y_position = chart_data["debt_to_equity"][mid_idx]
                elif "roe" in chart_data:
                    y_position = chart_data["roe"][mid_idx]
                elif "pe_ratio" in chart_data:
                    y_position = chart_data["pe_ratio"][mid_idx]

                fig.add_trace(
                    go.Scatter(
                        x=[chart_data["quarters"][mid_idx]],
                        y=[y_position],
                        mode="markers",
                        marker=dict(
                            size=12, color="rgba(70, 130, 180, 0.6)", symbol="square"
                        ),
                        name=f"💡 Pattern Zone {i+1}",
                        hovertemplate=f"<b>Pattern Zone:</b><br>{zone.get('hint', 'Look for patterns in this area')}<extra></extra>",
                        showlegend=False,
                    )
                )

    def evaluate_attempt(
        self,
        exercise_id: str,
        user_patterns: List[str],
        user_session_id: str,
        time_taken_seconds: int,
    ) -> PatternFeedback:
        """
        Evaluate user's pattern recognition attempt and provide feedback

        Args:
            exercise_id: ID of the exercise being evaluated
            user_patterns: List of pattern IDs identified by user
            user_session_id: User identifier for tracking
            time_taken_seconds: Time taken to complete the exercise

        Returns:
            PatternFeedback with score, accuracy, and educational feedback
        """
        # Retrieve the exercise (prefer cache, fallback to stored retrieval)
        exercise = self.exercise_cache.get(exercise_id)

        if exercise is None:
            try:
                exercise = self._get_stored_exercise(exercise_id)
            except Exception:
                # Could not retrieve exercise - return a clear feedback object
                return PatternFeedback(
                    attempt_id=f"{exercise_id}_{user_session_id}_{int(time_taken_seconds)}",
                    accuracy_score=0.0,
                    correct_patterns=[],
                    missed_patterns=[],
                    false_positives=list(user_patterns),
                    educational_explanation=(
                        "Exercise not found or invalid. Unable to evaluate the attempt."
                    ),
                    improvement_suggestions=[],
                    stage_progression_impact=0.0,
                    next_exercise_recommendation=None,
                )

        # Ensure exercise exposes expected_patterns
        expected_patterns = getattr(exercise, "expected_patterns", None)
        if not expected_patterns or not isinstance(expected_patterns, list):
            return PatternFeedback(
                attempt_id=f"{exercise_id}_{user_session_id}_{int(time_taken_seconds)}",
                accuracy_score=0.0,
                correct_patterns=[],
                missed_patterns=[],
                false_positives=list(user_patterns),
                educational_explanation=(
                    "Exercise does not contain expected patterns. Cannot evaluate."
                ),
                improvement_suggestions=[],
                stage_progression_impact=0.0,
                next_exercise_recommendation=None,
            )

        # Compare user-identified patterns against expected patterns
        correct_patterns = list(set(user_patterns) & set(expected_patterns))
        missed_patterns = list(set(expected_patterns) - set(user_patterns))
        false_positives = list(set(user_patterns) - set(expected_patterns))

        # Basic accuracy: proportion of expected patterns identified
        accuracy = (
            len(correct_patterns) / len(expected_patterns) if expected_patterns else 0.0
        )

        # Penalize for false positives (small penalty per false positive)
        if false_positives:
            accuracy *= max(0.0, 1 - (len(false_positives) * 0.1))

        # Time-based bonus (same heuristic as other evaluation paths)
        time_bonus = max(0, 10 - (time_taken_seconds / 60))
        # Compose a human-friendly explanation
        if accuracy >= 0.9:
            feedback_msg = "Excellent pattern recognition! You identified the key patterns correctly."
        elif accuracy >= 0.7:
            feedback_msg = "Good work! You caught most of the important patterns."
        elif accuracy >= 0.5:
            feedback_msg = "You're on the right track, but missed some key patterns."
        else:
            feedback_msg = (
                "This pattern is tricky - review the fundamentals and try again."
            )

        if missed_patterns:
            feedback_msg += f" Consider looking for: {', '.join(missed_patterns)}."

        if false_positives:
            feedback_msg += f" Be careful about false signals - double-check these patterns: {', '.join(false_positives)}."

        # Suggest improvements
        improvement_suggestions = (
            [
                "Focus on the relationship between debt levels and coverage ratios",
                "Look for sustained trends rather than temporary fluctuations",
                "Consider the broader market context when identifying patterns",
            ]
            if accuracy < 0.8
            else [
                "Excellent pattern recognition skills!",
                "Try more advanced exercises to challenge yourself",
            ]
        )

        return PatternFeedback(
            attempt_id=f"{exercise_id}_{user_session_id}_{int(time_taken_seconds)}",
            accuracy_score=accuracy,
            correct_patterns=correct_patterns,
            missed_patterns=missed_patterns,
            false_positives=false_positives,
            educational_explanation=feedback_msg,
            improvement_suggestions=improvement_suggestions,
            stage_progression_impact=accuracy,
            next_exercise_recommendation=None,
        )

    def _get_stored_exercise(self, exercise_id: str) -> PatternExercise:
        """
        Retrieve stored exercise by ID (mock implementation for testing)
        In production, this would query a database or cache
        """
        # Try DB first
        persisted = self._load_exercise_from_db(exercise_id)
        if persisted is not None:
            return persisted

        # Return a minimal, valid PatternExercise compatible with the dataclass (fallback)
        expected_patterns = ["deleveraging_trend", "high_debt_periods"]

        chart_data = {
            "dates": ["2020-01-01", "2020-04-01", "2020-07-01", "2020-10-01"],
            "quarters": ["Q1 2020", "Q2 2020", "Q3 2020", "Q4 2020"],
            "debt_to_equity": [1.2, 1.1, 1.0, 0.8],
            "interest_coverage": [5.0, 4.5, 6.0, 7.0],
        }

        success_criteria = self._define_success_criteria(
            ExerciseDifficulty.GUIDED, expected_patterns
        )

        return PatternExercise(
            exercise_id=exercise_id,
            pattern_type=PatternType.DEBT_ANALYSIS,
            difficulty=ExerciseDifficulty.GUIDED,
            title="Mock Debt Analysis Exercise",
            description="Mock exercise for testing debt patterns",
            ticker="MOCK",
            company_name="Mock Company",
            chart_data=chart_data,
            pattern_zones=[],
            expected_patterns=expected_patterns,
            hints=["Look for decreasing debt-to-equity trend"],
            educational_context="Mock context for testing",
            success_criteria=success_criteria,
            time_limit_seconds=900,
        )

    def _generate_educational_feedback(
        self,
        pattern_type: PatternType,
        identified_patterns: List[str],
        missed_patterns: List[str],
        accuracy: float,
        difficulty: ExerciseDifficulty,
    ) -> str:
        """Generate educational feedback based on attempt results"""

        feedback_base = {
            PatternType.DEBT_ANALYSIS: {
                "focus": "debt management and leverage patterns",
                "key_metrics": "debt-to-equity ratio, interest coverage",
                "tips": "Look for trends over time, not just absolute values",
            },
            PatternType.GROWTH_INDICATORS: {
                "focus": "sustainable growth patterns",
                "key_metrics": "ROE trends, revenue growth consistency",
                "tips": "Quality of growth matters more than just high numbers",
            },
            PatternType.VALUE_TRAPS: {
                "focus": "distinguishing value from value traps",
                "key_metrics": "P/E ratios with fundamental deterioration",
                "tips": "Low valuation + declining fundamentals = potential trap",
            },
        }

        pattern_info = feedback_base[pattern_type]

        if accuracy >= 0.8:
            return f"Excellent understanding of {pattern_info['focus']}! Your pattern recognition skills are strong."
        else:
            return f"Focus on {pattern_info['focus']} using {pattern_info['key_metrics']}. Tip: {pattern_info['tips']}"

    def get_exercise_progress_summary(self, user_session_id: str) -> Dict[str, Any]:
        """Get summary of user's pattern recognition exercise progress"""

        # This would typically query a database, but for now return a structure
        # that could be populated from actual user attempts

        return {
            "total_exercises_attempted": 0,
            "exercises_by_pattern_type": {
                PatternType.DEBT_ANALYSIS.value: {"attempted": 0, "avg_accuracy": 0.0},
                PatternType.GROWTH_INDICATORS.value: {
                    "attempted": 0,
                    "avg_accuracy": 0.0,
                },
                PatternType.VALUE_TRAPS.value: {"attempted": 0, "avg_accuracy": 0.0},
            },
            "exercises_by_difficulty": {
                ExerciseDifficulty.GUIDED.value: {"attempted": 0, "avg_accuracy": 0.0},
                ExerciseDifficulty.ASSISTED.value: {
                    "attempted": 0,
                    "avg_accuracy": 0.0,
                },
                ExerciseDifficulty.INDEPENDENT.value: {
                    "attempted": 0,
                    "avg_accuracy": 0.0,
                },
                ExerciseDifficulty.MASTERY.value: {"attempted": 0, "avg_accuracy": 0.0},
            },
            "overall_accuracy": 0.0,
            "current_stage_recommendation": ExerciseDifficulty.GUIDED.value,
            "next_recommended_pattern": PatternType.DEBT_ANALYSIS.value,
        }
