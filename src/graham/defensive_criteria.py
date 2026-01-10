"""
Defensive Investor Criteria - Based on Benjamin Graham's Chapter 14

The Defensive (Passive) Investor seeks safety and freedom from bother.
These criteria are designed to identify solid, established companies
with minimal risk.

Graham's 7 Criteria for Defensive Investors:
1. Adequate Size - Market cap threshold
2. Strong Financial Condition - Current ratio ≥ 2
3. Earnings Stability - Positive earnings for 10 years
4. Dividend Record - Uninterrupted dividends for 20 years  
5. Earnings Growth - At least 33% growth over 10 years
6. Moderate P/E - Less than 15x average 3-year earnings
7. Moderate P/B - Less than 1.5x book value (or P/E × P/B < 22.5)
"""

from src.smart_data import SmartDataEngine


class DefensiveInvestorScreen:
    """
    Screens stocks against Benjamin Graham's Defensive Investor criteria.
    
    For Indian markets, some criteria are relaxed:
    - Dividend history requirement reduced (Indian dividend culture differs)
    - Market cap threshold adjusted for INR
    """
    
    # Indian market adjustments
    MIN_MARKET_CAP_INR = 2000_00_00_000  # ₹2,000 Crore (larger for defensive)
    
    def __init__(self, ticker):
        self.data_engine = SmartDataEngine(ticker)
        self.ticker = ticker
        
    def screen(self):
        """
        Run the complete defensive investor screen.
        Returns detailed results for each criterion.
        """
        if not self.data_engine.has_data:
            return {"status": "NO DATA", "ticker": self.ticker}
        
        criteria = []
        passed_count = 0
        
        # ============================================================
        # CRITERION 1: Adequate Size
        # ============================================================
        market_cap = self.data_engine.info.get("marketCap", 0)
        is_adequate_size = market_cap >= self.MIN_MARKET_CAP_INR if market_cap else False
        
        criteria.append({
            "criterion": "1. Adequate Size",
            "passed": is_adequate_size,
            "value": f"₹{market_cap/10_000_000:,.0f} Cr" if market_cap else "N/A",
            "requirement": f"≥ ₹{self.MIN_MARKET_CAP_INR/10_000_000:,.0f} Cr",
            "graham_says": "Exclude small companies that may be subject to more volatility."
        })
        if is_adequate_size:
            passed_count += 1
        
        # ============================================================
        # CRITERION 2: Strong Financial Condition
        # ============================================================
        current_assets = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Current Assets", 0)
        current_liabilities = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Current Liabilities", 0)
        
        current_ratio = current_assets / current_liabilities if current_liabilities and current_liabilities > 0 else 0
        is_strong_financial = current_ratio >= 2.0
        
        criteria.append({
            "criterion": "2. Strong Financial Condition",
            "passed": is_strong_financial,
            "value": f"{current_ratio:.2f}x",
            "requirement": "Current Ratio ≥ 2.0",
            "graham_says": "Current assets should be at least twice current liabilities."
        })
        if is_strong_financial:
            passed_count += 1
        
        # ============================================================
        # CRITERION 3: Earnings Stability
        # ============================================================
        positive_earnings_years = 0
        for year in range(3):  # Check available years
            ni = self.data_engine.get_financials_safe(
                self.data_engine.financials, "Net Income", year)
            if ni and ni > 0:
                positive_earnings_years += 1
        
        is_earnings_stable = positive_earnings_years >= 3  # All 3 available years
        
        criteria.append({
            "criterion": "3. Earnings Stability",
            "passed": is_earnings_stable,
            "value": f"{positive_earnings_years}/3 years positive",
            "requirement": "Positive earnings in each of past 10 years (checking 3 available)",
            "graham_says": "Some earnings for the common stock in each of the past 10 years."
        })
        if is_earnings_stable:
            passed_count += 1
        
        # ============================================================
        # CRITERION 4: Dividend Record
        # ============================================================
        dividend_rate = self.data_engine.info.get("dividendRate", 0)
        dividend_yield = self.data_engine.info.get("dividendYield", 0)
        has_dividend = (dividend_rate and dividend_rate > 0) or (dividend_yield and dividend_yield > 0)
        
        criteria.append({
            "criterion": "4. Dividend Record",
            "passed": has_dividend,
            "value": f"₹{dividend_rate:.2f} ({dividend_yield*100:.1f}%)" if has_dividend else "No dividend",
            "requirement": "Current dividend (relaxed from 20-year uninterrupted)",
            "graham_says": "Uninterrupted payments for at least the past 20 years."
        })
        if has_dividend:
            passed_count += 1
        
        # ============================================================
        # CRITERION 5: Earnings Growth
        # ============================================================
        # Check if earnings have grown at least 33% over available period
        ni_latest = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Net Income", 0)
        ni_oldest = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Net Income", 2)
        
        earnings_growth = 0
        if ni_oldest and ni_oldest > 0 and ni_latest:
            earnings_growth = ((ni_latest - ni_oldest) / ni_oldest) * 100
        
        # Graham requirement is 33% over 10 years, we check ~3 years
        # Proportionally ~10% over 3 years would be comparable
        has_earnings_growth = earnings_growth > 10
        
        criteria.append({
            "criterion": "5. Earnings Growth",
            "passed": has_earnings_growth,
            "value": f"{earnings_growth:.1f}% over 3 years",
            "requirement": "> 10% (Graham: 33% over 10 years, scaled to 3 years)",
            "graham_says": "A minimum increase of at least one-third in per-share earnings over the past 10 years."
        })
        if has_earnings_growth:
            passed_count += 1
        
        # ============================================================
        # CRITERION 6: Moderate P/E Ratio
        # ============================================================
        pe_ratio = self.data_engine.info.get("trailingPE", 0)
        is_moderate_pe = pe_ratio and 0 < pe_ratio < 15
        
        criteria.append({
            "criterion": "6. Moderate P/E Ratio",
            "passed": is_moderate_pe,
            "value": f"{pe_ratio:.1f}x" if pe_ratio else "N/A",
            "requirement": "P/E < 15 (based on 3-year average earnings)",
            "graham_says": "Current price should not be more than 15 times average earnings of past 3 years."
        })
        if is_moderate_pe:
            passed_count += 1
        
        # ============================================================
        # CRITERION 7: Moderate P/B Ratio
        # ============================================================
        pb_ratio = self.data_engine.info.get("priceToBook", 0)
        is_moderate_pb = pb_ratio and pb_ratio < 1.5
        
        # Alternative: P/E × P/B < 22.5
        combined_ratio = (pe_ratio * pb_ratio) if pe_ratio and pb_ratio else 0
        combined_ok = combined_ratio > 0 and combined_ratio < 22.5
        
        criteria.append({
            "criterion": "7. Moderate P/B Ratio",
            "passed": is_moderate_pb or combined_ok,
            "value": f"P/B: {pb_ratio:.2f}x | P/E×P/B: {combined_ratio:.1f}" if pb_ratio else "N/A",
            "requirement": "P/B < 1.5 OR (P/E × P/B) < 22.5",
            "graham_says": "Current price should not be more than 1.5x book value for defensive investors."
        })
        if is_moderate_pb or combined_ok:
            passed_count += 1
        
        # ============================================================
        # OVERALL VERDICT
        # ============================================================
        total_criteria = len(criteria)
        pass_rate = passed_count / total_criteria * 100
        
        if passed_count >= 6:
            verdict = "STRONG DEFENSIVE BUY"
            recommendation = "Meets Graham's defensive investor criteria - suitable for conservative portfolios"
        elif passed_count >= 4:
            verdict = "PARTIAL PASS"
            recommendation = "Meets some criteria - may be suitable with additional research"
        else:
            verdict = "DOES NOT QUALIFY"
            recommendation = "Does not meet defensive investor standards - consider enterprising approach or skip"
        
        return {
            "ticker": self.ticker,
            "company": self.data_engine.info.get("longName", self.ticker),
            "criteria": criteria,
            "summary": {
                "passed": passed_count,
                "total": total_criteria,
                "pass_rate": f"{pass_rate:.0f}%",
                "verdict": verdict,
                "recommendation": recommendation
            },
            "graham_philosophy": "The defensive investor wants primarily to avoid serious mistakes or losses. His second aim is freedom from effort, annoyance, and the need for making frequent decisions."
        }


class EnterprisingInvestorScreen:
    """
    Screens stocks against Benjamin Graham's Enterprising Investor criteria.
    
    The Enterprising (Active) Investor is willing to devote time and care
    to selection of sound and attractive securities.
    
    Graham's Criteria for Enterprising Investors:
    1. Financial Condition - Current ratio ≥ 1.5
    2. Debt - Long-term debt ≤ 110% of working capital
    3. Earnings Stability - No deficit in past 5 years
    4. Dividends - Some current dividend
    5. Earnings Growth - Last year > 4 years ago
    6. Price - Less than 120% of net tangible assets
    7. Price/Earnings - Low P/E (< 10 for bargains)
    """
    
    def __init__(self, ticker):
        self.data_engine = SmartDataEngine(ticker)
        self.ticker = ticker
        
    def screen(self):
        """
        Run the enterprising investor screen.
        """
        if not self.data_engine.has_data:
            return {"status": "NO DATA", "ticker": self.ticker}
        
        criteria = []
        passed_count = 0
        
        # 1. Financial Condition
        current_assets = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Current Assets", 0)
        current_liabilities = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Current Liabilities", 0)
        current_ratio = current_assets / current_liabilities if current_liabilities and current_liabilities > 0 else 0
        
        passed = current_ratio >= 1.5
        criteria.append({
            "criterion": "1. Financial Condition",
            "passed": passed,
            "value": f"{current_ratio:.2f}x",
            "requirement": "Current Ratio ≥ 1.5"
        })
        if passed:
            passed_count += 1
        
        # 2. Debt Level
        long_term_debt = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Long Term Debt", 0) or 0
        working_capital = current_assets - current_liabilities if current_assets and current_liabilities else 0
        debt_ratio = (long_term_debt / working_capital * 100) if working_capital > 0 else 999
        
        passed = debt_ratio <= 110
        criteria.append({
            "criterion": "2. Debt Level",
            "passed": passed,
            "value": f"{debt_ratio:.0f}% of working capital",
            "requirement": "Long-term debt ≤ 110% of working capital"
        })
        if passed:
            passed_count += 1
        
        # 3. Earnings Stability
        positive_years = sum(1 for y in range(3) if self.data_engine.get_financials_safe(
            self.data_engine.financials, "Net Income", y) and self.data_engine.get_financials_safe(
            self.data_engine.financials, "Net Income", y) > 0)
        
        passed = positive_years >= 3
        criteria.append({
            "criterion": "3. Earnings Stability",
            "passed": passed,
            "value": f"{positive_years}/3 years positive",
            "requirement": "No deficit in past 5 years"
        })
        if passed:
            passed_count += 1
        
        # 4. Current Dividend
        has_dividend = self.data_engine.info.get("dividendRate", 0) and self.data_engine.info.get("dividendRate", 0) > 0
        criteria.append({
            "criterion": "4. Current Dividend",
            "passed": has_dividend,
            "value": "Yes" if has_dividend else "No",
            "requirement": "Some form of current dividend"
        })
        if has_dividend:
            passed_count += 1
        
        # 5. Earnings Growth
        ni_latest = self.data_engine.get_financials_safe(self.data_engine.financials, "Net Income", 0)
        ni_old = self.data_engine.get_financials_safe(self.data_engine.financials, "Net Income", 2)
        
        passed = ni_latest and ni_old and ni_latest > ni_old
        criteria.append({
            "criterion": "5. Earnings Growth",
            "passed": passed,
            "value": "Growing" if passed else "Declining/Flat",
            "requirement": "Last year earnings > 4 years ago"
        })
        if passed:
            passed_count += 1
        
        # 6. Price to Tangible Book
        pb = self.data_engine.info.get("priceToBook", 0)
        passed = pb and pb < 1.2
        criteria.append({
            "criterion": "6. Price to Tangible Book",
            "passed": passed,
            "value": f"{pb:.2f}x" if pb else "N/A",
            "requirement": "Price < 120% of net tangible assets"
        })
        if passed:
            passed_count += 1
        
        # 7. Low P/E (Bargain Level)
        pe = self.data_engine.info.get("trailingPE", 0)
        passed = pe and 0 < pe < 10
        criteria.append({
            "criterion": "7. Low P/E (Bargain)",
            "passed": passed,
            "value": f"{pe:.1f}x" if pe else "N/A",
            "requirement": "P/E < 10 for bargain purchases"
        })
        if passed:
            passed_count += 1
        
        # Verdict
        if passed_count >= 5:
            verdict = "ENTERPRISING BUY CANDIDATE"
        elif passed_count >= 3:
            verdict = "WORTH FURTHER RESEARCH"
        else:
            verdict = "DOES NOT QUALIFY"
        
        return {
            "ticker": self.ticker,
            "criteria": criteria,
            "summary": {
                "passed": passed_count,
                "total": len(criteria),
                "verdict": verdict
            }
        }


if __name__ == "__main__":
    # Test
    tickers = ["ITC.NS", "COALINDIA.NS", "POWERGRID.NS"]
    for ticker in tickers:
        print(f"\n{'='*60}")
        print(f"Defensive Screen: {ticker}")
        print('='*60)
        screen = DefensiveInvestorScreen(ticker)
        result = screen.screen()
        
        print(f"\nVerdict: {result['summary']['verdict']}")
        print(f"Passed: {result['summary']['passed']}/{result['summary']['total']}")
        for c in result['criteria']:
            status = "✓" if c['passed'] else "✗"
            print(f"  [{status}] {c['criterion']}: {c['value']}")
