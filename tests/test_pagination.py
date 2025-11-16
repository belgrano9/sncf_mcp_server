#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test pagination feature for SNCF train search."""

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

def search_trains_paginated(paris_id, marseille_id, datetime_str, page=1):
    """Search trains with pagination."""
    per_page = 10

    # Fetch 100 journeys
    response = api_get(
        "coverage/sncf/journeys",
        params={
            "from": paris_id,
            "to": marseille_id,
            "datetime": datetime_str,
            "count": 100
        }
    )

    journeys = response.get("journeys", [])
    total_journeys = len(journeys)
    total_pages = (total_journeys + per_page - 1) // per_page

    if page < 1 or page > total_pages:
        return None, total_journeys, total_pages

    # Get page slice
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_journeys)
    page_journeys = journeys[start_idx:end_idx]

    return page_journeys, total_journeys, total_pages, start_idx, end_idx

# Calculate tomorrow at 8 AM
tomorrow = datetime.now() + timedelta(days=1)
datetime_str = tomorrow.strftime("%Y%m%dT080000")

print("=" * 70)
print("SNCF Train Search with Pagination")
print(f"Route: Paris to Marseille | Date: {tomorrow.strftime('%Y-%m-%d 08:00')}")
print("=" * 70)
print()

# Find stations
paris_id, paris_name = find_station("Paris")
marseille_id, marseille_name = find_station("Marseille")

print(f"Origin: {paris_name}")
print(f"Destination: {marseille_name}")
print()

# Test different pages
for page_num in [1, 2, 3]:
    result = search_trains_paginated(paris_id, marseille_id, datetime_str, page_num)

    if result[0] is None:
        print(f"Page {page_num}: Invalid page number")
        continue

    page_journeys, total_journeys, total_pages, start_idx, end_idx = result

    print("-" * 70)
    print(f"PAGE {page_num}/{total_pages}")
    print(f"Showing results {start_idx + 1}-{end_idx} of {total_journeys} journeys")
    print("-" * 70)

    for i, journey in enumerate(page_journeys, start=start_idx + 1):
        dep = journey["departure_date_time"]
        arr = journey["arrival_date_time"]

        dep_time = f"{dep[0:4]}-{dep[4:6]}-{dep[6:8]} {dep[9:11]}:{dep[11:13]}"
        arr_time = f"{arr[0:4]}-{arr[4:6]}-{arr[6:8]} {arr[9:11]}:{arr[11:13]}"

        duration_sec = journey["duration"]
        hours = duration_sec // 3600
        mins = (duration_sec % 3600) // 60

        transfers = journey.get("nb_transfers", 0)
        transfer_text = "Direct" if transfers == 0 else f"{transfers} transfer(s)"

        print(f"  {i}. {dep_time} -> {arr_time} | {hours}h {mins}min | {transfer_text}")

    print()

print("=" * 70)
print(f"Total journeys available: {total_journeys}")
print(f"Total pages (10 per page): {total_pages}")
print("=" * 70)
