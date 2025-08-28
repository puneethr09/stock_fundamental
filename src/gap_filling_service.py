"""
Educational Gap-Filling Service for Stock Fundamental Analysis Platform

This module implements the Educational Gap-Filling Approach from the Financial Education
Mastery Framework. The system converts data limitations into learning opportunities by
detecting low-confidence analysis areas and providing structured research guidance.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json


class GapSeverity(Enum):
    """Severity levels for identified gaps"""

    CRITICAL = "critical"
    MODERATE = "moderate"
    MINOR = "minor"


class ResearchCategory(Enum):
    """Categories for research assignments"""

    ECONOMIC_MOATS = "economic_moats"
    MANAGEMENT_QUALITY = "management_quality"
    INDUSTRY_ANALYSIS = "industry_analysis"
    FINANCIAL_DEEP_DIVE = "financial_deep_dive"
    COMPETITIVE_LANDSCAPE = "competitive_landscape"
    GOVERNANCE_ASSESSMENT = "governance_assessment"


@dataclass
class AnalysisGap:
    """Data class representing an identified analysis gap"""

    gap_id: str
    category: ResearchCategory
    severity: GapSeverity
    description: str
    missing_metrics: List[str]
    confidence_impact: float  # 0.0 to 1.0, where 1.0 is high impact
    ticker: str
    company_name: str


@dataclass
class ResearchGuide:
    """Data class for research assignments and guides"""

    guide_id: str
    gap_id: str
    title: str
    category: ResearchCategory
    objective: str
    research_questions: List[str]
    step_by_step_instructions: List[str]
    indian_market_sources: List[Dict[str, str]]
    estimated_time_minutes: int
    difficulty_level: str  # "beginner", "intermediate", "advanced"
    deliverables: List[str]


@dataclass
class ResearchProgress:
    """Data class for tracking research progress"""

    user_session_id: str
    guide_id: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    completion_percentage: float = 0.0
    notes: str = ""
    completed_steps: List[int] = None

    def __post_init__(self):
        if self.completed_steps is None:
            self.completed_steps = []


class EducationalGapFillingService:
    """
    Educational Gap-Filling Service for detecting analysis limitations and
    providing structured learning opportunities.

    Features:
    - Gap detection in financial ratio analysis
    - Research guide generation with Indian market context
    - Progress tracking for educational assignments
    - Integration with existing Five Rules analysis
    """

    def __init__(self):
        """Initialize the Educational Gap-Filling Service"""
        self.critical_ratios = [
            "ROE",
            "ROA",
            "ROIC",
            "Current Ratio",
            "Debt to Equity",
            "Operating Margin",
            "Net Profit Margin",
            "Interest Coverage",
        ]
        self.indian_market_sources = self._initialize_indian_sources()
        self.research_templates = self._initialize_research_templates()

    def _initialize_indian_sources(self) -> Dict[str, List[Dict[str, str]]]:
        """Initialize Indian market-specific data sources"""
        return {
            ResearchCategory.ECONOMIC_MOATS.value: [
                {
                    "name": "BSE Company Information",
                    "url": "https://www.bseindia.com",
                    "description": "Official company profiles and annual reports",
                    "access": "free",
                },
                {
                    "name": "NSE Corporate Information",
                    "url": "https://www.nseindia.com",
                    "description": "Listed company information and investor presentations",
                    "access": "free",
                },
                {
                    "name": "Economic Times Company Reports",
                    "url": "https://economictimes.indiatimes.com",
                    "description": "Company analysis and industry reports",
                    "access": "free",
                },
                {
                    "name": "Business Standard Archives",
                    "url": "https://www.business-standard.com",
                    "description": "Historical company performance and industry trends",
                    "access": "free",
                },
            ],
            ResearchCategory.MANAGEMENT_QUALITY.value: [
                {
                    "name": "Annual Reports (BSE/NSE)",
                    "url": "Company website investor relations section",
                    "description": "Management discussion and analysis sections",
                    "access": "free",
                },
                {
                    "name": "Corporate Governance Reports",
                    "url": "BSE/NSE regulatory filing sections",
                    "description": "Board composition and governance practices",
                    "access": "free",
                },
                {
                    "name": "Investor Presentations",
                    "url": "Company IR pages",
                    "description": "Management outlook and strategic direction",
                    "access": "free",
                },
            ],
            ResearchCategory.INDUSTRY_ANALYSIS.value: [
                {
                    "name": "CII Industry Reports",
                    "url": "https://www.cii.in",
                    "description": "Confederation of Indian Industry sector analysis",
                    "access": "free",
                },
                {
                    "name": "FICCI Sector Studies",
                    "url": "https://www.ficci.in",
                    "description": "Federation of Indian Chambers sector insights",
                    "access": "free",
                },
                {
                    "name": "ASSOCHAM Industry Analysis",
                    "url": "https://www.assocham.org",
                    "description": "Associated Chambers of Commerce reports",
                    "access": "free",
                },
                {
                    "name": "Ministry of Corporate Affairs",
                    "url": "https://www.mca.gov.in",
                    "description": "Official government industry data and regulations",
                    "access": "free",
                },
            ],
            ResearchCategory.FINANCIAL_DEEP_DIVE.value: [
                {
                    "name": "Company Annual Reports",
                    "url": "BSE/NSE company pages",
                    "description": "Detailed financial statements and notes",
                    "access": "free",
                },
                {
                    "name": "Quarterly Results",
                    "url": "BSE/NSE results section",
                    "description": "Recent financial performance data",
                    "access": "free",
                },
                {
                    "name": "SEBI EDIFAR Database",
                    "url": "https://www.sebi.gov.in",
                    "description": "Electronic Data Information Filing and Retrieval",
                    "access": "free",
                },
            ],
            ResearchCategory.COMPETITIVE_LANDSCAPE.value: [
                {
                    "name": "Industry Association Reports",
                    "url": "Sector-specific association websites",
                    "description": "Competitive positioning and market share data",
                    "access": "free",
                },
                {
                    "name": "Business News Analysis",
                    "url": "ET, BS, Mint, Hindu Business Line",
                    "description": "Competitive moves and market developments",
                    "access": "free",
                },
            ],
        }

    def _initialize_research_templates(self) -> Dict[str, ResearchGuide]:
        """Initialize research guide templates"""
        templates = {}

        # Economic Moats Research Template
        templates[ResearchCategory.ECONOMIC_MOATS.value] = {
            "title": "Economic Moats Analysis for {company_name}",
            "objective": "Identify and evaluate the competitive advantages that protect {company_name} from competition",
            "research_questions": [
                "What unique assets or capabilities does {company_name} possess?",
                "How sustainable are these competitive advantages over time?",
                "What barriers to entry exist in {company_name}'s primary business segments?",
                "How does {company_name} maintain pricing power in its markets?",
                "What switching costs do customers face when considering alternatives?",
                "How does {company_name}'s scale provide cost or operational advantages?",
            ],
            "step_by_step_instructions": [
                "Review the company's annual report management discussion section",
                "Identify the company's primary revenue streams and business segments",
                "Research the competitive landscape in each major segment",
                "Analyze barriers to entry (regulatory, capital requirements, expertise)",
                "Evaluate customer loyalty and switching costs",
                "Assess network effects or scale advantages",
                "Compare with direct competitors' positioning",
                "Document evidence of sustained competitive advantages",
            ],
            "estimated_time_minutes": 90,
            "difficulty_level": "intermediate",
            "deliverables": [
                "List of identified competitive advantages",
                "Assessment of moat sustainability (1-5 years)",
                "Comparison with key competitors",
                "Risk factors that could erode competitive position",
            ],
        }

        # Management Quality Template
        templates[ResearchCategory.MANAGEMENT_QUALITY.value] = {
            "title": "Management Quality Assessment for {company_name}",
            "objective": "Evaluate the competence, integrity, and strategic vision of {company_name}'s management team",
            "research_questions": [
                "What is the track record of key management personnel?",
                "How transparent is management in communicating with shareholders?",
                "What is the management's strategic vision and execution capability?",
                "How does management allocate capital (acquisitions, dividends, buybacks)?",
                "What is the board composition and independence level?",
                "How does management compensation align with shareholder interests?",
            ],
            "step_by_step_instructions": [
                "Review management profiles in annual reports",
                "Analyze management discussion and analysis sections",
                "Research background of CEO and key executives",
                "Evaluate capital allocation decisions over past 5 years",
                "Review board composition and director qualifications",
                "Assess management compensation structure",
                "Look for any governance issues or controversies",
                "Compare with industry best practices",
            ],
            "estimated_time_minutes": 75,
            "difficulty_level": "intermediate",
            "deliverables": [
                "Management team assessment summary",
                "Capital allocation effectiveness analysis",
                "Governance strengths and weaknesses",
                "Red flags or areas of concern",
            ],
        }

        # Financial Deep-Dive Template
        templates[ResearchCategory.FINANCIAL_DEEP_DIVE.value] = {
            "title": "Financial Deep-Dive Analysis for {company_name}",
            "objective": "Manually calculate and verify key financial metrics when automated data is incomplete",
            "research_questions": [
                "What are the company's true earnings quality indicators?",
                "How consistent are the financial reporting practices?",
                "What off-balance-sheet items might affect financial position?",
                "How does working capital management affect cash flow?",
                "What seasonal or cyclical factors impact financial performance?",
            ],
            "step_by_step_instructions": [
                "Download the latest 3 annual reports from company website",
                "Extract balance sheet, income statement, and cash flow data",
                "Calculate missing ratios using raw financial statement data",
                "Verify automated calculations against manual calculations",
                "Identify any unusual items or accounting adjustments",
                "Analyze cash flow quality and working capital trends",
                "Review notes to financial statements for important details",
            ],
            "estimated_time_minutes": 120,
            "difficulty_level": "advanced",
            "deliverables": [
                "Manually calculated financial ratios spreadsheet",
                "Earnings quality assessment",
                "Cash flow analysis summary",
                "Accounting policy evaluation",
            ],
        }

        return templates

    def detect_analysis_gaps(
        self,
        ratios_df: pd.DataFrame,
        warnings: List[str],
        company_name: str,
        ticker: str,
    ) -> List[AnalysisGap]:
        """
        Detect gaps in the financial analysis that could benefit from manual research

        Args:
            ratios_df: DataFrame with financial ratios
            warnings: List of existing analysis warnings
            company_name: Company name for context
            ticker: Stock ticker symbol

        Returns:
            List of identified analysis gaps
        """
        gaps = []

        if ratios_df is None or ratios_df.empty:
            # Critical gap - no data available at all
            gaps.append(
                AnalysisGap(
                    gap_id=f"{ticker}_no_data",
                    category=ResearchCategory.FINANCIAL_DEEP_DIVE,
                    severity=GapSeverity.CRITICAL,
                    description="No financial data available from automated sources",
                    missing_metrics=["All financial ratios"],
                    confidence_impact=1.0,
                    ticker=ticker,
                    company_name=company_name,
                )
            )
            return gaps

        # Check for missing critical ratios
        missing_ratios = []
        for ratio in self.critical_ratios:
            if ratio not in ratios_df.columns:
                missing_ratios.append(ratio)
            else:
                # Check for NaN values in the ratio
                nan_count = ratios_df[ratio].isna().sum()
                if nan_count > len(ratios_df) * 0.5:  # More than 50% missing
                    missing_ratios.append(ratio)

        if missing_ratios:
            severity = (
                GapSeverity.CRITICAL
                if len(missing_ratios) > 4
                else GapSeverity.MODERATE
            )
            gaps.append(
                AnalysisGap(
                    gap_id=f"{ticker}_missing_ratios",
                    category=ResearchCategory.FINANCIAL_DEEP_DIVE,
                    severity=severity,
                    description=f"Missing or incomplete financial ratios: {', '.join(missing_ratios)}",
                    missing_metrics=missing_ratios,
                    confidence_impact=len(missing_ratios) / len(self.critical_ratios),
                    ticker=ticker,
                    company_name=company_name,
                )
            )

        # Check historical data availability
        if len(ratios_df) < 3:
            gaps.append(
                AnalysisGap(
                    gap_id=f"{ticker}_limited_history",
                    category=ResearchCategory.FINANCIAL_DEEP_DIVE,
                    severity=GapSeverity.MODERATE,
                    description=f"Limited historical data available ({len(ratios_df)} years)",
                    missing_metrics=["Historical trend analysis"],
                    confidence_impact=0.6,
                    ticker=ticker,
                    company_name=company_name,
                )
            )

        # Detect industry-specific gaps based on warnings
        high_warning_count = len(
            [
                w
                for w in warnings
                if any(
                    keyword in w.lower() for keyword in ["high", "low", "poor", "risk"]
                )
            ]
        )

        if high_warning_count >= 3:
            gaps.append(
                AnalysisGap(
                    gap_id=f"{ticker}_competitive_analysis",
                    category=ResearchCategory.ECONOMIC_MOATS,
                    severity=GapSeverity.MODERATE,
                    description="Multiple performance warnings suggest need for competitive analysis",
                    missing_metrics=["Competitive positioning", "Economic moats"],
                    confidence_impact=0.7,
                    ticker=ticker,
                    company_name=company_name,
                )
            )

        # Always suggest management quality assessment for comprehensive analysis
        gaps.append(
            AnalysisGap(
                gap_id=f"{ticker}_management_quality",
                category=ResearchCategory.MANAGEMENT_QUALITY,
                severity=GapSeverity.MINOR,
                description="Management quality assessment recommended for complete analysis",
                missing_metrics=["Management competence", "Corporate governance"],
                confidence_impact=0.3,
                ticker=ticker,
                company_name=company_name,
            )
        )

        # Industry analysis gap for contextual understanding
        gaps.append(
            AnalysisGap(
                gap_id=f"{ticker}_industry_context",
                category=ResearchCategory.INDUSTRY_ANALYSIS,
                severity=GapSeverity.MINOR,
                description="Industry analysis provides important context for ratio interpretation",
                missing_metrics=["Industry benchmarks", "Sector trends"],
                confidence_impact=0.4,
                ticker=ticker,
                company_name=company_name,
            )
        )

        return gaps

    def generate_research_guides(self, gaps: List[AnalysisGap]) -> List[ResearchGuide]:
        """
        Generate detailed research guides for identified gaps

        Args:
            gaps: List of identified analysis gaps

        Returns:
            List of research guides with step-by-step instructions
        """
        guides = []

        for gap in gaps:
            template = self.research_templates.get(gap.category.value)
            if not template:
                continue

            guide = ResearchGuide(
                guide_id=f"guide_{gap.gap_id}",
                gap_id=gap.gap_id,
                title=template["title"].format(company_name=gap.company_name),
                category=gap.category,
                objective=template["objective"].format(company_name=gap.company_name),
                research_questions=template["research_questions"],
                step_by_step_instructions=template["step_by_step_instructions"],
                indian_market_sources=self.indian_market_sources.get(
                    gap.category.value, []
                ),
                estimated_time_minutes=template["estimated_time_minutes"],
                difficulty_level=template["difficulty_level"],
                deliverables=template["deliverables"],
            )

            guides.append(guide)

        # Sort by severity and confidence impact
        guides.sort(
            key=lambda g: (
                (
                    0
                    if any(
                        gap.severity == GapSeverity.CRITICAL
                        for gap in gaps
                        if gap.gap_id == g.gap_id.replace("guide_", "")
                    )
                    else (
                        1
                        if any(
                            gap.severity == GapSeverity.MODERATE
                            for gap in gaps
                            if gap.gap_id == g.gap_id.replace("guide_", "")
                        )
                        else 2
                    )
                ),
                -max(
                    [
                        gap.confidence_impact
                        for gap in gaps
                        if gap.gap_id == g.gap_id.replace("guide_", "")
                    ],
                    default=0,
                ),
            )
        )

        return guides

    def get_indian_market_sources(
        self, category: ResearchCategory
    ) -> List[Dict[str, str]]:
        """
        Get Indian market-specific sources for a research category

        Args:
            category: Research category

        Returns:
            List of relevant Indian market sources
        """
        return self.indian_market_sources.get(category.value, [])

    def track_research_progress(
        self,
        session_data: Dict[str, Any],
        guide_id: str,
        progress_update: Dict[str, Any],
    ) -> ResearchProgress:
        """
        Track research assignment progress for a user session

        Args:
            session_data: Flask session data
            guide_id: Research guide identifier
            progress_update: Progress update data

        Returns:
            Updated research progress object
        """
        session_id = session_data.get("session_id", "anonymous")
        progress_key = f"research_progress_{guide_id}"

        # Get existing progress or create new
        existing_progress = session_data.get(progress_key, {})

        progress = ResearchProgress(
            user_session_id=session_id,
            guide_id=guide_id,
            started_at=existing_progress.get(
                "started_at", progress_update.get("started_at")
            ),
            completed_at=progress_update.get("completed_at"),
            completion_percentage=progress_update.get("completion_percentage", 0.0),
            notes=progress_update.get("notes", ""),
            completed_steps=progress_update.get("completed_steps", []),
        )

        # Store back in session
        session_data[progress_key] = {
            "user_session_id": progress.user_session_id,
            "guide_id": progress.guide_id,
            "started_at": progress.started_at,
            "completed_at": progress.completed_at,
            "completion_percentage": progress.completion_percentage,
            "notes": progress.notes,
            "completed_steps": progress.completed_steps,
        }

        return progress

    def get_user_progress_summary(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get summary of user's research progress

        Args:
            session_data: Flask session data

        Returns:
            Summary of research progress
        """
        progress_items = [
            (key, value)
            for key, value in session_data.items()
            if key.startswith("research_progress_")
        ]

        total_guides = len(progress_items)
        completed_guides = len(
            [
                item
                for _, item in progress_items
                if item.get("completion_percentage", 0) >= 100
            ]
        )

        in_progress_guides = len(
            [
                item
                for _, item in progress_items
                if 0 < item.get("completion_percentage", 0) < 100
            ]
        )

        total_time_spent = sum(
            [
                item.get("estimated_time", 0)
                * item.get("completion_percentage", 0)
                / 100
                for _, item in progress_items
            ]
        )

        return {
            "total_guides": total_guides,
            "completed_guides": completed_guides,
            "in_progress_guides": in_progress_guides,
            "completion_rate": (
                (completed_guides / total_guides * 100) if total_guides > 0 else 0
            ),
            "estimated_time_spent_minutes": total_time_spent,
        }

    def calculate_analysis_confidence_score(self, gaps: List[AnalysisGap]) -> float:
        """
        Calculate overall analysis confidence score based on identified gaps

        Args:
            gaps: List of identified analysis gaps

        Returns:
            Confidence score from 0.0 to 1.0 (higher is better)
        """
        if not gaps:
            return 1.0

        # Weight gaps by severity and confidence impact
        severity_weights = {
            GapSeverity.CRITICAL: 1.0,
            GapSeverity.MODERATE: 0.6,
            GapSeverity.MINOR: 0.2,
        }

        total_impact = sum(
            gap.confidence_impact * severity_weights[gap.severity] for gap in gaps
        )

        # Normalize to 0-1 scale (assuming max possible impact is number of gaps)
        max_possible_impact = len(gaps)
        confidence_score = max(0.0, 1.0 - (total_impact / max_possible_impact))

        return confidence_score
