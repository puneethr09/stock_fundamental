
import pandas as pd
import os
from src.dorsey_runner import run_dorsey_analysis
import time

def run_batch_analysis(input_file, output_file):
    print(f"Starting batch analysis on {input_file}...")
    
    # Read tickers
    # Assuming CSV has 'Symbol' or 'Ticker' column
    try:
        df = pd.read_csv(input_file)
        # Try finding relevant column
        ticker_col = None
        for col in ["Ticker", "Symbol", "SYMBOL", "Company Name"]:
            if col in df.columns:
                ticker_col = col
                break
        
        if not ticker_col:
            print("Error: Could not find 'Ticker' or 'Symbol' column in CSV.")
            return
            
        tickers = df[ticker_col].tolist()
        results = []
        
        print(f"Found {len(tickers)} tickers. Processing...")
        
        for i, t in enumerate(tickers):
            # Cleanup ticker
            t = str(t).strip()
            if not t.endswith(".NS") and not t.endswith(".BO"):
                t = f"{t}.NS"
            
            print(f"Analyzing [{i+1}/{len(tickers)}]: {t} ...")
            
            try:
                data = run_dorsey_analysis(t)
                
                # Flatten crucial data for the summary report
                row = {
                    "Ticker": t,
                    "Sector": data["sector_analysis"]["sector"],
                    "10_Min_Test": data["ten_minute_test"]["overall_verdict"],
                    "Moat_Rating": data["moat_analysis"]["moat_rating"],
                    "Intrinsic_Value": data["valuation"]["intrinsic_value"],
                    "Current_Price": data["valuation"]["current_price"],
                    "Valuation": data["valuation"]["verdict"],
                    "Margin_of_Safety": data["valuation"]["margin_of_safety"],
                    "Financial_Health": data["financial_health"]["health_rating"]
                }
                
                # Check for "Pitfalls" (Failures)
                pitfall_flags = []
                if data["ten_minute_test"]["overall_verdict"] == "FAIL":
                    pitfall_flags.append("Failed 10-Min Test")
                if "Risky" in data["financial_health"]["health_rating"]:
                    pitfall_flags.append("Financial Red Flags")
                row["Pitfalls"] = "; ".join(pitfall_flags) if pitfall_flags else "None"
                
                results.append(row)
                
            except Exception as e:
                print(f"Failed to analyze {t}: {e}")
                results.append({
                    "Ticker": t,
                    "Pitfalls": f"ERROR: {str(e)}"
                })
                
    except Exception as e:
        print(f"Fatal error reading input: {e}")
        return

    # Save Results
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)
    print(f"Analysis Complete. Results saved to {output_file}")

if __name__ == "__main__":
    input_path = "input/Indian_stocks_nifty_50.csv"
    output_path = "batch_analysis_results.csv"
    run_batch_analysis(input_path, output_path)
