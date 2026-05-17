---
name: domi-cli
description: CLI for the DOMI Obstruction MCP server. Call tools, list resources, and get prompts.
---

# DOMI Obstruction CLI

Command-line interface for querying Pittsburgh DOMI road obstruction and closure data.

## Installation

```bash
# Install dependencies
uv pip install fastmcp cyclopts rich mcp

# Or use uv directly (it will handle dependencies)
uv run --with fastmcp python cli.py list-tools
```

## Quick Start

```bash
# List all available tools
python cli.py list-tools

# Get count of obstructions
python cli.py call-tool obstruction_count

# Search for obstructions on Fifth Avenue
python cli.py call-tool search_obstructions --q "Fifth Avenue"

# List active closures
python cli.py call-tool list_active_entries --limit 50

# Match obstructions along a GPX route
python cli.py match-gpx --path "route.gpx"

# Match obstructions along a GPX route
python cli.py match-gpx --path "route.gpx"
```

## Tool Commands

### search_obstructions

Search DOMI obstruction/closure records with optional filters and text search.

```bash
python cli.py call-tool search_obstructions [OPTIONS]
```

**Options:**
- `--limit INTEGER` - Max records to return (default: 100)
- `--offset INTEGER` - Number of records to skip for pagination (default: 0)
- `--q TEXT` - Full-text search query
- `--filters TEXT` - JSON object of field filters

**Examples:**

```bash
# Search by street name
python cli.py call-tool search_obstructions --q "Fifth Avenue"

# Search with exact street match
python cli.py call-tool search_obstructions --filters '{"primary_street": "FIFTH AVE"}'

# Search for construction work
python cli.py call-tool search_obstructions --q "construction" --limit 50

# Combine search and filter for active entries
python cli.py call-tool search_obstructions --q "paving" --filters '{"active": true}'
```

### list_active_entries

List only currently active obstruction/closure entries.

```bash
python cli.py call-tool list_active_entries [OPTIONS]
```

**Options:**
- `--limit INTEGER` - Max records to return (default: 100)
- `--offset INTEGER` - Skip this many records (default: 0)

**Examples:**

```bash
# Get first 100 active entries
python cli.py call-tool list_active_entries

# Get next 50 active entries
python cli.py call-tool list_active_entries --limit 50 --offset 100
```

### match-gpx

Find active DOMI records matching a GPX route.

```bash
# Prompt for path
python cli.py match-gpx

# Direct path
python cli.py match-gpx --path "route.gpx"

# Custom distance threshold
python cli.py match-gpx --path "route.gpx" --distance-threshold 0.0005
```

### obstruction_count

Get total number of obstruction records in the dataset.

```bash
python cli.py call-tool obstruction_count
```

### match-gpx

Find active DOMI records matching a GPX route.

```bash
# Prompt for path
python cli.py match-gpx

# Direct path
python cli.py match-gpx --path "route.gpx"

# Custom distance threshold
python cli.py match-gpx --path "route.gpx" --distance-threshold 0.0005
```

### refresh_data

Refresh cached data from WPRDC source (admin operation).

```bash
python cli.py call-tool refresh_data [OPTIONS]
```

**Options:**
- `--max-records INTEGER` - Cap on number of records to ingest

**Examples:**

```bash
# Refresh all data
python cli.py call-tool refresh_data

# Refresh with limit
python cli.py call-tool refresh_data --max-records 1000
```

## Utility Commands

```bash
# List available tools
python cli.py list-tools

# List available resources
python cli.py list-resources

# Read a specific resource
python cli.py read-resource <uri>

# List available prompts
python cli.py list-prompts

# Get a prompt with arguments
python cli.py get-prompt <name> [key=value ...]
```

## Using with UV

If you have `uv` installed, you can run without installing dependencies:

```bash
uv run --with fastmcp python cli.py list-tools
uv run --with fastmcp python cli.py call-tool search_obstructions --q "Forbes"
```

## Output Format

All tool calls return JSON output with syntax highlighting:

```json
{
  "success": true,
  "result": {
    "records": [...],
    "total": 1234,
    "fields": [...],
    "records_format": "objects"
  }
}
```

## Common Workflows

### Find Active Closures on a Street

```bash
python cli.py call-tool search_obstructions \
  --q "Fifth Avenue" \
  --filters '{"active": true}'
```

### Get All Historical Data for Analysis

```bash
# Get count first
python cli.py call-tool obstruction_count

# Fetch in batches
python cli.py call-tool search_obstructions --limit 500 --offset 0 > batch1.json
python cli.py call-tool search_obstructions --limit 500 --offset 500 > batch2.json
```

### Monitor Daily Closures

```bash
# Add to cron job
0 8 * * * cd /path/to/cli && python cli.py call-tool list_active_entries > daily_closures.json
```

## Troubleshooting

**Connection errors**: Verify the server URL in `cli.py`:
```python
CLIENT_SPEC = 'https://domi-obstruction.fly.dev/mcp'
```

**JSON parsing errors**: Ensure filters are valid JSON:
```bash
# Good
--filters '{"primary_street": "FIFTH AVE"}'

# Bad (missing quotes)
--filters '{primary_street: FIFTH AVE}'
```

**No results**: Try broader search terms or remove filters.
