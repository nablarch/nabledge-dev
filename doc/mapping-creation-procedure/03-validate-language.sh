#!/bin/bash
# Phase 3 Validation: Validate Language Selection and File Type Filtering

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR"
TMP_DIR="$WORK_DIR/tmp"

echo "=== Phase 3 Validation: Language Selection ==="
echo ""

if [ ! -f "$TMP_DIR/files-v6-filtered.txt" ]; then
    echo "❌ Error: $TMP_DIR/files-v6-filtered.txt not found"
    exit 1
fi

ERRORS=0

# Check no duplicate language-agnostic paths
echo "Checking for duplicate language-agnostic paths..."

check_duplicates() {
    local filtered_file=$1
    local version=$2

    # Convert paths to language-agnostic form and check for duplicates
    local temp_file=$(mktemp)
    sed 's|/en/|/LANG/|g; s|/ja/|/LANG/|g' "$filtered_file" | sort | uniq -d > "$temp_file"

    local dup_count=$(wc -l < "$temp_file")
    if [ "$dup_count" -gt 0 ]; then
        echo "❌ $version: $dup_count duplicate language-agnostic paths found:"
        head -5 "$temp_file" | sed 's/^/  /'
        [ "$dup_count" -gt 5 ] && echo "  ... and $((dup_count - 5)) more"
        ((ERRORS++))
    else
        echo "✅ $version: No duplicate language-agnostic paths"
    fi

    rm -f "$temp_file"
}

check_duplicates "$TMP_DIR/files-v6-filtered.txt" "v6"
check_duplicates "$TMP_DIR/files-v5-filtered.txt" "v5"
echo ""

# Check English versions selected when available
echo "Checking English preference..."

check_english_preference() {
    local selection_file=$1
    local version=$2

    if [ ! -f "$selection_file" ]; then
        echo "⚠️  $version: Selection report not found, skipping English preference check"
        return
    fi

    # Count how many times JA was selected
    local ja_selected=$(grep -c "Selected JA (no EN):" "$selection_file" 2>/dev/null || echo 0)
    local ja_skipped=$(grep -c "skipped JA:" "$selection_file" 2>/dev/null || echo 0)

    echo "  $version:"
    echo "    - EN selected (JA skipped): $ja_skipped"
    echo "    - JA selected (no EN): $ja_selected"

    if [ "$ja_selected" -gt 0 ]; then
        echo "    ℹ️  Using JA fallback for files without EN version"
    fi
}

check_english_preference "$TMP_DIR/language-selection-v6.txt" "v6"
check_english_preference "$TMP_DIR/language-selection-v5.txt" "v5"
echo ""

# Check file type filtering
echo "Checking file type filtering..."

check_file_types() {
    local filtered_file=$1
    local version=$2

    local rst_count=$(grep -c '\.rst$' "$filtered_file")
    local md_count=$(grep -c '\.md$' "$filtered_file")
    local xml_count=$(grep -c '\.xml$' "$filtered_file")
    local config_count=$(grep -c '\.config$' "$filtered_file")
    local txt_count=$(grep -c '\.txt$' "$filtered_file")
    local other_count=$(grep -cvE '\.(rst|md|xml|config|txt)$' "$filtered_file")
    other_count=$(echo "$other_count" | tr -d ' ')

    echo "  $version:"
    echo "    - .rst files: $rst_count"
    echo "    - .md files: $md_count"
    echo "    - .xml files: $xml_count"
    echo "    - .config files: $config_count"
    echo "    - .txt files: $txt_count"

    if [ "$other_count" -gt 0 ]; then
        echo "    ❌ Unexpected file types: $other_count"
        ((ERRORS++))
    else
        echo "    ✅ All files are .rst, .md, .xml, .config, or .txt"
    fi

    # Check all .md are from dev guide or archetype README.md
    local bad_md=$(grep '\.md$' "$filtered_file" | grep -v "nablarch-system-development-guide" | grep -v "README.md" | wc -l)
    bad_md=$(echo "$bad_md" | tr -d ' ')
    if [ "$bad_md" -gt 0 ]; then
        echo "    ❌ $bad_md .md files not from development guide or README.md"
        ((ERRORS++))
    else
        echo "    ✅ All .md files from development guide or README.md"
    fi

    # Check all .xml are from archetypes (excluding build parents)
    local bad_xml=$(grep '\.xml$' "$filtered_file" | grep -v "nablarch-single-module-archetype" | wc -l)
    bad_xml=$(echo "$bad_xml" | tr -d ' ')
    if [ "$bad_xml" -gt 0 ]; then
        echo "    ❌ $bad_xml .xml files not from archetypes"
        ((ERRORS++))
    fi

    local parent_pom=$(grep '\.xml$' "$filtered_file" | grep -E "(nablarch-archetype-build-parent|nablarch-archetype-parent)" | wc -l)
    parent_pom=$(echo "$parent_pom" | tr -d ' ')
    if [ "$parent_pom" -gt 0 ]; then
        echo "    ❌ $parent_pom build parent pom.xml files included (should be excluded)"
        ((ERRORS++))
    else
        echo "    ✅ Build parent poms excluded"
    fi

    # Check all .config are from spotbugs/published-config
    local bad_config=$(grep '\.config$' "$filtered_file" | grep -v "spotbugs/published-config" | wc -l)
    bad_config=$(echo "$bad_config" | tr -d ' ')
    if [ "$bad_config" -gt 0 ]; then
        echo "    ❌ $bad_config .config files not from spotbugs/published-config"
        ((ERRORS++))
    else
        echo "    ✅ All .config files from spotbugs/published-config"
    fi

    # Check all .txt are config.txt from jspanalysis
    local bad_txt=$(grep '\.txt$' "$filtered_file" | grep -v "config.txt" | wc -l)
    bad_txt=$(echo "$bad_txt" | tr -d ' ')
    if [ "$bad_txt" -gt 0 ]; then
        echo "    ❌ $bad_txt .txt files not config.txt"
        ((ERRORS++))
    else
        echo "    ✅ All .txt files are config.txt"
    fi
}

check_file_types "$TMP_DIR/files-v6-filtered.txt" "v6"
echo ""
check_file_types "$TMP_DIR/files-v5-filtered.txt" "v5"
echo ""

# Validate against expected ranges
echo "Checking file counts against expected ranges..."

v6_count=$(wc -l < "$TMP_DIR/files-v6-filtered.txt")
v5_count=$(wc -l < "$TMP_DIR/files-v5-filtered.txt")

# Expected ranges (based on known official doc structure)
# v6: ~336 rst + ~167 md + ~9 xml + ~90 config + ~3 txt = ~605
# v5: ~433 rst + ~9 md + ~9 xml + ~90 config + ~3 txt = ~544

echo "  v6: $v6_count files"
if [ "$v6_count" -lt 550 ] || [ "$v6_count" -gt 650 ]; then
    echo "    ⚠️  Outside expected range (550-650)"
    echo "    This may indicate missing files or incorrect filtering"
else
    echo "    ✅ Within expected range"
fi

echo "  v5: $v5_count files"
if [ "$v5_count" -lt 500 ] || [ "$v5_count" -gt 600 ]; then
    echo "    ⚠️  Outside expected range (500-600)"
    echo "    This may indicate missing files or incorrect filtering"
else
    echo "    ✅ Within expected range"
fi
echo ""

# Summary
if [ $ERRORS -eq 0 ]; then
    echo "=== Validation Passed ==="
    exit 0
else
    echo "=== Validation Failed with $ERRORS errors ==="
    echo ""
    echo "Review errors above and fix issues in Phase 3 script"
    exit 1
fi
