#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple test for SNCF API without MCP wrapper."""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Load environment
load_dotenv(override=True)
SNCF_API_KEY = os.getenv("SNCF_API")

if not SNCF_API_KEY:
    print("ERROR: SNCF_API key not found!")
    sys.exit(1)

BASE_URL = "https://api.sncf.com/v1"

def api_get(endpoint, params=None):
    """Make a GET request to the SNCF API."""
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(
        url, auth=(SNCF_API_KEY, ""), params=params, timeout=30
    )
    response.raise_for_status()
    return response.json()

def find_station(name):
    """Find station ID by name, preferring train stations."""
    response = api_get("coverage/sncf/places", params={"q": name})
    places = response.get("places", [])

    # Try to find a stop_area (train station) first
    for place in places:
        if place.get("embedded_type") == "stop_area":
            return place["id"], place["name"]

    # Otherwise return first result
    if places:
        return places[0]["id"], places[0]["name"]
    return None, None

# Calculate tomorrow at 8 AM
tomorrow = datetime.now() + timedelta(days=1)
datetime_str = tomorrow.strftime("%Y%m%dT080000")

print("=" * 60)
print("SNCF Train Search: Paris to Marseille")
print(f"Date: {tomorrow.strftime('%Y-%m-%d 08:00')}")
print("=" * 60)
print()

# Find stations
print("Finding stations...")
paris_id, paris_name = find_station("Paris")
marseille_id, marseille_name = find_station("Marseille")

print(f"Origin: {paris_name} ({paris_id})")
print(f"Destination: {marseille_name} ({marseille_id})")
print()

# Search trains
print("Searching for trains...")
response = api_get(
    "coverage/sncf/journeys",
    params={
        "from": paris_id,
        "to": marseille_id,
        "datetime": datetime_str,
        "count": 10  # Request 10 journey options
    }
)

journeys = response.get("journeys", [])

if not journeys:
    print("No trains found!")
else:
    print(f"Found {len(journeys)} journey options:")
    print()

    for i, journey in enumerate(journeys, 1):
        # Extract times
        dep = journey["departure_date_time"]
        arr = journey["arrival_date_time"]

        # Format nicely
        dep_time = f"{dep[0:4]}-{dep[4:6]}-{dep[6:8]} {dep[9:11]}:{dep[11:13]}"
        arr_time = f"{arr[0:4]}-{arr[4:6]}-{arr[6:8]} {arr[9:11]}:{arr[11:13]}"

        # Duration
        duration_sec = journey["duration"]
        hours = duration_sec // 3600
        mins = (duration_sec % 3600) // 60

        # Transfers
        transfers = journey.get("nb_transfers", 0)
        transfer_text = "Direct" if transfers == 0 else f"{transfers} transfer(s)"

        print(f"  {i}. Depart: {dep_time} -> Arrive: {arr_time}")
        print(f"     Duration: {hours}h {mins}min | {transfer_text}")
        print()

print("=" * 60)
