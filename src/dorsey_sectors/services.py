
from src.dorsey_sectors.base import SectorStrategy

class BusinessServicesStrategy(SectorStrategy):
    """
    Implements Chapter 18: Business Services.
    (Outsourcers, Data Processors, Ad Agencies)
    Key Metrics:
    - Recurring Revenue (Stability)
    - Cash Flow vs Net Income (Earnings Quality)
    - "Sticky" relationships
    """
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Business Services"
        
    def analyze(self):
        insights = []
        
        # 1. Earnings Stability (Std Dev of Operating Margin?)
        # Let's check Margin Stability over 3 years
        op_inc_0 = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", 0)
        op_inc_1 = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", 1)
        
        # Proxy: Is Operating Income growing steadily?
        growth = 0
        if op_inc_1 > 0:
            growth = ((op_inc_0 - op_inc_1) / op_inc_1) * 100
            
        judgment = "Growing" if growth > 5 else "Stagnant"
        
        insights.append({
            "metric": "Op Income Growth",
            "value": f"{growth:.1f}%",
            "judgment": judgment,
            "context": "Business services rely on recurring contracts. Consistent growth is key."
        })
        
        # 2. Cash Flow to Net Income
        # "Cash is King" applies here too. 
        fcf = self.data_engine.calculate_fcf(0)
        ni = self.data_engine.get_financials_safe(self.data_engine.financials, "Net Income", 0)
        
        if ni > 0:
            ratio = fcf / ni
            insights.append({
                "metric": "FCF / Net Income",
                "value": f"{ratio:.2f}x",
                "judgment": "High Quality" if ratio > 0.9 else "Accounting Warning",
                "context": "Should convert >90% of earnings to cash (low capex needs)."
            })
            
        return {"sector": self.sector_name, "insights": insights}
