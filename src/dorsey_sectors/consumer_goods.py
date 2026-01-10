"""
Consumer Goods Sector Strategy - Chapter 23

Implements Pat Dorsey's analysis framework for consumer goods companies.

Per Dorsey's Five Rules:
- Brand strength is the primary moat source
- Pricing power indicates brand value
- Distribution networks create barriers
- Focus on organic growth vs acquisitions
"""

from src.dorsey_sectors.base import SectorStrategy


class ConsumerGoodsStrategy(SectorStrategy):
    """
    Implements Chapter 23: Consumer Goods.
    
    Per Pat Dorsey's Five Rules:
    - Brand is only a moat if it increases willingness to pay or customer loyalty
    - Look for pricing power as evidence of brand strength
    - Distribution networks can be barriers to entry
    - Organic growth (selling more, raising prices, new products) preferred
    
    Key Metrics:
    - Gross Margin (Brand strength indicator)
    - Advertising to Sales (Brand investment)
    - Inventory Turnover (Working capital efficiency)
    - Organic Revenue Growth
    - ROIC (Brand economics)
    """
    
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Consumer Goods"
        
    def analyze(self):
        insights = []
        moat_indicators = []
        red_flags = []
        
        # --- 1. Gross Margin (Brand Strength Indicator) ---
        # Dorsey: Strong brands allow premium pricing = higher margins
        rev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
        cost = self.data_engine.get_financials_safe(self.data_engine.financials, "Cost Of Revenue", 0)
        
        gross_margin = ((rev - cost) / rev * 100) if rev and rev > 0 else 0
        
        if gross_margin > 50:
            gm_judgment = "Strong Brand Power"
            moat_indicators.append("High gross margin suggests strong pricing power from brand")
        elif gross_margin > 35:
            gm_judgment = "Good"
        elif gross_margin > 20:
            gm_judgment = "Commodity-like"
        else:
            gm_judgment = "Weak Pricing Power"
            red_flags.append("Low gross margin indicates commodity product or weak brand")
        
        insights.append({
            "metric": "Gross Margin",
            "value": f"{gross_margin:.1f}%",
            "judgment": gm_judgment,
            "context": "Per Dorsey: Brand moat shows in ability to charge premium prices. >45% indicates strong brand.",
            "benchmark": ">50% strong brand, 35-50% moderate, <35% commodity"
        })
        
        # --- 2. Advertising & Marketing Spend ---
        sga = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Selling General And Administration", 0)
        
        if sga and rev and rev > 0:
            sga_ratio = (sga / rev) * 100
            
            # High SG&A in consumer goods often means marketing spend
            insights.append({
                "metric": "SG&A to Revenue (Marketing Proxy)",
                "value": f"{sga_ratio:.1f}%",
                "judgment": "Brand Investment" if sga_ratio > 25 else "Efficient",
                "context": "Consumer goods companies invest significantly in marketing. 15-30% is typical."
            })
        
        # --- 3. Inventory Turnover ---
        inventory = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Inventory", 0)
        cogs = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Cost Of Revenue", 0)
        
        if inventory and inventory > 0 and cogs:
            inv_turnover = cogs / inventory
            
            if inv_turnover > 6:
                inv_judgment = "Efficient"
            elif inv_turnover > 4:
                inv_judgment = "Good"
            else:
                inv_judgment = "Slow Moving"
                
            insights.append({
                "metric": "Inventory Turnover",
                "value": f"{inv_turnover:.1f}x",
                "judgment": inv_judgment,
                "context": "CPG companies should turn inventory efficiently. >5x is good."
            })
        
        # --- 4. Revenue Growth (Organic Growth Focus) ---
        rev_prev = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Total Revenue", 1)
        
        if rev and rev_prev and rev_prev > 0:
            rev_growth = ((rev - rev_prev) / rev_prev) * 100
            
            if rev_growth > 10:
                growth_judgment = "Strong"
            elif rev_growth > 5:
                growth_judgment = "Healthy"
            elif rev_growth > 0:
                growth_judgment = "Slow"
            else:
                growth_judgment = "Declining"
                red_flags.append("Revenue declining - verify market share and category growth")
                
            insights.append({
                "metric": "Revenue Growth",
                "value": f"{rev_growth:.1f}%",
                "judgment": growth_judgment,
                "context": "Consumer goods typically grow 5-10%. Higher suggests market share gains or pricing power."
            })
        
        # --- 5. Operating Margin (Brand Economics) ---
        op_income = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Operating Income", 0)
        
        if op_income and rev and rev > 0:
            op_margin = (op_income / rev) * 100
            
            if op_margin > 20:
                op_judgment = "Excellent"
                moat_indicators.append("High operating margin indicates strong brand economics and scale")
            elif op_margin > 15:
                op_judgment = "Good"
            elif op_margin > 10:
                op_judgment = "Average"
            else:
                op_judgment = "Low"
                
            insights.append({
                "metric": "Operating Margin",
                "value": f"{op_margin:.1f}%",
                "judgment": op_judgment,
                "context": "Strong consumer brands achieve 18%+ operating margins."
            })
        
        # --- 6. ROIC (Capital Efficiency) ---
        roic = self.data_engine.calculate_roic(0)
        
        if roic:
            if roic > 20:
                roic_judgment = "Excellent"
                moat_indicators.append(f"ROIC of {roic:.1f}% indicates strong moat")
            elif roic > 15:
                roic_judgment = "Good"
            elif roic > 10:
                roic_judgment = "Average"
            else:
                roic_judgment = "Low"
                
            insights.append({
                "metric": "ROIC",
                "value": f"{roic:.1f}%",
                "judgment": roic_judgment,
                "context": "Strong brands have high ROIC due to asset-light models and pricing power."
            })
        
        # --- 7. Dividend (Mature Company Indicator) ---
        dividend_yield = self.data_engine.info.get("dividendYield", 0)
        if dividend_yield:
            insights.append({
                "metric": "Dividend Yield",
                "value": f"{dividend_yield*100:.1f}%",
                "judgment": "Income Play" if dividend_yield > 0.03 else "Growth Focus",
                "context": "Mature consumer goods companies often return cash via dividends."
            })
        
        return {
            "sector": self.sector_name,
            "chapter_reference": "Chapter 23: Consumer Goods",
            "insights": insights,
            "moat_indicators": moat_indicators if moat_indicators else None,
            "red_flags": red_flags if red_flags else None,
            "dorsey_wisdom": "A brand creates an economic moat only if it increases the consumer's willingness to pay or increases customer captivity. Lots of brands have no moat at all.",
            "key_questions": [
                "Can the company raise prices without losing customers?",
                "Is growth organic or acquisition-driven?",
                "Is the brand #1 or #2 in its category?",
                "What's the distribution advantage?"
            ]
        }
