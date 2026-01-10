"""
Financial Health & Red Flag Analysis - Chapters 5-8

Implements comprehensive financial statement analysis with focus on:
- Chapter 5-6: Financial Statement Basics
- Chapter 7: Management Assessment Proxies
- Chapter 8: Avoiding Financial Fakery (Red Flags)
"""

from src.smart_data import SmartDataEngine


class FinancialsAnalyzer:
    """
    Implements Financial Health & Red Flag Analysis (Chapters 5-8).
    
    Chapter 8 Red Flags (Financial Fakery):
    1. Operating cash flow declining while net income growing
    2. Days Sales Outstanding (DSO) increasing
    3. Inventory bloat (growing faster than sales)
    4. Receivables bloat (growing faster than sales)
    5. One-time charges recurring frequently
    6. Earnings growing faster than sales long-term
    7. Non-operating income boosting results
    """
    
    def __init__(self, ticker):
        self.data_engine = SmartDataEngine(ticker)
        self.ticker = ticker
        
    def analyze_health(self):
        """
        Returns comprehensive financial health analysis with red flags.
        """
        results = {
            "ticker": self.ticker,
            "health_rating": "Neutral",
            "health_score": 0,
            "max_score": 5,
            "red_flags": [],
            "amber_flags": [],
            "checks": []
        }
        
        if not self.data_engine.has_data:
            return results
        
        score = 0
        
        # ============================================================
        # CHECK 1: Interest Coverage (Rule: > 5x is safe)
        # ============================================================
        op_income = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Operating Income", 0)
        interest = abs(self.data_engine.get_financials_safe(
            self.data_engine.financials, "Interest Expense", 0) or 0)
        
        if interest > 0:
            int_coverage = op_income / interest if op_income else 0
            
            if int_coverage > 5:
                status = "PASS"
                score += 1
            elif int_coverage > 2:
                status = "WARNING"
                results["amber_flags"].append("Interest coverage between 2-5x - monitor debt levels")
            else:
                status = "FAIL"
                results["red_flags"].append(f"Weak interest coverage ({int_coverage:.1f}x) - debt burden is concerning")
            
            results["checks"].append({
                "metric": "Interest Coverage",
                "value": f"{int_coverage:.1f}x",
                "status": status,
                "context": "Per Dorsey: > 5x is safe, < 2x is dangerous"
            })
        else:
            results["checks"].append({
                "metric": "Interest Coverage",
                "value": "N/A (No Interest)",
                "status": "PASS",
                "context": "No material interest expense detected"
            })
            score += 1
        
        # ============================================================
        # CHECK 2: Cash Flow vs Earnings Quality
        # Chapter 8: OCF declining while NI growing is a red flag
        # ============================================================
        ni_curr = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Net Income", 0)
        ni_prev = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Net Income", 1)
        cfo_curr = self.data_engine.get_financials_safe(
            self.data_engine.cashflow, "Operating Cash Flow", 0)
        cfo_prev = self.data_engine.get_financials_safe(
            self.data_engine.cashflow, "Operating Cash Flow", 1)
        
        if ni_curr and cfo_curr:
            cfo_to_ni = cfo_curr / ni_curr if ni_curr != 0 else 0
            
            if cfo_to_ni >= 1.0:
                cash_status = "PASS"
                score += 1
            elif cfo_to_ni >= 0.8:
                cash_status = "OK"
            else:
                cash_status = "WARNING"
                results["amber_flags"].append(f"Cash flow is only {cfo_to_ni*100:.0f}% of net income")
            
            results["checks"].append({
                "metric": "CFO to Net Income",
                "value": f"{cfo_to_ni*100:.0f}%",
                "status": cash_status,
                "context": "Per Dorsey Ch8: Cash should match or exceed earnings"
            })
            
            # Check for divergence (critical red flag)
            if ni_prev and cfo_prev and ni_prev > 0 and cfo_prev > 0:
                ni_growth = ((ni_curr - ni_prev) / ni_prev) * 100
                cfo_growth = ((cfo_curr - cfo_prev) / cfo_prev) * 100
                
                if ni_growth > 10 and cfo_growth < -5:
                    results["red_flags"].append(
                        f"🚨 CRITICAL: Earnings up {ni_growth:.0f}% but cash flow down {cfo_growth:.0f}% - possible earnings manipulation"
                    )
        
        # ============================================================
        # RED FLAG: Inventory Growing Faster than Sales
        # Chapter 8: Inventory bloat
        # ============================================================
        inv_curr = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Inventory", 0)
        inv_prev = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Inventory", 1)
        sales_curr = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Total Revenue", 0)
        sales_prev = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Total Revenue", 1)
        
        if inv_prev and inv_prev > 0 and sales_prev and sales_prev > 0 and inv_curr and sales_curr:
            inv_growth = ((inv_curr - inv_prev) / inv_prev) * 100
            sales_growth = ((sales_curr - sales_prev) / sales_prev) * 100
            
            if inv_growth > sales_growth + 15:
                results["red_flags"].append(
                    f"Inventory bloat: Growing {inv_growth:.0f}% vs Sales {sales_growth:.0f}% (gap > 15%)"
                )
            elif inv_growth > sales_growth + 5:
                results["amber_flags"].append(
                    f"Inventory rising faster than sales ({inv_growth:.0f}% vs {sales_growth:.0f}%)"
                )
            else:
                score += 1
        else:
            score += 1  # No inventory or not applicable
        
        # ============================================================
        # RED FLAG: Receivables Growing Faster than Sales
        # Chapter 8: Receivables bloat / aggressive revenue recognition
        # ============================================================
        rec_curr = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Accounts Receivable", 0)
        rec_prev = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Accounts Receivable", 1)
        
        if rec_prev and rec_prev > 0 and sales_prev and sales_prev > 0 and rec_curr and sales_curr:
            rec_growth = ((rec_curr - rec_prev) / rec_prev) * 100
            sales_growth = ((sales_curr - sales_prev) / sales_prev) * 100
            
            if rec_growth > sales_growth + 15:
                results["red_flags"].append(
                    f"Receivables bloat: Growing {rec_growth:.0f}% vs Sales {sales_growth:.0f}% - may indicate aggressive revenue recognition"
                )
            elif rec_growth > sales_growth + 5:
                results["amber_flags"].append(
                    f"Receivables rising faster than sales ({rec_growth:.0f}% vs {sales_growth:.0f}%)"
                )
            else:
                score += 1
        else:
            score += 1
        
        # ============================================================
        # RED FLAG: Days Sales Outstanding (DSO) Increasing
        # Chapter 8: DSO trend
        # ============================================================
        if rec_curr and sales_curr and sales_curr > 0:
            dso_curr = (rec_curr / sales_curr) * 365
            
            if rec_prev and sales_prev and sales_prev > 0:
                dso_prev = (rec_prev / sales_prev) * 365
                dso_change = dso_curr - dso_prev
                
                results["checks"].append({
                    "metric": "Days Sales Outstanding",
                    "value": f"{dso_curr:.0f} days (Δ{dso_change:+.0f})",
                    "status": "WARNING" if dso_change > 10 else "OK",
                    "context": "Per Dorsey Ch8: Rising DSO may indicate collection problems"
                })
                
                if dso_change > 15:
                    results["amber_flags"].append(f"DSO increased by {dso_change:.0f} days - verify collection trends")
        
        # ============================================================
        # RED FLAG: Earnings Growing Faster than Sales (Long-term)
        # Chapter 8: Not sustainable without margin expansion
        # ============================================================
        sales_old = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Total Revenue", 2)
        ni_old = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Net Income", 2)
        
        if sales_curr and sales_old and sales_old > 0 and ni_curr and ni_old and ni_old > 0:
            sales_cagr = ((sales_curr / sales_old) ** 0.5 - 1) * 100
            ni_cagr = ((ni_curr / ni_old) ** 0.5 - 1) * 100
            
            if ni_cagr > sales_cagr + 10:
                results["amber_flags"].append(
                    f"Earnings CAGR ({ni_cagr:.0f}%) significantly exceeds Sales CAGR ({sales_cagr:.0f}%) - verify sustainability"
                )
        
        # ============================================================
        # CHECK: Current Ratio
        # ============================================================
        current_assets = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Current Assets", 0)
        current_liabilities = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Current Liabilities", 0)
        
        if current_liabilities and current_liabilities > 0 and current_assets:
            current_ratio = current_assets / current_liabilities
            
            if current_ratio >= 1.5:
                cr_status = "PASS"
                score += 1
            elif current_ratio >= 1.0:
                cr_status = "OK"
            else:
                cr_status = "WARNING"
                results["amber_flags"].append("Current ratio below 1.0 - may face liquidity issues")
            
            results["checks"].append({
                "metric": "Current Ratio",
                "value": f"{current_ratio:.2f}x",
                "status": cr_status,
                "context": "≥ 1.5x is healthy for most industries"
            })
        
        # ============================================================
        # FINAL HEALTH RATING
        # ============================================================
        results["health_score"] = score
        
        if len(results["red_flags"]) > 0:
            results["health_rating"] = "RISKY"
        elif len(results["amber_flags"]) > 2:
            results["health_rating"] = "WEAK"
        elif score >= 4:
            results["health_rating"] = "ROBUST"
        elif score >= 2:
            results["health_rating"] = "MODERATE"
        else:
            results["health_rating"] = "WEAK"
        
        return results
    
    def get_chapter8_summary(self):
        """
        Returns a focused summary of Chapter 8 red flags only.
        """
        health = self.analyze_health()
        
        return {
            "ticker": self.ticker,
            "financial_fakery_detected": len(health["red_flags"]) > 0,
            "red_flags": health["red_flags"],
            "amber_flags": health["amber_flags"],
            "dorsey_chapter8_wisdom": "The most common tricks involve boosting revenue, playing with operating expenses, or hiding expenses below the line. Always compare earnings to cash flow."
        }


if __name__ == "__main__":
    # Test
    test_tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
    for ticker in test_tickers:
        print(f"\n{'='*60}")
        print(f"Financial Analysis: {ticker}")
        print('='*60)
        f = FinancialsAnalyzer(ticker)
        result = f.analyze_health()
        
        print(f"Health Rating: {result['health_rating']} ({result['health_score']}/{result['max_score']})")
        
        if result["red_flags"]:
            print("\n🚨 RED FLAGS:")
            for flag in result["red_flags"]:
                print(f"  - {flag}")
        
        if result["amber_flags"]:
            print("\n⚠️ WARNINGS:")
            for flag in result["amber_flags"]:
                print(f"  - {flag}")
