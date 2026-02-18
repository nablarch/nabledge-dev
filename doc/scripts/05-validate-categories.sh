#!/bin/bash
# Phase 5 Validation: Validate Categories

set -euo pipefail

DATE=$(date +%Y%m%d)
WORK_DIR="work/$DATE/mapping"

echo "=== Phase 5 Validation: Categories ==="
echo ""

# Check all categories are defined
echo "Checking category definitions..."
v6_cats=$(jq -r '.mappings[].categories[]?' "$WORK_DIR/mapping-v6.json" 2>/dev/null | sort -u)
v6_defined=$(jq -r '.categories[].id' work/20260213/create-mapping-info/categories-v6.json | sort -u)

unknown_v6=0
while read -r cat; do
    if ! echo "$v6_defined" | grep -q "^${cat}$"; then
        echo "❌ Unknown category in v6: $cat"
        ((unknown_v6++))
    fi
done <<< "$v6_cats"

[ $unknown_v6 -eq 0 ] && echo "✅ All v6 categories are defined" || echo "❌ $unknown_v6 unknown v6 categories"
echo ""

# Check all entries have at least one category
echo "Checking all entries have categories..."
empty_v6=$(jq '[.mappings[] | select(.categories == [])] | length' "$WORK_DIR/mapping-v6.json")
[ "$empty_v6" -eq 0 ] && echo "✅ All v6 entries have categories" || echo "❌ $empty_v6 v6 entries have no categories"

empty_v5=$(jq '[.mappings[] | select(.categories == [])] | length' "$WORK_DIR/mapping-v5.json")
[ "$empty_v5" -eq 0 ] && echo "✅ All v5 entries have categories" || echo "❌ $empty_v5 v5 entries have no categories"
echo ""

if [ $unknown_v6 -eq 0 ] && [ "$empty_v6" -eq 0 ] && [ "$empty_v5" -eq 0 ]; then
    echo "=== Validation Passed ==="
    exit 0
else
    echo "=== Validation Failed ==="
    exit 1
fi
