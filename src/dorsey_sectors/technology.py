
from src.dorsey_sectors.base import SectorStrategy

class TechnologyStrategy(SectorStrategy):
    """
    Implements Chapter 21: Software & Hardware.
    Key Metrics:
    - Gross Margins (Pricing Power)
    - R&D as % of Sales
    - Cash Flow vs Net Income (Earnings Quality)
    """
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Technology"
        
    def analyze(self):
        insights = []
        
        # 1. Gross Margins (Software vs Hardware Check)
        gm_0 = self.data_engine.get_financials_safe(self.data_engine.info, "grossMargins", 0) * 100
        
        # Manual Fallback if info is missing (Common for Indian stocks)
        if gm_0 == 0:
             rev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
             cost = self.data_engine.get_financials_safe(self.data_engine.financials, "Cost Of Revenue", 0)
             if rev > 0:
                 gm_0 = ((rev - cost) / rev) * 100
        
        verdict = "Average"
        if gm_0 > 70: verdict = "Software-Like (Excellent)"
        elif gm_0 > 40: verdict = "Solid"
        elif gm_0 < 20: verdict = "Commodity/Hardware"
        
        insights.append({
            "metric": "Gross Margins",
            "value": f"{gm_0:.1f}%",
            "judgment": verdict,
            "context": "Software firms should have 70%+ margins. Hardware is lower."
        })
        
        # 2. Earnings Quality
        fcf = self.data_engine.calculate_fcf(0)
        ni = self.data_engine.get_financials_safe(self.data_engine.financials, "Net Income", 0)
        
        ratio = fcf / ni if ni > 0 else 0
        insights.append({
            "metric": "Cash Flow Conversion",
            "value": f"{ratio:.2f}x",
            "judgment": "Honest Earnings" if ratio > 0.9 else "Accounting Gimmicks?",
            "context": "Cash Flow should broadly match Net Income."
        })
            
        return {"sector": self.sector_name, "insights": insights}
