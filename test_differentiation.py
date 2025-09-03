#!/usr/bin/env python3
"""
Test script to verify that qualitative insights are actually different
for companies with different financial metrics.
"""

from src.tool_independence_trainer import ToolIndependenceTrainer
from src.educational_framework import LearningStage


def test_qualitative_differentiation():
    trainer = ToolIndependenceTrainer()

    # Company 1: Excellent financials
    excellent_company = {
        "symbol": "EXCELLENT",
        "company_name": "Excellent Corp",
        "industry": "Technology",
        "debt_to_equity": 0.1,  # Very low debt
        "current_ratio": 2.5,  # Excellent liquidity
        "roe": 0.25,  # Exceptional returns
        "net_margin": 0.20,  # Strong margins
        "revenue_growth": 0.20,  # High growth
    }

    # Company 2: Poor financials
    poor_company = {
        "symbol": "POOR",
        "company_name": "Struggling Corp",
        "industry": "Technology",
        "debt_to_equity": 2.0,  # Very high debt
        "current_ratio": 0.8,  # Poor liquidity
        "roe": 0.02,  # Poor returns
        "net_margin": 0.01,  # Terrible margins
        "revenue_growth": -0.05,  # Declining revenue
    }

    print("🧪 TESTING QUALITATIVE DIFFERENTIATION")
    print("=" * 50)

    challenge1 = trainer.generate_stage_appropriate_challenge(
        "test1", LearningStage.ASSISTED_ANALYSIS, excellent_company
    )

    challenge2 = trainer.generate_stage_appropriate_challenge(
        "test2", LearningStage.ASSISTED_ANALYSIS, poor_company
    )

    print("\n💎 EXCELLENT COMPANY INSIGHTS:")
    print("-" * 30)
    print("Financial Health:")
    for indicator in challenge1.company_basic_info["financial_health_indicators"]:
        print(f"  • {indicator}")

    print("\nGrowth Story:")
    for story in challenge1.company_basic_info["growth_story"]:
        print(f"  • {story}")

    print("\n💥 POOR COMPANY INSIGHTS:")
    print("-" * 30)
    print("Financial Health:")
    for indicator in challenge2.company_basic_info["financial_health_indicators"]:
        print(f"  • {indicator}")

    print("\nGrowth Story:")
    for story in challenge2.company_basic_info["growth_story"]:
        print(f"  • {story}")

    # Compare if they're the same
    same_health = (
        challenge1.company_basic_info["financial_health_indicators"]
        == challenge2.company_basic_info["financial_health_indicators"]
    )
    same_growth = (
        challenge1.company_basic_info["growth_story"]
        == challenge2.company_basic_info["growth_story"]
    )

    print(f"\n🔍 COMPARISON RESULTS:")
    print(f"Financial Health insights are the same: {same_health}")
    print(f"Growth story insights are the same: {same_growth}")

    if same_health and same_growth:
        print("❌ PROBLEM CONFIRMED: Insights are identical!")
        print("The system is NOT differentiating based on actual metrics.")
    else:
        print("✅ WORKING CORRECTLY: Insights are different!")


if __name__ == "__main__":
    test_qualitative_differentiation()
