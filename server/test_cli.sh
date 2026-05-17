#!/usr/bin/env bash
# Test script for DOMI Obstruction CLI

set -e

echo "🧪 Testing DOMI Obstruction CLI"
echo "================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Test 1: List tools
echo "Test 1: List tools..."
python3 cli.py list-tools > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ list-tools works"
else
    echo "❌ list-tools failed"
    exit 1
fi

# Test 2: Get count
echo "Test 2: Get obstruction count..."
OUTPUT=$(python3 cli.py call-tool obstruction_count 2>&1)
if echo "$OUTPUT" | grep -q "total"; then
    COUNT=$(echo "$OUTPUT" | grep -o '"total": [0-9]*' | grep -o '[0-9]*')
    echo "✅ obstruction_count works (found $COUNT records)"
else
    echo "❌ obstruction_count failed"
    echo "$OUTPUT"
    exit 1
fi

# Test 3: List active entries
echo "Test 3: List active entries..."
OUTPUT=$(python3 cli.py call-tool list_active_entries --limit 10 2>&1)
if echo "$OUTPUT" | grep -q "success"; then
    echo "✅ list_active_entries works"
else
    echo "❌ list_active_entries failed"
    echo "$OUTPUT"
    exit 1
fi

# Test 4: Search
echo "Test 4: Search obstructions..."
OUTPUT=$(python3 cli.py call-tool search_obstructions --q "Avenue" --limit 5 2>&1)
if echo "$OUTPUT" | grep -q "records"; then
    echo "✅ search_obstructions works"
else
    echo "❌ search_obstructions failed"
    echo "$OUTPUT"
    exit 1
fi

echo ""
echo "🎉 All tests passed!"
echo ""
echo "Quick start:"
echo "  python3 cli.py list-tools"
echo "  python3 cli.py call-tool search_obstructions --q \"Fifth Avenue\""
echo "  python3 cli.py call-tool list_active_entries"
echo ""
echo "For more examples, see:"
echo "  - CLI_README.md (quick start)"
echo "  - CLI_USAGE.md (comprehensive guide)"
echo "  - ../QUICK_REFERENCE.md (cheat sheet)"
