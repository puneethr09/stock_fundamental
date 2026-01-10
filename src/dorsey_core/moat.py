
from src.smart_data import SmartDataEngine
import numpy as np

class MoatAnalyzer:
    """
    Implements Moat Analysis (Chapter 3).
    Evaluates:
    1. quantitative evidence of a moat (ROIC > Cost of Capital)
    2. Stability of margins.
    """
    
    def __init__(self, ticker):
        self.data_engine = SmartDataEngine(ticker)
        
    def analyze_moat(self):
        """
        Determines if the company has a Wide, Narrow, or No Moat.
        """
        if not self.data_engine.has_data:
            return {"moat_rating": "UNKNOWN", "details": []}
            
        details = []
        
        # --- 1. ROIC Test (The Gold Standard) ---
        # Rule: Wide Moat = ROIC > 15% for 10+ years (We'll check available years).
        # Rule: Narrow Moat = ROIC > 15% for 5-10 years.
        
        # Get historical ROIC manually
        # Note: In a real "Hardcore" implementation we might need more history.
        # SmartDataEngine currently does 3 years (0, 1, 2). Let's use that trending.
        
        roic_0 = self.data_engine.calculate_roic(0)
        roic_1 = self.data_engine.calculate_roic(1)
        roic_2 = self.data_engine.calculate_roic(2)
        
        avg_roic = (roic_0 + roic_1 + roic_2) / 3 if roic_0 and roic_1 and roic_2 else roic_0
        
        roic_status = "FAIL"
        if avg_roic > 15:
            roic_rating = "Excellent"
            roic_status = "PASS"
        elif avg_roic > 10:
            roic_rating = "Good"
            roic_status = "BORDERLINE"
        else:
            roic_rating = "Poor"
            
        details.append({
            "metric": "Avg ROIC (3yr)",
            "value": f"{avg_roic:.1f}%",
            "rating": roic_rating,
            "comment": "ROIC above 15% is strong evidence of a moat."
        })
        
        # --- 2. Gross Margin Stability ---
        # Rule: Moaty companies have pricing power -> stable or rising margins.
        gm_0 = self.data_engine.get_financials_safe(self.data_engine.info, "grossMargins", 0) * 100
        # If info fails, we try calculation from financials
        if gm_0 == 0:
             rev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
             cost = self.data_engine.get_financials_safe(self.data_engine.financials, "Cost Of Revenue", 0)
             if rev > 0:
                 gm_0 = ((rev - cost) / rev) * 100

        details.append({
            "metric": "Gross Margin (Latest)",
            "value": f"{gm_0:.1f}%",
            "rating": "High" if gm_0 > 40 else "Average",
            "comment": "High gross margins indicate pricing power or low cost production."
        })
        
        # --- VERDICT ---
        # Simple heuristic for this implementation
        if avg_roic > 15:
            moat_rating = "Wide Moat"
        elif avg_roic > 10 and gm_0 > 40:
            moat_rating = "Narrow Moat"
        elif avg_roic > 10:
             moat_rating = "Possible Moat"
        else:
            moat_rating = "No Moat"
            
        return {
            "moat_rating": moat_rating,
            "details": details
        }

if __name__ == "__main__":
    m = MoatAnalyzer("TCS.NS")
    print(m.analyze_moat())
