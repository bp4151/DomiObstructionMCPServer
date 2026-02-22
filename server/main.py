"""MCP server exposing WPRDC DOMI obstruction data.

Uses the Model Context Protocol specification 2025-11-25
(https://modelcontextprotocol.io/specification/2025-11-25) via the mcp Python SDK.
Tool definitions use the FastMCP decorator pattern (see
https://modelcontextprotocol.io/docs/develop/build-server).
"""

import asyncio
import json
import logging
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from wprdc import fetch_obstructions, run_ingestion

# STDIO transport: log to stderr only so stdout is not corrupted (MCP JSON-RPC)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)

# Initialize FastMCP server (name used in tool discovery)
mcp = FastMCP("domi-obstruction-mcp")

# In-memory cache populated on startup (records, total, fields)
_cached_records: list[dict] = []
_cached_total: int = 0
_cached_fields: list[dict] = []


def _apply_filters(records: list[dict], filters: dict | None, q: str | None) -> list[dict]:
    """Filter records by exact field match and optional text search."""
    if not filters and not q:
        return records
    out = []
    search_fields = (
        "work_description",
        "primary_street",
        "from_street",
        "to_street",
        "closure_id",
        "permit_id",
        "applicant_name",
    )
    q_lower = (q or "").strip().lower()
    for r in records:
        if filters:
            if not all(r.get(k) == v for k, v in filters.items()):
                continue
        if q_lower:
            if not any(
                q_lower in str((r.get(f) or "")).lower() for f in search_fields
            ):
                continue
        out.append(r)
    return out


def _slice_cache(limit: int, offset: int, filters: dict | None, q: str | None) -> dict:
    """Serve a slice of cached data as API-shaped result."""
    filtered = _apply_filters(_cached_records, filters, q)
    total = len(filtered)
    slice_records = filtered[offset : offset + limit]
    return {
        "success": True,
        "result": {
            "records": slice_records,
            "total": total,
            "fields": _cached_fields,
            "records_format": "objects",
            "resource_id": "a9a1d93a-9d3b-4c18-bd80-82ed6f86404a",
        },
    }

@mcp.tool("search_obstructions")
async def wprdc_search_obstructions(
    limit: int = 100,
    offset: int = 0,
    q: str | None = None,
    filters: str | None = None,
) -> str:
    """Search DOMI (Department of Mobility and Infrastructure) obstruction/closure records from WPRDC.

    Returns permit/closure data with streets, dates, and geometry. Use limit/offset for pagination.

    Args:
        limit: Max records to return (default 100).
        offset: Number of records to skip for pagination.
        q: Optional full-text search query.
        filters: Optional JSON object of field filters, e.g. {"primary_street": "SECOND AVE"}.
    """
    filters_dict: dict | None = None
    if filters:
        try:
            filters_dict = json.loads(filters)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid filters JSON: {e}") from e

    if _cached_records:
        data = _slice_cache(limit, offset, filters_dict, q)
    else:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None,
            lambda: fetch_obstructions(
                limit=limit, offset=offset, filters=filters_dict, q=q
            ),
        )
    return json.dumps(data, indent=2)


@mcp.tool("list_active_entries")
async def list_active_entries(limit: int = 100, offset: int = 0) -> str:
    """List all active DOMI obstruction/closure entries from the cached dataset.

    Returns permit/closure records with streets, dates, and geometry. Use limit/offset for pagination.

    Args:
        limit: Max records to return (default 100).
        offset: Number of records to skip for pagination.
    """
    filters = {"active": True}  
    if _cached_records:
        data = _slice_cache(limit, offset, filters, None)
    else:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None,
            lambda: fetch_obstructions(limit=limit, offset=offset, filters=filters),
        )
    return json.dumps(data, indent=2)


@mcp.tool("obstruction_count")
async def wprdc_obstruction_count() -> str:
    """Return total number of DOMI obstruction records in the WPRDC datastore."""
    if _cached_records:
        total = _cached_total
    else:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None,
            lambda: fetch_obstructions(limit=0, offset=0),
        )
        total = data.get("result", {}).get("total", 0)
    return json.dumps({"total": total}, indent=2)


@mcp.tool("refresh_data")
async def refresh_data(max_records: int | None = None) -> str:
    """Refresh cached obstruction data from the WPRDC source by running ingestion.

    Fetches the latest data from WPRDC and updates the in-memory cache used by
    search_obstructions, list_active_entries, and obstruction_count.

    Args:
        max_records: Optional cap on how many records to ingest. If omitted, uses
            WPRDC_INGEST_MAX_RECORDS from environment, or ingests all records.
    """
    global _cached_records, _cached_total, _cached_fields

    ingest_limit = max_records
    if ingest_limit is None:
        env_max = os.environ.get("WPRDC_INGEST_MAX_RECORDS")
        ingest_limit = int(env_max) if env_max not in (None, "") else None

    logger.info("Refresh requested (max_records=%s)", ingest_limit or "all")
    loop = asyncio.get_event_loop()
    records, total, fields = await loop.run_in_executor(
        None,
        lambda: run_ingestion(max_records=ingest_limit),
    )
    _cached_records = records
    _cached_total = total
    _cached_fields = fields
    logger.info("Cache refreshed: %s records", len(_cached_records))

    return json.dumps(
        {
            "success": True,
            "cached_records": len(_cached_records),
            "total_available": _cached_total,
        },
        indent=2,
    )


def main(transport: str, host: str, port: int) -> int:
    global _cached_records, _cached_total, _cached_fields

    logger.info("Starting DOMI Obstruction MCP server (WPRDC)")

    max_records = os.environ.get("WPRDC_INGEST_MAX_RECORDS")
    ingest_limit = int(max_records) if max_records not in (None, "") else None
    logger.info("Running ingestion on startup (max_records=%s) ...", ingest_limit or "all")
    _cached_records, _cached_total, _cached_fields = run_ingestion(max_records=ingest_limit)
    logger.info("Cache ready: %s records", len(_cached_records))

    if transport == "streamable-http":
        logger.info("Starting streaming HTTP transport on %s:%s", host, port)
        mcp.settings.host = host
        mcp.settings.port = port
        # Accept any Host header when bound to 0.0.0.0 (e.g. behind App Runner, ALB, or remote clients).
        # Otherwise DNS rebinding protection would reject requests with the public hostname.
        if host in ("0.0.0.0", "::"):
            mcp.settings.transport_security = TransportSecuritySettings(
                enable_dns_rebinding_protection=False,
            )
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    load_dotenv()
    transport = os.environ.get("MCP_TRANSPORT", "stdio")  # "stdio" | "streamable-http"
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8000"))

    raise SystemExit(main(transport=transport, host=host, port=port))
