import json
import os
import sys
from typing import Annotated

import cyclopts
import mcp.types
from rich.console import Console

from fastmcp import Client

# Modify this to change how the CLI connects to the MCP server.
CLIENT_SPEC = 'https://domi-obstruction.fly.dev/mcp'

app = cyclopts.App(name="domi-obstruction.fly.dev", help="CLI for domi-obstruction.fly.dev MCP server")
call_tool_app = cyclopts.App(name="call-tool", help="Call a tool on the server")
app.command(call_tool_app)

console = Console()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _print_tool_result(result):
    if result.is_error:
        for block in result.content:
            if isinstance(block, mcp.types.TextContent):
                console.print(f"[bold red]Error:[/bold red] {block.text}")
            else:
                console.print(f"[bold red]Error:[/bold red] {block}")
        sys.exit(1)

    if result.structured_content is not None:
        console.print_json(json.dumps(result.structured_content))
        return

    for block in result.content:
        if isinstance(block, mcp.types.TextContent):
            console.print(block.text)
        elif isinstance(block, mcp.types.ImageContent):
            size = len(block.data) * 3 // 4
            console.print(f"[dim][Image: {block.mimeType}, ~{size} bytes][/dim]")
        elif isinstance(block, mcp.types.AudioContent):
            size = len(block.data) * 3 // 4
            console.print(f"[dim][Audio: {block.mimeType}, ~{size} bytes][/dim]")


async def _call_tool(tool_name: str, arguments: dict) -> None:
    # Filter out None values and empty lists (defaults for optional array params)
    filtered = {
        k: v
        for k, v in arguments.items()
        if v is not None and (not isinstance(v, list) or len(v) > 0)
    }
    async with Client(CLIENT_SPEC) as client:
        result = await client.call_tool(tool_name, filtered, raise_on_error=False)
        _print_tool_result(result)
        if result.is_error:
            sys.exit(1)


# ---------------------------------------------------------------------------
# List / read commands
# ---------------------------------------------------------------------------


@app.command(name="match-gpx")
async def match_gpx(
    path: Annotated[str | None, cyclopts.Parameter(help="Path to GPX file")] = None,
    distance_threshold: Annotated[
        float, cyclopts.Parameter(help="Distance threshold in degrees")
    ] = 0.0001,
) -> None:
    """Find active DOMI records matching a GPX route."""
    if not path:
        from rich.prompt import Prompt

        path = Prompt.ask("[bold cyan]Enter path to GPX file[/bold cyan]")

    if not path or not os.path.exists(path):
        console.print(f"[bold red]Error:[/bold red] File not found: {path}")
        return

    try:
        with open(path, "r") as f:
            gpx_content = f.read()
    except Exception as e:
        console.print(f"[bold red]Error reading file:[/bold red] {e}")
        return

    await _call_tool(
        "match_gpx_obstructions",
        {"gpx_content": gpx_content, "distance_threshold": distance_threshold},
    )


@app.command
async def list_tools() -> None:
    """List available tools."""
    async with Client(CLIENT_SPEC) as client:
        tools = await client.list_tools()
        if not tools:
            console.print("[dim]No tools found.[/dim]")
            return
        for tool in tools:
            sig_parts = []
            props = tool.inputSchema.get("properties", {})
            required = set(tool.inputSchema.get("required", []))
            for pname, pschema in props.items():
                ptype = pschema.get("type", "string")
                if pname in required:
                    sig_parts.append(f"{pname}: {ptype}")
                else:
                    sig_parts.append(f"{pname}: {ptype} = ...")
            sig = f"{tool.name}({', '.join(sig_parts)})"
            console.print(f"  [cyan]{sig}[/cyan]")
            if tool.description:
                console.print(f"    {tool.description}")
            console.print()


@app.command
async def list_resources() -> None:
    """List available resources."""
    async with Client(CLIENT_SPEC) as client:
        resources = await client.list_resources()
        if not resources:
            console.print("[dim]No resources found.[/dim]")
            return
        for r in resources:
            console.print(f"  [cyan]{r.uri}[/cyan]")
            desc_parts = [r.name or "", r.description or ""]
            desc = " � ".join(p for p in desc_parts if p)
            if desc:
                console.print(f"    {desc}")
        console.print()


@app.command
async def read_resource(uri: Annotated[str, cyclopts.Parameter(help="Resource URI")]) -> None:
    """Read a resource by URI."""
    async with Client(CLIENT_SPEC) as client:
        contents = await client.read_resource(uri)
        for block in contents:
            if isinstance(block, mcp.types.TextResourceContents):
                console.print(block.text)
            elif isinstance(block, mcp.types.BlobResourceContents):
                size = len(block.blob) * 3 // 4
                console.print(f"[dim][Blob: {block.mimeType}, ~{size} bytes][/dim]")


@app.command
async def list_prompts() -> None:
    """List available prompts."""
    async with Client(CLIENT_SPEC) as client:
        prompts = await client.list_prompts()
        if not prompts:
            console.print("[dim]No prompts found.[/dim]")
            return
        for p in prompts:
            args_str = ""
            if p.arguments:
                parts = [a.name for a in p.arguments]
                args_str = f"({', '.join(parts)})"
            console.print(f"  [cyan]{p.name}{args_str}[/cyan]")
            if p.description:
                console.print(f"    {p.description}")
        console.print()


@app.command
async def get_prompt(
    name: Annotated[str, cyclopts.Parameter(help="Prompt name")],
    *arguments: str,
) -> None:
    """Get a prompt by name. Pass arguments as key=value pairs."""
    parsed: dict[str, str] = {}
    for arg in arguments:
        if "=" not in arg:
            console.print(f"[bold red]Error:[/bold red] Invalid argument {arg!r} � expected key=value")
            sys.exit(1)
        key, value = arg.split("=", 1)
        parsed[key] = value

    async with Client(CLIENT_SPEC) as client:
        result = await client.get_prompt(name, parsed or None)
        for msg in result.messages:
            console.print(f"[bold]{msg.role}:[/bold]")
            if isinstance(msg.content, mcp.types.TextContent):
                console.print(f"  {msg.content.text}")
            elif isinstance(msg.content, mcp.types.ImageContent):
                size = len(msg.content.data) * 3 // 4
                console.print(f"  [dim][Image: {msg.content.mimeType}, ~{size} bytes][/dim]")
            else:
                console.print(f"  {msg.content}")
            console.print()


# ---------------------------------------------------------------------------
# Tool commands (generated from server schema)
# ---------------------------------------------------------------------------

@call_tool_app.command(name='search_obstructions')
async def search_obstructions(
    *,
    limit: Annotated[int, cyclopts.Parameter(help="")] = 100,
    offset: Annotated[int, cyclopts.Parameter(help="")] = 0,
    q: Annotated[str | None, cyclopts.Parameter(help="JSON Schema: {\n                            \"anyOf\": [\n                              {\n                                \"type\": \"string\"\n                              },\n                              {\n                                \"type\": \"null\"\n                              }\n                            ],\n                            \"default\": null,\n                            \"title\": \"Q\"\n                          }")] = None,
    filters: Annotated[str | None, cyclopts.Parameter(help="JSON Schema: {\n                            \"anyOf\": [\n                              {\n                                \"type\": \"string\"\n                              },\n                              {\n                                \"type\": \"null\"\n                              }\n                            ],\n                            \"default\": null,\n                            \"title\": \"Filters\"\n                          }")] = None,
) -> None:
    '''Search DOMI (Department of Mobility and Infrastructure) obstruction/closure records from WPRDC.

Returns permit/closure data with streets, dates, and geometry. Use limit/offset for pagination.

Args:
    limit: Max records to return (default 100).
    offset: Number of records to skip for pagination.
    q: Optional full-text search query.
    filters: Optional JSON object of field filters, e.g. {"primary_street": "SECOND AVE"}.
'''
    # Parse JSON parameters
    q_parsed = json.loads(q) if isinstance(q, str) else q
    filters_parsed = json.loads(filters) if isinstance(filters, str) else filters

    await _call_tool('search_obstructions', {'limit': limit, 'offset': offset, 'q': q_parsed, 'filters': filters_parsed})


@call_tool_app.command(name='list_active_entries')
async def list_active_entries(
    *,
    limit: Annotated[int, cyclopts.Parameter(help="")] = 100,
    offset: Annotated[int, cyclopts.Parameter(help="")] = 0,
) -> None:
    '''List all active DOMI obstruction/closure entries from the cached dataset.

Returns permit/closure records with streets, dates, and geometry. Use limit/offset for pagination.

Args:
    limit: Max records to return (default 100).
    offset: Number of records to skip for pagination.
'''
    await _call_tool('list_active_entries', {'limit': limit, 'offset': offset})


@call_tool_app.command(name='obstruction_count')
async def obstruction_count(
) -> None:
    '''Return total number of DOMI obstruction records in the WPRDC datastore.'''
    await _call_tool('obstruction_count', {})


@call_tool_app.command(name='refresh_data')
async def refresh_data(
    *,
    max_records: Annotated[str | None, cyclopts.Parameter(help="JSON Schema: {\n                            \"anyOf\": [\n                              {\n                                \"type\": \"integer\"\n                              },\n                              {\n                                \"type\": \"null\"\n                              }\n                            ],\n                            \"default\": null,\n                            \"title\": \"Max Records\"\n                          }")] = None,
) -> None:
    '''Refresh cached obstruction data from the WPRDC source by running ingestion.

Fetches the latest data from WPRDC and updates the in-memory cache used by
search_obstructions, list_active_entries, and obstruction_count.

Args:
    max_records: Optional cap on how many records to ingest. If omitted, uses
        WPRDC_INGEST_MAX_RECORDS from environment, or ingests all records.
'''
    # Parse JSON parameters
    max_records_parsed = json.loads(max_records) if isinstance(max_records, str) else max_records

    await _call_tool('refresh_data', {'max_records': max_records_parsed})


@call_tool_app.command(name="match_gpx_obstructions")
async def match_gpx_obstructions(
    *,
    gpx_content: Annotated[str, cyclopts.Parameter(help="GPX XML content")],
    distance_threshold: Annotated[
        float,
        cyclopts.Parameter(
            help='JSON Schema: {\n                            "type": "number",\n                            "default": 0.0001,\n                            "title": "Distance Threshold"\n                          }'
        ),
    ] = 0.0001,
) -> None:
    """Find active DOMI records that match route segments in a GPX file."""
    await _call_tool(
        "match_gpx_obstructions",
        {"gpx_content": gpx_content, "distance_threshold": distance_threshold},
    )


if __name__ == "__main__":
    app()
