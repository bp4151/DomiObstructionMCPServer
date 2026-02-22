# DOMI Obstruction MCP Server

An [MCP](https://modelcontextprotocol.io/) (Model Context Protocol) server that exposes **DOMI obstruction/closure data** from the [Western Pennsylvania Regional Data Center (WPRDC)](https://data.wprdc.org). Data is ingested from the WPRDC API on startup and served from an in-memory cache.

## Build and run

### Local (uv)

From the **server** directory:

```bash
cd server
uv run python main.py
```

Or with a system Python and existing venv:

```bash
cd server
pip install -e .
python main.py
```

The server uses **stdio** transport: it reads JSON-RPC from stdin and writes to stdout. An MCP client must launch this process and attach to its stdin/stdout.

### Docker

Two images are supported: **stdio** (default for MCP clients that spawn the process) and **streaming HTTP** (network endpoint for remote clients).

#### Stdio image (default)

Uses `Dockerfile_Stdio`. The server communicates over stdin/stdout; the client must attach to the container’s stdio.

From the **server** directory:

```bash
cd server
docker build -f Dockerfile_Stdio -t domi-obstruction-mcp:stdio .
```

Run (client attaches to stdin/stdout):

```bash
docker run -i --rm domi-obstruction-mcp:stdio
```

Optional: cap records ingested on startup (faster startup, smaller memory):

```bash
docker run -i --rm -e WPRDC_INGEST_MAX_RECORDS=5000 domi-obstruction-mcp:stdio
```

#### Streaming HTTP image

Uses `Dockerfile_HTTP`. The server listens on a port (default 8000) for streaming HTTP transport; clients connect via URL (e.g. `http://localhost:8000/mcp`).

From the **server** directory:

```bash
cd server
docker build -f Dockerfile_HTTP -t domi-obstruction-mcp:http .
```

Run (expose port 8000):

```bash
docker run --rm -p 8000:8000 domi-obstruction-mcp:http
```

Optional: custom port or record cap:

```bash
docker run --rm -p 9000:9000 -e MCP_PORT=9000 -e WPRDC_INGEST_MAX_RECORDS=5000 domi-obstruction-mcp:http
```

### Environment variables

| Variable | Description |
|----------|-------------|
| `WPRDC_INGEST_MAX_RECORDS` | Optional. Max number of records to ingest on startup. If unset, all records are fetched (slower first start). Example: `5000`. |
| `MCP_TRANSPORT` | Optional. Transport to use: `stdio` (default) or `streamable-http`. Only relevant when running the server directly (e.g. Docker streaming HTTP image sets this to `streamable-http`). |
| `MCP_HOST` | Optional. For streaming HTTP transport, bind address. Default: `0.0.0.0`. |
| `MCP_PORT` | Optional. For streaming HTTP transport, port to listen on. Default: `8000`. |

---

## Client configuration

Configure your MCP client to start this server as a **stdio** subprocess, or connect to the **streaming HTTP** endpoint. Use the path to the **server** folder as the working directory when running locally with stdio.

### Cursor — mcp.json blocks

Add the server in **Settings → MCP** (or `.cursor/mcp.json`). Use one of the following depending on transport.

#### STDIO transport

Cursor spawns the server process (or Docker container) and communicates over stdin/stdout.

**Local (uv):**

```json
{
  "mcpServers": {
    "domi-obstruction-mcp": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "C:\\Users\\You\\PycharmProjects\\DomiObstructionMCPServer\\server"
    }
  }
}
```

**Docker (stdio image):** Build with `Dockerfile_Stdio` as `domi-obstruction-mcp:stdio` (or `:latest`). Ensure the container is running first (e.g. `docker compose up -d`), or use `run --rm -i` so Cursor spawns it:

```json
{
  "mcpServers": {
    "domi-obstruction-mcp": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "domi-obstruction-mcp:latest"],
      "transport": "stdio"
    }
  }
}
```

#### Streaming HTTP transport

The server must be running as the **streaming HTTP** image with a port exposed (e.g. `docker run --rm -p 8000:8000 domi-obstruction-mcp:http`). Cursor connects via URL; no process is spawned.

```json
{
  "mcpServers": {
    "domi-obstruction-mcp": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Use a different host/port if you run the container with `-p HOST_PORT:8000` or `MCP_PORT` (e.g. `http://localhost:9000/mcp`).

#### Testing the streaming HTTP server

1. **Start the streaming HTTP server** (pick one):

   **Docker (recommended):**
   ```bash
   cd server
   docker build -f Dockerfile_HTTP -t domi-obstruction-mcp:http .
   docker run --rm -p 8000:8000 domi-obstruction-mcp:http
   ```

   **Local (uv) with streaming HTTP:**
   ```bash
   cd server
   set MCP_TRANSPORT=streamable-http
   set MCP_PORT=8000
   uv run python main.py
   ```
   On PowerShell: `$env:MCP_TRANSPORT="streamable-http"; $env:MCP_PORT="8000"; uv run python main.py`

2. **Check that the server is up** — in another terminal:
   ```bash
   curl -s -o NUL -w "%{http_code}" http://localhost:8000/
   ```
   A response (e.g. 200 or 404) means the server is listening. Or open `http://localhost:8000/` in a browser.

3. **Use Cursor** — ensure `.cursor/mcp.json` has the streaming HTTP entry (e.g. `"url": "http://localhost:8000/mcp"`). Restart Cursor or reload MCP, then pick the **domi-obstruction-mcp-http** server and try a tool (e.g. `obstruction_count` or `search_obstructions`).

### Cursor — legacy attach (Docker stdio)

Alternatively, with a **running** stdio container (e.g. `docker compose up -d`), you can attach by container name:

```json
{
  "mcpServers": {
    "domi-obstruction-mcp": {
      "command": "docker",
      "args": ["attach", "domi-obstruction-mcp"]
    }
  }
}
```

### Claude Desktop

In your Claude Desktop config (e.g. `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "domi-obstruction": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "C:\\path\\to\\DomiObstructionMCPServer\\server"
    }
  }
}
```

### Generic MCP client

Start the server process with stdin/stdout connected (no extra arguments). The client sends [MCP JSON-RPC](https://modelcontextprotocol.io/specification/2025-11-25) over stdin and reads responses from stdout.

---

## Tools (tool calls)

The server exposes two tools. Clients discover them via `tools/list` and invoke them via `tools/call`.

### 1. `wprdc_search_obstructions`

Search DOMI obstruction/closure records. Returns permit and closure data including streets, dates, and geometry. Results are served from the cache populated at startup.

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `limit` | integer | No | Max records to return. Default: `100`. |
| `offset` | integer | No | Number of records to skip (pagination). Default: `0`. |
| `q` | string | No | Full-text search over work description, streets, permit/closure IDs, applicant. |
| `filters` | string | No | JSON object of field filters for exact match. Example: `"{\"primary_street\": \"SECOND AVE\"}"`. |

**Example tool calls (arguments JSON):**

```json
{ "limit": 10, "offset": 0 }
```

```json
{ "limit": 5, "q": "bridge" }
```

```json
{ "limit": 20, "filters": "{\"primary_street\": \"SECOND AVE\"}" }
```

**Response:** JSON with `success: true` and `result` containing `records`, `total`, and `fields`. Each record includes fields such as `closure_id`, `permit_id`, `primary_street`, `from_street`, `to_street`, `work_description`, `from_date`, `to_date`, `geometry`, `wkt`, and others.

---

### 2. `wprdc_obstruction_count`

Return the total number of DOMI obstruction records (from the WPRDC datastore, as of ingestion).

**Arguments:** None.

**Example tool call (arguments JSON):**

```json
{}
```

**Response:** JSON of the form `{ "total": 63211 }`.

---

## Data source

- **API:** [WPRDC Datastore Search](https://data.wprdc.org/api/3/action/datastore_search)
- **Resource ID:** `a9a1d93a-9d3b-4c18-bd80-82ed6f86404a`
- **Content:** City of Pittsburgh DOMI (Department of Mobility and Infrastructure) obstruction/closure permits.
