
from src.smart_data import SmartDataEngine
import numpy as np

class ValuationAnalyzer:
    """
    Implements Valuation Analysis (Chapters 9-10).
    1. Relative Valuation: P/E vs History.
    2. Intrinsic Value: Discounted Cash Flow (DCF).
    
    India-specific parameters (EY India Cost of Capital Survey 2024):
    - Base Cost of Equity: 14.2%
    - Equity Risk Premium: 7.25% (Incwert 2024)
    - Terminal Growth: 4.5% (India nominal GDP long-term)
    """
    
    # Sector-specific cost of equity adjustments (EY 2024 data)
    SECTOR_COE_ADJUSTMENTS = {
        "technology": 0.01,       # +1% for IT/Tech (higher risk)
        "consumer cyclical": 0.0,  # Base for FMCG/Consumer
        "consumer defensive": 0.0,
        "financial services": 0.0,  # Base for Banking
        "real estate": 0.02,       # +2% for Real Estate (high risk)
        "utilities": -0.01,        # -1% for Utilities (stable)
        "energy": 0.005,           # +0.5% for Energy
        "healthcare": 0.0,
        "industrials": 0.005,
        "basic materials": 0.01,
        "communication services": 0.005,
    }
    
    def __init__(self, ticker):
        self.data_engine = SmartDataEngine(ticker)
        # India-specific base parameters (EY India CoE Survey 2024)
        self.base_cost_of_equity = 0.142  # 14.2% average
        self.terminal_growth = 0.045  # 4.5% (India nominal GDP long-term)
        
    def _get_model_inputs(self):
        """
        Internal helper to get the correct FCF, Growth Rate, and Balance Sheet items
        based on the sector checks.
        """
        if not self.data_engine.has_data:
            return None
            
        # 1. Detect Sector
        sector = self.data_engine.info.get("sector", "").lower()
        industry = self.data_engine.info.get("industry", "").lower()
        
        is_financial = "financial" in sector or "bank" in industry or "insurance" in industry
        is_utility = "utility" in sector or "utilities" in industry or "energy" in sector
        is_telecom = "communication" in sector or "telecom" in industry
        
        model_type = "FCF (Standard)"
        current_fcf = 0.0
        equity_mode = False # If True, result is Equity Value (don't subtract debt)
        
        # 2. Select Model & Calculate Base Metric
        if is_financial:
            model_type = "FCFE (Financials)"
            equity_mode = True
            ni = self.data_engine.get_financials_safe(self.data_engine.financials, "Net Income", 0)
            capex = self.data_engine.get_financials_safe(self.data_engine.cashflow, "Capital Expenditur", 0)
            if capex == 0: capex = self.data_engine.get_financials_safe(self.data_engine.cashflow, "Capital Expenditure", 0)
            current_fcf = ni + capex # NI - Net CapEx
            
        elif (is_utility or is_telecom):
            # Check for High Growth Phase (Rev Growth > 15%).
            # If Growing fast, don't use DDM (undervalues). Use Net Income (Market pays for EPS).
            rev_curr = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
            rev_prev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 1)
            growth = 0
            if rev_prev > 0: growth = (rev_curr - rev_prev) / rev_prev
            
            raw_fcf = self.data_engine.calculate_fcf(0)
            
            # Logic:
            # 1. If Growth > 15% and FCF < 0: Use Net Income (FCFE Proxy).
            # 2. Else If FCF < 0 and Div Yield > 3%: Use DDM.
            # 3. Else: FCFF.
            
            if growth > 0.15 and raw_fcf < 0:
                model_type = "NI (High Growth Proxy)"
                equity_mode = True
                # Use Net Income
                current_fcf = self.data_engine.get_financials_safe(self.data_engine.financials, "Net Income", 0)
            
            elif raw_fcf < 0 and self.data_engine.info.get("dividendYield", 0) > 0.03:
                model_type = "DDM (High Yield)"
                equity_mode = True
                div_paid = abs(self.data_engine.get_financials_safe(self.data_engine.cashflow, "Cash Dividends Paid", 0))
                if div_paid == 0:
                     mkt_cap = self.data_engine.info.get("marketCap", 0)
                     div_paid = mkt_cap * self.data_engine.info.get("dividendYield", 0)
                current_fcf = div_paid
            else:
                current_fcf = raw_fcf
        else:
            current_fcf = self.data_engine.calculate_fcf(0)
            
        # 3. Calculate Base Growth Rate & Cap
        if is_utility:
            growth_cap = 0.08 # Regulated utilities grow slowly
        elif is_telecom:
            growth_cap = 0.12 # Telecoms grow faster than utilities but have high CapEx (Data consumption growth)
        elif is_financial:
            growth_cap = 0.10 # Banks grow with GDP + inflation, usually 10-12% max in long run
        else:
            growth_cap = 0.15 # Tech/Consumer can grow fast
        
        op_curr = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", 0)
        op_prev = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", 2)
        
        base_growth = 0.06
        if op_prev > 0:
            cagr = (op_curr / op_prev)**(1/2) - 1
            base_growth = max(0.02, min(cagr, growth_cap))
        
        # 4. Balance Sheet Items
        debt = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Total Debt", 0)
        cash = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Cash And Cash Equivalents", 0)
        shares = self.data_engine.info.get("sharesOutstanding", 0)
        
        return {
            "current_fcf": current_fcf,
            "base_growth": base_growth,
            "growth_cap": growth_cap,
            "equity_mode": equity_mode,
            "debt": debt,
            "cash": cash,
            "shares": shares,
            "model_type": model_type,
            "sector": sector  # For sector-specific CoE adjustment
        }

    def _compute_dcf(self, inputs, growth_rate, discount_rate, terminal_growth):
        """Pure math calculation for DCF."""
        if not inputs or inputs["shares"] == 0: return 0.0
        
        current_fcf = inputs["current_fcf"]
        projected_fcf = current_fcf
        total_pv = 0
        
        for i in range(1, 6):
            projected_fcf *= (1 + growth_rate)
            discount_factor = (1 + discount_rate) ** i
            total_pv += (projected_fcf / discount_factor)
            
        terminal_val = (projected_fcf * (1 + terminal_growth)) / (discount_rate - terminal_growth)
        tv_discounted = terminal_val / ((1 + discount_rate) ** 5)
        
        total_value = total_pv + tv_discounted
        
        if inputs["equity_mode"]:
            equity_val = total_value
        else:
            equity_val = total_value - inputs["debt"] + inputs["cash"]
            
        return equity_val / inputs["shares"]

    def get_valuation_scenarios(self):
        """
        Returns 3 scenarios: Conservative, Base, Optimistic.
        Uses India-specific cost of equity with sector adjustments.
        """
        inputs = self._get_model_inputs()
        if not inputs: return {}
        
        base_growth = inputs["base_growth"]
        cap = inputs["growth_cap"]
        sector = inputs.get("sector", "")
        
        # Get sector-specific CoE adjustment
        sector_adjustment = self.SECTOR_COE_ADJUSTMENTS.get(sector, 0.0)
        base_coe = self.base_cost_of_equity + sector_adjustment
        
        # Define Scenarios with India-specific parameters
        scenarios = {
            "Conservative": {
                "growth": min(base_growth * 0.8, cap * 0.8),
                "discount": base_coe + 0.015,  # +1.5% for conservative
                "terminal": self.terminal_growth - 0.015  # 3% terminal
            },
            "Base": {
                "growth": base_growth,
                "discount": base_coe,  # Sector-adjusted CoE
                "terminal": self.terminal_growth  # 4.5% India GDP
            },
            "Optimistic": {
                "growth": min(base_growth * 1.2, cap * 1.2),
                "discount": base_coe - 0.015,  # -1.5% for optimistic
                "terminal": self.terminal_growth + 0.01  # 5.5% terminal
            }
        }
        
        results = {}
        for name, params in scenarios.items():
            val = self._compute_dcf(inputs, params["growth"], params["discount"], params["terminal"])
            results[name] = {
                "value": val,
                "growth_used": params["growth"] * 100,
                "discount_used": params["discount"] * 100
            }
            
        return {
            "scenarios": results,
            "model_type": inputs["model_type"]
        }

    def get_valuation_verdict(self):
        """
        Verdict based on BASE case, but returns all 3 for UI.
        """
        data = self.get_valuation_scenarios()
        if not data: return {}
        
        base_val = data["scenarios"]["Base"]["value"]
        current_price = self.data_engine.info.get("currentPrice", 0)
        
        verdict = "HOLD"
        margin_of_safety = 0
        
        if base_val > 0 and current_price > 0:
            if current_price < base_val:
                margin_of_safety = ((base_val - current_price) / base_val) * 100
                if margin_of_safety > 30: 
                    verdict = "BUY (Undervalued)"
                else:
                    verdict = "HOLD (Fair Value)"
            else:
                premium = ((current_price - base_val) / base_val) * 100
                if premium > 50:
                    verdict = "SELL (Overvalued)"
                else:
                    verdict = "HOLD (Premium)"
                    
        return {
            "current_price": current_price,
            "intrinsic_value": base_val, # For backward compatibility in simple views
            "scenarios": data["scenarios"],
            "model_type": data["model_type"],
            "margin_of_safety": margin_of_safety,
            "verdict": verdict
        }
    
    def calculate_epv(self):
        """
        Greenwald's Earnings Power Value - values company assuming zero growth.
        EPV = Adjusted EBIT × (1 - Tax Rate) / Cost of Capital
        
        This provides a conservative baseline: what is the company worth
        if it never grows but maintains current earnings power forever?
        """
        if not self.data_engine.has_data:
            return None
            
        # Get normalized EBIT (3-year average if available)
        ebit_values = []
        for i in range(3):
            ebit = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", i)
            if ebit and ebit > 0:
                ebit_values.append(ebit)
        
        if not ebit_values:
            return {"value": None, "note": "No positive EBIT available"}
        
        avg_ebit = sum(ebit_values) / len(ebit_values)
        
        # Get sector and calculate CoE
        sector = self.data_engine.info.get("sector", "").lower()
        sector_adjustment = self.SECTOR_COE_ADJUSTMENTS.get(sector, 0.0)
        coe = self.base_cost_of_equity + sector_adjustment
        
        # Tax rate (India corporate tax ~25%)
        tax_rate = 0.25
        
        # NOPAT (Net Operating Profit After Tax)
        nopat = avg_ebit * (1 - tax_rate)
        
        # Maintenance CapEx approximation (use depreciation as proxy)
        depreciation = abs(self.data_engine.get_financials_safe(
            self.data_engine.cashflow, "Depreciation And Amortization", 0) or 0)
        
        # Owner earnings = NOPAT - Maintenance CapEx
        owner_earnings = nopat - depreciation * 0.8  # Assume 80% of D&A is maintenance
        
        # Capitalize at cost of equity
        enterprise_value = owner_earnings / coe
        
        # Adjust for cash and debt
        debt = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Total Debt", 0) or 0
        cash = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Cash And Cash Equivalents", 0) or 0
        equity_value = enterprise_value + cash - debt
        
        shares = self.data_engine.info.get("sharesOutstanding", 0)
        if shares <= 0:
            return {"value": None, "note": "No shares outstanding data"}
        
        epv_per_share = equity_value / shares
        current_price = self.data_engine.info.get("currentPrice", 0)
        
        return {
            "value": round(epv_per_share, 2),
            "normalized_ebit": round(avg_ebit / 10_000_000, 2),  # In Cr
            "cost_of_capital": f"{coe * 100:.1f}%",
            "current_price": current_price,
            "upside": round((epv_per_share - current_price) / current_price * 100, 1) if current_price > 0 else 0,
            "verdict": "Undervalued" if epv_per_share > current_price * 1.2 else (
                "Fair" if epv_per_share > current_price * 0.8 else "Overvalued"
            )
        }
    
    def calculate_peg_fair_value(self):
        """
        PEG-based fair value estimation.
        Peter Lynch: Fair PEG = 1.0, meaning P/E should roughly equal growth rate.
        
        Fair P/E = Expected Growth Rate (%) × PEG Multiplier
        """
        eps = self.data_engine.info.get("trailingEps", 0)
        current_pe = self.data_engine.info.get("trailingPE", 0)
        
        if not eps or eps <= 0 or not current_pe:
            return {"value": None, "note": "EPS or P/E not available"}
        
        # Get growth rate (same methodology as DCF)
        op_curr = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", 0)
        op_prev = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Income", 2)
        
        growth_rate = 0.06
        if op_prev and op_prev > 0 and op_curr and op_curr > 0:
            growth_rate = (op_curr / op_prev) ** 0.5 - 1
            growth_rate = max(0.05, min(growth_rate, 0.20))  # Cap between 5% and 20%
        
        growth_pct = growth_rate * 100
        
        # Calculate fair value at different PEG levels
        # Lower PEG = more conservative
        peg_conservative = 0.8   # Strict value investor
        peg_base = 1.2           # Reasonable for quality
        peg_optimistic = 1.8     # Growth premium
        
        fair_pe_conservative = growth_pct * peg_conservative
        fair_pe_base = growth_pct * peg_base
        fair_pe_optimistic = growth_pct * peg_optimistic
        
        current_price = self.data_engine.info.get("currentPrice", 0)
        current_peg = current_pe / growth_pct if growth_pct > 0 else 0
        
        return {
            "conservative": round(eps * fair_pe_conservative, 2),
            "base": round(eps * fair_pe_base, 2),
            "optimistic": round(eps * fair_pe_optimistic, 2),
            "current_peg": round(current_peg, 2),
            "growth_rate": f"{growth_pct:.1f}%",
            "current_price": current_price,
            "assessment": "Cheap" if current_peg < 1.0 else (
                "Fair" if current_peg < 1.5 else (
                    "Expensive" if current_peg < 2.5 else "Very Expensive"
                )
            )
        }

if __name__ == "__main__":
    v = ValuationAnalyzer("RELIANCE.NS")
    print(v.get_valuation_verdict())
