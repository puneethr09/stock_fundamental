"""
Gamified Progress Tracking System

This module implements badge awards, achievement tracking, and progress visualization
that motivates users through their financial education journey. It integrates with
the Educational Mastery Framework and Behavioral Analytics to provide comprehensive
gamification without compromising privacy or performance.
"""

import json
import time
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from .educational_framework import (
    LearningStage,
    InteractionType,
    EducationalMasteryFramework,
    StageAssessmentResult,
)


class BadgeType(Enum):
    """Types of badges that can be awarded to users"""

    # Analysis milestone badges
    FIRST_ANALYSIS = "first_analysis"
    BRONZE_ANALYST = "bronze_analyst"  # 10 analyses
    SILVER_ANALYST = "silver_analyst"  # 50 analyses
    GOLD_ANALYST = "gold_analyst"  # 100 analyses
    PLATINUM_ANALYST = "platinum_analyst"  # 500 analyses

    # Pattern recognition achievement badges
    DEBT_DETECTIVE = "debt_detective"  # Master debt analysis patterns
    GROWTH_SPOTTER = "growth_spotter"  # Master growth indicators
    VALUE_HUNTER = "value_hunter"  # Master value assessment patterns
    PATTERN_MASTER = "pattern_master"  # Master all pattern types

    # Research mastery badges
    RESEARCH_ROOKIE = "research_rookie"  # Complete first research guide
    RESEARCH_SCHOLAR = "research_scholar"  # Complete 10 research guides
    RESEARCH_EXPERT = "research_expert"  # High-quality research engagement

    # Community contributor badges
    HELPFUL_CONTRIBUTOR = "helpful_contributor"  # Quality community insights
    KNOWLEDGE_SHARER = "knowledge_sharer"  # Multiple quality contributions
    COMMUNITY_LEADER = "community_leader"  # Consistently excellent contributions

    # Learning streak badges
    CONSISTENT_LEARNER = "consistent_learner"  # 7-day streak
    DEDICATED_STUDENT = "dedicated_student"  # 30-day streak
    LEARNING_CHAMPION = "learning_champion"  # 90-day streak

    # Stage progression badges
    DISCOVERY_GRADUATE = "discovery_graduate"  # Graduate from Stage 1
    ANALYSIS_GRADUATE = "analysis_graduate"  # Graduate from Stage 2
    THINKING_GRADUATE = "thinking_graduate"  # Graduate from Stage 3
    MASTERY_ACHIEVED = "mastery_achieved"  # Reach Stage 4


@dataclass
class Badge:
    """Represents an earned badge with metadata"""

    badge_type: BadgeType
    earned_timestamp: float
    context: Dict[str, Any]
    display_name: str
    description: str
    achievement_value: int  # For progress calculation


@dataclass
class ProgressMetrics:
    """Tracks user progress across different skill areas"""

    analysis_count: int = 0
    pattern_recognition_score: float = 0.0
    research_engagement_score: float = 0.0
    community_contribution_score: float = 0.0
    current_streak: int = 0
    best_streak: int = 0
    last_active_date: Optional[str] = None
    total_session_time: float = 0.0
    stage_progression_points: float = 0.0
    skill_competencies: Dict[str, float] = field(default_factory=dict)


@dataclass
class AchievementContext:
    """Context information for achievement evaluation"""

    session_id: str
    user_id: str
    current_stage: LearningStage
    behavioral_data: Dict[str, Any]
    session_history: List[Dict[str, Any]]
    interaction_counts: Dict[InteractionType, int]


class GamifiedProgressTracker:
    """
    Core gamification system that awards badges and tracks progress

    Integrates with EducationalMasteryFramework and BehavioralAnalyticsTracker
    to provide motivation through achievements without impacting performance.
    """

    def __init__(self, educational_framework: EducationalMasteryFramework):
        """Initialize the gamified progress tracker"""
        self.educational_framework = educational_framework

        # Badge definitions with display information
        self.badge_definitions = {
            BadgeType.FIRST_ANALYSIS: {
                "display_name": "First Steps",
                "description": "Completed your first stock analysis",
                "achievement_value": 10,
                "criteria": {"min_analyses": 1},
            },
            BadgeType.BRONZE_ANALYST: {
                "display_name": "Bronze Analyst",
                "description": "Completed 10 stock analyses",
                "achievement_value": 25,
                "criteria": {"min_analyses": 10},
            },
            BadgeType.SILVER_ANALYST: {
                "display_name": "Silver Analyst",
                "description": "Completed 50 stock analyses",
                "achievement_value": 50,
                "criteria": {"min_analyses": 50},
            },
            BadgeType.GOLD_ANALYST: {
                "display_name": "Gold Analyst",
                "description": "Completed 100 stock analyses",
                "achievement_value": 100,
                "criteria": {"min_analyses": 100},
            },
            BadgeType.PLATINUM_ANALYST: {
                "display_name": "Platinum Analyst",
                "description": "Completed 500 stock analyses",
                "achievement_value": 250,
                "criteria": {"min_analyses": 500},
            },
            BadgeType.DEBT_DETECTIVE: {
                "display_name": "Debt Detective",
                "description": "Mastered debt analysis patterns",
                "achievement_value": 75,
                "criteria": {"debt_pattern_mastery": 0.8},
            },
            BadgeType.GROWTH_SPOTTER: {
                "display_name": "Growth Spotter",
                "description": "Mastered growth indicator patterns",
                "achievement_value": 75,
                "criteria": {"growth_pattern_mastery": 0.8},
            },
            BadgeType.VALUE_HUNTER: {
                "display_name": "Value Hunter",
                "description": "Mastered value assessment patterns",
                "achievement_value": 75,
                "criteria": {"value_pattern_mastery": 0.8},
            },
            BadgeType.PATTERN_MASTER: {
                "display_name": "Pattern Master",
                "description": "Mastered all pattern recognition types",
                "achievement_value": 150,
                "criteria": {"all_patterns_mastered": True},
            },
            BadgeType.CONSISTENT_LEARNER: {
                "display_name": "Consistent Learner",
                "description": "Maintained a 7-day learning streak",
                "achievement_value": 30,
                "criteria": {"min_streak": 7},
            },
            BadgeType.DEDICATED_STUDENT: {
                "display_name": "Dedicated Student",
                "description": "Maintained a 30-day learning streak",
                "achievement_value": 100,
                "criteria": {"min_streak": 30},
            },
            BadgeType.LEARNING_CHAMPION: {
                "display_name": "Learning Champion",
                "description": "Maintained a 90-day learning streak",
                "achievement_value": 200,
                "criteria": {"min_streak": 90},
            },
            BadgeType.RESEARCH_ROOKIE: {
                "display_name": "Research Rookie",
                "description": "Completed your first research guide",
                "achievement_value": 20,
                "criteria": {"min_research_guides": 1},
            },
            BadgeType.RESEARCH_SCHOLAR: {
                "display_name": "Research Scholar",
                "description": "Completed 10 research guides",
                "achievement_value": 60,
                "criteria": {"min_research_guides": 10},
            },
            BadgeType.RESEARCH_EXPERT: {
                "display_name": "Research Expert",
                "description": "Demonstrated high-quality research engagement",
                "achievement_value": 100,
                "criteria": {"research_engagement_score": 0.8},
            },
            BadgeType.HELPFUL_CONTRIBUTOR: {
                "display_name": "Helpful Contributor",
                "description": "Made quality contributions to the community",
                "achievement_value": 40,
                "criteria": {"min_contributions": 5},
            },
            BadgeType.KNOWLEDGE_SHARER: {
                "display_name": "Knowledge Sharer",
                "description": "Made multiple quality community contributions",
                "achievement_value": 80,
                "criteria": {"min_contributions": 15},
            },
            BadgeType.COMMUNITY_LEADER: {
                "display_name": "Community Leader",
                "description": "Consistently excellent community contributions",
                "achievement_value": 150,
                "criteria": {"min_contributions": 50, "contribution_quality": 0.9},
            },
            BadgeType.DISCOVERY_GRADUATE: {
                "display_name": "Discovery Graduate",
                "description": "Graduated from Guided Discovery stage",
                "achievement_value": 100,
                "criteria": {"min_stage": LearningStage.ASSISTED_ANALYSIS},
            },
            BadgeType.ANALYSIS_GRADUATE: {
                "display_name": "Analysis Graduate",
                "description": "Graduated from Assisted Analysis stage",
                "achievement_value": 150,
                "criteria": {"min_stage": LearningStage.INDEPENDENT_THINKING},
            },
            BadgeType.THINKING_GRADUATE: {
                "display_name": "Thinking Graduate",
                "description": "Graduated from Independent Thinking stage",
                "achievement_value": 200,
                "criteria": {"min_stage": LearningStage.ANALYTICAL_MASTERY},
            },
            BadgeType.MASTERY_ACHIEVED: {
                "display_name": "Mastery Achieved",
                "description": "Reached Analytical Mastery stage",
                "achievement_value": 300,
                "criteria": {"current_stage": LearningStage.ANALYTICAL_MASTERY},
            },
        }

    def check_achievement_conditions(
        self, context: AchievementContext
    ) -> List[BadgeType]:
        """
        Check what badges the user has earned based on current activity

        Args:
            context: Achievement context with user data and session info

        Returns:
            List of newly earned badge types
        """
        newly_earned = []
        current_badges = self._get_earned_badges(context.user_id)
        earned_badge_types = {badge.badge_type for badge in current_badges}

        progress = self._get_progress_metrics(context.user_id)

        # Check analysis milestone badges
        analysis_badges = [
            (BadgeType.FIRST_ANALYSIS, 1),
            (BadgeType.BRONZE_ANALYST, 10),
            (BadgeType.SILVER_ANALYST, 50),
            (BadgeType.GOLD_ANALYST, 100),
            (BadgeType.PLATINUM_ANALYST, 500),
        ]

        for badge_type, required_count in analysis_badges:
            if (
                badge_type not in earned_badge_types
                and progress.analysis_count >= required_count
            ):
                newly_earned.append(badge_type)

        # Check pattern recognition badges
        skill_competencies = progress.skill_competencies or {}
        if (
            BadgeType.DEBT_DETECTIVE not in earned_badge_types
            and skill_competencies.get("debt_analysis", 0.0) >= 0.8
        ):
            newly_earned.append(BadgeType.DEBT_DETECTIVE)

        if (
            BadgeType.GROWTH_SPOTTER not in earned_badge_types
            and skill_competencies.get("growth_indicators", 0.0) >= 0.8
        ):
            newly_earned.append(BadgeType.GROWTH_SPOTTER)

        if (
            BadgeType.VALUE_HUNTER not in earned_badge_types
            and skill_competencies.get("value_assessment", 0.0) >= 0.8
        ):
            newly_earned.append(BadgeType.VALUE_HUNTER)

        # Check pattern master (requires all three pattern badges)
        pattern_badges = {
            BadgeType.DEBT_DETECTIVE,
            BadgeType.GROWTH_SPOTTER,
            BadgeType.VALUE_HUNTER,
        }
        if (
            BadgeType.PATTERN_MASTER not in earned_badge_types
            and pattern_badges.issubset(earned_badge_types.union(set(newly_earned)))
        ):
            newly_earned.append(BadgeType.PATTERN_MASTER)

        # Check streak badges
        streak_badges = [
            (BadgeType.CONSISTENT_LEARNER, 7),
            (BadgeType.DEDICATED_STUDENT, 30),
            (BadgeType.LEARNING_CHAMPION, 90),
        ]

        for badge_type, required_streak in streak_badges:
            if (
                badge_type not in earned_badge_types
                and progress.current_streak >= required_streak
            ):
                newly_earned.append(badge_type)

        return newly_earned

    def award_badge(self, badge_type: BadgeType, context: AchievementContext) -> Badge:
        """
        Award a specific badge to the user

        Args:
            badge_type: Type of badge to award
            context: Achievement context for the badge

        Returns:
            The awarded Badge object
        """
        badge_def = self.badge_definitions[badge_type]

        badge = Badge(
            badge_type=badge_type,
            earned_timestamp=time.time(),
            context={
                "session_id": context.session_id,
                "stage": context.current_stage.value,
                "behavioral_snapshot": context.behavioral_data,
            },
            display_name=badge_def["display_name"],
            description=badge_def["description"],
            achievement_value=badge_def["achievement_value"],
        )

        # Store badge in localStorage-compatible format
        self._store_badge(context.user_id, badge)

        # Update stage progression points
        self._update_stage_progression_points(
            context.user_id, badge_def["achievement_value"]
        )

        return badge

    def update_progress_metrics(
        self, user_id: str, completion_data: Dict[str, Any]
    ) -> ProgressMetrics:
        """
        Update user progress metrics based on completed activities

        Args:
            user_id: User identifier for progress tracking
            completion_data: Data about completed activities

        Returns:
            Updated progress metrics
        """
        progress = self._get_progress_metrics(user_id)

        # Update analysis count
        if completion_data.get("analysis_completed"):
            progress.analysis_count += 1

        # Update skill competencies
        if "skill_improvements" in completion_data:
            for skill, improvement in completion_data["skill_improvements"].items():
                current_score = progress.skill_competencies.get(skill, 0.0)
                # Add improvement to current score, capped at 1.0
                progress.skill_competencies[skill] = min(
                    1.0, current_score + improvement
                )

        # Update pattern recognition score
        if "pattern_performance" in completion_data:
            pattern_score = completion_data["pattern_performance"]
            progress.pattern_recognition_score = (
                progress.pattern_recognition_score * 0.9 + pattern_score * 0.1
            )

        # Update research engagement
        if "research_quality" in completion_data:
            research_score = completion_data["research_quality"]
            progress.research_engagement_score = (
                progress.research_engagement_score * 0.85 + research_score * 0.15
            )

        # Update community contribution score
        if "community_contribution" in completion_data:
            community_score = completion_data["community_contribution"]
            progress.community_contribution_score = (
                progress.community_contribution_score * 0.9 + community_score * 0.1
            )

        # Update session time
        if "session_duration" in completion_data:
            progress.total_session_time += completion_data["session_duration"]

        # Update learning streak
        today = datetime.now().strftime("%Y-%m-%d")
        if progress.last_active_date:
            last_date = datetime.strptime(progress.last_active_date, "%Y-%m-%d")
            today_date = datetime.strptime(today, "%Y-%m-%d")
            days_diff = (today_date - last_date).days

            if days_diff == 1:
                # Consecutive day - extend streak
                progress.current_streak += 1
                progress.best_streak = max(
                    progress.best_streak, progress.current_streak
                )
            elif days_diff > 1:
                # Streak broken - reset
                progress.current_streak = 1
        else:
            # First day
            progress.current_streak = 1
            progress.best_streak = 1

        progress.last_active_date = today

        # Store updated progress
        self._store_progress_metrics(user_id, progress)

        return progress

    def calculate_learning_streak(
        self, user_id: str, session_history: List[Dict[str, Any]]
    ) -> Tuple[int, int]:
        """
        Calculate current and best learning streaks from session history

        Args:
            user_id: User identifier
            session_history: List of historical session data

        Returns:
            Tuple of (current_streak, best_streak)
        """
        if not session_history:
            return 0, 0

        # Group sessions by date
        daily_sessions = {}
        for session in session_history:
            session_date = datetime.fromtimestamp(session.get("timestamp", 0)).strftime(
                "%Y-%m-%d"
            )

            if session_date not in daily_sessions:
                daily_sessions[session_date] = []
            daily_sessions[session_date].append(session)

        # Calculate streaks by working backwards from most recent date
        sorted_dates = sorted(daily_sessions.keys(), reverse=True)
        current_streak = 0
        best_streak = 0
        temp_streak = 0

        today = datetime.now().strftime("%Y-%m-%d")

        # Calculate current streak (working backwards from today/most recent)
        for i, date in enumerate(sorted_dates):
            if i == 0:
                # Most recent session
                days_from_today = (
                    datetime.now() - datetime.strptime(date, "%Y-%m-%d")
                ).days
                if days_from_today <= 1:  # Today or yesterday
                    current_streak = 1
                    temp_streak = 1
                else:
                    current_streak = 0  # Streak broken
                    break
            else:
                prev_date = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d")
                curr_date = datetime.strptime(date, "%Y-%m-%d")
                days_diff = (prev_date - curr_date).days

                if days_diff == 1:
                    current_streak += 1
                    temp_streak += 1
                else:
                    break  # Current streak ended

        # Calculate best streak (forward pass)
        sorted_dates_forward = sorted(daily_sessions.keys())
        temp_streak = 0

        for i, date in enumerate(sorted_dates_forward):
            if i == 0:
                temp_streak = 1
            else:
                prev_date = datetime.strptime(sorted_dates_forward[i - 1], "%Y-%m-%d")
                curr_date = datetime.strptime(date, "%Y-%m-%d")
                days_diff = (curr_date - prev_date).days

                if days_diff == 1:
                    temp_streak += 1
                else:
                    temp_streak = 1

            best_streak = max(best_streak, temp_streak)

        return current_streak, best_streak

    def get_personalized_goals(
        self,
        user_id: str,
        current_stage: LearningStage,
        recent_activity: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate personalized learning goals based on stage and activity

        Args:
            user_id: User identifier
            current_stage: Current learning stage
            recent_activity: Recent user activity data

        Returns:
            Dictionary of personalized goals and recommendations
        """
        progress = self._get_progress_metrics(user_id)

        goals = {
            "daily_target": self._calculate_daily_target(
                current_stage, recent_activity
            ),
            "weekly_focus": self._determine_weekly_focus(current_stage, progress),
            "skill_priorities": self._identify_skill_priorities(progress),
            "next_badge": self._get_next_achievable_badge(user_id, progress),
            "encouragement": self._generate_encouragement(current_stage, progress),
        }

        return goals

    def display_achievement_showcase(self, user_id: str) -> Dict[str, Any]:
        """
        Generate data for displaying user achievements and progress

        Args:
            user_id: User identifier

        Returns:
            Comprehensive achievement and progress data for UI display
        """
        badges = self._get_earned_badges(user_id)
        progress = self._get_progress_metrics(user_id)

        # Organize badges by category
        badge_categories = {
            "analysis_milestones": [],
            "pattern_mastery": [],
            "research_excellence": [],
            "community_contributions": [],
            "learning_streaks": [],
            "stage_progressions": [],
        }

        category_mapping = {
            BadgeType.FIRST_ANALYSIS: "analysis_milestones",
            BadgeType.BRONZE_ANALYST: "analysis_milestones",
            BadgeType.SILVER_ANALYST: "analysis_milestones",
            BadgeType.GOLD_ANALYST: "analysis_milestones",
            BadgeType.PLATINUM_ANALYST: "analysis_milestones",
            BadgeType.DEBT_DETECTIVE: "pattern_mastery",
            BadgeType.GROWTH_SPOTTER: "pattern_mastery",
            BadgeType.VALUE_HUNTER: "pattern_mastery",
            BadgeType.PATTERN_MASTER: "pattern_mastery",
            BadgeType.CONSISTENT_LEARNER: "learning_streaks",
            BadgeType.DEDICATED_STUDENT: "learning_streaks",
            BadgeType.LEARNING_CHAMPION: "learning_streaks",
        }

        for badge in badges:
            category = category_mapping.get(badge.badge_type, "analysis_milestones")
            badge_categories[category].append(
                {
                    "badge_type": badge.badge_type.value,
                    "display_name": badge.display_name,
                    "description": badge.description,
                    "earned_date": datetime.fromtimestamp(
                        badge.earned_timestamp
                    ).strftime("%Y-%m-%d"),
                    "achievement_value": badge.achievement_value,
                }
            )

        return {
            "badges": badge_categories,
            "progress": {
                "analysis_count": progress.analysis_count,
                "current_streak": progress.current_streak,
                "best_streak": progress.best_streak,
                "total_session_time": round(
                    progress.total_session_time / 3600, 1
                ),  # Hours
                "skill_competencies": progress.skill_competencies,
                "stage_progression_points": progress.stage_progression_points,
            },
            "statistics": {
                "total_badges": len(badges),
                "total_achievement_points": sum(
                    badge.achievement_value for badge in badges
                ),
                "days_active": self._calculate_days_active(user_id),
                "average_session_time": self._calculate_average_session_time(progress),
            },
        }

    def _get_earned_badges(self, user_id: str) -> List[Badge]:
        """Get list of badges earned by user from localStorage"""
        # Load from persistence layer (server-side storage)
        try:
            from .persistence import get_badges_for_user

            rows = get_badges_for_user(user_id)
            badges: List[Badge] = []
            for row in rows:
                payload = row.get("payload", {})
                # payload may already be a dict representation
                badge_type_val = payload.get("badge_type") or row.get("badge_type")
                try:
                    btype = BadgeType(badge_type_val)
                except Exception:
                    continue
                badges.append(
                    Badge(
                        badge_type=btype,
                        earned_timestamp=float(payload.get("earned_timestamp", 0)),
                        context=payload.get("context", {}),
                        display_name=payload.get("display_name", ""),
                        description=payload.get("description", ""),
                        achievement_value=int(payload.get("achievement_value", 0)),
                    )
                )
            return badges
        except Exception:
            return []

    def _store_badge(self, user_id: str, badge: Badge) -> None:
        """Store earned badge in localStorage-compatible format"""
        try:
            from .persistence import save_badge

            payload = {
                "badge_type": badge.badge_type.value,
                "earned_timestamp": badge.earned_timestamp,
                "context": badge.context,
                "display_name": badge.display_name,
                "description": badge.description,
                "achievement_value": badge.achievement_value,
            }
            save_badge(user_id, payload)
        except Exception:
            # Best-effort: swallow persistence errors in dev
            return

    def _get_progress_metrics(self, user_id: str) -> ProgressMetrics:
        """Get user progress metrics from persistence layer or return defaults"""
        try:
            from .persistence import get_progress_metrics

            raw = get_progress_metrics(user_id)
            if not raw:
                return ProgressMetrics(
                    skill_competencies={
                        "debt_analysis": 0.0,
                        "growth_indicators": 0.0,
                        "value_assessment": 0.0,
                    }
                )

            # Build ProgressMetrics from stored dict
            pm = ProgressMetrics()
            pm.analysis_count = int(raw.get("analysis_count", pm.analysis_count))
            pm.pattern_recognition_score = float(
                raw.get("pattern_recognition_score", pm.pattern_recognition_score)
            )
            pm.research_engagement_score = float(
                raw.get("research_engagement_score", pm.research_engagement_score)
            )
            pm.community_contribution_score = float(
                raw.get("community_contribution_score", pm.community_contribution_score)
            )
            pm.current_streak = int(raw.get("current_streak", pm.current_streak))
            pm.best_streak = int(raw.get("best_streak", pm.best_streak))
            pm.last_active_date = raw.get("last_active_date", pm.last_active_date)
            pm.total_session_time = float(
                raw.get("total_session_time", pm.total_session_time)
            )
            pm.stage_progression_points = float(
                raw.get("stage_progression_points", pm.stage_progression_points)
            )
            pm.skill_competencies = raw.get("skill_competencies", pm.skill_competencies)
            return pm
        except Exception:
            return ProgressMetrics(
                skill_competencies={
                    "debt_analysis": 0.0,
                    "growth_indicators": 0.0,
                    "value_assessment": 0.0,
                }
            )

    def _store_progress_metrics(self, user_id: str, progress: ProgressMetrics) -> None:
        """Store progress metrics in localStorage-compatible format"""
        try:
            from .persistence import save_progress_metrics

            payload = {
                "analysis_count": progress.analysis_count,
                "pattern_recognition_score": progress.pattern_recognition_score,
                "research_engagement_score": progress.research_engagement_score,
                "community_contribution_score": progress.community_contribution_score,
                "current_streak": progress.current_streak,
                "best_streak": progress.best_streak,
                "last_active_date": progress.last_active_date,
                "total_session_time": progress.total_session_time,
                "stage_progression_points": progress.stage_progression_points,
                "skill_competencies": progress.skill_competencies,
            }
            save_progress_metrics(user_id, payload)
        except Exception:
            return

    def _update_stage_progression_points(self, user_id: str, points: int) -> None:
        """Update stage progression points for mastery calculation"""
        progress = self._get_progress_metrics(user_id)
        progress.stage_progression_points += points
        self._store_progress_metrics(user_id, progress)

    def _calculate_daily_target(
        self, stage: LearningStage, recent_activity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate personalized daily learning targets"""
        base_targets = {
            LearningStage.GUIDED_DISCOVERY: {"analyses": 1, "minutes": 15},
            LearningStage.ASSISTED_ANALYSIS: {"analyses": 2, "minutes": 25},
            LearningStage.INDEPENDENT_THINKING: {"analyses": 3, "minutes": 35},
            LearningStage.ANALYTICAL_MASTERY: {"analyses": 2, "minutes": 30},
        }

        return base_targets.get(stage, {"analyses": 1, "minutes": 15})

    def _determine_weekly_focus(
        self, stage: LearningStage, progress: ProgressMetrics
    ) -> str:
        """Determine weekly focus area based on stage and progress"""
        if stage == LearningStage.GUIDED_DISCOVERY:
            return "Master basic financial ratio interpretation"
        elif stage == LearningStage.ASSISTED_ANALYSIS:
            return "Develop pattern recognition skills"
        elif stage == LearningStage.INDEPENDENT_THINKING:
            return "Practice independent stock comparison"
        else:
            return "Refine advanced analytical techniques"

    def _identify_skill_priorities(self, progress: ProgressMetrics) -> List[str]:
        """Identify which skills need the most improvement"""
        competencies = progress.skill_competencies
        if not competencies:
            return ["debt_analysis", "growth_indicators", "value_assessment"]

        # Sort by lowest scores first
        sorted_skills = sorted(competencies.items(), key=lambda x: x[1])

        return [skill for skill, score in sorted_skills if score < 0.7]

    def _get_next_achievable_badge(
        self, user_id: str, progress: ProgressMetrics
    ) -> Optional[Dict[str, Any]]:
        """Identify the next badge the user is closest to earning"""
        earned_badges = {badge.badge_type for badge in self._get_earned_badges(user_id)}

        # Analysis milestone badges
        analysis_milestones = [
            (BadgeType.FIRST_ANALYSIS, 1, "Complete 1 more analysis"),
            (
                BadgeType.BRONZE_ANALYST,
                10,
                f"Complete {10 - progress.analysis_count} more analyses",
            ),
            (
                BadgeType.SILVER_ANALYST,
                50,
                f"Complete {50 - progress.analysis_count} more analyses",
            ),
            (
                BadgeType.GOLD_ANALYST,
                100,
                f"Complete {100 - progress.analysis_count} more analyses",
            ),
            (
                BadgeType.PLATINUM_ANALYST,
                500,
                f"Complete {500 - progress.analysis_count} more analyses",
            ),
        ]

        for badge_type, required, description in analysis_milestones:
            if badge_type not in earned_badges and progress.analysis_count < required:
                return {
                    "badge_type": badge_type.value,
                    "display_name": self.badge_definitions[badge_type]["display_name"],
                    "description": description,
                    "progress_percent": min(
                        100, (progress.analysis_count / required) * 100
                    ),
                }

        return None

    def _generate_encouragement(
        self, stage: LearningStage, progress: ProgressMetrics
    ) -> str:
        """Generate personalized encouragement message"""
        if progress.current_streak > 0:
            return f"Great job maintaining your {progress.current_streak}-day learning streak!"
        elif progress.analysis_count > 0:
            return f"You've completed {progress.analysis_count} analyses - keep building your skills!"
        else:
            return "Ready to start your financial analysis journey? Let's begin!"

    def _calculate_days_active(self, user_id: str) -> int:
        """Calculate total number of days user has been active"""
        # Placeholder - would calculate from session history
        return 1

    def _calculate_average_session_time(self, progress: ProgressMetrics) -> float:
        """Calculate average session time in minutes"""
        if progress.analysis_count == 0:
            return 0.0
        return (progress.total_session_time / 60) / max(1, progress.analysis_count)
