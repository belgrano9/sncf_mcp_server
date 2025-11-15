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


def search_journeys_with_context(origin_id, dest_id, departure_time):
    """
    Queries the API for journeys and returns formatted results with context.
    Returns a string with the journey options formatted for Claude to read.
    """
    if not origin_id or not dest_id:
        return "❌ Missing Origin or Destination ID. Cannot search for journeys."

    try:
        response = api_get(
            "coverage/sncf/journeys",
            params={"from": origin_id, "to": dest_id, "datetime": departure_time},
        )

        journeys = response.get("journeys", [])

        if not journeys:
            return "❌ No journeys found for this route and time. Try a different time or date."

        # Build the journey list
        result = f"Found {len(journeys)} journey option(s):\n\n"

        for i, journey in enumerate(journeys[:5]):  # Limit to top 5
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
def search_trains(origin: str, destination: str, departure_datetime: str = None) -> str:
    """
    Search for train journeys between two stations.

    Args:
        origin: Starting station name (e.g., "Paris Est", "Lyon")
        destination: Destination station name (e.g., "München Hbf", "Barcelona")
        departure_datetime: Optional datetime. Accepts flexible formats:
                           - ISO: "2025-11-28 08:00" (RECOMMENDED)
                           - European: "28/11/2025 08:00"
                           - Written: "November 28, 2025 8:00am"
                           If not provided, searches from current time.
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
        origin_result["station_id"], dest_result["station_id"], api_datetime
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


# ============================================================================
# 4. Server Startup
# ============================================================================

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
