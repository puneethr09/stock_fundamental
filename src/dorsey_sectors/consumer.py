
from src.dorsey_sectors.base import SectorStrategy

class ConsumerStrategy(SectorStrategy):
    """
    Implements Chapter 17 (Consumer Services) & Chapter 23 (Consumer Goods).
    Key Metrics:
    - Inventory Turnover (Efficiency)
    - Cash Conversion Cycle
    - Brand Power (Gross Margins)
    """
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Consumer Goods/Services"
        
    def analyze(self):
        insights = []
        
        # 1. Brand Power Proxy: Gross Margins
        # Durable competitive advantage usually shows up in margins > 40-50% for consumer goods
        # Manual Calculation: (Rev - COGS) / Rev
        rev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
        cogs = self.data_engine.get_financials_safe(self.data_engine.financials, "Cost Of Revenue", 0)
        
        gm_0 = 0
        if rev > 0:
            gm_0 = ((rev - cogs) / rev) * 100
        
        judgment = "Average"
        if gm_0 > 50: judgment = "Strong Brand Power"
        elif gm_0 < 20: judgment = "Commodity/No Brand"
        
        insights.append({
            "metric": "Brand Power (Gross Margin)",
            "value": f"{gm_0:.1f}%",
            "judgment": judgment,
            "context": "Strong consumer brands command pricing power (>50% margins)."
        })
        
        # 2. Inventory Turnover (Efficiency)
        # Cost of Goods Sold / Average Inventory
        cogs = self.data_engine.get_financials_safe(self.data_engine.financials, "Cost Of Revenue", 0)
        inv_curr = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Inventory", 0)
        inv_prev = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Inventory", 1)
        avg_inv = (inv_curr + inv_prev) / 2 if (inv_curr + inv_prev) > 0 else inv_curr
        
        if avg_inv > 0:
            turnover = cogs / avg_inv
            insights.append({
                "metric": "Inventory Turnover",
                "value": f"{turnover:.1f}x",
                "judgment": "High" if turnover > 8 else "Low",
                "context": "Higher turnover means goods aren't sitting on shelves (Cash is king)."
            })
        
        # 3. Same Store Sales (Proxy: Revenue Growth)
        # Specific SSS data is hard to get, so we look for consistent Rev Growth > 5%
        rev_curr = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
        rev_prev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 1)
        
        if rev_prev > 0:
            growth = ((rev_curr - rev_prev) / rev_prev) * 100
            insights.append({
                "metric": "Revenue Growth (SSS Proxy)",
                "value": f"{growth:.1f}%",
                "judgment": "Robust" if growth > 8 else "Sluggish",
                "context": "Consistent growth suggests expansion or pricing power."
            })
            
        return {"sector": self.sector_name, "insights": insights}
