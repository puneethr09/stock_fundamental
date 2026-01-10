"""
Industrial Materials Sector Strategy - Chapter 24

Implements Pat Dorsey's analysis framework for industrial materials companies.

Per Dorsey's Five Rules:
- Industrial materials are often commoditized and cyclical
- Low-cost producers have the best moats
- Industry consolidation improves pricing power
- Strong balance sheets essential for cycle survival
"""

from src.dorsey_sectors.base import SectorStrategy


class IndustrialStrategy(SectorStrategy):
    """
    Implements Chapter 24: Industrial Materials.
    
    Per Pat Dorsey's Five Rules:
    - Industrial materials face demand volatility and commodity pricing
    - Moats come from being the low-cost producer or industry consolidation
    - Cyclical earnings require averaging over full cycles
    - Strong balance sheets survive commodity downturns
    
    Key Metrics:
    - Fixed Asset Turnover (capital efficiency)
    - Price-to-Sales (useful for volatile earnings)
    - Book Value Growth (value creation over cycles)
    - Debt/Capital (cycle survival)
    - Average margins over multiple years
    
    Note: Energy (Ch 25) and Utilities (Ch 26) now have separate strategies.
    This strategy focuses on industrial materials and basic materials.
    """
    
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Industrial Materials"
        
    def analyze(self):
        insights = []
        moat_indicators = []
        red_flags = []
        
        # --- 1. Fixed Asset Turnover (Capital Efficiency) ---
        rev = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Total Revenue", 0)
        ppe = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Net PPE", 0)
        
        if ppe and ppe > 0 and rev:
            asset_turnover = rev / ppe
            
            if asset_turnover > 3:
                turn_judgment = "Asset Light"
                moat_indicators.append("High asset turnover suggests efficient operations")
            elif asset_turnover > 1.5:
                turn_judgment = "Good Efficiency"
            elif asset_turnover > 0.8:
                turn_judgment = "Capital Intensive"
            else:
                turn_judgment = "Very Capital Intensive"
                
            insights.append({
                "metric": "Fixed Asset Turnover",
                "value": f"{asset_turnover:.2f}x",
                "judgment": turn_judgment,
                "context": "Per Dorsey: High fixed costs = capital intensity. Look for scale advantages."
            })
        
        # --- 2. Operating Margin (Cost Position) ---
        op_income = self.data_engine.get_financials_safe(
            self.data_engine.financials, "Operating Income", 0)
        
        if op_income and rev and rev > 0:
            op_margin = (op_income / rev) * 100
            
            if op_margin > 15:
                margin_judgment = "Strong - Possible Low-Cost Producer"
                moat_indicators.append("High operating margin suggests low-cost position")
            elif op_margin > 10:
                margin_judgment = "Average"
            elif op_margin > 5:
                margin_judgment = "Thin"
            else:
                margin_judgment = "Weak"
                red_flags.append("Low margins - vulnerable to commodity downturn")
                
            insights.append({
                "metric": "Operating Margin",
                "value": f"{op_margin:.1f}%",
                "judgment": margin_judgment,
                "context": "Per Dorsey: Low-cost producers maintain margins through cycles."
            })
        
        # --- 3. Average Operating Margin (Cycle View) ---
        # Calculate average margin over available years
        op_margins = []
        for year in range(3):
            op_inc = self.data_engine.get_financials_safe(
                self.data_engine.financials, "Operating Income", year)
            rev_y = self.data_engine.get_financials_safe(
                self.data_engine.financials, "Total Revenue", year)
            if op_inc and rev_y and rev_y > 0:
                op_margins.append((op_inc / rev_y) * 100)
        
        if len(op_margins) >= 2:
            avg_margin = sum(op_margins) / len(op_margins)
            margin_volatility = max(op_margins) - min(op_margins)
            
            insights.append({
                "metric": "Avg Operating Margin (3yr)",
                "value": f"{avg_margin:.1f}%",
                "judgment": "Stable" if margin_volatility < 5 else "Volatile",
                "context": "Cyclical industries: use average earnings over full cycle."
            })
            
            if margin_volatility > 10:
                red_flags.append(f"High margin volatility ({margin_volatility:.0f}%) - typical of cyclical business")
        
        # --- 4. Debt to Capital (Cycle Survival) ---
        total_debt = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Total Debt", 0)
        total_equity = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Stockholders Equity", 0)
        
        if total_debt and total_equity and total_equity > 0:
            debt_to_capital = (total_debt / (total_debt + total_equity)) * 100
            
            if debt_to_capital < 30:
                debt_judgment = "Conservative - Cycle Resilient"
                moat_indicators.append("Strong balance sheet can survive commodity downturns")
            elif debt_to_capital < 45:
                debt_judgment = "Moderate"
            else:
                debt_judgment = "High - Cycle Risk"
                red_flags.append("High leverage in cyclical industry is risky")
                
            insights.append({
                "metric": "Debt to Capital",
                "value": f"{debt_to_capital:.1f}%",
                "judgment": debt_judgment,
                "context": "Per Dorsey: Cyclical firms need <40% debt to survive downturns."
            })
        
        # --- 5. Book Value Growth (Value Creation) ---
        eq_curr = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Stockholders Equity", 0)
        eq_old = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Stockholders Equity", 2)
        
        if eq_curr and eq_old and eq_old > 0:
            bv_growth = ((eq_curr - eq_old) / eq_old) * 100
            bv_cagr = ((eq_curr / eq_old) ** 0.5 - 1) * 100
            
            if bv_cagr > 10:
                bv_judgment = "Strong Value Creation"
            elif bv_cagr > 5:
                bv_judgment = "Healthy"
            elif bv_cagr > 0:
                bv_judgment = "Slow"
            else:
                bv_judgment = "Destroying Value"
                red_flags.append("Negative book value growth - company destroying shareholder value")
                
            insights.append({
                "metric": "Book Value CAGR (2yr)",
                "value": f"{bv_cagr:.1f}%",
                "judgment": bv_judgment,
                "context": "For cyclicals, Book Value growth > Inflation indicates value creation."
            })
        
        # --- 6. Price to Sales (Cyclical Valuation) ---
        market_cap = self.data_engine.info.get("marketCap", 0)
        
        if market_cap and rev and rev > 0:
            ps_ratio = market_cap / rev
            
            if ps_ratio < 0.5:
                ps_judgment = "Deep Value"
            elif ps_ratio < 1.0:
                ps_judgment = "Attractive"
            elif ps_ratio < 2.0:
                ps_judgment = "Fair"
            else:
                ps_judgment = "Premium"
                
            insights.append({
                "metric": "Price/Sales",
                "value": f"{ps_ratio:.2f}x",
                "judgment": ps_judgment,
                "context": "Per Dorsey: P/S useful for cyclicals with volatile earnings. <1x is generally attractive."
            })
        
        # --- 7. Dividend Yield (Income Component) ---
        div_yield = self.data_engine.info.get("dividendYield", 0)
        
        if div_yield:
            yield_pct = div_yield * 100
            insights.append({
                "metric": "Dividend Yield",
                "value": f"{yield_pct:.1f}%",
                "judgment": "Income Attractive" if yield_pct > 3 else "Low",
                "context": "Cyclical industrials often pay dividends. Verify sustainability through cycles."
            })
        
        # --- 8. Industry Consolidation Note ---
        insights.append({
            "metric": "Industry Consolidation",
            "value": "Manual Assessment",
            "judgment": "ℹ️ Moat Indicator",
            "context": "Per Dorsey: Industries with Top 3 players >50% market share have better pricing power."
        })
        
        return {
            "sector": self.sector_name,
            "chapter_reference": "Chapter 24: Industrial Materials",
            "insights": insights,
            "moat_indicators": moat_indicators if moat_indicators else None,
            "red_flags": red_flags if red_flags else None,
            "dorsey_wisdom": "The more a product becomes a commodity, the more a firm has to rely on having the lowest costs in its industry. Look for industry consolidation and low-cost producers.",
            "key_questions": [
                "Is this company a low-cost producer?",
                "Is the industry consolidated or fragmented?",
                "Can the company survive a major commodity downturn?",
                "What is the normalized earning power across a full cycle?"
            ]
        }
