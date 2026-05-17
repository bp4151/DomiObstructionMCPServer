# DOMI Obstruction MCP - Quick Reference

## 🎯 What You Have

- ✅ **FastMCP Server** - Running at https://domi-obstruction.fly.dev/mcp
- ✅ **Cursor Skill** - In `../.cursor/skills/domi-obstruction-mcp/`
- ✅ **CLI Tool** - In `../server/cli.py`
- ✅ **Documentation** - Complete guides and examples

## 🚀 Quick Start

### Using in Cursor (Natural Language)

Just ask questions:
```
"What streets in Pittsburgh are closed right now?"
"Show me construction on Fifth Avenue"
"Find all water main work by PWSA"
"Are there any closures along my route? [attach GPX]"
```

The AI will automatically use your MCP tools.

### Using CLI (Command Line)

```bash
# List tools
python cli.py list-tools

# Search
python cli.py call-tool search_obstructions --q "Fifth Avenue"

# Active closures
python cli.py call-tool list_active_entries

# Find obstructions along a route
python cli.py match-gpx --path "route.gpx"

# Get count
python cli.py call-tool obstruction_count
```

## 📂 File Locations

| What | Where |
|------|-------|
| **Cursor Skill** | `../.cursor/skills/domi-obstruction-mcp/SKILL.md` |
| **Skill Examples** | `../.cursor/skills/domi-obstruction-mcp/examples.md` |
| **CLI Script** | `../server/cli.py` |
| **CLI Quick Start** | `../server/CLI_README.md` |
| **CLI Full Guide** | `../server/CLI_USAGE.md` |
| **Conversion Guide** | `FASTMCP_TO_SKILL_AND_CLI.md` |
| **Server Code** | `../server/main.py` |

## 🔧 Installation

### CLI Installation

**Linux/macOS/WSL:**
```bash
cd server
bash install_cli.sh
```

**Windows PowerShell:**
```powershell
cd server
powershell -ExecutionPolicy Bypass -File install_cli.ps1
```

**Or use without installing:**
```bash
uv run --with fastmcp python cli.py list-tools
```

### Skill Installation

Already installed! Located at `../.cursor/skills/domi-obstruction-mcp/`

## 📖 Available Tools

| Tool | Description |
|------|-------------|
| `search_obstructions` | Search all obstruction records with filters |
| `list_active_entries` | Get only active closures |
| `obstruction_count` | Get total count |
| `match_gpx_obstructions` | Find active closures matching a GPX route |
| `refresh_data` | Refresh cached data (admin) |

## 💡 Common Commands

### CLI

```bash
# Search by street
python cli.py call-tool search_obstructions --q "Forbes"

# Exact match
python cli.py call-tool search_obstructions \
  --filters '{"primary_street": "FIFTH AVE"}'

# Active only
python cli.py call-tool search_obstructions \
  --filters '{"active": true}'

# Match GPX route
python cli.py match-gpx --path "my_route.gpx"

# Paginate
python cli.py call-tool search_obstructions \
  --limit 500 --offset 0

# Save to file
python cli.py call-tool list_active_entries > closures.json

# Use with jq
python cli.py call-tool search_obstructions --q "Forbes" | \
  jq '.result.records[].primary_street'
```

### Cursor Prompts

```
"What streets are currently closed in Pittsburgh?"

"Show me all historical closures on Forbes Avenue"

"Find all construction work by PWSA"

"Which streets have the most closures?"

"Export active closures to JSON"
```

## 🔗 Key Concepts

### Search vs Filter

- **Text search** (`--q`): Flexible, searches multiple fields
- **Exact filter** (`--filters`): Precise, matches exact values

```bash
# Text search (finds "Fifth Ave", "Fifth Avenue", etc.)
--q "Fifth"

# Exact match (only "FIFTH AVE")
--filters '{"primary_street": "FIFTH AVE"}'
```

### Pagination

Use `limit` and `offset` for large datasets:

```bash
# First 500
--limit 500 --offset 0

# Next 500
--limit 500 --offset 500

# Next 500
--limit 500 --offset 1000
```

### Active vs All Records

- `list_active_entries` - Only current closures
- `search_obstructions` - All records (historical + current)

## 📊 Data Fields

Each record includes:

```json
{
  "closure_id": "C2024-123",
  "permit_id": "P2024-456",
  "primary_street": "FIFTH AVE",
  "from_street": "FORBES AVE",
  "to_street": "BIGELOW BLVD",
  "work_description": "Water main replacement",
  "applicant_name": "PWSA",
  "start_date": "2024-03-01",
  "end_date": "2024-04-15",
  "active": true,
  "full_closure": false,
  "lanes_closed": 1,
  "geometry": {...}
}
```

## 🎓 Documentation

| Guide | What It Covers |
|-------|----------------|
| **../server/CLI_README.md** | Quick start for CLI |
| **../server/CLI_USAGE.md** | Comprehensive CLI guide with examples |
| **SKILL.md** (in `../.cursor/skills/`) | Cursor skill instructions |
| **examples.md** | Real-world usage examples |
| **FASTMCP_TO_SKILL_AND_CLI.md** | How conversion works |

## ⚡ Tips

1. **Start with text search** (`--q`) before using exact filters
2. **Check total first** with `obstruction_count()` before paginating
3. **Use jq** for parsing and filtering JSON output
4. **Cache results** locally if doing multiple analyses
5. **Combine search and filter** for precise results

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Skill not triggering | Restart Cursor, check `../.cursor/skills/` location |
| CLI import errors | Run `pip install fastmcp cyclopts rich mcp` |
| Connection errors | Check `CLIENT_SPEC` in cli.py |
| No results | Try broader search, check spelling |
| JSON parse error | Use single quotes around JSON: `'{"key": "value"}'` |

## 🔄 Updating

### When Server Changes

```bash
# Regenerate CLI
fastmcp generate-cli https://domi-obstruction.fly.dev/mcp > ../server/cli.py

# Update skill documentation
# Edit ../.cursor/skills/domi-obstruction-mcp/SKILL.md
```

### Local Development

```bash
# Run server locally
cd server
python main.py

# Update CLI to use local server
# Edit CLIENT_SPEC in cli.py:
CLIENT_SPEC = 'http://localhost:8000/mcp'
```

## 🌟 Next Steps

1. ✅ Test the skill: Ask Cursor about Pittsburgh road closures
2. ✅ Try CLI commands from examples above
3. ✅ Read full documentation in ../server/CLI_USAGE.md
4. ✅ Explore examples.md for real-world patterns
5. ✅ Customize for your needs

## 📞 Need Help?

- **Skill guide**: `../.cursor/skills/domi-obstruction-mcp/SKILL.md`
- **CLI guide**: `../server/CLI_USAGE.md`
- **Examples**: `../.cursor/skills/domi-obstruction-mcp/examples.md`
- **Conversion guide**: `FASTMCP_TO_SKILL_AND_CLI.md`

---

**Remember**: Your FastMCP server is now accessible via:
- 💬 Natural language (Cursor with skill)
- ⌨️ Command line (CLI)
- 🔌 MCP protocol (any MCP client)
- 🌐 HTTP API (direct endpoint)

All from one FastMCP server definition! 🚀
