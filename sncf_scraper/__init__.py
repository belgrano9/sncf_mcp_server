"""
SNCF Price Scraper - Educational Proof of Concept

⚠️ DISCLAIMER: This is for educational purposes only.
Web scraping may violate SNCF's Terms of Service.
For production use, consider official API access or commercial providers.

TWO APPROACHES AVAILABLE:
1. SNCFPriceScraper - Simple HTTP (doesn't work - 401 error)
2. SNCFBrowserScraper - Browser automation (WORKS! 🎉)
"""

from .scraper import SNCFPriceScraper
from .browser_scraper import SNCFBrowserScraper
from .models import TrainOffer, PriceSearchResult

__all__ = [
    "SNCFPriceScraper",      # Simple HTTP (educational - shows why it fails)
    "SNCFBrowserScraper",    # Browser automation (actually works!)
    "TrainOffer",
    "PriceSearchResult"
]
