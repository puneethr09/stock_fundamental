"""
Software Sector Strategy - Chapter 19

Implements Pat Dorsey's analysis framework for software companies.

Per Dorsey's Five Rules:
- Software companies can have very wide moats due to switching costs
- High gross margins (70%+) are the hallmark of software economics
- Recurring revenue (maintenance, subscriptions) is key
- Low capital requirements lead to high FCF conversion
- Network effects possible in platform businesses
"""

from src.dorsey_sectors.base import SectorStrategy


class SoftwareStrategy(SectorStrategy):
    """
    Implements Chapter 19: Software.
    
    Per Pat Dorsey's Five Rules:
    - Software has among the widest moats of any industry
    - Switching costs are primary moat source (enterprise software)
    - Network effects for platform/marketplace software
    - High gross margins (70%+) are expected
    - Strong FCF conversion due to low CapEx
    
    Key Metrics:
    - Gross Margin (>70% = software-like economics)
    - R&D as % of Sales (innovation investment)
    - Deferred Revenue Growth (recurring revenue indicator)
    - FCF Conversion (should be close to net income)
    - License vs Maintenance Revenue Mix
    """
    
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Software"
        
    def analyze(self):
        insights = []
        moat_indicators = []
        red_flags = []
        
        # --- 1. Gross Margin (Core Software Indicator) ---
        # Dorsey: Successful software firms have gross margins > 70%
        rev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
        cost = self.data_engine.get_financials_safe(self.data_engine.financials, "Cost Of Revenue", 0)
        
        gross_margin = ((rev - cost) / rev * 100) if rev and rev > 0 else 0
        
        if gross_margin > 70:
            gm_judgment = "Software Excellence"
            moat_indicators.append("High gross margins indicate strong pricing power and software economics")
        elif gross_margin > 50:
            gm_judgment = "Good"
        else:
            gm_judgment = "Hardware-like"
            red_flags.append("Gross margin below 50% - may have hardware/services component")
        
        insights.append({
            "metric": "Gross Margin",
            "value": f"{gross_margin:.1f}%",
            "judgment": gm_judgment,
            "context": "Per Dorsey: Successful software firms average 70%+ gross margins.",
            "benchmark": ">70% excellent, 50-70% good, <50% hardware-like"
        })
        
        # --- 2. R&D Intensity ---
        # Software companies invest heavily in R&D (15-25% of revenue typical)
        rd_expense = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Research And Development", 0)
        
        if rd_expense and rev and rev > 0:
            rd_intensity = (rd_expense / rev) * 100
            
            if rd_intensity > 20:
                rd_judgment = "High Innovation Investment"
            elif rd_intensity > 12:
                rd_judgment = "Healthy"
            else:
                rd_judgment = "Low - May Be Mature"
                
            insights.append({
                "metric": "R&D Intensity",
                "value": f"{rd_intensity:.1f}%",
                "judgment": rd_judgment,
                "context": "Software companies typically invest 15-25% of revenue in R&D for product development."
            })
        
        # --- 3. Operating Margin ---
        op_income = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", 0)
        
        if op_income and rev and rev > 0:
            op_margin = (op_income / rev) * 100
            
            if op_margin > 30:
                op_judgment = "Excellent"
                moat_indicators.append("High operating margin suggests scale benefits and moat")
            elif op_margin > 20:
                op_judgment = "Good"
            elif op_margin > 10:
                op_judgment = "Developing"
            else:
                op_judgment = "Low"
                
            insights.append({
                "metric": "Operating Margin",
                "value": f"{op_margin:.1f}%",
                "judgment": op_judgment,
                "context": "Mature software companies should achieve 25%+ operating margins."
            })
        
        # --- 4. FCF Conversion (Cash Earnings Quality) ---
        ni = self.data_engine.get_financials_safe(self.data_engine.financials, "Net Income", 0)
        cfo = self.data_engine.get_financials_safe(self.data_engine.cashflow, "Operating Cash Flow", 0)
        capex = abs(self.data_engine.get_financials_safe(self.data_engine.cashflow, "Capital Expenditure", 0) or 0)
        fcf = cfo - capex if cfo else 0
        
        if ni and ni > 0 and fcf:
            fcf_conversion = (fcf / ni) * 100
            
            if fcf_conversion > 100:
                fcf_judgment = "Excellent"
                moat_indicators.append("FCF exceeds net income - high earnings quality")
            elif fcf_conversion > 80:
                fcf_judgment = "Good"
            else:
                fcf_judgment = "Verify"
                
            insights.append({
                "metric": "FCF to Net Income",
                "value": f"{fcf_conversion:.0f}%",
                "judgment": fcf_judgment,
                "context": "Software is capital-light. FCF should be close to or exceed net income."
            })
        
        # --- 5. Deferred Revenue (Recurring Revenue Proxy) ---
        deferred_rev = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Deferred Revenue", 0)
        deferred_rev_prev = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Deferred Revenue", 1)
        
        if deferred_rev and deferred_rev_prev and deferred_rev_prev > 0:
            deferred_growth = ((deferred_rev - deferred_rev_prev) / deferred_rev_prev) * 100
            
            if deferred_growth > 15:
                def_judgment = "Strong Growth"
                moat_indicators.append("Growing deferred revenue indicates expanding recurring revenue base")
            elif deferred_growth > 0:
                def_judgment = "Growing"
            else:
                def_judgment = "Declining"
                red_flags.append("Declining deferred revenue - may indicate customer churn")
                
            insights.append({
                "metric": "Deferred Revenue Growth",
                "value": f"{deferred_growth:.1f}%",
                "judgment": def_judgment,
                "context": "Rising deferred revenue signals future cash flows and customer stickiness."
            })
        
        # --- 6. Revenue Growth (Market Position) ---
        rev_prev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 1)
        
        if rev and rev_prev and rev_prev > 0:
            rev_growth = ((rev - rev_prev) / rev_prev) * 100
            
            if rev_growth > 20:
                growth_judgment = "High Growth"
            elif rev_growth > 10:
                growth_judgment = "Healthy Growth"
            elif rev_growth > 0:
                growth_judgment = "Mature"
            else:
                growth_judgment = "Declining"
                red_flags.append("Revenue declining - verify competitive position")
                
            insights.append({
                "metric": "Revenue Growth",
                "value": f"{rev_growth:.1f}%",
                "judgment": growth_judgment,
                "context": "Software companies should grow faster than GDP. >15% is strong."
            })
        
        # --- 7. Customer Acquisition Cost Proxy ---
        sga = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Selling General And Administration", 0)
        
        if sga and rev and rev > 0:
            sga_ratio = (sga / rev) * 100
            
            insights.append({
                "metric": "SG&A to Revenue",
                "value": f"{sga_ratio:.1f}%",
                "judgment": "Efficient" if sga_ratio < 30 else "High Sales Investment",
                "context": "High SG&A can indicate growth investment or sales model inefficiency."
            })
        
        return {
            "sector": self.sector_name,
            "chapter_reference": "Chapter 19: Software",
            "insights": insights,
            "moat_indicators": moat_indicators if moat_indicators else None,
            "red_flags": red_flags if red_flags else None,
            "dorsey_wisdom": "Software companies can have very wide moats due to switching costs. Once a customer builds their business around your software, moving is painful and expensive.",
            "key_questions": [
                "Is revenue recurring (subscriptions/maintenance) or one-time (licenses)?",
                "What percentage of revenue comes from existing customers vs new?",
                "How sticky is the product (switching costs)?",
                "Is there a network effect (more users = more value)?"
            ]
        }
