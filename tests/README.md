# SNCF MCP Server - Tests

This directory contains test scripts for the SNCF MCP server.

## Test Files

### Main Tests

- **`test_simple.py`** - Simple train search test without MCP wrapper
  - Tests direct API calls for train search
  - Searches Paris to Marseille tomorrow at 8 AM
  - Shows 10 journey options
  - Usage: `uv run tests/test_simple.py`

- **`test_pagination.py`** - Pagination feature test
  - Demonstrates pagination with 10 results per page
  - Shows multiple pages (1, 2, 3) of train results
  - Tests with 100 total journeys
  - Usage: `uv run tests/test_pagination.py`

- **`test_search.py`** - MCP tool wrapper test
  - Tests the search_trains MCP tool directly
  - Requires proper MCP setup
  - Usage: `uv run tests/test_search.py`

### Debug Scripts

- **`debug_api.py`** - API response debugging
  - Shows raw API responses
  - Tests different count parameters
  - Saves full API response to `api_response.json`
  - Usage: `uv run tests/debug_api.py`

- **`debug_env.py`** - Environment variable debugging
  - Tests .env file loading
  - Checks if SNCF_API key is properly loaded
  - Usage: `uv run tests/debug_env.py`

- **`debug_env2.py`** - Advanced .env debugging
  - Tests dotenv_values vs load_dotenv
  - Shows all SNCF-related environment variables
  - Usage: `uv run tests/debug_env2.py`

## Running Tests

### Prerequisites

1. Make sure you have a valid SNCF API key in `.env` file:
   ```
   SNCF_API=your-api-key-here
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

### Run All Tests

```bash
# From project root
uv run tests/run_all_tests.py
```

### Run Individual Tests

```bash
# Simple train search
uv run tests/test_simple.py

# Pagination test
uv run tests/test_pagination.py

# MCP wrapper test
uv run tests/test_search.py
```

## Expected Behavior

All tests should:
- Successfully load the SNCF API key from .env
- Connect to the SNCF Navitia API
- Return train journey results
- Handle pagination correctly (for pagination test)

If tests fail, check:
1. `.env` file exists with valid SNCF_API key
2. Internet connection is working
3. SNCF API is accessible
4. No environment variable conflicts (run `debug_env2.py`)

## Notes

- Tests use `unset SNCF_API` before running to ensure clean .env loading
- Windows users may see Unicode encoding warnings (these don't affect functionality)
- API responses are cached for 15 minutes by the SNCF API
