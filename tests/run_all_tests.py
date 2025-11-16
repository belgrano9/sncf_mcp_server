#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run all SNCF MCP server tests."""

import sys
import subprocess
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Get tests directory
tests_dir = Path(__file__).parent

# Define tests to run
tests = [
    ("Environment Check", "debug_env2.py"),
    ("Simple Train Search", "test_simple.py"),
    ("Pagination Test", "test_pagination.py"),
]

print("=" * 80)
print("SNCF MCP Server - Test Suite")
print("=" * 80)
print()

results = []

for test_name, test_file in tests:
    print("-" * 80)
    print(f"Running: {test_name}")
    print(f"File: {test_file}")
    print("-" * 80)

    test_path = tests_dir / test_file

    try:
        # Run test with uv
        result = subprocess.run(
            ["uv", "run", str(test_path)],
            capture_output=False,
            text=True,
            timeout=60,
            env={**subprocess.os.environ, "SNCF_API": ""}  # Unset SNCF_API
        )

        if result.returncode == 0:
            print(f"\n✅ {test_name} PASSED")
            results.append((test_name, "PASSED"))
        else:
            print(f"\n❌ {test_name} FAILED (exit code {result.returncode})")
            results.append((test_name, "FAILED"))

    except subprocess.TimeoutExpired:
        print(f"\n⏱️  {test_name} TIMEOUT")
        results.append((test_name, "TIMEOUT"))

    except Exception as e:
        print(f"\n❌ {test_name} ERROR: {e}")
        results.append((test_name, "ERROR"))

    print()

# Summary
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)

passed = sum(1 for _, status in results if status == "PASSED")
total = len(results)

for test_name, status in results:
    status_icon = "✅" if status == "PASSED" else "❌"
    print(f"{status_icon} {test_name}: {status}")

print()
print(f"Results: {passed}/{total} tests passed")
print("=" * 80)

# Exit with appropriate code
sys.exit(0 if passed == total else 1)
