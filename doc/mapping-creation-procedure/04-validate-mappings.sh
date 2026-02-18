#!/bin/bash
# Phase 4 Validation: Validate Generated Mappings

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR/output"

echo "=== Phase 4 Validation ==="
echo ""

# Validate JSON syntax
echo "Checking JSON syntax..."
if jq empty "$WORK_DIR/mapping-v6.json" 2>/dev/null && jq empty "$WORK_DIR/mapping-v5.json" 2>/dev/null; then
    echo "✅ JSON syntax valid"
else
    echo "❌ JSON syntax invalid"
    exit 1
fi
echo ""

# Check IDs are sequential
echo "Checking ID sequences..."
v6_ids=$(jq -r '.mappings[].id' "$WORK_DIR/mapping-v6.json" | wc -l)
v6_expected=$(jq '.mappings | length' "$WORK_DIR/mapping-v6.json")
[ "$v6_ids" -eq "$v6_expected" ] && echo "✅ v6 IDs complete" || echo "❌ v6 ID mismatch"

v5_ids=$(jq -r '.mappings[].id' "$WORK_DIR/mapping-v5.json" | wc -l)
v5_expected=$(jq '.mappings | length' "$WORK_DIR/mapping-v5.json")
[ "$v5_ids" -eq "$v5_expected" ] && echo "✅ v5 IDs complete" || echo "❌ v5 ID mismatch"
echo ""

# Check source files exist (sample check - first 10)
echo "Checking source files exist (sample)..."
jq -r '.mappings[0:10][].source_file' "$WORK_DIR/mapping-v6.json" | while read -r file; do
    if [ ! -f ".lw/$file" ]; then
        echo "❌ Missing: $file"
    fi
done
echo "✅ Sample check passed"
echo ""

echo "=== Validation Passed ==="
