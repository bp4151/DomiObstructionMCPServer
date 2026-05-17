# DOMI Obstruction CLI

Command-line interface for the DOMI Obstruction MCP Server.

## Quick Start

```bash
# List available tools
python cli.py list-tools

# Search for road closures
python cli.py call-tool search_obstructions --q "Fifth Avenue"

# Get active closures
python cli.py call-tool list_active_entries

# Find obstructions along a GPX route
python cli.py match-gpx --path "route.gpx"

# Get total count
python cli.py call-tool obstruction_count

# Find obstructions along a GPX route
python cli.py match-gpx --path "route.gpx"
```

## Installation

### Linux/macOS/WSL

#### Using the installer (Recommended)

```bash
bash install_cli.sh
```

#### Using UV

```bash
uv run --with fastmcp python cli.py list-tools
```

#### Traditional Installation

```bash
pip install fastmcp cyclopts rich mcp
python cli.py list-tools
```

### Windows

#### Using PowerShell installer (Recommended)

```powershell
powershell -ExecutionPolicy Bypass -File install_cli.ps1
```

See `WINDOWS_INSTALL.md` for detailed Windows instructions.

#### Manual Installation

```powershell
pip install fastmcp cyclopts rich mcp
python cli.py list-tools
```

## Common Commands

### Search by street name
```bash
python cli.py call-tool search_obstructions --q "Forbes Avenue"
```

### Search with exact filter
```bash
python cli.py call-tool search_obstructions --filters '{"primary_street": "FIFTH AVE"}'
```

### Get active closures only
```bash
python cli.py call-tool list_active_entries --limit 50
```

### Match obstructions along a GPX route
```bash
# Prompt for file path
python cli.py match-gpx

# Provide file path directly
python cli.py match-gpx --path "my_route.gpx"

# Use a custom distance threshold (in degrees)
python cli.py match-gpx --path "my_route.gpx" --distance-threshold 0.0005
```

### Combine search and filter
```bash
python cli.py call-tool search_obstructions \
  --q "construction" \
  --filters '{"active": true}'
```

### Match obstructions along a GPX route
```bash
# Prompt for file path
python cli.py match-gpx

# Provide file path directly
python cli.py match-gpx --path "my_route.gpx"

# Use a custom distance threshold (in degrees)
python cli.py match-gpx --path "my_route.gpx" --distance-threshold 0.0005
```

## Output to File

```bash
# Save results to JSON
python cli.py call-tool list_active_entries > closures.json

# Use with jq for parsing
python cli.py call-tool search_obstructions --q "Forbes" | jq '.result.records'
```

## Configuration

Edit `CLIENT_SPEC` in `cli.py` to change the server URL:

```python
CLIENT_SPEC = 'https://domi-obstruction.fly.dev/mcp'  # Production
# CLIENT_SPEC = 'http://localhost:8000/mcp'  # Local development
```

## Documentation

- **Detailed usage guide**: See [CLI_USAGE.md](CLI_USAGE.md)
- **Server documentation**: See [README_SERVER.md](README_SERVER.md)
- **Cursor skill**: See [../.cursor/skills/domi-obstruction-mcp/SKILL.md](../.cursor/skills/domi-obstruction-mcp/SKILL.md)

## Help

```bash
python cli.py --help
python cli.py call-tool --help
python cli.py call-tool search_obstructions --help
```
