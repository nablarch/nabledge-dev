#!/bin/bash
# Find Missing Files in Mapping
# Identifies official documentation files not included in mapping

set -euo pipefail

echo "=== Finding Missing Files ==="
echo ""

# Function to check version
check_version() {
    local version=$1
    local mapping_file=$2
    local doc_paths=$3

    echo "## Nablarch $version"
    echo ""

    # Extract all source_file paths from mapping (add .lw/ prefix to match actual files)
    jq -r '.mappings[].source_file' "$mapping_file" | sed 's|^|.lw/|' | sort > /tmp/mapped_files_$version.txt

    # Find all .rst files in official docs
    find $doc_paths -name "*.rst" | sed 's|^\./||' | sort > /tmp/official_files_$version.txt

    # Find missing files (in official but not in mapping)
    comm -23 /tmp/official_files_$version.txt /tmp/mapped_files_$version.txt > /tmp/missing_files_$version.txt

    # Find extra files (in mapping but not in official)
    comm -13 /tmp/official_files_$version.txt /tmp/mapped_files_$version.txt > /tmp/extra_files_$version.txt

    missing_count=$(wc -l < /tmp/missing_files_$version.txt)
    extra_count=$(wc -l < /tmp/extra_files_$version.txt)

    echo "Missing files (in official docs but not mapped): $missing_count"
    if [ "$missing_count" -gt 0 ]; then
        echo ""
        echo "First 20 missing files:"
        head -20 /tmp/missing_files_$version.txt | sed 's/^/  - /'
        if [ "$missing_count" -gt 20 ]; then
            echo "  ... and $((missing_count - 20)) more"
        fi
        echo ""
        echo "Full list: /tmp/missing_files_$version.txt"
    fi
    echo ""

    echo "Extra files (mapped but not in official docs): $extra_count"
    if [ "$extra_count" -gt 0 ]; then
        echo ""
        echo "Extra files:"
        cat /tmp/extra_files_$version.txt | sed 's/^/  - /'
        echo ""
        echo "Full list: /tmp/extra_files_$version.txt"
    fi
    echo ""
    echo "---"
    echo ""
}

# Check v6
check_version "v6" \
    "work/20260213/create-mapping-info/mapping-v6.json" \
    ".lw/nab-official/v6/nablarch-document .lw/nab-official/v6/nablarch-system-development-guide .lw/nab-official/v6/nablarch-single-module-archetype"

# Check v5
check_version "v5" \
    "work/20260213/create-mapping-info/mapping-v5.json" \
    ".lw/nab-official/v5/nablarch-document .lw/nab-official/v5/nablarch-single-module-archetype"

echo "=== Analysis ==="
echo ""
echo "To analyze missing files by directory:"
echo "  cat /tmp/missing_files_v6.txt | cut -d'/' -f1-5 | sort | uniq -c"
echo ""
echo "To see missing file patterns:"
echo "  cat /tmp/missing_files_v6.txt | grep -E '(index|conf|_static|_templates)'"
