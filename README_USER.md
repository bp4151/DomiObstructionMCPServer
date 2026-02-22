# DOMI Obstruction MCP Server — User Guide

This guide explains how to connect MCP clients to the **Fly.io-hosted** DOMI Obstruction MCP server and how to call its tools. The server exposes WPRDC DOMI obstruction/closure data (streets, dates, permits, geometry).

---

## Adding the Fly.io MCP Server to Your Client

The Fly.io deployment uses **streaming HTTP**. You add the server by configuring your client with the public MCP URL. The same URL works from any platform; only the **config file location** differs by OS.

**MCP endpoint URL:**

```text
https://domi-obstruction.fly.dev/mcp
```

### Where to Edit MCP Config

Create or edit your MCP config file and add the `domi-obstruction-mcp` (or Fly.io) server entry as below.

| Platform | Config file (choose one) |
|----------|---------------------------|
| **Windows** | **Project:** `YourProject\.cursor\mcp.json` |
| | **User (Cursor):** `%APPDATA%\Cursor\User\globalStorage\cursor.mcp\mcp.json` or **Settings → MCP** in Cursor |
| **macOS** | **Project:** `YourProject/.cursor/mcp.json` |
| | **User (Cursor):** `~/Library/Application Support/Cursor/User/globalStorage/cursor.mcp/mcp.json` or **Settings → MCP** |
| **Linux** | **Project:** `YourProject/.cursor/mcp.json` |
| | **User (Cursor):** `~/.config/Cursor/User/globalStorage/cursor.mcp/mcp.json` or **Settings → MCP** |

Use **project-level** if you want this server only for a specific repo. Use **user-level** (or add the same block to your user config) to have it available in all projects.

### Config Block to Add

Add this to the `mcpServers` object in your MCP config file. If you already have other servers, add the `domi-obstruction-mcp` key alongside them.

**Windows / Mac / Linux (same JSON):**

```json
{
  "mcpServers": {
    "domi-obstruction-mcp": {
      "url": "https://domi-obstruction.fly.dev/mcp"
    }
  }
}
```

**Steps (all platforms):**

1. Open **Cursor Settings → MCP** (or open the config file path for your OS above).
2. Add the server entry with `"url": "https://domi-obstruction.fly.dev/mcp"`.
3. Save the file. Reload Cursor or run **Developer: Reload Window** if the server does not appear.

You should see **domi-obstruction-mcp** and tools: `search_obstructions`, `list_active_entries`, `obstruction_count`, `refresh_data`.

---

## Tool Reference and Sample Calls

The server exposes four tools. Arguments are passed as JSON. Responses are JSON (e.g. `records`, `total`, or status messages).

---

### 1. `search_obstructions`

Search DOMI obstruction/closure records. Returns permit/closure data with streets, dates, and geometry. Use for a single street, multiple streets (via query or filters), or free-text search.

**Parameters:**

| Name    | Type    | Required | Description |
|---------|---------|----------|-------------|
| `limit` | integer | No       | Max records to return (default `100`). |
| `offset`| integer | No       | Records to skip for pagination (default `0`). |
| `q`     | string  | No       | Full-text search (work description, streets, permit/closure IDs, applicant). |
| `filters` | string | No     | JSON object of field filters for exact match, e.g. `{"primary_street": "SECOND AVE"}`. |

**Sample 1 — Single street (filter by primary street):**

```json
{
  "limit": 20,
  "offset": 0,
  "filters": "{\"primary_street\": \"SECOND AVE\"}"
}
```

**Sample 2 — Single query (full-text search):**

```json
{
  "limit": 10,
  "q": "bridge"
}
```

**Sample 3 — Multiple streets (one query with full-text):**

Use `q` to match any of several street names in one call:

```json
{
  "limit": 50,
  "q": "FORBES AVE FIFTH AVE"
}
```

**Sample 4 — Multiple streets (separate filter calls):**

To get exact matches for each street, call the tool once per street with `filters`:

First street:

```json
{
  "limit": 25,
  "filters": "{\"primary_street\": \"FORBES AVE\"}"
}
```

Second street (e.g. next page or another request):

```json
{
  "limit": 25,
  "filters": "{\"primary_street\": \"FIFTH AVE\"}"
}
```

**Sample 5 — Pagination:**

```json
{
  "limit": 10,
  "offset": 20,
  "q": "closure"
}
```

**Response (conceptually):** JSON with `result` containing `records`, `total`, and `fields`. Each record includes fields such as `closure_id`, `permit_id`, `primary_street`, `from_street`, `to_street`, `work_description`, `from_date`, `to_date`, `geometry`, `wkt`, etc.

---

### 2. `list_active_entries`

List active DOMI obstruction/closure entries from the cached dataset. Use for “current” obstructions only.

**Parameters:**

| Name    | Type    | Required | Description |
|---------|---------|----------|-------------|
| `limit` | integer | No       | Max records to return (default `100`). |
| `offset`| integer | No       | Records to skip for pagination (default `0`). |

**Sample — First 50 active entries:**

```json
{
  "limit": 50,
  "offset": 0
}
```

**Sample — Next page:**

```json
{
  "limit": 50,
  "offset": 50
}
```

**Response:** JSON with `result` containing `records`, `total`, and `fields` (same record shape as search).

---

### 3. `obstruction_count`

Return the total number of DOMI obstruction records in the datastore (as of last ingestion).

**Parameters:** None.

**Sample:**

```json
{}
```

**Response:** e.g. `{ "total": 63211 }`.

---

### 4. `refresh_data`

Refresh the server’s cached obstruction data from the WPRDC source. Use after the dataset is updated and you want the server to reload.

**Parameters:**

| Name         | Type    | Required | Description |
|--------------|---------|----------|-------------|
| `max_records`| integer | No       | Optional cap on how many records to ingest. If omitted, uses env `WPRDC_INGEST_MAX_RECORDS` or all records. |

**Sample — Refresh all (or up to env limit):**

```json
{}
```

**Sample — Refresh with cap:**

```json
{
  "max_records": 5000
}
```

**Response:** JSON indicating success and that the cache was updated (exact format depends on server implementation).

---

## Quick Reference

| Tool                  | Purpose |
|-----------------------|---------|
| `search_obstructions` | Search by street(s), keyword, or filters; paginate with `limit`/`offset`. |
| `list_active_entries`| List active obstructions only; paginate with `limit`/`offset`. |
| `obstruction_count`  | Get total record count. |
| `refresh_data`       | Reload cache from WPRDC (optional `max_records`). |

For local or self-hosted setup, see [client/README_CLIENT.md](client/README_CLIENT.md) and [server/README_SERVER.md](server/README_SERVER.md).
