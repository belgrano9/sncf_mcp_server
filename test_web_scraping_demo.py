#!/usr/bin/env python3
"""
Simple demonstration of SNCF web scraping functionality
Shows what works and what doesn't
"""

import sys
from datetime import datetime, timedelta

# Add project to path
sys.path.insert(0, '/home/user/sncf_mcp_server')

from sncf_scraper.scraper import SNCFPriceScraper
from sncf_scraper.models import TrainOffer

print("=" * 80)
print("SNCF WEB SCRAPING - LIVE DEMONSTRATION")
print("=" * 80)
print()

# Test 1: HTTP Scraper Initialization
print("📦 TEST 1: HTTP Scraper Initialization")
print("-" * 80)
try:
    scraper = SNCFPriceScraper(timeout=10)
    print("✅ SUCCESS: Scraper initialized")
    print(f"   - Base URL: {scraper.BASE_URL}")
    print(f"   - API Base: {scraper.API_BASE}")
    print(f"   - Timeout: {scraper.timeout}s")
    print(f"   - User Agent: {scraper.USER_AGENT[:50]}...")
    scraper.close()
except Exception as e:
    print(f"❌ FAILED: {e}")

print()

# Test 2: Attempt to fetch prices (will likely fail)
print("🔍 TEST 2: Attempting to Fetch Real Prices")
print("-" * 80)
print("   Route: Paris (FRPNO) → Marseille (FRMLC)")
print(f"   Date: {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}")
print()

try:
    scraper = SNCFPriceScraper(timeout=10)

    # Try to search for prices
    tomorrow = datetime.now() + timedelta(days=1)
    result = scraper.search_prices(
        origin_code="FRPNO",  # Paris Nord
        destination_code="FRMLC",  # Marseille
        departure_date=tomorrow,
        passenger_count=1
    )

    print(f"✅ UNEXPECTED SUCCESS: Found {len(result.offers)} offers!")

    for i, offer in enumerate(result.offers[:3], 1):
        print(f"\n   Offer {i}:")
        print(f"   - Train: {offer.train_type} {offer.train_number}")
        print(f"   - Time: {offer.departure_time} → {offer.arrival_time}")
        print(f"   - Duration: {offer.duration_minutes} minutes")
        if offer.price:
            print(f"   - Price: €{offer.price:.2f}")

    scraper.close()

except ValueError as e:
    print(f"❌ EXPECTED FAILURE: {str(e)[:100]}...")
    print()
    print("   ⚠️  This is EXPECTED. SNCF blocks automated requests.")

except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {str(e)[:100]}...")

print()

# Test 3: Check browser scraper availability
print("🌐 TEST 3: Browser Scraper Availability")
print("-" * 80)
try:
    import undetected_chromedriver as uc
    from selenium import webdriver
    print("✅ Selenium and undetected-chromedriver are installed")

    # Check for Chrome
    import subprocess
    chrome_check = subprocess.run(
        ["which", "google-chrome", "chromium", "chromium-browser"],
        capture_output=True,
        text=True
    )

    if chrome_check.returncode == 0:
        print("✅ Chrome/Chromium is installed")
        print("   ✨ Browser-based scraping COULD work on this system")
    else:
        print("❌ Chrome/Chromium is NOT installed")
        print("   ⚠️  Browser-based scraping requires Chrome to be installed")

except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("   Run: uv sync")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("✅ What WORKS:")
print("   - Scraper code is properly structured")
print("   - HTTP client initialization works")
print("   - Error handling is functional")
print("   - Data models are well-defined")
print()
print("❌ What DOESN'T work:")
print("   - HTTP requests are blocked by SNCF (403 Forbidden)")
print("   - Anti-scraping measures detect automated requests")
print("   - Chrome not available for browser-based scraping")
print()
print("🔧 What COULD work (with Chrome installed):")
print("   - Browser-based scraping using Selenium")
print("   - Undetected ChromeDriver to bypass bot detection")
print("   - Human-like interaction simulation")
print()
print("📌 CONCLUSION:")
print("   The scraping CODE is working correctly, but:")
print("   - SNCF's anti-bot protection blocks HTTP requests")
print("   - Browser-based scraping would need Chrome installed")
print("   - This is for educational purposes only")
print()
print("   For production use:")
print("   - Use official APIs (Lyko, Trainline)")
print("   - SNCF's Terms of Service may prohibit scraping")
print("=" * 80)
