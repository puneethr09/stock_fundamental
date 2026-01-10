"""
Intelligent Investor - Core Analysis Module

Implements Benjamin Graham's core investment principles:
- Mr. Market concept (market sentiment indicator)
- Margin of Safety calculation
- Graham Number for quick valuation
- Graham Intrinsic Value formula
"""

from src.smart_data import SmartDataEngine
import math


class GrahamAnalyzer:
    """
    Implements Benjamin Graham's core investment principles from
    "The Intelligent Investor".
    
    Key Concepts:
    1. Mr. Market - View market as emotional partner, exploit irrationality
    2. Margin of Safety - Buy significantly below intrinsic value
    3. Graham Number - Quick valuation benchmark
    4. Intrinsic Value - Calculate true worth based on earnings and growth
    """
    
    def __init__(self, ticker):
        self.data_engine = SmartDataEngine(ticker)
        self.ticker = ticker
        
    def analyze(self):
        """
        Complete Graham analysis including all key metrics.
        """
        if not self.data_engine.has_data:
            return {"status": "NO DATA", "ticker": self.ticker}
        
        results = {
            "ticker": self.ticker,
            "company": self.data_engine.info.get("longName", self.ticker),
            "current_price": self.data_engine.info.get("currentPrice", 0),
            "graham_number": self.calculate_graham_number(),
            "graham_intrinsic_value": self.calculate_intrinsic_value(),
            "margin_of_safety": self.calculate_margin_of_safety(),
            "mr_market_indicator": self.get_mr_market_indicator(),
            "graham_principles_checklist": self.check_graham_principles()
        }
        
        return results
    
    def calculate_graham_number(self):
        """
        Graham Number = √(22.5 × EPS × BVPS)
        
        This is the maximum price a defensive investor should pay for a stock.
        The 22.5 comes from P/E of 15 × P/B of 1.5 = 22.5
        """
        eps = self.data_engine.info.get("trailingEps", 0)
        bvps = self.data_engine.info.get("bookValue", 0)
        
        if not eps or not bvps or eps <= 0 or bvps <= 0:
            return {
                "value": None,
                "formula": "√(22.5 × EPS × BVPS)",
                "inputs": {"EPS": eps, "BVPS": bvps},
                "note": "Cannot calculate - negative or missing EPS/BVPS"
            }
        
        graham_number = math.sqrt(22.5 * eps * bvps)
        current_price = self.data_engine.info.get("currentPrice", 0)
        
        upside = ((graham_number - current_price) / current_price * 100) if current_price > 0 else 0
        
        return {
            "value": round(graham_number, 2),
            "formula": "√(22.5 × EPS × BVPS)",
            "inputs": {"EPS": round(eps, 2), "BVPS": round(bvps, 2)},
            "current_price": current_price,
            "upside_potential": f"{upside:.1f}%",
            "verdict": "Undervalued" if upside > 20 else ("Fair" if upside > -10 else "Overvalued")
        }
    
    def calculate_intrinsic_value(self, growth_rate=None, aaa_bond_yield=7.0):
        """
        Graham Intrinsic Value Formula (Revised 1974):
        
        V = [EPS × (8.5 + 2g) × 4.4] / Y
        
        Where:
        - EPS = Trailing 12-month earnings per share
        - 8.5 = Base P/E for no-growth company
        - g = Expected 7-10 year growth rate (%)
        - 4.4 = Average AAA bond yield in 1960s
        - Y = Current AAA corporate bond yield (%)
        
        For India, we use RBI 10-year G-Sec yield as proxy (~7%)
        """
        eps = self.data_engine.info.get("trailingEps", 0)
        
        # Estimate growth rate from historical data if not provided
        if growth_rate is None:
            # Use revenue growth as proxy for expected growth
            rev_curr = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
            rev_prev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 2)
            
            if rev_prev and rev_prev > 0 and rev_curr:
                cagr = ((rev_curr / rev_prev) ** 0.5 - 1) * 100
                growth_rate = min(cagr, 15)  # Cap at 15% per Graham's conservatism
            else:
                growth_rate = 5  # Conservative default
        
        if not eps or eps <= 0:
            return {
                "value": None,
                "formula": "[EPS × (8.5 + 2g) × 4.4] / Y",
                "note": "Cannot calculate - negative or missing EPS"
            }
        
        # Original formula
        original_value = eps * (8.5 + 2 * growth_rate)
        
        # Revised formula (1974) with interest rate adjustment
        revised_value = (eps * (8.5 + 2 * growth_rate) * 4.4) / aaa_bond_yield
        
        current_price = self.data_engine.info.get("currentPrice", 0)
        margin = ((revised_value - current_price) / revised_value * 100) if revised_value > 0 else 0
        
        return {
            "original_formula_value": round(original_value, 2),
            "revised_formula_value": round(revised_value, 2),
            "formula": "[EPS × (8.5 + 2g) × 4.4] / Y",
            "inputs": {
                "EPS": round(eps, 2),
                "growth_rate_g": f"{growth_rate:.1f}%",
                "bond_yield_Y": f"{aaa_bond_yield:.1f}%"
            },
            "current_price": current_price,
            "margin_of_safety": f"{margin:.1f}%",
            "verdict": "Buy" if margin > 30 else ("Hold" if margin > 0 else "Avoid")
        }
    
    def calculate_margin_of_safety(self):
        """
        Margin of Safety = (Intrinsic Value - Current Price) / Intrinsic Value × 100
        
        Graham recommended buying only when there's a significant margin of safety
        (typically 30-50% below intrinsic value).
        """
        graham_num = self.calculate_graham_number()
        intrinsic = self.calculate_intrinsic_value()
        current_price = self.data_engine.info.get("currentPrice", 0)
        
        margins = {}
        
        if graham_num.get("value"):
            gn_margin = ((graham_num["value"] - current_price) / graham_num["value"] * 100) if graham_num["value"] > 0 else 0
            margins["graham_number_margin"] = {
                "value": f"{gn_margin:.1f}%",
                "assessment": "Strong" if gn_margin > 30 else ("Adequate" if gn_margin > 15 else ("Thin" if gn_margin > 0 else "Negative"))
            }
        
        if intrinsic.get("revised_formula_value"):
            iv_margin = ((intrinsic["revised_formula_value"] - current_price) / intrinsic["revised_formula_value"] * 100) if intrinsic["revised_formula_value"] > 0 else 0
            margins["intrinsic_value_margin"] = {
                "value": f"{iv_margin:.1f}%",
                "assessment": "Strong" if iv_margin > 30 else ("Adequate" if iv_margin > 15 else ("Thin" if iv_margin > 0 else "Negative"))
            }
        
        return {
            "principle": "Buy stocks with significant discount to intrinsic value as buffer against errors",
            "thresholds": {
                "strong": "> 30%",
                "adequate": "15-30%",
                "thin": "0-15%",
                "negative": "< 0%"
            },
            "current_margins": margins
        }
    
    def get_mr_market_indicator(self):
        """
        Mr. Market Indicator - Assesses if market is euphoric or depressed
        based on current P/E relative to historical averages.
        
        Graham's allegory: Mr. Market is an emotional business partner who
        offers to buy/sell shares at wildly fluctuating prices. Use his
        moods as opportunities, not guidance.
        """
        current_pe = self.data_engine.info.get("trailingPE", 0)
        forward_pe = self.data_engine.info.get("forwardPE", 0)
        
        # Get 5-year average P/E as benchmark (if available)
        five_year_avg_pe = self.data_engine.info.get("fiveYearAvgDividendYield", None)
        
        # Industry P/E comparison
        sector_pe = self.data_engine.info.get("sectorPE", 15)  # Default to 15
        
        if not current_pe or current_pe <= 0:
            return {
                "indicator": "Cannot Assess",
                "current_pe": current_pe,
                "note": "P/E not available or negative earnings"
            }
        
        # Simple mood assessment based on absolute P/E levels
        if current_pe < 10:
            mood = "Pessimistic"
            opportunity = "Mr. Market is offering bargains - consider buying"
        elif current_pe < 15:
            mood = "Cautious"
            opportunity = "Reasonable valuations - selective buying"
        elif current_pe < 25:
            mood = "Neutral to Optimistic"
            opportunity = "Fair valuations - hold or trim"
        else:
            mood = "Euphoric"
            opportunity = "Mr. Market is overpaying - consider selling or stay away"
        
        return {
            "mr_market_mood": mood,
            "current_pe": round(current_pe, 1),
            "forward_pe": round(forward_pe, 1) if forward_pe else None,
            "opportunity": opportunity,
            "graham_wisdom": "Mr. Market is there to serve you, not guide you. Exploit his emotional extremes."
        }
    
    def check_graham_principles(self):
        """
        Quick checklist of Graham's core investment principles.
        """
        principles = []
        
        # 1. Adequate Size
        market_cap = self.data_engine.info.get("marketCap", 0)
        min_cap = 500_00_00_000  # ₹500 Cr for India
        principles.append({
            "principle": "Adequate Size",
            "passed": market_cap > min_cap if market_cap else False,
            "value": f"₹{market_cap/10_000_000:,.0f} Cr" if market_cap else "N/A",
            "requirement": "Large enough to be liquid and stable"
        })
        
        # 2. Strong Financial Condition
        current_ratio = self.data_engine.info.get("currentRatio", 0)
        principles.append({
            "principle": "Strong Financial Condition",
            "passed": current_ratio >= 2.0 if current_ratio else False,
            "value": f"{current_ratio:.2f}x" if current_ratio else "N/A",
            "requirement": "Current ratio ≥ 2.0"
        })
        
        # 3. Earnings Stability
        has_positive_earnings = True  # Simplified check
        ni = self.data_engine.get_financials_safe(self.data_engine.financials, "Net Income", 0)
        has_positive_earnings = ni and ni > 0
        principles.append({
            "principle": "Earnings Stability",
            "passed": has_positive_earnings,
            "value": "Positive" if has_positive_earnings else "Loss-making",
            "requirement": "Some earnings in each of past 10 years"
        })
        
        # 4. Dividend Record
        dividend_rate = self.data_engine.info.get("dividendRate", 0)
        principles.append({
            "principle": "Dividend Record",
            "passed": dividend_rate and dividend_rate > 0,
            "value": f"₹{dividend_rate:.2f}" if dividend_rate else "None",
            "requirement": "Uninterrupted dividends for 20 years (relaxed for India)"
        })
        
        # 5. Moderate P/E
        pe = self.data_engine.info.get("trailingPE", 0)
        principles.append({
            "principle": "Moderate P/E Ratio",
            "passed": pe and pe < 15,
            "value": f"{pe:.1f}x" if pe else "N/A",
            "requirement": "P/E < 15 (based on 3-year average earnings)"
        })
        
        # 6. Moderate P/B
        pb = self.data_engine.info.get("priceToBook", 0)
        principles.append({
            "principle": "Moderate P/B Ratio",
            "passed": pb and pb < 1.5,
            "value": f"{pb:.2f}x" if pb else "N/A",
            "requirement": "P/B < 1.5"
        })
        
        # 7. Combined P/E × P/B < 22.5
        if pe and pb:
            combined = pe * pb
            principles.append({
                "principle": "P/E × P/B < 22.5",
                "passed": combined < 22.5,
                "value": f"{combined:.1f}",
                "requirement": "Combined ratio < 22.5 for defensive investors"
            })
        
        passed_count = sum(1 for p in principles if p.get("passed"))
        total_count = len(principles)
        
        return {
            "principles": principles,
            "passed": passed_count,
            "total": total_count,
            "assessment": "Strong Graham Stock" if passed_count >= 5 else ("Possible Value" if passed_count >= 3 else "Doesn't Meet Graham Criteria")
        }


if __name__ == "__main__":
    # Test
    test_tickers = ["TCS.NS", "HDFCBANK.NS", "ITC.NS"]
    for ticker in test_tickers:
        print(f"\n{'='*60}")
        print(f"Graham Analysis: {ticker}")
        print('='*60)
        g = GrahamAnalyzer(ticker)
        result = g.analyze()
        
        print(f"\nGraham Number: {result['graham_number']}")
        print(f"\nIntrinsic Value: {result['graham_intrinsic_value']}")
        print(f"\nMr. Market: {result['mr_market_indicator']}")
        print(f"\nPrinciples Check: {result['graham_principles_checklist']['assessment']}")
        print(f"  Passed: {result['graham_principles_checklist']['passed']}/{result['graham_principles_checklist']['total']}")
