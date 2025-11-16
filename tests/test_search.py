#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick test script for searching trains from Paris to Marseille tomorrow."""

import sys
from datetime import datetime, timedelta
from server import search_trains

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Calculate tomorrow's date at 8:00 AM
tomorrow = datetime.now() + timedelta(days=1)
tomorrow_str = tomorrow.strftime("%Y-%m-%d 08:00")

print("Testing SNCF Train Search")
print("=" * 50)
print(f"Searching: Paris to Marseille")
print(f"Date: {tomorrow_str}")
print("=" * 50)
print()

# Search for trains
result = search_trains("Paris", "Marseille", tomorrow_str)
print(result)
