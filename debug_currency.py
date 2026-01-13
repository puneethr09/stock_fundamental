
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.smart_data import SmartDataEngine
import yfinance as yf

ticker = "HCLTECH.NS"
print(f"Debugging {ticker}...")

engine = SmartDataEngine(ticker)

print(f"Price Currency: {engine.info.get('currency')}")
print(f"Financial Currency: {engine.info.get('financialCurrency')}")
print(f"FX Rate Applied: {engine.fx_rate}")

# Check raw values
try:
    if "Total Revenue" in engine.financials.index:
        raw_revenue = engine.financials.loc["Total Revenue"].iloc[0]
        print(f"Raw Revenue (0): {raw_revenue}")
        safe_revenue = engine.get_financials_safe(engine.financials, "Total Revenue", 0)
        print(f"Safe Revenue (0): {safe_revenue}")

        # Check if raw revenue looks like USD or INR
        # HCL Revenue is ~1 Lakh Crore = 1,000,000,000,000 INR
        # In USD it would be ~12 Billion = 12,000,000,000 USD
        print(f"Raw Revenue Length: {len(str(int(raw_revenue)))}")
    else:
        print("Total Revenue not found in financials")
except Exception as e:
    print(f"Error accessing financials: {e}")

if engine.fx_rate > 1.0:
    print("WARNING: FX Rate is being applied!")
else:
    print("FX Rate is 1.0 (Correct)")
