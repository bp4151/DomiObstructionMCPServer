# DomiObstructionMCPServer

This repository contains the **DOMI Obstruction MCP Server**, an [MCP](https://modelcontextprotocol.io/) server that exposes WPRDC DOMI obstruction/closure data.

## Project layout

| Path | Description |
|------|-------------|
| **`server/`** | MCP server implementation (entrypoint, WPRDC ingestion, Docker, docs) |
| **`client/`** | Instructions for connecting Cursor (or other clients) to the MCP server |

## Quick start

- **Build and run the MCP server:** see [**server/README_SERVER.md**](server/README_SERVER.md) for local run, Docker, and tool call reference.
- **Connect Cursor to the server:** see [**client/README_CLIENT.md**](client/README_CLIENT.md) for step-by-step Cursor MCP setup.
