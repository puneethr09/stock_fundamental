"""
Moat Analysis - Chapter 3: Economic Moats

Implements Pat Dorsey's framework for identifying companies with
durable competitive advantages (economic moats).

Per Dorsey, there are 4 primary sources of economic moats:
1. Intangible Assets (brands, patents, licenses)
2. Switching Costs (customer lock-in)
3. Network Effects (value increases with users)
4. Cost Advantages (process or scale-based)
"""

from src.smart_data import SmartDataEngine
import numpy as np


class MoatAnalyzer:
    """
    Implements Moat Analysis (Chapter 3).
    
    Evaluates both quantitative evidence of a moat (ROIC, margins) and
    attempts to identify the likely source(s) of competitive advantage.
    
    Per Pat Dorsey's Four Sources of Economic Moats:
    1. Intangible Assets - Brands that increase willingness to pay, patents, licenses
    2. Switching Costs - Monetary/psychological costs that lock in customers
    3. Network Effects - Value increases as more users join
    4. Cost Advantages - Process-based (can be copied) or scale-based (durable)
    """
    
    def __init__(self, ticker):
        self.data_engine = SmartDataEngine(ticker)
        self.ticker = ticker
        
    def analyze_moat(self):
        """
        Determines if the company has a Wide, Narrow, or No Moat.
        Also identifies likely sources of the moat based on available data.
        """
        if not self.data_engine.has_data:
            return {"moat_rating": "UNKNOWN", "details": [], "moat_sources": []}
            
        details = []
        moat_sources = []
        moat_score = 0  # Accumulate evidence of moat
        
        # ============================================================
        # SECTION 1: ROIC TEST (The Gold Standard for Moat Detection)
        # ============================================================
        # Rule: Wide Moat = ROIC > 15% for 10+ years
        # Rule: Narrow Moat = ROIC > 15% for 5-10 years
        
        roic_0 = self.data_engine.calculate_roic(0)
        roic_1 = self.data_engine.calculate_roic(1)
        roic_2 = self.data_engine.calculate_roic(2)
        
        roic_values = [r for r in [roic_0, roic_1, roic_2] if r is not None and r != 0]
        avg_roic = sum(roic_values) / len(roic_values) if roic_values else 0
        
        # Check ROIC consistency (all years > 12%)
        roic_consistent = all(r > 12 for r in roic_values) if len(roic_values) >= 2 else False
        
        if avg_roic > 15:
            roic_rating = "Excellent"
            moat_score += 3
        elif avg_roic > 12:
            roic_rating = "Good"
            moat_score += 2
        elif avg_roic > 8:
            roic_rating = "Fair"
            moat_score += 1
        else:
            roic_rating = "Poor"
            
        details.append({
            "metric": "Avg ROIC (3yr)",
            "value": f"{avg_roic:.1f}%",
            "rating": roic_rating,
            "comment": "ROIC > 15% is strong evidence of a moat. Consistency across years is key."
        })
        
        if roic_consistent:
            details.append({
                "metric": "ROIC Consistency",
                "value": "Consistent",
                "rating": "Strong",
                "comment": "ROIC has remained above 12% across all available years."
            })
            moat_score += 1
        
        # ============================================================
        # SECTION 2: GROSS MARGIN ANALYSIS (Pricing Power / Brand)
        # ============================================================
        gm_0 = self.data_engine.info.get("grossMargins", 0) * 100 if self.data_engine.info.get("grossMargins") else 0
        
        # Fallback: Calculate from financials
        if gm_0 == 0:
            rev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
            cost = self.data_engine.get_financials_safe(self.data_engine.financials, "Cost Of Revenue", 0)
            if rev > 0:
                gm_0 = ((rev - cost) / rev) * 100
        
        # Calculate margin stability (3-year trend)
        gm_values = []
        for year in range(3):
            rev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", year)
            cost = self.data_engine.get_financials_safe(self.data_engine.financials, "Cost Of Revenue", year)
            if rev > 0:
                gm_values.append(((rev - cost) / rev) * 100)
        
        margin_stable = False
        if len(gm_values) >= 2:
            margin_std = np.std(gm_values)
            margin_stable = margin_std < 3  # Less than 3% standard deviation
        
        if gm_0 > 50:
            gm_rating = "Exceptional"
            moat_score += 2
            moat_sources.append({
                "source": "Intangible Assets (Brand/Patent)",
                "evidence": f"High gross margin ({gm_0:.1f}%) suggests strong pricing power",
                "strength": "Strong"
            })
        elif gm_0 > 35:
            gm_rating = "High"
            moat_score += 1
        else:
            gm_rating = "Average"
            
        details.append({
            "metric": "Gross Margin (Latest)",
            "value": f"{gm_0:.1f}%",
            "rating": gm_rating,
            "comment": "High gross margins (>40%) indicate pricing power, brand strength, or patent protection."
        })
        
        if margin_stable and len(gm_values) >= 2:
            details.append({
                "metric": "Margin Stability (3yr)",
                "value": "Stable",
                "rating": "Positive",
                "comment": "Stable margins suggest durable competitive advantage."
            })
            moat_score += 1
        
        # ============================================================
        # SECTION 3: FREE CASH FLOW CONVERSION (Earnings Quality)
        # ============================================================
        # Rule: FCF/Sales > 5% is evidence of moat (per Dorsey)
        fcf = self.data_engine.calculate_fcf(0)
        rev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
        
        if rev > 0 and fcf:
            fcf_margin = (fcf / rev) * 100
            if fcf_margin > 15:
                fcf_rating = "Excellent"
                moat_score += 2
            elif fcf_margin > 8:
                fcf_rating = "Good"
                moat_score += 1
            elif fcf_margin > 5:
                fcf_rating = "Acceptable"
            else:
                fcf_rating = "Low"
                
            details.append({
                "metric": "FCF/Sales",
                "value": f"{fcf_margin:.1f}%",
                "rating": fcf_rating,
                "comment": "Per Dorsey: FCF/Sales > 5% indicates solid cash generation. > 10% is excellent."
            })
        
        # ============================================================
        # SECTION 4: SWITCHING COSTS PROXY
        # ============================================================
        # Proxy: Revenue stability (low volatility = sticky customers)
        rev_values = []
        for year in range(3):
            r = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", year)
            if r > 0:
                rev_values.append(r)
        
        if len(rev_values) >= 2:
            # Check for consistent revenue (not declining significantly)
            rev_growth_stable = all(rev_values[i] >= rev_values[i+1] * 0.95 for i in range(len(rev_values)-1))
            
            if rev_growth_stable:
                moat_sources.append({
                    "source": "Switching Costs (Customer Stickiness)",
                    "evidence": "Stable/growing revenue suggests customer retention",
                    "strength": "Moderate"
                })
                moat_score += 1
        
        # ============================================================
        # SECTION 5: COST ADVANTAGES PROXY
        # ============================================================
        # Proxy: Operating margin > industry norm with high asset turnover
        op_margin = self.data_engine.info.get("operatingMargins", 0) * 100 if self.data_engine.info.get("operatingMargins") else 0
        
        total_assets = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Total Assets", 0)
        if rev > 0 and total_assets > 0:
            asset_turnover = rev / total_assets
            
            if asset_turnover > 1.5 and op_margin > 15:
                moat_sources.append({
                    "source": "Cost Advantage (Efficiency)",
                    "evidence": f"High asset turnover ({asset_turnover:.2f}x) with good margins ({op_margin:.1f}%)",
                    "strength": "Strong"
                })
                moat_score += 1
            elif asset_turnover > 1.0:
                details.append({
                    "metric": "Asset Turnover",
                    "value": f"{asset_turnover:.2f}x",
                    "rating": "Good",
                    "comment": "Good asset efficiency may indicate operational moat"
                })
        
        # ============================================================
        # SECTION 6: NETWORK EFFECTS (Qualitative Note)
        # ============================================================
        # Hard to detect programmatically - add guidance
        sector = self.data_engine.info.get("sector", "").lower()
        industry = self.data_engine.info.get("industry", "").lower()
        
        if "technology" in sector or "internet" in industry or "platform" in industry:
            details.append({
                "metric": "Network Effects Potential",
                "value": "Possible",
                "rating": "Check Manually",
                "comment": "Tech/Platform companies may have network effects. Verify if value increases with more users."
            })
        
        # ============================================================
        # FINAL MOAT VERDICT
        # ============================================================
        if moat_score >= 8:
            moat_rating = "Wide Moat"
        elif moat_score >= 5:
            moat_rating = "Narrow Moat"
        elif moat_score >= 3:
            moat_rating = "Possible Moat"
        else:
            moat_rating = "No Moat"
            
        return {
            "moat_rating": moat_rating,
            "moat_score": moat_score,
            "moat_sources": moat_sources if moat_sources else [{"source": "None Identified", "evidence": "No clear moat source detected from available data", "strength": "N/A"}],
            "details": details,
            "dorsey_four_moats": {
                "intangible_assets": "High gross margins suggest brand/patent protection" if gm_0 > 40 else "Not evident from margins",
                "switching_costs": "Revenue stability suggests customer stickiness" if moat_score >= 3 else "Not evident",
                "network_effects": "Manual verification recommended for tech/platform businesses",
                "cost_advantages": "High asset turnover with good margins" if (asset_turnover > 1.2 if 'asset_turnover' in dir() else False) else "Not evident"
            }
        }


if __name__ == "__main__":
    # Test with various companies
    test_tickers = ["TCS.NS", "HDFCBANK.NS", "HINDUNILVR.NS"]
    for ticker in test_tickers:
        print(f"\n{'='*50}")
        print(f"Testing: {ticker}")
        print('='*50)
        m = MoatAnalyzer(ticker)
        result = m.analyze_moat()
        print(f"Moat Rating: {result['moat_rating']} (Score: {result.get('moat_score', 'N/A')})")
        print(f"Moat Sources: {result['moat_sources']}")
        for detail in result['details']:
            print(f"  - {detail['metric']}: {detail['value']} ({detail['rating']})")
