
from src.smart_data import SmartDataEngine
from src.dorsey_sectors.base import SectorStrategy
from src.dorsey_sectors.money_finance import FinancialStrategy
from src.dorsey_sectors.technology import TechnologyStrategy

class SectorFactory:
    """
    Routes a ticker to the appropriate Sector Strategy based on Dorsey's Part II categories.
    """
    
    @staticmethod
    def get_strategy(ticker):
        # 1. Detect Sector from YFinance
        engine = SmartDataEngine(ticker)
        sector_y = engine.info.get("sector", "").lower()
        industry_y = engine.info.get("industry", "").lower()
        
        # 2. Route
        if "financial" in sector_y or "bank" in industry_y or "insurance" in industry_y:
            return FinancialStrategy(ticker)
            
        if "technology" in sector_y or "software" in industry_y or "semiconductor" in industry_y:
            return TechnologyStrategy(ticker)
            
        if "healthcare" in sector_y or "pharm" in industry_y or "biotech" in industry_y:
            from src.dorsey_sectors.healthcare import HealthcareStrategy
            return HealthcareStrategy(ticker)
        
        if "consumer" in sector_y or "retail" in industry_y or "food" in industry_y:
            from src.dorsey_sectors.consumer import ConsumerStrategy
            return ConsumerStrategy(ticker)
            
        if "energy" in sector_y or "utility" in sector_y or "utilit" in industry_y or "oil" in industry_y or "basic material" in sector_y or "industrials" in sector_y:
            from src.dorsey_sectors.industrials import IndustrialStrategy
            return IndustrialStrategy(ticker)
            
        if "communication" in sector_y or "telecom" in industry_y or "wireless" in industry_y:
            from src.dorsey_sectors.telecom import TelecomStrategy
            return TelecomStrategy(ticker)
        
        if "media" in industry_y or "entertainment" in industry_y:
            from src.dorsey_sectors.media import MediaStrategy
            return MediaStrategy(ticker)
            
        if "business service" in industry_y or "consulting" in industry_y:
            from src.dorsey_sectors.services import BusinessServicesStrategy
            return BusinessServicesStrategy(ticker)
        
        # Fallback
        return SectorStrategy(ticker)

if __name__ == "__main__":
    # Test
    s = SectorFactory.get_strategy("HDFCBANK.NS")
    print(f"Strategy: {s.__class__.__name__}")
    print(s.analyze())
