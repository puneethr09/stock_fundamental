
from src.dorsey_sectors.base import SectorStrategy

class FinancialStrategy(SectorStrategy):
    """
    Implements Chapter 16: The Money Business (Banks, Insurance, Asset Mgmt).
    Key Metrics:
    - Price to Book (P/B)
    - Return on Equity (ROE)
    - Efficiency Ratio (Non-Interest Exp / Revenue)
    """
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Financial Services"
        
    def analyze(self):
        insights = []
        
        # 1. Price to Book (Core Valuation for Banks)
        pb = self.data_engine.info.get("priceToBook", 0)
        insights.append({
            "metric": "Price to Book (P/B)",
            "value": f"{pb:.2f}x",
            "judgment": "Good" if pb < 1.5 else ("Premium" if pb < 3.0 else "Expensive"),
            "context": "Banks trade on book value. < 1.5x is usually good value."
        })
        
        # 2. ROE (Management Quality in Banks)
        # Re-calc manually to be safe
        ni = self.data_engine.get_financials_safe(self.data_engine.financials, "Net Income", 0)
        eq = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Stockholders Equity", 0)
        roe = (ni / eq) * 100 if eq > 0 else 0
        
        insights.append({
            "metric": "Return on Equity (ROE)",
            "value": f"{roe:.1f}%",
            "judgment": "Excellent" if roe > 15 else ("Good" if roe > 10 else "Weak"),
            "context": "Banks leverage OPM. High ROE (>12%) is essential."
        })
        
        # 3. Efficiency Ratio Check (Rough Approximation)
        # Non-Interest Expense / Revenue. 
        # Using Operating Expense / Total Revenue as proxy if specific keys missing
        total_rev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
        # Assuming 'Selling General And Administration' or similar is the main non-interest exp
        opex = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Expense", 0)
        
        if total_rev > 0:
            eff_ratio = (opex / total_rev) * 100
            insights.append({
                "metric": "Efficiency Ratio (Proxy)",
                "value": f"{eff_ratio:.1f}%",
                "judgment": "Efficient" if eff_ratio < 50 else "Inefficient",
                "context": "Lower is better. < 50% is best-in-class."
            })
            
        return {"sector": self.sector_name, "insights": insights}
