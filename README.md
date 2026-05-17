# DomiObstructionMCPServer

This repository contains the **DOMI Obstruction MCP Server**, an [MCP](https://modelcontextprotocol.io/) server that exposes WPRDC DOMI obstruction/closure data.

## 📂 Project Layout

| Path | Description |
|------|-------------|
| **[`docs/`](docs/)** | **⭐ Documentation (Start here)** |
| **[`server/`](server/)** | MCP server implementation (entrypoint, WPRDC ingestion, Docker, docs) |
| **[`client/`](client/)** | Instructions for connecting Cursor (or other clients) to the MCP server |
| **[`.cursor/skills/`](.cursor/skills/)** | Cursor Skills for natural language querying |

## 🚀 Quick Start

- **Documentation Index:** See [**`docs/DOCUMENTATION_INDEX.md`**](docs/DOCUMENTATION_INDEX.md) for a complete guide.
- **Quick Reference:** See [**`docs/QUICK_REFERENCE.md`**](docs/QUICK_REFERENCE.md) for a one-page cheat sheet.
- **Build and run the MCP server:** See [**`server/README_SERVER.md`**](server/README_SERVER.md) for local run, Docker, and tool call reference.
- **Connect Cursor to the server:** See [**`client/README_CLIENT.md`**](client/README_CLIENT.md) for step-by-step Cursor MCP setup.

## 💬 Natural Language Queries

If you are using Cursor, you can ask questions in natural language:
- "What streets in Pittsburgh are closed right now?"
- "Show me construction on Fifth Avenue"
- "Find all water main work by PWSA"
- "Check if my route is affected by closures [attach route.gpx]"

The AI will automatically use the MCP tools via the installed [Cursor Skill](.cursor/skills/domi-obstruction-mcp/SKILL.md).

## ⌨️ Command Line Interface

You can also use the CLI for direct queries and scripting:
```bash
cd server
bash install_cli.sh
python cli.py call-tool list_active_entries
```
See [**`server/CLI_README.md`**](server/CLI_README.md) for more details.
