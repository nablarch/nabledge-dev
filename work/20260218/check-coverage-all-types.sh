#!/bin/bash
# Mapping Coverage Check - All File Types
# Verifies mapping coverage for .rst, .md, and .xml files

set -euo pipefail

echo "=== Mapping Coverage Check (All File Types) ==="
echo ""

check_version() {
    local version=$1
    local mapping_file=$2
    shift 2
    local doc_paths="$@"

    echo "## Nablarch $version"
    echo ""

    # Count by file type in official docs
    rst_count=$(find $doc_paths -name "*.rst" 2>/dev/null | wc -l || echo 0)
    md_count=$(find $doc_paths -name "*.md" 2>/dev/null | wc -l || echo 0)
    xml_count=$(find $doc_paths -name "*.xml" 2>/dev/null | wc -l || echo 0)
    total_count=$((rst_count + md_count + xml_count))

    echo "Official documentation files:"
    echo "  - .rst files: $rst_count"
    echo "  - .md files: $md_count"
    echo "  - .xml files: $xml_count"
    echo "  - Total: $total_count"
    echo ""

    # Count by file type in mapping
    mapping_rst=$(jq -r '.mappings[].source_file' "$mapping_file" | grep '\.rst$' | wc -l)
    mapping_md=$(jq -r '.mappings[].source_file' "$mapping_file" | grep '\.md$' | wc -l)
    mapping_xml=$(jq -r '.mappings[].source_file' "$mapping_file" | grep '\.xml$' | wc -l)
    mapping_total=$(jq '.mappings | length' "$mapping_file")

    echo "Mapping entries:"
    echo "  - .rst: $mapping_rst"
    echo "  - .md: $mapping_md"
    echo "  - .xml: $mapping_xml"
    echo "  - Total: $mapping_total"
    echo ""

    # Comparison
    if [ "$total_count" -eq "$mapping_total" ]; then
        echo "✅ Coverage: Complete"
    else
        echo "❌ Coverage: Incomplete"
        echo "   Difference: $((total_count - mapping_total)) files"
    fi
    echo ""

    # Detail by type
    echo "Coverage by file type:"
    [ "$rst_count" -eq "$mapping_rst" ] && rst_status="✅" || rst_status="❌ ($((rst_count - mapping_rst)))"
    [ "$md_count" -eq "$mapping_md" ] && md_status="✅" || md_status="❌ ($((md_count - mapping_md)))"
    [ "$xml_count" -eq "$mapping_xml" ] && xml_status="✅" || xml_status="❌ ($((xml_count - mapping_xml)))"

    echo "  - .rst: $rst_status"
    echo "  - .md: $md_status"
    echo "  - .xml: $xml_status"
    echo ""
    echo "---"
    echo ""
}

# v6
check_version "v6" \
    "work/20260213/create-mapping-info/mapping-v6.json" \
    ".lw/nab-official/v6/nablarch-document/en" \
    ".lw/nab-official/v6/nablarch-system-development-guide" \
    ".lw/nab-official/v6/nablarch-single-module-archetype"

# v5
check_version "v5" \
    "work/20260213/create-mapping-info/mapping-v5.json" \
    ".lw/nab-official/v5/nablarch-document/en" \
    ".lw/nab-official/v5/nablarch-single-module-archetype"

echo "## Notes"
echo ""
echo "- Only English (/en/) documentation is mapped (Japanese /ja/ excluded by design)"
echo "- Mapping includes .rst (framework docs), .md (dev guide), .xml (archetype configs)"
echo "- Some files may be intentionally excluded (e.g., index files, build configs)"
