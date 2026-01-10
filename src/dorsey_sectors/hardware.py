"""
Hardware Sector Strategy - Chapter 20

Implements Pat Dorsey's analysis framework for hardware companies.

Per Dorsey's Five Rules:
- Hardware companies face inventory risk and obsolescence
- Lower gross margins than software (30-50% typical)
- Capital intensive with significant R&D requirements
- Cyclical demand patterns
- Must manage product replacement cycles
"""

from src.dorsey_sectors.base import SectorStrategy


class HardwareStrategy(SectorStrategy):
    """
    Implements Chapter 20: Hardware.
    
    Per Pat Dorsey's Five Rules:
    - Hardware faces inventory risk and rapid obsolescence
    - Gross margins typically 30-50% (vs 70%+ for software)
    - Higher CapEx requirements
    - Cyclical and technology-driven
    - Must monitor inventory levels carefully
    
    Key Metrics:
    - Gross Margin (30-50% typical for hardware)
    - Inventory Turnover (speed of product movement)
    - Inventory to Revenue ratio (working capital efficiency)
    - R&D Intensity (5-15% typical)
    - CapEx to Sales (capital intensity)
    
    Key Risks:
    - Inventory obsolescence
    - Technology disruption
    - Competition from low-cost manufacturers
    """
    
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Hardware"
        
    def analyze(self):
        insights = []
        moat_indicators = []
        red_flags = []
        
        # --- 1. Gross Margin (Hardware vs Software Distinction) ---
        rev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
        cost = self.data_engine.get_financials_safe(self.data_engine.financials, "Cost Of Revenue", 0)
        
        gross_margin = ((rev - cost) / rev * 100) if rev and rev > 0 else 0
        
        if gross_margin > 50:
            gm_judgment = "Strong - May Have Service/Software Mix"
        elif gross_margin > 35:
            gm_judgment = "Healthy for Hardware"
        elif gross_margin > 20:
            gm_judgment = "Commodity-like"
            red_flags.append("Low gross margin indicates commodity product with limited pricing power")
        else:
            gm_judgment = "Very Low"
            red_flags.append("Very low gross margin - verify business model sustainability")
        
        insights.append({
            "metric": "Gross Margin",
            "value": f"{gross_margin:.1f}%",
            "judgment": gm_judgment,
            "context": "Hardware typically has 30-50% gross margins. Higher suggests software/service component.",
            "benchmark": ">50% premium, 35-50% healthy, <35% commodity"
        })
        
        # --- 2. Inventory Turnover (Critical for Hardware) ---
        inventory = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Inventory", 0)
        cogs = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Cost Of Revenue", 0)
        
        if inventory and inventory > 0 and cogs:
            inv_turnover = cogs / inventory
            
            if inv_turnover > 8:
                inv_judgment = "Excellent - Fast Moving"
            elif inv_turnover > 5:
                inv_judgment = "Good"
            elif inv_turnover > 3:
                inv_judgment = "Average"
            else:
                inv_judgment = "Slow"
                red_flags.append("Low inventory turnover - risk of obsolescence")
                
            insights.append({
                "metric": "Inventory Turnover",
                "value": f"{inv_turnover:.1f}x",
                "judgment": inv_judgment,
                "context": "Per Dorsey: Hardware companies face inventory obsolescence risk. Faster turnover is safer."
            })
        
        # --- 3. Inventory to Revenue Ratio ---
        if inventory and rev and rev > 0:
            inv_to_rev = (inventory / rev) * 100
            
            if inv_to_rev < 10:
                inv_rev_judgment = "Lean"
            elif inv_to_rev < 20:
                inv_rev_judgment = "Normal"
            else:
                inv_rev_judgment = "Heavy"
                red_flags.append("High inventory relative to revenue - working capital intensive")
                
            insights.append({
                "metric": "Inventory to Revenue",
                "value": f"{inv_to_rev:.1f}%",
                "judgment": inv_rev_judgment,
                "context": "<15% is efficient for hardware companies."
            })
        
        # --- 4. Inventory Growth vs Revenue Growth ---
        inventory_prev = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Inventory", 1)
        rev_prev = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Total Revenue", 1)
        
        if inventory and inventory_prev and inventory_prev > 0:
            inv_growth = ((inventory - inventory_prev) / inventory_prev) * 100
            rev_growth = ((rev - rev_prev) / rev_prev * 100) if rev_prev and rev_prev > 0 else 0
            
            if inv_growth > rev_growth + 10:
                inv_vs_rev_judgment = "⚠️ Warning"
                red_flags.append(f"Inventory growing faster than revenue ({inv_growth:.0f}% vs {rev_growth:.0f}%) - potential demand issue")
            elif inv_growth > rev_growth:
                inv_vs_rev_judgment = "Watch"
            else:
                inv_vs_rev_judgment = "Healthy"
                
            insights.append({
                "metric": "Inventory Growth vs Revenue Growth",
                "value": f"{inv_growth:.1f}% vs {rev_growth:.1f}%",
                "judgment": inv_vs_rev_judgment,
                "context": "Inventory growing faster than revenue can signal demand problems."
            })
        
        # --- 5. R&D Intensity ---
        rd_expense = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Research And Development", 0)
        
        if rd_expense and rev and rev > 0:
            rd_intensity = (rd_expense / rev) * 100
            
            if rd_intensity > 15:
                rd_judgment = "High - Innovation Focused"
            elif rd_intensity > 8:
                rd_judgment = "Healthy"
            elif rd_intensity > 3:
                rd_judgment = "Low"
            else:
                rd_judgment = "Minimal"
                red_flags.append("Low R&D investment may lead to competitive disadvantage")
                
            insights.append({
                "metric": "R&D Intensity",
                "value": f"{rd_intensity:.1f}%",
                "judgment": rd_judgment,
                "context": "Hardware companies typically invest 5-15% of revenue in R&D."
            })
        
        # --- 6. CapEx Intensity ---
        capex = abs(self.data_engine.get_financials_safe(
            self.data_engine.cashflow, "Capital Expenditure", 0) or 0)
        
        if capex and rev and rev > 0:
            capex_intensity = (capex / rev) * 100
            
            if capex_intensity > 15:
                capex_judgment = "Very Capital Intensive"
            elif capex_intensity > 8:
                capex_judgment = "Capital Intensive"
            elif capex_intensity > 3:
                capex_judgment = "Moderate"
            else:
                capex_judgment = "Asset Light"
                moat_indicators.append("Low CapEx suggests efficient operations or fabless model")
                
            insights.append({
                "metric": "CapEx to Revenue",
                "value": f"{capex_intensity:.1f}%",
                "judgment": capex_judgment,
                "context": "Hardware manufacturing is typically capital intensive. Fabless models have lower CapEx."
            })
        
        # --- 7. Operating Margin ---
        op_income = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Operating Income", 0)
        
        if op_income and rev and rev > 0:
            op_margin = (op_income / rev) * 100
            
            if op_margin > 20:
                op_judgment = "Excellent for Hardware"
                moat_indicators.append("High operating margin suggests competitive advantage")
            elif op_margin > 10:
                op_judgment = "Good"
            elif op_margin > 5:
                op_judgment = "Thin"
            else:
                op_judgment = "Low"
                
            insights.append({
                "metric": "Operating Margin",
                "value": f"{op_margin:.1f}%",
                "judgment": op_judgment,
                "context": "Hardware operating margins typically 10-20%. Higher suggests moat."
            })
        
        # --- 8. Days Inventory Outstanding ---
        if inventory and cogs and cogs > 0:
            dio = (inventory / cogs) * 365
            
            if dio < 45:
                dio_judgment = "Efficient"
            elif dio < 90:
                dio_judgment = "Normal"
            else:
                dio_judgment = "High"
                red_flags.append(f"High days inventory ({dio:.0f} days) - obsolescence risk")
                
            insights.append({
                "metric": "Days Inventory Outstanding",
                "value": f"{dio:.0f} days",
                "judgment": dio_judgment,
                "context": "Lower is better for hardware. High DIO increases obsolescence risk."
            })
        
        return {
            "sector": self.sector_name,
            "chapter_reference": "Chapter 20: Hardware",
            "insights": insights,
            "moat_indicators": moat_indicators if moat_indicators else None,
            "red_flags": red_flags if red_flags else None,
            "dorsey_wisdom": "Hardware companies can accumulate excess inventory or struggle to meet sudden demand. When the Internet bubble burst, Cisco wrote down billions in excess inventory.",
            "key_questions": [
                "What's the product replacement cycle?",
                "Is this a commodity or differentiated product?",
                "What's the manufacturing model (own fabs vs fabless)?",
                "How quickly does technology obsolete inventory?"
            ]
        }
