"""
Tool Independence Training System for Stock Fundamental Analysis Platform

This module implements challenges that teach users to analyze stocks without relying
on automated tools, developing independent analytical thinking and confidence in
investment decisions through progressive revelation and prediction exercises.
"""

import json
import time
import random
import uuid
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import numpy as np

from src.educational_framework import (
    EducationalMasteryFramework,
    LearningStage,
    InteractionType,
    BehavioralData,
)
from src.pattern_recognition_trainer import PatternType, ExerciseDifficulty


class ChallengeType(Enum):
    """Types of tool independence challenges"""

    RATIO_INTERPRETATION = "ratio_interpretation"
    BLIND_ANALYSIS = "blind_analysis"
    PREDICTION_VALIDATION = "prediction_validation"
    CONFIDENCE_BUILDING = "confidence_building"
    SCENARIO_ANALYSIS = "scenario_analysis"


class PredictionCategory(Enum):
    """Categories for user predictions in blind analysis"""

    FINANCIAL_HEALTH = "financial_health"
    GROWTH_POTENTIAL = "growth_potential"
    RISK_FACTORS = "risk_factors"
    INVESTMENT_DECISION = "investment_decision"


@dataclass
class UserPrediction:
    """Data structure for user predictions"""

    category: PredictionCategory
    prediction: str
    confidence_level: int  # 1-5 scale
    reasoning: str
    timestamp: float


@dataclass
class ChallengeResult:
    """Result data structure for completed challenges"""

    challenge_id: str
    challenge_type: ChallengeType
    user_predictions: List[UserPrediction]
    actual_metrics: Dict[str, Any]
    accuracy_score: float  # 0.0 to 1.0
    reasoning_quality_score: float  # 0.0 to 1.0
    confidence_progression: float  # -1.0 to 1.0
    completion_time: float
    educational_feedback: List[str]


@dataclass
class ToolIndependenceChallenge:
    """Data structure representing a tool independence challenge"""

    challenge_id: str
    challenge_type: ChallengeType
    difficulty_level: int  # 1-4 corresponding to learning stages
    title: str
    description: str
    company_symbol: str
    company_basic_info: Dict[str, Any]
    hidden_metrics: Dict[str, Any]
    prediction_prompts: List[Dict[str, str]]
    reveal_sequence: List[str]
    success_criteria: Dict[str, float]
    educational_context: Dict[str, Any]


class ToolIndependenceTrainer:
    """
    Core system for tool independence training challenges.

    Provides stage-appropriate challenges that teach users to analyze stocks
    using reasoning and pattern recognition rather than relying on automated tools.
    """

    def __init__(self):
        """Initialize the Tool Independence Trainer"""
        self.educational_framework = EducationalMasteryFramework()
        self.challenge_history = {}  # session_id -> list of challenges
        self.performance_history = {}  # session_id -> performance metrics
        self.confidence_progression = {}  # session_id -> confidence evolution

        # Challenge configuration
        self.min_accuracy_for_advancement = 0.7
        self.confidence_boost_threshold = 0.8
        self.adaptive_difficulty_window = 5  # Last 5 challenges for adaptation

        # Initialize challenge templates
        self.challenge_templates = self._initialize_challenge_templates()

    # Backwards-compatible wrapper expected by some tests
    def generate_challenge(
        self, user_stage: Any, challenge_type: Any, ticker: str, user_session_id: str
    ):
        """Compatibility wrapper: older tests call generate_challenge with different param names."""
        # Map inputs to current API
        try:
            stage = user_stage if not hasattr(user_stage, "value") else user_stage
        except Exception:
            stage = user_stage

        return self.generate_stage_appropriate_challenge(user_session_id, stage, ticker)

    # (detailed Flask-interface implementation of
    # track_analytical_confidence_progress exists later in this file)

    def _initialize_challenge_templates(self) -> Dict[str, Dict]:
        """Initialize challenge templates for different stages and types"""

        return {
            "stage_1_ratio_interpretation": {
                "title": "Understanding Company Health Without Numbers",
                "description": "Interpret what financial ratios mean in plain language",
                "prediction_prompts": [
                    {
                        "category": "financial_health",
                        "prompt": "Based on the company description, how healthy do you think their finances are?",
                    },
                    {
                        "category": "risk_factors",
                        "prompt": "What potential risks do you see in this business?",
                    },
                ],
            },
            "stage_2_pattern_recognition": {
                "title": "Spotting Financial Patterns",
                "description": "Identify patterns and trends from qualitative information",
                "prediction_prompts": [
                    {
                        "category": "growth_potential",
                        "prompt": "What do you think about this company's growth prospects?",
                    },
                    {
                        "category": "financial_health",
                        "prompt": "How would you assess the company's financial stability?",
                    },
                ],
            },
            "stage_3_blind_analysis": {
                "title": "Independent Analysis Challenge",
                "description": "Make comprehensive predictions before seeing quantitative data",
                "prediction_prompts": [
                    {
                        "category": "financial_health",
                        "prompt": "Predict the company's debt-to-equity ratio range",
                    },
                    {
                        "category": "growth_potential",
                        "prompt": "Estimate revenue growth trend over the past 3 years",
                    },
                    {
                        "category": "investment_decision",
                        "prompt": "Would you invest in this company? Why?",
                    },
                ],
            },
            "stage_4_complex_scenarios": {
                "title": "Master Analyst Challenge",
                "description": "Navigate complex investment scenarios without tool assistance",
                "prediction_prompts": [
                    {
                        "category": "financial_health",
                        "prompt": "Comprehensive financial health assessment",
                    },
                    {
                        "category": "risk_factors",
                        "prompt": "Identify and rank the top 3 investment risks",
                    },
                    {
                        "category": "investment_decision",
                        "prompt": "Provide a detailed investment recommendation",
                    },
                ],
            },
        }

    def generate_stage_appropriate_challenge(
        self,
        session_id: str,
        current_stage: LearningStage,
        company_data: Union[str, Dict[str, Any]],
        challenge_type: Optional[ChallengeType] = None,
    ) -> ToolIndependenceChallenge:
        """
        Generate a challenge appropriate for the user's current learning stage

        Args:
            session_id: User session identifier
            current_stage: User's current learning stage
            company_data: Company ticker symbol (str) or financial data (dict)
            challenge_type: Specific challenge type (optional)

        Returns:
            ToolIndependenceChallenge: Generated challenge
        """

        # Handle both string ticker and dict company data
        if isinstance(company_data, str):
            ticker = company_data
            company_symbol = ticker
            # Create basic company data structure
            company_info = {
                "symbol": ticker,
                "name": f"Company {ticker}",
                "ticker": ticker,
            }
        else:
            company_info = company_data
            company_symbol = company_info.get("symbol", "UNKNOWN")

        # Determine challenge type based on stage if not specified
        if challenge_type is None:
            challenge_type = self._select_challenge_type_for_stage(
                current_stage, session_id
            )

        # Get difficulty level based on stage
        difficulty_level = self._get_difficulty_level(current_stage, session_id)

        # Generate challenge
        challenge = self._create_challenge(
            challenge_type=challenge_type,
            difficulty_level=difficulty_level,
            company_symbol=company_symbol,
            company_data=company_info,
            session_id=session_id,
        )

        # Store challenge in history
        if session_id not in self.challenge_history:
            self.challenge_history[session_id] = []
        self.challenge_history[session_id].append(challenge)

        return challenge

    def _select_challenge_type_for_stage(
        self, stage: LearningStage, session_id: str
    ) -> ChallengeType:
        """Select appropriate challenge type based on learning stage"""

        # Get recent performance for personalization
        recent_performance = self._get_recent_performance(session_id, window=3)

        stage_challenge_weights = {
            LearningStage.GUIDED_DISCOVERY: {
                ChallengeType.RATIO_INTERPRETATION: 0.6,
                ChallengeType.CONFIDENCE_BUILDING: 0.4,
            },
            LearningStage.ASSISTED_ANALYSIS: {
                ChallengeType.RATIO_INTERPRETATION: 0.3,
                ChallengeType.PREDICTION_VALIDATION: 0.4,
                ChallengeType.CONFIDENCE_BUILDING: 0.3,
            },
            LearningStage.INDEPENDENT_THINKING: {
                ChallengeType.BLIND_ANALYSIS: 0.5,
                ChallengeType.PREDICTION_VALIDATION: 0.3,
                ChallengeType.SCENARIO_ANALYSIS: 0.2,
            },
            LearningStage.ANALYTICAL_MASTERY: {
                ChallengeType.BLIND_ANALYSIS: 0.3,
                ChallengeType.SCENARIO_ANALYSIS: 0.4,
                ChallengeType.CONFIDENCE_BUILDING: 0.3,
            },
        }

        weights = stage_challenge_weights.get(
            stage, stage_challenge_weights[LearningStage.GUIDED_DISCOVERY]
        )

        # Weighted random selection
        challenge_types = list(weights.keys())
        probabilities = list(weights.values())

        return random.choices(challenge_types, weights=probabilities)[0]

    def _get_difficulty_level(self, stage: LearningStage, session_id: str) -> int:
        """Get difficulty level based on stage and performance"""

        base_difficulty = {
            LearningStage.GUIDED_DISCOVERY: 1,
            LearningStage.ASSISTED_ANALYSIS: 2,
            LearningStage.INDEPENDENT_THINKING: 3,
            LearningStage.ANALYTICAL_MASTERY: 4,
        }

        difficulty = base_difficulty.get(stage, 1)

        # Adapt based on recent performance
        recent_accuracy = self._calculate_recent_accuracy(session_id)

        if recent_accuracy > 0.8 and difficulty < 4:
            difficulty += 1  # Increase difficulty for high performers
        elif recent_accuracy < 0.5 and difficulty > 1:
            difficulty -= 1  # Decrease difficulty for struggling users

        return difficulty

    def _create_challenge(
        self,
        challenge_type: ChallengeType,
        difficulty_level: int,
        company_symbol: str,
        company_data: Dict[str, Any],
        session_id: str,
    ) -> ToolIndependenceChallenge:
        """Create a specific challenge based on parameters"""

        challenge_id = (
            f"{challenge_type.value}_{company_symbol}_{str(uuid.uuid4())[:8]}"
        )

        # Get template based on difficulty level
        template_key = (
            f"stage_{difficulty_level}_{self._get_template_suffix(challenge_type)}"
        )
        template = self.challenge_templates.get(
            template_key, self.challenge_templates["stage_1_ratio_interpretation"]
        )

        # Prepare company basic info (visible to user)
        company_basic_info = self._extract_basic_info(company_data)

        # Prepare hidden metrics (to be revealed)
        hidden_metrics = self._extract_quantitative_metrics(company_data)

        # Create prediction prompts
        prediction_prompts = self._customize_prediction_prompts(
            template["prediction_prompts"], company_basic_info, difficulty_level
        )

        # Define reveal sequence
        reveal_sequence = self._create_reveal_sequence(challenge_type, hidden_metrics)

        # Set success criteria
        success_criteria = self._define_success_criteria(
            challenge_type, difficulty_level
        )

        # Prepare educational context
        educational_context = self._prepare_educational_context(
            challenge_type, company_basic_info, hidden_metrics
        )

        return ToolIndependenceChallenge(
            challenge_id=challenge_id,
            challenge_type=challenge_type,
            difficulty_level=difficulty_level,
            title=template["title"],
            description=template["description"],
            company_symbol=company_symbol,
            company_basic_info=company_basic_info,
            hidden_metrics=hidden_metrics,
            prediction_prompts=prediction_prompts,
            reveal_sequence=reveal_sequence,
            success_criteria=success_criteria,
            educational_context=educational_context,
        )

    def _get_template_suffix(self, challenge_type: ChallengeType) -> str:
        """Get template suffix for challenge type"""

        suffix_map = {
            ChallengeType.RATIO_INTERPRETATION: "ratio_interpretation",
            ChallengeType.BLIND_ANALYSIS: "blind_analysis",
            ChallengeType.PREDICTION_VALIDATION: "pattern_recognition",
            ChallengeType.CONFIDENCE_BUILDING: "ratio_interpretation",
            ChallengeType.SCENARIO_ANALYSIS: "complex_scenarios",
        }

        return suffix_map.get(challenge_type, "ratio_interpretation")

    def _extract_basic_info(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive qualitative information visible to users for meaningful analysis"""

        # Get quantitative data to derive qualitative insights
        debt_to_equity = company_data.get("debt_to_equity", 0)
        current_ratio = company_data.get("current_ratio", 0)
        roe = company_data.get("roe", 0)
        revenue_growth = company_data.get("revenue_growth", 0)
        net_margin = company_data.get("net_margin", 0)

        return {
            "symbol": company_data.get("symbol", ""),
            "company_name": company_data.get("company_name", ""),
            "industry": company_data.get("industry", "Technology"),
            "sector": company_data.get("sector", "Information Technology"),
            "business_description": company_data.get(
                "business_description",
                "A technology company focused on software solutions and digital services.",
            ),
            "business_description_full": company_data.get(
                "business_description_full",
                company_data.get(
                    "business_description",
                    "A technology company focused on software solutions and digital services.",
                ),
            ),
            "market_cap_range": self._categorize_market_cap(
                company_data.get("market_cap", 25000)
            ),
            "listing_status": company_data.get("listing_status", "Listed"),
            "exchange": company_data.get("exchange", "NSE"),
            # Rich qualitative insights derived from metrics (without revealing exact numbers)
            "financial_health_indicators": self._derive_financial_health_narrative(
                debt_to_equity, current_ratio, roe, net_margin
            ),
            "growth_story": self._derive_growth_narrative(revenue_growth, company_data),
            "business_model_strength": self._derive_business_model_insights(
                company_data
            ),
            "competitive_position": self._derive_competitive_insights(company_data),
            "management_quality_signals": self._derive_management_insights(
                company_data
            ),
            "industry_dynamics": self._derive_industry_context(company_data),
            "recent_developments": self._derive_recent_news_context(company_data),
            "risk_signals": self._derive_risk_indicators(company_data),
        }

    def _extract_quantitative_metrics(
        self, company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract quantitative metrics to be hidden initially"""

        return {
            "financial_ratios": {
                "debt_to_equity": company_data.get("debt_to_equity", 0),
                "current_ratio": company_data.get("current_ratio", 0),
                "roe": company_data.get("roe", 0),
                "pe_ratio": company_data.get("pe_ratio", 0),
                "price_to_book": company_data.get("price_to_book", 0),
            },
            "growth_metrics": {
                "revenue_growth": company_data.get("revenue_growth", 0),
                "earnings_growth": company_data.get("earnings_growth", 0),
                "book_value_growth": company_data.get("book_value_growth", 0),
            },
            "profitability": {
                "gross_margin": company_data.get("gross_margin", 0),
                "operating_margin": company_data.get("operating_margin", 0),
                "net_margin": company_data.get("net_margin", 0),
            },
            "risk_indicators": {
                "beta": company_data.get("beta", 1.0),
                "volatility": company_data.get("volatility", 0),
                "debt_coverage": company_data.get("debt_coverage", 0),
            },
        }

    def _categorize_market_cap(self, market_cap: float) -> str:
        """Categorize market cap without revealing exact numbers"""

        if market_cap >= 75000:  # 75000+ crores
            return "Large Cap"
        elif market_cap >= 25000:  # 25000-75000 crores
            return "Mid Cap"
        elif market_cap >= 5000:  # 5000-25000 crores
            return "Small Cap"
        else:
            return "Micro Cap"

    def _derive_financial_health_narrative(
        self, debt_to_equity: float, current_ratio: float, roe: float, net_margin: float
    ) -> List[str]:
        """Create financial health narrative without revealing exact numbers"""

        indicators = []

        # Debt management insights with context
        if debt_to_equity < 0.3:
            indicators.append(
                "💪 Company maintains conservative debt levels with strong balance sheet (debt-to-equity likely under 30%)"
            )
        elif debt_to_equity < 0.7:
            indicators.append(
                "⚖️ Company has moderate debt levels - manageable financial structure (debt-to-equity in healthy 30-70% range)"
            )
        elif debt_to_equity < 1.2:
            indicators.append(
                "⚠️ Company carries higher debt burden - requires monitoring (debt-to-equity above 70%, concerning level)"
            )
        else:
            indicators.append(
                "🚨 Company has significant debt obligations - potential financial stress (debt-to-equity very high, above 120%)"
            )

        # Liquidity insights with context
        if current_ratio > 2.0:
            indicators.append(
                "💰 Strong cash position and short-term liquidity (current ratio above 2.0, excellent coverage)"
            )
        elif current_ratio > 1.5:
            indicators.append(
                "✅ Adequate liquidity to meet short-term obligations (current ratio 1.5-2.0, healthy range)"
            )
        elif current_ratio > 1.0:
            indicators.append(
                "⚡ Tight but manageable liquidity position (current ratio 1.0-1.5, requires attention)"
            )
        else:
            indicators.append(
                "🔴 Potential liquidity concerns - may struggle with short-term payments (current ratio below 1.0, cash stress)"
            )

        # Profitability insights with context
        if roe > 0.18:
            indicators.append(
                "🌟 Exceptional returns to shareholders - highly efficient operations (ROE above 18%, top-tier performance)"
            )
        elif roe > 0.12:
            indicators.append(
                "📈 Good returns to shareholders - solid operational efficiency (ROE 12-18%, above-average)"
            )
        elif roe > 0.08:
            indicators.append(
                "📊 Moderate returns to shareholders - average efficiency (ROE 8-12%, meets expectations)"
            )
        else:
            indicators.append(
                "📉 Low returns to shareholders - operational efficiency concerns (ROE below 8%, underperforming)"
            )

        # Margin insights with context
        if net_margin > 0.15:
            indicators.append(
                "💎 Strong profit margins indicate pricing power and cost control (net margin above 15%, premium)"
            )
        elif net_margin > 0.08:
            indicators.append(
                "✨ Healthy profit margins showing good operational control (net margin 8-15%, solid)"
            )
        elif net_margin > 0.03:
            indicators.append(
                "⭐ Thin profit margins - competitive pressure visible (net margin 3-8%, basic profitability)"
            )
        else:
            indicators.append(
                "❌ Struggling with profitability - cost or pricing challenges (net margin below 3%, concerning)"
            )

        return indicators

    def _derive_growth_narrative(
        self, revenue_growth: float, company_data: Dict[str, Any]
    ) -> List[str]:
        """Create growth story narrative without exact numbers"""

        growth_story = []

        # Revenue growth insights
        if revenue_growth > 0.25:
            growth_story.append(
                "🚀 Experiencing rapid expansion with strong market demand (exceptional growth trajectory)"
            )
            growth_story.append(
                "📊 Successful scaling of business operations (revenue momentum is strong)"
            )
        elif revenue_growth > 0.15:
            growth_story.append(
                "📈 Solid growth trajectory indicating market acceptance (above-average expansion)"
            )
            growth_story.append(
                "🎯 Expanding market share in competitive landscape (gaining ground on competitors)"
            )
        elif revenue_growth > 0.05:
            growth_story.append(
                "⚖️ Modest growth in line with industry averages (steady but unspectacular progress)"
            )
            growth_story.append(
                "🔄 Maintaining steady business expansion (consistent but limited growth)"
            )
        elif revenue_growth > -0.05:
            growth_story.append(
                "😐 Flat revenue suggesting market saturation or challenges (stagnant performance)"
            )
            growth_story.append(
                "🔧 Company working to reignite growth momentum (seeking turnaround strategies)"
            )
        else:
            growth_story.append(
                "📉 Declining revenues indicate significant business challenges (negative growth trend)"
            )
            growth_story.append(
                "🆘 Turnaround efforts may be required (fundamental business issues)"
            )

        # Add contextual growth factors
        industry = company_data.get("industry", "")
        if "technology" in industry.lower():
            if revenue_growth > 0.15:
                growth_story.append(
                    "💻 Strong tech sector performance with innovation-driven growth"
                )
            else:
                growth_story.append(
                    "⚡ Technology sector facing headwinds or increased competition"
                )

        return growth_story

    def _derive_business_model_insights(
        self, company_data: Dict[str, Any]
    ) -> List[str]:
        """Derive business model strength indicators"""

        insights = []
        industry = company_data.get("industry", "").lower()
        sector = company_data.get("sector", "").lower()

        # Industry-specific business model insights with context
        if "technology" in industry or "software" in industry:
            insights.append(
                "💻 Software/tech business model with recurring revenue potential (subscription-based models typical in 70-80% of tech companies)"
            )
            insights.append(
                "📈 Scalable operations with lower marginal costs as business grows (tech companies can achieve 80%+ gross margins)"
            )
            insights.append(
                "🔬 Innovation and R&D capabilities critical for competitive advantage (tech companies typically invest 15-20% of revenue in R&D)"
            )

        elif "pharmaceutical" in industry or "healthcare" in industry:
            insights.append(
                "🏥 Healthcare/pharma model with regulatory moats and patent protection (patent protection typically 10-20 years)"
            )
            insights.append(
                "⏰ High R&D investments with long development cycles (drug development takes 10-15 years, costs $1-3B)"
            )
            insights.append(
                "💊 Potential for blockbuster products driving significant returns (successful drugs can generate $1B+ annual revenue)"
            )

        elif "fmcg" in industry or "consumer" in industry:
            insights.append(
                "🛒 Consumer goods model with brand loyalty and distribution advantages (strong brands command 20-40% price premiums)"
            )
            insights.append(
                "🔄 Stable demand patterns with defensive characteristics (consumer staples show 5-10% revenue volatility vs 20-30% for cyclicals)"
            )
            insights.append(
                "📦 Marketing and supply chain efficiency drive profitability (FMCG companies typically spend 10-15% of revenue on marketing)"
            )

        elif "financial" in sector:
            insights.append(
                "🏦 Financial services model dependent on interest rates and credit quality (1% rate change impacts margins by 10-20%)"
            )
            insights.append(
                "📋 Regulatory compliance and capital requirements shape operations (banks maintain 8-12% capital adequacy ratios)"
            )
            insights.append(
                "📊 Economic cycles significantly impact business performance (loan loss provisions can vary 0.5-3% of assets)"
            )

        elif "energy" in industry or "renewable" in industry:
            insights.append(
                "⚡ Energy business model with commodity price exposure (oil/gas prices drive 60-80% of revenue volatility)"
            )
            insights.append(
                "🌱 Renewable energy transition creating new opportunities (renewable capacity growing 10-15% annually)"
            )
            insights.append(
                "🔋 Capital-intensive operations requiring long-term investments (energy projects require 5-20 year payback periods)"
            )

        else:
            insights.append(
                "🏭 Traditional business model with asset-heavy operations (asset turnover typically 0.5-1.5x for manufacturing)"
            )
            insights.append(
                "⚙️ Capital efficiency and operational leverage key performance drivers (fixed costs create 20-40% operating leverage)"
            )

        return insights

    def _derive_competitive_insights(self, company_data: Dict[str, Any]) -> List[str]:
        """Derive competitive position insights"""

        insights = []
        market_cap = company_data.get("market_cap", 0)
        industry = company_data.get("industry", "").lower()

        # Size-based competitive position with context
        if market_cap > 75000:  # Large cap
            insights.append(
                "🏆 Market leader with strong competitive moats and pricing power (large-caps typically command 20-40% market share)"
            )
            insights.append(
                "🌟 Established brand recognition and customer relationships (top 3 players in most industries)"
            )
            insights.append(
                "💰 Resources to invest in innovation and market expansion (large-caps spend 2-5x more on R&D than smaller competitors)"
            )
        elif market_cap > 25000:  # Mid cap
            insights.append(
                "🎯 Established player with regional or niche market strength (mid-caps often dominate specific segments)"
            )
            insights.append(
                "📈 Growing competitive position with expansion opportunities (mid-caps show 15-25% higher growth rates than large-caps)"
            )
            insights.append(
                "⚖️ Balancing growth investments with profitability requirements (mid-caps face pressure to scale efficiently)"
            )
        else:  # Small/micro cap
            insights.append(
                "🚀 Emerging player with agility but limited resources (small-caps can pivot 3-5x faster than large competitors)"
            )
            insights.append(
                "💎 Potential for rapid growth but higher execution risks (small-caps show 200-500% higher volatility)"
            )
            insights.append(
                "⚠️ May face challenges competing with larger established players (resource constraints limit market penetration)"
            )

        # Industry-specific competitive factors with context
        if "technology" in industry:
            insights.append(
                "💻 Technology sector requires continuous innovation to maintain relevance (tech companies reinvent 30-50% of products every 2-3 years)"
            )
            insights.append(
                "🔗 Network effects and ecosystem development provide competitive advantages (winner-takes-most markets common in tech)"
            )
        elif "energy" in industry:
            insights.append(
                "⚡ Energy sector faces regulatory and environmental pressures (ESG requirements reshaping competitive landscape)"
            )
            insights.append(
                "🌱 Renewable transition creating new competitive dynamics (traditional energy companies investing 20-40% in renewables)"
            )

        return insights

    def _derive_management_insights(self, company_data: Dict[str, Any]) -> List[str]:
        """Derive management quality signals"""

        insights = []

        # Management quality indicators with context (would normally come from data analysis)
        insights.append(
            "👥 Management has demonstrated strategic vision and execution capability (successful companies show 80%+ strategic goal achievement)"
        )
        insights.append(
            "📊 Track record of delivering on guidance and shareholder commitments (top-quartile companies meet guidance 85-95% of the time)"
        )
        insights.append(
            "🔍 Transparent communication with stakeholders and markets (quarterly earnings calls, annual reports provide comprehensive updates)"
        )
        insights.append(
            "💼 Prudent capital allocation decisions balancing growth and returns (optimal companies maintain 15-25% ROE with sustainable growth)"
        )

        # Add industry-specific management considerations with context
        industry = company_data.get("industry", "").lower()
        if "technology" in industry:
            insights.append(
                "🔬 Technology leadership requires visionary management and innovation culture (tech CEOs typically have 10-20 years industry experience)"
            )
        elif "financial" in industry:
            insights.append(
                "🏦 Financial services management must balance risk and growth (banking CEOs focus on 8-12% capital ratios while maximizing returns)"
            )
        elif "energy" in industry:
            insights.append(
                "⚡ Energy sector management navigating transition and regulatory changes (energy leaders must balance traditional operations with renewable investments)"
            )
        else:
            insights.append(
                "🎯 Industry expertise and operational excellence drive competitive advantage (successful managers typically have 15+ years sector experience)"
            )

        return insights

    def _derive_industry_context(self, company_data: Dict[str, Any]) -> List[str]:
        """Derive industry dynamics and context"""

        context = []
        industry = company_data.get("industry", "").lower()

        if "technology" in industry:
            context.append(
                "💻 Technology sector experiencing rapid transformation and disruption (AI/Cloud driving 25-40% market growth annually)"
            )
            context.append(
                "📱 Digital adoption trends creating new market opportunities (global digitalization market expected to reach $6.8T by 2025)"
            )
            context.append(
                "⚖️ Regulatory scrutiny increasing for large tech platforms (data privacy laws affecting 60%+ of global tech revenue)"
            )

        elif "financial" in industry:
            context.append(
                "🏦 Financial sector adapting to digital transformation and fintech competition (traditional banks losing 15-25% market share to fintechs)"
            )
            context.append(
                "📈 Interest rate environment significantly impacts sector profitability (1% rate change affects bank margins by 10-15%)"
            )
            context.append(
                "📋 Regulatory changes affecting operational requirements and costs (compliance costs represent 4-8% of revenue for major banks)"
            )

        elif "healthcare" in industry:
            context.append(
                "🏥 Healthcare sector benefiting from aging demographics and innovation (global healthcare market growing 7-9% annually)"
            )
            context.append(
                "✅ Regulatory approval processes create barriers but also protection (FDA approval provides 5-20 year market exclusivity)"
            )
            context.append(
                "💰 Cost containment pressures affecting pricing and reimbursement (healthcare inflation 2-3x general inflation rates)"
            )

        elif "energy" in industry:
            context.append(
                "⚡ Energy sector undergoing massive transition to renewables (renewable capacity growing 10-15% annually)"
            )
            context.append(
                "🌍 ESG pressures reshaping investment and operational strategies (ESG mandates affecting $30T+ in global assets)"
            )
            context.append(
                "📊 Commodity price volatility creates significant earnings variability (oil price changes drive 60-80% of energy company earnings)"
            )

        else:
            context.append(
                "🏭 Industry facing standard competitive and regulatory pressures (average industry concentration increasing 10-15% over past decade)"
            )
            context.append(
                "📈 Economic cycles and consumer spending patterns affect demand (consumer discretionary spending varies 20-40% with economic cycles)"
            )

        return context

    def _derive_recent_news_context(self, company_data: Dict[str, Any]) -> List[str]:
        """Generate realistic recent developments context"""

        developments = []

        # Simulate realistic recent developments based on company characteristics
        market_cap = company_data.get("market_cap", 25000)
        industry = company_data.get("industry", "").lower()

        if market_cap > 50000:  # Large companies
            developments.append(
                "📊 Recent quarterly results met analyst expectations (large-caps beat estimates 55-60% of the time)"
            )
            developments.append(
                "🎯 Management provided forward guidance in line with market consensus (guidance accuracy typically 85-90% for large-caps)"
            )
            developments.append(
                "🚀 Announced strategic initiatives to expand market presence (large companies invest 3-5% of revenue in strategic initiatives)"
            )
        else:  # Smaller companies
            developments.append(
                "📈 Company reported progress on key strategic initiatives (small-caps show 20-30% higher strategic pivot rates)"
            )
            developments.append(
                "🤝 Recent partnerships announced to enhance growth prospects (partnerships critical for 70%+ of small-cap growth strategies)"
            )
            developments.append(
                "⚙️ Management highlighted operational improvements and cost optimization (small-caps focus on 10-20% cost reduction targets)"
            )

        if "technology" in industry:
            developments.append(
                "🔬 Product innovation pipeline showing promising developments (tech companies launch 2-4 major products annually)"
            )
            developments.append(
                "📱 Digital transformation initiatives gaining customer traction (enterprise digital adoption accelerating 25-40% annually)"
            )
        elif "energy" in industry:
            developments.append(
                "🌱 Renewable energy investments and capacity expansion announced (energy companies allocating 20-40% capex to renewables)"
            )
            developments.append(
                "⚡ Operational efficiency improvements reducing production costs (typical targets: 5-15% cost reduction)"
            )

        return developments

    def _derive_risk_indicators(self, company_data: Dict[str, Any]) -> List[str]:
        """Derive risk factor indicators without exact metrics"""

        risks = []
        industry = company_data.get("industry", "").lower()
        market_cap = company_data.get("market_cap", 25000)

        # Size-based risks with context
        if market_cap < 10000:  # Smaller companies
            risks.append(
                "⚠️ Smaller company size may limit access to capital markets (small-caps face 20-40% higher borrowing costs)"
            )
            risks.append(
                "📊 Higher volatility and liquidity risks compared to large-cap peers (small-caps show 200-300% higher price volatility)"
            )
            risks.append(
                "📉 Greater sensitivity to economic downturns and market cycles (small-caps decline 40-60% more in recessions)"
            )

        # Industry-specific risks with context
        if "technology" in industry:
            risks.append(
                "💻 Technology disruption and obsolescence risks (tech products have 2-5 year typical lifecycles)"
            )
            risks.append(
                "🔥 Intense competition and rapid product innovation cycles (tech companies face 30-50% annual competitive threats)"
            )
            risks.append(
                "⚖️ Regulatory and data privacy compliance requirements (compliance costs represent 2-5% of tech company revenue)"
            )

        elif "financial" in industry:
            risks.append(
                "💳 Credit risk and loan portfolio quality concerns (loan losses typically vary 0.5-3% of assets across cycles)"
            )
            risks.append(
                "📈 Interest rate sensitivity and regulatory capital requirements (1% rate change affects earnings by 10-20%)"
            )
            risks.append(
                "📊 Economic cycle dependency and market volatility impact (financial sector earnings 40-60% more volatile than market)"
            )

        elif "energy" in industry:
            risks.append(
                "⚡ Commodity price volatility creating earnings uncertainty (oil price changes drive 60-80% of earnings variance)"
            )
            risks.append(
                "🌍 Environmental regulations and transition risks (carbon taxes could impact 20-40% of traditional energy costs)"
            )
            risks.append(
                "🔋 Capital intensity requiring continuous large investments (energy companies typically invest 15-25% of revenue in capex)"
            )

        # General business risks with context
        risks.append(
            "🏆 Competitive pressures and market share erosion potential (companies lose 5-15% market share annually in competitive industries)"
        )
        risks.append(
            "👥 Key personnel retention and succession planning challenges (CEO turnover costs typically 200-400% of annual salary)"
        )
        risks.append(
            "📋 Regulatory changes affecting operational requirements (regulatory compliance costs growing 5-10% annually across industries)"
        )

        return risks

    def _customize_prediction_prompts(
        self,
        template_prompts: List[Dict[str, str]],
        company_info: Dict[str, Any],
        difficulty_level: int,
    ) -> List[Dict[str, str]]:
        """Customize prediction prompts based on company and difficulty"""

        customized_prompts = []

        for prompt in template_prompts:
            customized_prompt = prompt.copy()

            # Add company-specific context
            if "company_name" in company_info:
                customized_prompt["prompt"] = customized_prompt["prompt"].replace(
                    "this company", f"{company_info['company_name']}"
                )

            # Adjust complexity based on difficulty level
            if difficulty_level >= 3:
                customized_prompt[
                    "prompt"
                ] += " Provide specific reasoning for your assessment."

            customized_prompts.append(customized_prompt)

        return customized_prompts

    def _create_reveal_sequence(
        self, challenge_type: ChallengeType, hidden_metrics: Dict[str, Any]
    ) -> List[str]:
        """Create sequence for revealing hidden information"""

        base_sequence = [
            "financial_ratios",
            "profitability",
            "growth_metrics",
            "risk_indicators",
        ]

        # Customize based on challenge type
        if challenge_type == ChallengeType.BLIND_ANALYSIS:
            return base_sequence
        elif challenge_type == ChallengeType.RATIO_INTERPRETATION:
            return ["financial_ratios", "profitability"]
        elif challenge_type == ChallengeType.PREDICTION_VALIDATION:
            return ["growth_metrics", "financial_ratios"]
        else:
            return base_sequence

    def _define_success_criteria(
        self, challenge_type: ChallengeType, difficulty_level: int
    ) -> Dict[str, float]:
        """Define success criteria for the challenge"""

        base_criteria = {
            "minimum_accuracy": 0.6,
            "reasoning_quality": 0.5,
            "confidence_consistency": 0.7,
        }

        # Adjust based on difficulty
        difficulty_multipliers = [0.7, 0.8, 0.9, 1.0]
        multiplier = difficulty_multipliers[min(difficulty_level - 1, 3)]

        return {k: v * multiplier for k, v in base_criteria.items()}

    def _prepare_educational_context(
        self,
        challenge_type: ChallengeType,
        company_info: Dict[str, Any],
        hidden_metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Prepare educational context for the challenge"""

        return {
            "learning_objectives": self._get_learning_objectives(challenge_type),
            "key_concepts": self._get_key_concepts(challenge_type),
            "industry_context": company_info.get("industry", ""),
            "difficulty_hints": self._get_difficulty_hints(challenge_type),
            "success_indicators": self._get_success_indicators(hidden_metrics),
        }

    def _get_learning_objectives(self, challenge_type: ChallengeType) -> List[str]:
        """Get learning objectives for challenge type"""

        objectives_map = {
            ChallengeType.RATIO_INTERPRETATION: [
                "Understand financial ratios in business context",
                "Develop intuitive grasp of financial health indicators",
            ],
            ChallengeType.BLIND_ANALYSIS: [
                "Build analytical confidence without numerical tools",
                "Develop independent reasoning skills",
            ],
            ChallengeType.PREDICTION_VALIDATION: [
                "Learn to validate analytical predictions",
                "Understand prediction accuracy patterns",
            ],
            ChallengeType.CONFIDENCE_BUILDING: [
                "Build trust in analytical instincts",
                "Develop decision-making confidence",
            ],
            ChallengeType.SCENARIO_ANALYSIS: [
                "Apply analytical thinking to complex scenarios",
                "Integrate multiple analysis factors",
            ],
        }

        return objectives_map.get(
            challenge_type, ["Develop analytical thinking skills"]
        )

    def _get_key_concepts(self, challenge_type: ChallengeType) -> List[str]:
        """Get key concepts for challenge type"""

        concepts_map = {
            ChallengeType.RATIO_INTERPRETATION: [
                "Financial Health",
                "Debt Analysis",
                "Profitability",
            ],
            ChallengeType.BLIND_ANALYSIS: [
                "Independent Analysis",
                "Prediction Accuracy",
                "Reasoning Quality",
            ],
            ChallengeType.PREDICTION_VALIDATION: [
                "Growth Patterns",
                "Trend Analysis",
                "Market Context",
            ],
            ChallengeType.CONFIDENCE_BUILDING: [
                "Analytical Confidence",
                "Decision Making",
                "Risk Assessment",
            ],
            ChallengeType.SCENARIO_ANALYSIS: [
                "Complex Analysis",
                "Multi-factor Integration",
                "Strategic Thinking",
            ],
        }

        return concepts_map.get(challenge_type, ["Analytical Thinking"])

    def _get_difficulty_hints(self, challenge_type: ChallengeType) -> List[str]:
        """Get difficulty-specific hints"""

        hints_map = {
            ChallengeType.RATIO_INTERPRETATION: [
                "Think about what each ratio tells you about business health",
                "Consider industry context when interpreting ratios",
            ],
            ChallengeType.BLIND_ANALYSIS: [
                "Use qualitative information to form predictions",
                "Trust your analytical reasoning process",
            ],
            ChallengeType.PREDICTION_VALIDATION: [
                "Compare your predictions with actual metrics",
                "Analyze gaps in your reasoning",
            ],
            ChallengeType.CONFIDENCE_BUILDING: [
                "Focus on building analytical confidence",
                "Learn from prediction accuracy patterns",
            ],
            ChallengeType.SCENARIO_ANALYSIS: [
                "Consider multiple analysis perspectives",
                "Integrate various factors in your assessment",
            ],
        }

        return hints_map.get(challenge_type, ["Apply analytical thinking"])

    def _get_success_indicators(self, hidden_metrics: Dict[str, Any]) -> List[str]:
        """Generate success indicators based on actual metrics"""

        indicators = []

        # Financial health indicators
        ratios = hidden_metrics.get("financial_ratios", {})
        if ratios.get("debt_to_equity", 0) < 0.5:
            indicators.append("Low debt levels indicate financial stability")
        if ratios.get("current_ratio", 0) > 1.5:
            indicators.append("Strong liquidity position")

        # Growth indicators
        growth = hidden_metrics.get("growth_metrics", {})
        if growth.get("revenue_growth", 0) > 0.15:
            indicators.append("Strong revenue growth trend")

        # Profitability indicators
        profit = hidden_metrics.get("profitability", {})
        if profit.get("net_margin", 0) > 0.10:
            indicators.append("Healthy profit margins")

        return indicators

    def _get_recent_performance(
        self, session_id: str, window: int = 5
    ) -> Dict[str, float]:
        """Get recent performance metrics for a session"""

        if session_id not in self.performance_history:
            return {"accuracy": 0.5, "confidence": 0.5, "reasoning_quality": 0.5}

        recent_results = self.performance_history[session_id][-window:]

        if not recent_results:
            return {"accuracy": 0.5, "confidence": 0.5, "reasoning_quality": 0.5}

        avg_accuracy = sum(
            result.get("accuracy_score", 0.5) for result in recent_results
        ) / len(recent_results)
        avg_confidence = sum(
            result.get("confidence_progression", 0.5) for result in recent_results
        ) / len(recent_results)
        avg_reasoning = sum(
            result.get("reasoning_quality_score", 0.5) for result in recent_results
        ) / len(recent_results)

        return {
            "accuracy": avg_accuracy,
            "confidence": avg_confidence,
            "reasoning_quality": avg_reasoning,
        }

    def _calculate_recent_accuracy(self, session_id: str) -> float:
        """Calculate recent accuracy for difficulty adaptation"""

        recent_performance = self._get_recent_performance(session_id)
        return recent_performance.get("accuracy", 0.5)

    def create_blind_analysis_exercise(
        self,
        session_id: str,
        company_data: Dict[str, Any],
        user_learning_history: Dict[str, Any],
    ) -> ToolIndependenceChallenge:
        """
        Create a blind analysis exercise with progressive revelation

        Args:
            session_id: User session identifier
            company_data: Company data for analysis
            user_learning_history: User's learning progress data

        Returns:
            ToolIndependenceChallenge: Blind analysis challenge
        """

        # Determine user's current stage from learning history
        current_stage = user_learning_history.get(
            "current_stage", LearningStage.GUIDED_DISCOVERY
        )

        # Generate blind analysis challenge
        challenge = self.generate_stage_appropriate_challenge(
            session_id=session_id,
            current_stage=current_stage,
            company_data=company_data,
            challenge_type=ChallengeType.BLIND_ANALYSIS,
        )

        return challenge

    def evaluate_prediction_accuracy(
        self, session_id: str, prediction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate prediction accuracy from form data (Flask interface)

        Args:
            session_id: User session identifier
            prediction_data: Dictionary with prediction form data

        Returns:
            Dict with evaluation results
        """

        # Convert form data to UserPrediction objects
        user_predictions = []

        prediction_categories = [
            ("financial_health", PredictionCategory.FINANCIAL_HEALTH),
            ("growth_potential", PredictionCategory.GROWTH_POTENTIAL),
            ("risk_factors", PredictionCategory.RISK_FACTORS),
            ("investment_decision", PredictionCategory.INVESTMENT_DECISION),
        ]

        for form_field, category in prediction_categories:
            if form_field in prediction_data and prediction_data[form_field]:
                user_prediction = UserPrediction(
                    category=category,
                    prediction=prediction_data[form_field],
                    confidence_level=int(prediction_data.get("confidence_level", 3)),
                    reasoning=prediction_data.get("reasoning", ""),
                    timestamp=time.time(),
                )
                user_predictions.append(user_prediction)

        # Get actual metrics (simplified for now)
        ticker = prediction_data.get("ticker", "")
        actual_metrics = self._get_actual_metrics_for_ticker(ticker)

        # Evaluate each prediction
        accuracy_scores = []
        prediction_breakdown = {}

        for prediction in user_predictions:
            category_accuracy = self._evaluate_category_prediction(
                prediction, actual_metrics
            )
            accuracy_scores.append(category_accuracy)

            prediction_breakdown[prediction.category.value] = {
                "user_prediction": prediction.prediction,
                "accuracy": category_accuracy,
                "expected_range": self._get_expected_range_for_category(
                    prediction.category, actual_metrics
                ),
            }

        # Calculate overall accuracy
        overall_accuracy = (
            sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
        )

        # Generate learning insights
        learning_insights = self._generate_learning_insights(
            user_predictions, actual_metrics, overall_accuracy
        )

        # Track confidence progress
        confidence_progress = self._update_confidence_progress(
            session_id,
            overall_accuracy,
            int(prediction_data.get("confidence_level", 3)),
        )

        return {
            "overall_accuracy": overall_accuracy,
            "prediction_breakdown": prediction_breakdown,
            "learning_insights": learning_insights,
            "confidence_progress": confidence_progress,
        }

    def evaluate_prediction_accuracy_detailed(
        self,
        user_predictions: List[UserPrediction],
        actual_metrics: Dict[str, Any],
        reasoning_quality: Optional[float] = None,
    ) -> ChallengeResult:
        """
        Evaluate prediction accuracy against actual metrics

        Args:
            user_predictions: List of user predictions
            actual_metrics: Actual company metrics
            reasoning_quality: Optional manual reasoning quality score

        Returns:
            ChallengeResult: Evaluation results
        """

        accuracy_scores = []
        detailed_feedback = []

        for prediction in user_predictions:
            category_accuracy = self._evaluate_category_prediction(
                prediction, actual_metrics
            )
            accuracy_scores.append(category_accuracy)

            # Generate feedback for this prediction
            feedback = self._generate_prediction_feedback(
                prediction, actual_metrics, category_accuracy
            )
            detailed_feedback.extend(feedback)

        # Calculate overall accuracy
        overall_accuracy = (
            sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
        )

        # Calculate reasoning quality if not provided
        if reasoning_quality is None:
            reasoning_quality = self._assess_reasoning_quality(user_predictions)

        # Calculate confidence progression
        confidence_progression = self._calculate_confidence_progression(
            user_predictions, overall_accuracy
        )

        # Generate challenge result
        challenge_result = ChallengeResult(
            challenge_id=f"eval_{int(time.time() * 1000)}",
            challenge_type=ChallengeType.PREDICTION_VALIDATION,  # Default type
            user_predictions=user_predictions,
            actual_metrics=actual_metrics,
            accuracy_score=overall_accuracy,
            reasoning_quality_score=reasoning_quality,
            confidence_progression=confidence_progression,
            completion_time=time.time(),
            educational_feedback=detailed_feedback,
        )

        return challenge_result

    def _evaluate_category_prediction(
        self, prediction: UserPrediction, actual_metrics: Dict[str, Any]
    ) -> float:
        """Evaluate accuracy for a specific prediction category"""

        category = prediction.category
        prediction_text = prediction.prediction.lower()

        if category == PredictionCategory.FINANCIAL_HEALTH:
            return self._evaluate_financial_health_prediction(
                prediction_text, actual_metrics
            )
        elif category == PredictionCategory.GROWTH_POTENTIAL:
            return self._evaluate_growth_prediction(prediction_text, actual_metrics)
        elif category == PredictionCategory.RISK_FACTORS:
            return self._evaluate_risk_prediction(prediction_text, actual_metrics)
        elif category == PredictionCategory.INVESTMENT_DECISION:
            return self._evaluate_investment_decision(prediction_text, actual_metrics)
        else:
            return 0.5  # Neutral score for unknown categories

    def _evaluate_financial_health_prediction(
        self, prediction_text: str, actual_metrics: Dict[str, Any]
    ) -> float:
        """Evaluate financial health prediction accuracy"""

        ratios = actual_metrics.get("financial_ratios", {})
        profitability = actual_metrics.get("profitability", {})

        # Determine actual financial health
        debt_to_equity = ratios.get("debt_to_equity", 0)
        current_ratio = ratios.get("current_ratio", 0)
        roe = ratios.get("roe", 0)
        net_margin = profitability.get("net_margin", 0)

        # Calculate health score (0-1)
        health_indicators = [
            1.0 if debt_to_equity < 0.5 else (0.5 if debt_to_equity < 1.0 else 0.0),
            1.0 if current_ratio > 1.5 else (0.5 if current_ratio > 1.0 else 0.0),
            1.0 if roe > 0.15 else (0.5 if roe > 0.08 else 0.0),
            1.0 if net_margin > 0.10 else (0.5 if net_margin > 0.05 else 0.0),
        ]

        actual_health_score = sum(health_indicators) / len(health_indicators)

        # Map prediction to score
        prediction_score = 0.5  # Default neutral

        if any(
            word in prediction_text
            for word in ["excellent", "very good", "strong", "healthy"]
        ):
            prediction_score = 0.9
        elif any(word in prediction_text for word in ["good", "decent", "acceptable"]):
            prediction_score = 0.7
        elif any(word in prediction_text for word in ["average", "moderate", "okay"]):
            prediction_score = 0.5
        elif any(word in prediction_text for word in ["poor", "weak", "concerning"]):
            prediction_score = 0.3
        elif any(
            word in prediction_text for word in ["terrible", "very poor", "dangerous"]
        ):
            prediction_score = 0.1

        # Calculate accuracy based on how close prediction is to actual
        accuracy = 1.0 - abs(prediction_score - actual_health_score)
        return max(0.0, accuracy)

    def _evaluate_growth_prediction(
        self, prediction_text: str, actual_metrics: Dict[str, Any]
    ) -> float:
        """Evaluate growth prediction accuracy"""

        growth = actual_metrics.get("growth_metrics", {})
        revenue_growth = growth.get("revenue_growth", 0)
        earnings_growth = growth.get("earnings_growth", 0)

        # Determine actual growth level
        avg_growth = (revenue_growth + earnings_growth) / 2

        actual_growth_level = 0.5  # Default moderate
        if avg_growth > 0.20:
            actual_growth_level = 0.9  # High growth
        elif avg_growth > 0.10:
            actual_growth_level = 0.7  # Good growth
        elif avg_growth > 0.05:
            actual_growth_level = 0.5  # Moderate growth
        elif avg_growth > 0:
            actual_growth_level = 0.3  # Low growth
        else:
            actual_growth_level = 0.1  # Negative/no growth

        # Map prediction to growth level
        prediction_level = 0.5  # Default

        if any(
            word in prediction_text for word in ["excellent", "high", "strong", "rapid"]
        ):
            prediction_level = 0.9
        elif any(word in prediction_text for word in ["good", "solid", "positive"]):
            prediction_level = 0.7
        elif any(word in prediction_text for word in ["moderate", "average", "steady"]):
            prediction_level = 0.5
        elif any(word in prediction_text for word in ["slow", "low", "weak"]):
            prediction_level = 0.3
        elif any(word in prediction_text for word in ["negative", "declining", "poor"]):
            prediction_level = 0.1

        accuracy = 1.0 - abs(prediction_level - actual_growth_level)
        return max(0.0, accuracy)

    def _evaluate_risk_prediction(
        self, prediction_text: str, actual_metrics: Dict[str, Any]
    ) -> float:
        """Evaluate risk prediction accuracy"""

        # This is a simplified risk evaluation
        risk_indicators = actual_metrics.get("risk_indicators", {})
        ratios = actual_metrics.get("financial_ratios", {})

        debt_to_equity = ratios.get("debt_to_equity", 0)
        beta = risk_indicators.get("beta", 1.0)

        # Calculate risk score
        risk_score = 0.5
        if debt_to_equity > 1.0:
            risk_score += 0.2
        if beta > 1.5:
            risk_score += 0.2

        risk_score = min(1.0, risk_score)

        # Map prediction to risk level
        prediction_risk = 0.5

        if any(
            word in prediction_text
            for word in ["high risk", "risky", "dangerous", "concerning"]
        ):
            prediction_risk = 0.8
        elif any(
            word in prediction_text
            for word in ["moderate risk", "some risk", "caution"]
        ):
            prediction_risk = 0.6
        elif any(word in prediction_text for word in ["low risk", "safe", "stable"]):
            prediction_risk = 0.2

        accuracy = 1.0 - abs(prediction_risk - risk_score)
        return max(0.0, accuracy)

    def _evaluate_investment_decision(
        self, prediction_text: str, actual_metrics: Dict[str, Any]
    ) -> float:
        """Evaluate investment decision prediction"""

        # Calculate overall investment attractiveness
        ratios = actual_metrics.get("financial_ratios", {})
        growth = actual_metrics.get("growth_metrics", {})
        profitability = actual_metrics.get("profitability", {})

        # Simple scoring system
        scores = []

        # Financial health
        debt_to_equity = ratios.get("debt_to_equity", 0)
        scores.append(
            1.0 if debt_to_equity < 0.5 else 0.5 if debt_to_equity < 1.0 else 0.0
        )

        # Growth
        revenue_growth = growth.get("revenue_growth", 0)
        scores.append(
            1.0 if revenue_growth > 0.15 else 0.5 if revenue_growth > 0.05 else 0.0
        )

        # Profitability
        net_margin = profitability.get("net_margin", 0)
        scores.append(1.0 if net_margin > 0.10 else 0.5 if net_margin > 0.05 else 0.0)

        investment_attractiveness = sum(scores) / len(scores)

        # Map prediction to investment level
        prediction_investment = 0.5

        if any(
            word in prediction_text
            for word in ["buy", "invest", "purchase", "strong buy"]
        ):
            prediction_investment = 0.9
        elif any(word in prediction_text for word in ["hold", "keep", "maintain"]):
            prediction_investment = 0.5
        elif any(word in prediction_text for word in ["sell", "avoid", "don't invest"]):
            prediction_investment = 0.1

        accuracy = 1.0 - abs(prediction_investment - investment_attractiveness)
        return max(0.0, accuracy)

    def _assess_reasoning_quality(self, predictions: List[UserPrediction]) -> float:
        """Assess the quality of reasoning in predictions"""

        quality_scores = []

        for prediction in predictions:
            reasoning = prediction.reasoning.lower()

            # Basic quality indicators
            quality_score = 0.3  # Base score

            # Length and detail
            if len(reasoning) > 50:
                quality_score += 0.2
            if len(reasoning) > 100:
                quality_score += 0.1

            # Specific analytical terms
            analytical_terms = [
                "ratio",
                "growth",
                "debt",
                "profit",
                "margin",
                "revenue",
                "cash flow",
                "equity",
                "return",
                "risk",
                "industry",
                "market",
            ]

            term_count = sum(1 for term in analytical_terms if term in reasoning)
            quality_score += min(0.3, term_count * 0.05)

            # Comparative language
            comparative_terms = [
                "compared to",
                "relative to",
                "better than",
                "worse than",
                "similar to",
            ]
            if any(term in reasoning for term in comparative_terms):
                quality_score += 0.1

            quality_scores.append(min(1.0, quality_score))

        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.5

    def _calculate_confidence_progression(
        self, predictions: List[UserPrediction], accuracy: float
    ) -> float:
        """Calculate confidence progression based on predictions and accuracy"""

        if not predictions:
            return 0.0

        # Average confidence level from predictions
        avg_confidence = sum(p.confidence_level for p in predictions) / len(predictions)
        normalized_confidence = avg_confidence / 5.0  # Convert 1-5 to 0-1

        # Confidence progression considers both confidence and accuracy
        if accuracy > 0.7 and normalized_confidence > 0.6:
            return min(1.0, (accuracy + normalized_confidence) / 2)
        elif accuracy < 0.5 and normalized_confidence > 0.8:
            return -0.3  # Overconfidence penalty
        else:
            return (accuracy + normalized_confidence) / 2 - 0.5

    def _generate_prediction_feedback(
        self,
        prediction: UserPrediction,
        actual_metrics: Dict[str, Any],
        accuracy_score: float,
    ) -> List[str]:
        """Generate educational feedback for a prediction"""

        feedback = []
        category = prediction.category

        if accuracy_score > 0.8:
            feedback.append(
                f"Excellent prediction for {category.value}! Your reasoning was on track."
            )
        elif accuracy_score > 0.6:
            feedback.append(
                f"Good prediction for {category.value}. Your analysis showed solid understanding."
            )
        else:
            feedback.append(
                f"Your {category.value} prediction needs refinement. Let's explore why..."
            )

        # Add category-specific feedback
        if category == PredictionCategory.FINANCIAL_HEALTH:
            ratios = actual_metrics.get("financial_ratios", {})
            debt_to_equity = ratios.get("debt_to_equity", 0)

            if debt_to_equity < 0.5:
                feedback.append(
                    "The company has low debt levels, indicating strong financial health."
                )
            elif debt_to_equity > 1.0:
                feedback.append(
                    "High debt-to-equity ratio suggests potential financial stress."
                )

        elif category == PredictionCategory.GROWTH_POTENTIAL:
            growth = actual_metrics.get("growth_metrics", {})
            revenue_growth = growth.get("revenue_growth", 0) * 100

            if revenue_growth > 15:
                feedback.append(
                    f"Strong revenue growth of {revenue_growth:.1f}% indicates good growth potential."
                )
            elif revenue_growth < 5:
                feedback.append(
                    f"Revenue growth of {revenue_growth:.1f}% suggests limited growth prospects."
                )

        return feedback

    def adapt_challenge_difficulty(
        self,
        session_id: str,
        performance_history: List[Dict[str, Any]],
        current_stage: LearningStage,
    ) -> Dict[str, Any]:
        """
        Adapt challenge difficulty based on performance history

        Args:
            session_id: User session identifier
            performance_history: Recent performance data
            current_stage: Current learning stage

        Returns:
            Dict with adaptation recommendations
        """

        if not performance_history:
            return {"difficulty_adjustment": 0, "recommendations": []}

        # Analyze recent performance
        recent_accuracy = [
            p.get("accuracy_score", 0.5) for p in performance_history[-5:]
        ]
        recent_confidence = [
            p.get("confidence_progression", 0.0) for p in performance_history[-5:]
        ]

        avg_accuracy = sum(recent_accuracy) / len(recent_accuracy)
        avg_confidence = sum(recent_confidence) / len(recent_confidence)

        # Determine adjustments
        difficulty_adjustment = 0
        recommendations = []

        if avg_accuracy > 0.8 and avg_confidence > 0.6:
            difficulty_adjustment = +1
            recommendations.append(
                "Performance is excellent - increasing challenge difficulty"
            )
            recommendations.append("Ready for more complex analytical scenarios")

        elif avg_accuracy < 0.5:
            difficulty_adjustment = -1
            recommendations.append("Reducing difficulty to build confidence")
            recommendations.append("Focus on fundamental analytical concepts")

        elif avg_confidence < 0.3:
            recommendations.append(
                "Building analytical confidence through supportive challenges"
            )
            recommendations.append(
                "Emphasizing reasoning validation and positive feedback"
            )

        # Stage-specific recommendations
        if current_stage == LearningStage.GUIDED_DISCOVERY:
            recommendations.append("Continue with guided interpretation exercises")
        elif current_stage == LearningStage.ASSISTED_ANALYSIS:
            recommendations.append("Ready for pattern recognition challenges")
        elif current_stage == LearningStage.INDEPENDENT_THINKING:
            recommendations.append("Blind analysis exercises recommended")
        else:
            recommendations.append("Complex scenario analysis appropriate")

        # Store adaptation results
        adaptation_result = {
            "difficulty_adjustment": difficulty_adjustment,
            "recommendations": recommendations,
            "current_accuracy": avg_accuracy,
            "current_confidence": avg_confidence,
            "timestamp": time.time(),
        }

        # Update performance tracking
        if session_id not in self.performance_history:
            self.performance_history[session_id] = []

        self.performance_history[session_id].append(adaptation_result)

        return adaptation_result

    def _get_actual_metrics_for_ticker(self, ticker: str) -> Dict[str, Any]:
        """Get actual metrics for a ticker (simplified implementation)"""
        # This would normally fetch from a data source
        # For now, return simulated metrics
        return {
            "financial_ratios": {
                "debt_to_equity": 0.6,
                "current_ratio": 1.8,
                "roe": 0.12,
                "pe_ratio": 15.0,
            },
            "growth_metrics": {"revenue_growth": 0.08, "earnings_growth": 0.10},
            "profitability": {"net_margin": 0.08, "operating_margin": 0.12},
            "risk_indicators": {"beta": 1.1, "volatility": 0.25},
        }

    def _get_expected_range_for_category(
        self, category: PredictionCategory, actual_metrics: Dict[str, Any]
    ) -> str:
        """Get expected range description for a category"""

        if category == PredictionCategory.FINANCIAL_HEALTH:
            ratios = actual_metrics.get("financial_ratios", {})
            debt_ratio = ratios.get("debt_to_equity", 0)
            if debt_ratio < 0.5:
                return "Good to Excellent"
            elif debt_ratio < 1.0:
                return "Average to Good"
            else:
                return "Poor to Average"

        elif category == PredictionCategory.GROWTH_POTENTIAL:
            growth = actual_metrics.get("growth_metrics", {})
            avg_growth = (
                growth.get("revenue_growth", 0) + growth.get("earnings_growth", 0)
            ) / 2
            if avg_growth > 0.15:
                return "High Growth"
            elif avg_growth > 0.08:
                return "Moderate Growth"
            else:
                return "Low Growth"

        return "Variable"

    def _generate_learning_insights(
        self,
        user_predictions: List[UserPrediction],
        actual_metrics: Dict[str, Any],
        overall_accuracy: float,
    ) -> List[str]:
        """Generate learning insights based on prediction accuracy"""

        insights = []

        if overall_accuracy > 0.8:
            insights.append(
                "Excellent analytical intuition! Your predictions align well with the data."
            )
        elif overall_accuracy > 0.6:
            insights.append(
                "Good analytical thinking. Consider incorporating more quantitative factors."
            )
        else:
            insights.append(
                "Focus on understanding key financial ratios and their business implications."
            )

        # Category-specific insights
        for prediction in user_predictions:
            if prediction.category == PredictionCategory.FINANCIAL_HEALTH:
                ratios = actual_metrics.get("financial_ratios", {})
                if ratios.get("debt_to_equity", 0) > 1.0:
                    insights.append(
                        "High debt levels can indicate financial stress - watch debt-to-equity ratios."
                    )

        return insights

    def _update_confidence_progress(
        self, session_id: str, accuracy: float, confidence_level: int
    ) -> Dict[str, Any]:
        """Update confidence progress tracking"""

        if session_id not in self.confidence_progression:
            self.confidence_progression[session_id] = []

        # Calculate current confidence based on accuracy and stated confidence
        current_confidence = (accuracy + (confidence_level / 5.0)) / 2

        progress_entry = {
            "current_confidence": current_confidence,
            "challenges_completed": len(self.confidence_progression[session_id]) + 1,
            "accuracy": accuracy,
            "confidence_level": confidence_level,
            "timestamp": time.time(),
        }

        self.confidence_progression[session_id].append(progress_entry)

        return progress_entry

    def get_analytical_confidence_summary(self, session_id: str) -> Dict[str, Any]:
        """Get analytical confidence summary for a session"""

        if session_id not in self.confidence_progression:
            return {
                "current_confidence": 0.5,
                "challenges_completed": 0,
                "progress_trend": "no_data",
                "achievements": [],
            }

        progress_data = self.confidence_progression[session_id]
        recent_entries = progress_data[-5:]  # Last 5 entries

        current_confidence = (
            recent_entries[-1]["current_confidence"] if recent_entries else 0.5
        )
        avg_accuracy = sum(entry["accuracy"] for entry in recent_entries) / len(
            recent_entries
        )

        # Determine trend
        if len(recent_entries) >= 3:
            recent_conf = (
                sum(entry["current_confidence"] for entry in recent_entries[-3:]) / 3
            )
            earlier_conf = (
                sum(entry["current_confidence"] for entry in recent_entries[-6:-3]) / 3
                if len(progress_data) >= 6
                else recent_conf
            )

            if recent_conf > earlier_conf + 0.1:
                trend = "improving"
            elif recent_conf < earlier_conf - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        # Achievements
        achievements = []
        if avg_accuracy > 0.8:
            achievements.append("High Accuracy Analyst")
        if current_confidence > 0.7:
            achievements.append("Confident Decision Maker")
        if len(progress_data) >= 10:
            achievements.append("Persistent Learner")

        return {
            "current_confidence": current_confidence,
            "challenges_completed": len(progress_data),
            "progress_trend": trend,
            "achievements": achievements,
            "average_accuracy": avg_accuracy,
        }

    def track_analytical_confidence_progress(
        self, session_id: str, evaluation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Track analytical confidence progress (Flask interface)

        Args:
            session_id: User session identifier
            evaluation_result: Evaluation result from prediction accuracy

        Returns:
            Dict with confidence progress metrics
        """

        accuracy = evaluation_result.get("overall_accuracy", 0.5)
        confidence_level = evaluation_result.get("confidence_level", 3)

        return self._update_confidence_progress(session_id, accuracy, confidence_level)

    def track_analytical_confidence_progress_detailed(
        self,
        session_id: str,
        challenge_results: List[ChallengeResult],
        session_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Track analytical confidence progress over time

        Args:
            session_id: User session identifier
            challenge_results: List of completed challenge results
            session_data: Additional session information

        Returns:
            Dict with confidence progress metrics
        """

        if not challenge_results:
            return {
                "confidence_score": 0.5,
                "progress_trend": "neutral",
                "achievements": [],
            }

        # Calculate confidence metrics
        accuracy_scores = [r.accuracy_score for r in challenge_results]
        confidence_progressions = [r.confidence_progression for r in challenge_results]

        current_confidence = sum(confidence_progressions[-3:]) / min(
            3, len(confidence_progressions)
        )
        accuracy_trend = sum(accuracy_scores[-5:]) / min(5, len(accuracy_scores))

        # Determine progress trend
        if len(accuracy_scores) >= 3:
            recent_avg = sum(accuracy_scores[-3:]) / 3
            earlier_avg = (
                sum(accuracy_scores[-6:-3]) / 3
                if len(accuracy_scores) >= 6
                else recent_avg
            )

            if recent_avg > earlier_avg + 0.1:
                progress_trend = "improving"
            elif recent_avg < earlier_avg - 0.1:
                progress_trend = "declining"
            else:
                progress_trend = "stable"
        else:
            progress_trend = "insufficient_data"

        # Identify achievements
        achievements = []

        if accuracy_trend > 0.8:
            achievements.append("High Accuracy Achiever")
        if current_confidence > 0.6:
            achievements.append("Confident Analyst")
        if (
            len(
                [
                    r
                    for r in challenge_results
                    if r.challenge_type == ChallengeType.BLIND_ANALYSIS
                ]
            )
            >= 5
        ):
            achievements.append("Blind Analysis Expert")

        # Update confidence progression tracking
        if session_id not in self.confidence_progression:
            self.confidence_progression[session_id] = []

        confidence_entry = {
            "timestamp": time.time(),
            "confidence_score": current_confidence,
            "accuracy_trend": accuracy_trend,
            "progress_trend": progress_trend,
            "achievements": achievements,
        }

        self.confidence_progression[session_id].append(confidence_entry)

        return confidence_entry
