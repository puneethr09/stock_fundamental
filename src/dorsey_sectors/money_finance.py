
from src.dorsey_sectors.base import SectorStrategy


class BankingStrategy(SectorStrategy):
    """
    Implements Chapter 17: Banks.
    
    Per Pat Dorsey's Five Rules:
    - Bank analysis is "all about risk" - credit risk and interest rate risk
    - Banks leverage depositor money, so ROE > 12% is the minimum bar
    - Focus on asset quality, efficiency, and sustainable returns
    
    Key Metrics:
    - Price to Book (P/B) - Core valuation for banks
    - Return on Equity (ROE) - Must be > 12% consistently  
    - Efficiency Ratio - Non-Interest Expense / Revenue (< 50% is best)
    - Net Interest Margin (NIM) - Core profitability metric
    
    Indian Banking Specific (Manual verification recommended):
    - NPA Ratio - Asset quality (critical for Indian banks)
    - CASA Ratio - Low-cost deposit base (moat indicator)
    - Provision Coverage Ratio (PCR) - Safety buffer
    - Capital Adequacy Ratio (CAR) - Regulatory requirement
    """
    
    def __init__(self, ticker):
        super().__init__(ticker)
        self.sector_name = "Banks"
        
    def analyze(self):
        insights = []
        red_flags = []
        
        # --- 1. Price to Book (Core Valuation for Banks) ---
        pb = self.data_engine.info.get("priceToBook", 0)
        pb_judgment = "Attractive" if pb < 1.2 else ("Fair" if pb < 2.0 else ("Premium" if pb < 3.0 else "Expensive"))
        insights.append({
            "metric": "Price to Book (P/B)",
            "value": f"{pb:.2f}x" if pb else "N/A",
            "judgment": pb_judgment,
            "context": "Banks trade on book value. < 1.5x is usually good value for quality banks."
        })
        
        # --- 2. ROE (Critical for Banks - Dorsey recommends > 12%) ---
        ni = self.data_engine.get_financials_safe(self.data_engine.financials, "Net Income", 0)
        eq = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Stockholders Equity", 0)
        roe = (ni / eq) * 100 if eq > 0 else 0
        
        # Per Dorsey: Banks should achieve ROE > 12% consistently
        roe_judgment = "Excellent" if roe > 15 else ("Good" if roe > 12 else ("Marginal" if roe > 8 else "Weak"))
        insights.append({
            "metric": "Return on Equity (ROE)",
            "value": f"{roe:.1f}%",
            "judgment": roe_judgment,
            "context": "Per Dorsey: Banks using leverage must achieve ROE > 12% consistently. Below this, they're not earning their cost of capital."
        })
        
        if roe < 10 and roe > 0:
            red_flags.append("ROE below 10% - bank may not be creating value for shareholders")
        
        # --- 3. Efficiency Ratio (Operating Efficiency) ---
        total_rev = self.data_engine.get_financials_safe(self.data_engine.financials, "Total Revenue", 0)
        opex = self.data_engine.get_financials_safe(self.data_engine.financials, "Operating Expense", 0)
        
        if total_rev > 0 and opex > 0:
            eff_ratio = (opex / total_rev) * 100
            eff_judgment = "Best-in-Class" if eff_ratio < 45 else ("Efficient" if eff_ratio < 55 else ("Average" if eff_ratio < 65 else "Inefficient"))
            insights.append({
                "metric": "Efficiency Ratio (Proxy)",
                "value": f"{eff_ratio:.1f}%",
                "judgment": eff_judgment,
                "context": "Lower is better. < 50% is excellent for banks. This measures how much of revenue goes to operating expenses."
            })
            
            if eff_ratio > 70:
                red_flags.append("Efficiency ratio > 70% - bank has high operating costs")
        
        # --- 4. Net Interest Margin (NIM) Proxy ---
        # NIM = (Interest Income - Interest Expense) / Average Earning Assets
        # Using available data as proxy
        interest_income = self.data_engine.get_financials_safe(self.data_engine.financials, "Interest Income", 0)
        interest_expense = self.data_engine.get_financials_safe(self.data_engine.financials, "Interest Expense", 0)
        total_assets = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Total Assets", 0)
        
        if interest_income > 0 and total_assets > 0:
            # Approximate NIM using total assets as earning assets proxy
            net_interest_income = interest_income - abs(interest_expense) if interest_expense else interest_income
            nim_proxy = (net_interest_income / total_assets) * 100
            
            nim_judgment = "Strong" if nim_proxy > 3.5 else ("Good" if nim_proxy > 2.5 else ("Thin" if nim_proxy > 1.5 else "Weak"))
            insights.append({
                "metric": "Net Interest Margin (NIM) Proxy",
                "value": f"{nim_proxy:.2f}%",
                "judgment": nim_judgment,
                "context": "NIM measures spread between lending and borrowing rates. > 3% is generally strong for Indian banks."
            })
        
        # --- 5. Indian Banking Specific Notes ---
        insights.append({
            "metric": "Asset Quality (NPA) Check",
            "value": "Manual Verification Required",
            "judgment": "⚠️ Important",
            "context": "GNPA < 2% is excellent, 2-5% acceptable, > 5% is concerning. Check bank's quarterly results for exact NPA figures."
        })
        
        insights.append({
            "metric": "CASA Ratio Check",
            "value": "Manual Verification Required", 
            "judgment": "ℹ️ Moat Indicator",
            "context": "CASA (Current + Savings deposits / Total deposits) > 40% indicates strong low-cost deposit franchise - a key moat for Indian banks."
        })
        
        # --- 6. Leverage Check ---
        total_debt = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Total Debt", 0)
        if eq > 0:
            total_assets = self.data_engine.get_financials_safe(self.data_engine.balance_sheet, "Total Assets", 0)
            leverage = total_assets / eq if eq > 0 else 0
            insights.append({
                "metric": "Financial Leverage",
                "value": f"{leverage:.1f}x",
                "judgment": "Normal" if leverage < 15 else ("High" if leverage < 20 else "Very High"),
                "context": "Banks are inherently leveraged (10-15x is normal). Focus on ROE being > 12% given this leverage."
            })
        
        return {
            "sector": self.sector_name,
            "chapter_reference": "Chapter 17: Banks",
            "insights": insights,
            "red_flags": red_flags if red_flags else None,
            "manual_checks": [
                "Verify exact NPA (GNPA and NNPA) from quarterly results",
                "Check CASA ratio from bank's investor presentation",
                "Review Provision Coverage Ratio (PCR) - should be > 70%",
                "Check Capital Adequacy Ratio (CAR) - should be > 12%"
            ]
        }


# Alias for backward compatibility
FinancialStrategy = BankingStrategy
