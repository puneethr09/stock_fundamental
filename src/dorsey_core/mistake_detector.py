"""
Mistake Detector - Chapter 2: Seven Mistakes to Avoid

Implements detection and warnings for the seven common investment mistakes
outlined in Pat Dorsey's Chapter 2.

The Seven Mistakes:
1. Swinging for the fences - Seeking home runs instead of base hits
2. "It's different this time" - Believing the current time is unique
3. Falling in love with products - Letting product love blind analysis
4. Panicking when the market down - Selling at worst possible time
5. Trying to time the market - In/out trading destroys returns
6. Ignoring valuation - Buying good companies at bad prices
7. Relying only on earnings - Ignoring cash flow quality
"""

from src.smart_data import SmartDataEngine


class MistakeDetector:
    """
    Detects when an investor might be making one of Dorsey's seven mistakes.
    
    Provides warnings and educational guidance to help investors avoid
    common pitfalls.
    """
    
    def __init__(self, ticker):
        self.data_engine = SmartDataEngine(ticker)
        self.ticker = ticker
        
    def detect_mistakes(self):
        """
        Analyze the stock for potential mistake indicators.
        Returns warnings and educational tips.
        """
        if not self.data_engine.has_data:
            return {"status": "NO DATA", "ticker": self.ticker}
        
        warnings = []
        educational_tips = []
        
        # ============================================================
        # MISTAKE 6: IGNORING VALUATION
        # ============================================================
        # Detectable: High P/E, High P/B without moat justification
        
        pe = self.data_engine.info.get("trailingPE", 0)
        pb = self.data_engine.info.get("priceToBook", 0)
        
        if pe and pe > 30:
            warnings.append({
                "mistake": "6. Ignoring Valuation",
                "indicator": f"P/E ratio of {pe:.1f}x is very high",
                "risk": "Even great companies can be bad investments at high prices",
                "dorsey_says": "The more you pay for a stock, the lower your returns. A wonderful company is not always a wonderful investment."
            })
        
        if pb and pb > 5:
            warnings.append({
                "mistake": "6. Ignoring Valuation",
                "indicator": f"P/B ratio of {pb:.1f}x is premium",
                "risk": "High book value multiples require exceptional growth to justify",
                "dorsey_says": "Valuation always matters. Don't confuse a good company with a good investment."
            })
        
        # Check combined P/E × P/B (Graham's 22.5 rule)
        if pe and pb and pe * pb > 50:
            warnings.append({
                "mistake": "6. Ignoring Valuation",
                "indicator": f"P/E × P/B = {pe*pb:.1f} (Graham limit is 22.5)",
                "risk": "Significantly exceeds Graham's defensive investor limit",
                "dorsey_says": "Margin of safety is essential. Don't overpay just because a company is growing."
            })
        
        # ============================================================
        # MISTAKE 7: RELYING ONLY ON EARNINGS
        # ============================================================
        # Detectable: Earnings growing but cash flow declining
        
        ni_curr = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Net Income", 0)
        ni_prev = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Net Income", 1)
        cfo_curr = self.data_engine.get_financials_safe(
            self.data_engine.cashflow, "Operating Cash Flow", 0)
        cfo_prev = self.data_engine.get_financials_safe(
            self.data_engine.cashflow, "Operating Cash Flow", 1)
        
        if ni_curr and ni_prev and ni_prev > 0:
            ni_growth = ((ni_curr - ni_prev) / ni_prev) * 100
            
            if cfo_curr and cfo_prev and cfo_prev > 0:
                cfo_growth = ((cfo_curr - cfo_prev) / cfo_prev) * 100
                
                # Warning if earnings up but cash flow down
                if ni_growth > 5 and cfo_growth < -5:
                    warnings.append({
                        "mistake": "7. Relying Only on Earnings",
                        "indicator": f"Earnings grew {ni_growth:.1f}% but cash flow declined {cfo_growth:.1f}%",
                        "risk": "Earnings quality may be deteriorating",
                        "dorsey_says": "Cash flow is much harder to manipulate than earnings. Always verify earnings with cash flow."
                    })
        
        # Check if CFO < Net Income consistently
        if ni_curr and cfo_curr and ni_curr > 0:
            cfo_to_ni = cfo_curr / ni_curr
            if cfo_to_ni < 0.7:
                warnings.append({
                    "mistake": "7. Relying Only on Earnings",
                    "indicator": f"Cash flow is only {cfo_to_ni*100:.0f}% of net income",
                    "risk": "Low cash conversion may indicate accrual-heavy earnings",
                    "dorsey_says": "Earnings don't pay the bills - cash does. Be wary when cash flow lags earnings."
                })
        
        # ============================================================
        # MISTAKE 1: SWINGING FOR THE FENCES
        # ============================================================
        # Detectable: High beta, high volatility, small cap with no profits
        
        beta = self.data_engine.info.get("beta", 1)
        market_cap = self.data_engine.info.get("marketCap", 0)
        has_profit = ni_curr and ni_curr > 0
        
        if beta and beta > 2:
            warnings.append({
                "mistake": "1. Swinging for the Fences",
                "indicator": f"Beta of {beta:.2f} indicates high volatility",
                "risk": "High-beta stocks often underperform on risk-adjusted basis",
                "dorsey_says": "Base hits win games - you don't need to find the next 10-bagger. Focus on solid, 15%+ annual returns."
            })
        
        if market_cap and market_cap < 100_00_00_000 and not has_profit:  # < ₹100 Cr
            warnings.append({
                "mistake": "1. Swinging for the Fences",
                "indicator": "Small cap with no profits",
                "risk": "Speculative bet rather than investment",
                "dorsey_says": "Seeking big wins often leads to big losses. Stick to your circle of competence."
            })
        
        # ============================================================
        # EDUCATIONAL TIPS (Always Include)
        # ============================================================
        
        educational_tips.append({
            "mistake": "2. 'It's Different This Time'",
            "tip": "Every market cycle has people saying fundamentals don't matter anymore. They always do eventually.",
            "application": "Check if current valuations are justified by historical standards, not just recent trends."
        })
        
        educational_tips.append({
            "mistake": "3. Falling in Love with Products",
            "tip": "Being a happy customer doesn't mean the company is a good investment.",
            "application": "Analyze the business model, not just the product experience."
        })
        
        educational_tips.append({
            "mistake": "4. Panicking When Market Down",
            "tip": "Market downturns are sales for long-term investors.",
            "application": "Have a watchlist of quality companies ready to buy during corrections."
        })
        
        educational_tips.append({
            "mistake": "5. Trying to Time the Market",
            "tip": "Time in the market beats timing the market.",
            "application": "Focus on buying good companies at fair prices, not predicting market moves."
        })
        
        # ============================================================
        # OVERALL ASSESSMENT
        # ============================================================
        
        risk_level = "LOW"
        if len(warnings) >= 3:
            risk_level = "HIGH"
        elif len(warnings) >= 1:
            risk_level = "MODERATE"
        
        return {
            "ticker": self.ticker,
            "company": self.data_engine.info.get("longName", self.ticker),
            "mistake_warnings": warnings,
            "educational_tips": educational_tips,
            "risk_level": risk_level,
            "warning_count": len(warnings),
            "dorsey_wisdom": "The best way to avoid mistakes is to have a systematic investment process and stick to it."
        }


if __name__ == "__main__":
    # Test
    test_tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
    for ticker in test_tickers:
        print(f"\n{'='*60}")
        print(f"Mistake Detection: {ticker}")
        print('='*60)
        detector = MistakeDetector(ticker)
        result = detector.detect_mistakes()
        
        print(f"Risk Level: {result['risk_level']}")
        print(f"Warnings: {result['warning_count']}")
        for warning in result['mistake_warnings']:
            print(f"  ⚠️ {warning['mistake']}: {warning['indicator']}")
