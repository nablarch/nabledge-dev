#!/bin/bash
# Phase 7: Final Validation
# Comprehensive validation before mapping completion

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR"
TMP_DIR="$WORK_DIR/tmp"

echo "=== Phase 7: Final Validation ==="
echo ""

# Create tmp directory if it doesn't exist
mkdir -p "$TMP_DIR"

ERRORS=0

# 1. Completeness
echo "## 1. Completeness Check"
echo ""

v6_count=$(jq '.mappings | length' "$WORK_DIR/mapping-v6.json")
v5_count=$(jq '.mappings | length' "$WORK_DIR/mapping-v5.json")

echo "v6: $v6_count mappings"
echo "v5: $v5_count mappings"
echo ""

# Check all fields populated
empty_cats_v6=$(jq '[.mappings[] | select(.categories == [])] | length' "$WORK_DIR/mapping-v6.json")
empty_targets_v6=$(jq '[.mappings[] | select(.target_files == [])] | length' "$WORK_DIR/mapping-v6.json")

if [ "$empty_cats_v6" -gt 0 ]; then
    echo "❌ $empty_cats_v6 v6 entries missing categories"
    ((ERRORS++))
else
    echo "✅ All v6 entries have categories"
fi

if [ "$empty_targets_v6" -gt 0 ]; then
    echo "⚠️  $empty_targets_v6 v6 entries missing target_files (may be intentional)"
else
    echo "✅ All v6 entries have target_files"
fi
echo ""

# 2. Consistency
echo "## 2. Consistency Check"
echo ""

# Check for duplicate IDs
dup_ids_v6=$(jq -r '.mappings[].id' "$WORK_DIR/mapping-v6.json" | sort | uniq -d | wc -l)
if [ "$dup_ids_v6" -gt 0 ]; then
    echo "❌ $dup_ids_v6 duplicate IDs in v6"
    ((ERRORS++))
else
    echo "✅ No duplicate IDs in v6"
fi

# Check for duplicate source files
dup_sources_v6=$(jq -r '.mappings[].source_file' "$WORK_DIR/mapping-v6.json" | sort | uniq -d | wc -l)
if [ "$dup_sources_v6" -gt 0 ]; then
    echo "❌ $dup_sources_v6 duplicate source files in v6"
    ((ERRORS++))
else
    echo "✅ No duplicate source files in v6"
fi
echo ""

# 3. Generate Summary
echo "## 3. Summary"
echo ""

cat > "$TMP_DIR/validation-report.md" <<EOF
# Mapping Validation Report

**Date**: $(date -Iseconds)

## Summary

| Version | Mappings | Errors |
|---------|----------|--------|
| v6 | $v6_count | $ERRORS |
| v5 | $v5_count | - |

## Details

### Completeness
- v6 entries without categories: $empty_cats_v6
- v6 entries without target_files: $empty_targets_v6

### Consistency
- v6 duplicate IDs: $dup_ids_v6
- v6 duplicate source files: $dup_sources_v6

## Status

EOF

if [ $ERRORS -eq 0 ]; then
    echo "Status: ✅ PASSED" >> "$TMP_DIR/validation-report.md"
    echo "✅ All validations passed"
    echo ""
    echo "Report: $TMP_DIR/validation-report.md"
    exit 0
else
    echo "Status: ❌ FAILED ($ERRORS errors)" >> "$TMP_DIR/validation-report.md"
    echo "❌ Validation failed with $ERRORS errors"
    echo ""
    echo "Report: $TMP_DIR/validation-report.md"
    exit 1
fi
