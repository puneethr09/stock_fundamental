"""
Dorsey Runner - Main Integration Module

Executes the complete Dorsey Protocol for stock analysis.
Combines all modules into a unified analysis result for the UI.

Includes:
- Ten-Minute Test (Chapter 12)
- Moat Analysis (Chapter 3)
- Financial Health (Chapters 5-8)
- Valuation (Chapters 9-10)
- Sector-Specific Analysis (Chapters 13-26)
- Mistake Detection (Chapter 2)
- Dorsey Scorecard (Chapter 11)
- Graham Analysis (Intelligent Investor)
"""

from src.ten_minute_test import TenMinuteTest
from src.dorsey_core.moat import MoatAnalyzer
from src.dorsey_core.financials import FinancialsAnalyzer
from src.dorsey_core.valuation import ValuationAnalyzer
from src.dorsey_core.mistake_detector import MistakeDetector
from src.dorsey_core.scorecard import DorseyScorecard
from src.dorsey_sectors.factory import SectorFactory

# Graham modules
from src.graham.intelligent_investor import GrahamAnalyzer
from src.graham.defensive_criteria import DefensiveInvestorScreen


def run_dorsey_analysis(ticker):
    """
    Executes the full Dorsey Protocol.
    Returns a unified dictionary for the UI.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'TCS.NS')
        
    Returns:
        Dictionary containing all analysis results
    """
    results = {}
    
    # ============================================================
    # 1. TEN MINUTE TEST (Chapter 12)
    # ============================================================
    tm = TenMinuteTest(ticker)
    results["ten_minute_test"] = tm.run_test()
    
    # ============================================================
    # 2. CORE FRAMEWORK
    # ============================================================
    
    # Moat Analysis (Chapter 3)
    m = MoatAnalyzer(ticker)
    results["moat_analysis"] = m.analyze_moat()
    
    # Financial Health (Chapters 5-8)
    f = FinancialsAnalyzer(ticker)
    results["financial_health"] = f.analyze_health()
    
    # Valuation (Chapters 9-10)
    v = ValuationAnalyzer(ticker)
    results["valuation"] = v.get_valuation_verdict()
    
    # Combined Valuation (AlphaSpread-like: DCF + Relative)
    combined_val = v.get_combined_intrinsic_value()
    if combined_val:
        results["valuation"]["combined"] = combined_val
    
    # Mistake Detection (Chapter 2)
    md = MistakeDetector(ticker)
    results["mistake_warnings"] = md.detect_mistakes()
    
    # ============================================================
    # 3. SECTOR SPECIFICS (Chapters 13-26)
    # ============================================================
    s = SectorFactory.get_strategy(ticker)
    results["sector_analysis"] = s.analyze()
    results["sector_chapter"] = SectorFactory.get_chapter_reference(ticker)
    
    # ============================================================
    # 4. DORSEY SCORECARD (Chapter 11)
    # ============================================================
    scorecard = DorseyScorecard(ticker)
    full_scorecard = scorecard.generate_scorecard()
    
    results["scorecard"] = {
        "total_score": full_scorecard.get("total_score", 0),
        "max_score": full_scorecard.get("max_score", 100),
        "percentage": full_scorecard.get("percentage", "0%"),
        "recommendation": full_scorecard.get("recommendation", "N/A"),
        "confidence": full_scorecard.get("confidence", "N/A"),
        "summary": full_scorecard.get("summary", ""),
        "scores": full_scorecard.get("scores", {}),
        "dorsey_five_rules_check": full_scorecard.get("dorsey_five_rules_check", {})
    }
    
    # ============================================================
    # 5. GRAHAM ANALYSIS (Intelligent Investor)
    # ============================================================
    try:
        graham = GrahamAnalyzer(ticker)
        graham_result = graham.analyze()
        
        results["graham_analysis"] = {
            "graham_number": graham_result.get("graham_number", {}),
            "intrinsic_value": graham_result.get("graham_intrinsic_value", {}),
            "margin_of_safety": graham_result.get("margin_of_safety", {}),
            "mr_market": graham_result.get("mr_market_indicator", {}),
            "principles_check": graham_result.get("graham_principles_checklist", {})
        }
        
        # Defensive Investor Screen
        defensive = DefensiveInvestorScreen(ticker)
        defensive_result = defensive.screen()
        
        results["graham_defensive_screen"] = {
            "passed": defensive_result.get("summary", {}).get("passed", 0),
            "total": defensive_result.get("summary", {}).get("total", 7),
            "verdict": defensive_result.get("summary", {}).get("verdict", "N/A"),
            "criteria": defensive_result.get("criteria", [])
        }
    except Exception as e:
        results["graham_analysis"] = {"error": str(e)}
        results["graham_defensive_screen"] = {"error": str(e)}
    
    return results


def run_quick_analysis(ticker):
    """
    Runs a quick analysis with just the scorecard summary.
    Useful for bulk screening.
    """
    scorecard = DorseyScorecard(ticker)
    return scorecard.get_quick_summary()


def run_graham_only(ticker):
    """
    Runs just the Graham analysis for value investors.
    """
    results = {}
    
    # Graham Analysis
    graham = GrahamAnalyzer(ticker)
    results["graham"] = graham.analyze()
    
    # Defensive Screen
    defensive = DefensiveInvestorScreen(ticker)
    results["defensive_screen"] = defensive.screen()
    
    return results


if __name__ == "__main__":
    # Test
    import json
    
    print("="*70)
    print("DORSEY RUNNER TEST")
    print("="*70)
    
    result = run_dorsey_analysis("TCS.NS")
    
    print(f"\nScorecard: {result['scorecard']['total_score']}/{result['scorecard']['max_score']}")
    print(f"Recommendation: {result['scorecard']['recommendation']}")
    print(f"Moat Rating: {result['moat_analysis'].get('moat_rating', 'N/A')}")
    print(f"Ten-Minute Test: {result['ten_minute_test'].get('overall_verdict', 'N/A')}")
    print(f"Health: {result['financial_health'].get('health_rating', 'N/A')}")
    print(f"Sector: {result['sector_chapter']}")
    
    if result.get('graham_analysis'):
        gn = result['graham_analysis'].get('graham_number', {})
        if gn.get('value'):
            print(f"Graham Number: ₹{gn['value']}")
    
    if result.get('mistake_warnings'):
        warnings = result['mistake_warnings'].get('mistake_warnings', [])
        print(f"Mistake Warnings: {len(warnings)}")
