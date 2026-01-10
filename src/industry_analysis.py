
import pandas as pd

def get_sector_data(ticker_obj):
    """
    Extracts sector and industry from a yfinance Ticker object.
    """
    info = ticker_obj.info
    return {
        "sector": info.get("sector", "Unknown"),
        "industry": info.get("industry", "Unknown")
    }

def analyze_industry_specifics(ticker_obj, financials_data):
    """
    Applies Industry-Specific Rules (Pat Dorsey style).
    Returns a dictionary of insights and checks.
    """
    info = ticker_obj.info
    sector = info.get("sector", "").lower()
    industry = info.get("industry", "").lower()
    insights = {
        "industry_type": f"{sector.title()} ({industry.title()})",
        "key_metrics": [],
        "verdict": "Neutral" # Bullish, Bearish, Neutral
    }
    
    # --- 1. BANKING & FINANCE ---
    if "financial" in sector or "bank" in industry:
        insights["industry_group"] = "Financial Services"
        # Rule: Ignore traditional Debt/Equity. Focus on ROE and Book Value.
        roe = info.get("returnOnEquity", 0)
        pb_ratio = info.get("priceToBook", 0)
        
        insights["key_metrics"].append({
            "metric": "Return on Equity (ROE)",
            "value": f"{roe*100:.2f}%",
            "threshold": "> 12%",
            "status": "Good" if roe > 0.12 else "Weak",
            "reason": "Banks leverage OPM (Other People's Money). High ROE indicates efficient use of capital."
        })
        
        insights["key_metrics"].append({
            "metric": "Price to Book (P/B)",
            "value": f"{pb_ratio:.2f}",
            "threshold": "< 1.5",
            "status": "Undervalued" if pb_ratio < 1.0 else ("Fair" if pb_ratio < 2.0 else "Premium"),
            "reason": "For banks, book value is a reliable proxy for intrinsic value."
        })

    # --- 2. TECHNOLOGY / SOFTWARE ---
    elif "technology" in sector or "software" in industry:
        insights["industry_group"] = "Technology"
        # Rule: Look for high gross margins and low debt. P/E can be higher.
        gross_margins = info.get("grossMargins", 0)
        debt_to_equity = info.get("debtToEquity", 0) / 100 # yfinance gives as percentage often
        
        insights["key_metrics"].append({
            "metric": "Gross Margins",
            "value": f"{gross_margins*100:.2f}%",
            "threshold": "> 50%",
            "status": "Excellent" if gross_margins > 0.50 else "Average",
            "reason": "Software companies should have high margins due to low incremental costs."
        })
        
        insights["key_metrics"].append({
            "metric": "Debt/Equity",
            "value": f"{debt_to_equity:.2f}",
            "threshold": "< 0.5",
            "status": "Safe" if debt_to_equity < 0.5 else "Risky",
            "reason": "Tech companies rarely need high debt loads. High debt is a red flag."
        })

    # --- 3. RETAIL ---
    elif "consumer" in sector or "retail" in industry:
        insights["industry_group"] = "Retail / Consumer"
        # Rule: Inventory Turnover is king.
        # Note: We need inventory data. If not easily available in `info`, we might skip or approximate.
        # yfinance `info` usually doesn't have turnover rates directly, we need calculated ratios.
        pass # Will be handled if we passed the full ratios dataframe
        
    # --- 4. ENERGY / UTILITIES ---
    elif "energy" in sector or "utilities" in sector:
         insights["industry_group"] = "Energy/Utilities"
         # Rule: Capital intensive. Watch Interest Coverage.
         # This part usually requires the computed ratios_df to be accurate.
         pass

    # Generic/Fallback Analysis if no specific match or to supplement
    if not insights.get("industry_group"):
         insights["industry_group"] = "General"
         
    return insights

def analyze_industry_context(ratios_df, ticker_obj):
    """
    Wrapper to analyze using the dataframe context which has historicals.
    """
    insights = analyze_industry_specifics(ticker_obj, None)
    
    # Add dataframe specific checks (Trends)
    # E.g. for Retail, calculate recent Inventory Turnover trend if columns exist
    
    return insights
