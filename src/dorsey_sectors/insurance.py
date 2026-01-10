"""
Dorsey Chapter 18: Asset Management and Insurance

This module implements sector-specific analysis for insurance companies and
asset management firms based on Pat Dorsey's Five Rules methodology.
"""

from src.dorsey_sectors.base import SectorStrategy


class InsuranceStrategy(SectorStrategy):
    """
    Implements Chapter 18: Insurance (Life, P&C, Health).
    
    Per Pat Dorsey's Five Rules:
    - Insurance is cyclical, influenced by pricing decisions and investment returns
    - Insurers may face less pressure to underwrite profitably during high market returns
    - Focus on underwriting discipline and float management
    
    Key Metrics:
    - Combined Ratio (Loss Ratio + Expense Ratio) - should be < 100%
    - Investment Returns - float management effectiveness
    - Premium Growth Rate - market share and pricing power
    - Reserve Adequacy - conservative accounting indicator
    - ROE - must exceed cost of equity consistently
    """
    
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Insurance"
        
    def analyze(self):
        insights = []
        red_flags = []
        
        # --- 1. ROE (Critical for Insurance - Must exceed cost of equity) ---
        ni = self.data_engine.get_financials_safe(self.data_engine.financials, "Net Income", 0)
        eq = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Stockholders Equity", 0)
        roe = (ni / eq) * 100 if eq > 0 else 0
        
        roe_judgment = "Excellent" if roe > 18 else ("Good" if roe > 14 else ("Acceptable" if roe > 10 else "Weak"))
        insights.append({
            "metric": "Return on Equity (ROE)",
            "value": f"{roe:.1f}%",
            "judgment": roe_judgment,
            "context": "Per Dorsey: Insurance ROE must consistently exceed cost of equity (typically 12-14%). Strong insurers achieve 15%+."
        })
        
        if roe < 10 and roe > 0:
            red_flags.append("ROE below 10% - insurer may not be creating shareholder value")
        
        # --- 2. Price to Book (Valuation for Insurers) ---
        pb = self.data_engine.info.get("priceToBook", 0)
        pb_judgment = "Attractive" if pb < 1.5 else ("Fair" if pb < 2.5 else ("Premium" if pb < 4.0 else "Expensive"))
        insights.append({
            "metric": "Price to Book (P/B)",
            "value": f"{pb:.2f}x" if pb else "N/A",
            "judgment": pb_judgment,
            "context": "Insurance companies, like banks, are valued on book value. < 2x is generally fair for quality insurers."
        })
        
        # --- 3. Premium/Revenue Growth (Market Position) ---
        total_rev_curr = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
        total_rev_prev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 1)
        
        if total_rev_prev > 0 and total_rev_curr > 0:
            premium_growth = ((total_rev_curr - total_rev_prev) / total_rev_prev) * 100
            growth_judgment = "Strong" if premium_growth > 15 else ("Healthy" if premium_growth > 8 else ("Moderate" if premium_growth > 3 else "Slow"))
            insights.append({
                "metric": "Premium/Revenue Growth",
                "value": f"{premium_growth:.1f}%",
                "judgment": growth_judgment,
                "context": "Sustainable premium growth of 5-15% is healthy. Very high growth may indicate aggressive pricing."
            })
            
            if premium_growth > 30:
                red_flags.append("Very high premium growth (>30%) - may indicate aggressive/risky underwriting")
        
        # --- 4. Operating Margin (Profitability Proxy) ---
        op_income = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", 0)
        if total_rev_curr > 0 and op_income != 0:
            op_margin = (op_income / total_rev_curr) * 100
            margin_judgment = "Strong" if op_margin > 15 else ("Good" if op_margin > 10 else ("Thin" if op_margin > 5 else "Weak"))
            insights.append({
                "metric": "Operating Margin",
                "value": f"{op_margin:.1f}%",
                "judgment": margin_judgment,
                "context": "Indicates underwriting profitability plus investment income. > 12% is generally healthy."
            })
        
        # --- 5. Combined Ratio Guidance (Manual Check) ---
        insights.append({
            "metric": "Combined Ratio (P&C Insurance)",
            "value": "Manual Verification Required",
            "judgment": "⚠️ Essential Metric",
            "context": "Combined Ratio = Loss Ratio + Expense Ratio. < 100% means underwriting profit. < 95% is excellent. Check company's annual report."
        })
        
        # --- 6. Investment Portfolio Quality (Manual Check) ---
        insights.append({
            "metric": "Investment Portfolio Quality",
            "value": "Manual Verification Required",
            "judgment": "ℹ️ Important for Float",
            "context": "Review investment portfolio composition. Conservative bond-heavy portfolio is safer. Check for duration mismatch with liabilities."
        })
        
        # --- 7. Solvency/Capital Check ---
        total_assets = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Total Assets", 0)
        total_liab = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Total Liabilities Net Minority Interest", 0)
        
        if total_assets > 0 and total_liab > 0:
            solvency_ratio = ((total_assets - total_liab) / total_liab) * 100
            insights.append({
                "metric": "Solvency Ratio Proxy",
                "value": f"{solvency_ratio:.1f}%",
                "judgment": "Strong" if solvency_ratio > 50 else ("Adequate" if solvency_ratio > 25 else "Watch"),
                "context": "Higher solvency indicates stronger capital buffer. Check regulatory solvency ratio in annual report."
            })
        
        return {
            "sector": self.sector_name,
            "chapter_reference": "Chapter 18: Asset Management and Insurance",
            "insights": insights,
            "red_flags": red_flags if red_flags else None,
            "manual_checks": [
                "Verify Combined Ratio from annual report (for P&C insurers)",
                "Check Medical Loss Ratio (for health insurers) - typically 80-85%",
                "Review investment portfolio composition and duration",
                "Check Solvency Ratio as per IRDAI requirements (should be > 150%)",
                "Analyze claim settlement ratio for life insurers"
            ]
        }


class AssetManagementStrategy(SectorStrategy):
    """
    Implements Chapter 18: Asset Management.
    
    Per Pat Dorsey's Five Rules:
    - Asset managers benefit from scale - larger AUM means better margins
    - Key focus on AUM growth, fee rates, and performance vs benchmark
    - Switching costs can create moats if performance is consistent
    
    Key Metrics:
    - AUM Growth - Scale building indicator
    - Revenue/AUM (Fee Rate) - Pricing power
    - Operating Margin - Scale economics
    - Performance vs Benchmark - Value creation for clients
    """
    
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Asset Management"
        
    def analyze(self):
        insights = []
        red_flags = []
        
        # --- 1. ROE (Profitability Check) ---
        ni = self.data_engine.get_financials_safe(self.data_engine.financials, "Net Income", 0)
        eq = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Stockholders Equity", 0)
        roe = (ni / eq) * 100 if eq > 0 else 0
        
        roe_judgment = "Excellent" if roe > 20 else ("Good" if roe > 15 else ("Fair" if roe > 10 else "Weak"))
        insights.append({
            "metric": "Return on Equity (ROE)",
            "value": f"{roe:.1f}%",
            "judgment": roe_judgment,
            "context": "Asset managers are capital-light businesses. Good ones achieve ROE > 15%."
        })
        
        # --- 2. Revenue Growth (AUM Proxy) ---
        total_rev_curr = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
        total_rev_prev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 1)
        
        if total_rev_prev > 0 and total_rev_curr > 0:
            rev_growth = ((total_rev_curr - total_rev_prev) / total_rev_prev) * 100
            growth_judgment = "Strong" if rev_growth > 15 else ("Good" if rev_growth > 8 else ("Moderate" if rev_growth > 2 else "Slow"))
            insights.append({
                "metric": "Revenue Growth (AUM Proxy)",
                "value": f"{rev_growth:.1f}%",
                "judgment": growth_judgment,
                "context": "Revenue growth indicates AUM growth + fee stability. > 10% is healthy in normal markets."
            })
        
        # --- 3. Operating Margin (Scale Benefits) ---
        op_income = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", 0)
        if total_rev_curr > 0 and op_income != 0:
            op_margin = (op_income / total_rev_curr) * 100
            margin_judgment = "Excellent" if op_margin > 35 else ("Good" if op_margin > 25 else ("Acceptable" if op_margin > 15 else "Low"))
            insights.append({
                "metric": "Operating Margin",
                "value": f"{op_margin:.1f}%",
                "judgment": margin_judgment,
                "context": "Asset managers should have high margins (30%+) due to scale economics. Low margins suggest lack of scale or high costs."
            })
            
            if op_margin < 20 and op_margin > 0:
                red_flags.append("Operating margin below 20% - may lack scale benefits")
        
        # --- 4. Net Margin (Bottom-line Efficiency) ---
        if total_rev_curr > 0 and ni != 0:
            net_margin = (ni / total_rev_curr) * 100
            insights.append({
                "metric": "Net Profit Margin",
                "value": f"{net_margin:.1f}%",
                "judgment": "Strong" if net_margin > 25 else ("Good" if net_margin > 15 else "Moderate"),
                "context": "Capital-light business should convert significant revenue to profit. > 20% is good."
            })
        
        # --- 5. FCF Generation ---
        cfo = self.data_engine.get_financials_safe(self.data_engine.cashflow, "Operating Cash Flow", 0)
        capex = abs(self.data_engine.get_financials_safe(self.data_engine.cashflow, "Capital Expenditure", 0))
        fcf = cfo - capex if cfo else 0
        
        if fcf != 0 and total_rev_curr > 0:
            fcf_margin = (fcf / total_rev_curr) * 100
            insights.append({
                "metric": "Free Cash Flow Margin",
                "value": f"{fcf_margin:.1f}%",
                "judgment": "Excellent" if fcf_margin > 25 else ("Good" if fcf_margin > 15 else "Moderate"),
                "context": "Asset managers are low-CapEx businesses. FCF should be close to net income."
            })
        
        # --- 6. AUM Guidance (Manual) ---
        insights.append({
            "metric": "AUM Growth & Composition",
            "value": "Manual Verification Required",
            "judgment": "ℹ️ Key Metric",
            "context": "Check AUM growth breakdown: Market appreciation vs Net inflows. Net inflows indicate competitive strength."
        })
        
        return {
            "sector": self.sector_name,
            "chapter_reference": "Chapter 18: Asset Management and Insurance",
            "insights": insights,
            "red_flags": red_flags if red_flags else None,
            "manual_checks": [
                "Verify AUM growth from investor presentations",
                "Check net inflows vs market appreciation in AUM growth",
                "Review expense ratio trends for mutual fund schemes",
                "Analyze performance track record vs benchmark",
                "Check client retention/redemption rates"
            ]
        }
