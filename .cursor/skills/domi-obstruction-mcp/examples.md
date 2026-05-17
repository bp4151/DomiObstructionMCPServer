# DOMI Obstruction MCP Examples

Real-world examples for using the DOMI Obstruction MCP server.

## Example Queries

### 1. Find Active Closures on a Specific Street

**Question:** "What closures are currently active on Fifth Avenue?"

**Using MCP tools:**
```python
# Get all active entries and filter for Fifth Avenue
list_active_entries(limit=500)
# Then filter in your analysis for primary_street containing "FIFTH"

# OR use search with filters
search_obstructions(
    filters='{"primary_street": "FIFTH AVE", "active": true}'
)
```

**Expected data:**
```json
{
  "success": true,
  "result": {
    "records": [
      {
        "closure_id": "C2024-123",
        "primary_street": "FIFTH AVE",
        "from_street": "FORBES AVE",
        "to_street": "BIGELOW BLVD",
        "work_description": "Water main replacement",
        "start_date": "2024-03-01",
        "end_date": "2024-04-15",
        "active": true,
        "full_closure": false,
        "lanes_closed": 1
      }
    ],
    "total": 1
  }
}
```

### 2. Find All Construction Projects This Month

**Question:** "What construction work is happening this month?"

**Approach:**
```python
# Get all active entries
list_active_entries(limit=500)

# Then filter by date range in your analysis
# Records have start_date and end_date fields
```

### 3. Historical Analysis - Most Affected Streets

**Question:** "Which streets have had the most closures historically?"

**Approach:**
```python
# Get all records (paginate if needed)
search_obstructions(limit=5000, offset=0)

# Analyze primary_street field frequencies
# Group by primary_street and count
```

### 4. Find Work by Specific Applicant

**Question:** "What work is PWSA (Pittsburgh Water and Sewer Authority) doing?"

**Using MCP tools:**
```python
search_obstructions(q="PWSA", limit=100)

# OR
search_obstructions(q="Pittsburgh Water", limit=100)
```

### 5. Lane Closures vs Full Closures

**Question:** "Show me all full street closures"

**Using MCP tools:**
```python
search_obstructions(
    filters='{"full_closure": true}',
    limit=200
)
```

### 6. Long-Term Projects

**Question:** "What projects have been running for over 6 months?"

**Approach:**
```python
# Get all active entries
list_active_entries(limit=500)

# Calculate duration from start_date to end_date
# Filter where duration > 180 days
```

### 7. Geographic Analysis

**Question:** "What closures are near a specific intersection?"

**Approach:**
```python
# Search for streets near the intersection
search_obstructions(q="Forbes", limit=100)
search_obstructions(q="Fifth", limit=100)

# Use geometry field if available for precise location
```

### 8. Permit Type Analysis

**Question:** "How many obstruction permits vs closure permits are there?"

**Approach:**
```python
# Get all records
search_obstructions(limit=5000, offset=0)

# Group by permit_type field
```

### 9. Daily Monitoring

**Question:** "What changed today?"

**Workflow:**
```python
# Morning: Get active count
obstruction_count()
list_active_entries(limit=1000)

# Evening: Compare with morning snapshot
# New entries = entries not in morning list
```

### 10. Export for GIS Analysis

**Question:** "Export all closures with coordinates for mapping"

**Approach:**
```python
# Get all records with geometry
search_obstructions(limit=5000, offset=0)

# Extract geometry field (contains coordinates)
# Export to GeoJSON or shapefile
```

## CLI Examples

### Basic Search

```bash
# Search by keyword
python cli.py call-tool search_obstructions --q "Fifth Avenue"

# Get count
python cli.py call-tool obstruction_count

# List active
python cli.py call-tool list_active_entries --limit 100
```

### Advanced Filtering

```bash
# Exact street match
python cli.py call-tool search_obstructions \
  --filters '{"primary_street": "FIFTH AVE"}'

# Active closures only
python cli.py call-tool search_obstructions \
  --filters '{"active": true}'

# Full closures only
python cli.py call-tool search_obstructions \
  --filters '{"full_closure": true}'

# Combine filters
python cli.py call-tool search_obstructions \
  --filters '{"primary_street": "FIFTH AVE", "active": true}'
```

### Pagination

```bash
# First batch
python cli.py call-tool search_obstructions --limit 500 --offset 0 > batch1.json

# Second batch
python cli.py call-tool search_obstructions --limit 500 --offset 500 > batch2.json

# Third batch
python cli.py call-tool search_obstructions --limit 500 --offset 1000 > batch3.json
```

### Using jq for Analysis

```bash
# Count active closures
python cli.py call-tool list_active_entries --limit 9999 | jq '.result.total'

# Extract street names
python cli.py call-tool list_active_entries | jq -r '.result.records[].primary_street'

# Find full closures
python cli.py call-tool list_active_entries | jq '.result.records[] | select(.full_closure == true)'

# Sort by start date
python cli.py call-tool search_obstructions --limit 500 | \
  jq '.result.records | sort_by(.start_date)'

# Group by street
python cli.py call-tool search_obstructions --limit 1000 | \
  jq '[.result.records | group_by(.primary_street)[] | {street: .[0].primary_street, count: length}]'
```

## Cursor Skill Examples

When the skill is installed, you can ask natural language questions:

### Example 1: Current Closures

**Prompt:** "What streets in Pittsburgh are closed right now?"

**What the AI does:**
1. Reads the SKILL.md to understand available tools
2. Calls `list_active_entries(limit=200)`
3. Analyzes the results
4. Presents a formatted list with street names and work descriptions

### Example 2: Specific Street Analysis

**Prompt:** "Show me all historical data for Fifth Avenue closures"

**What the AI does:**
1. Calls `search_obstructions(filters='{"primary_street": "FIFTH AVE"}', limit=500)`
2. Analyzes patterns (frequency, duration, types of work)
3. Generates summary statistics
4. Creates visualizations if requested

### Example 3: Impact Analysis

**Prompt:** "Which applicant causes the most street disruptions?"

**What the AI does:**
1. Calls `search_obstructions(limit=5000)` to get full dataset
2. Groups by applicant_name
3. Counts entries per applicant
4. Calculates total days of closures per applicant
5. Presents ranked list

### Example 4: Geographic Query

**Prompt:** "Are there any road closures affecting the route from Downtown to Oakland?"

**What the AI does:**
1. Identifies major streets on that route (Fifth, Forbes, etc.)
2. Calls `list_active_entries()` 
3. Filters for those streets
4. Maps the locations
5. Identifies which closures affect the route

## Data Schema Reference

Each record contains these key fields:

```python
{
    # Identifiers
    "closure_id": "C2024-123",
    "permit_id": "P2024-456",
    "permit_type": "Obstruction",
    
    # Location
    "primary_street": "FIFTH AVE",
    "from_street": "FORBES AVE",
    "to_street": "BIGELOW BLVD",
    "geometry": {...},  # GeoJSON coordinates
    
    # Timing
    "start_date": "2024-03-01",
    "end_date": "2024-04-15",
    "active": true,
    
    # Work details
    "work_description": "Water main replacement",
    "applicant_name": "PWSA",
    
    # Closure details
    "full_closure": false,
    "closure_type": "Lane closure",
    "lane_count": 4,
    "lanes_closed": 1,
    
    # Administrative
    "permit_status": "Active",
    "created_date": "2024-02-15",
    "modified_date": "2024-03-01"
}
```

## Best Practices

### 1. Start Broad, Then Filter

```python
# Don't do this (too narrow might miss results)
search_obstructions(filters='{"primary_street": "Fifth Avenue"}')

# Do this (use text search for flexibility)
search_obstructions(q="Fifth")

# Then filter results as needed
```

### 2. Use Pagination for Large Datasets

```python
# Don't do this (might timeout or return incomplete data)
search_obstructions(limit=99999)

# Do this (paginate in reasonable chunks)
for offset in range(0, 5000, 500):
    search_obstructions(limit=500, offset=offset)
```

### 3. Cache Data for Multiple Analyses

```bash
# Fetch once
python cli.py call-tool search_obstructions --limit 5000 > full_data.json

# Analyze multiple times
jq '.result.records[] | select(.active == true)' full_data.json
jq '[.result.records | group_by(.primary_street)]' full_data.json
jq '.result.records | map(.lanes_closed) | add' full_data.json
```

### 4. Combine Text Search with Filters

```python
# Find active water main work on Forbes
search_obstructions(
    q="water main",
    filters='{"primary_street": "FORBES AVE", "active": true}'
)
```

### 5. Check Total Before Paginating

```python
# Get count first
count_result = obstruction_count()
total = count_result['total']

# Calculate pages needed
pages = (total // 500) + 1

# Paginate accordingly
for page in range(pages):
    search_obstructions(limit=500, offset=page * 500)
```

## Integration Examples

### Python Script

```python
#!/usr/bin/env python3
"""Daily closure report"""

import json
import subprocess
from datetime import datetime

def get_active_closures():
    result = subprocess.run(
        ['python', 'cli.py', 'call-tool', 'list_active_entries', '--limit', '1000'],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def generate_report(data):
    records = data['result']['records']
    print(f"# DOMI Daily Closure Report - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"\nTotal active closures: {len(records)}\n")
    
    for record in records:
        print(f"## {record['primary_street']}")
        print(f"- Work: {record['work_description']}")
        print(f"- Duration: {record['start_date']} to {record['end_date']}")
        print(f"- Type: {'Full closure' if record.get('full_closure') else 'Partial closure'}")
        print()

if __name__ == '__main__':
    data = get_active_closures()
    generate_report(data)
```

### Shell Script for Email Alerts

```bash
#!/bin/bash
# email_alert.sh - Send alert if Fifth Avenue is affected

CLOSURES=$(python cli.py call-tool list_active_entries --limit 1000 | \
           jq '.result.records[] | select(.primary_street | contains("FIFTH"))')

if [ -n "$CLOSURES" ]; then
    echo "$CLOSURES" | mail -s "Fifth Avenue Closure Alert" user@example.com
fi
```

### Cron Job for Monitoring

```cron
# Monitor every hour for new closures
0 * * * * cd /path/to/cli && python cli.py call-tool list_active_entries > /tmp/current_closures.json && diff /tmp/last_closures.json /tmp/current_closures.json && cp /tmp/current_closures.json /tmp/last_closures.json
```

## Troubleshooting Examples

### No Results for Street Search

```bash
# If this returns nothing:
python cli.py call-tool search_obstructions --q "5th Avenue"

# Try variations:
python cli.py call-tool search_obstructions --q "Fifth"
python cli.py call-tool search_obstructions --q "FIFTH AVE"
python cli.py call-tool search_obstructions --filters '{"primary_street": "FIFTH AVE"}'
```

### Finding Exact Field Values

```bash
# Get all unique street names
python cli.py call-tool search_obstructions --limit 5000 | \
  jq -r '.result.records[].primary_street' | sort -u

# Get all permit types
python cli.py call-tool search_obstructions --limit 5000 | \
  jq -r '.result.records[].permit_type' | sort -u
```

### Debugging Filters

```bash
# This might fail silently:
python cli.py call-tool search_obstructions --filters '{"street": "FIFTH AVE"}'

# Check field names first:
python cli.py call-tool search_obstructions --limit 1 | jq '.result.records[0] | keys'

# Use correct field name:
python cli.py call-tool search_obstructions --filters '{"primary_street": "FIFTH AVE"}'
```
