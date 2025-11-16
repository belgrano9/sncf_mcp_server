# Test Organization Summary

## What Changed

All test and debug files have been organized into the `tests/` directory for better project structure.

## Files Moved

- `test_simple.py` → `tests/test_simple.py`
- `test_search.py` → `tests/test_search.py`
- `test_pagination.py` → `tests/test_pagination.py`
- `debug_api.py` → `tests/debug_api.py`
- `debug_env.py` → `tests/debug_env.py`
- `debug_env2.py` → `tests/debug_env2.py`

## New Files Added

- `tests/__init__.py` - Makes tests a Python package
- `tests/README.md` - Comprehensive test documentation
- `tests/run_all_tests.py` - Automated test runner
- `tests/SUMMARY.md` - This file

## Updated Files

- `.gitignore` - Added test output files (api_response.json)
- `README.md` - Updated architecture section and added testing documentation

## Project Structure

```
sncf_mcp_server/
├── server.py              # Main MCP server
├── pyproject.toml         # Dependencies
├── .env                   # API key (gitignored)
├── README.md              # Main documentation
└── tests/                 # Test suite
    ├── __init__.py
    ├── README.md          # Test documentation
    ├── SUMMARY.md         # This file
    ├── run_all_tests.py   # Test runner
    ├── test_simple.py     # Simple search test
    ├── test_pagination.py # Pagination test
    ├── test_search.py     # MCP wrapper test
    ├── debug_api.py       # API debugging
    ├── debug_env.py       # Env debugging
    └── debug_env2.py      # Advanced env debugging
```

## How to Run Tests

```bash
# From project root
uv run tests/run_all_tests.py

# Individual tests
uv run tests/test_simple.py
uv run tests/test_pagination.py
```

## Benefits

- ✅ Cleaner project root directory
- ✅ All tests in one place
- ✅ Better organization for CI/CD
- ✅ Easier to find and run tests
- ✅ Proper test documentation
