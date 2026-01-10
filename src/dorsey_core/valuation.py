
from src.smart_data import SmartDataEngine
import numpy as np

class ValuationAnalyzer:
    """
    Implements Valuation Analysis (Chapters 9-10).
    1. Relative Valuation: P/E vs History.
    2. Intrinsic Value: Discounted Cash Flow (DCF).
    """
    
    def __init__(self, ticker):
        self.data_engine = SmartDataEngine(ticker)
        self.discount_rate = 0.11 # Conservative 11% for Indian market
        self.terminal_growth = 0.03 # 3% terminal growth
        
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
            "model_type": model_type
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
        """
        inputs = self._get_model_inputs()
        if not inputs: return {}
        
        base_growth = inputs["base_growth"]
        cap = inputs["growth_cap"]
        
        # Define Scenarios
        scenarios = {
            "Conservative": {
                "growth": min(base_growth * 0.8, cap * 0.8),
                "discount": 0.12,
                "terminal": 0.02
            },
            "Base": {
                "growth": base_growth,
                "discount": 0.11,
                "terminal": 0.03
            },
            "Optimistic": {
                "growth": min(base_growth * 1.2, cap * 1.2), # Allow slight flex? No, strict to cap * 1.2 might be okay if base is low
                "discount": 0.10,
                "terminal": 0.04
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

if __name__ == "__main__":
    v = ValuationAnalyzer("RELIANCE.NS")
    print(v.get_valuation_verdict())
