
import yfinance as yf
import pandas as pd
import numpy as np

class SmartDataEngine:
    """
    Robust data extraction layer for Indian Stocks.
    Manually calculates metrics from financial statements when yfinance summaries are missing.
    """
    
    def __init__(self, ticker):
        self.ticker_symbol = ticker
        self.ticker = yf.Ticker(ticker)
        self.info = self.ticker.info
        self.financials = self.ticker.financials
        self.balance_sheet = self.ticker.balance_sheet
        self.cashflow = self.ticker.cashflow
        
        # Ensure dataframes are not empty and handle safely
        self.has_data = not (self.financials.empty or self.balance_sheet.empty or self.cashflow.empty)
        
        # --- Currency Normalization ---
        # yfinance often returns USD financials for Indian stocks (ADRs), but price in INR.
        # We must align financials to the listing currency (INR).
        self.fx_rate = 1.0
        price_curr = self.info.get("currency", "INR")
        fin_curr = self.info.get("financialCurrency", "INR")
        
        if price_curr == "INR" and fin_curr == "USD":
            # Sanity check: Many Indian IT companies report in USD but yfinance returns INR numbers
            # If Revenue > 500 Billion (50,000 Crores), it's likely already in INR
            # (Largest Indian IT company TCS is ~$30B Revenue = 2.5 Lakh Crore INR)
            try:
                if "Total Revenue" in self.financials.index:
                    rev = self.financials.loc["Total Revenue"].iloc[0]
                    if rev > 500_000_000_000:  # > 500 Billion
                        self.fx_rate = 1.0
                    else:
                        self.fx_rate = 84.0
                else:
                    self.fx_rate = 84.0
            except:
                self.fx_rate = 84.0
            
    def get_financials_safe(self, df, key, year_idx=0):
        """Safely retrieve a value from a DataFrame row (key) and column (year_idx)."""
        if not self.has_data:
            return 0.0
        try:
            if key in df.index:
                val = df.loc[key].iloc[year_idx]
                val = float(val) if not pd.isna(val) else 0.0
                return val * self.fx_rate
        except Exception:
            return 0.0
        return 0.0

    def calculate_invested_capital(self, year_idx=0):
        """
        Invested Capital = Total Equity + Total Debt - Cash & Equivalents
        """
        total_equity = self.get_financials_safe(self.balance_sheet, "Stockholders Equity", year_idx)
        # Total Debt might be split
        long_term_debt = self.get_financials_safe(self.balance_sheet, "Long Term Debt", year_idx)
        current_debt = self.get_financials_safe(self.balance_sheet, "Current Debt", year_idx)
        total_debt_bs = self.get_financials_safe(self.balance_sheet, "Total Debt", year_idx)
        
        # Use explicit sum if Total Debt missing
        total_debt = total_debt_bs if total_debt_bs > 0 else (long_term_debt + current_debt)
        
        cash = self.get_financials_safe(self.balance_sheet, "Cash And Cash Equivalents", year_idx)
        
        return total_equity + total_debt - cash

    def calculate_nopat(self, year_idx=0):
        """
        NOPAT = Operating Income * (1 - Tax Rate)
        """
        operating_income = self.get_financials_safe(self.financials, "Operating Income", year_idx)
        tax_provision = self.get_financials_safe(self.financials, "Tax Provision", year_idx)
        pretax_income = self.get_financials_safe(self.financials, "Pretax Income", year_idx)
        
        if pretax_income == 0:
            tax_rate = 0.25 # Assume standard 25% if no data
        else:
            tax_rate = tax_provision / pretax_income
            # Cap realistic tax rate 0 to 40%
            tax_rate = max(0.0, min(tax_rate, 0.40))
            
        return operating_income * (1 - tax_rate)

    def calculate_roic(self, year_idx=0):
        """
        ROIC = NOPAT / Invested Capital
        """
        ic = self.calculate_invested_capital(year_idx)
        nopat = self.calculate_nopat(year_idx)
        
        if ic == 0:
            return 0.0
        return (nopat / ic) * 100

    def calculate_fcf(self, year_idx=0):
        """
        Free Cash Flow = Operating Cash Flow - Capital Expenditure
        """
        ocf = self.get_financials_safe(self.cashflow, "Operating Cash Flow", year_idx)
        # CapEx is usually negative in cashflow
        capex = self.get_financials_safe(self.cashflow, "Capital Expenditure", year_idx)
        
        # If capex is positive for some reason, subtract it. If negative (outflow), add strictly? 
        # Standard: OCF + CapEx (since CapEx is negative).
        # Let's check sign.
        if capex > 0:
            capex = -capex # Force outflow behavior
            
        return ocf + capex

    def get_manual_metrics(self):
        """
        Returns a dictionary of strict Dorsey metrics calculated manually.
        """
        metrics = {
            "ROIC_Current": self.calculate_roic(0),
            "ROIC_1Y_Ago": self.calculate_roic(1),
            "ROIC_2Y_Ago": self.calculate_roic(2),
            "Invested_Capital": self.calculate_invested_capital(0),
            "FCF": self.calculate_fcf(0),
            "Debt_to_Equity_Manual": 0.0
        }
        
        # Debt/Equity Manual
        equity = self.get_financials_safe(self.balance_sheet, "Stockholders Equity", 0)
        debt = self.get_financials_safe(self.balance_sheet, "Total Debt", 0)
        if equity > 0:
            metrics["Debt_to_Equity_Manual"] = debt / equity
            
        return metrics

# Test function
if __name__ == "__main__":
    ticker = "RELIANCE.NS"
    engine = SmartDataEngine(ticker)
    print(f"--- Analysis for {ticker} ---")
    print(engine.get_manual_metrics())
