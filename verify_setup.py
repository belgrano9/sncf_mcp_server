#!/usr/bin/env python3
"""Quick setup verification for SNCF browser scraper."""

import sys

print("=" * 70)
print("SNCF Browser Scraper - Setup Verification")
print("=" * 70)
print()

# Test 1: Import dependencies
print("Test 1: Checking dependencies...")
try:
    import selenium
    print(f"  OK - Selenium {selenium.__version__}")
except ImportError as e:
    print(f"  FAIL - Selenium not found: {e}")
    sys.exit(1)

try:
    import undetected_chromedriver as uc
    print(f"  OK - undetected-chromedriver {uc.__version__}")
except ImportError as e:
    print(f"  FAIL - undetected-chromedriver not found: {e}")
    sys.exit(1)

# Test 2: Import scraper module
print("\nTest 2: Checking scraper module...")
try:
    from sncf_scraper import SNCFBrowserScraper
    print("  OK - SNCFBrowserScraper imported")
except ImportError as e:
    print(f"  FAIL - Could not import scraper: {e}")
    sys.exit(1)

# Test 3: Initialize (but don't run full test)
print("\nTest 3: Initializing scraper...")
try:
    scraper = SNCFBrowserScraper(headless=True)
    print("  OK - Scraper initialized")
except Exception as e:
    print(f"  FAIL - Could not initialize: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("SUCCESS - All checks passed!")
print("=" * 70)
print()
print("Next steps:")
print("  1. Run the browser test:")
print("     uv run tests/test_browser_scraper.py")
print()
print("  2. Or use in your code:")
print("     from sncf_scraper import SNCFBrowserScraper")
print("     scraper = SNCFBrowserScraper()")
print("     result = scraper.search_prices(...)")
print()
print("Note: First run will download ChromeDriver (~100MB)")
print("=" * 70)
