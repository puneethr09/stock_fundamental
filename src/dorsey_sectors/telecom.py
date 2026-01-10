
from src.dorsey_sectors.base import SectorStrategy

class TelecomStrategy(SectorStrategy):
    """
    Implements Chapter 22: Telecom.
    Key Metrics:
    - ARPU (Avg Revenue Per User) - Hard to get auto, proxy with Rev Growth.
    - Ratio of CapEx to Sales (Network Maintenance)
    - Debt Loads (Leverage)
    """
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Telecom"
        
    def analyze(self):
        insights = []
        
        # 1. CapEx Intensity (Network upkeep is expensive)
        capex = abs(self.data_engine.get_financials_safe(self.data_engine.cashflow, "Capital Expenditure", 0))
        rev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
        
        if rev > 0:
            intensity = (capex / rev) * 100
            judgment = "Heavy Spend" if intensity > 20 else "Moderate"
            if intensity < 10: judgment = "Asset Light?" # Rare for Telco
            
            insights.append({
                "metric": "CapEx % of Sales",
                "value": f"{intensity:.1f}%",
                "judgment": judgment,
                "context": "Telecoms spend heavily (15-20%) just to maintain netorks."
            })
            
        # 2. Leverage (Debt/EBITDA proxy)
        # Using Debt/Equity as simpler proxy
        metrics = self.data_engine.get_manual_metrics()
        de = metrics["Debt_to_Equity_Manual"]
        
        insights.append({
            "metric": "Leverage (D/E)",
            "value": f"{de:.2f}",
            "judgment": "High" if de > 1.5 else "Safe",
            "context": "Telecoms carry high debt, but >1.5-2.0 is risky due to rate sensitivity."
        })
            
        return {"sector": self.sector_name, "insights": insights}
