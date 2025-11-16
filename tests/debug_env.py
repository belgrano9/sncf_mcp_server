#!/usr/bin/env python3
"""Debug .env file loading."""

import os
from dotenv import load_dotenv

print("Current directory:", os.getcwd())
print(".env file path:", os.path.join(os.getcwd(), ".env"))
print(".env exists:", os.path.exists(".env"))
print()

load_dotenv()

api_key = os.getenv("SNCF_API")
print(f"SNCF_API value: '{api_key}'")
print(f"Type: {type(api_key)}")
print(f"Is None: {api_key is None}")
print(f"Is empty: {api_key == ''}")
print(f"Truthiness: {bool(api_key)}")

if api_key:
    print(f"Length: {len(api_key)}")
    print(f"Repr: {repr(api_key)}")
