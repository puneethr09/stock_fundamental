"""
Ten-Minute Test - Chapter 12

Pat Dorsey's quick pre-screening checklist to filter out companies 
before deep analysis. This saves time by eliminating obviously 
unsuitable investments.

Per Chapter 12, the test includes:
1. Minimum quality hurdles (market cap, trading venue, IPO status)
2. Operating profit history
3. Cash flow consistency
4. ROE with reasonable leverage
5. Earnings stability
6. Balance sheet cleanliness
7. Share dilution check
"""

from src.smart_data import SmartDataEngine


class TenMinuteTest:
    """
    Implements Pat Dorsey's '10-Minute Test' (Chapter 12).
    A quick pre-screen to filter out companies before deep analysis.
    
    Per the book, avoid:
    - Companies with minuscule market caps (penny stocks)
    - Bulletin board traded stocks
    - Recent IPOs (except spinoffs)
    - Foreign firms without regular financial filings
    
    Quick checks:
    1. Has ever made an operating profit?
    2. Generates consistent cash flow from operations?
    3. ROE consistently above 10% with reasonable leverage?
    4. Is earnings growth consistent or erratic?
    5. How clean is the balance sheet?
    6. Does the firm generate free cash flow?
    7. Has share count increased significantly?
    """
    
    # Minimum market cap threshold (₹500 Crore for India)
    MIN_MARKET_CAP_INR = 500_00_00_000  # 500 Crore
    
    def __init__(self, ticker):
        self.data_engine = SmartDataEngine(ticker)
        self.ticker = ticker
        self.results = {
            "ticker": ticker,
            "passed": False,
            "overall_verdict": "FAIL",
            "score": 0,
            "max_score": 8,
            "checklist": [],
            "minimum_quality_hurdles": [],
            "warnings": []
        }

    def run_test(self):
        """
        Executes the complete 10-minute screener.
        Returns a dictionary of results.
        """
        if not self.data_engine.has_data:
            self.results["overall_verdict"] = "NO DATA"
            return self.results
            
        score = 0
        
        # ============================================================
        # MINIMUM QUALITY HURDLES (Pre-filters)
        # ============================================================
        
        # --- HURDLE 1: Market Cap Check ---
        market_cap = self.data_engine.info.get("marketCap", 0)
        if market_cap and market_cap > 0:
            market_cap_cr = market_cap / 10_000_000  # Convert to Crores
            hurdle_cap = {
                "name": "Adequate Market Cap",
                "passed": market_cap > self.MIN_MARKET_CAP_INR,
                "value": f"₹{market_cap_cr:,.0f} Cr",
                "threshold": "≥ ₹500 Cr",
                "reason": "Avoid micro/penny stocks with low liquidity and higher manipulation risk."
            }
            self.results["minimum_quality_hurdles"].append(hurdle_cap)
            if market_cap < self.MIN_MARKET_CAP_INR:
                self.results["warnings"].append("Small market cap - exercise extra caution")
        
        # --- HURDLE 2: Recent IPO Check ---
        # Note: Hard to detect programmatically. Add as guidance.
        self.results["minimum_quality_hurdles"].append({
            "name": "Not a Recent IPO",
            "passed": "Manual Check",
            "value": "Verify Manually",
            "threshold": "Listed > 2 years",
            "reason": "Recent IPOs lack track record. Exception: spinoffs from established companies."
        })
        
        # ============================================================
        # CHECK 1: Has Ever Made Operating Profit?
        # ============================================================
        has_op_profit = False
        op_incomes = []
        for year in range(3):
            op_inc = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", year)
            if op_inc is not None:
                op_incomes.append(op_inc)
                if op_inc > 0:
                    has_op_profit = True
        
        check_op_profit = {
            "name": "Has Made Operating Profit?",
            "status": "PASS" if has_op_profit else "FAIL",
            "value": "Yes" if has_op_profit else "No",
            "reason": "Company should have demonstrated ability to generate operating profit."
        }
        if has_op_profit:
            score += 1
        self.results["checklist"].append(check_op_profit)
        
        # ============================================================
        # CHECK 2: Generates Free Cash Flow?
        # ============================================================
        fcf = self.data_engine.calculate_fcf(0)
        check_fcf = {
            "name": "Generates Free Cash Flow?",
            "status": "PASS" if fcf and fcf > 0 else "FAIL",
            "value": f"₹{fcf:,.0f}" if fcf else "N/A",
            "reason": "Positive FCF indicates the business generates surplus cash after investments."
        }
        if fcf and fcf > 0:
            score += 1
        self.results["checklist"].append(check_fcf)
        
        # ============================================================
        # CHECK 3: Consistent Cash Flow from Operations?
        # ============================================================
        cfo_positive_years = 0
        for year in range(3):
            cfo = self.data_engine.get_financials_safe(self.data_engine.cashflow, "Operating Cash Flow", year)
            if cfo and cfo > 0:
                cfo_positive_years += 1
        
        check_cfo = {
            "name": "Consistent Operating Cash Flow?",
            "status": "PASS" if cfo_positive_years >= 2 else "FAIL",
            "value": f"{cfo_positive_years}/3 years positive",
            "reason": "Cash flow from operations should be positive most years."
        }
        if cfo_positive_years >= 2:
            score += 1
        self.results["checklist"].append(check_cfo)
        
        # ============================================================
        # CHECK 4: Operating Profit Growing?
        # ============================================================
        op_income_curr = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", 0)
        op_income_prev = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", 1)
        
        growth = 0.0
        if op_income_prev and op_income_prev > 0 and op_income_curr:
            growth = ((op_income_curr - op_income_prev) / op_income_prev) * 100
        
        check_growth = {
            "name": "Operating Profit Growing?",
            "status": "PASS" if growth > -10 else "FAIL",
            "value": f"{growth:.1f}%",
            "reason": "Operating profit shouldn't be declining significantly."
        }
        if growth > -10:
            score += 1
        self.results["checklist"].append(check_growth)
        
        # ============================================================
        # CHECK 5: Manageable Debt?
        # ============================================================
        metrics = self.data_engine.get_manual_metrics()
        d_e = metrics.get("Debt_to_Equity_Manual", 0)
        
        # Get sector for context
        sector = self.data_engine.info.get("sector", "").lower()
        is_financial = "financial" in sector
        
        # Financial firms can have higher leverage
        debt_threshold = 5.0 if is_financial else 1.5
        
        check_debt = {
            "name": "Manageable Debt?",
            "status": "PASS" if d_e < debt_threshold else ("WARNING" if d_e < debt_threshold * 1.5 else "FAIL"),
            "value": f"{d_e:.2f}x",
            "threshold": f"< {debt_threshold:.1f}x" + (" (Financial sector)" if is_financial else ""),
            "reason": "High debt limits flexibility and increases risk during downturns."
        }
        if d_e < debt_threshold:
            score += 1
        self.results["checklist"].append(check_debt)
        
        # ============================================================
        # CHECK 6: ROE > 10%?
        # ============================================================
        ni = self.data_engine.get_financials_safe(self.data_engine.financials, "Net Income", 0)
        eq = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Stockholders Equity", 0)
        roe = (ni / eq) * 100 if eq and eq > 0 else 0
        
        roe_threshold = 12 if is_financial else 10  # Higher bar for banks
        
        check_roe = {
            "name": f"ROE > {roe_threshold}%?",
            "status": "PASS" if roe > roe_threshold else "FAIL",
            "value": f"{roe:.1f}%",
            "reason": "ROE measures management's ability to compound shareholder capital."
        }
        if roe > roe_threshold:
            score += 1
        self.results["checklist"].append(check_roe)
        
        # ============================================================
        # CHECK 7: Clean Balance Sheet?
        # ============================================================
        # Proxy: Check if there's significant "Other" items or unusual liabilities
        total_assets = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Total Assets", 0)
        current_assets = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Current Assets", 0)
        ppe = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Net PPE", 0)
        goodwill = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Goodwill", 0) or 0
        
        # Check goodwill as % of assets (too high = acquisition-heavy, risky)
        goodwill_pct = (goodwill / total_assets * 100) if total_assets and total_assets > 0 else 0
        
        clean_bs = goodwill_pct < 30  # Less than 30% goodwill
        
        check_balance = {
            "name": "Clean Balance Sheet?",
            "status": "PASS" if clean_bs else "WARNING",
            "value": f"Goodwill: {goodwill_pct:.1f}% of assets",
            "reason": "Excessive goodwill or intangibles can indicate overpaid acquisitions."
        }
        if clean_bs:
            score += 1
        self.results["checklist"].append(check_balance)
        
        # ============================================================
        # CHECK 8: Shares Outstanding Stable?
        # ============================================================
        shares_current = self.data_engine.info.get("sharesOutstanding", 0)
        # Note: Historical shares hard to get from yfinance. Use proxy check.
        
        check_dilution = {
            "name": "Shares Outstanding Stable?",
            "status": "INFO",
            "value": f"{shares_current:,.0f}" if shares_current else "N/A",
            "reason": "Verify shares haven't increased > 5% over 3 years. Excessive dilution hurts shareholders."
        }
        # Give benefit of doubt, add to score
        score += 1
        self.results["checklist"].append(check_dilution)
        
        # ============================================================
        # FINAL VERDICT
        # ============================================================
        self.results["score"] = score
        
        if score >= 7:
            self.results["overall_verdict"] = "PASS"
            self.results["passed"] = True
        elif score >= 5:
            self.results["overall_verdict"] = "MARGINAL - Worth a Closer Look"
            self.results["passed"] = True
        elif score >= 3:
            self.results["overall_verdict"] = "WEAK - Proceed with Caution"
            self.results["passed"] = False
        else:
            self.results["overall_verdict"] = "FAIL - Skip This Stock"
            self.results["passed"] = False
            
        return self.results


if __name__ == "__main__":
    # Test various stocks
    test_tickers = ["RELIANCE.NS", "HDFCBANK.NS", "TCS.NS"]
    for ticker in test_tickers:
        print(f"\n{'='*50}")
        print(f"Ten-Minute Test: {ticker}")
        print('='*50)
        t = TenMinuteTest(ticker)
        result = t.run_test()
        print(f"Verdict: {result['overall_verdict']} (Score: {result['score']}/{result['max_score']})")
        for check in result['checklist']:
            print(f"  [{check['status']}] {check['name']}: {check['value']}")
