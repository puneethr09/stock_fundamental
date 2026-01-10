"""
Telecom Sector Strategy - Chapter 22

Implements Pat Dorsey's analysis framework for telecommunications companies.

Per Dorsey's Five Rules:
- Telecom is capital intensive with high fixed costs
- Network effects possible in mobile/wireless
- Leverage is typically high due to infrastructure needs
- Focus on ARPU, churn, and CapEx intensity
"""

from src.dorsey_sectors.base import SectorStrategy


class TelecomStrategy(SectorStrategy):
    """
    Implements Chapter 22: Telecom.
    
    Per Pat Dorsey's Five Rules:
    - Telecom requires massive capital investment (network infrastructure)
    - High fixed costs mean scale is critical
    - Wireless has some network effects (calling friends on same network)
    - Competition has intensified, eroding pricing power
    
    Key Metrics:
    - CapEx Intensity (% of revenue spent on network)
    - EBITDA Margin (operating efficiency)
    - Debt/EBITDA (leverage relative to cash flow)
    - ARPU trend (average revenue per user - proxy with revenue growth)
    - Churn rate (customer retention - qualitative)
    """
    
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Telecom"
        
    def analyze(self):
        insights = []
        moat_indicators = []
        red_flags = []
        
        # --- 1. CapEx Intensity (Network Investment) ---
        capex = abs(self.data_engine.get_financials_safe(
            self.data_engine.cashflow, "Capital Expenditure", 0) or 0)
        rev = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Total Revenue", 0)
        
        if rev and rev > 0 and capex > 0:
            capex_intensity = (capex / rev) * 100
            
            if capex_intensity > 25:
                capex_judgment = "Very High - Heavy Investment Phase"
            elif capex_intensity > 15:
                capex_judgment = "Typical for Telecom"
            elif capex_intensity > 10:
                capex_judgment = "Moderate"
            else:
                capex_judgment = "Low - May Be Underinvesting"
                red_flags.append("Low CapEx may indicate network underinvestment")
                
            insights.append({
                "metric": "CapEx as % of Revenue",
                "value": f"{capex_intensity:.1f}%",
                "judgment": capex_judgment,
                "context": "Per Dorsey: Telecoms spend 15-20% of revenue just to maintain networks."
            })
        
        # --- 2. EBITDA Margin (Operating Efficiency) ---
        op_income = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Operating Income", 0)
        depreciation = self.data_engine.get_financials_safe(
            self.data_engine.cashflow, "Depreciation And Amortization", 0) or 0
        
        if op_income and rev and rev > 0:
            # EBITDA = Operating Income + D&A (approximate)
            ebitda = op_income + depreciation
            ebitda_margin = (ebitda / rev) * 100
            
            if ebitda_margin > 40:
                ebitda_judgment = "Excellent"
                moat_indicators.append("High EBITDA margin suggests scale advantages")
            elif ebitda_margin > 30:
                ebitda_judgment = "Good"
            elif ebitda_margin > 20:
                ebitda_judgment = "Average"
            else:
                ebitda_judgment = "Weak"
                red_flags.append("Low EBITDA margin - may lack scale or face intense competition")
                
            insights.append({
                "metric": "EBITDA Margin",
                "value": f"{ebitda_margin:.1f}%",
                "judgment": ebitda_judgment,
                "context": "Strong telecoms achieve 35%+ EBITDA margins from scale."
            })
            
            # --- 3. Debt/EBITDA (Critical for Telecom) ---
            total_debt = self.data_engine.get_financials_safe(
                self.data_engine.balance_sheet, "Total Debt", 0)
            
            if total_debt and ebitda and ebitda > 0:
                debt_ebitda = total_debt / ebitda
                
                if debt_ebitda < 2:
                    debt_judgment = "Conservative"
                elif debt_ebitda < 3:
                    debt_judgment = "Moderate"
                elif debt_ebitda < 4:
                    debt_judgment = "High"
                else:
                    debt_judgment = "Very High - Watch Carefully"
                    red_flags.append("Debt/EBITDA > 4x is concerning for capital-intensive telecom")
                    
                insights.append({
                    "metric": "Debt/EBITDA",
                    "value": f"{debt_ebitda:.1f}x",
                    "judgment": debt_judgment,
                    "context": "Telecom debt is typically 2-3x EBITDA. Higher requires careful scrutiny."
                })
        
        # --- 4. Revenue Growth (ARPU Proxy) ---
        rev_prev = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Total Revenue", 1)
        
        if rev and rev_prev and rev_prev > 0:
            rev_growth = ((rev - rev_prev) / rev_prev) * 100
            
            if rev_growth > 10:
                growth_judgment = "Strong"
            elif rev_growth > 3:
                growth_judgment = "Healthy"
            elif rev_growth > 0:
                growth_judgment = "Slow"
            else:
                growth_judgment = "Declining"
                red_flags.append("Declining revenue may indicate competitive pressure or churn")
                
            insights.append({
                "metric": "Revenue Growth (ARPU Proxy)",
                "value": f"{rev_growth:.1f}%",
                "judgment": growth_judgment,
                "context": "Revenue growth driven by subscriber additions and ARPU. Both matter."
            })
        
        # --- 5. Interest Coverage ---
        interest = abs(self.data_engine.get_financials_safe(
            self.data_engine.financials, "Interest Expense", 0) or 0)
        
        if op_income and interest and interest > 0:
            int_coverage = op_income / interest
            
            if int_coverage > 5:
                cov_judgment = "Strong"
            elif int_coverage > 3:
                cov_judgment = "Adequate"
            elif int_coverage > 2:
                cov_judgment = "Thin"
            else:
                cov_judgment = "Risky"
                red_flags.append("Low interest coverage - debt service may strain cash flows")
                
            insights.append({
                "metric": "Interest Coverage",
                "value": f"{int_coverage:.1f}x",
                "judgment": cov_judgment,
                "context": "Telecoms should cover interest at least 3x given high leverage."
            })
        
        # --- 6. Free Cash Flow Yield ---
        cfo = self.data_engine.get_financials_safe(
            self.data_engine.cashflow, "Operating Cash Flow", 0)
        market_cap = self.data_engine.info.get("marketCap", 0)
        
        if cfo and capex and market_cap and market_cap > 0:
            fcf = cfo - capex
            fcf_yield = (fcf / market_cap) * 100
            
            insights.append({
                "metric": "FCF Yield",
                "value": f"{fcf_yield:.1f}%",
                "judgment": "Attractive" if fcf_yield > 5 else ("Fair" if fcf_yield > 2 else "Low"),
                "context": "Positive FCF yield indicates capacity for dividends and debt paydown."
            })
        
        # --- 7. Subscriber Metrics Guidance ---
        insights.append({
            "metric": "Subscriber Metrics",
            "value": "Manual Verification Required",
            "judgment": "ℹ️ Key Growth Driver",
            "context": "Check ARPU trend, subscriber churn (<2% monthly is good), and active user growth."
        })
        
        return {
            "sector": self.sector_name,
            "chapter_reference": "Chapter 22: Telecom",
            "insights": insights,
            "moat_indicators": moat_indicators if moat_indicators else None,
            "red_flags": red_flags if red_flags else None,
            "dorsey_wisdom": "Cable and telephone companies have enjoyed local monopolies in the past, but competition from satellite and new technologies has intensified. Focus on sustainable competitive advantages.",
            "key_questions": [
                "What is the ARPU trend (growing or declining)?",
                "What is the subscriber churn rate?",
                "Is spectrum position advantageous?",
                "How competitive is the market (pricing pressure)?"
            ]
        }
