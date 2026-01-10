
from src.dorsey_sectors.base import SectorStrategy

class IndustrialStrategy(SectorStrategy):
    """
    Implements Chapter 24 (Industrials), Chapter 25 (Energy), Chapter 26 (Utilities).
    Key Metrics:
    - Fixed Asset Turnover (Capital Intensity)
    - Dividend Yield (for Utilities/Energy)
    - Book Value Growth (Cyclicals)
    """
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Industrials/Energy/Materials"
        
    def analyze(self):
        insights = []
        
        # 1. Capital Intensity (Fixed Asset Turnover)
        # Revenue / PP&E
        rev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
        ppe = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Net PPE", 0) # Net Property, Plant, Equipment
        
        # YFinance sometimes calls it 'Net Tangible Assets' or similar if PPE missing, be careful.
        # Fallback to Total Assets if PPE is 0 to get some ratio suitable for banks? No, this is industrials.
        
        if ppe > 0:
            turnover = rev / ppe
            judgment = "Asset Light" if turnover > 3 else "Capital Intensive"
            
            insights.append({
                "metric": "Fixed Asset Turnover",
                "value": f"{turnover:.2f}x",
                "judgment": judgment,
                "context": "High capital intensity means high fixed costs. Needs scale."
            })
            
        # 2. Dividend Yield (Critical for Utilities/Energy)
        div_yield = self.data_engine.info.get("dividendYield", 0) or 0
        div_yield = div_yield * 100 # Convert to %
        
        insights.append({
            "metric": "Dividend Yield",
            "value": f"{div_yield:.2f}%",
            "judgment": "Attractive" if div_yield > 3 else "Low",
            "context": "Utilities and Energy majors are often income plays."
        })
        
        # 3. Book Value Growth (Value Creation in Cyclicals)
        # Compare Equity this year vs last year
        eq_curr = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Stockholders Equity", 0)
        eq_prev = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Stockholders Equity", 1)
        
        if eq_prev > 0:
            growth = ((eq_curr - eq_prev) / eq_prev) * 100
            insights.append({
                "metric": "Book Value Growth",
                "value": f"{growth:.1f}%",
                "judgment": "Creating Value" if growth > 8 else "Stagnant",
                "context": "For cyclical industries, growing Book Value > Inflation is key."
            })
            
        return {"sector": self.sector_name, "insights": insights}
