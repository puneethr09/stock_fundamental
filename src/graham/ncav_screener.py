"""
Net Current Asset Value (NCAV) Screener

Benjamin Graham's "Net-Net" strategy from Security Analysis (1934).

This is a deep value strategy that identifies stocks trading below their
liquidation value - essentially buying a dollar for less than 50 cents.

NCAV Formula:
NCAV = Current Assets - Total Liabilities - Preferred Stock

Buy when: Market Price < 66.7% of NCAV per share (Graham's rule)

Note: Financial sector stocks are excluded as their balance sheets
have different structures.
"""

from src.smart_data import SmartDataEngine


class NCAVScreener:
    """
    Ben Graham's Net-Net strategy for finding deeply undervalued stocks.
    
    A stock trading below NCAV is theoretically worth more dead than alive -
    you could buy it, liquidate the current assets, pay off all debts,
    and still pocket the difference.
    
    Graham's Rule: Buy at ≤ 66.7% of NCAV (33% margin of safety on liquidation value)
    """
    
    def __init__(self, ticker):
        self.data_engine = SmartDataEngine(ticker)
        self.ticker = ticker
        
    def calculate_ncav(self):
        """
        Calculate Net Current Asset Value.
        
        NCAV = Current Assets - Total Liabilities - Preferred Stock
        NCAV per share = NCAV / Shares Outstanding
        """
        if not self.data_engine.has_data:
            return {"status": "NO DATA", "ticker": self.ticker}
        
        # Get balance sheet items
        current_assets = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Current Assets", 0)
        total_liabilities = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Total Liabilities Net Minority Interest", 0)
        preferred_stock = self.data_engine.get_financials_safe(
            self.data_engine.balance_sheet, "Preferred Stock", 0) or 0
        
        # Check if financial sector (exclude from NCAV analysis)
        sector = self.data_engine.info.get("sector", "").lower()
        if "financial" in sector:
            return {
                "ticker": self.ticker,
                "status": "EXCLUDED",
                "reason": "Financial sector stocks excluded from NCAV analysis due to different balance sheet structure",
                "sector": sector
            }
        
        if not current_assets or not total_liabilities:
            return {
                "ticker": self.ticker,
                "status": "INSUFFICIENT DATA",
                "reason": "Current assets or total liabilities not available"
            }
        
        # Calculate NCAV
        ncav = current_assets - total_liabilities - preferred_stock
        
        # Get shares outstanding and current price
        shares_outstanding = self.data_engine.info.get("sharesOutstanding", 0)
        current_price = self.data_engine.info.get("currentPrice", 0)
        
        if not shares_outstanding or shares_outstanding <= 0:
            return {
                "ticker": self.ticker,
                "status": "INSUFFICIENT DATA",
                "reason": "Shares outstanding not available"
            }
        
        # Calculate per share values
        ncav_per_share = ncav / shares_outstanding
        
        # Graham's buy threshold (66.67% of NCAV)
        graham_buy_price = ncav_per_share * 0.667
        
        # Calculate metrics
        price_to_ncav = (current_price / ncav_per_share * 100) if ncav_per_share > 0 else None
        discount_to_ncav = ((ncav_per_share - current_price) / ncav_per_share * 100) if ncav_per_share > 0 else None
        
        # Determine verdict
        if ncav_per_share <= 0:
            verdict = "NEGATIVE NCAV"
            recommendation = "Stock has negative net current assets - not a net-net candidate"
            is_net_net = False
        elif current_price <= graham_buy_price:
            verdict = "NET-NET OPPORTUNITY"
            recommendation = f"Trading at significant discount to NCAV - classic Graham net-net"
            is_net_net = True
        elif current_price <= ncav_per_share:
            verdict = "BELOW NCAV"
            recommendation = "Trading below NCAV but above Graham's strict threshold"
            is_net_net = False
        else:
            verdict = "ABOVE NCAV"
            recommendation = "Trading above liquidation value - not a net-net"
            is_net_net = False
        
        return {
            "ticker": self.ticker,
            "company": self.data_engine.info.get("longName", self.ticker),
            "sector": sector,
            "ncav_analysis": {
                "current_assets": current_assets,
                "total_liabilities": total_liabilities,
                "preferred_stock": preferred_stock,
                "ncav": ncav,
                "shares_outstanding": shares_outstanding,
                "ncav_per_share": round(ncav_per_share, 2),
                "graham_buy_price": round(graham_buy_price, 2),
                "current_price": current_price
            },
            "metrics": {
                "price_to_ncav_percentage": f"{price_to_ncav:.1f}%" if price_to_ncav else "N/A",
                "discount_to_ncav": f"{discount_to_ncav:.1f}%" if discount_to_ncav else "N/A",
                "margin_of_safety": f"{100 - price_to_ncav:.1f}%" if price_to_ncav and price_to_ncav < 100 else "None"
            },
            "verdict": verdict,
            "is_net_net": is_net_net,
            "recommendation": recommendation,
            "graham_says": "A stock is a bargain if it can be bought at no more than two-thirds the value of the net current assets."
        }
    
    def quick_screen(self):
        """
        Quick check if stock qualifies as a net-net.
        Returns simple pass/fail.
        """
        result = self.calculate_ncav()
        
        if result.get("status") in ["NO DATA", "EXCLUDED", "INSUFFICIENT DATA"]:
            return {
                "ticker": self.ticker,
                "is_net_net": False,
                "reason": result.get("reason", result.get("status"))
            }
        
        return {
            "ticker": self.ticker,
            "is_net_net": result.get("is_net_net", False),
            "ncav_per_share": result.get("ncav_analysis", {}).get("ncav_per_share"),
            "current_price": result.get("ncav_analysis", {}).get("current_price"),
            "verdict": result.get("verdict")
        }


def screen_universe(tickers):
    """
    Screen a list of tickers for net-net opportunities.
    Returns list of candidates.
    """
    candidates = []
    excluded = []
    
    for ticker in tickers:
        screener = NCAVScreener(ticker)
        result = screener.quick_screen()
        
        if result.get("is_net_net"):
            candidates.append(result)
        elif result.get("reason"):
            excluded.append({
                "ticker": ticker,
                "reason": result.get("reason")
            })
    
    return {
        "candidates": candidates,
        "excluded_count": len(excluded),
        "total_screened": len(tickers),
        "net_nets_found": len(candidates)
    }


if __name__ == "__main__":
    # Test with some value stocks
    test_tickers = ["COALINDIA.NS", "ONGC.NS", "NMDC.NS", "VEDL.NS"]
    
    for ticker in test_tickers:
        print(f"\n{'='*60}")
        print(f"NCAV Analysis: {ticker}")
        print('='*60)
        
        screener = NCAVScreener(ticker)
        result = screener.calculate_ncav()
        
        if result.get("status"):
            print(f"Status: {result.get('status')}")
            print(f"Reason: {result.get('reason', 'N/A')}")
        else:
            print(f"Company: {result.get('company')}")
            print(f"\nNCAV per Share: ₹{result['ncav_analysis']['ncav_per_share']:.2f}")
            print(f"Graham Buy Price: ₹{result['ncav_analysis']['graham_buy_price']:.2f}")
            print(f"Current Price: ₹{result['ncav_analysis']['current_price']:.2f}")
            print(f"\nVerdict: {result['verdict']}")
            print(f"Recommendation: {result['recommendation']}")
