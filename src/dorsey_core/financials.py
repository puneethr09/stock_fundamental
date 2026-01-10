
from src.smart_data import SmartDataEngine

class FinancialsAnalyzer:
    """
    Implements Financial Health & Red Flag Analysis (Chapters 5-8).
    Checks for:
    1. Leverage Safety (Interest Coverage).
    2. Working Capital Red Flags (Inventory/Receivables bloat).
    """
    
    def __init__(self, ticker):
        self.data_engine = SmartDataEngine(ticker)
        
    def analyze_health(self):
        """
        Returns a dictionary of health checks and red flags.
        """
        results = {
            "health_rating": "Neutral",
            "red_flags": [],
            "checks": []
        }
        
        if not self.data_engine.has_data:
            return results
        
        # --- 1. Interest Coverage (Rule: > 5x is safe) ---
        op_income = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", 0)
        interest = self.data_engine.get_financials_safe(self.data_engine.financials, "Interest Expense", 0)
        
        # Interest is often negative in dataframes, take abs
        interest = abs(interest)
        
        if interest > 0:
            int_coverage = op_income / interest
            status = "PASS" if int_coverage > 5 else "WARNING"
            if int_coverage < 2: status = "FAIL" # Dangerous
            
            results["checks"].append({
                "metric": "Interest Coverage",
                "value": f"{int_coverage:.1f}x",
                "status": status,
                "rule": "Should be > 5x for safety."
            })
        else:
            results["checks"].append({
                "metric": "Interest Coverage",
                "value": "N/A (No Interest)",
                "status": "PASS",
                "rule": "No debt interest detected."
            })
            
        # --- 2. Red Flag: Inventory Growing Faster than Sales? ---
        # Compare Change in Inventory vs Change in Sales
        inv_curr = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Inventory", 0)
        inv_prev = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Inventory", 1)
        
        sales_curr = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
        sales_prev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 1)
        
        if inv_prev > 0 and sales_prev > 0:
            inv_growth = ((inv_curr - inv_prev) / inv_prev) * 100
            sales_growth = ((sales_curr - sales_prev) / sales_prev) * 100
            
            if inv_growth > (sales_growth + 10): # Inventory growing much faster
                results["red_flags"].append(
                    f"Inventory bloat: Growing at {inv_growth:.1f}% vs Sales at {sales_growth:.1f}%."
                )
            
        # --- 3. Red Flag: Receivables bloat? ---
        rec_curr = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Accounts Receivable", 0)
        rec_prev = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Accounts Receivable", 1)
        
        if rec_prev > 0 and sales_prev > 0:
             rec_growth = ((rec_curr - rec_prev) / rec_prev) * 100
             sales_growth2 = ((sales_curr - sales_prev) / sales_prev) * 100 # Redundant calc but clarity
             
             if rec_growth > (sales_growth2 + 10):
                 results["red_flags"].append(
                     f"Receivables bloat: Growing at {rec_growth:.1f}% vs Sales at {sales_growth2:.1f}%."
                 )
        
        # Verdict
        if len(results["red_flags"]) > 0:
            results["health_rating"] = "Risky"
        elif any(c["status"] == "FAIL" for c in results["checks"]):
            results["health_rating"] = "Weak"
        else:
            results["health_rating"] = "Robust"
            
        return results

if __name__ == "__main__":
    f = FinancialsAnalyzer("RELIANCE.NS")
    print(f.analyze_health())
