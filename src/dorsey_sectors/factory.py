"""
Sector Factory for Dorsey Analysis

Routes tickers to appropriate sector-specific analysis strategies based on
Pat Dorsey's Part II sector chapters (Chapters 13-26).

Complete Chapter Mapping:
- Ch 14: Healthcare (Pharma, Biotech, Medical Devices)
- Ch 15: Consumer Services (Retail, Restaurants)
- Ch 16: Business Services (Data Processors, Outsourcing)
- Ch 17: Banks
- Ch 18: Asset Management and Insurance
- Ch 19: Software
- Ch 20: Hardware
- Ch 21: Media (Publishing, Broadcasting, Cable)
- Ch 22: Telecom
- Ch 23: Consumer Goods
- Ch 24: Industrial Materials
- Ch 25: Energy
- Ch 26: Utilities
"""

from src.smart_data import SmartDataEngine
from src.dorsey_sectors.base import SectorStrategy

# Import all sector strategies
from src.dorsey_sectors.money_finance import BankingStrategy
from src.dorsey_sectors.insurance import InsuranceStrategy, AssetManagementStrategy
from src.dorsey_sectors.software import SoftwareStrategy
from src.dorsey_sectors.hardware import HardwareStrategy
from src.dorsey_sectors.consumer_goods import ConsumerGoodsStrategy
from src.dorsey_sectors.energy import EnergyStrategy
from src.dorsey_sectors.utilities import UtilitiesStrategy


class SectorFactory:
    """
    Routes a ticker to the appropriate Sector Strategy based on Dorsey's Part II categories.
    
    Uses yfinance sector/industry data to determine the best strategy match.
    Falls back to base SectorStrategy if no specific match found.
    """
    
    @staticmethod
    def get_strategy(ticker):
        """
        Determine and return the appropriate sector strategy for a ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'HDFCBANK.NS')
            
        Returns:
            SectorStrategy subclass instance appropriate for the stock's sector
        """
        # 1. Get sector and industry from yfinance
        engine = SmartDataEngine(ticker)
        sector_y = engine.info.get("sector", "").lower()
        industry_y = engine.info.get("industry", "").lower()
        
        # ============================================================
        # FINANCIAL SECTOR (Chapters 17 & 18)
        # ============================================================
        
        # Insurance companies (Chapter 18)
        if "insurance" in industry_y:
            return InsuranceStrategy(ticker)
        
        # Asset Management (Chapter 18)
        if any(term in industry_y for term in ["asset management", "mutual fund", "investment management", "capital markets"]):
            return AssetManagementStrategy(ticker)
        
        # Banks (Chapter 17)
        if "bank" in industry_y:
            return BankingStrategy(ticker)
        
        # Other Financial Services - default to Banking
        if "financial" in sector_y:
            return BankingStrategy(ticker)
        
        # ============================================================
        # TECHNOLOGY SECTOR (Chapters 19 & 20)
        # ============================================================
        
        # Software (Chapter 19)
        if any(term in industry_y for term in ["software", "information technology services", "internet"]):
            return SoftwareStrategy(ticker)
        
        # Semiconductors and Hardware (Chapter 20)
        if any(term in industry_y for term in ["semiconductor", "hardware", "electronic", "computer"]):
            return HardwareStrategy(ticker)
        
        # Generic Technology - check gross margin to determine
        if "technology" in sector_y:
            # Default to Software (can refine based on margins in strategy)
            return SoftwareStrategy(ticker)
        
        # ============================================================
        # HEALTHCARE SECTOR (Chapter 14)
        # ============================================================
        if "healthcare" in sector_y or any(term in industry_y for term in ["pharm", "biotech", "medical", "drug"]):
            from src.dorsey_sectors.healthcare import HealthcareStrategy
            return HealthcareStrategy(ticker)
        
        # ============================================================
        # CONSUMER SECTORS (Chapters 15 & 23)
        # ============================================================
        
        # Consumer Goods (Chapter 23) - FMCG, packaged goods
        if any(term in industry_y for term in ["personal products", "household", "food products", "beverages", "tobacco", "packaged"]):
            return ConsumerGoodsStrategy(ticker)
        
        # Consumer Services (Chapter 15) - Retail, Restaurants
        if any(term in industry_y for term in ["retail", "restaurant", "hotel", "leisure"]):
            from src.dorsey_sectors.consumer import ConsumerStrategy
            return ConsumerStrategy(ticker)
        
        # Generic Consumer
        if "consumer" in sector_y:
            # Check if cyclical or defensive
            if "cyclical" in sector_y:
                from src.dorsey_sectors.consumer import ConsumerStrategy
                return ConsumerStrategy(ticker)
            else:
                return ConsumerGoodsStrategy(ticker)
        
        # ============================================================
        # ENERGY SECTOR (Chapter 25)
        # ============================================================
        if "energy" in sector_y or any(term in industry_y for term in ["oil", "gas", "petroleum", "drilling"]):
            return EnergyStrategy(ticker)
        
        # ============================================================
        # UTILITIES SECTOR (Chapter 26)
        # ============================================================
        if "utilities" in sector_y or any(term in industry_y for term in ["utility", "electric", "power", "water"]):
            return UtilitiesStrategy(ticker)
        
        # ============================================================
        # TELECOM (Chapter 22)
        # ============================================================
        if "communication" in sector_y or any(term in industry_y for term in ["telecom", "wireless", "telephone"]):
            from src.dorsey_sectors.telecom import TelecomStrategy
            return TelecomStrategy(ticker)
        
        # ============================================================
        # MEDIA (Chapter 21)
        # ============================================================
        if any(term in industry_y for term in ["media", "entertainment", "broadcasting", "publishing", "movies"]):
            from src.dorsey_sectors.media import MediaStrategy
            return MediaStrategy(ticker)
        
        # ============================================================
        # BUSINESS SERVICES (Chapter 16)
        # ============================================================
        if any(term in industry_y for term in ["business service", "consulting", "staffing", "outsourcing", "data processing"]):
            from src.dorsey_sectors.services import BusinessServicesStrategy
            return BusinessServicesStrategy(ticker)
        
        # ============================================================
        # INDUSTRIAL MATERIALS (Chapter 24)
        # ============================================================
        if any(term in sector_y for term in ["industrials", "materials", "basic material"]):
            from src.dorsey_sectors.industrials import IndustrialStrategy
            return IndustrialStrategy(ticker)
        
        # ============================================================
        # REAL ESTATE (not in Dorsey's book but common sector)
        # ============================================================
        if "real estate" in sector_y:
            # Use base strategy with note
            return SectorStrategy(ticker)
        
        # ============================================================
        # FALLBACK
        # ============================================================
        return SectorStrategy(ticker)
    
    @staticmethod
    def get_chapter_reference(ticker):
        """
        Get the Dorsey chapter reference for a given ticker.
        Useful for educational display.
        """
        strategy = SectorFactory.get_strategy(ticker)
        strategy_name = strategy.__class__.__name__
        
        chapter_map = {
            "HealthcareStrategy": "Chapter 14: Healthcare",
            "ConsumerStrategy": "Chapter 15: Consumer Services",
            "BusinessServicesStrategy": "Chapter 16: Business Services",
            "BankingStrategy": "Chapter 17: Banks",
            "FinancialStrategy": "Chapter 17: Banks",
            "InsuranceStrategy": "Chapter 18: Insurance",
            "AssetManagementStrategy": "Chapter 18: Asset Management",
            "SoftwareStrategy": "Chapter 19: Software",
            "HardwareStrategy": "Chapter 20: Hardware",
            "TechnologyStrategy": "Chapter 19-20: Technology",
            "MediaStrategy": "Chapter 21: Media",
            "TelecomStrategy": "Chapter 22: Telecom",
            "ConsumerGoodsStrategy": "Chapter 23: Consumer Goods",
            "IndustrialStrategy": "Chapter 24: Industrial Materials",
            "EnergyStrategy": "Chapter 25: Energy",
            "UtilitiesStrategy": "Chapter 26: Utilities",
            "SectorStrategy": "Generic Analysis"
        }
        
        return chapter_map.get(strategy_name, "Unknown")


if __name__ == "__main__":
    # Test various sectors
    test_tickers = [
        ("HDFCBANK.NS", "Banks - Chapter 17"),
        ("SBILIFE.NS", "Insurance - Chapter 18"),
        ("TCS.NS", "Software - Chapter 19"),
        ("SUNPHARMA.NS", "Healthcare - Chapter 14"),
        ("HINDUNILVR.NS", "Consumer Goods - Chapter 23"),
        ("BHARTIARTL.NS", "Telecom - Chapter 22"),
        ("NTPC.NS", "Utilities - Chapter 26"),
        ("RELIANCE.NS", "Energy - Chapter 25"),
        ("INFY.NS", "Software - Chapter 19"),
    ]
    
    print("=" * 70)
    print("SECTOR FACTORY TEST")
    print("=" * 70)
    
    for ticker, expected in test_tickers:
        try:
            strategy = SectorFactory.get_strategy(ticker)
            chapter = SectorFactory.get_chapter_reference(ticker)
            print(f"{ticker:15} | {strategy.__class__.__name__:25} | {chapter}")
        except Exception as e:
            print(f"{ticker:15} | ERROR: {e}")
