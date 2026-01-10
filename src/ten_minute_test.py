
from src.smart_data import SmartDataEngine

class TenMinuteTest:
    """
    Implements Pat Dorsey's '10-Minute Test' (Chapter 12).
    A quick pre-screen to filter out companies before deep analysis.
    """
    
    def __init__(self, ticker):
        self.data_engine = SmartDataEngine(ticker)
        self.results = {
            "passed": False,
            "overall_verdict": "FAIL",
            "checklist": []
        }

    def run_test(self):
        """
        Executes the 10-minute screener.
        Returns a dictionary of results.
        """
        if not self.data_engine.has_data:
            self.results["overall_verdict"] = "NO DATA"
            return self.results
            
        failures = 0
        
        # --- CHECK 1: Minimum Quality (Free Cash Flow) ---
        # Rule: Companies should generate cash, not burn it.
        fcf = self.data_engine.calculate_fcf(0)
        check_fcf = {
            "name": "Generates Free Cash Flow?",
            "status": "PASS" if fcf > 0 else "FAIL",
            "value": f"₹{fcf:,.0f}",
            "reason": "Positive FCF indicates the business generates surplus cash."
        }
        if fcf <= 0: failures += 1
        self.results["checklist"].append(check_fcf)
        
        # --- CHECK 2: Operating Profit Growth (Sales/Earnings) ---
        # Rule: Operating Income shoudn't be shrinking significantly.
        op_income_curr = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", 0)
        op_income_prev = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", 1)
        
        growth = 0.0
        if op_income_prev > 0:
            growth = ((op_income_curr - op_income_prev) / op_income_prev) * 100
        
        check_growth = {
            "name": "Operating Profit Growing?",
            "status": "PASS" if growth > -5 else "FAIL", # Allow slight dip, but not collapse
            "value": f"{growth:.1f}%",
            "reason": "Consistent operating profit growth is a sign of a healthy core business."
        }
        if growth < -5: failures += 1
        self.results["checklist"].append(check_growth)
        
        # --- CHECK 3: Financial Health (Leverage) ---
        # Rule: Debt to Equity shouldn't be excessive (>1.0 usually red flag, unless Utility/Bank)
        # Note: We need sector context here eventually, but for generic 10-min test use 1.5 as safe limit.
        metrics = self.data_engine.get_manual_metrics()
        d_e = metrics["Debt_to_Equity_Manual"]
        
        check_debt = {
            "name": "Manageable Debt?",
            "status": "PASS" if d_e < 1.0 else "WARNING", # Strict Dorsey rule is < 0.5 for non-banks? Let's say 1.0
            "value": f"{d_e:.2f}",
            "reason": "High debt limits flexibility. Debt/Equity > 1.0 is risky."
        }
        if d_e > 2.0: # Fail only if very high
            check_debt["status"] = "FAIL"
            failures += 1
            
        self.results["checklist"].append(check_debt)
        
        # --- CHECK 4: Return on Equity (ROE) ---
        # Rule: ROE > 10-15% consistently.
        # We need Net Income / Equity
        ni = self.data_engine.get_financials_safe(self.data_engine.financials, "Net Income", 0)
        eq = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Stockholders Equity", 0)
        roe = (ni / eq) * 100 if eq > 0 else 0
        
        check_roe = {
            "name": "ROE > 10%?",
            "status": "PASS" if roe > 10 else "FAIL",
            "value": f"{roe:.1f}%",
            "reason": "ROE measures management's ability to compound capital."
        }
        if roe < 10: failures += 1
        self.results["checklist"].append(check_roe)
        
        # VERDICT
        if failures == 0:
            self.results["overall_verdict"] = "PASS"
            self.results["passed"] = True
        elif failures == 1:
            self.results["overall_verdict"] = "MARGINAL"
            self.results["passed"] = True 
        else:
            self.results["overall_verdict"] = "FAIL"
            self.results["passed"] = False
            
        return self.results

if __name__ == "__main__":
    t = TenMinuteTest("RELIANCE.NS")
    print(t.run_test())
