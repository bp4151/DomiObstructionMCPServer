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

## Dependencies

Dependencies are declared in **`pyproject.toml`** in the `[project]` `dependencies` list. All commands below assume you are in the **server** directory.

### Adding a dependency

1. Edit `pyproject.toml` and add a line to the `dependencies` list, e.g.:
   ```toml
   dependencies = [
       "httpx>=0.28.1",
       "mcp[cli]>=1.23.0",
       "python-dotenv>=1.0.0",
       "your-package>=1.0.0",
   ]
   ```
2. Install so the environment matches the file:
   ```bash
   uv sync
   ```
   Or with pip:
   ```bash
   pip install -e .
   ```

To look up a package name or available versions: `pip index versions <package-name>`, or use `uv add <package-name>` to add and install in one step.

### Updating a dependency

1. Change the version in `pyproject.toml` (e.g. `"httpx>=0.28.1"` → `"httpx>=0.29.0"` or pin with `==`).
2. Reinstall:
   ```bash
   uv sync
   ```
   Or with pip:
   ```bash
   pip install -e . --upgrade
   ```
   If you use a lockfile (e.g. `uv.lock`), run `uv lock --upgrade` then `uv sync`.

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

The server exposes several tools for querying and analyzing DOMI data.

### 1. `search_obstructions`

Search DOMI obstruction/closure records. Returns permit and closure data including streets, dates, and geometry. Results are served from the cache populated at startup.

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `limit` | integer | No | Max records to return. Default: `100`. |
| `offset` | integer | No | Number of records to skip (pagination). Default: `0`. |
| `q` | string | No | Full-text search over work description, streets, permit/closure IDs, applicant. |
| `filters` | string | No | JSON object of field filters for exact match. Example: `"{\"primary_street\": \"SECOND AVE\"}"`. |
| `gpx_content` | string | Yes | XML content of a GPX file. Only for `match_gpx_obstructions`. |
| `distance_threshold` | number | No | Distance in degrees to consider a match. Default: `0.0001` (~10m). |

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

### 2. `list_active_entries`

List all active DOMI obstruction/closure entries from the cached dataset.

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `limit` | integer | No | Max records to return. Default: `100`. |
| `offset` | integer | No | Number of records to skip (pagination). Default: `0`. |

**Example tool call:**

```json
{ "limit": 50, "offset": 0 }
```

**Response:** JSON with `success: true` and `result` containing `records`, `total`, and `fields`.

---

### 3. `obstruction_count`

Return the total number of DOMI obstruction records (from the WPRDC datastore, as of ingestion).

**Arguments:** None.

**Example tool call (arguments JSON):**

```json
{}
```

**Response:** JSON of the form `{ "total": 63211 }`.

---

### 4. `match_gpx_obstructions`

Find active DOMI records that match route segments in a GPX file. This tool uses spatial matching to identify obstructions that intersect or are very close to a provided route.

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `gpx_content` | string | Yes | The XML content of the GPX file. |
| `distance_threshold` | number | No | Distance in degrees to consider a match. Default: `0.0001` (~10m). |

**Example tool call (arguments JSON):**

```json
{
  "gpx_content": "<?xml version=\"1.0\"...<trk>...</gpx>",
  "distance_threshold": 0.0002
}
```

**Response:** JSON with `success: true`, `matches` (list of record objects), and `total_matches`.

---

### 5. `refresh_data`

Refresh cached obstruction data from the WPRDC source by running ingestion.

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `max_records` | integer | No | Optional cap on how many records to ingest. |

**Example tool call:**

```json
{ "max_records": 5000 }
```

**Response:** JSON with `success: true`, `cached_records`, and `total_available`.

---

## Data source

- **API:** [WPRDC Datastore Search](https://data.wprdc.org/api/3/action/datastore_search)
- **Resource ID:** `a9a1d93a-9d3b-4c18-bd80-82ed6f86404a`
- **Content:** City of Pittsburgh DOMI (Department of Mobility and Infrastructure) obstruction/closure permits.
