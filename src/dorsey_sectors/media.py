
from src.dorsey_sectors.base import SectorStrategy

class MediaStrategy(SectorStrategy):
    """
    Implements Chapter 21: Media (Publishing, Broadcasting, Cable, Entertainment).
    
    Per Pat Dorsey's Five Rules:
    - Media can have strong moats via content libraries and distribution
    - Cable historically had local monopolies (now facing competition)
    - Focus on cash flow generation from content monetization
    
    Key Metrics:
    - FCF Margin (Content monetization efficiency)
    - Asset Turnover (Content library utilization)
    - Advertising Revenue Stability
    """
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Media"
        
    def analyze(self):
        insights = []
        
        # 1. Free Cash Flow Margin (Cash is Queen in Media)
        fcf = self.data_engine.calculate_fcf(0)
        rev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
        
        if rev > 0:
            margin = (fcf / rev) * 100
            
            judgment = "Cash Machine" if margin > 15 else "Average"
            if margin < 5: judgment = "Capital Intense/Low"
            
            insights.append({
                "metric": "FCF Margin",
                "value": f"{margin:.1f}%",
                "judgment": judgment,
                "context": "Media companies should convert ads/subs to cash efficiently (>15%)."
            })
            
        # 2. Asset Turnover (for broadcasters/publishers)
        # Revenue / Total Assets
        assets = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Total Assets", 0)
        if assets > 0:
            turnover = rev / assets
            insights.append({
                "metric": "Asset Turnover",
                "value": f"{turnover:.2f}x",
                "judgment": "Efficient" if turnover > 1.2 else "Heavy Assets",
                "context": "Indicates how well content assets are monetized."
            })
            
        return {"sector": self.sector_name, "insights": insights}
