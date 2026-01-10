
from src.dorsey_sectors.base import SectorStrategy

class HealthcareStrategy(SectorStrategy):
    """
    Implements Chapter 15: Healthcare.
    Key Metrics:
    - R&D Productivity (R&D % of Sales)
    - Patent Cliff Risk (Revenue Concentration) - Hard to get auto, will use Margins as proxy.
    - Regulatory Risk.
    """
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Healthcare"
        
    def analyze(self):
        insights = []
        
        # 1. R&D Intensity
        rnd = self.data_engine.get_financials_safe(self.data_engine.financials, "Research And Development", 0)
        rev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
        
        if rev > 0:
            intensity = (rnd / rev) * 100
            judgment = "High Innovation" if intensity > 15 else ("Standard" if intensity > 5 else "Generic/Low R&D")
            
            insights.append({
                "metric": "R&D Intensity",
                "value": f"{intensity:.1f}%",
                "judgment": judgment,
                "context": "Pharma needs high R&D (>10%) to replace expiring patents. Generics can be lower."
            })
        else:
            insights.append({
                "metric": "R&D Intensity",
                "value": "N/A",
                "judgment": "Unknown",
                "context": "R&D expense not reported separately."
            })

        # 2. Operating Margin (Patent Protection Proxy)
        # High margins usually imply patent protection (Pricing Power).
        # Generics usually have lower margins (10-15%).
        op_income = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", 0)
        if rev > 0:
            op_margin = (op_income / rev) * 100
            
            judgment = "Protected/Patented" if op_margin > 20 else "Competitive/Generic"
            insights.append({
                "metric": "Operating Margin",
                "value": f"{op_margin:.1f}%",
                "judgment": judgment,
                "context": "High margins (>20%) suggest patent protection or strong niche."
            })

        return {"sector": self.sector_name, "insights": insights}
