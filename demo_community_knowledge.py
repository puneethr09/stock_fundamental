#!/usr/bin/env python3
"""
Community Knowledge Base System - Demo Script

This script demonstrates the core functionality of the Community Knowledge Base System
including contribution, voting, and retrieval of community insights.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from community_knowledge import CommunityKnowledgeBase, InsightCategory
import tempfile


def demo_community_knowledge_system():
    """Demonstrate the Community Knowledge Base System functionality"""

    print("=" * 60)
    print("Community Knowledge Base System - Demo")
    print("=" * 60)

    # Create temporary database for demo
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        demo_db_path = tmp.name

    try:
        # Initialize the system
        kb = CommunityKnowledgeBase(db_path=demo_db_path)
        print("✅ Community Knowledge Base initialized")

        # Generate some demo users
        user1 = kb.generate_anonymous_user_id("demo_user_session_1")
        user2 = kb.generate_anonymous_user_id("demo_user_session_2")
        user3 = kb.generate_anonymous_user_id("demo_user_session_3")

        print(f"✅ Generated anonymous user IDs")
        print(f"   User 1: {user1}")
        print(f"   User 2: {user2}")
        print(f"   User 3: {user3}")
        print()

        # Demo 1: Contributing insights
        print("📝 DEMO 1: Contributing Community Insights")
        print("-" * 40)

        insights_data = [
            (
                "TCS",
                InsightCategory.MOAT_ANALYSIS,
                user1,
                "TCS has a strong competitive moat due to its established client relationships, "
                "scale advantages, and deep domain expertise in banking and financial services.",
            ),
            (
                "TCS",
                InsightCategory.MANAGEMENT,
                user2,
                "The management team has consistently delivered strong results with focus on "
                "digital transformation and maintaining industry-leading margins.",
            ),
            (
                "INFY",
                InsightCategory.COMPETITIVE_ANALYSIS,
                user1,
                "Infosys is well-positioned against competitors with its strong automation "
                "capabilities and growing cloud services portfolio.",
            ),
            (
                "TCS",
                InsightCategory.INDUSTRY_ANALYSIS,
                user3,
                "The IT services industry is experiencing robust growth driven by digital "
                "transformation needs across all sectors post-pandemic.",
            ),
        ]

        for ticker, category, user_id, content in insights_data:
            success, message = kb.contribute_insight(ticker, category, content, user_id)
            if success:
                print(f"✅ {ticker} - {category.value}: {message}")
            else:
                print(f"❌ {ticker} - {category.value}: {message}")

        print()

        # Demo 2: Retrieving insights
        print("🔍 DEMO 2: Retrieving Community Insights")
        print("-" * 40)

        tcs_insights = kb.get_insights_for_ticker("TCS")
        print(f"Found {len(tcs_insights)} insights for TCS:")

        for i, insight in enumerate(tcs_insights, 1):
            print(
                f"\n{i}. Category: {insight.category.value.replace('_', ' ').title()}"
            )
            print(f"   Content: {insight.content[:80]}...")
            print(f"   Votes: ↑{insight.votes_up} ↓{insight.votes_down}")
            print(f"   Created: {insight.created_at.strftime('%Y-%m-%d %H:%M')}")

        print()

        # Demo 3: Voting system
        print("🗳️  DEMO 3: Community Voting System")
        print("-" * 40)

        # Get first insight ID for voting
        if tcs_insights:
            insight_id = tcs_insights[0].id

            # Different users vote on the insight
            success1, msg1 = kb.vote_on_insight(insight_id, user2, "up")
            success2, msg2 = kb.vote_on_insight(insight_id, user3, "up")

            print(f"Vote 1 (User 2): {'✅' if success1 else '❌'} {msg1}")
            print(f"Vote 2 (User 3): {'✅' if success2 else '❌'} {msg2}")

            # Check updated vote counts
            updated_insights = kb.get_insights_for_ticker("TCS")
            first_insight = updated_insights[0]
            print(
                f"Updated votes for first insight: ↑{first_insight.votes_up} ↓{first_insight.votes_down}"
            )

        print()

        # Demo 4: Category-based insights
        print("📊 DEMO 4: Insights by Category")
        print("-" * 40)

        moat_insights = kb.get_insights_by_category(InsightCategory.MOAT_ANALYSIS)
        print(f"Found {len(moat_insights)} moat analysis insights across all stocks:")

        for insight in moat_insights:
            print(f"• {insight.ticker}: {insight.content[:60]}...")

        print()

        # Demo 5: Spam prevention
        print("🛡️  DEMO 5: Spam Prevention System")
        print("-" * 40)

        # Try to submit duplicate content
        duplicate_content = insights_data[0][3]  # Same content as first insight
        success, message = kb.contribute_insight(
            "TCS", InsightCategory.MOAT_ANALYSIS, duplicate_content, user1
        )
        print(f"Duplicate content submission: {'✅' if success else '❌'} {message}")

        # Try invalid content
        invalid_content = "Too short"
        success, message = kb.contribute_insight(
            "TCS", InsightCategory.MOAT_ANALYSIS, invalid_content, user2
        )
        print(f"Invalid content submission: {'✅' if success else '❌'} {message}")

        print()

        # Demo 6: User statistics
        print("📈 DEMO 6: User Contribution Statistics")
        print("-" * 40)

        for i, user_id in enumerate([user1, user2, user3], 1):
            stats = kb.get_contribution_stats(user_id)
            print(f"User {i} Statistics:")
            print(f"  Total Contributions: {stats['total_contributions']}")
            print(f"  Total Upvotes: {stats['total_up_votes']}")
            print(f"  Total Downvotes: {stats['total_down_votes']}")
            print(f"  Net Vote Score: {stats['net_votes']}")
            print()

        print("=" * 60)
        print("✅ Demo completed successfully!")
        print(
            "The Community Knowledge Base System is fully functional and ready for use."
        )
        print("=" * 60)

    finally:
        # Clean up temporary database
        try:
            os.unlink(demo_db_path)
        except:
            pass


if __name__ == "__main__":
    demo_community_knowledge_system()
