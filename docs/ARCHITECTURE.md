# DOMI Obstruction MCP Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     DOMI OBSTRUCTION MCP SYSTEM                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       DATA SOURCE (WPRDC)                        │
│  Western Pennsylvania Regional Data Center                      │
│  • Road obstruction permits                                     │
│  • Street closure records                                       │
│  • Construction permits                                         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FASTMCP SERVER (../server/main.py)                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Tools:                                                   │   │
│  │  • search_obstructions()   - Search all records         │   │
│  │  • list_active_entries()   - Get active closures        │   │
│  │  • obstruction_count()     - Get total count            │   │
│  │  • match_gpx_obstructions()- Match GPX route           │   │
│  │  • refresh_data()          - Refresh cache              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Cache: In-memory record storage                                │
│  Transport: stdio + HTTP (https://domi-obstruction.fly.dev)     │
└───────────────────┬──────────────────────┬──────────────────────┘
                    │                      │
        ┌───────────┴──────────┐  ┌────────┴─────────┐
        ▼                      ▼  ▼                  ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  CURSOR SKILL   │   │   CLI TOOL      │   │   MCP CLIENTS   │
│                 │   │                 │   │                 │
│  ../.cursor/skills/│   │  ../server/cli.py  │   │  • Claude       │
│  domi-obstruct..│   │                 │   │  • Others       │
└─────────────────┘   └─────────────────┘   └─────────────────┘
        │                      │                      │
        ▼                      ▼                      ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  Natural Lang   │   │  Command Line   │   │  Tool Calls     │
│  "What streets  │   │  $ python cli.py│   │  call_tool()    │
│   are closed?"  │   │    call-tool... │   │                 │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

## Data Flow

### Query Flow (Natural Language via Cursor)

```
User Question
    │
    │ "What streets are closed in Pittsburgh?"
    ▼
Cursor AI
    │
    │ Reads: ../.cursor/skills/domi-obstruction-mcp/SKILL.md
    │ Understands: Available tools, usage patterns
    ▼
Tool Selection
    │
    │ Chooses: list_active_entries(limit=200)
    ▼
MCP Protocol
    │
    │ Calls server tool via MCP
    ▼
FastMCP Server
    │
    │ Executes: list_active_entries()
    │ Filters: active=true from cache
    ▼
JSON Response
    │
    │ Returns: {"success": true, "result": {...}}
    ▼
AI Analysis
    │
    │ Processes records
    │ Formats output
    ▼
User Response
    │
    │ "There are 47 active closures:
    │  • Fifth Avenue: Water main work
    │  • Forbes Avenue: Paving project
    │  ..."
```

### Query Flow (CLI)

```
User Command
    │
    │ $ python cli.py call-tool search_obstructions --q "Forbes"
    ▼
CLI Parser (cyclopts)
    │
    │ Parses arguments
    │ Validates parameters
    ▼
FastMCP Client
    │
    │ Connects to: CLIENT_SPEC URL
    │ Sends: MCP tool call request
    ▼
FastMCP Server
    │
    │ Executes: search_obstructions(q="Forbes")
    │ Searches: cached records
    ▼
JSON Response
    │
    │ Returns: {"success": true, "result": {...}}
    ▼
CLI Output (Rich)
    │
    │ Formats JSON
    │ Syntax highlighting
    ▼
Terminal
    │
    │ Displays formatted JSON
    │ Can pipe to jq, files, etc.
```

## Component Details

### 1. FastMCP Server (`../server/main.py`)

**Purpose**: Core MCP server exposing DOMI data

**Key Components**:
- `@mcp.tool()` decorators define tools
- In-memory cache for performance
- WPRDC data ingestion on startup
- Supports stdio and HTTP transports

**Deployment**:
- Fly.io: https://domi-obstruction.fly.dev/mcp
- Local: `python main.py`

### 2. Cursor Skill (`../.cursor/skills/domi-obstruction-mcp/`)

**Purpose**: Teach AI assistants how to use the MCP server

**Files**:
```
domi-obstruction-mcp/
├── SKILL.md       # Main skill (auto-loaded)
├── README.md      # Setup guide
└── examples.md    # Usage patterns
```

**Triggers**:
- Keywords: Pittsburgh, road closure, construction, DOMI, obstruction
- User questions about street closures
- Requests for permit data

**What It Provides**:
- Tool descriptions and parameters
- Usage patterns and best practices
- Common workflows
- Data schema reference

### 3. CLI Tool (`../server/cli.py`)

**Purpose**: Command-line access to MCP tools

**Generated By**: `fastmcp generate-cli <url>`

**Features**:
- Type-safe argument parsing
- JSON input/output
- Rich error formatting
- Help text from docstrings
- Works with/without installation (via uv)

**Commands**:
```bash
# Meta commands
list-tools          # List all available tools
list-resources      # List resources
list-prompts        # List prompts

# Tool commands
call-tool <name>    # Call specific tool with args
```

### 4. Documentation

**Project Root**:
- `SUMMARY.md` - What was created (start here)
- `QUICK_REFERENCE.md` - One-page cheat sheet
- `FASTMCP_TO_SKILL_AND_CLI.md` - How it works
- `ARCHITECTURE.md` - This file

**Server Directory**:
- `../server/CLI_README.md` - CLI quick start
- `../server/CLI_USAGE.md` - Comprehensive CLI guide
- `../server/install_cli.sh` - Installer
- `../server/test_cli.sh` - Tests

**Skill Directory**:
- `SKILL.md` - Skill instructions
- `examples.md` - Real-world examples

## Data Model

### Record Schema

```python
{
    # Identifiers
    "closure_id": str,          # Unique closure ID
    "permit_id": str,           # Associated permit ID
    "permit_type": str,         # Type of permit
    
    # Location
    "primary_street": str,      # Main street affected
    "from_street": str,         # Starting intersection
    "to_street": str,          # Ending intersection
    "geometry": dict,           # GeoJSON coordinates
    
    # Timing
    "start_date": str,          # ISO date string
    "end_date": str,           # ISO date string
    "active": bool,             # Currently active?
    
    # Work Details
    "work_description": str,    # What work is being done
    "applicant_name": str,      # Who requested permit
    
    # Closure Details
    "full_closure": bool,       # Full vs partial closure
    "closure_type": str,        # Type of closure
    "lane_count": int,          # Total lanes on street
    "lanes_closed": int,        # Number of lanes closed
    
    # Metadata
    "permit_status": str,       # Status of permit
    "created_date": str,        # When record created
    "modified_date": str        # Last update
}
```

### API Response Format

```json
{
  "success": true,
  "result": {
    "records": [
      { /* record 1 */ },
      { /* record 2 */ }
    ],
    "total": 1234,
    "fields": [
      {"id": "closure_id", "type": "text"},
      {"id": "primary_street", "type": "text"}
    ],
    "records_format": "objects",
    "resource_id": "a9a1d93a-9d3b-4c18-bd80-82ed6f86404a"
  }
}
```

## Tool Reference

### search_obstructions

**Purpose**: Search all records with optional filters

**Parameters**:
- `limit` (int, default 100): Max results
- `offset` (int, default 0): Skip N records
- `q` (str, optional): Text search query
- `filters` (str, optional): JSON filter object

**Search Fields** (when using `q`):
- work_description
- primary_street
- from_street
- to_street
- closure_id
- permit_id
- applicant_name

**Example Filters**:
```json
{"primary_street": "FIFTH AVE"}
{"active": true}
{"full_closure": true}
{"primary_street": "FIFTH AVE", "active": true}
```

### list_active_entries

**Purpose**: Get only currently active closures

**Parameters**:
- `limit` (int, default 100): Max results
- `offset` (int, default 0): Skip N records

**Note**: Equivalent to `search_obstructions(filters='{"active": true}')`

### obstruction_count

**Purpose**: Get total record count

**Parameters**: None

**Returns**: `{"total": 1234}`

### match_gpx_obstructions

**Purpose**: Find active closures matching a GPX route

**Parameters**:
- `gpx_content` (str): XML content of GPX file
- `distance_threshold` (float, default 0.0001): Match distance in degrees

### refresh_data

**Purpose**: Refresh cached data from WPRDC

**Parameters**:
- `max_records` (int, optional): Limit records to ingest

**Note**: Admin operation, triggers full data refresh

## Integration Patterns

### Pattern 1: Natural Language Query

```
User → Cursor → Skill → MCP Server → Response → AI Analysis → User
```

**Best For**:
- Exploratory queries
- Complex analysis
- Multi-step workflows
- Non-technical users

### Pattern 2: Direct CLI Usage

```
User → CLI → MCP Server → Response → Terminal
```

**Best For**:
- Quick lookups
- Scripting
- Automation
- Piping to other tools

### Pattern 3: Programmatic Access

```
Script → MCP Client → MCP Server → Response → Processing
```

**Best For**:
- Data pipelines
- Monitoring systems
- Custom applications
- Integration with other services

### Pattern 4: Hybrid Approach

```
User → Cursor (with skill) → Generates CLI script → User runs script
```

**Best For**:
- Complex workflows
- Repeated queries
- Learning CLI usage
- Documentation

## Performance Characteristics

### Cache Strategy

**On Startup**:
1. Server loads all records into memory
2. Records stored in `_cached_records` list
3. Total count cached in `_cached_total`
4. Field metadata cached in `_cached_fields`

**On Query**:
1. Filter in-memory (fast)
2. No external API call (cached)
3. Slice results for pagination
4. Return formatted JSON

**Refresh**:
- Manual via `refresh_data()` tool
- Fetches latest from WPRDC
- Updates in-memory cache
- No downtime during refresh

### Scalability

**Current**:
- ~5000 records in cache
- Sub-millisecond search
- Pagination support
- Single server instance

**Limitations**:
- Memory bound by record count
- No distributed cache
- Single point of failure

**Future Improvements**:
- Redis/Memcached for distributed cache
- Database for persistence
- Multiple server instances
- Background refresh scheduler

## Security Considerations

### Current Implementation

**Exposed**:
- Read-only access to public data
- No authentication required
- CORS enabled for HTTP transport

**Protected**:
- No write operations exposed
- Admin operations (refresh_data) require tool access
- Server-side filtering (no SQL injection)

### Best Practices

1. **Rate Limiting**: Implement for public API
2. **Authentication**: Add for admin operations
3. **Input Validation**: Already implemented in FastMCP
4. **Logging**: Monitor usage patterns
5. **HTTPS**: Required for production (already using)

## Deployment Architecture

### Current Setup

```
                Internet
                    │
                    ▼
            ┌──────────────┐
            │   Fly.io     │
            │   (Edge)     │
            └──────┬───────┘
                   │
                   ▼
        ┌────────────────────┐
        │  FastMCP Server    │
        │  Container         │
        │                    │
        │  • HTTP transport  │
        │  • In-memory cache │
        │  • WPRDC client    │
        └─────────┬──────────┘
                  │
                  ▼
          ┌───────────────┐
          │    WPRDC API  │
          │  (Data Source)│
          └───────────────┘
```

### Local Development

```
    Terminal
        │
        ▼
┌────────────────┐
│  FastMCP Server│
│  (stdio)       │
└────────┬───────┘
         │
         ▼
   ┌──────────┐
   │ WPRDC API│
   └──────────┘
```

## Extension Points

### Adding New Tools

1. Add `@mcp.tool()` function to `../server/main.py`
2. Regenerate CLI: `fastmcp generate-cli <url> > cli.py`
3. Update skill: Add tool docs to `SKILL.md`
4. Update examples: Add usage patterns

### Adding New Data Sources

1. Create new data client (like `wprdc.py`)
2. Add ingestion function
3. Update cache strategy
4. Create new tools for queries
5. Document in skill

### Custom CLI Commands

Add to `cli.py`:
```python
@app.command
async def my_command(arg: str) -> None:
    """My custom command."""
    async with Client(CLIENT_SPEC) as client:
        result = await client.call_tool('tool_name', {'arg': arg})
        _print_tool_result(result)
```

## Maintenance Procedures

### Regular Updates

**Weekly**:
- Monitor server logs
- Check data freshness
- Review usage patterns

**Monthly**:
- Update dependencies
- Refresh documentation
- Review and add examples

**Quarterly**:
- Performance analysis
- Capacity planning
- Feature requests review

### Incident Response

**Server Down**:
1. Check Fly.io status
2. Review logs: `fly logs`
3. Restart if needed: `fly deploy`

**Data Issues**:
1. Check WPRDC API status
2. Manual refresh: Call `refresh_data()`
3. Verify data integrity

**Client Issues**:
1. Verify CLIENT_SPEC URL
2. Check network connectivity
3. Test with curl: `curl <server-url>/mcp`

## Monitoring & Observability

### Current Logging

```python
logger.info("Starting DOMI Obstruction MCP server")
logger.info("Running ingestion on startup")
logger.info("Cache ready: %s records", len(_cached_records))
logger.info("Refresh requested (max_records=%s)", ingest_limit)
```

### Recommended Additions

1. **Metrics**:
   - Tool call counts
   - Response times
   - Cache hit rates
   - Error rates

2. **Tracing**:
   - Request flow
   - External API calls
   - Cache operations

3. **Alerts**:
   - Server downtime
   - High error rates
   - Data staleness
   - Performance degradation

## Summary

This architecture provides:

✅ **Multiple Interfaces**: Natural language, CLI, MCP protocol  
✅ **Fast Performance**: In-memory caching  
✅ **Developer Friendly**: Auto-generated CLI, comprehensive docs  
✅ **Extensible**: Easy to add tools, data sources, commands  
✅ **Production Ready**: Deployed, tested, documented  

All from a single FastMCP server definition! 🚀
