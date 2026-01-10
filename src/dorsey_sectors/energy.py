"""
Energy Sector Strategy - Chapter 25

Implements Pat Dorsey's analysis framework for energy companies.

Per Dorsey's Five Rules:
- Energy is cyclical - profitability depends on commodity prices
- Reserve replacement is critical for E&P companies
- Low-cost producers survive downturns
- Strong balance sheets essential for commodity cycles
"""

from src.dorsey_sectors.base import SectorStrategy


class EnergyStrategy(SectorStrategy):
    """
    Implements Chapter 25: Energy.
    
    Per Pat Dorsey's Five Rules:
    - Energy profitability depends heavily on commodity prices
    - E&P companies must replace reserves to maintain production
    - Finding costs determine profitability
    - Strong balance sheets help survive commodity cycles
    - Integrated majors offer diversification
    
    Key Metrics:
    - Reserve Replacement (manual - production sustainability)
    - Finding & Development Costs (manual - profitability)
    - Production Growth
    - Debt/Capital (cycle survival)
    - Cash Flow at Low Prices (stress test)
    - Dividend Sustainability
    
    Sub-sectors:
    - E&P (Exploration & Production) - highest risk, reserve-focused
    - Integrated Majors - diversified, more stable
    - Refining - spread-based, different dynamics
    - Services - contract-driven, cyclical
    """
    
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Energy"
        
    def analyze(self):
        insights = []
        moat_indicators = []
        red_flags = []
        
        # --- 1. Revenue Stability (Commodity Exposure) ---
        rev_curr = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Total Revenue", 0)
        rev_prev = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Total Revenue", 1)
        rev_old = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Total Revenue", 2)
        
        if rev_curr and rev_prev and rev_old and rev_old > 0:
            rev_growth = ((rev_curr - rev_prev) / rev_prev) * 100 if rev_prev > 0 else 0
            rev_volatility = abs(rev_curr - rev_old) / rev_old * 100
            
            insights.append({
                "metric": "Revenue Growth (YoY)",
                "value": f"{rev_growth:.1f}%",
                "judgment": "Growing" if rev_growth > 5 else ("Stable" if rev_growth > -5 else "Declining"),
                "context": "Energy revenue is volatile with commodity prices. Focus on cash flow not just revenue."
            })
            
            if rev_volatility > 30:
                red_flags.append("High revenue volatility (>30%) - typical of commodity exposure")
        
        # --- 2. Operating Margin (Cost Discipline) ---
        op_income = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Operating Income", 0)
        
        if op_income and rev_curr and rev_curr > 0:
            op_margin = (op_income / rev_curr) * 100
            
            if op_margin > 25:
                op_judgment = "Excellent"
                moat_indicators.append("High operating margin suggests low-cost position")
            elif op_margin > 15:
                op_judgment = "Good"
            elif op_margin > 5:
                op_judgment = "Thin"
            else:
                op_judgment = "Weak"
                red_flags.append("Low operating margin - may struggle in price downturns")
                
            insights.append({
                "metric": "Operating Margin",
                "value": f"{op_margin:.1f}%",
                "judgment": op_judgment,
                "context": "Per Dorsey: Low-cost producers with high margins survive commodity cycles."
            })
        
        # --- 3. Debt to Capital (Cycle Survival) ---
        total_debt = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Total Debt", 0)
        total_equity = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Stockholders Equity", 0)
        
        if total_debt and total_equity and total_equity > 0:
            debt_to_capital = (total_debt / (total_debt + total_equity)) * 100
            
            if debt_to_capital < 30:
                debt_judgment = "Conservative"
                moat_indicators.append("Strong balance sheet can survive commodity downturns")
            elif debt_to_capital < 45:
                debt_judgment = "Moderate"
            else:
                debt_judgment = "High - Cycle Risk"
                red_flags.append("High leverage in cyclical industry is dangerous")
                
            insights.append({
                "metric": "Debt to Capital",
                "value": f"{debt_to_capital:.1f}%",
                "judgment": debt_judgment,
                "context": "Per Dorsey: Energy companies need <40% debt to survive commodity cycles."
            })
        
        # --- 4. Free Cash Flow Generation ---
        cfo = self.data_engine.get_financials_safe(
            self.data_engine.cashflow, "Operating Cash Flow", 0)
        capex = abs(self.data_engine.get_financials_safe(
            self.data_engine.cashflow, "Capital Expenditure", 0) or 0)
        
        if cfo:
            fcf = cfo - capex
            
            if fcf > 0:
                fcf_judgment = "Positive"
            else:
                fcf_judgment = "Negative"
                red_flags.append("Negative FCF - requires external funding or asset sales")
            
            if rev_curr and rev_curr > 0:
                fcf_margin = (fcf / rev_curr) * 100
                insights.append({
                    "metric": "FCF Margin",
                    "value": f"{fcf_margin:.1f}%",
                    "judgment": fcf_judgment,
                    "context": "Positive FCF indicates company can fund operations and dividends internally."
                })
        
        # --- 5. CapEx to Cash Flow (Reinvestment Rate) ---
        if cfo and cfo > 0 and capex > 0:
            capex_to_cfo = (capex / cfo) * 100
            
            if capex_to_cfo < 60:
                capex_judgment = "Sustainable"
            elif capex_to_cfo < 80:
                capex_judgment = "High Reinvestment"
            else:
                capex_judgment = "Unsustainable"
                
            insights.append({
                "metric": "CapEx as % of Operating Cash Flow",
                "value": f"{capex_to_cfo:.0f}%",
                "judgment": capex_judgment,
                "context": "High CapEx is typical for E&P. Should leave room for dividends and debt reduction."
            })
        
        # --- 6. Dividend Sustainability ---
        dividends = abs(self.data_engine.get_financials_safe(
            self.data_engine.cashflow, "Common Stock Dividend Paid", 0) or 0)
        ni = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Net Income", 0)
        
        if dividends > 0 and cfo and cfo > 0:
            payout_cfo = (dividends / cfo) * 100
            
            if payout_cfo < 50:
                div_judgment = "Sustainable"
            elif payout_cfo < 80:
                div_judgment = "Watch"
            else:
                div_judgment = "At Risk"
                red_flags.append("Dividend payout exceeds 80% of cash flow - may not be sustainable")
                
            insights.append({
                "metric": "Dividend as % of OCF",
                "value": f"{payout_cfo:.0f}%",
                "judgment": div_judgment,
                "context": "Energy dividends should be funded by operating cash flow, not debt."
            })
        
        # --- 7. Reserve & Production Notes (Manual) ---
        insights.append({
            "metric": "Reserve Replacement Ratio",
            "value": "Manual Verification Required",
            "judgment": "⚠️ Critical for E&P",
            "context": "Reserve Replacement >100% means company is finding more oil/gas than it produces. Essential for E&P valuation."
        })
        
        insights.append({
            "metric": "Finding & Development Costs",
            "value": "Manual Verification Required",
            "judgment": "ℹ️ Profitability Driver",
            "context": "F&D costs must be well below commodity prices for profitable production. Check annual reports."
        })
        
        return {
            "sector": self.sector_name,
            "chapter_reference": "Chapter 25: Energy",
            "insights": insights,
            "moat_indicators": moat_indicators if moat_indicators else None,
            "red_flags": red_flags if red_flags else None,
            "dorsey_wisdom": "Energy companies' profitability is largely dependent on factors they can't control - the price of oil and gas. Look for low-cost producers with strong balance sheets.",
            "key_questions": [
                "What is the reserve replacement ratio?",
                "What are Finding & Development costs vs commodity prices?",
                "Can the company survive a prolonged price downturn?",
                "Is the dividend funded by operating cash flow?"
            ]
        }
