#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug API response to see why only 1 journey is returned."""

import os
import sys
import json
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
    print(f"\n[DEBUG] Request URL: {url}")
    print(f"[DEBUG] Params: {params}")

    response = requests.get(
        url, auth=(SNCF_API_KEY, ""), params=params, timeout=30
    )
    response.raise_for_status()
    return response.json()

# Find Paris and Marseille stations
print("Finding stations...")
paris_response = api_get("coverage/sncf/places", params={"q": "Paris"})
marseille_response = api_get("coverage/sncf/places", params={"q": "Marseille"})

# Get first stop_area for each
paris_id = None
marseille_id = None

for place in paris_response.get("places", []):
    if place.get("embedded_type") == "stop_area":
        paris_id = place["id"]
        print(f"Paris: {place['name']} ({paris_id})")
        break

for place in marseille_response.get("places", []):
    if place.get("embedded_type") == "stop_area":
        marseille_id = place["id"]
        print(f"Marseille: {place['name']} ({marseille_id})")
        break

# Calculate tomorrow at 8 AM
tomorrow = datetime.now() + timedelta(days=1)
datetime_str = tomorrow.strftime("%Y%m%dT080000")

print(f"\nSearching for trains on {tomorrow.strftime('%Y-%m-%d')} at 08:00")

# Search trains with default parameters
print("\n" + "="*60)
print("TEST 1: Default search")
print("="*60)
response = api_get(
    "coverage/sncf/journeys",
    params={"from": paris_id, "to": marseille_id, "datetime": datetime_str}
)

print(f"\n[DEBUG] Number of journeys in response: {len(response.get('journeys', []))}")
print(f"[DEBUG] Response keys: {list(response.keys())}")

# Check if there are pagination links
if 'links' in response:
    print(f"[DEBUG] Links in response: {response['links']}")

# Print first journey details
if response.get('journeys'):
    j = response['journeys'][0]
    print(f"\n[DEBUG] First journey keys: {list(j.keys())}")
    print(f"[DEBUG] Departure: {j['departure_date_time']}")
    print(f"[DEBUG] Arrival: {j['arrival_date_time']}")

# Try with count parameter to request more results
print("\n" + "="*60)
print("TEST 2: With count=10 parameter")
print("="*60)
response2 = api_get(
    "coverage/sncf/journeys",
    params={
        "from": paris_id,
        "to": marseille_id,
        "datetime": datetime_str,
        "count": 10
    }
)

print(f"[DEBUG] Number of journeys with count=10: {len(response2.get('journeys', []))}")

# Print all journey times
for i, journey in enumerate(response2.get('journeys', []), 1):
    dep = journey["departure_date_time"]
    arr = journey["arrival_date_time"]
    dep_time = f"{dep[0:4]}-{dep[4:6]}-{dep[6:8]} {dep[9:11]}:{dep[11:13]}"
    arr_time = f"{arr[0:4]}-{arr[4:6]}-{arr[6:8]} {arr[9:11]}:{arr[11:13]}"
    print(f"  {i}. {dep_time} -> {arr_time}")

# Save full response for inspection
with open('api_response.json', 'w', encoding='utf-8') as f:
    json.dump(response2, f, indent=2, ensure_ascii=False)
    print(f"\n[DEBUG] Full API response saved to api_response.json")
