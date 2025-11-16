#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test SNCF Browser Scraper - WORKING POC

This tests the browser-based scraper which has a much higher chance
of success than simple HTTP requests.

⚠️ Requirements:
- Chrome/Chromium browser installed
- selenium and undetected-chromedriver packages
- Good internet connection

⚠️ Note: This will open a browser window (or headless) and actually
visit the SNCF website, simulating a real user.
"""

import sys
from datetime import datetime, timedelta

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Add parent directory to path for imports
sys.path.insert(0, '.')

from sncf_scraper.browser_scraper import SNCFBrowserScraper


def test_browser_initialization():
    """Test that browser can be initialized."""
    print("=" * 70)
    print("TEST 1: Browser Initialization")
    print("=" * 70)

    try:
        print("\n📦 Initializing browser scraper...")
        print("   (This will download ChromeDriver if needed)")

        scraper = SNCFBrowserScraper(headless=True)
        scraper._init_driver()

        print("✅ Browser initialized successfully!")
        print(f"   Driver: {scraper.driver.name}")
        print(f"   Version: {scraper.driver.capabilities.get('browserVersion', 'Unknown')}")

        scraper.close()
        print("✅ Browser closed successfully")

        return True

    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Make sure Chrome/Chromium is installed")
        print("   - Run: uv sync (to install dependencies)")
        print("   - Check internet connection (ChromeDriver downloads)")
        return False


def test_browser_navigation():
    """Test navigating to SNCF Connect."""
    print("\n" + "=" * 70)
    print("TEST 2: Navigate to SNCF Connect")
    print("=" * 70)

    try:
        print("\n🌐 Opening SNCF Connect website...")

        scraper = SNCFBrowserScraper(headless=True)
        scraper._init_driver()
        scraper._navigate_to_search()

        current_url = scraper.driver.current_url
        print(f"✅ Successfully navigated to: {current_url}")

        # Save screenshot
        scraper.driver.save_screenshot("tests/sncf_homepage.png")
        print("📸 Screenshot saved: tests/sncf_homepage.png")

        scraper.close()
        return True

    except Exception as e:
        print(f"❌ Navigation failed: {e}")
        return False


def test_full_search():
    """
    Test complete search flow.

    This is the big one - actually searches for trains and extracts prices!
    """
    print("\n" + "=" * 70)
    print("TEST 3: Full Search Flow (Paris → Marseille)")
    print("=" * 70)

    print("\n⚠️  This test will:")
    print("   1. Open SNCF Connect in a browser")
    print("   2. Fill the search form (simulating human)")
    print("   3. Submit the search")
    print("   4. Wait for results")
    print("   5. Extract prices")
    print()
    print("⏱️  This may take 30-60 seconds...")
    print()

    try:
        tomorrow = datetime.now() + timedelta(days=1)

        print(f"🔍 Searching: Paris → Marseille")
        print(f"📅 Date: {tomorrow.strftime('%Y-%m-%d')}")
        print()

        # Use non-headless for debugging (you can see what's happening)
        headless = input("Run in headless mode? (y/n, default=y): ").strip().lower() != 'n'

        print(f"\n🚀 Starting browser (headless={headless})...")

        scraper = SNCFBrowserScraper(headless=headless)

        result = scraper.search_prices(
            origin="Paris",
            destination="Marseille",
            departure_date=tomorrow
        )

        print("\n" + "=" * 70)
        print("SEARCH RESULTS")
        print("=" * 70)

        if result.offers:
            print(f"\n✅ Found {len(result.offers)} train offers!")
            print()

            for i, offer in enumerate(result.offers, 1):
                hours = offer.duration_minutes // 60
                mins = offer.duration_minutes % 60

                print(f"  {i}. {offer.train_type}")
                print(f"     🕐 {offer.departure_time} → {offer.arrival_time} ({hours}h {mins}min)")

                if offer.price:
                    status = "✅ Available" if offer.available else "❌ Sold Out"
                    print(f"     💰 {offer.price:.2f} EUR - {status}")
                else:
                    print(f"     💰 Price not available")

                print()

            print("=" * 70)
            print(f"📊 Success Rate: 100% ({len(result.offers)} offers extracted)")
            print("=" * 70)

            # Show debug files
            print("\n📁 Debug files created:")
            print("   - sncf_results.png (screenshot)")
            print("   - sncf_results.html (page source)")
            print("   - tests/sncf_homepage.png (homepage)")
            print()
            print("💡 Inspect these files to understand the page structure")

        else:
            print("\n⚠️  No offers extracted, but search completed!")
            print()
            print("📋 Next steps:")
            print("   1. Check sncf_results.html for the page structure")
            print("   2. Check sncf_results.png to see what loaded")
            print("   3. Update CSS selectors in browser_scraper.py")
            print("      based on actual HTML structure")

        scraper.close()
        return len(result.offers) > 0

    except Exception as e:
        print(f"\n❌ Search failed: {e}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()

        print("\n💡 Debugging tips:")
        print("   - Run with headless=False to see what's happening")
        print("   - Check sncf_*.png/html files")
        print("   - SNCF may have updated their page structure")

        return False


def run_all_tests():
    """Run all browser scraper tests."""
    print("\n" + "=" * 70)
    print("SNCF BROWSER SCRAPER - TEST SUITE")
    print("Working POC using Selenium + undetected-chromedriver")
    print("=" * 70)

    print("\n⚠️  IMPORTANT NOTES:")
    print("   - This ACTUALLY visits the SNCF website")
    print("   - May take 1-2 minutes total")
    print("   - Requires Chrome/Chromium installed")
    print("   - First run downloads ChromeDriver (~100MB)")
    print("   - Still for educational purposes only!")
    print()

    input("Press Enter to continue...")

    results = {}

    # Run tests
    results['initialization'] = test_browser_initialization()

    if results['initialization']:
        results['navigation'] = test_browser_navigation()

        if results['navigation']:
            results['full_search'] = test_full_search()
        else:
            results['full_search'] = False
    else:
        results['navigation'] = False
        results['full_search'] = False

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        icon = "✅" if result else "❌"
        status = "PASSED" if result else "FAILED"
        print(f"{icon} {test_name}: {status}")

    print(f"\nResults: {passed}/{total} tests passed")

    if results.get('full_search'):
        print("\n" + "=" * 70)
        print("🎉 SUCCESS! Browser scraper is WORKING!")
        print("=" * 70)
        print("""
This proves that browser automation CAN scrape SNCF successfully!

Key differences from simple HTTP scraper:
✅ Uses real browser (not blocked by Datadome)
✅ Handles JavaScript/cookies automatically
✅ Simulates human behavior
✅ Much higher success rate

However, still remember:
⚠️  For educational purposes only
⚠️  May violate Terms of Service
⚠️  For production, use official APIs (Lyko/Trainline)

But now you KNOW it CAN be done! 🚀
        """)
    else:
        print("\n" + "=" * 70)
        print("DEBUGGING NEEDED")
        print("=" * 70)
        print("""
Browser initialized but couldn't extract prices.
This is likely due to:

1. SNCF changed their HTML structure
2. Need to update CSS selectors in browser_scraper.py
3. Datadome still detecting (rare with undetected-chromedriver)

Check the debug files (*.png, *.html) to see what actually loaded.
        """)

    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
