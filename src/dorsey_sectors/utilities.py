"""
Utilities Sector Strategy - Chapter 26

Implements Pat Dorsey's analysis framework for utility companies.

Per Dorsey's Five Rules:
- Utilities are regulated businesses with limited upside
- Regulatory environment is the key determinant of returns
- Dividend sustainability is critical for income investors
- Conservative balance sheets are important
- Focus on core business vs diversification
"""

from src.dorsey_sectors.base import SectorStrategy


class UtilitiesStrategy(SectorStrategy):
    """
    Implements Chapter 26: Utilities.
    
    Per Pat Dorsey's Five Rules:
    - Utilities operate in regulated environments
    - Returns are largely determined by regulators, not management
    - Stable, but limited growth potential
    - Dividend yield is primary attraction
    - Beware of high yield with deteriorating fundamentals
    
    Key Metrics:
    - Regulatory Environment (qualitative - manual)
    - Rate Base Growth (earnings driver)
    - Dividend Yield and Sustainability
    - Payout Ratio
    - Debt/Capital (higher leverage acceptable)
    - ROE (vs allowed return)
    
    Utility Types:
    - Electric utilities
    - Gas utilities
    - Water utilities
    - Multi-utilities
    """
    
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Utilities"
        
    def analyze(self):
        insights = []
        moat_indicators = []
        red_flags = []
        
        # --- 1. Dividend Yield (Primary Attraction) ---
        div_yield = self.data_engine.info.get("dividendYield", 0)
        
        if div_yield:
            yield_pct = div_yield * 100
            
            if yield_pct > 6:
                yield_judgment = "Very High - Verify Sustainability"
                red_flags.append("Very high dividend yield may indicate stress or dividend at risk")
            elif yield_pct > 4:
                yield_judgment = "Attractive Income"
            elif yield_pct > 2:
                yield_judgment = "Moderate"
            else:
                yield_judgment = "Low for Utility"
                
            insights.append({
                "metric": "Dividend Yield",
                "value": f"{yield_pct:.1f}%",
                "judgment": yield_judgment,
                "context": "Per Dorsey: Utilities are bought for income. 3-5% yield is typical."
            })
        
        # --- 2. Dividend Payout Ratio ---
        ni = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Net Income", 0)
        dividends = abs(self.data_engine.get_financials_safe(
            self.data_engine.cashflow, "Common Stock Dividend Paid", 0) or 0)
        
        if ni and ni > 0 and dividends > 0:
            payout_ratio = (dividends / ni) * 100
            
            if payout_ratio < 60:
                payout_judgment = "Conservative - Room for Growth"
            elif payout_ratio < 80:
                payout_judgment = "Typical for Utility"
            elif payout_ratio < 100:
                payout_judgment = "High"
                red_flags.append("Payout ratio > 80% leaves little room for error")
            else:
                payout_judgment = "Unsustainable"
                red_flags.append("Paying more in dividends than earning - not sustainable")
                
            insights.append({
                "metric": "Payout Ratio",
                "value": f"{payout_ratio:.0f}%",
                "judgment": payout_judgment,
                "context": "Utilities typically pay 60-80% of earnings. Higher ratios are riskier."
            })
        
        # --- 3. Return on Equity (vs Allowed Return) ---
        equity = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Stockholders Equity", 0)
        roe = (ni / equity * 100) if ni and equity and equity > 0 else 0
        
        if roe > 0:
            if roe > 12:
                roe_judgment = "Above Allowed ROE"
                moat_indicators.append("ROE above typical allowed return suggests operational excellence")
            elif roe > 9:
                roe_judgment = "Typical Regulated Return"
            elif roe > 6:
                roe_judgment = "Below Average"
            else:
                roe_judgment = "Poor"
                red_flags.append("ROE significantly below allowed return - check for issues")
                
            insights.append({
                "metric": "Return on Equity",
                "value": f"{roe:.1f}%",
                "judgment": roe_judgment,
                "context": "Regulators typically allow 9-12% ROE. Actual ROE depends on efficiency."
            })
        
        # --- 4. Debt/Capital (Higher Acceptable for Utilities) ---
        total_debt = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Total Debt", 0)
        
        if total_debt and equity and equity > 0:
            debt_to_capital = (total_debt / (total_debt + equity)) * 100
            
            if debt_to_capital < 50:
                debt_judgment = "Conservative"
            elif debt_to_capital < 60:
                debt_judgment = "Typical for Utility"
            elif debt_to_capital < 70:
                debt_judgment = "High but May Be Acceptable"
            else:
                debt_judgment = "Very High"
                red_flags.append("Very high leverage even for a utility")
                
            insights.append({
                "metric": "Debt/Capital",
                "value": f"{debt_to_capital:.1f}%",
                "judgment": debt_judgment,
                "context": "Utilities can handle higher leverage (50-60%) due to stable cash flows."
            })
        
        # --- 5. Interest Coverage ---
        op_income = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Operating Income", 0)
        interest = abs(self.data_engine.get_financials_safe(
            self.data_engine.financials, "Interest Expense", 0) or 0)
        
        if op_income and interest and interest > 0:
            int_coverage = op_income / interest
            
            if int_coverage > 4:
                cov_judgment = "Strong"
            elif int_coverage > 2.5:
                cov_judgment = "Adequate"
            elif int_coverage > 1.5:
                cov_judgment = "Thin"
            else:
                cov_judgment = "Risky"
                red_flags.append("Low interest coverage - debt service may be strained")
                
            insights.append({
                "metric": "Interest Coverage",
                "value": f"{int_coverage:.1f}x",
                "judgment": cov_judgment,
                "context": "Utilities with predictable cash flows should cover interest 3x+."
            })
        
        # --- 6. Revenue Stability ---
        rev_curr = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Total Revenue", 0)
        rev_prev = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Total Revenue", 1)
        
        if rev_curr and rev_prev and rev_prev > 0:
            rev_growth = ((rev_curr - rev_prev) / rev_prev) * 100
            
            if abs(rev_growth) < 5:
                stability = "Stable"
                moat_indicators.append("Revenue stability typical of regulated utility")
            elif rev_growth > 5:
                stability = "Growing"
            else:
                stability = "Declining"
                
            insights.append({
                "metric": "Revenue Growth",
                "value": f"{rev_growth:.1f}%",
                "judgment": stability,
                "context": "Utilities grow slowly (2-4%) with rate base. Major swings are unusual."
            })
        
        # --- 7. Regulatory Environment Notes ---
        insights.append({
            "metric": "Regulatory Environment",
            "value": "Manual Assessment Required",
            "judgment": "⚠️ Key Driver",
            "context": "Per Dorsey: 'Regulation is key for utilities.' Stable, supportive regulators = better investment."
        })
        
        insights.append({
            "metric": "Rate Base Growth",
            "value": "Manual Verification Required",
            "judgment": "ℹ️ Growth Driver",
            "context": "Rate base growth of 2-4% annually drives earnings. Check capital investment plans."
        })
        
        # --- 8. Credit Rating Note ---
        insights.append({
            "metric": "Credit Rating",
            "value": "Check Externally",
            "judgment": "ℹ️ Access to Capital",
            "context": "Investment grade rating is essential for utilities to access cheap debt capital."
        })
        
        return {
            "sector": self.sector_name,
            "chapter_reference": "Chapter 26: Utilities",
            "insights": insights,
            "moat_indicators": moat_indicators if moat_indicators else None,
            "red_flags": red_flags if red_flags else None,
            "dorsey_wisdom": "Utilities can be traps for income-seeking investors. A high dividend yield is meaningless if the company can't sustain it. Watch payout ratios carefully.",
            "key_questions": [
                "Is the regulatory environment stable and supportive?",
                "Is the dividend sustainable at current payout ratios?",
                "What is the rate base growth trajectory?",
                "Has the company diversified into riskier non-regulated businesses?"
            ]
        }
