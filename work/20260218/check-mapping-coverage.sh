#!/bin/bash
# Mapping Coverage Check
# Verifies that all official documentation files are mapped

set -euo pipefail

echo "=== Mapping Coverage Check ==="
echo ""

# v6 Check
echo "## Nablarch v6"
echo ""

# Count official doc files
v6_nablarch_doc=$(find .lw/nab-official/v6/nablarch-document -name "*.rst" | wc -l)
v6_dev_guide=$(find .lw/nab-official/v6/nablarch-system-development-guide -name "*.rst" 2>/dev/null | wc -l || echo 0)
v6_archetype=$(find .lw/nab-official/v6/nablarch-single-module-archetype -name "*.rst" 2>/dev/null | wc -l || echo 0)
v6_total=$((v6_nablarch_doc + v6_dev_guide + v6_archetype))

echo "Official documentation files:"
echo "  - nablarch-document: $v6_nablarch_doc files"
echo "  - nablarch-system-development-guide: $v6_dev_guide files"
echo "  - nablarch-single-module-archetype: $v6_archetype files"
echo "  - Total: $v6_total files"
echo ""

# Count mapping entries
v6_mappings=$(jq '.mappings | length' work/20260213/create-mapping-info/mapping-v6.json)
echo "Mapping entries: $v6_mappings"
echo ""

if [ "$v6_total" -eq "$v6_mappings" ]; then
    echo "✅ Coverage: Complete (all files mapped)"
else
    echo "❌ Coverage: Incomplete"
    echo "   Difference: $((v6_total - v6_mappings)) files"
    if [ "$v6_total" -gt "$v6_mappings" ]; then
        echo "   → Missing mappings (official files not in mapping)"
    else
        echo "   → Extra mappings (mapping entries for non-existent files?)"
    fi
fi
echo ""
echo "---"
echo ""

# v5 Check
echo "## Nablarch v5"
echo ""

# Count official doc files
v5_nablarch_doc=$(find .lw/nab-official/v5/nablarch-document -name "*.rst" | wc -l)
v5_archetype=$(find .lw/nab-official/v5/nablarch-single-module-archetype -name "*.rst" 2>/dev/null | wc -l || echo 0)
v5_total=$((v5_nablarch_doc + v5_archetype))

echo "Official documentation files:"
echo "  - nablarch-document: $v5_nablarch_doc files"
echo "  - nablarch-single-module-archetype: $v5_archetype files"
echo "  - Total: $v5_total files"
echo ""

# Count mapping entries
v5_mappings=$(jq '.mappings | length' work/20260213/create-mapping-info/mapping-v5.json)
echo "Mapping entries: $v5_mappings"
echo ""

if [ "$v5_total" -eq "$v5_mappings" ]; then
    echo "✅ Coverage: Complete (all files mapped)"
else
    echo "❌ Coverage: Incomplete"
    echo "   Difference: $((v5_total - v5_mappings)) files"
    if [ "$v5_total" -gt "$v5_mappings" ]; then
        echo "   → Missing mappings (official files not in mapping)"
    else
        echo "   → Extra mappings (mapping entries for non-existent files?)"
    fi
fi
echo ""
echo "---"
echo ""

# Summary
echo "## Summary"
echo ""
echo "| Version | Official Files | Mapping Entries | Status |"
echo "|---------|---------------|-----------------|--------|"

v6_status="✅ Complete"
if [ "$v6_total" -ne "$v6_mappings" ]; then
    v6_status="❌ Incomplete ($((v6_total - v6_mappings)))"
fi

v5_status="✅ Complete"
if [ "$v5_total" -ne "$v5_mappings" ]; then
    v5_status="❌ Incomplete ($((v5_total - v5_mappings)))"
fi

echo "| v6 | $v6_total | $v6_mappings | $v6_status |"
echo "| v5 | $v5_total | $v5_mappings | $v5_status |"
echo ""

# Exit with error if incomplete
if [ "$v6_total" -ne "$v6_mappings" ] || [ "$v5_total" -ne "$v5_mappings" ]; then
    echo "⚠️  Run detailed check to identify missing/extra files"
    exit 1
else
    echo "✅ All official documentation files are mapped"
    exit 0
fi
