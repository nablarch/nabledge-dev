#!/bin/bash
# Phase 5.5: Apply Scope Filtering
# Removes out-of-scope entries based on category and path patterns

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR"
TMP_DIR="$WORK_DIR/tmp"
MAPPING_V6="$WORK_DIR/mapping-v6.json"
MAPPING_V5="$WORK_DIR/mapping-v5.json"

echo "=== Phase 5.5: Apply Scope Filtering ==="
echo ""

if [ ! -f "$MAPPING_V6" ]; then
    echo "❌ Error: $MAPPING_V6 not found. Run previous phases first."
    exit 1
fi

mkdir -p "$TMP_DIR"

# Create backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp "$MAPPING_V6" "$TMP_DIR/mapping-v6-backup-before-scope-filter-$TIMESTAMP.json"
echo "✅ Created backup: $TMP_DIR/mapping-v6-backup-before-scope-filter-$TIMESTAMP.json"
echo ""

# Count before filtering
BEFORE_COUNT=$(jq '.mappings | length' "$MAPPING_V6")
echo "Entries before filtering: $BEFORE_COUNT"
echo ""

# Apply filters
echo "Applying scope filters..."
echo ""

# Filter 1: Remove archetype-related entries
echo "Filter 1: Removing archetype-related entries..."
ARCHETYPE_COUNT=$(jq '[.mappings[] | select(.categories | contains(["archetype"]) or contains(["check-published-api"]))] | length' "$MAPPING_V6")
echo "  - Found $ARCHETYPE_COUNT archetype entries"

jq '.mappings |= map(select(.categories | contains(["archetype"]) or contains(["check-published-api"]) | not))' "$MAPPING_V6" > "$TMP_DIR/mapping-v6-temp.json"
mv "$TMP_DIR/mapping-v6-temp.json" "$MAPPING_V6"

# Filter 2: Remove Sample_Project entries
echo "Filter 2: Removing Sample_Project entries..."
SAMPLE_COUNT=$(jq '[.mappings[] | select(.source_file | contains("Sample_Project"))] | length' "$MAPPING_V6")
echo "  - Found $SAMPLE_COUNT Sample_Project entries"

jq '.mappings |= map(select(.source_file | contains("Sample_Project") | not))' "$MAPPING_V6" > "$TMP_DIR/mapping-v6-temp.json"
mv "$TMP_DIR/mapping-v6-temp.json" "$MAPPING_V6"

# Filter 3: Remove textlint test file
echo "Filter 3: Removing textlint test file..."
TEXTLINT_COUNT=$(jq '[.mappings[] | select(.source_file | contains(".textlint/test/"))] | length' "$MAPPING_V6")
echo "  - Found $TEXTLINT_COUNT textlint test entries"

jq '.mappings |= map(select(.source_file | contains(".textlint/test/") | not))' "$MAPPING_V6" > "$TMP_DIR/mapping-v6-temp.json"
mv "$TMP_DIR/mapping-v6-temp.json" "$MAPPING_V6"

# Filter 4: Remove license file
echo "Filter 4: Removing license file..."
LICENSE_COUNT=$(jq '[.mappings[] | select(.source_file | endswith("/license.rst"))] | length' "$MAPPING_V6")
echo "  - Found $LICENSE_COUNT license entries"

jq '.mappings |= map(select(.source_file | endswith("/license.rst") | not))' "$MAPPING_V6" > "$TMP_DIR/mapping-v6-temp.json"
mv "$TMP_DIR/mapping-v6-temp.json" "$MAPPING_V6"

echo ""

# Count after filtering
AFTER_COUNT=$(jq '.mappings | length' "$MAPPING_V6")
REMOVED_COUNT=$((BEFORE_COUNT - AFTER_COUNT))

echo "=== Filtering Complete ==="
echo ""
echo "Before: $BEFORE_COUNT entries"
echo "After:  $AFTER_COUNT entries"
echo "Removed: $REMOVED_COUNT entries"
echo ""

# Generate filtering report
cat > "$TMP_DIR/scope-filtering-report.md" <<EOF
# Scope Filtering Report

**Date**: $(date -Iseconds)

## Summary

- **Before filtering**: $BEFORE_COUNT entries
- **After filtering**: $AFTER_COUNT entries
- **Removed**: $REMOVED_COUNT entries

## Filters Applied

### Filter 1: Archetype-related entries
- **Pattern**: Categories contain "archetype" or "check-published-api"
- **Removed**: $ARCHETYPE_COUNT entries
- **Rationale**: Archetype content can be analyzed statically

### Filter 2: Sample_Project entries
- **Pattern**: Source file path contains "Sample_Project"
- **Removed**: $SAMPLE_COUNT entries
- **Rationale**: Project-specific implementation examples (proman/climan)

### Filter 3: Textlint test file
- **Pattern**: Source file path contains ".textlint/test/"
- **Removed**: $TEXTLINT_COUNT entries
- **Rationale**: Documentation tooling test file, not framework knowledge

### Filter 4: License file
- **Pattern**: Source file path ends with "/license.rst"
- **Removed**: $LICENSE_COUNT entries
- **Rationale**: Legal information only, not technical knowledge/know-how

## Scope Definition

**Included**:
- ✅ nablarch-document (complete framework reference)
- ✅ nablarch-system-development-guide (patterns and anti-patterns)

**Excluded**:
- ❌ nablarch-single-module-archetype (static analysis available)
- ❌ Sample_Project (project-specific patterns)
- ❌ Documentation tooling test files
- ❌ Non-technical files (license)

## Backup Location

Backup created at: \`$TMP_DIR/mapping-v6-backup-before-scope-filter-$TIMESTAMP.json\`

To restore:
\`\`\`bash
cp $TMP_DIR/mapping-v6-backup-before-scope-filter-$TIMESTAMP.json $MAPPING_V6
\`\`\`
EOF

echo "✅ Created: $TMP_DIR/scope-filtering-report.md"
echo ""
echo "Backup location: $TMP_DIR/mapping-v6-backup-before-scope-filter-$TIMESTAMP.json"
echo ""
echo "Next step: Run doc/mapping-creation-procedure/06-define-targets.sh"
