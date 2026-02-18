#!/bin/bash
# Phase 6 Validation: Validate Target Files

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR/output"

echo "=== Phase 6 Validation: Target Files ==="
echo ""

ERRORS=0

# Check all entries have target files
echo "## 1. Completeness Check"
echo ""

check_completeness() {
    local mapping_file=$1
    local version=$2

    local empty_count=$(jq '[.mappings[] | select(.target_files == [])] | length' "$mapping_file")
    local total_count=$(jq '.mappings | length' "$mapping_file")
    local empty_percent=$((empty_count * 100 / total_count))

    if [ "$empty_count" -eq 0 ]; then
        echo "✅ $version: All entries have target_files"
    elif [ "$empty_percent" -lt 5 ]; then
        echo "⚠️  $version: $empty_count entries ($empty_percent%) have empty target_files (acceptable if < 5%)"
    else
        echo "❌ $version: $empty_count entries ($empty_percent%) have empty target_files (exceeds 5% threshold)"
        ((ERRORS++))
    fi
}

check_completeness "$WORK_DIR/mapping-v6.json" "v6"
check_completeness "$WORK_DIR/mapping-v5.json" "v5"
echo ""

# Check target file naming conventions
echo "## 2. Naming Convention Check"
echo ""

check_naming() {
    local mapping_file=$1
    local version=$2

    # Check .json extension
    local no_json=$(jq -r '.mappings[].target_files[]?' "$mapping_file" | grep -v '\.json$' | wc -l)
    no_json=$(echo "$no_json" | tr -d ' ')

    if [ "$no_json" -gt 0 ]; then
        echo "❌ $version: $no_json targets without .json extension"
        jq -r '.mappings[] | select(.target_files[] | endswith(".json") | not) | "\(.id): \(.target_files[])"' "$mapping_file" | head -5
        [ "$no_json" -gt 5 ] && echo "  ... and $((no_json - 5)) more"
        ((ERRORS++))
    else
        echo "✅ $version: All targets use .json extension"
    fi

    # Check kebab-case (no uppercase, no underscores in filename)
    local bad_case=$(jq -r '.mappings[].target_files[]?' "$mapping_file" | grep -E '[A-Z_]' | wc -l)
    bad_case=$(echo "$bad_case" | tr -d ' ')

    if [ "$bad_case" -gt 0 ]; then
        echo "❌ $version: $bad_case targets not in kebab-case (contain uppercase or underscores)"
        jq -r '.mappings[] | select(.target_files[] | test("[A-Z_]")) | "\(.id): \(.target_files[])"' "$mapping_file" | head -5
        [ "$bad_case" -gt 5 ] && echo "  ... and $((bad_case - 5)) more"
        ((ERRORS++))
    else
        echo "✅ $version: All targets use kebab-case"
    fi
}

check_naming "$WORK_DIR/mapping-v6.json" "v6"
echo ""
check_naming "$WORK_DIR/mapping-v5.json" "v5"
echo ""

# Check category → directory mapping compliance
echo "## 3. Directory Mapping Check"
echo ""

check_directory_mapping() {
    local mapping_file=$1
    local version=$2

    # Define expected directory prefixes for each category type
    # This is a simplified check - full validation would require reading categories file
    local invalid_paths=0

    # Check common patterns
    # - features/processing/ for processing patterns
    # - features/handlers/ for handlers
    # - features/libraries/ for libraries
    # - features/tools/ for tools
    # - features/adapters/ for adaptors
    # - about/ for about
    # - setup/ for setup
    # - guides/ for dev-guide
    # - checks/ for checks
    # - migration/ for migration

    # Check no files outside expected directories
    local unexpected=$(jq -r '.mappings[].target_files[]?' "$mapping_file" | \
        grep -vE '^(features/(processing|handlers|libraries|tools|adapters)|about|setup|guides|checks|migration)/' | \
        wc -l)
    unexpected=$(echo "$unexpected" | tr -d ' ')

    if [ "$unexpected" -gt 0 ]; then
        echo "⚠️  $version: $unexpected targets in unexpected directories"
        jq -r '.mappings[] | select(.target_files[] | test("^(features/(processing|handlers|libraries|tools|adapters)|about|setup|guides|checks|migration)/") | not) | "\(.id): \(.target_files[])"' "$mapping_file" | head -5
        [ "$unexpected" -gt 5 ] && echo "  ... and $((unexpected - 5)) more"
        echo "     Review these against category → directory mapping table"
    else
        echo "✅ $version: All targets in expected directories"
    fi
}

check_directory_mapping "$WORK_DIR/mapping-v6.json" "v6"
echo ""
check_directory_mapping "$WORK_DIR/mapping-v5.json" "v5"
echo ""

# Check for duplicate targets
echo "## 4. Duplicate Target Check"
echo ""

check_duplicates() {
    local mapping_file=$1
    local version=$2

    # Extract all target files and find duplicates
    local dup_file=$(mktemp)
    jq -r '.mappings[].target_files[]?' "$mapping_file" | sort | uniq -d > "$dup_file"
    local dup_count=$(wc -l < "$dup_file")

    if [ "$dup_count" -gt 0 ]; then
        echo "⚠️  $version: $dup_count duplicate target paths (same target from different sources)"
        echo "     This may be intentional (multiple sources → one knowledge file)"
        head -5 "$dup_file" | while read -r target; do
            echo "     - $target (used by: $(jq -r ".mappings[] | select(.target_files[] == \"$target\") | .id" "$mapping_file" | tr '\n' ' '))"
        done
        [ "$dup_count" -gt 5 ] && echo "     ... and $((dup_count - 5)) more"
    else
        echo "✅ $version: No duplicate target paths"
    fi

    rm -f "$dup_file"
}

check_duplicates "$WORK_DIR/mapping-v6.json" "v6"
echo ""
check_duplicates "$WORK_DIR/mapping-v5.json" "v5"
echo ""

# Summary
if [ $ERRORS -eq 0 ]; then
    echo "=== Validation Passed ==="
    exit 0
else
    echo "=== Validation Failed with $ERRORS errors ==="
    echo ""
    echo "Fix errors and re-run validation"
    exit 1
fi
