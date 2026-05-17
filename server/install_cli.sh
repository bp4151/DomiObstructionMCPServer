#!/usr/bin/env bash
# Installation script for DOMI Obstruction CLI

set -e

echo "🚧 DOMI Obstruction CLI Installer"
echo "=================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    echo "   Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_CMD="python3"
PIP_CMD="pip3"

echo "✅ Python found: $($PYTHON_CMD --version)"
echo ""

# Check if UV is available (recommended)
if command -v uv &> /dev/null; then
    echo "✅ UV found: $(uv --version)"
    USE_UV=true
else
    echo "ℹ️  UV not found - will use pip instead"
    echo "   (Install UV for faster dependency management: https://github.com/astral-sh/uv)"
    USE_UV=false
fi

echo ""
echo "Installing dependencies..."
echo ""

if [ "$USE_UV" = true ]; then
    echo "Using UV to install dependencies..."
    uv pip install fastmcp cyclopts rich mcp
else
    echo "Using pip to install dependencies..."
    $PIP_CMD install fastmcp cyclopts rich mcp
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Quick start:"
echo "  python3 cli.py list-tools"
echo "  python3 cli.py call-tool search_obstructions --q \"Fifth Avenue\""
echo "  python3 cli.py call-tool list_active_entries"
echo ""
echo "For more examples, see CLI_README.md or CLI_USAGE.md"
