"""Ingest DOMI obstruction data from WPRDC (Western Pennsylvania Regional Data Center)."""

import json
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://data.wprdc.org"
RESOURCE_ID = "a9a1d93a-9d3b-4c18-bd80-82ed6f86404a"
DATASTORE_SEARCH_PATH = "api/3/action/datastore_search"


def fetch_obstructions(
    *,
    limit: int = 100,
    offset: int = 0,
    filters: dict[str, Any] | None = None,
    q: str | None = None,
) -> dict[str, Any]:
    """
    Fetch DOMI obstruction/closure records from WPRDC datastore.

    Args:
        limit: Max number of records to return (default 100).
        offset: Number of records to skip for pagination.
        filters: Optional field filters, e.g. {"primary_street": "SECOND AVE"}.
        q: Optional full-text search query.

    Returns:
        API response with "result" containing "records", "total", "fields", "_links".
    """
    url = f"{BASE_URL}/{DATASTORE_SEARCH_PATH}"
    params: dict[str, Any] = {
        "resource_id": RESOURCE_ID,
        "limit": limit,
        "offset": offset,
    }
    if q:
        params["q"] = q
    if filters:
        params["filters"] = json.dumps(filters)

    with httpx.Client(timeout=30.0) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    if not data.get("success"):
        raise RuntimeError(f"WPRDC API error: {data}")

    result = data["result"]
    logger.info(
        "Fetched %s records (offset=%s, total=%s)",
        len(result.get("records", [])),
        offset,
        result.get("total"),
    )
    return data


def fetch_all_obstructions(
    *,
    max_records: int | None = None,
    page_size: int = 1000,
    filters: dict[str, Any] | None = None,
    q: str | None = None,
) -> list[dict[str, Any]]:
    """
    Fetch all (or up to max_records) obstruction records by paginating the API.

    Args:
        max_records: If set, stop after this many records; otherwise fetch all.
        page_size: Records per API request.
        filters: Optional field filters.
        q: Optional full-text search query.

    Returns:
        List of record dicts.
    """
    all_records: list[dict[str, Any]] = []
    offset = 0

    while True:
        data = fetch_obstructions(
            limit=page_size,
            offset=offset,
            filters=filters,
            q=q,
        )
        result = data["result"]
        records = result.get("records", [])
        if not records:
            break
        all_records.extend(records)
        total = result.get("total", 0)
        offset += len(records)
        if offset >= total or (max_records is not None and len(all_records) >= max_records):
            break
        if max_records is not None and len(all_records) >= max_records:
            all_records = all_records[:max_records]
            break

    return all_records


def run_ingestion(
    max_records: int | None = None,
    page_size: int = 1000,
) -> tuple[list[dict[str, Any]], int, list[dict[str, Any]]]:
    """
    Ingest obstruction data from WPRDC for caching. Fetches total/fields then all records.

    Returns:
        (records, total, fields) for in-memory cache.
    """
    meta = fetch_obstructions(limit=0, offset=0)
    result = meta["result"]
    total = result.get("total", 0)
    fields = result.get("fields", [])
    records = fetch_all_obstructions(max_records=max_records, page_size=page_size)
    logger.info("Ingestion complete: %s records cached (total available: %s)", len(records), total)
    return records, total, fields
