"""
Dorsey Scorecard - Chapter 11: Putting It All Together

Combines all analysis modules into a comprehensive investment scorecard
based on Pat Dorsey's Five Rules framework.

This is the culmination of Dorsey's analysis framework, integrating:
- Ten-Minute Test (Chapter 12)
- Moat Analysis (Chapter 3)
- Financial Health (Chapters 5-8)
- Valuation (Chapters 9-10)
- Sector-Specific Analysis (Chapters 13-26)
"""

from src.smart_data import SmartDataEngine
from src.ten_minute_test import TenMinuteTest
from src.dorsey_core.moat import MoatAnalyzer
from src.dorsey_core.financials import FinancialsAnalyzer
from src.dorsey_core.valuation import ValuationAnalyzer
from src.dorsey_sectors.factory import SectorFactory


class DorseyScorecard:
    """
    Complete Dorsey Analysis Scorecard - Chapter 11: Putting It All Together.
    
    Combines all modules into a single investment decision framework:
    1. Ten-Minute Test: Quick quality filter
    2. Moat Analysis: Sustainable competitive advantage
    3. Financial Health: Balance sheet and red flags
    4. Valuation: Price vs intrinsic value
    5. Sector Analysis: Industry-specific considerations
    
    Final Output: BUY / HOLD / AVOID recommendation with confidence level
    """
    
    def __init__(self, ticker):
        self.ticker = ticker
        self.data_engine = SmartDataEngine(ticker)
        
    def generate_scorecard(self):
        """
        Generate comprehensive Dorsey scorecard.
        """
        if not self.data_engine.has_data:
            return {
                "ticker": self.ticker,
                "status": "NO DATA",
                "recommendation": "CANNOT ANALYZE"
            }
        
        # Get basic info
        company_name = self.data_engine.info.get("longName", self.ticker)
        current_price = self.data_engine.info.get("currentPrice", 0)
        sector = self.data_engine.info.get("sector", "Unknown")
        
        # ============================================================
        # 1. TEN-MINUTE TEST
        # ============================================================
        ten_min = TenMinuteTest(self.ticker)
        ten_min_result = ten_min.run_test()
        
        # ============================================================
        # 2. MOAT ANALYSIS
        # ============================================================
        moat_analyzer = MoatAnalyzer(self.ticker)
        moat_result = moat_analyzer.analyze_moat()
        
        # ============================================================
        # 3. FINANCIAL HEALTH
        # ============================================================
        financials = FinancialsAnalyzer(self.ticker)
        health_result = financials.analyze_health()
        
        # ============================================================
        # 4. VALUATION
        # ============================================================
        valuation = ValuationAnalyzer(self.ticker)
        valuation_result = valuation.get_valuation_scenarios()
        
        # Calculate valuation vs price
        valuation_assessment = "Unknown"
        margin_of_safety = 0
        
        if valuation_result and "scenarios" in valuation_result:
            base_value = valuation_result["scenarios"].get("Base", {}).get("value", 0)
            if base_value and current_price:
                margin_of_safety = ((base_value - current_price) / base_value) * 100
                
                if margin_of_safety > 30:
                    valuation_assessment = "Undervalued"
                elif margin_of_safety > 10:
                    valuation_assessment = "Fairly Valued"
                elif margin_of_safety > -10:
                    valuation_assessment = "Fully Valued"
                else:
                    valuation_assessment = "Overvalued"
        
        # ============================================================
        # 5. SECTOR ANALYSIS
        # ============================================================
        sector_strategy = SectorFactory.get_strategy(self.ticker)
        sector_result = sector_strategy.analyze()
        sector_chapter = SectorFactory.get_chapter_reference(self.ticker)
        
        # ============================================================
        # COMPOSITE SCORING
        # ============================================================
        total_score = 0
        max_score = 100
        
        # Ten-Minute Test (25 points max)
        ten_min_score = (ten_min_result.get("score", 0) / ten_min_result.get("max_score", 8)) * 25
        total_score += ten_min_score
        
        # Moat Rating (30 points max)
        moat_scores = {
            "Wide Moat": 30,
            "Narrow Moat": 20,
            "Possible Moat": 10,
            "No Moat": 0
        }
        moat_score = moat_scores.get(moat_result.get("moat_rating", "No Moat"), 0)
        total_score += moat_score
        
        # Financial Health (20 points max)
        health_scores = {
            "ROBUST": 20,
            "MODERATE": 12,
            "WEAK": 6,
            "RISKY": 0
        }
        health_score = health_scores.get(health_result.get("health_rating", "WEAK"), 6)
        
        # Deduct for red flags
        red_flag_count = len(health_result.get("red_flags", []))
        health_score = max(0, health_score - (red_flag_count * 5))
        total_score += health_score
        
        # Valuation (25 points max)
        valuation_scores = {
            "Undervalued": 25,
            "Fairly Valued": 15,
            "Fully Valued": 5,
            "Overvalued": 0,
            "Unknown": 10
        }
        val_score = valuation_scores.get(valuation_assessment, 10)
        total_score += val_score
        
        # ============================================================
        # FINAL RECOMMENDATION
        # ============================================================
        if total_score >= 75:
            recommendation = "STRONG BUY"
            confidence = "HIGH"
        elif total_score >= 60:
            recommendation = "BUY"
            confidence = "MODERATE-HIGH"
        elif total_score >= 45:
            recommendation = "HOLD / WATCHLIST"
            confidence = "MODERATE"
        elif total_score >= 30:
            recommendation = "AVOID"
            confidence = "MODERATE"
        else:
            recommendation = "STRONG AVOID"
            confidence = "HIGH"
        
        # ============================================================
        # BUILD SCORECARD
        # ============================================================
        scorecard = {
            "ticker": self.ticker,
            "company": company_name,
            "sector": sector,
            "sector_chapter": sector_chapter,
            "current_price": current_price,
            
            "scores": {
                "ten_minute_test": {
                    "score": round(ten_min_score, 1),
                    "max": 25,
                    "verdict": ten_min_result.get("overall_verdict", "UNKNOWN")
                },
                "moat": {
                    "score": moat_score,
                    "max": 30,
                    "rating": moat_result.get("moat_rating", "Unknown")
                },
                "financial_health": {
                    "score": health_score,
                    "max": 20,
                    "rating": health_result.get("health_rating", "Unknown"),
                    "red_flags": red_flag_count
                },
                "valuation": {
                    "score": val_score,
                    "max": 25,
                    "assessment": valuation_assessment,
                    "margin_of_safety": f"{margin_of_safety:.1f}%"
                }
            },
            
            "total_score": round(total_score, 1),
            "max_score": max_score,
            "percentage": f"{(total_score/max_score)*100:.0f}%",
            
            "recommendation": recommendation,
            "confidence": confidence,
            
            "dorsey_five_rules_check": {
                "1_do_homework": ten_min_result.get("passed", False),
                "2_find_moats": moat_result.get("moat_rating", "") in ["Wide Moat", "Narrow Moat"],
                "3_margin_of_safety": margin_of_safety > 20,
                "4_hold_long_term": moat_result.get("moat_rating", "") == "Wide Moat",
                "5_know_when_to_sell": len(health_result.get("red_flags", [])) == 0
            },
            
            "summary": self._generate_summary(
                ten_min_result, moat_result, health_result, 
                valuation_assessment, margin_of_safety, recommendation
            ),
            
            "key_risks": health_result.get("red_flags", []) + health_result.get("amber_flags", []),
            
            "detailed_results": {
                "ten_minute_test": ten_min_result,
                "moat_analysis": moat_result,
                "financial_health": health_result,
                "valuation": valuation_result,
                "sector_analysis": sector_result
            }
        }
        
        return scorecard
    
    def _generate_summary(self, ten_min, moat, health, valuation_assess, mos, recommendation):
        """Generate a human-readable summary."""
        
        summary_parts = []
        
        # Ten-minute test
        if ten_min.get("passed"):
            summary_parts.append("Passes basic quality screens")
        else:
            summary_parts.append("Some quality concerns in initial screen")
        
        # Moat
        moat_rating = moat.get("moat_rating", "Unknown")
        if "Wide" in moat_rating:
            summary_parts.append("Has sustainable competitive advantages")
        elif "Narrow" in moat_rating:
            summary_parts.append("Has some competitive advantages")
        else:
            summary_parts.append("Limited competitive moat")
        
        # Health
        health_rating = health.get("health_rating", "Unknown")
        if health_rating == "ROBUST":
            summary_parts.append("Strong financial health")
        elif health_rating == "RISKY":
            summary_parts.append("Financial health concerns present")
        
        # Valuation
        summary_parts.append(f"{valuation_assess} at current price")
        
        if mos > 20:
            summary_parts.append(f"with {mos:.0f}% margin of safety")
        
        return ". ".join(summary_parts) + "."
    
    def get_quick_summary(self):
        """
        Get a brief summary without full analysis details.
        """
        scorecard = self.generate_scorecard()
        
        return {
            "ticker": scorecard["ticker"],
            "company": scorecard["company"],
            "score": f"{scorecard['total_score']}/{scorecard['max_score']}",
            "recommendation": scorecard["recommendation"],
            "moat": scorecard["scores"]["moat"]["rating"],
            "valuation": scorecard["scores"]["valuation"]["assessment"],
            "health": scorecard["scores"]["financial_health"]["rating"],
            "summary": scorecard["summary"]
        }


if __name__ == "__main__":
    # Test
    test_tickers = ["TCS.NS", "HDFCBANK.NS", "HINDUNILVR.NS"]
    
    for ticker in test_tickers:
        print(f"\n{'='*70}")
        print(f"DORSEY SCORECARD: {ticker}")
        print('='*70)
        
        scorecard = DorseyScorecard(ticker)
        result = scorecard.get_quick_summary()
        
        print(f"\nCompany: {result['company']}")
        print(f"Score: {result['score']}")
        print(f"Recommendation: {result['recommendation']}")
        print(f"\nMoat: {result['moat']}")
        print(f"Valuation: {result['valuation']}")
        print(f"Health: {result['health']}")
        print(f"\nSummary: {result['summary']}")
