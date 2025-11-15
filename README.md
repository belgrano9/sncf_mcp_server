# SNCF MCP Server

A Model Context Protocol (MCP) server that provides access to SNCF (French National Railway) transportation data through the Navitia API.

## Setup

### 1. Install Dependencies

This project uses `uv` for Python package management:

```bash
uv sync
```

### 2. Configure API Key

Create a `.env` file in the project root with your SNCF API key:

```
SNCF_API=your-api-key-here
```

You can get an API key by registering at: https://www.sncf.com/fr/api

### 3. Configure Claude Desktop

Add this MCP server to your Claude Desktop configuration file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sncf": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\tomso\\workspace\\sncf_mcp",
        "run",
        "main.py"
      ]
    }
  }
}
```

Note: Update the path in `--directory` to match your actual repository location.

### 4. Restart Claude Desktop

After updating the configuration, restart Claude Desktop for the changes to take effect.

## Available Tools

### `get_coverage`

Get SNCF network coverage information including production status and geographical coverage.

**Usage in Claude:**
```
Can you check the SNCF network coverage?
```

## API Reference

This server uses the SNCF Open API powered by Navitia:
- Base URL: https://api.sncf.com/v1
- Documentation: https://www.digital.sncf.com/startup/api
- Authentication: HTTP Basic Auth (API key as username, empty password)

## Development

To test the server locally, you can use either of these commands:

### Run the server directly:
```bash
uv run .\server.py
```

### Run with FastMCP development mode:
```bash
fastmcp dev server.py
```

The server communicates via stdio following the MCP protocol.
