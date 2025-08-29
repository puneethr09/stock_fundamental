"""
Behavioral Analytics Tracker

This module provides session-based behavioral tracking that integrates with the
Educational Mastery Framework to enable anonymous learning stage assessment.
Enhanced with gamification integration for achievement tracking.
"""

import time
import json
from typing import Dict, List, Optional, Any
from functools import wraps
from flask import session, request
from .educational_framework import (
    EducationalMasteryFramework,
    InteractionType,
    LearningStage,
    StageAssessmentResult,
)
from .gamified_progress_tracker import (
    GamifiedProgressTracker,
    AchievementContext,
    BadgeType,
)


class BehavioralAnalyticsTracker:
    """
    Session-based behavioral analytics tracker for educational framework integration
    Enhanced with gamification and achievement tracking
    """

    def __init__(self):
        """Initialize the behavioral analytics tracker with gamification"""
        self.framework = EducationalMasteryFramework()
        self.gamification = GamifiedProgressTracker(self.framework)
        self.interaction_start_times = {}  # Track interaction start times

    def track_interaction_start(
        self, session_id: str, interaction_type: InteractionType
    ) -> None:
        """Track the start of an interaction for duration calculation"""
        self.interaction_start_times[f"{session_id}_{interaction_type.value}"] = (
            time.time()
        )

    def track_interaction_end(
        self, interaction_type: InteractionType, context: Optional[Dict] = None
    ) -> None:
        """
        Track the end of an interaction and log it to the educational framework
        Enhanced with gamification achievement processing

        Args:
            interaction_type: Type of interaction that ended
            context: Additional context about the interaction
        """
        if "anonymous_user_id" not in session:
            return  # Skip tracking if no session

        session_id = session["anonymous_user_id"]
        start_key = f"{session_id}_{interaction_type.value}"

        # Calculate duration if we have a start time
        duration = 0
        if start_key in self.interaction_start_times:
            duration = time.time() - self.interaction_start_times[start_key]
            del self.interaction_start_times[start_key]

        # Track the behavior in the framework
        interaction_data = {"duration": duration, "context": context or {}}
        self.framework.track_user_behavior(session, interaction_type, interaction_data)

        # Process gamification achievements
        self._process_gamification_achievements(
            session_id, interaction_type, duration, context or {}
        )

    def track_tooltip_usage(self, tooltip_id: str, tooltip_content: str) -> None:
        """Track tooltip usage for learning stage assessment"""
        try:
            self.track_interaction_end(
                InteractionType.TOOLTIP_USAGE,
                {
                    "tooltip_id": tooltip_id,
                    "content_length": len(tooltip_content),
                    "page": (
                        request.endpoint
                        if request and hasattr(request, "endpoint")
                        else "unknown"
                    ),
                },
            )
        except RuntimeError:
            # Handle case where we're outside request context (e.g., in tests)
            self.track_interaction_end(
                InteractionType.TOOLTIP_USAGE,
                {
                    "tooltip_id": tooltip_id,
                    "content_length": len(tooltip_content),
                    "page": "test_context",
                },
            )

    def track_warning_engagement(
        self, warning_type: str, engagement_duration: float
    ) -> None:
        """Track user engagement with financial warnings"""
        try:
            self.track_interaction_end(
                InteractionType.WARNING_ENGAGEMENT,
                {
                    "warning_type": warning_type,
                    "engagement_duration": engagement_duration,
                    "page": (
                        request.endpoint
                        if request and hasattr(request, "endpoint")
                        else "unknown"
                    ),
                },
            )
        except RuntimeError:
            # Handle case where we're outside request context (e.g., in tests)
            self.track_interaction_end(
                InteractionType.WARNING_ENGAGEMENT,
                {
                    "warning_type": warning_type,
                    "engagement_duration": engagement_duration,
                    "page": "test_context",
                },
            )

    def track_research_guide_access(
        self, guide_type: str, guide_complexity: str
    ) -> None:
        """Track access to research guides from gap-filling service"""
        try:
            self.track_interaction_end(
                InteractionType.RESEARCH_GUIDE_ACCESS,
                {
                    "guide_type": guide_type,
                    "complexity": guide_complexity,
                    "page": (
                        request.endpoint
                        if request and hasattr(request, "endpoint")
                        else "unknown"
                    ),
                },
            )
        except RuntimeError:
            # Handle case where we're outside request context (e.g., in tests)
            self.track_interaction_end(
                InteractionType.RESEARCH_GUIDE_ACCESS,
                {
                    "guide_type": guide_type,
                    "complexity": guide_complexity,
                    "page": "test_context",
                },
            )

    def track_community_contribution(
        self, contribution_type: str, content_length: int
    ) -> None:
        """Track community knowledge base contributions"""
        try:
            self.track_interaction_end(
                InteractionType.COMMUNITY_CONTRIBUTION,
                {
                    "contribution_type": contribution_type,
                    "content_length": content_length,
                    "page": (
                        request.endpoint
                        if request and hasattr(request, "endpoint")
                        else "unknown"
                    ),
                },
            )
        except RuntimeError:
            # Handle case where we're outside request context (e.g., in tests)
            self.track_interaction_end(
                InteractionType.COMMUNITY_CONTRIBUTION,
                {
                    "contribution_type": contribution_type,
                    "content_length": content_length,
                    "page": "test_context",
                },
            )

    def track_analysis_completion(
        self, company_symbol: str, analysis_depth: str
    ) -> None:
        """Track completion of stock analysis"""
        try:
            self.track_interaction_end(
                InteractionType.ANALYSIS_COMPLETION,
                {
                    "company_symbol": company_symbol,
                    "analysis_depth": analysis_depth,
                    "page": (
                        request.endpoint
                        if request and hasattr(request, "endpoint")
                        else "unknown"
                    ),
                },
            )
        except RuntimeError:
            # Handle case where we're outside request context (e.g., in tests)
            self.track_interaction_end(
                InteractionType.ANALYSIS_COMPLETION,
                {
                    "company_symbol": company_symbol,
                    "analysis_depth": analysis_depth,
                    "page": "test_context",
                },
            )

    def track_cross_stock_comparison(self, stocks_compared: List[str]) -> None:
        """Track cross-stock comparison activities"""
        try:
            self.track_interaction_end(
                InteractionType.CROSS_STOCK_COMPARISON,
                {
                    "stocks_compared": stocks_compared,
                    "comparison_count": len(stocks_compared),
                    "page": (
                        request.endpoint
                        if request and hasattr(request, "endpoint")
                        else "unknown"
                    ),
                },
            )
        except RuntimeError:
            # Handle case where we're outside request context (e.g., in tests)
            self.track_interaction_end(
                InteractionType.CROSS_STOCK_COMPARISON,
                {
                    "stocks_compared": stocks_compared,
                    "comparison_count": len(stocks_compared),
                    "page": "test_context",
                },
            )

    def track_prediction_attempt(
        self, prediction_type: str, confidence_level: str
    ) -> None:
        """Track user prediction attempts"""
        try:
            self.track_interaction_end(
                InteractionType.PREDICTION_ATTEMPT,
                {
                    "prediction_type": prediction_type,
                    "confidence_level": confidence_level,
                    "page": (
                        request.endpoint
                        if request and hasattr(request, "endpoint")
                        else "unknown"
                    ),
                },
            )
        except RuntimeError:
            # Handle case where we're outside request context (e.g., in tests)
            self.track_interaction_end(
                InteractionType.PREDICTION_ATTEMPT,
                {
                    "prediction_type": prediction_type,
                    "confidence_level": confidence_level,
                    "page": "test_context",
                },
            )

    def get_current_stage_assessment(self) -> Optional[StageAssessmentResult]:
        """Get current learning stage assessment for the user"""
        if "anonymous_user_id" not in session:
            return None

        # Try to get cached assessment first
        cached_assessment = self.framework.get_cached_assessment(session)
        if cached_assessment:
            return cached_assessment

        # Generate new assessment
        assessment = self.framework.assess_learning_stage(session)

        # Cache the assessment
        session["cached_stage_assessment"] = {
            "assessment": {
                "current_stage": assessment.current_stage.value,
                "confidence_score": assessment.confidence_score,
                "progress_within_stage": assessment.progress_within_stage,
                "next_stage_readiness": assessment.next_stage_readiness,
                "behavioral_scores": assessment.behavioral_scores,
                "recommendations": assessment.recommendations,
            },
            "timestamp": time.time(),
        }

        return assessment

    def get_stage_content_config(
        self, analysis_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Get stage-appropriate content configuration

        Args:
            analysis_context: Context about current analysis

        Returns:
            Content configuration for UI adaptation
        """
        assessment = self.get_current_stage_assessment()
        if not assessment:
            # Return default configuration for new users
            return self._get_default_content_config()

        return self.framework.get_stage_appropriate_content(
            assessment, analysis_context or {}
        )

    def _get_default_content_config(self) -> Dict[str, Any]:
        """Get default content configuration for new users"""
        return {
            "ui_adaptations": {
                "show_tooltips": True,
                "simplified_language": True,
                "basic_educational_content": True,
                "guided_tutorials": True,
                "explanation_depth": "detailed",
            },
            "content_complexity": "basic",
            "stage_info": {
                "current_stage": "guided_discovery",
                "stage_name": "Guided Discovery",
                "progress_within_stage": 0.0,
                "next_stage_readiness": 0.0,
                "confidence_score": 0.3,
            },
            "recommendations": [
                "Explore tooltips to learn about financial ratios",
                "Read warning explanations to understand risks",
                "Complete analysis for multiple stocks to see patterns",
            ],
            "learning_prompts": [
                "💡 Try clicking on tooltips to learn what each financial ratio means",
                "📚 Read the warning explanations to understand potential risks",
                "🔍 Look for patterns in the financial data visualization",
            ],
            "tooltip_complexity": "detailed",
            "show_educational_tooltips": True,
            "educational_content": {
                "focus": "Understanding Basics",
                "key_concepts": [
                    "Financial Ratios",
                    "Risk Indicators",
                    "Company Health",
                ],
                "suggested_actions": [
                    "Learn what each ratio means for this company",
                    "Understand why certain warnings appear",
                    "Explore the relationship between different metrics",
                ],
            },
        }

    def should_show_stage_progress(self) -> bool:
        """Determine if stage progress should be shown to user"""
        assessment = self.get_current_stage_assessment()
        if not assessment:
            return False

        # Show progress if user has sufficient confidence score and interactions
        behavioral_history = session.get("behavioral_history", [])
        return assessment.confidence_score > 0.6 and len(behavioral_history) >= 10

    def get_stage_progress_data(self) -> Optional[Dict[str, Any]]:
        """Get stage progress data for UI display"""
        if not self.should_show_stage_progress():
            return None

        assessment = self.get_current_stage_assessment()
        if not assessment:
            return None

        return {
            "current_stage": assessment.current_stage.value,
            "stage_name": self.framework._get_stage_display_name(
                assessment.current_stage
            ),
            "progress_within_stage": round(assessment.progress_within_stage * 100, 1),
            "next_stage_readiness": round(assessment.next_stage_readiness * 100, 1),
            "confidence_score": round(assessment.confidence_score * 100, 1),
            "behavioral_scores": {
                key: round(score * 100, 1)
                for key, score in assessment.behavioral_scores.items()
            },
            "recommendations": assessment.recommendations[
                :3
            ],  # Limit to top 3 recommendations
        }

    def _process_gamification_achievements(
        self,
        session_id: str,
        interaction_type: InteractionType,
        duration: float,
        context: Dict[str, Any],
    ) -> None:
        """
        Process achievements and update gamification progress based on user interaction

        Args:
            session_id: User session identifier
            interaction_type: Type of interaction completed
            duration: Duration of the interaction
            context: Additional interaction context
        """
        try:
            # Get current learning stage for context
            current_stage = self._get_current_learning_stage(session_id)

            # Prepare completion data for progress update
            completion_data = {
                "session_duration": duration,
                "interaction_type": interaction_type.value,
                "context": context,
            }

            # Update progress based on interaction type
            if interaction_type == InteractionType.ANALYSIS_COMPLETION:
                completion_data.update(
                    {
                        "analysis_completed": True,
                        "skill_improvements": self._extract_skill_improvements(context),
                    }
                )

            elif interaction_type == InteractionType.COMMUNITY_CONTRIBUTION:
                completion_data.update(
                    {
                        "community_contribution": self._calculate_contribution_quality(
                            context
                        )
                    }
                )

            elif interaction_type == InteractionType.RESEARCH_GUIDE_ACCESS:
                completion_data.update(
                    {"research_quality": self._assess_research_engagement(context)}
                )

            # Update progress metrics
            self.gamification.update_progress_metrics(session_id, completion_data)

            # Check for new achievements
            achievement_context = AchievementContext(
                session_id=session_id,
                user_id=session_id,  # Using session_id as anonymous user_id
                current_stage=current_stage,
                behavioral_data=context,
                session_history=self._get_session_history(session_id),
                interaction_counts=self._get_interaction_counts(session_id),
            )

            newly_earned = self.gamification.check_achievement_conditions(
                achievement_context
            )

            # Award new badges
            for badge_type in newly_earned:
                badge = self.gamification.award_badge(badge_type, achievement_context)
                self._store_achievement_notification(session_id, badge)

        except Exception as e:
            # Log error but don't break the main tracking flow
            print(f"Gamification processing error: {e}")

    def _get_current_learning_stage(self, session_id: str) -> LearningStage:
        """Get current learning stage for the user"""
        try:
            assessment = self.framework.assess_learning_stage(
                {"anonymous_user_id": session_id}
            )
            return assessment.current_stage
        except:
            return LearningStage.GUIDED_DISCOVERY

    def _extract_skill_improvements(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Extract skill improvement data from analysis context"""
        improvements = {}

        if "analysis_depth" in context:
            depth = context["analysis_depth"]
            if depth == "comprehensive":
                improvements["debt_analysis"] = 0.1
                improvements["growth_indicators"] = 0.1
                improvements["value_assessment"] = 0.1
            elif depth == "detailed":
                improvements["debt_analysis"] = 0.05
                improvements["growth_indicators"] = 0.05
                improvements["value_assessment"] = 0.05

        return improvements

    def _calculate_contribution_quality(self, context: Dict[str, Any]) -> float:
        """Calculate quality score for community contributions"""
        base_score = 0.5

        if "content_length" in context:
            length = context["content_length"]
            if length > 200:
                base_score = 0.8
            elif length > 100:
                base_score = 0.7

        return base_score

    def _assess_research_engagement(self, context: Dict[str, Any]) -> float:
        """Assess quality of research guide engagement"""
        # Basic implementation - can be enhanced
        return 0.6

    def _get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get historical session data for the user"""
        # Placeholder - would load from localStorage or framework data
        return []

    def _get_interaction_counts(self, session_id: str) -> Dict[InteractionType, int]:
        """Get interaction counts by type for the user"""
        # Placeholder - would calculate from historical data
        return {interaction_type: 0 for interaction_type in InteractionType}

    def _store_achievement_notification(self, session_id: str, badge) -> None:
        """Store achievement notification for UI display"""
        # This would store the notification for display in the UI
        # Implementation would use localStorage or session storage
        pass


# Global tracker instance
behavioral_tracker = BehavioralAnalyticsTracker()


def track_interaction(interaction_type: InteractionType):
    """
    Decorator to automatically track user interactions

    Usage:
        @track_interaction(InteractionType.ANALYSIS_COMPLETION)
        def analyze_stock():
            # Function implementation
            pass
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Track interaction start
            if "anonymous_user_id" in session:
                behavioral_tracker.track_interaction_start(
                    session["anonymous_user_id"], interaction_type
                )

            # Execute the function
            result = f(*args, **kwargs)

            # Track interaction end (will be called by specific tracking methods)
            # The actual end tracking should be done in the function implementation
            # using the specific track_* methods

            return result

        return decorated_function

    return decorator


def track_page_interaction(
    interaction_type: InteractionType, context: Optional[Dict] = None
):
    """
    Function to manually track interactions from JavaScript or form submissions

    Args:
        interaction_type: Type of interaction
        context: Additional context about the interaction
    """
    behavioral_tracker.track_interaction_end(interaction_type, context)


def get_learning_stage_context() -> Dict[str, Any]:
    """
    Get learning stage context for template rendering

    Returns:
        Dictionary with learning stage data for templates
    """
    content_config = behavioral_tracker.get_stage_content_config()
    progress_data = behavioral_tracker.get_stage_progress_data()

    return {
        "learning_stage": content_config,
        "stage_progress": progress_data,
        "show_stage_progress": behavioral_tracker.should_show_stage_progress(),
    }


def adapt_content_for_stage(
    content: Dict[str, Any], analysis_context: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Adapt content based on user's learning stage

    Args:
        content: Base content to adapt
        analysis_context: Context about current analysis

    Returns:
        Adapted content based on learning stage
    """
    stage_config = behavioral_tracker.get_stage_content_config(analysis_context)

    # Apply stage-based adaptations
    adapted_content = content.copy()

    # Adapt tooltip complexity
    if stage_config["tooltip_complexity"] == "concise":
        adapted_content["show_detailed_tooltips"] = False
    else:
        adapted_content["show_detailed_tooltips"] = True

    # Adapt explanation depth
    explanation_depth = stage_config["ui_adaptations"].get(
        "explanation_depth", "moderate"
    )
    adapted_content["explanation_depth"] = explanation_depth

    # Add stage-specific recommendations
    adapted_content["learning_recommendations"] = stage_config.get(
        "recommendations", []
    )

    # Add learning prompts
    adapted_content["learning_prompts"] = stage_config.get("learning_prompts", [])

    return adapted_content
