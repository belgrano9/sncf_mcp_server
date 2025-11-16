import os
from datetime import datetime
from dotenv import load_dotenv
import requests
from fastmcp import FastMCP
from dateutil import parser as date_parser  # More flexible parser

# ============================================================================
# 1. Configuration & Constants
# ============================================================================

load_dotenv()

SNCF_API_KEY = os.getenv("SNCF_API")
if not SNCF_API_KEY:
    raise ValueError("SNCF_API key not found in .env file")

BASE_URL = "https://api.sncf.com/v1"
DEFAULT_TIMEOUT = 30

# Create the MCP server
mcp = FastMCP("SNCF Train Search")


# ============================================================================
# 2. Core Helper Functions (Modified to Return Context)
# ============================================================================


def api_get(endpoint, params=None):
    """Make a GET request to the SNCF API."""
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(
        url, auth=(SNCF_API_KEY, ""), params=params, timeout=DEFAULT_TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def get_formatted_date(date_str=None):
    """
    Flexible date parser that handles multiple formats.
    Returns API format (YYYYMMDDTHHMMSS).
    """
    if not date_str:
        dt_obj = datetime.now()
    else:
        try:
            # First, try to detect if it's clearly day-first (European style)
            # If day > 12, it MUST be day-first
            if "/" in date_str:
                parts = date_str.split()[0].split("/")  # Get date part before time
                if len(parts) >= 2 and parts[0].isdigit():
                    first_num = int(parts[0])
                    if first_num > 12:
                        # Must be day-first (e.g., 28/11/2025)
                        dt_obj = date_parser.parse(date_str, dayfirst=True)
                    else:
                        # Ambiguous or month-first, use European default for SNCF
                        dt_obj = date_parser.parse(date_str, dayfirst=True)
                else:
                    dt_obj = date_parser.parse(date_str, dayfirst=True)
            else:
                # For other formats (ISO, written dates), let parser decide
                dt_obj = date_parser.parse(date_str)

        except (ValueError, date_parser.ParserError) as e:
            raise ValueError(
                f"❌ Could not parse date '{date_str}'. "
                f"Supported formats:\n"
                f"  - ISO: '2025-11-28' or '2025-11-28 08:00'\n"
                f"  - European: '28/11/2025' or '28/11/2025 08:00'\n"
                f"  - Written: 'November 28, 2025' or '28 November 2025'\n"
                f"Error: {str(e)}"
            )

    return dt_obj.strftime("%Y%m%dT%H%M%S")


def find_station_id(station_name):
    """
    Search for a station name and return both ID and context.
    Returns a dict with: success, station_id, station_name, context
    """
    try:
        response = api_get("coverage/sncf/places", params={"q": station_name})
        places = response.get("places", [])

        if not places:
            return {
                "success": False,
                "station_id": None,
                "station_name": None,
                "context": f"❌ No stations found for '{station_name}'. Please check the spelling or try a different name.",
            }

        # Build a narrative for Claude
        context = f"🔍 Searched for '{station_name}':\n"
        for i, place in enumerate(places[:3]):
            marker = "✓" if i == 0 else " "
            context += f"  {marker} {place['name']} (ID: {place['id']})\n"

        context += f"\n→ Selected: {places[0]['name']}"

        return {
            "success": True,
            "station_id": places[0]["id"],
            "station_name": places[0]["name"],
            "context": context,
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "station_id": None,
            "station_name": None,
            "context": f"❌ API Error while searching for '{station_name}': {str(e)}",
        }


def search_journeys_with_context(origin_id, dest_id, departure_time, page=1):
    """
    Queries the API for journeys and returns formatted results with context.
    Returns a string with the journey options formatted for Claude to read.

    Args:
        origin_id: Origin station ID
        dest_id: Destination station ID
        departure_time: Departure datetime in API format
        page: Page number (1-indexed), shows 10 results per page
    """
    if not origin_id or not dest_id:
        return "❌ Missing Origin or Destination ID. Cannot search for journeys."

    # Validate page number
    if page < 1:
        return "❌ Page number must be 1 or greater."

    try:
        # Request more results to enable pagination (100 journeys)
        response = api_get(
            "coverage/sncf/journeys",
            params={
                "from": origin_id,
                "to": dest_id,
                "datetime": departure_time,
                "count": 100,  # Fetch 100 journeys to enable pagination
            },
        )

        journeys = response.get("journeys", [])

        if not journeys:
            return "❌ No journeys found for this route and time. Try a different time or date."

        # Pagination settings
        per_page = 10
        total_journeys = len(journeys)
        total_pages = (total_journeys + per_page - 1) // per_page  # Ceiling division

        # Validate page number against total pages
        if page > total_pages:
            return f"❌ Page {page} does not exist. Only {total_pages} page(s) available with {total_journeys} journey(s)."

        # Calculate slice for current page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_journeys)
        page_journeys = journeys[start_idx:end_idx]

        # Build the journey list with pagination info
        result = f"Found {total_journeys} journey option(s) | Page {page}/{total_pages}\n"
        if total_pages > 1:
            result += f"ℹ️  Showing results {start_idx + 1}-{end_idx} of {total_journeys}\n"
        result += "\n"

        for i, journey in enumerate(page_journeys, start=start_idx + 1):
            # Extract times
            departs = journey["departure_date_time"]
            arrives = journey["arrival_date_time"]

            # Format nicely
            pretty_dep = f"{departs[0:4]}-{departs[4:6]}-{departs[6:8]} {departs[9:11]}:{departs[11:13]}"
            pretty_arr = f"{arrives[0:4]}-{arrives[4:6]}-{arrives[6:8]} {arrives[9:11]}:{arrives[11:13]}"

            # Calculate duration
            duration_seconds = journey["duration"]
            duration_hours = duration_seconds / 3600
            duration_mins = (duration_seconds % 3600) / 60

            # Count transfers
            nb_transfers = journey.get("nb_transfers", 0)
            transfer_text = (
                "Direct" if nb_transfers == 0 else f"{nb_transfers} change(s)"
            )

            result += f"  {i+1}. Depart: {pretty_dep} → Arrive: {pretty_arr}\n"
            result += f"     Duration: {int(duration_hours)}h {int(duration_mins)}min | {transfer_text}\n"

            # Add section details if there are transfers
            if nb_transfers > 0:
                sections = journey.get("sections", [])
                train_sections = [
                    s for s in sections if s.get("type") == "public_transport"
                ]
                if train_sections:
                    result += f"     Route: "
                    route_parts = []
                    for section in train_sections:
                        from_name = section.get("from", {}).get("name", "?")
                        to_name = section.get("to", {}).get("name", "?")
                        route_parts.append(f"{from_name} → {to_name}")
                    result += " | ".join(route_parts)
                    result += "\n"

            result += "\n"

        return result

    except requests.exceptions.RequestException as e:
        return f"❌ API Error while searching for journeys: {str(e)}"


# ============================================================================
# 3. MCP Tools (The "Buttons" Claude Can Press)
# ============================================================================


@mcp.tool()
def search_trains(
    origin: str, destination: str, departure_datetime: str = None, page: int = 1
) -> str:
    """
    Search for train journeys between two stations with pagination.

    Args:
        origin: Starting station name (e.g., "Paris Est", "Lyon")
        destination: Destination station name (e.g., "München Hbf", "Barcelona")
        departure_datetime: Optional datetime. Accepts flexible formats:
                           - ISO: "2025-11-28 08:00" (RECOMMENDED)
                           - European: "28/11/2025 08:00"
                           - Written: "November 28, 2025 8:00am"
                           If not provided, searches from current time.
        page: Page number for pagination (default: 1). Shows 10 results per page.
              Request different pages to see more trains (e.g., page=2, page=3).
    """

    # Build up a story for Claude
    story = "═══════════════════════════════════\n"
    story += "    SNCF JOURNEY SEARCH\n"
    story += "═══════════════════════════════════\n\n"

    # Step 1: Find origin station
    origin_result = find_station_id(origin)
    story += origin_result["context"] + "\n\n"

    if not origin_result["success"]:
        story += "⚠️ Cannot proceed without valid origin station."
        return story

    # Step 2: Find destination station
    dest_result = find_station_id(destination)
    story += dest_result["context"] + "\n\n"

    if not dest_result["success"]:
        story += "⚠️ Cannot proceed without valid destination station."
        return story

    # Step 3: Format the datetime
    api_datetime = get_formatted_date(departure_datetime)

    if departure_datetime:
        story += f"📅 Searching for trains departing after: {departure_datetime}\n"
    else:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        story += f"📅 Searching for trains departing after: {current_time} (now)\n"

    story += f"🔄 API datetime format: {api_datetime}\n\n"

    # Step 4: Search journeys
    story += "─────────────────────────────────\n"
    story += "🚄 AVAILABLE TRAINS\n"
    story += "─────────────────────────────────\n\n"

    journey_results = search_journeys_with_context(
        origin_result["station_id"], dest_result["station_id"], api_datetime, page
    )

    story += journey_results

    story += "\n═══════════════════════════════════\n"

    return story


@mcp.tool()
def find_station(station_name: str) -> str:
    """
    Search for a train station by name and return matching options.

    Useful for checking station names before searching for journeys,
    or when you're not sure of the exact station name.

    Args:
        station_name: Station name to search for (e.g., "Paris", "Munich", "Lyon")

    Returns:
        A formatted string showing matching stations with their IDs and full names.
    """

    result = find_station_id(station_name)

    story = "═══════════════════════════════════\n"
    story += "    STATION SEARCH\n"
    story += "═══════════════════════════════════\n\n"

    story += result["context"] + "\n"

    if result["success"]:
        story += f"\n✅ Best match: {result['station_name']}\n"
        story += f"   ID: {result['station_id']}\n"

    story += "\n═══════════════════════════════════\n"

    return story


@mcp.tool()
def get_train_prices(
    origin: str,
    destination: str,
    departure_datetime: str = None,
    page: int = 1,
    per_page: int = 5
) -> str:
    """
    Get train prices (EXPERIMENTAL - Educational Proof of Concept).

    ⚠️ WARNING: This is an experimental feature that attempts to scrape
    prices from SNCF. It may not work due to:
    - Anti-scraping measures
    - API changes
    - Terms of Service restrictions

    For production use, consider:
    - Lyko SNCF Connect API
    - Trainline API
    - Official SNCF partnerships

    Args:
        origin: Origin station name (e.g., "Paris", "Lyon")
        destination: Destination station name (e.g., "Marseille")
        departure_datetime: Date/time in flexible formats (default: today)
        page: Page number for pagination (default: 1)
        per_page: Results per page (default: 5, max: 20)

    Returns:
        Formatted string with price information (if available)
    """
    # Import here to make it optional
    try:
        from price_checker import check_sncf_prices, format_price_results
    except ImportError as e:
        return (
            "❌ Price checking module not available.\n\n"
            f"Error: {e}\n\n"
            "This is an experimental feature. "
            "For real pricing, please visit https://www.sncf-connect.com"
        )

    story = "═══════════════════════════════════\n"
    story += "  SNCF PRICE CHECK (EXPERIMENTAL)\n"
    story += "═══════════════════════════════════\n\n"

    story += "⚠️  WARNING: Experimental feature\n"
    story += "    May not work due to anti-scraping measures\n"
    story += "    For educational purposes only\n\n"

    # Find stations (reuse existing logic)
    origin_result = find_station_id(origin)
    if not origin_result["success"]:
        story += f"❌ Origin station not found: {origin}\n"
        return story

    dest_result = find_station_id(destination)
    if not dest_result["success"]:
        story += f"❌ Destination station not found: {destination}\n"
        return story

    # Format date
    api_datetime = get_formatted_date(departure_datetime)
    # Convert to date only (YYYY-MM-DD)
    date_str = api_datetime[:8]  # YYYYMMDD
    formatted_date = f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}"

    story += f"📍 Route: {origin_result['station_name']} → {dest_result['station_name']}\n"
    story += f"📅 Date: {formatted_date}\n\n"

    story += "─────────────────────────────────\n"
    story += "Attempting to fetch prices...\n"
    story += "─────────────────────────────────\n\n"

    # Attempt price check
    try:
        price_result = check_sncf_prices(
            origin_id=origin_result["station_id"],
            destination_id=dest_result["station_id"],
            date=formatted_date,
            page=page,
            per_page=per_page
        )

        # Format results
        formatted_output = format_price_results(price_result)
        story += formatted_output

    except Exception as e:
        story += f"❌ Price check failed: {str(e)}\n\n"
        story += "This feature is experimental and may not work.\n"
        story += "For real pricing, please visit:\n"
        story += "- SNCF Connect: https://www.sncf-connect.com\n"
        story += "- Or use commercial API providers\n"

    story += "\n═══════════════════════════════════\n"

    return story


# ============================================================================
# 4. Server Startup
# ============================================================================

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
