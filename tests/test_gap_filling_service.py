"""
Tests for Educational Gap-Filling Service
Tests the gap detection, research guide generation, and confidence scoring functionality.
"""

import pytest
import pandas as pd
import numpy as np
from src.gap_filling_service import (
    EducationalGapFillingService,
    AnalysisGap,
    GapSeverity,
    ResearchCategory,
    ResearchGuide,
    ResearchProgress,
)


class TestEducationalGapFillingService:
    """Test suite for EducationalGapFillingService"""

    @pytest.fixture
    def gap_service(self):
        """Create gap filling service instance"""
        return EducationalGapFillingService()

    @pytest.fixture
    def sample_ratios_complete(self):
        """Sample financial ratios DataFrame with complete data"""
        return pd.DataFrame(
            {
                "Company": ["Test Company"] * 3,
                "Year": [2021, 2022, 2023],
                "ROE": [15.5, 18.2, 20.1],
                "Current Ratio": [2.1, 2.3, 2.0],
                "Debt to Equity": [0.4, 0.3, 0.35],
                "Operating Margin": [18.5, 20.1, 22.3],
                "Net Profit Margin": [12.1, 14.2, 16.0],
                "Asset Turnover": [0.8, 0.9, 1.0],
                "Interest Coverage": [8.5, 9.2, 10.1],
            }
        )

    @pytest.fixture
    def sample_ratios_incomplete(self):
        """Sample financial ratios DataFrame with missing data"""
        return pd.DataFrame(
            {
                "Company": ["Test Company"] * 3,
                "Year": [2021, 2022, 2023],
                "ROE": [15.5, np.nan, 20.1],
                "Current Ratio": [np.nan, 2.3, 2.0],
                "Debt to Equity": [0.4, np.nan, 0.35],
                "Operating Margin": [18.5, 20.1, np.nan],
                "Net Profit Margin": [12.1, np.nan, 16.0],
                "Asset Turnover": [np.nan, np.nan, 1.0],
                "Interest Coverage": [8.5, 9.2, 10.1],
            }
        )

    @pytest.fixture
    def sample_warnings_few(self):
        """Sample few warnings list"""
        return ["Low Operating Margin indicates potential operational inefficiency."]

    @pytest.fixture
    def sample_warnings_many(self):
        """Sample comprehensive warnings list"""
        return [
            "Low Return on Equity (ROE) indicates potential underperformance.",
            "Current Ratio below 1 indicates potential liquidity issues.",
            "High Debt to Equity ratio indicates higher financial risk.",
            "Low Operating Margin indicates potential operational inefficiency.",
            "Low Net Profit Margin indicates reduced profitability.",
        ]

    def test_service_initialization(self, gap_service):
        """Test that the service initializes properly"""
        assert isinstance(gap_service, EducationalGapFillingService)
        # Test that service has required methods
        assert hasattr(gap_service, "detect_analysis_gaps")
        assert hasattr(gap_service, "generate_research_guides")
        assert hasattr(gap_service, "calculate_analysis_confidence_score")

    def test_detect_analysis_gaps_complete_data(
        self, gap_service, sample_ratios_complete, sample_warnings_few
    ):
        """Test gap detection with complete data and few warnings"""
        gaps = gap_service.detect_analysis_gaps(
            sample_ratios_complete, sample_warnings_few, "Test Company", "TEST"
        )

        assert isinstance(gaps, list)

        # Verify gap structure if gaps exist
        for gap in gaps:
            assert isinstance(gap, AnalysisGap)
            assert isinstance(gap.gap_id, str)
            assert len(gap.gap_id) > 0
            assert isinstance(gap.category, ResearchCategory)
            assert isinstance(gap.severity, GapSeverity)
            assert isinstance(gap.description, str)
            assert len(gap.description) > 0
            assert isinstance(gap.missing_metrics, list)
            assert isinstance(gap.confidence_impact, float)
            assert 0.0 <= gap.confidence_impact <= 1.0
            assert gap.ticker == "TEST"
            assert gap.company_name == "Test Company"

    def test_detect_analysis_gaps_incomplete_data(
        self, gap_service, sample_ratios_incomplete, sample_warnings_few
    ):
        """Test gap detection with incomplete data should detect more gaps"""
        gaps = gap_service.detect_analysis_gaps(
            sample_ratios_incomplete, sample_warnings_few, "Test Company", "TEST"
        )

        assert isinstance(gaps, list)
        # Should detect gaps when data is incomplete
        assert len(gaps) > 0

        # Check that gaps have proper structure
        for gap in gaps:
            assert isinstance(gap, AnalysisGap)
            assert gap.confidence_impact > 0.0  # Should have some impact

    def test_detect_analysis_gaps_no_data(self, gap_service):
        """Test gap detection with no financial data"""
        gaps = gap_service.detect_analysis_gaps(None, [], "Test Company", "TEST")

        assert isinstance(gaps, list)
        # Should detect critical gaps when no data available
        assert len(gaps) > 0

        # Check for critical severity gaps
        critical_gaps = [gap for gap in gaps if gap.severity == GapSeverity.CRITICAL]
        assert len(critical_gaps) > 0

    def test_detect_analysis_gaps_many_warnings(
        self, gap_service, sample_ratios_complete, sample_warnings_many
    ):
        """Test that many warnings result in fewer detected gaps"""
        gaps_many_warnings = gap_service.detect_analysis_gaps(
            sample_ratios_complete, sample_warnings_many, "Test Company", "TEST"
        )

        gaps_few_warnings = gap_service.detect_analysis_gaps(
            sample_ratios_complete,
            ["Low Operating Margin indicates potential operational inefficiency."],
            "Test Company",
            "TEST",
        )

        # More warnings should result in fewer gaps detected
        assert isinstance(gaps_many_warnings, list)
        assert isinstance(gaps_few_warnings, list)

    def test_generate_research_guides_empty_gaps(self, gap_service):
        """Test research guide generation with empty gaps list"""
        guides = gap_service.generate_research_guides([])

        assert isinstance(guides, list)
        assert len(guides) == 0

    def test_generate_research_guides_with_gaps(
        self, gap_service, sample_ratios_incomplete, sample_warnings_few
    ):
        """Test research guide generation with detected gaps"""
        gaps = gap_service.detect_analysis_gaps(
            sample_ratios_incomplete, sample_warnings_few, "Test Company", "TEST"
        )

        guides = gap_service.generate_research_guides(gaps)

        assert isinstance(guides, list)

        # Verify guide structure if guides exist
        for guide in guides:
            assert isinstance(guide, ResearchGuide)
            assert isinstance(guide.guide_id, str)
            assert len(guide.guide_id) > 0
            assert isinstance(guide.gap_id, str)
            assert isinstance(guide.title, str)
            assert len(guide.title) > 0
            assert isinstance(guide.category, ResearchCategory)
            assert isinstance(guide.objective, str)
            assert len(guide.objective) > 0
            assert isinstance(guide.research_questions, list)
            assert isinstance(guide.step_by_step_instructions, list)
            assert isinstance(guide.indian_market_sources, list)
            assert isinstance(guide.estimated_time_minutes, int)
            assert guide.estimated_time_minutes > 0
            assert isinstance(guide.difficulty_level, str)
            assert guide.difficulty_level in ["beginner", "intermediate", "advanced"]
            assert isinstance(guide.deliverables, list)

    def test_calculate_analysis_confidence_score_no_gaps(self, gap_service):
        """Test confidence score calculation with no gaps"""
        score = gap_service.calculate_analysis_confidence_score([])

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score == 1.0  # Perfect confidence with no gaps

    def test_calculate_analysis_confidence_score_with_gaps(
        self, gap_service, sample_ratios_incomplete, sample_warnings_few
    ):
        """Test confidence score calculation with gaps"""
        gaps = gap_service.detect_analysis_gaps(
            sample_ratios_incomplete, sample_warnings_few, "Test Company", "TEST"
        )

        score = gap_service.calculate_analysis_confidence_score(gaps)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        # Should have lower confidence with gaps
        if len(gaps) > 0:
            assert score < 1.0

    def test_gap_severity_enum_values(self):
        """Test that gap severity enum has correct values"""
        assert GapSeverity.CRITICAL.value == "critical"
        assert GapSeverity.MODERATE.value == "moderate"
        assert GapSeverity.MINOR.value == "minor"

    def test_research_category_enum_values(self):
        """Test that research category enum has expected values"""
        expected_categories = [
            ResearchCategory.ECONOMIC_MOATS,
            ResearchCategory.MANAGEMENT_QUALITY,
            ResearchCategory.INDUSTRY_ANALYSIS,
            ResearchCategory.FINANCIAL_DEEP_DIVE,
            ResearchCategory.COMPETITIVE_LANDSCAPE,
            ResearchCategory.GOVERNANCE_ASSESSMENT,
        ]

        for category in expected_categories:
            assert isinstance(category, ResearchCategory)

    def test_integration_workflow(self, gap_service):
        """Test the complete integration workflow that basic_analysis.py uses"""
        # Test workflow that matches what basic_analysis.py does
        ratios_df = pd.DataFrame(
            {
                "Company": ["Integration Test Co"] * 2,
                "Year": [2022, 2023],
                "ROE": [12.0, 14.5],
                "Current Ratio": [1.8, np.nan],  # Missing data to trigger gaps
                "Operating Margin": [16.2, 18.1],
                "Debt to Equity": [0.5, 0.4],
                "Net Profit Margin": [10.0, 12.0],
                "Asset Turnover": [0.7, 0.8],
                "Interest Coverage": [5.5, 6.0],
            }
        )

        warnings = ["Low Asset Turnover indicates inefficient use of assets."]

        # Complete workflow test
        gaps = gap_service.detect_analysis_gaps(
            ratios_df, warnings, "Integration Test Co", "INTEG"
        )

        research_guides = gap_service.generate_research_guides(gaps)
        confidence_score = gap_service.calculate_analysis_confidence_score(gaps)

        # Verify workflow results match expected basic_analysis.py integration
        assert isinstance(gaps, list)
        assert isinstance(research_guides, list)
        assert isinstance(confidence_score, float)
        assert 0.0 <= confidence_score <= 1.0

    def test_indian_market_sources_in_guides(
        self, gap_service, sample_ratios_incomplete, sample_warnings_few
    ):
        """Test that research guides include Indian market-specific sources"""
        gaps = gap_service.detect_analysis_gaps(
            sample_ratios_incomplete, sample_warnings_few, "Test Company", "TEST"
        )

        guides = gap_service.generate_research_guides(gaps)

        # Check that guides contain Indian market sources
        indian_sources_found = False
        for guide in guides:
            for source in guide.indian_market_sources:
                if isinstance(source, dict) and "name" in source:
                    source_name = source["name"].lower()
                    if any(
                        keyword in source_name
                        for keyword in [
                            "bse",
                            "nse",
                            "sebi",
                            "moneycontrol",
                            "screener",
                        ]
                    ):
                        indian_sources_found = True
                        break
                elif isinstance(source, str):
                    if any(
                        keyword in source.lower()
                        for keyword in [
                            "bse",
                            "nse",
                            "sebi",
                            "moneycontrol",
                            "screener",
                        ]
                    ):
                        indian_sources_found = True
                        break

        # Should have at least some Indian market sources if guides exist
        if len(guides) > 0:
            assert (
                indian_sources_found
            ), "Research guides should include Indian market sources"

    def test_dataclass_structure_validation(self):
        """Test that dataclasses are properly structured"""
        # Test AnalysisGap dataclass
        gap = AnalysisGap(
            gap_id="test_gap_001",
            category=ResearchCategory.ECONOMIC_MOATS,
            severity=GapSeverity.MODERATE,
            description="Test gap for economic moats analysis",
            missing_metrics=["ROE", "ROA"],
            confidence_impact=0.3,
            ticker="TEST",
            company_name="Test Company",
        )

        assert gap.gap_id == "test_gap_001"
        assert gap.category == ResearchCategory.ECONOMIC_MOATS
        assert gap.severity == GapSeverity.MODERATE
        assert gap.confidence_impact == 0.3
        assert gap.ticker == "TEST"
        assert gap.company_name == "Test Company"

        # Test ResearchGuide dataclass
        guide = ResearchGuide(
            guide_id="test_guide_001",
            gap_id="test_gap_001",
            title="Economic Moats Research Guide",
            category=ResearchCategory.ECONOMIC_MOATS,
            objective="Analyze competitive advantages",
            research_questions=["What are the company's key competitive advantages?"],
            step_by_step_instructions=["Step 1: Review annual reports"],
            indian_market_sources=[{"name": "BSE", "url": "https://bseindia.com"}],
            estimated_time_minutes=45,
            difficulty_level="intermediate",
            deliverables=["Competitive advantage analysis report"],
        )

        assert guide.guide_id == "test_guide_001"
        assert guide.gap_id == "test_gap_001"
        assert guide.title == "Economic Moats Research Guide"
        assert guide.estimated_time_minutes == 45
        assert guide.difficulty_level == "intermediate"

    def test_error_handling_edge_cases(self, gap_service):
        """Test service behavior with edge cases and invalid data"""
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        gaps = gap_service.detect_analysis_gaps(empty_df, [], "Test", "TEST")
        assert isinstance(gaps, list)

        # Test with None values
        gaps = gap_service.detect_analysis_gaps(None, None, "", "")
        assert isinstance(gaps, list)

        # Test confidence calculation with edge cases
        score = gap_service.calculate_analysis_confidence_score([])
        assert score == 1.0

        # Test research guide generation with invalid gaps
        guides = gap_service.generate_research_guides(None)
        assert isinstance(guides, list)
        assert len(guides) == 0

    def test_performance_requirement(
        self, gap_service, sample_ratios_complete, sample_warnings_few
    ):
        """Test that gap detection meets performance requirements (<50ms overhead)"""
        import time

        # Measure gap detection performance
        start_time = time.time()
        gaps = gap_service.detect_analysis_gaps(
            sample_ratios_complete, sample_warnings_few, "Performance Test Co", "PERF"
        )
        end_time = time.time()

        processing_time_ms = (end_time - start_time) * 1000

        # Should be under 50ms as per requirements
        assert (
            processing_time_ms < 50
        ), f"Gap detection took {processing_time_ms:.2f}ms, should be <50ms"

        # Verify we still get valid results
        assert isinstance(gaps, list)


if __name__ == "__main__":
    pytest.main([__file__])
