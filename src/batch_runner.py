"""
Batch Stock Analysis Runner

Runs analysis on all Indian stocks from CSV files and stores results for ranking.
Designed to be run nightly after market close.

Usage:
    python -m src.batch_runner                    # All stocks from nifty_500
    python -m src.batch_runner --input input/Indian_stocks_nifty_50.csv  # Specific CSV
    python -m src.batch_runner --limit 10         # Test with 10 stocks
"""

import os
import sys
import csv
import json
import argparse
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Set

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging to both console and file
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "batch_analysis.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w'),  # Clear log file on each run
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

from src.dorsey_runner import run_dorsey_analysis
from src.dorsey_core.scorecard import DorseyScorecard


def load_stocks_from_csv(csv_path: str) -> List[Dict]:
    """Load stocks from a single CSV file"""
    stocks = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticker = row.get("Ticker", "").strip()
                if ticker:
                    stocks.append({
                        "ticker": ticker + ".NS",  # Add NSE suffix
                        "name": row.get("Company Name", ticker),
                        "industry": row.get("Industry", "Unknown"),
                    })
    except FileNotFoundError:
        logger.error(f"CSV not found: {csv_path}")
    return stocks


def load_all_stocks(input_dir: str = "input") -> List[Dict]:
    """Load all unique stocks from all CSV files in input directory"""
    all_stocks = []
    seen_tickers: Set[str] = set()
    
    csv_files = [
        "Indian_stocks_nifty_500.csv",
        "Indian_stocks_nifty_200.csv", 
        "Indian_stocks_nifty_50.csv",
        "Indian_stocks_nifty_large_midcap_250.csv",
        "Indian_stocks_nifty_midcap_100.csv",
        "Indian_stocks_nifty_smallcap_250.csv",
        "Indian_stocks_all_market.csv",
    ]
    
    for csv_file in csv_files:
        csv_path = os.path.join(input_dir, csv_file)
        stocks = load_stocks_from_csv(csv_path)
        for stock in stocks:
            if stock["ticker"] not in seen_tickers:
                seen_tickers.add(stock["ticker"])
                all_stocks.append(stock)
    
    logger.info(f"Loaded {len(all_stocks)} unique stocks from {len(csv_files)} CSV files")
    return all_stocks


def analyze_stock(stock: Dict, delay: float = 2.0) -> Dict:
    """Run full analysis on a single stock with rate limiting"""
    import time
    ticker = stock["ticker"]
    result = {
        "ticker": ticker,
        "name": stock["name"],
        "industry": stock["industry"],
        "analyzed_at": datetime.now().isoformat(),
        "error": None,
    }
    
    # Rate limiting delay
    time.sleep(delay)
    
    # Retry logic for rate limiting
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Run full Dorsey analysis
            analysis = run_dorsey_analysis(ticker)
            
            # Extract key metrics for ranking
            scorecard = analysis.get("scorecard", {})
            valuation = analysis.get("valuation", {})
            combined = valuation.get("combined", {})
            moat = analysis.get("moat_analysis", {})
            health = analysis.get("financial_health", {})
            graham = analysis.get("graham_defensive_screen", {})
            
            result["dorsey_score"] = scorecard.get("total_score", 0)
            result["recommendation"] = scorecard.get("recommendation", "N/A")
            result["confidence"] = scorecard.get("confidence", "N/A")
            
            result["valuation_upside"] = combined.get("margin_of_safety", 0)
            result["combined_value"] = combined.get("combined_value", 0)
            result["dcf_value"] = combined.get("dcf_value", 0)
            result["relative_value"] = combined.get("relative_value", 0)
            result["current_price"] = valuation.get("current_price", 0)
            result["valuation_verdict"] = combined.get("verdict", valuation.get("verdict", "N/A"))
            
            result["moat_rating"] = moat.get("moat_rating", "None")
            result["moat_score"] = _moat_to_score(moat.get("moat_rating", "None"))
            
            result["health_rating"] = health.get("health_rating", "N/A")
            result["health_score"] = _health_to_score(health.get("health_rating", "N/A"))
            
            result["graham_passed"] = graham.get("passed", 0)
            result["graham_total"] = graham.get("total", 7)
            result["graham_verdict"] = graham.get("verdict", "N/A")
            
            # Composite score (weighted)
            result["composite_score"] = (
                result["dorsey_score"] * 0.4 +
                min(result["valuation_upside"], 100) * 0.3 +
                result["moat_score"] * 10 * 0.2 +
                result["health_score"] * 10 * 0.1
            )
            break  # Success, exit retry loop
            
        except Exception as e:
            error_str = str(e)
            if "Rate" in error_str or "Too Many" in error_str:
                # Rate limited - wait and retry
                wait_time = (attempt + 1) * 5  # 5, 10, 15 seconds
                logger.warning(f"Rate limited on {ticker}, waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                if attempt == max_retries - 1:
                    result["error"] = error_str
                    result["dorsey_score"] = 0
                    result["composite_score"] = 0
            else:
                result["error"] = error_str
                result["dorsey_score"] = 0
                result["composite_score"] = 0
                break  # Non-rate-limit error, don't retry
    
    return result


def _moat_to_score(moat_rating: str) -> int:
    """Convert moat rating to numeric score"""
    if "Wide" in moat_rating:
        return 3
    elif "Narrow" in moat_rating:
        return 2
    return 1


def _health_to_score(health_rating: str) -> int:
    """Convert health rating to numeric score"""
    if "ROBUST" in health_rating.upper():
        return 3
    elif "MODERATE" in health_rating.upper():
        return 2
    return 1


def run_batch_analysis(stocks: List[Dict], max_workers: int = 1) -> List[Dict]:
    """Run analysis on all stocks sequentially (safest for rate limits)"""
    import time
    
    results = []
    total = len(stocks)
    completed = 0
    errors = 0
    consecutive_errors = 0
    
    logger.info("=" * 60)
    logger.info(f"Starting SEQUENTIAL batch analysis of {total} stocks")
    logger.info("Strategy: Single Worker | 2.0s Delay | 30s Pause per 50 | 5min Cooldown on 5 Errors")
    logger.info("=" * 60)
    
    start_time = datetime.now()
    
    for i, stock in enumerate(stocks):
        # 1. Chunk Pause (Every 50 stocks)
        if i > 0 and i % 50 == 0:
            logger.info("=" * 40)
            logger.info(f"☕ Taking a 30s break (Chunk {i}) to cool down API...")
            logger.info("=" * 40)
            time.sleep(30)
            
            # Incremental Save (safety against crashes)
            save_results(results, output_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
        
        # 2. Consecutive Error Cooldown
        if consecutive_errors >= 5:
            logger.warning("=" * 40)
            logger.warning("⚠️ High Error Rate (5 consecutive). Pausing for 5 minutes...")
            logger.warning("=" * 40)
            time.sleep(300)
            consecutive_errors = 0 # Reset to try again
        
        # Run Analysis
        completed += 1
        try:
            result = analyze_stock(stock)
            results.append(result)
            
            if result.get("error"):
                errors += 1
                consecutive_errors += 1
                status = "❌"
            else:
                consecutive_errors = 0 # Success resets counter
                status = "✅"
            
            # Log progress
            elapsed = (datetime.now() - start_time).seconds
            rate = completed / max(elapsed, 1)
            remaining = (total - completed) / max(rate, 0.1)
            remaining_min = remaining / 60
            
            logger.info(f"[{completed}/{total}] {status} {stock['ticker']:15} | "
                  f"Score: {result.get('dorsey_score', 0):>3} | "
                  f"ETA: {remaining_min:.1f}m")
                
        except Exception as e:
            errors += 1
            consecutive_errors += 1
            print(f"[{completed}/{total}] ❌ {stock['ticker']} - Critical Fail: {e}")
            
    end_time = datetime.now()
    duration = (end_time - start_time).seconds
    
    logger.info("=" * 60)
    logger.info("Batch analysis complete!")
    logger.info(f"Total: {total} | Success: {total - errors} | Errors: {errors}")
    logger.info(f"Duration: {duration}s ({duration/60:.1f} min)")
    logger.info("=" * 60)
    
    return results


def save_results(results: List[Dict], output_dir: str = "data") -> str:
    """Save results to JSON file with timestamp"""
    os.makedirs(output_dir, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"rankings_{date_str}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Sort by composite score (descending)
    results_sorted = sorted(results, key=lambda x: x.get("composite_score", 0), reverse=True)
    
    output = {
        "generated_at": datetime.now().isoformat(),
        "total_stocks": len(results),
        "stocks": results_sorted,
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Results saved to: {filepath}")
    
    # Also save as 'latest.json' for easy access
    latest_path = os.path.join(output_dir, "latest.json")
    with open(latest_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Latest copy saved to: {latest_path}")
    
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Batch Stock Analysis Runner")
    parser.add_argument("--input", type=str, help="Specific CSV file to process")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of stocks (for testing)")
    parser.add_argument("--workers", type=int, default=1, help="Number of parallel workers (keep low to avoid rate limits)")
    parser.add_argument("--output", type=str, default="data", help="Output directory")
    
    args = parser.parse_args()
    
    # Load stocks
    if args.input:
        stocks = load_stocks_from_csv(args.input)
    else:
        stocks = load_all_stocks()
    
    # Apply limit if specified
    if args.limit:
        stocks = stocks[:args.limit]
        print(f"[INFO] Limited to {args.limit} stocks for testing")
    
    if not stocks:
        print("[ERROR] No stocks to analyze!")
        return
    
    # Run batch analysis
    results = run_batch_analysis(stocks, max_workers=args.workers)
    
    # Save results
    save_results(results, args.output)
    
    # Print top 10
    print("\n🏆 TOP 10 STOCKS BY COMPOSITE SCORE:")
    print("-" * 60)
    sorted_results = sorted(results, key=lambda x: x.get("composite_score", 0), reverse=True)
    for i, stock in enumerate(sorted_results[:10], 1):
        print(f"{i:2}. {stock['ticker']:15} | Score: {stock.get('dorsey_score', 0):>3} | "
              f"Upside: {stock.get('valuation_upside', 0):>5.1f}% | "
              f"Moat: {stock.get('moat_rating', 'N/A')}")


if __name__ == "__main__":
    main()
