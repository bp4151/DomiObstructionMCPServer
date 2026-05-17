---
name: domi-obstruction-mcp
description: Search and analyze Pittsburgh DOMI (Department of Mobility and Infrastructure) road obstruction and closure data from WPRDC. Use when the user asks about Pittsburgh road closures, construction permits, street obstructions, traffic disruptions, or DOMI permits.
---

# DOMI Obstruction MCP Server

This skill provides access to Pittsburgh's Department of Mobility and Infrastructure (DOMI) obstruction and closure records via an MCP server.

## When to Use

Use this skill when the user asks about:
- Pittsburgh road closures or construction
- Street obstructions or lane closures
- DOMI permits or closure permits
- Traffic disruptions in Pittsburgh
- Active construction projects affecting streets
- Specific streets that are closed or obstructed

## Available Tools

### search_obstructions
Search all obstruction/closure records with optional filters and text search.

**Common usage patterns:**

```python
# Search by street name
search_obstructions(q="Fifth Avenue")

# Search with filters
search_obstructions(filters='{"primary_street": "FIFTH AVE"}')

# Paginate results
search_obstructions(limit=50, offset=50)

# Combine search and filters
search_obstructions(q="construction", filters='{"active": true}')
```

**Parameters:**
- `limit` (int, default 100): Max records to return
- `offset` (int, default 0): Skip this many records (for pagination)
- `q` (str, optional): Full-text search query - searches across work_description, primary_street, from_street, to_street, closure_id, permit_id, applicant_name
- `filters` (str, optional): JSON object with exact field matches, e.g. `{"primary_street": "SECOND AVE"}` or `{"active": true}`

### list_active_entries
List only currently active obstructions/closures.

**Usage:**
```python
# Get first 100 active entries
list_active_entries()

# Paginate through active entries
list_active_entries(limit=50, offset=0)
```

### obstruction_count
Get total number of obstruction records in the dataset.

**Usage:**
```python
obstruction_count()
```

### match_gpx_obstructions
Find active DOMI records that match route segments in a GPX file.

**Usage:**
```python
# Match with default threshold (~10m)
match_gpx_obstructions(gpx_content='<?xml version="1.0"...')

# Match with custom threshold (~50m)
match_gpx_obstructions(gpx_content='...', distance_threshold=0.0005)
```

### refresh_data
Refresh the cached data from WPRDC source (admin operation).

**Usage:**
```python
# Refresh all data
refresh_data()

# Refresh with limit
refresh_data(max_records=1000)
```

## Understanding the Data

Each obstruction record includes:
- **Location**: primary_street, from_street, to_street, geometry coordinates
- **Timing**: start_date, end_date, active status
- **Permit details**: closure_id, permit_id, permit_type
- **Work info**: work_description, applicant_name
- **Closure details**: closure_type, full_closure, lane_count, lanes_closed

## Common Workflows

### Finding Active Closures on a Street
```python
# Search for active closures on Fifth Avenue
list_active_entries(limit=100)
# Then filter results for the specific street in your analysis
```

### Finding All Historical Data for a Street
```python
search_obstructions(filters='{"primary_street": "FIFTH AVE"}', limit=500)
```

### Searching by Description
```python
# Find water main work
search_obstructions(q="water main")

# Find paving projects
search_obstructions(q="paving")
```

### Analyzing Closure Duration
```python
# Get records and calculate duration from start_date to end_date
search_obstructions(q="construction", limit=100)
```

## Response Format

All tools return JSON with this structure:
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

## Tips

1. **Street name variations**: Streets may appear as "FIFTH AVE", "Fifth Avenue", or "5th Ave" - use text search with `q` parameter for flexibility
2. **Active vs historical**: Use `list_active_entries()` for current closures, `search_obstructions()` for historical analysis
3. **Large datasets**: Results are paginated - use `limit` and `offset` to retrieve all records
4. **Combine filters**: Use both `q` for text search and `filters` for exact matches
5. **Dates**: Check start_date and end_date fields to determine if a closure is current

## Server Connection

The MCP server is available at:
- **HTTP**: https://domi-obstruction.fly.dev/mcp
- **Local STDIO**: via MCP client configuration

When using the MCP tools, they're automatically available as `domi-obstruction-mcp-http-*` or `domi-obstruction-mcp-flyio-*` depending on connection method.
