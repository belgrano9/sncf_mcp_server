# SNCF MCP Server 🚄

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for querying **SNCF** (French national railway) train schedules using the official Navitia API. Integrates seamlessly with Claude Desktop and other MCP-compatible clients.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-latest-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🔍 **Search trains** between any two French cities with real-time data
- 🚉 **Find stations** in any city across France
- 📅 **Flexible date parsing** - accepts ISO, European, and written date formats
- ⚡ **Real-time data** - uses official SNCF Navitia API with live timetables
- 🎯 **Smart journey planning** - shows transfers, duration, and route details
- 🌍 **International routes** - supports cross-border journeys (e.g., Paris-Munich)
- 🛠️ **Claude Desktop ready** - works out of the box with MCP clients

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- SNCF API key (free registration)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/belgrano9/sncf_mcp_server.git
   cd sncf_mcp_server
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Get your SNCF API key**
   - Register at [SNCF Digital API Portal](https://www.digital.sncf.com/startup/api)
   - Request access to the Navitia API
   - Copy your API key

4. **Configure environment variables**

   Create a `.env` file in the project root:
   ```env
   SNCF_API=your-api-key-here
   ```

   ⚠️ **IMPORTANT**: Never commit your `.env` file! It's already in `.gitignore`.

5. **Test the server**
   ```bash
   uv run server.py
   ```

## 📖 Usage

### Standalone Testing

Test the search functionality directly in Python:

```python
from server import search_trains, find_station

# Search for trains
result = search_trains("Paris", "Lyon", "2025-11-20 14:00")
print(result)

# Find a station
stations = find_station("Paris")
print(stations)
```

Or use the included Jupyter notebook (`test_notebook.ipynb`) for interactive testing.

### Claude Desktop Integration

Add to your Claude Desktop config file:

**Windows** (`%APPDATA%\Claude\claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "sncf": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\YourName\\path\\to\\sncf_mcp_server",
        "run",
        "server.py"
      ]
    }
  }
}
```

**macOS** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "sncf": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/sncf_mcp_server",
        "run",
        "server.py"
      ]
    }
  }
}
```

**Linux** (`~/.config/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "sncf": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/sncf_mcp_server",
        "run",
        "server.py"
      ]
    }
  }
}
```

Restart Claude Desktop, and you can ask:
- *"Show me trains from Paris to Lyon tomorrow at 2pm"*
- *"What's the earliest train from Paris Gare de l'Est to Munich tomorrow?"*
- *"Find all train stations in Paris"*
- *"How long does it take to get from Bordeaux to Marseille?"*

## 🛠️ MCP Tools

### 1. `search_trains`

Find trains between two stations with real-time data.

**Parameters:**
- `origin` (string): Origin station/city name (e.g., "Paris", "Lyon", "Paris Gare de l'Est")
- `destination` (string): Destination station/city name (e.g., "München Hbf", "Barcelona")
- `departure_datetime` (string, optional): Travel date/time in flexible formats:
  - ISO: `"2025-11-28 08:00"` (recommended)
  - European: `"28/11/2025 08:00"`
  - Written: `"November 28, 2025 8:00am"`
  - Default: current time

**Example Output:**
```
═══════════════════════════════════
    SNCF JOURNEY SEARCH
═══════════════════════════════════

🔍 Searched for 'Paris Est':
  ✓ Paris Gare de l'Est (ID: stop_area:SNCF:...)
    Paris - Bercy (ID: stop_area:SNCF:...)
    Paris Montparnasse (ID: stop_area:SNCF:...)

→ Selected: Paris Gare de l'Est

🔍 Searched for 'München Hbf':
  ✓ München Hauptbahnhof (ID: stop_area:OCE:...)

→ Selected: München Hauptbahnhof

📅 Searching for trains departing after: 2025-11-28 08:00
🔄 API datetime format: 20251128T080000

─────────────────────────────────
🚄 AVAILABLE TRAINS
─────────────────────────────────

Found 5 journey option(s):

  1. Depart: 2025-11-28 08:55 → Arrive: 2025-11-28 14:54
     Duration: 5h 59min | Direct

  2. Depart: 2025-11-28 10:55 → Arrive: 2025-11-28 16:54
     Duration: 5h 59min | Direct

  3. Depart: 2025-11-28 12:55 → Arrive: 2025-11-28 19:18
     Duration: 6h 23min | 1 change(s)
     Route: Paris Gare de l'Est → Stuttgart Hbf | Stuttgart Hbf → München Hbf

═══════════════════════════════════
```

### 2. `find_station`

Search for train stations in a city or by name.

**Parameters:**
- `station_name` (string): Station/city name to search (e.g., "Paris", "Lyon Part-Dieu")

**Example Output:**
```
═══════════════════════════════════
    STATION SEARCH
═══════════════════════════════════

🔍 Searched for 'Paris':
  ✓ Paris Gare de Lyon (ID: stop_area:SNCF:87686006)
    Paris Montparnasse (ID: stop_area:SNCF:87391003)
    Paris Gare du Nord (ID: stop_area:SNCF:87271007)

→ Selected: Paris Gare de Lyon

✅ Best match: Paris Gare de Lyon
   ID: stop_area:SNCF:87686006

═══════════════════════════════════
```

## 🏗️ Architecture

```
sncf_mcp_server/
├── server.py           # FastMCP server implementation
├── pyproject.toml      # Dependencies & project config
├── .env                # API key (not committed)
├── .gitignore          # Git ignore rules
├── README.md           # This file
└── test_notebook.ipynb # Jupyter notebook for testing
```

### How It Works

1. **Station Search**: Queries Navitia API's `/places` endpoint with fuzzy matching
2. **Journey Planning**: Uses `/journeys` endpoint with origin, destination, and datetime
3. **Date Parsing**: Flexible parser handles multiple date/time formats
4. **Response Formatting**: Returns human-readable journey information with:
   - Departure and arrival times
   - Journey duration
   - Number of transfers
   - Route details for multi-leg journeys

### Key Implementation Details

- ✅ Real-time data (no local database needed)
- ✅ Flexible date parsing with `python-dateutil`
- ✅ European date format support (day-first parsing)
- ✅ Automatic station ID resolution from city names
- ✅ Shows top 3 station matches for transparency
- ✅ Handles both domestic and international routes
- ✅ Transfer information with route breakdown

## 🌍 Supported Routes

The server supports **any route** in the SNCF/Navitia network:

- **High-Speed (TGV)**: Paris-Lyon, Paris-Marseille, Paris-Bordeaux, Paris-Strasbourg
- **International**: Paris-London (Eurostar), Paris-Munich, Paris-Barcelona, Paris-Brussels
- **Long-Distance (Intercités)**: Regional connections across France
- **TER (Regional Express)**: Local services
- **Cross-border**: Connections to Germany, Italy, Spain, Switzerland, Belgium

**Major Cities:**
- Paris (multiple stations: Gare du Nord, Gare de Lyon, Montparnasse, Est, Austerlitz, Saint-Lazare, Bercy)
- Lyon, Marseille, Bordeaux, Toulouse
- Strasbourg, Nantes, Nice, Lille
- International: London, Munich, Barcelona, Brussels, Geneva, Milan
- **1000+ stations** across France and Europe!

Use `find_station` to discover available stations in any city.

## 🔧 Development

### Project Setup

```bash
# Clone and install
git clone https://github.com/belgrano9/sncf_mcp_server.git
cd sncf_mcp_server
uv sync

# Set up your API key in .env
echo "SNCF_API=your-api-key-here" > .env

# Run the server
uv run server.py

# Or use FastMCP dev mode
fastmcp dev server.py
```

### Dependencies

- **fastmcp** - MCP server framework
- **requests** (>=2.32.5) - HTTP client for API calls
- **python-dotenv** (>=1.2.1) - Environment variable management
- **python-dateutil** - Flexible date/time parsing
- **httpx** (>=0.28.1) - Async HTTP client
- **loguru** (>=0.7.3) - Logging
- **rich** (>=14.2.0) - Terminal formatting

### File Structure

- `server.py` - Main MCP server with `search_trains` and `find_station` tools
- `.env` - API key configuration (never commit!)
- `test_notebook.ipynb` - Interactive testing notebook

## 📝 Data Source

Real-time data from [SNCF Navitia API](https://www.digital.sncf.com/startup/api):
- **API Base URL**: `https://api.sncf.com/v1`
- **Authentication**: HTTP Basic Auth (API key as username)
- **Coverage**: SNCF network across France and international connections
- **Update Frequency**: Real-time (no manual updates needed)
- **Format**: JSON responses
- **Documentation**: [Navitia API Docs](https://doc.navitia.io/)

### Getting an API Key

1. Visit [SNCF Digital](https://www.digital.sncf.com/startup/api)
2. Create an account
3. Request access to the Navitia API
4. Copy your API key to `.env`

## 🐛 Known Issues

- Windows console may show encoding errors with Unicode characters (functionality not affected)
- Station name matching uses first result - use `find_station` for ambiguous names
- International routes may have limited availability depending on API coverage

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Ideas for Contributions

- [ ] Add price information (if available in API)
- [ ] Support for train status/real-time delays
- [ ] Multi-leg journey optimization
- [ ] Visualization of routes on maps
- [ ] Additional query filters (train type, max transfers, etc.)
- [ ] Support for round-trip queries
- [ ] Save favorite routes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [SNCF](https://www.sncf.com) for providing the Navitia open API
- [FastMCP](https://github.com/jlowin/fastmcp) by [@jlowin](https://github.com/jlowin) for the excellent MCP framework
- [Anthropic](https://www.anthropic.com) for Claude and the Model Context Protocol
- [Navitia](https://www.navitia.io/) for powering the transit data API

## 📮 Support

- **Issues**: [GitHub Issues](https://github.com/belgrano9/sncf_mcp_server/issues)
- **API Documentation**: [Navitia API Docs](https://doc.navitia.io/)
- **MCP Docs**: [Model Context Protocol](https://modelcontextprotocol.io)

## 🔗 Related Projects

- [Renfe MCP Server](https://github.com/belgrano9/renfe_mcp_server/tree/master) - Similar server for Spanish railways
- [FastMCP](https://github.com/jlowin/fastmcp) - The framework powering this server
- [MCP Servers](https://github.com/modelcontextprotocol/servers) - Official MCP server implementations

---

**Built with ❤️ using [FastMCP](https://github.com/jlowin/fastmcp) and [Claude](https://claude.ai)**

*Voyagez intelligent, voyagez en train! 🚄*
