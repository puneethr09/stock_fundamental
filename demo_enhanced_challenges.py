#!/usr/bin/env python3
"""
Demo script showing the enhanced Tool Independence Training System
with rich qualitative information that enables meaningful analysis
without relying on exact metrics.
"""

from src.tool_independence_trainer import (
    ToolIndependenceTrainer,
    UserPrediction,
    PredictionCategory,
)
from src.educational_framework import LearningStage
import time


def demo_enhanced_challenge_system():
    """Demonstrate the enhanced challenge system with rich qualitative information"""

    print("🎯 TOOL INDEPENDENCE TRAINING SYSTEM - ENHANCED DEMO")
    print("=" * 60)

    trainer = ToolIndependenceTrainer()

    # Test with dramatically different company scenarios
    companies = [
        {
            "name": "STAR PERFORMER (Excellent Metrics)",
            "data": {
                "symbol": "STAR",
                "company_name": "Star Performer Limited",
                "industry": "Information Technology",
                "sector": "Technology",
                "business_description": "Global leader in next-generation digital services and consulting",
                "market_cap": 150000,  # Large cap
                "debt_to_equity": 0.05,  # Extremely low debt
                "current_ratio": 3.0,  # Excellent liquidity
                "roe": 0.35,  # Exceptional returns
                "net_margin": 0.25,  # Outstanding margins
                "revenue_growth": 0.30,  # Explosive growth
            },
        },
        {
            "name": "STRUGGLING COMPANY (Poor Metrics)",
            "data": {
                "symbol": "DEBT",
                "company_name": "Debt-Heavy Industries",
                "industry": "Steel & Iron",
                "sector": "Basic Materials",
                "business_description": "Traditional steel manufacturing facing challenges",
                "market_cap": 8000,  # Small cap
                "debt_to_equity": 3.0,  # Extremely high debt
                "current_ratio": 0.7,  # Poor liquidity
                "roe": 0.01,  # Terrible returns
                "net_margin": 0.005,  # Almost no profitability
                "revenue_growth": -0.15,  # Declining revenue
            },
        },
    ]

    for company in companies:
        print(f"\n📊 SCENARIO: {company['name']}")
        print("-" * 40)

        # Generate challenge
        challenge = trainer.generate_stage_appropriate_challenge(
            session_id="demo_session",
            current_stage=LearningStage.ASSISTED_ANALYSIS,
            company_data=company["data"],
        )

        print(f"Company: {challenge.company_basic_info['company_name']}")
        print(f"Industry: {challenge.company_basic_info['industry']}")
        print(f"Market Cap: {challenge.company_basic_info['market_cap_range']}")

        print("\n💡 QUALITATIVE INSIGHTS PROVIDED:")

        print("\n  🏦 Financial Health:")
        for indicator in challenge.company_basic_info["financial_health_indicators"]:
            print(f"    • {indicator}")

        print("\n  📈 Growth Narrative:")
        for story in challenge.company_basic_info["growth_story"]:
            print(f"    • {story}")

        print("\n  🏢 Business Model:")
        for insight in challenge.company_basic_info["business_model_strength"][:2]:
            print(f"    • {insight}")

        print("\n  ⚠️ Risk Factors:")
        for risk in challenge.company_basic_info["risk_signals"][:2]:
            print(f"    • {risk}")

        print(f"\n❓ ANALYTICAL CHALLENGE:")
        print(f"   {challenge.prediction_prompts[0]['prompt']}")

        print("\n" + "=" * 60)

    print("\n✅ CONCLUSION:")
    print("The enhanced system provides rich qualitative context that enables")
    print("meaningful analytical thinking WITHOUT revealing exact metrics!")
    print("Users can now make informed predictions based on:")
    print("  • Business model insights")
    print("  • Industry dynamics")
    print("  • Competitive positioning")
    print("  • Management quality signals")
    print("  • Financial health narratives")
    print("  • Growth story context")


if __name__ == "__main__":
    demo_enhanced_challenge_system()
