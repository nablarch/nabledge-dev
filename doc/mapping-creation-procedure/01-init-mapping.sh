#!/bin/bash
# Phase 1: Initialize Mapping Files
# Creates empty JSON structure for mapping files

set -euo pipefail

# Output directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR/output"

echo "=== Phase 1: Initialize Mapping Files ==="
echo ""
echo "Creating directory: $WORK_DIR"
mkdir -p "$WORK_DIR"
echo ""

# Create v6 mapping file
echo "Creating mapping-v6.json..."
cat > "$WORK_DIR/mapping-v6.json" <<'EOF'
{
  "schema_version": "1.0",
  "version": "6",
  "created_at": "",
  "mappings": []
}
EOF

# Update created_at
TIMESTAMP=$(date -Iseconds)
jq --arg ts "$TIMESTAMP" '.created_at = $ts' "$WORK_DIR/mapping-v6.json" > "$WORK_DIR/mapping-v6.json.tmp"
mv "$WORK_DIR/mapping-v6.json.tmp" "$WORK_DIR/mapping-v6.json"

echo "✅ Created: $WORK_DIR/mapping-v6.json"
echo ""

# Create v5 mapping file
echo "Creating mapping-v5.json..."
cat > "$WORK_DIR/mapping-v5.json" <<'EOF'
{
  "schema_version": "1.0",
  "version": "5",
  "created_at": "",
  "mappings": []
}
EOF

jq --arg ts "$TIMESTAMP" '.created_at = $ts' "$WORK_DIR/mapping-v5.json" > "$WORK_DIR/mapping-v5.json.tmp"
mv "$WORK_DIR/mapping-v5.json.tmp" "$WORK_DIR/mapping-v5.json"

echo "✅ Created: $WORK_DIR/mapping-v5.json"
echo ""

# Validate
echo "Validating..."
if jq empty "$WORK_DIR/mapping-v6.json" 2>/dev/null && jq empty "$WORK_DIR/mapping-v5.json" 2>/dev/null; then
    echo "✅ JSON files are valid"
else
    echo "❌ JSON validation failed"
    exit 1
fi

# Check schema
v6_version=$(jq -r '.version' "$WORK_DIR/mapping-v6.json")
v5_version=$(jq -r '.version' "$WORK_DIR/mapping-v5.json")

if [ "$v6_version" = "6" ] && [ "$v5_version" = "5" ]; then
    echo "✅ Version fields are correct"
else
    echo "❌ Version fields are incorrect"
    exit 1
fi

echo ""
echo "=== Phase 1 Complete ==="
echo ""
echo "Output files:"
echo "  - $WORK_DIR/mapping-v6.json"
echo "  - $WORK_DIR/mapping-v5.json"
echo ""
echo "Next step: Run doc/scripts/02-collect-files.sh"
