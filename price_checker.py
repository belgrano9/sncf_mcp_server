"""
SNCF Price Checker - Educational Proof of Concept

⚠️ DISCLAIMER ⚠️
This module is for EDUCATIONAL PURPOSES ONLY.

Web scraping may violate SNCF's Terms of Service. This proof-of-concept
demonstrates how price checking COULD work, but:

1. May not function due to anti-scraping measures
2. Should NOT be used in production
3. May violate ToS and legal restrictions
4. For production, use official APIs or licensed providers

For commercial use, consider:
- Lyko SNCF Connect API (https://lyko.tech)
- Trainline API
- Official SNCF partnership programs
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from sncf_scraper import SNCFPriceScraper, PriceSearchResult

logger = logging.getLogger(__name__)


def check_sncf_prices(
    origin_id: str,
    destination_id: str,
    date: str,
    page: int = 1,
    per_page: int = 5
) -> Dict[str, Any]:
    """
    Check SNCF train prices (experimental).

    ⚠️ WARNING: This is a proof-of-concept and may not work.

    Args:
        origin_id: Origin station ID from Navitia API
        destination_id: Destination station ID from Navitia API
        date: Date in YYYY-MM-DD format
        page: Page number for pagination
        per_page: Results per page (max 20)

    Returns:
        Dictionary with price results and pagination info

    Raises:
        ValueError: If scraping fails or stations not supported
    """
    logger.warning(
        "⚠️ Price scraping is experimental and may not work. "
        "This is for educational purposes only."
    )

    try:
        # Parse date
        departure_date = datetime.strptime(date, "%Y-%m-%d")

        # Convert Navitia station IDs to SNCF station codes
        # This is a simplified mapping - real implementation would need
        # a complete station code database
        origin_code = _navitia_to_sncf_code(origin_id)
        destination_code = _navitia_to_sncf_code(destination_id)

        # Create scraper and search
        with SNCFPriceScraper() as scraper:
            result = scraper.search_prices(
                origin_code=origin_code,
                destination_code=destination_code,
                departure_date=departure_date
            )

        # Apply pagination
        per_page = min(max(1, per_page), 20)
        page = max(1, page)

        total_results = len(result.offers)
        total_pages = (total_results + per_page - 1) // per_page

        # Calculate slice
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_results)

        paginated_offers = result.offers[start_idx:end_idx]

        return {
            "success": True,
            "origin": origin_id,
            "destination": destination_id,
            "date": date,
            "offers": [offer.to_dict() for offer in paginated_offers],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_results": total_results,
                "total_pages": total_pages,
                "start_index": start_idx + 1,
                "end_index": end_idx,
            },
            "disclaimer": (
                "⚠️ This is experimental price data. "
                "Actual prices may vary. Please verify on SNCF.com before booking."
            )
        }

    except ValueError as e:
        logger.error(f"Price check failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "note": (
                "Price scraping is currently not functional. "
                "For real pricing, please use:\n"
                "- SNCF Connect website (https://www.sncf-connect.com)\n"
                "- Commercial API providers (e.g., Lyko, Trainline)\n"
                "- Official SNCF partnerships"
            )
        }

    except Exception as e:
        logger.error(f"Unexpected error in price check: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Unexpected error: {type(e).__name__}",
            "note": "Price scraping encountered an unexpected error."
        }


def _navitia_to_sncf_code(navitia_id: str) -> str:
    """
    Convert Navitia station ID to SNCF station code.

    This is a simplified stub. A real implementation would need:
    - Complete database mapping Navitia IDs to SNCF codes
    - Station code lookup service
    - Fallback to station name matching

    Args:
        navitia_id: Navitia station ID (e.g., "stop_area:SNCF:87686006")

    Returns:
        SNCF station code (e.g., "FRPLY" for Paris Gare de Lyon)

    Raises:
        ValueError: If mapping not available
    """
    # Extract SNCF code from Navitia ID
    # Example: "stop_area:SNCF:87686006" -> extract the numeric code

    # This is a VERY simplified mapping
    # Real implementation needs a comprehensive database
    SIMPLE_MAPPINGS = {
        "stop_area:SNCF:87686006": "FRPLY",  # Paris Gare de Lyon
        "stop_area:SNCF:87751008": "FRMSC",  # Marseille Saint-Charles
        "stop_area:SNCF:87271007": "FRPNO",  # Paris Gare du Nord
        "stop_area:SNCF:87391003": "FRPMO",  # Paris Montparnasse
        # Add more mappings as needed
    }

    if navitia_id in SIMPLE_MAPPINGS:
        return SIMPLE_MAPPINGS[navitia_id]

    # If not found, raise error
    raise ValueError(
        f"Station code mapping not available for {navitia_id}. "
        f"Price scraping requires a complete station code database. "
        f"This is a proof-of-concept with limited station support."
    )


def format_price_results(result: Dict[str, Any]) -> str:
    """
    Format price check results as a readable string.

    Args:
        result: Result dictionary from check_sncf_prices()

    Returns:
        Formatted string
    """
    if not result.get("success"):
        output = "❌ PRICE CHECK FAILED\n\n"
        output += f"Error: {result.get('error', 'Unknown error')}\n\n"
        output += result.get("note", "")
        return output

    output = "═══════════════════════════════════\n"
    output += "   SNCF PRICE CHECK (EXPERIMENTAL)\n"
    output += "═══════════════════════════════════\n\n"

    output += f"Route: {result['origin']} → {result['destination']}\n"
    output += f"Date: {result['date']}\n\n"

    pagination = result['pagination']
    output += f"📋 Showing results {pagination['start_index']}-{pagination['end_index']} "
    output += f"of {pagination['total_results']}\n"
    output += f"📄 Page {pagination['page']}/{pagination['total_pages']}\n\n"

    output += "─────────────────────────────────\n"
    output += "AVAILABLE TRAINS\n"
    output += "─────────────────────────────────\n\n"

    for i, offer in enumerate(result['offers'], start=pagination['start_index']):
        hours = offer['duration_minutes'] // 60
        mins = offer['duration_minutes'] % 60

        output += f"  {i}. {offer['train_type']} {offer['train_number']}\n"
        output += f"     {offer['departure_time']} → {offer['arrival_time']} "
        output += f"({hours}h {mins}min)\n"

        if offer.get('price'):
            price_str = f"{offer['price']:.2f} {offer['currency']}"
            status = "[Available]" if offer['available'] else "[Sold Out]"
            output += f"     💰 Price: {price_str} {status}\n"
        else:
            output += f"     💰 Price: Not available\n"

        if offer.get('fare_type'):
            output += f"     Fare: {offer['fare_type']}"
            if offer.get('fare_class'):
                output += f" ({offer['fare_class']} class)"
            output += "\n"

        output += "\n"

    if pagination['total_pages'] > 1:
        output += "─────────────────────────────────\n"
        output += f"💡 To see more results, request page {pagination['page'] + 1}\n"

    output += "\n⚠️ " + result.get('disclaimer', '') + "\n"
    output += "\n═══════════════════════════════════\n"

    return output
