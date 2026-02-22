# Connect Cursor to the DOMI Obstruction MCP Server

This guide explains how to add the DOMI Obstruction MCP server to Cursor so you can use its tools (search obstructions, list entries, count, refresh) from the editor. The server supports two transports: **STDIO** (Cursor spawns the process) and **streaming HTTP** (HTTP endpoint; Cursor connects by URL).

## Prerequisites

- **STDIO:** [uv](https://docs.astral.sh/uv/) installed and the [server](../server/) dependencies installable (e.g. `cd server && uv sync`), **or** a Docker image built from the server (e.g. `Dockerfile_Stdio`).
- **Streaming HTTP:** The server must already be running with streaming HTTP transport (Docker image `Dockerfile_HTTP` or local with `MCP_TRANSPORT=streamable-http`). Cursor connects via URL; it does not start the process.

## 1. Open Cursor MCP settings

1. In Cursor, open **Settings** (e.g. `Ctrl+,` / `Cmd+,`).
2. Search for **MCP** or go to **Cursor Settings → MCP**.
3. You can edit the config in the UI or via the config file.

**Config file locations:**

- **Project-level:** `.cursor/mcp.json` in your project root (this repo: `DomiObstructionMCPServer/.cursor/mcp.json`).
- **User-level:** Cursor’s global MCP config (see Cursor docs for the path in your OS).

Use the **project-level** file if you want this server only for this repo.

## 2. Add the MCP server config

Create or edit `.cursor/mcp.json` in the **repository root** (parent of `client/` and `server/`). Choose **one** of the options below depending on whether you use **STDIO** or **streaming HTTP**.

### STDIO transport

Cursor starts the server process (or container) and communicates over stdin/stdout.

#### Option A: Run the server with uv (recommended for development)

Replace the `cwd` path with the **absolute** path to the `server` folder on your machine.

```json
{
  "mcpServers": {
    "domi-obstruction-mcp": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "C:\\Users\\YourUsername\\PycharmProjects\\DomiObstructionMCPServer\\server"
    }
  }
}
```

- **Windows:** Use double backslashes in `cwd`, or forward slashes: `"C:/Users/YourUsername/PycharmProjects/DomiObstructionMCPServer/server"`.
- **macOS/Linux:** Use your actual path, e.g. `"/home/you/projects/DomiObstructionMCPServer/server"`.

Ensure `uv` is on your PATH where Cursor runs.

#### Option B: Docker (Cursor spawns the stdio container)

Build the stdio image from the **server** directory:

```bash
cd server
docker build -f Dockerfile_Stdio -t domi-obstruction-mcp:stdio .
```

Then in `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "domi-obstruction-mcp": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "domi-obstruction-mcp:stdio"]
    }
  }
}
```

Optional: cap records for faster startup: add `-e WPRDC_INGEST_MAX_RECORDS=5000` to `args` (e.g. `["run", "--rm", "-i", "-e", "WPRDC_INGEST_MAX_RECORDS=5000", "domi-obstruction-mcp:stdio"]`).

#### Option C: Docker Compose (attach to running stdio container)

From the repo root: `docker compose up -d`. Then configure Cursor to attach to the running container:

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

Docker must be running and the container `domi-obstruction-mcp` must be up.

---

### Streaming HTTP transport

The server must be running with **streaming HTTP** (it listens on a port). Cursor connects by URL; no process is spawned by Cursor.

**Start the streaming HTTP server first** (pick one):

- **Docker:** From the **server** directory:
  ```bash
  docker build -f Dockerfile_HTTP -t domi-obstruction-mcp:http .
  docker run --rm -p 8000:8000 domi-obstruction-mcp:http
  ```
- **Local (uv):** From the **server** directory, set env and run:
  ```bash
  # PowerShell
  $env:MCP_TRANSPORT="streamable-http"; $env:MCP_PORT="8000"; uv run python main.py
  # Windows CMD
  set MCP_TRANSPORT=streamable-http & set MCP_PORT=8000 & uv run python main.py
  # macOS/Linux
  MCP_TRANSPORT=streamable-http MCP_PORT=8000 uv run python main.py
  ```

Then in `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "domi-obstruction-mcp-http": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Use a different host/port if you exposed the container or server differently (e.g. `http://localhost:9000/mcp` if using `-p 9000:9000` and `MCP_PORT=9000`).

## 3. Restart Cursor (if needed)

After saving `mcp.json`, Cursor may pick up the change automatically. If the server doesn’t appear under MCP tools, restart Cursor or reload the window (`Ctrl+Shift+P` / `Cmd+Shift+P` → “Developer: Reload Window”).

## 4. Verify the connection

1. In a Cursor chat, check that MCP tools are available (e.g. a tools or MCP section in the UI).
2. You should see **domi-obstruction-mcp** (STDIO) or **domi-obstruction-mcp-http** (streaming HTTP) and tools such as (names may be prefixed by the server):
   - **search_obstructions** – search DOMI obstruction records (limit, offset, q, filters).
   - **list_active_entries** – list active obstruction/closure entries (limit, offset).
   - **obstruction_count** – total record count.
   - **refresh_data** – refresh the in-memory cache from WPRDC (optional max_records).
3. Try a prompt that uses the server, e.g. “How many DOMI obstruction records are there?” or “Search the first 5 DOMI obstructions.”

## Troubleshooting

| Issue | What to try |
|-------|-------------|
| Server not listed / tools missing | Confirm `mcp.json` is valid JSON and in the correct path (e.g. repo root `.cursor/mcp.json`). Reload Cursor. |
| “Command not found” (uv) | Install [uv](https://docs.astral.sh/uv/) and ensure it’s on PATH for Cursor’s environment. |
| “Command not found” (docker) | Ensure Docker is installed and running; use Option A (uv) if you don’t use Docker. |
| Server starts then exits (STDIO) | Run the server manually from the `server` folder: `uv run python main.py`. Fix any Python/dependency errors. |
| Streaming HTTP: connection refused / no tools | Ensure the streaming HTTP server is running (e.g. `docker run --rm -p 8000:8000 domi-obstruction-mcp:http` or local with `MCP_TRANSPORT=streamable-http`). Check that the URL in `mcp.json` matches (e.g. `http://localhost:8000/mcp`). |
| Wrong or empty results | Server ingests on startup; first run can be slow. For faster startup, use `WPRDC_INGEST_MAX_RECORDS=5000` (env or Docker `-e`). |

For full server and tool details, see [**server/README_SERVER.md**](../server/README_SERVER.md).
