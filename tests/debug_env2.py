#!/usr/bin/env python3
"""Debug .env file loading with dotenv_values."""

import os
from dotenv import dotenv_values, load_dotenv

print("=== Using dotenv_values ===")
config = dotenv_values(".env")
print(f"Config dict: {config}")
print(f"SNCF_API from dict: '{config.get('SNCF_API', 'NOT FOUND')}'")
print()

print("=== Using load_dotenv ===")
load_dotenv(verbose=True, override=True)
print(f"SNCF_API from os.getenv: '{os.getenv('SNCF_API', 'NOT FOUND')}'")
print()

print("=== All environment variables with SNCF ===")
for key, value in os.environ.items():
    if 'SNCF' in key.upper():
        print(f"{key} = {value}")
