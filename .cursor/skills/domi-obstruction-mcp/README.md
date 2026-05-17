# DOMI Obstruction MCP Skill

This Cursor skill teaches AI assistants how to use the DOMI Obstruction MCP server to query Pittsburgh road closure and obstruction data.

## Installation

This skill is automatically available when placed in `.cursor/skills/domi-obstruction-mcp/`.

The MCP server must be configured separately in your MCP client settings.

## MCP Server Configuration

Add to your MCP settings (e.g., `~/.cursor/mcp_settings.json` or Claude Desktop config):

```json
{
  "mcpServers": {
    "domi-obstruction-http": {
      "type": "http",
      "url": "https://domi-obstruction.fly.dev/mcp"
    }
  }
}
```

Or for local STDIO:

```json
{
  "mcpServers": {
    "domi-obstruction-local": {
      "command": "python",
      "args": ["/path/to/server/main.py"],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

## Usage

Once installed, AI assistants will automatically know how to:
- Search for Pittsburgh road closures
- Query DOMI obstruction permits
- Find active construction affecting specific streets
- Analyze historical closure data

Just ask natural language questions like:
- "What streets in Pittsburgh are closed right now?"
- "Find all construction on Fifth Avenue"
- "Show me active DOMI permits"
- "How many road closures are there total?"

## Data Source

Data comes from the Western Pennsylvania Regional Data Center (WPRDC) DOMI obstruction dataset.
