# FastMCP to Skill & CLI Conversion Guide

This document explains how your FastMCP server was converted into a Cursor Skill and CLI.

## What Was Created

### 1. Cursor Skill (`../.cursor/skills/domi-obstruction-mcp/`)

A Cursor Skill teaches AI assistants how to use your MCP server effectively.

**Files created:**
- `SKILL.md` - Main skill instructions (automatically loaded by Cursor)
- `README.md` - Installation and setup guide
- `examples.md` - Real-world usage examples

**What it does:**
- Teaches AI assistants about your MCP tools: `search_obstructions`, `list_active_entries`, `obstruction_count`, `match_gpx_obstructions`, and `refresh_data`.
- Provides usage patterns and best practices
- Enables natural language queries like "What streets are closed in Pittsburgh?"
- Automatically triggered when users mention roads, closures, Pittsburgh, DOMI, etc.

**Installation:**
The skill is already in your project at `../.cursor/skills/domi-obstruction-mcp/`. Cursor will automatically discover it.

**Usage:**
Just ask questions in natural language:
- "What streets in Pittsburgh are closed?"
- "Show me construction on Fifth Avenue"
- "Find all PWSA water main work"

### 2. CLI (`../server/cli.py` + documentation)

A command-line interface for direct access to your MCP server.

**Files created/updated:**
- `cli.py` - Generated CLI (already existed, we added docs)
- `SKILL.md` - CLI documentation in skill format
- `CLI_README.md` - Quick start guide
- `CLI_USAGE.md` - Comprehensive usage guide with examples
- `install_cli.sh` - Installation script
- `../.cursor/skills/domi-obstruction-mcp/examples.md` - Usage examples

**What it does:**
- Provides command-line access to all MCP tools
- Enables scripting and automation
- Supports JSON output for piping to other tools
- Works with or without installation (via `uv`)

**Installation:**
```bash
# Option 1: Use installer
cd server
bash install_cli.sh

# Option 2: Use UV (no installation needed)
uv run --with fastmcp python cli.py list-tools

# Option 3: Manual pip install
pip install fastmcp cyclopts rich mcp
```

**Usage:**
```bash
# List tools
python cli.py list-tools

# Search for closures
python cli.py call-tool search_obstructions --q "Fifth Avenue"

# Get active closures
python cli.py call-tool list_active_entries

# Match GPX route
python cli.py match-gpx --path "route.gpx"

# Pipe to jq
python cli.py call-tool list_active_entries | jq '.result.total'
```

## How the Conversion Works

### FastMCP Server → Cursor Skill

1. **Tool Discovery**: We analyzed your FastMCP tools using the `@mcp.tool()` decorators
2. **Documentation**: We extracted docstrings and parameter descriptions
3. **Usage Patterns**: We identified common use cases from your tool signatures
4. **Skill Structure**: We created a SKILL.md following Cursor's skill format:
   - YAML frontmatter with name and description
   - Usage instructions organized by tool
   - Examples and best practices
   - Common workflows

**Key features of the skill:**
- **Trigger terms**: Keywords like "Pittsburgh", "road closure", "DOMI", "obstruction"
- **Progressive disclosure**: Main instructions in SKILL.md, detailed examples in examples.md
- **Concise**: Under 500 lines, focused on what AI needs to know

### FastMCP Server → CLI

The CLI was generated using FastMCP's built-in CLI generator:

```bash
fastmcp generate-cli https://domi-obstruction.fly.dev/mcp > cli.py
```

**What it provides:**
- Type-safe Python CLI using cyclopts
- Automatic argument parsing
- JSON input/output
- Rich formatting for errors
- Help text from docstrings

## Directory Structure

```
domiobstructionmcpserver/
├── .cursor/
│   └── skills/
│       └── domi-obstruction-mcp/         # Cursor Skill
│           ├── SKILL.md                   # Main skill (required)
│           ├── README.md                  # Installation guide
│           └── examples.md                # Usage examples
│
└── server/
    ├── cli.py                             # CLI implementation
    ├── SKILL.md                           # CLI documentation (skill format)
    ├── CLI_README.md                      # CLI quick start
    ├── CLI_USAGE.md                       # CLI comprehensive guide
    ├── install_cli.sh                     # CLI installer
    └── main.py                            # FastMCP server
```

## Using the Skill

### In Cursor

1. The skill is automatically discovered (it's in `../.cursor/skills/`)
2. Ask natural language questions about Pittsburgh road closures
3. The AI will automatically use your MCP tools

**Example conversation:**
```
You: What streets are closed in Pittsburgh right now?

AI: Let me check the current closures...
    [Calls list_active_entries()]
    
    There are currently 47 active road closures in Pittsburgh:
    - Fifth Avenue (Forbes to Bigelow): Water main replacement
    - Forbes Avenue (Oakland): Paving project
    ...
```

### With Other MCP Clients

Add to your MCP client config (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "domi-obstruction": {
      "type": "http",
      "url": "https://domi-obstruction.fly.dev/mcp"
    }
  }
}
```

Then use the skill as documentation for how to query the data.

## Using the CLI

### Basic Commands

```bash
# List available tools
python cli.py list-tools

# Get help
python cli.py --help
python cli.py call-tool --help
```

### Search Examples

```bash
# Text search
python cli.py call-tool search_obstructions --q "Fifth Avenue"

# Exact filter
python cli.py call-tool search_obstructions --filters '{"primary_street": "FIFTH AVE"}'

# Active only
python cli.py call-tool list_active_entries --limit 100

# Pagination
python cli.py call-tool search_obstructions --limit 500 --offset 0
```

### Scripting

```bash
# Save to file
python cli.py call-tool list_active_entries > closures.json

# Pipe to jq
python cli.py call-tool search_obstructions --q "Forbes" | \
  jq '.result.records[] | .primary_street'

# Count active
python cli.py call-tool list_active_entries --limit 9999 | \
  jq '.result.total'
```

## Customization

### Modifying the Skill

Edit `../.cursor/skills/domi-obstruction-mcp/SKILL.md`:

1. **Add new usage patterns**: Document common queries
2. **Update trigger terms**: Add keywords in the description
3. **Add examples**: Include real-world use cases
4. **Refine instructions**: Improve AI understanding

**Best practices:**
- Keep SKILL.md under 500 lines
- Use clear, concise language
- Include specific examples
- Add trigger keywords to description

### Customizing the CLI

Edit `../server/cli.py`:

1. **Change server URL**: Modify `CLIENT_SPEC`
2. **Add custom commands**: Add new `@app.command` functions
3. **Modify output format**: Customize `_print_tool_result()`
4. **Add shortcuts**: Create convenience commands

Example custom command:
```python
@app.command
async def active_on_street(street: str) -> None:
    """Get active closures on a specific street."""
    async with Client(CLIENT_SPEC) as client:
        result = await client.call_tool(
            'search_obstructions',
            {'q': street, 'filters': '{"active": true}'}
        )
        _print_tool_result(result)
```

## Advanced: Creating Skills for Other FastMCP Servers

### Step 1: Analyze the Server

```python
# List all tools
import mcp
async with mcp.Client("https://your-server.com/mcp") as client:
    tools = await client.list_tools()
    for tool in tools:
        print(f"{tool.name}: {tool.description}")
```

### Step 2: Create Skill Structure

```bash
mkdir -p .cursor/skills/your-skill-name
cd .cursor/skills/your-skill-name
```

### Step 3: Write SKILL.md

```markdown
---
name: your-skill-name
description: Brief description including when to use it and trigger keywords
---

# Your Skill Name

## Available Tools

### tool_name
Description and usage examples

## Common Workflows
Step-by-step guides
```

### Step 4: Generate CLI

```bash
fastmcp generate-cli https://your-server.com/mcp > cli.py
```

### Step 5: Add Documentation

Create README.md, examples.md, and CLI_USAGE.md following the templates in this project.

## Benefits of This Approach

### For Users
- **Natural language queries**: Just ask questions
- **Automatic discovery**: AI knows when to use your tools
- **Consistent interface**: Same tools via skill or CLI

### For Developers
- **Single source of truth**: FastMCP server defines everything
- **Auto-generated**: CLI and docs from server schema
- **Maintainable**: Update server, regenerate CLI

### For AI Assistants
- **Clear instructions**: Know exactly how to use tools
- **Context-aware**: Triggered by relevant keywords
- **Examples**: Learn from real usage patterns

## Maintenance

### Updating the CLI

When you update your FastMCP server:

```bash
# Regenerate CLI
fastmcp generate-cli https://domi-obstruction.fly.dev/mcp > cli.py

# Update documentation if needed
# (Tool signatures, new tools, changed behavior)
```

### Updating the Skill

When you add new tools or change behavior:

1. Update SKILL.md with new tool documentation
2. Add new examples to examples.md
3. Update trigger keywords in description if needed

### Testing

```bash
# Test CLI
python cli.py list-tools
python cli.py call-tool search_obstructions --q "test"

# Test skill (in Cursor)
Ask: "Test my DOMI skill by searching for Forbes Avenue closures"
```

## Troubleshooting

### Skill Not Triggering

1. Check skill location: Must be in `../.cursor/skills/skill-name/SKILL.md`
2. Verify frontmatter: Must have `name` and `description`
3. Add more trigger keywords to description
4. Restart Cursor to reload skills

### CLI Connection Issues

1. Check `CLIENT_SPEC` in cli.py
2. Verify server is running: `curl https://domi-obstruction.fly.dev/mcp`
3. Check network connectivity
4. Try local server for debugging

### Import Errors

```bash
# Install missing dependencies
pip install fastmcp cyclopts rich mcp

# Or use UV
uv run --with fastmcp python cli.py list-tools
```

## Next Steps

1. **Test the skill**: Ask Cursor questions about Pittsburgh road closures
2. **Try the CLI**: Run example commands from CLI_README.md
3. **Read examples**: Check examples.md for real-world usage
4. **Customize**: Adapt the skill and CLI to your needs
5. **Share**: Document your setup for team members

## Resources

- **FastMCP Docs**: https://github.com/jlowin/fastmcp
- **MCP Specification**: https://modelcontextprotocol.io
- **Cursor Skills**: Built-in skill system (automatic discovery)
- **This Project**: Examples of skill + CLI implementation

## Summary

You now have:

✅ **Cursor Skill** - AI assistants can use your MCP server via natural language
✅ **CLI Tool** - Command-line access with full scripting support  
✅ **Documentation** - Comprehensive guides and examples
✅ **Installation Scripts** - Easy setup for users
✅ **Examples** - Real-world usage patterns

Your FastMCP server is now accessible in multiple ways:
- **Via Cursor**: Natural language queries
- **Via CLI**: Command-line scripting
- **Via MCP Protocol**: Direct tool calls
- **Via HTTP**: API endpoint

All generated from your single FastMCP server definition! 🚀
