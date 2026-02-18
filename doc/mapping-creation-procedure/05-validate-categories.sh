#!/bin/bash
# Phase 5 Validation: Validate Categories

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR/output"

echo "=== Phase 5 Validation: Categories ==="
echo ""

# Check all categories are defined
echo "Checking category definitions..."
v6_cats=$(jq -r '.mappings[].categories[]?' "$WORK_DIR/mapping-v6.json" 2>/dev/null | sort -u)
v6_defined=$(jq -r '.categories[].id' doc/mapping-creation-procedure/categories-v6.json | sort -u)

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

# Check processing patterns are mutually exclusive
echo "Checking processing pattern exclusivity..."
processing_patterns="batch-nablarch|batch-jsr352|rest|http-messaging|web|messaging-mom|messaging-db"

multi_v6=$(jq -r ".mappings[] | select([.categories[] | select(test(\"^($processing_patterns)\$\"))] | length > 1) | {id, categories}" "$WORK_DIR/mapping-v6.json" 2>/dev/null)
if [ -n "$multi_v6" ]; then
    echo "❌ v6 entries with multiple processing patterns:"
    echo "$multi_v6" | jq -c '.' | head -5
    multi_v6_count=$(echo "$multi_v6" | jq -s 'length')
    [ "$multi_v6_count" -gt 5 ] && echo "  ... and $((multi_v6_count - 5)) more"
    unknown_v6=$((unknown_v6 + multi_v6_count))
else
    echo "✅ All v6 entries have mutually exclusive processing patterns"
fi

multi_v5=$(jq -r ".mappings[] | select([.categories[] | select(test(\"^($processing_patterns)\$\"))] | length > 1) | {id, categories}" "$WORK_DIR/mapping-v5.json" 2>/dev/null)
if [ -n "$multi_v5" ]; then
    echo "❌ v5 entries with multiple processing patterns"
    multi_v5_count=$(echo "$multi_v5" | jq -s 'length')
    unknown_v6=$((unknown_v6 + multi_v5_count))
else
    echo "✅ All v5 entries have mutually exclusive processing patterns"
fi
echo ""

if [ $unknown_v6 -eq 0 ] && [ "$empty_v6" -eq 0 ] && [ "$empty_v5" -eq 0 ]; then
    echo "=== Validation Passed ==="
    exit 0
else
    echo "=== Validation Failed ==="
    exit 1
fi
