# DOMI Obstruction CLI - Usage Guide

Complete guide for using the DOMI Obstruction MCP command-line interface.

## Installation

### Option 1: Using UV (Recommended)

```bash
# No installation needed - UV handles dependencies automatically
uv run --with fastmcp python cli.py list-tools
```

### Option 2: Traditional Installation

```bash
# Install dependencies
pip install fastmcp cyclopts rich mcp

# Run CLI
python cli.py list-tools
```

### Option 3: Poetry/PDM

```bash
# If your project uses poetry
poetry add fastmcp cyclopts rich mcp
poetry run python cli.py list-tools
```

## Configuration

The CLI connects to the MCP server via the `CLIENT_SPEC` variable in `cli.py`:

```python
CLIENT_SPEC = 'https://domi-obstruction.fly.dev/mcp'
```

To use a local server, change to:

```python
CLIENT_SPEC = 'http://localhost:8000/mcp'
```

## Command Reference

### General Commands

#### list-tools
List all available MCP tools with their signatures.

```bash
python cli.py list-tools
```

**Output:**
```
search_obstructions(limit: int = ..., offset: int = ..., q: string = ..., filters: string = ...)
  Search DOMI obstruction/closure records from WPRDC.

list_active_entries(limit: int = ..., offset: int = ...)
  List all active DOMI obstruction/closure entries.

obstruction_count()
  Return total number of DOMI obstruction records.

match_gpx_obstructions(gpx_content: string, distance_threshold: number = ...)
  Find active DOMI records that match route segments in a GPX file.

refresh_data(max_records: string = ...)
  Refresh cached obstruction data from WPRDC.
```

#### list-resources
List available MCP resources.

```bash
python cli.py list-resources
```

#### list-prompts
List available MCP prompts.

```bash
python cli.py list-prompts
```

### Tool Commands

All tool commands follow the pattern:
```bash
python cli.py call-tool <tool-name> [OPTIONS]
```

#### search_obstructions

Search all obstruction records with filtering and pagination.

**Basic search:**
```bash
# Search by keyword
python cli.py call-tool search_obstructions --q "Fifth Avenue"

# Search for construction
python cli.py call-tool search_obstructions --q "construction"

# Search for specific permit
python cli.py call-tool search_obstructions --q "P202401234"
```

**Exact filters:**
```bash
# Filter by street name (exact match)
python cli.py call-tool search_obstructions \
  --filters '{"primary_street": "FIFTH AVE"}'

# Filter for active closures only
python cli.py call-tool search_obstructions \
  --filters '{"active": true}'

# Multiple filters
python cli.py call-tool search_obstructions \
  --filters '{"primary_street": "FIFTH AVE", "active": true}'
```

**Pagination:**
```bash
# First 50 results
python cli.py call-tool search_obstructions --limit 50 --offset 0

# Next 50 results
python cli.py call-tool search_obstructions --limit 50 --offset 50

# Get 100 results starting from position 200
python cli.py call-tool search_obstructions --limit 100 --offset 200
```

**Combined queries:**
```bash
# Search + filter + pagination
python cli.py call-tool search_obstructions \
  --q "water main" \
  --filters '{"active": true}' \
  --limit 25
```

#### list_active_entries

Get only currently active obstructions.

```bash
# Get all active entries (up to 100)
python cli.py call-tool list_active_entries

# Paginate through active entries
python cli.py call-tool list_active_entries --limit 50 --offset 0
python cli.py call-tool list_active_entries --limit 50 --offset 50
```

#### obstruction_count

Get total count of records.

```bash
python cli.py call-tool obstruction_count
```

**Output:**
```json
{
  "total": 1234
}
```

#### match-gpx (Custom Command)

Find active DOMI records matching a route defined in a GPX file. This is a high-level command that handles file reading and spatial matching.

```bash
# Basic usage (prompts for path if not provided)
python cli.py match-gpx

# Direct path
python cli.py match-gpx --path "route.gpx"

# Custom threshold (~50m instead of default ~10m)
python cli.py match-gpx --path "route.gpx" --distance-threshold 0.0005
```

#### refresh_data

Admin command to refresh cached data.

```bash
# Refresh all data
python cli.py call-tool refresh_data

# Refresh with limit
python cli.py call-tool refresh_data --max-records 1000
```

## Output and Piping

All commands output JSON that can be piped to other tools:

```bash
# Save to file
python cli.py call-tool list_active_entries > active_closures.json

# Use with jq
python cli.py call-tool search_obstructions --q "Forbes" | jq '.result.records'

# Count results
python cli.py call-tool search_obstructions --q "construction" | jq '.result.total'

# Extract specific field
python cli.py call-tool list_active_entries | jq '.result.records[].primary_street'
```

## Common Use Cases

### 1. Daily Closure Report

Create a daily report of active closures:

```bash
#!/bin/bash
# daily_report.sh

echo "DOMI Daily Closure Report - $(date)"
echo "========================================"

# Get active closures
python cli.py call-tool list_active_entries --limit 1000 \
  | jq -r '.result.records[] | "\(.primary_street): \(.work_description)"'
```

Run daily with cron:
```cron
0 8 * * * /path/to/daily_report.sh > /path/to/reports/$(date +\%Y\%m\%d).txt
```

### 2. Street Impact Analysis

Find all historical closures for a street:

```bash
#!/bin/bash
# analyze_street.sh

STREET=$1

python cli.py call-tool search_obstructions \
  --filters "{\"primary_street\": \"$STREET\"}" \
  --limit 1000 \
  | jq '.result.records | length'
```

Usage:
```bash
bash analyze_street.sh "FIFTH AVE"
```

### 3. Export All Data

Paginate through entire dataset:

```bash
#!/bin/bash
# export_all.sh

LIMIT=500
OFFSET=0
OUTPUT_DIR="./data"

mkdir -p $OUTPUT_DIR

# Get total count
TOTAL=$(python cli.py call-tool obstruction_count | jq '.total')
echo "Total records: $TOTAL"

while [ $OFFSET -lt $TOTAL ]; do
  echo "Fetching records $OFFSET to $(($OFFSET + $LIMIT))..."
  
  python cli.py call-tool search_obstructions \
    --limit $LIMIT \
    --offset $OFFSET \
    > "$OUTPUT_DIR/batch_$OFFSET.json"
  
  OFFSET=$(($OFFSET + $LIMIT))
  sleep 1  # Be nice to the server
done

echo "Export complete!"
```

### 4. Monitor Specific Applicant

Track permits by applicant:

```bash
python cli.py call-tool search_obstructions \
  --q "ALCOSAN" \
  --limit 100 \
  | jq '.result.records[] | {street: .primary_street, dates: .start_date + " to " + .end_date}'
```

### 5. Active vs Total Statistics

```bash
#!/bin/bash
# stats.sh

TOTAL=$(python cli.py call-tool obstruction_count | jq '.total')
ACTIVE=$(python cli.py call-tool list_active_entries --limit 9999 | jq '.result.total')

echo "Total records: $TOTAL"
echo "Active closures: $ACTIVE"
echo "Percentage active: $(echo "scale=2; $ACTIVE * 100 / $TOTAL" | bc)%"
```

## Error Handling

### Connection Errors

If you see connection errors:

```
Error: Could not connect to https://domi-obstruction.fly.dev/mcp
```

Check:
1. Server is running: `curl https://domi-obstruction.fly.dev/mcp`
2. Network connectivity
3. CLIENT_SPEC in `cli.py` is correct

### JSON Parsing Errors

If filters fail to parse:

```
Error: Invalid filters JSON: Expecting property name enclosed in double quotes
```

Ensure proper JSON formatting:
- ✅ Good: `'{"key": "value"}'`
- ❌ Bad: `'{key: value}'`
- ❌ Bad: `"{\"key\": \"value\"}"`  (unless you escape quotes properly)

### No Results

If you get no results:
1. Try broader search terms
2. Check spelling (especially street names)
3. Try without filters first
4. Use `obstruction_count` to verify data exists

## Advanced Usage

### Custom Output Formatting

Create a wrapper script for formatted output:

```bash
#!/bin/bash
# pretty_search.sh

python cli.py call-tool search_obstructions "$@" | \
  jq -r '.result.records[] | "📍 \(.primary_street)\n   🚧 \(.work_description)\n   📅 \(.start_date) → \(.end_date)\n"'
```

Usage:
```bash
bash pretty_search.sh --q "Forbes"
```

### CSV Export

Convert JSON to CSV:

```bash
python cli.py call-tool list_active_entries --limit 1000 | \
  jq -r '.result.records[] | [.closure_id, .primary_street, .start_date, .end_date, .work_description] | @csv' \
  > active_closures.csv
```

### Integration with Other Tools

**SQLite:**
```bash
# Export to SQLite
python cli.py call-tool search_obstructions --limit 5000 | \
  jq -r '.result.records[]' | \
  sqlite3 closures.db ".import /dev/stdin closures"
```

**PostgreSQL:**
```bash
# Export to PostgreSQL via psql
python cli.py call-tool search_obstructions --limit 5000 | \
  jq -c '.result.records[]' | \
  psql -d mydb -c "COPY closures FROM STDIN WITH (FORMAT json)"
```

## Development

### Modifying the CLI

The CLI is generated from the MCP server schema. To regenerate:

```bash
fastmcp generate-cli https://domi-obstruction.fly.dev/mcp > cli.py
```

### Adding Custom Commands

Add custom commands to `cli.py`:

```python
@app.command
async def my_custom_command(street: str) -> None:
    """Custom command to search by street."""
    async with Client(CLIENT_SPEC) as client:
        result = await client.call_tool(
            'search_obstructions',
            {'filters': f'{{"primary_street": "{street}"}}'}
        )
        _print_tool_result(result)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'fastmcp'` | Install dependencies: `pip install fastmcp` or use `uv run --with fastmcp` |
| `Connection refused` | Check server is running and CLIENT_SPEC is correct |
| `JSON parse error in filters` | Ensure filters use double quotes: `'{"key": "value"}'` |
| Empty results | Try broader search or remove filters |
| Timeout errors | Use smaller limit values or check server status |

## Getting Help

```bash
# Get general help
python cli.py --help

# Get help for specific command
python cli.py call-tool --help
python cli.py call-tool search_obstructions --help
```

## Performance Tips

1. **Use pagination** for large datasets (limit + offset)
2. **Filter at query time** rather than fetching everything
3. **Cache results** locally if doing multiple analyses
4. **Use specific filters** instead of broad text search when possible
5. **Batch exports** during off-peak hours

## Examples Repository

Find more examples at:
- Server docs: `README_SERVER.md`
- Main README: `../README.md`
- Skill documentation: `../.cursor/skills/domi-obstruction-mcp/SKILL.md`
