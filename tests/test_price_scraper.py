#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test SNCF Price Scraper - Educational Proof of Concept

⚠️ DISCLAIMER: These tests demonstrate the price scraper implementation
but may fail due to:
- Anti-scraping measures
- SNCF website changes
- Network restrictions
- Terms of Service violations

This is for educational purposes only.
"""

import sys
from datetime import datetime, timedelta

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from sncf_scraper import SNCFPriceScraper
from price_checker import check_sncf_prices, format_price_results


def test_scraper_initialization():
    """Test that scraper can be initialized."""
    print("=" * 70)
    print("TEST 1: Scraper Initialization")
    print("=" * 70)

    try:
        scraper = SNCFPriceScraper(timeout=10)
        print("✅ Scraper initialized successfully")
        print(f"   Base URL: {scraper.BASE_URL}")
        print(f"   API Base: {scraper.API_BASE}")
        scraper.close()
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


def test_price_check_with_known_stations():
    """Test price checking with known station codes."""
    print("\n" + "=" * 70)
    print("TEST 2: Price Check with Known Stations")
    print("=" * 70)

    # Use Paris Gare de Lyon → Marseille Saint-Charles
    origin_id = "stop_area:SNCF:87686006"  # Paris Gare de Lyon
    destination_id = "stop_area:SNCF:87751008"  # Marseille Saint-Charles

    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.strftime("%Y-%m-%d")

    print(f"\n📍 Testing route: Paris → Marseille")
    print(f"📅 Date: {date_str}")
    print(f"\n⚠️  Note: This will likely fail due to anti-scraping measures")
    print("   This is expected and demonstrates why official APIs are needed.\n")

    try:
        result = check_sncf_prices(
            origin_id=origin_id,
            destination_id=destination_id,
            date=date_str,
            page=1,
            per_page=5
        )

        if result.get("success"):
            print("✅ Price check completed (unexpectedly!)")
            print(f"   Found {result['pagination']['total_results']} offers")

            # Show first offer if available
            if result['offers']:
                first_offer = result['offers'][0]
                print(f"\n   First offer:")
                print(f"   - Train: {first_offer['train_type']} {first_offer['train_number']}")
                print(f"   - Time: {first_offer['departure_time']} → {first_offer['arrival_time']}")
                if first_offer.get('price'):
                    print(f"   - Price: {first_offer['price']} {first_offer['currency']}")

            # Print formatted output
            print("\n" + "-" * 70)
            print("Formatted output:")
            print("-" * 70)
            print(format_price_results(result))

            return True
        else:
            print("❌ Price check failed (as expected)")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            print(f"\n   Note: {result.get('note', '')}")
            return False

    except Exception as e:
        print(f"❌ Price check raised exception (expected): {type(e).__name__}")
        print(f"   Message: {str(e)}")
        print("\n   This is normal - SNCF has anti-scraping measures.")
        return False


def test_unknown_station_handling():
    """Test handling of unknown stations."""
    print("\n" + "=" * 70)
    print("TEST 3: Unknown Station Handling")
    print("=" * 70)

    # Use a station ID not in our mapping
    unknown_id = "stop_area:SNCF:99999999"
    known_id = "stop_area:SNCF:87686006"

    date_str = datetime.now().strftime("%Y-%m-%d")

    print(f"\n📍 Testing with unknown station: {unknown_id}")

    try:
        result = check_sncf_prices(
            origin_id=unknown_id,
            destination_id=known_id,
            date=date_str
        )

        if not result.get("success"):
            print("✅ Correctly handled unknown station")
            print(f"   Error: {result.get('error', '')[:100]}...")
            return True
        else:
            print("❌ Should have failed for unknown station")
            return False

    except Exception as e:
        print(f"✅ Correctly raised exception for unknown station")
        print(f"   Exception: {type(e).__name__}")
        return True


def run_all_tests():
    """Run all price scraper tests."""
    print("\n" + "=" * 70)
    print("SNCF PRICE SCRAPER - TEST SUITE")
    print("Educational Proof of Concept")
    print("=" * 70)

    print("\n⚠️  IMPORTANT DISCLAIMERS:")
    print("   - These tests are for educational purposes only")
    print("   - Web scraping may violate SNCF's Terms of Service")
    print("   - Tests may fail due to anti-scraping measures (expected)")
    print("   - DO NOT use in production")
    print()

    results = {}

    # Run tests
    results['initialization'] = test_scraper_initialization()
    results['price_check'] = test_price_check_with_known_stations()
    results['unknown_station'] = test_unknown_station_handling()

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        icon = "✅" if result else "❌"
        print(f"{icon} {test_name}: {'PASSED' if result else 'FAILED'}")

    print(f"\nResults: {passed}/{total} tests passed")

    print("\n" + "=" * 70)
    print("IMPORTANT NOTES:")
    print("=" * 70)
    print("""
It is EXPECTED that most tests will fail due to:
- SNCF's anti-scraping measures (403 Forbidden)
- Missing API endpoint knowledge
- Terms of Service restrictions

This proof-of-concept demonstrates:
✅ How price scraping COULD be implemented
✅ The challenges involved
✅ Why official APIs are necessary for production

For real price data, use:
- Lyko SNCF Connect API (https://lyko.tech)
- Trainline API
- Official SNCF partnerships
    """)
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
