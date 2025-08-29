"""
Educational Mastery Framework for Stock Fundamental Analysis Platform

This module implements the 4-stage learning progression system that adapts content
and interface based on user behavioral analytics. The framework provides privacy-first
behavioral tracking and stage-appropriate educational content delivery.
"""

import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime, timedelta


class LearningStage(Enum):
    """Learning progression stages for financial education"""

    GUIDED_DISCOVERY = "guided_discovery"  # Stage 1: 2-4 weeks
    ASSISTED_ANALYSIS = "assisted_analysis"  # Stage 2: 4-8 weeks
    INDEPENDENT_THINKING = "independent_thinking"  # Stage 3: 8-16 weeks
    ANALYTICAL_MASTERY = "analytical_mastery"  # Stage 4: Ongoing


class InteractionType(Enum):
    """Types of user interactions tracked for learning assessment"""

    TOOLTIP_USAGE = "tooltip_usage"
    WARNING_ENGAGEMENT = "warning_engagement"
    RESEARCH_GUIDE_ACCESS = "research_guide_access"
    COMMUNITY_CONTRIBUTION = "community_contribution"
    ANALYSIS_COMPLETION = "analysis_completion"
    CROSS_STOCK_COMPARISON = "cross_stock_comparison"
    PREDICTION_ATTEMPT = "prediction_attempt"


@dataclass
class BehavioralData:
    """Data structure for tracking user behavioral analytics"""

    interaction_type: InteractionType
    timestamp: float
    duration_seconds: float
    context: Dict[str, Any]
    session_id: str


@dataclass
class LearningStageProfile:
    """Profile configuration for each learning stage"""

    stage: LearningStage
    duration_weeks: Tuple[int, int]  # (min_weeks, max_weeks)
    tooltip_dependency_threshold: float  # 0.0 to 1.0
    analysis_depth_threshold: float
    pattern_recognition_threshold: float
    teaching_contribution_threshold: float
    ui_adaptations: Dict[str, Any]
    content_complexity: str  # "basic", "intermediate", "advanced", "expert"


@dataclass
class StageAssessmentResult:
    """Result of learning stage assessment"""

    current_stage: LearningStage
    confidence_score: float  # 0.0 to 1.0
    progress_within_stage: float  # 0.0 to 1.0
    next_stage_readiness: float  # 0.0 to 1.0
    behavioral_scores: Dict[str, float]
    recommendations: List[str]


class EducationalMasteryFramework:
    """
    Core framework for assessing user learning stages and providing adaptive educational content.

    The framework tracks user behavioral analytics to automatically categorize users into
    one of 4 learning stages and provides stage-appropriate content and interface elements.
    """

    def __init__(self):
        """Initialize the Educational Mastery Framework"""
        self.stage_profiles = self._initialize_stage_profiles()
        self.behavioral_history_days = 7  # Rolling window for data retention
        self.min_interactions_for_assessment = (
            5  # Minimum interactions needed for stage assessment
        )

    def _initialize_stage_profiles(self) -> Dict[LearningStage, LearningStageProfile]:
        """Initialize learning stage profile configurations"""

        return {
            LearningStage.GUIDED_DISCOVERY: LearningStageProfile(
                stage=LearningStage.GUIDED_DISCOVERY,
                duration_weeks=(2, 4),
                tooltip_dependency_threshold=0.8,
                analysis_depth_threshold=0.2,
                pattern_recognition_threshold=0.1,
                teaching_contribution_threshold=0.0,
                ui_adaptations={
                    "show_tooltips": True,
                    "simplified_language": True,
                    "basic_educational_content": True,
                    "guided_tutorials": True,
                    "explanation_depth": "detailed",
                },
                content_complexity="basic",
            ),
            LearningStage.ASSISTED_ANALYSIS: LearningStageProfile(
                stage=LearningStage.ASSISTED_ANALYSIS,
                duration_weeks=(4, 8),
                tooltip_dependency_threshold=0.5,
                analysis_depth_threshold=0.5,
                pattern_recognition_threshold=0.3,
                teaching_contribution_threshold=0.1,
                ui_adaptations={
                    "show_tooltips": True,
                    "simplified_language": False,
                    "pattern_highlighting": True,
                    "guided_research": True,
                    "explanation_depth": "moderate",
                },
                content_complexity="intermediate",
            ),
            LearningStage.INDEPENDENT_THINKING: LearningStageProfile(
                stage=LearningStage.INDEPENDENT_THINKING,
                duration_weeks=(8, 16),
                tooltip_dependency_threshold=0.3,
                analysis_depth_threshold=0.7,
                pattern_recognition_threshold=0.6,
                teaching_contribution_threshold=0.3,
                ui_adaptations={
                    "show_tooltips": False,
                    "advanced_content": True,
                    "confidence_building": True,
                    "peer_insights": True,
                    "explanation_depth": "concise",
                },
                content_complexity="advanced",
            ),
            LearningStage.ANALYTICAL_MASTERY: LearningStageProfile(
                stage=LearningStage.ANALYTICAL_MASTERY,
                duration_weeks=(16, 52),
                tooltip_dependency_threshold=0.1,
                analysis_depth_threshold=0.9,
                pattern_recognition_threshold=0.8,
                teaching_contribution_threshold=0.7,
                ui_adaptations={
                    "show_tooltips": False,
                    "expert_mode": True,
                    "teaching_tools": True,
                    "advanced_pattern_recognition": True,
                    "explanation_depth": "minimal",
                },
                content_complexity="expert",
            ),
        }

    def track_user_behavior(
        self,
        session_data: Dict,
        interaction_type: InteractionType,
        interaction_data: Dict,
    ) -> None:
        """
        Track user behavioral interaction for learning assessment

        Args:
            session_data: Flask session data (mutable)
            interaction_type: Type of interaction being tracked
            interaction_data: Specific data about the interaction
        """
        current_time = time.time()
        session_id = session_data.get("anonymous_user_id", "unknown")

        # Initialize behavioral tracking in session if not present
        if "behavioral_history" not in session_data:
            session_data["behavioral_history"] = []

        # Create behavioral data entry
        behavioral_entry = {
            "interaction_type": interaction_type.value,
            "timestamp": current_time,
            "duration_seconds": interaction_data.get("duration", 0),
            "context": interaction_data.get("context", {}),
            "session_id": session_id,
        }

        # Add to session history
        session_data["behavioral_history"].append(behavioral_entry)

        # Maintain rolling window (keep only last 7 days)
        cutoff_time = current_time - (self.behavioral_history_days * 24 * 3600)
        session_data["behavioral_history"] = [
            entry
            for entry in session_data["behavioral_history"]
            if entry["timestamp"] > cutoff_time
        ]

        # Update last activity timestamp
        session_data["last_educational_activity"] = current_time

    def assess_learning_stage(self, session_data: Dict) -> StageAssessmentResult:
        """
        Assess user's current learning stage based on behavioral analytics

        Args:
            session_data: Flask session data containing behavioral history

        Returns:
            StageAssessmentResult with current stage and progress metrics
        """
        behavioral_history = session_data.get("behavioral_history", [])

        # If insufficient data, default to guided discovery
        if len(behavioral_history) < self.min_interactions_for_assessment:
            return StageAssessmentResult(
                current_stage=LearningStage.GUIDED_DISCOVERY,
                confidence_score=0.3,
                progress_within_stage=0.0,
                next_stage_readiness=0.0,
                behavioral_scores={
                    "tooltip_dependency": 1.0,
                    "analysis_depth": 0.0,
                    "pattern_recognition": 0.0,
                    "teaching_contribution": 0.0,
                },
                recommendations=[
                    "Continue exploring basic analysis features",
                    "Click on tooltips to learn about financial ratios",
                    "Pay attention to warning explanations",
                ],
            )

        # Calculate behavioral scores
        behavioral_scores = self._calculate_behavioral_scores(behavioral_history)

        # Determine current stage based on behavioral patterns
        current_stage = self._determine_stage_from_scores(behavioral_scores)

        # Calculate progress metrics
        progress_metrics = self._calculate_progress_metrics(
            behavioral_scores, current_stage, behavioral_history
        )

        # Generate stage-appropriate recommendations
        recommendations = self._generate_recommendations(
            current_stage, behavioral_scores
        )

        return StageAssessmentResult(
            current_stage=current_stage,
            confidence_score=progress_metrics["confidence"],
            progress_within_stage=progress_metrics["progress_within_stage"],
            next_stage_readiness=progress_metrics["next_stage_readiness"],
            behavioral_scores=behavioral_scores,
            recommendations=recommendations,
        )

    def _calculate_behavioral_scores(
        self, behavioral_history: List[Dict]
    ) -> Dict[str, float]:
        """Calculate behavioral analytics scores from interaction history"""

        if not behavioral_history:
            return {
                "tooltip_dependency": 1.0,
                "analysis_depth": 0.0,
                "pattern_recognition": 0.0,
                "teaching_contribution": 0.0,
            }

        # Count interactions by type (with error handling)
        interaction_counts = {}
        valid_interactions = 0

        for entry in behavioral_history:
            # Skip malformed entries
            if (
                not entry
                or not isinstance(entry, dict)
                or "interaction_type" not in entry
            ):
                continue

            interaction_type = entry["interaction_type"]
            interaction_counts[interaction_type] = (
                interaction_counts.get(interaction_type, 0) + 1
            )
            valid_interactions += 1

        # Use valid interactions count for calculations
        total_interactions = max(1, valid_interactions)

        # Calculate tooltip dependency score (inverse - less usage = more advanced)
        tooltip_usage = interaction_counts.get(InteractionType.TOOLTIP_USAGE.value, 0)
        tooltip_dependency = min(1.0, tooltip_usage / max(1, total_interactions * 0.5))

        # Calculate analysis depth score
        analysis_interactions = (
            interaction_counts.get(InteractionType.WARNING_ENGAGEMENT.value, 0)
            + interaction_counts.get(InteractionType.RESEARCH_GUIDE_ACCESS.value, 0)
            + interaction_counts.get(InteractionType.ANALYSIS_COMPLETION.value, 0)
        )
        analysis_depth = min(
            1.0, analysis_interactions / max(1, total_interactions * 0.4)
        )

        # Calculate pattern recognition score
        pattern_interactions = interaction_counts.get(
            InteractionType.CROSS_STOCK_COMPARISON.value, 0
        ) + interaction_counts.get(InteractionType.PREDICTION_ATTEMPT.value, 0)
        pattern_recognition = min(
            1.0, pattern_interactions / max(1, total_interactions * 0.3)
        )

        # Calculate teaching contribution score
        teaching_interactions = interaction_counts.get(
            InteractionType.COMMUNITY_CONTRIBUTION.value, 0
        )
        teaching_contribution = min(
            1.0, teaching_interactions / max(1, total_interactions * 0.15)
        )

        return {
            "tooltip_dependency": tooltip_dependency,
            "analysis_depth": analysis_depth,
            "pattern_recognition": pattern_recognition,
            "teaching_contribution": teaching_contribution,
        }

    def _determine_stage_from_scores(
        self, behavioral_scores: Dict[str, float]
    ) -> LearningStage:
        """Determine learning stage based on behavioral scores"""

        tooltip_dep = behavioral_scores["tooltip_dependency"]
        analysis_depth = behavioral_scores["analysis_depth"]
        pattern_rec = behavioral_scores["pattern_recognition"]
        teaching_contrib = behavioral_scores["teaching_contribution"]

        # Stage 4: Analytical Mastery - Very low tooltip dependency, very high in analysis and patterns
        if (
            tooltip_dep < 0.15
            and analysis_depth > 0.85
            and pattern_rec > 0.75
            and teaching_contrib > 0.65
        ):
            return LearningStage.ANALYTICAL_MASTERY

        # Stage 3: Independent Thinking - Low tooltip dependency, good analysis and patterns
        if tooltip_dep < 0.35 and analysis_depth > 0.65 and pattern_rec > 0.5:
            return LearningStage.INDEPENDENT_THINKING

        # Stage 2: Assisted Analysis - Moderate tooltip dependency, moderate analysis depth
        if tooltip_dep < 0.65 and analysis_depth > 0.35:
            return LearningStage.ASSISTED_ANALYSIS

        # Stage 1: Guided Discovery - Default for high tooltip dependency or low engagement
        return LearningStage.GUIDED_DISCOVERY

    def _calculate_progress_metrics(
        self,
        behavioral_scores: Dict[str, float],
        current_stage: LearningStage,
        behavioral_history: List[Dict],
    ) -> Dict[str, float]:
        """Calculate progress metrics within current stage"""

        profile = self.stage_profiles[current_stage]

        # Calculate confidence score based on behavioral pattern consistency
        score_consistency = self._calculate_score_consistency(
            behavioral_scores, profile
        )
        confidence = min(1.0, score_consistency * 0.8 + len(behavioral_history) * 0.02)

        # Calculate progress within current stage
        progress_within_stage = self._calculate_stage_progress(
            behavioral_scores, profile
        )

        # Calculate readiness for next stage
        next_stage_readiness = self._calculate_next_stage_readiness(
            behavioral_scores, current_stage
        )

        return {
            "confidence": confidence,
            "progress_within_stage": progress_within_stage,
            "next_stage_readiness": next_stage_readiness,
        }

    def _calculate_score_consistency(
        self, behavioral_scores: Dict[str, float], profile: LearningStageProfile
    ) -> float:
        """Calculate how well behavioral scores match stage profile"""

        tooltip_match = 1.0 - abs(
            behavioral_scores["tooltip_dependency"]
            - profile.tooltip_dependency_threshold
        )
        analysis_match = 1.0 - abs(
            behavioral_scores["analysis_depth"] - profile.analysis_depth_threshold
        )
        pattern_match = 1.0 - abs(
            behavioral_scores["pattern_recognition"]
            - profile.pattern_recognition_threshold
        )
        teaching_match = 1.0 - abs(
            behavioral_scores["teaching_contribution"]
            - profile.teaching_contribution_threshold
        )

        return (tooltip_match + analysis_match + pattern_match + teaching_match) / 4.0

    def _calculate_stage_progress(
        self, behavioral_scores: Dict[str, float], profile: LearningStageProfile
    ) -> float:
        """Calculate progress within the current learning stage"""

        # Progress is based on how much behavioral scores exceed stage thresholds
        tooltip_progress = max(
            0,
            profile.tooltip_dependency_threshold
            - behavioral_scores["tooltip_dependency"],
        )
        analysis_progress = max(
            0, behavioral_scores["analysis_depth"] - profile.analysis_depth_threshold
        )
        pattern_progress = max(
            0,
            behavioral_scores["pattern_recognition"]
            - profile.pattern_recognition_threshold,
        )
        teaching_progress = max(
            0,
            behavioral_scores["teaching_contribution"]
            - profile.teaching_contribution_threshold,
        )

        average_progress = (
            tooltip_progress + analysis_progress + pattern_progress + teaching_progress
        ) / 4.0
        return min(1.0, average_progress * 2.0)  # Scale to 0-1 range

    def _calculate_next_stage_readiness(
        self, behavioral_scores: Dict[str, float], current_stage: LearningStage
    ) -> float:
        """Calculate readiness to progress to next learning stage"""

        stage_order = list(LearningStage)
        current_index = stage_order.index(current_stage)

        # If already at highest stage, return current mastery level
        if current_index >= len(stage_order) - 1:
            return min(
                1.0,
                (
                    behavioral_scores["analysis_depth"]
                    + behavioral_scores["pattern_recognition"]
                    + behavioral_scores["teaching_contribution"]
                )
                / 3.0,
            )

        # Get next stage requirements
        next_stage = stage_order[current_index + 1]
        next_profile = self.stage_profiles[next_stage]

        # Calculate readiness based on meeting next stage thresholds
        tooltip_ready = (
            behavioral_scores["tooltip_dependency"]
            <= next_profile.tooltip_dependency_threshold
        )
        analysis_ready = (
            behavioral_scores["analysis_depth"] >= next_profile.analysis_depth_threshold
        )
        pattern_ready = (
            behavioral_scores["pattern_recognition"]
            >= next_profile.pattern_recognition_threshold
        )
        teaching_ready = (
            behavioral_scores["teaching_contribution"]
            >= next_profile.teaching_contribution_threshold
        )

        readiness_score = (
            sum([tooltip_ready, analysis_ready, pattern_ready, teaching_ready]) / 4.0
        )
        return readiness_score

    def _generate_recommendations(
        self, current_stage: LearningStage, behavioral_scores: Dict[str, float]
    ) -> List[str]:
        """Generate stage-appropriate learning recommendations"""

        recommendations = []

        if current_stage == LearningStage.GUIDED_DISCOVERY:
            recommendations.extend(
                [
                    "Explore tooltips to understand financial ratio meanings",
                    "Read warning explanations carefully to build foundational knowledge",
                    "Complete analysis for multiple stocks to see patterns",
                ]
            )

            if behavioral_scores["analysis_depth"] < 0.3:
                recommendations.append(
                    "Click on info buttons (ℹ️) in warnings section for detailed explanations"
                )

        elif current_stage == LearningStage.ASSISTED_ANALYSIS:
            recommendations.extend(
                [
                    "Use research guides from educational gap-filling system",
                    "Start comparing ratios across different stocks in the same industry",
                    "Engage with community insights to learn from others",
                ]
            )

            if behavioral_scores["pattern_recognition"] < 0.4:
                recommendations.append(
                    "Try analyzing companies in the same sector to identify patterns"
                )

        elif current_stage == LearningStage.INDEPENDENT_THINKING:
            recommendations.extend(
                [
                    "Make predictions about stock performance before seeing analysis results",
                    "Contribute insights to the community knowledge base",
                    "Use advanced research guides for deeper analysis",
                ]
            )

            if behavioral_scores["teaching_contribution"] < 0.5:
                recommendations.append(
                    "Share your analysis insights with the community"
                )

        elif current_stage == LearningStage.ANALYTICAL_MASTERY:
            recommendations.extend(
                [
                    "Mentor newer users by providing high-quality community insights",
                    "Develop your own analysis frameworks using advanced tools",
                    "Explore complex cross-stock and cross-sector analysis patterns",
                ]
            )

        return recommendations

    def get_stage_appropriate_content(
        self, assessment_result: StageAssessmentResult, analysis_context: Dict
    ) -> Dict[str, Any]:
        """
        Get stage-appropriate content and UI adaptations

        Args:
            assessment_result: Current stage assessment
            analysis_context: Context about current analysis (company, ratios, etc.)

        Returns:
            Dictionary with stage-appropriate content and UI settings
        """
        profile = self.stage_profiles[assessment_result.current_stage]

        # Base content configuration
        content_config = {
            "ui_adaptations": profile.ui_adaptations.copy(),
            "content_complexity": profile.content_complexity,
            "stage_info": {
                "current_stage": assessment_result.current_stage.value,
                "stage_name": self._get_stage_display_name(
                    assessment_result.current_stage
                ),
                "progress_within_stage": assessment_result.progress_within_stage,
                "next_stage_readiness": assessment_result.next_stage_readiness,
                "confidence_score": assessment_result.confidence_score,
            },
            "recommendations": assessment_result.recommendations,
            "learning_prompts": self._get_stage_learning_prompts(
                assessment_result.current_stage
            ),
        }

        # Adapt tooltips based on stage
        if assessment_result.current_stage in [
            LearningStage.GUIDED_DISCOVERY,
            LearningStage.ASSISTED_ANALYSIS,
        ]:
            content_config["tooltip_complexity"] = "detailed"
            content_config["show_educational_tooltips"] = True
        else:
            content_config["tooltip_complexity"] = "concise"
            content_config["show_educational_tooltips"] = False

        # Adapt educational content based on stage
        content_config["educational_content"] = self._get_stage_educational_content(
            assessment_result.current_stage, analysis_context
        )

        return content_config

    def _get_stage_display_name(self, stage: LearningStage) -> str:
        """Get human-readable stage name"""
        stage_names = {
            LearningStage.GUIDED_DISCOVERY: "Guided Discovery",
            LearningStage.ASSISTED_ANALYSIS: "Assisted Analysis",
            LearningStage.INDEPENDENT_THINKING: "Independent Thinking",
            LearningStage.ANALYTICAL_MASTERY: "Analytical Mastery",
        }
        return stage_names.get(stage, "Unknown Stage")

    def _get_stage_learning_prompts(self, stage: LearningStage) -> List[str]:
        """Get learning prompts appropriate for current stage"""

        prompts = {
            LearningStage.GUIDED_DISCOVERY: [
                "💡 Try clicking on tooltips to learn what each financial ratio means",
                "📚 Read the warning explanations to understand potential risks",
                "🔍 Look for patterns in the financial data visualization",
            ],
            LearningStage.ASSISTED_ANALYSIS: [
                "🎯 Use research guides to dive deeper into analysis gaps",
                "📊 Compare this stock with others in the same industry",
                "🤝 Check community insights for different perspectives",
            ],
            LearningStage.INDEPENDENT_THINKING: [
                "🚀 Make your own predictions before seeing analysis results",
                "💭 Share your insights with the community",
                "🔗 Look for connections between different financial metrics",
            ],
            LearningStage.ANALYTICAL_MASTERY: [
                "🎓 Mentor others by providing detailed community insights",
                "⚡ Develop advanced analysis techniques",
                "🌟 Lead by example in analytical thinking",
            ],
        }

        return prompts.get(stage, [])

    def _get_stage_educational_content(
        self, stage: LearningStage, analysis_context: Dict
    ) -> Dict[str, Any]:
        """Get stage-appropriate educational content"""

        company_name = analysis_context.get("company_name", "this company")

        content = {
            LearningStage.GUIDED_DISCOVERY: {
                "focus": "Understanding Basics",
                "key_concepts": [
                    "Financial Ratios",
                    "Risk Indicators",
                    "Company Health",
                ],
                "suggested_actions": [
                    f"Learn what each ratio means for {company_name}",
                    "Understand why certain warnings appear",
                    "Explore the relationship between different metrics",
                ],
            },
            LearningStage.ASSISTED_ANALYSIS: {
                "focus": "Developing Analysis Skills",
                "key_concepts": [
                    "Pattern Recognition",
                    "Industry Comparison",
                    "Research Methods",
                ],
                "suggested_actions": [
                    f"Research {company_name}'s competitive position",
                    "Compare ratios with industry peers",
                    "Use research guides for deeper investigation",
                ],
            },
            LearningStage.INDEPENDENT_THINKING: {
                "focus": "Building Confidence",
                "key_concepts": [
                    "Independent Analysis",
                    "Prediction Making",
                    "Knowledge Sharing",
                ],
                "suggested_actions": [
                    f"Form your own opinion about {company_name}",
                    "Make predictions and test your analysis skills",
                    "Contribute insights to help others learn",
                ],
            },
            LearningStage.ANALYTICAL_MASTERY: {
                "focus": "Teaching and Leading",
                "key_concepts": [
                    "Advanced Techniques",
                    "Mentoring",
                    "Framework Development",
                ],
                "suggested_actions": [
                    f"Develop comprehensive analysis framework for {company_name}",
                    "Teach others through high-quality insights",
                    "Pioneer new analytical approaches",
                ],
            },
        }

        return content.get(stage, content[LearningStage.GUIDED_DISCOVERY])

    def update_stage_progress(
        self, session_data: Dict, user_actions: List[Dict]
    ) -> None:
        """
        Update learning stage progress based on user actions

        Args:
            session_data: Flask session data (mutable)
            user_actions: List of recent user actions to process
        """
        for action in user_actions:
            interaction_type = InteractionType(action["type"])
            interaction_data = {
                "duration": action.get("duration", 0),
                "context": action.get("context", {}),
            }

            self.track_user_behavior(session_data, interaction_type, interaction_data)

        # Update cached stage assessment if enough new interactions
        if len(user_actions) >= 3:
            assessment = self.assess_learning_stage(session_data)
            session_data["cached_stage_assessment"] = {
                "assessment": assessment.__dict__,
                "timestamp": time.time(),
            }

    def get_cached_assessment(
        self, session_data: Dict
    ) -> Optional[StageAssessmentResult]:
        """Get cached stage assessment if still valid"""
        cached = session_data.get("cached_stage_assessment")
        if not cached:
            return None

        # Cache is valid for 1 hour
        if time.time() - cached["timestamp"] > 3600:
            return None

        # Reconstruct assessment result from cached data
        cached_data = cached["assessment"]
        return StageAssessmentResult(
            current_stage=LearningStage(cached_data["current_stage"]),
            confidence_score=cached_data["confidence_score"],
            progress_within_stage=cached_data["progress_within_stage"],
            next_stage_readiness=cached_data["next_stage_readiness"],
            behavioral_scores=cached_data["behavioral_scores"],
            recommendations=cached_data["recommendations"],
        )
