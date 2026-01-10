
from src.ten_minute_test import TenMinuteTest
from src.dorsey_core.moat import MoatAnalyzer
from src.dorsey_core.financials import FinancialsAnalyzer
from src.dorsey_core.valuation import ValuationAnalyzer
from src.dorsey_sectors.factory import SectorFactory

def run_dorsey_analysis(ticker):
    """
    Executes the full Dorsey Protocol.
    Returns a unified dictionary for the UI.
    """
    results = {}
    
    # 1. Ten Minute Test
    tm = TenMinuteTest(ticker)
    results["ten_minute_test"] = tm.run_test()
    
    # 2. Core Framework (Moat, Health, Value)
    m = MoatAnalyzer(ticker)
    results["moat_analysis"] = m.analyze_moat()
    
    f = FinancialsAnalyzer(ticker)
    results["financial_health"] = f.analyze_health()
    
    v = ValuationAnalyzer(ticker)
    results["valuation"] = v.get_valuation_verdict()
    
    # 3. Sector Specifics
    s = SectorFactory.get_strategy(ticker)
    results["sector_analysis"] = s.analyze()
    
    return results
