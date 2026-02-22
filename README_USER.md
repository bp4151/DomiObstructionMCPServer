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

## Example

Query: 

domi-obstruction-mcp-flyio list-all-active where the primary_street contains "'Fort Pitt' Smithfield Commonwealth Penn
Smallman Butler 40th Friendship Negley Howe Beechwood Lilac". Remove the permit_type column, add work columns, and display
the results in markdown

  1. N NEGLEY AVE
  ┌─────────────────────────┬──────────────────────────────────────────────────────────────────────────────┐
  │ Field                   │ Value                                                                        │
  ├─────────────────────────┼──────────────────────────────────────────────────────────────────────────────┤
  │ closure_id              │ DOMI-PL-2025-06643-7                                                         │
  │ primary_street          │ N NEGLEY AVE                                                                 │
  │ from_street → to_street │ CALLOWHILL ST → MELLON TER                                                   │
  │ from_date               │ 2025-06-09                                                                   │
  │ to_date                 │ 2026-05-24                                                                   │
  │ work_description        │ DLCO REPLACING POLES AND UPGRADING SYSTEM FOR NEW PWSA HIGHLAND PUMP STATION │
  │ work_type               │ —                                                                            │
  │ applicant_name          │ DUQUESNE LIGHT COMPANY DOMI ACCOUNT                                          │
  │ contractor_name         │ DUQUESNE LIGHT COMPANY                                                       │
  │ special_instructions    │ —                                                                            │
  │ weekday_hours           │ 9AM-3PM                                                                      │
  │ weekend_hours           │ 7AM-5PM                                                                      │
  └─────────────────────────┴──────────────────────────────────────────────────────────────────────────────┘


  2. FORT PITT BLVD
  ┌────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Field          │ Value                                                                                                           │
  ├────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ closure_id     │ DOMI-CS-2025-06060-1                                                                                            │
  │ primary_street │ FORT PITT BLVD                                                                                                  │
  │ from_street →  │ STANWIX ST → FORT PITT BLVD RAMP                                                                                │
  │ to_street      │                                                                                                                 │
  │ from_date      │ 2025-06-09                                                                                                      │
  │ to_date        │ 2026-04-10                                                                                                      │
  │ work_descripti │ PHASE 3 CONSTRUCTION STAGING PERMIT. DEMOLITION OF BALCONIES ABOVE. SIDEWALK CLOSURE FOR PEDESTRIAN SAFETY. 12  │
  │ on             │ STORIES OF SCAFFOLDING TO BE ERECTED TO COMPLETE DEMOLITION.                                                    │
  │ work_type      │ BARRICADE                                                                                                       │
  │ applicant_name │ ERNEST SOTA                                                                                                     │
  │ contractor_nam │ SOTA CONSTRUCTION SERVICES, INC                                                                                 │
  │ e              │                                                                                                                 │
  │ special_instru │ —                                                                                                               │
  │ ctions         │                                                                                                                 │
  │ weekday_hours  │ ALL                                                                                                             │
  │ weekend_hours  │ ALL                                                                                                             │
  └────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  3. SMALLMAN ST
  ┌────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Field          │ Value                                                                                                           │
  ├────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ closure_id     │ DOMI-CS-2023-09809-1                                                                                            │
  │ primary_street │ SMALLMAN ST                                                                                                     │
  │ from_street →  │ 29TH ST → 30TH ST                                                                                               │
  │ to_street      │                                                                                                                 │
  │ from_date      │ 2023-10-30                                                                                                      │
  │ to_date        │ 2026-07-04                                                                                                      │
  │ work_descripti │ INSTALLATION OF BARRICADES ON SMALLMAN STREET AND SPRUCE WAY TO FACILITATE THE REDEVELOPMENT OF 2929 SMALLMAN   │
  │ on             │ STREET. KEEP 2 TRAVEL LANES OPEN ON SMALLMAN ST JANUARY 5-15, 2026.                                             │
  │ work_type      │ BARRICADE                                                                                                       │
  │ applicant_name │ KYLE BROWN                                                                                                      │
  │ contractor_nam │ THE HUDSON GROUP INC                                                                                            │
  │ e              │                                                                                                                 │
  │ special_instru │ KEEP 2 TRAVEL LANES OPEN ON SMALLMAN ST JANUARY 5-15, 2026.                                                     │
  │ ctions         │                                                                                                                 │
  │ weekday_hours  │ ALL                                                                                                             │
  │ weekend_hours  │ ALL                                                                                                             │
  └────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  4. BUTLER ST
  ┌──────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Field    │ Value                                                                                                                 │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ closure_ │ DOMI-CS-2024-04679-2                                                                                                  │
  │ id       │                                                                                                                       │
  │ primary_ │ BUTLER ST                                                                                                             │
  │ street   │                                                                                                                       │
  │ from_str │ MCCANDLESS AVE → 53RD ST                                                                                              │
  │ eet      │                                                                                                                       │
  │ →        │                                                                                                                       │
  │ to_stree │                                                                                                                       │
  │ t        │                                                                                                                       │
  │ from_dat │ 2024-04-22                                                                                                            │
  │ e        │                                                                                                                       │
  │ to_date  │ 2026-03-11                                                                                                            │
  │ work_des │ SELECTIVE CLOSURE OF SIDEWALKS AND PARKING LANES ADJACENT TO PROJECT SITE FOR LAYDOWN, DUMPSTERS, OFFLOADING,         │
  │ cription │ TRAILERS AND TEMP TOILETS, ETC. 2 PHASES BEING PROPOSED. REFERENCE THE MPT PLAN FOR SPECIFICS. AROUND THE CLOCK       │
  │          │ CLOSURE OF THE SIDEWALK AND PARKING LANE ON BUTLER ST AND ON MCCANDLESS AVE.                                          │
  │ work_typ │ BARRICADE                                                                                                             │
  │ e        │                                                                                                                       │
  │ applican │ NATHAN HEID                                                                                                           │
  │ t_name   │                                                                                                                       │
  │ contract │ FRANJO CONSTRUCTION CORPORATION                                                                                       │
  │ or_name  │                                                                                                                       │
  │ special_ │ COORDINATE WITH OTHER AREA CONSTRUCTION; CONTACT PRT (412)566-5321; MAINTAIN PEDESTRIAN PATH; ONE LANE EACH           │
  │ instruct │ DIRECTION; POST NO PARKING 48 HRS IN ADVANCE; PENNDOT 212/213.                                                        │
  │ ions     │                                                                                                                       │
  │ weekday_ │ ALL                                                                                                                   │
  │ hours    │                                                                                                                       │
  │ weekend_ │ ALL                                                                                                                   │
  │ hours    │                                                                                                                       │
  └──────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  5. PENN AVE
  ┌──────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Field                │ Value                                                                                                     │
  ├──────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ closure_id           │ DOMI-CS-2024-15816-1                                                                                      │
  │ primary_street       │ PENN AVE                                                                                                  │
  │ from_street →        │ 27TH ST → 28TH ST                                                                                         │
  │ to_street            │                                                                                                           │
  │ from_date            │ 2025-01-13                                                                                                │
  │ to_date              │ 2026-06-11                                                                                                │
  │ work_description     │ FENCING AROUND 2700 PENN (APN# 25-K-261) TO BEGIN WORK UNDER DP-2024-08439.                               │
  │ work_type            │ BARRICADE                                                                                                 │
  │ applicant_name       │ MARK ROBERTS                                                                                              │
  │ contractor_name      │ FRANJO CONSTRUCTION CORPORATION                                                                           │
  │ special_instructions │ PENNDOT PUB. 213 COMPLIANT PEDESTRIAN DETOUR REQUIRED DURING ALL SIDEWALK CLOSURES LEAVING 4' OR LESS OF  │
  │                      │ CLEARANCE.                                                                                                │
  │ weekday_hours        │ ALL                                                                                                       │
  │ weekend_hours        │ ALL                                                                                                       │
  └──────────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  6. PENN AVE
  ┌───────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Field         │ Value                                                                                                            │
  ├───────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ closure_id    │ DOMI-OP-2025-09309-3                                                                                             │
  │ primary_stree │ PENN AVE                                                                                                         │
  │ t             │                                                                                                                  │
  │ from_street → │ 35TH ST → 36TH ST                                                                                                │
  │ to_street     │                                                                                                                  │
  │ from_date     │ 2025-07-28                                                                                                       │
  │ to_date       │ 2026-04-03                                                                                                       │
  │ work_descript │ SMALL DIAMETER WATER MAIN INSTALLATION AND REPLACEMENT ALONG WITH SERVICE LINE REPLACEMENTS ON THE PUBLIC AND    │
  │ ion           │ PRIVATE SIDE ON LIGONIER ST. INTERSECTIONS INCLUDED WITH WORK @ SPRING WAY & PENN AVE.                           │
  │ work_type     │ DOMI APPROVED CAPITAL UTILITY PROJECT                                                                            │
  │ applicant_nam │ KEWEI ZHOU                                                                                                       │
  │ e             │                                                                                                                  │
  │ contractor_na │ AECOM DBA PWSA                                                                                                   │
  │ me            │                                                                                                                  │
  │ special_instr │ CONTACT PITTSBURGH REGIONAL TRANSIT AT 412-566-5321 AT LEAST 48 HOURS PRIOR TO TRAVEL LANE OBSTRUCTIONS OR       │
  │ uctions       │ CLOSURES.                                                                                                        │
  │ weekday_hours │ 7AM-5PM                                                                                                          │
  │ weekend_hours │ 7AM-5PM                                                                                                          │
  └───────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  7. PENN AVE
  ┌─────────────────────────┬────────────────────────────────────────┐
  │ Field                   │ Value                                  │
  ├─────────────────────────┼────────────────────────────────────────┤
  │ closure_id              │ DOMI-OP-2025-09309-4                   │
  │ primary_street          │ PENN AVE                               │
  │ from_street → to_street │ 35TH ST → 36TH ST                      │
  │ from_date               │ 2025-07-28                             │
  │ to_date                 │ 2026-04-03                             │
  │ work_description        │ Same as #6 (segment 4 of same permit). │
  │ work_type               │ DOMI APPROVED CAPITAL UTILITY PROJECT  │
  │ applicant_name          │ KEWEI ZHOU                             │
  │ contractor_name         │ AECOM DBA PWSA                         │
  │ special_instructions    │ Same as #6.                            │
  │ weekday_hours           │ 7AM-5PM                                │
  │ weekend_hours           │ 7AM-5PM                                │
  └─────────────────────────┴────────────────────────────────────────┘

  8. BEECHWOOD BLVD
  ┌──────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Field                │ Value                                                                                                     │
  ├──────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ closure_id           │ DOMI-OP-2025-11996-1                                                                                      │
  │ primary_street       │ BEECHWOOD BLVD                                                                                            │
  │ from_street →        │ FORBES AVE → BEACON ST                                                                                    │
  │ to_street            │                                                                                                           │
  │ from_date            │ 2025-10-06                                                                                                │
  │ to_date              │ 2026-03-22                                                                                                │
  │ work_description     │ WATER SERVICE LINE VERIFICATIONS AND LEAD SERVICE LINE REPLACEMENTS ON PUBLIC SIDE AND PRIVATE SIDE ON    │
  │                      │ BEECHWOOD BLVD.                                                                                           │
  │ work_type            │ DOMI APPROVED STAND ALONE SERVICE LINES PROJECT                                                           │
  │ applicant_name       │ KATIE MARCHESE                                                                                            │
  │ contractor_name      │ AECOM DBA PWSA                                                                                            │
  │ special_instructions │ MAINTAIN TWO LANES OF TRAFFIC FOR THE COMMERCIAL ST DETOUR                                                │
  │ weekday_hours        │ 9AM-3PM                                                                                                   │
  │ weekend_hours        │ 7AM-5PM                                                                                                   │
  └──────────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  9. SMITHFIELD ST

  ┌───────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Field         │ Value                                                                                                            │
  ├───────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ closure_id    │ DOMI-SIDE-2025-06532-1                                                                                           │
  │ primary_stree │ SMITHFIELD ST                                                                                                    │
  │ t             │                                                                                                                  │
  │ from_street → │ FORT PITT BLVD → FIRST AVE                                                                                       │
  │ to_street     │                                                                                                                  │
  │ from_date     │ 2025-11-03                                                                                                       │
  │ to_date       │ 2026-03-13                                                                                                       │
  │ work_descript │ SIDEWALK MAINTENANCE ALONG FORT PITT BOULEVARD AND SMITHFIELD STREET. SIDEWALK ABOVE UTILITY AND BASEMENT ACCESS │
  │ ion           │ VAULTS FOR 4 SMITHFIELD STREET. CLEAN/REPAINT OR FULL SLAB REPLACEMENT.                                          │
  │ work_type     │ —                                                                                                                │
  │ applicant_nam │ MICHAEL MCCORMICK                                                                                                │
  │ e             │                                                                                                                  │
  │ contractor_na │ WODA CONSTRUCTION, INC.                                                                                          │
  │ me            │                                                                                                                  │
  │ special_instr │ PENNDOT PUB. 213 COMPLIANT PEDESTRIAN DETOUR REQUIRED DURING ALL SIDEWALK CLOSURES.                              │
  │ uctions       │                                                                                                                  │
  │ weekday_hours │ 9AM-3PM                                                                                                          │
  │ weekend_hours │ 7AM-5PM                                                                                                          │
  └───────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  10. FORT PITT BLVD
  ┌─────────────────────────┬─────────────────────────────────────────────┐
  │ Field                   │ Value                                       │
  ├─────────────────────────┼─────────────────────────────────────────────┤
  │ closure_id              │ DOMI-SIDE-2025-06532-2                      │
  │ primary_street          │ FORT PITT BLVD                              │
  │ from_street → to_street │ SMITHFIELD ST → CHERRY WAY                  │
  │ from_date               │ 2025-11-03                                  │
  │ to_date                 │ 2026-03-13                                  │
  │ work_description        │ Same permit as #9 — Fort Pitt Blvd segment. │
  │ work_type               │ —                                           │
  │ applicant_name          │ MICHAEL MCCORMICK                           │
  │ contractor_name         │ WODA CONSTRUCTION, INC.                     │
  │ special_instructions    │ Same as #9.                                 │
  │ weekday_hours           │ 9AM-3PM                                     │
  │ weekend_hours           │ 7AM-5PM                                     │
  └─────────────────────────┴─────────────────────────────────────────────┘

  11. COMMONWEALTH PL
  ┌────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Field              │ Value                                                                                                       │
  ├────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ closure_id         │ DOMI-OP-2025-05193-1                                                                                        │
  │ primary_street     │ COMMONWEALTH PL                                                                                             │
  │ from_street →      │ FORT DUQUESNE BLVD → LIBERTY AVE                                                                            │
  │ to_street          │                                                                                                             │
  │ from_date          │ 2025-12-15                                                                                                  │
  │ to_date            │ 2026-02-20                                                                                                  │
  │ work_description   │ NEW FIBER OPTIC CABLE INSTALLATION VIA OPEN-CUT TRENCH. COMMONWEALTH PL & LIBERTY AVE TO FORT DUQUESNE BLVD │
  │                    │ & COMMONWEALTH PL.                                                                                          │
  │ work_type          │ TELECOM                                                                                                     │
  │ applicant_name     │ MERINDA SIMPSON                                                                                             │
  │ contractor_name    │ VYTAL DIGITAL INFRASTRUCTURE CORP.                                                                          │
  │ special_instructio │ PLATE/REOPEN OUTSIDE WORK HOURS; REMOVE OBSTRUCTIONS 2 HRS AROUND SPECIAL EVENTS; CONTACT PRT 412-566-5321; │
  │ ns                 │ PPS; ROLL KALL 855-589-1126.                                                                                │
  │ weekday_hours      │ 9AM-3PM                                                                                                     │
  │ weekend_hours      │ NONE                                                                                                        │
  └────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
  
  12. S NEGLEY AVE
  ┌──────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Field                │ Value                                                                                                     │
  ├──────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ closure_id           │ DOMI-OP-2025-13621-1                                                                                      │
  │ primary_street       │ S NEGLEY AVE                                                                                              │
  │ from_street →        │ HUGUS PL → EVA ST                                                                                         │
  │ to_street            │                                                                                                           │
  │ from_date            │ 2025-11-04                                                                                                │
  │ to_date              │ 2026-03-31                                                                                                │
  │ work_description     │ WATER SERVICE LINE VERIFICATION AND LEAD SERVICE LINE REPLACEMENT ON PUBLIC SIDE AND PRIVATE SIDE ON S    │
  │                      │ NEGLEY AVE.                                                                                               │
  │ work_type            │ RESTORATION                                                                                               │
  │ applicant_name       │ KATIE MARCHESE                                                                                            │
  │ contractor_name      │ AECOM DBA PWSA                                                                                            │
  │ special_instructions │ —                                                                                                         │
  │ weekday_hours        │ 9AM-3PM                                                                                                   │
  │ weekend_hours        │ —                                                                                                         │
  └──────────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  13. BEECHWOOD BLVD
  ┌──────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Field                │ Value                                                                                                     │
  ├──────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ closure_id           │ DOMI-UOP-2025-14265-7                                                                                     │
  │ primary_street       │ BEECHWOOD BLVD                                                                                            │
  │ from_street →        │ S DALLAS AVE → BEECHWOOD BLVD RAMP                                                                        │
  │ to_street            │                                                                                                           │
  │ from_date            │ 2025-11-19                                                                                                │
  │ to_date              │ 2026-04-27                                                                                                │
  │ work_description     │ WATER SERVICE LINE VERIFICATIONS AND LEAD SERVICE LINE REPLACEMENTS THROUGHOUT SQUIRREL HILL SOUTH;       │
  │                      │ DOMI-UP-2025-12719.                                                                                       │
  │ work_type            │ —                                                                                                         │
  │ applicant_name       │ EMILY WILSON                                                                                              │
  │ contractor_name      │ INDEPENDENT ENTERPRISES, INC., AECOM DBA PWSA                                                             │
  │ special_instructions │ MAINTAIN TWO LANES OF TRAFFIC FOR COMMERCIAL ST DETOUR                                                    │
  │ weekday_hours        │ 09:00–15:00                                                                                               │
  │ weekend_hours        │ 09:00–15:00                                                                                               │
  └──────────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  14. BEECHWOOD BLVD

  ┌─────────────────────────┬───────────────────────────────────────────────┐
  │ Field                   │ Value                                         │
  ├─────────────────────────┼───────────────────────────────────────────────┤
  │ closure_id              │ DOMI-UOP-2025-14265-8                         │
  │ primary_street          │ BEECHWOOD BLVD                                │
  │ from_street → to_street │ BEECHWOOD BLVD RAMP → SHAW AVE                │
  │ from_date               │ 2025-11-19                                    │
  │ to_date                 │ 2026-04-27                                    │
  │ work_description        │ Same permit as #13 — segment 8.               │
  │ work_type               │ —                                             │
  │ applicant_name          │ EMILY WILSON                                  │
  │ contractor_name         │ INDEPENDENT ENTERPRISES, INC., AECOM DBA PWSA │
  │ special_instructions    │ Same as #13.                                  │
  │ weekday_hours           │ 09:00–15:00                                   │
  │ weekend_hours           │ 09:00–15:00                                   │
  └─────────────────────────┴───────────────────────────────────────────────┘


## Quick Reference

| Tool                  | Purpose |
|-----------------------|---------|
| `search_obstructions` | Search by street(s), keyword, or filters; paginate with `limit`/`offset`. |
| `list_active_entries`| List active obstructions only; paginate with `limit`/`offset`. |
| `obstruction_count`  | Get total record count. |
| `refresh_data`       | Reload cache from WPRDC (optional `max_records`). |

For local or self-hosted setup, see [client/README_CLIENT.md](client/README_CLIENT.md) and [server/README_SERVER.md](server/README_SERVER.md).
