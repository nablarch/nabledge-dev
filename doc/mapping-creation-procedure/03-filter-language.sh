#!/bin/bash
# Phase 3: Apply Language Priority and File Type Filtering
# Selects /en/ over /ja/ and filters by file type (.rst, .md, .xml, .config, .txt)

set -euo pipefail

DATE=$(date +%Y%m%d)
WORK_DIR="work/$DATE/mapping"

echo "=== Phase 3: Language Priority and File Type Filtering ==="
echo ""

if [ ! -f "$WORK_DIR/files-v6-all.txt" ]; then
    echo "❌ Error: Run 02-collect-files.sh first"
    exit 1
fi

# Function to process files
process_files() {
    local input_file=$1
    local output_file=$2
    local report_file=$3
    local version=$4

    echo "Processing $version files..."

    # Step 1: Apply file type filter first
    local temp_typed="$WORK_DIR/temp-${version}-typed.txt"
    > "$temp_typed"

    while IFS= read -r file; do
        local ext="${file##*.}"
        local include=false

        case "$ext" in
            rst)
                # Include all .rst files
                include=true
                ;;
            md)
                # Include .md from development guide OR archetype README.md
                if echo "$file" | grep -q "nablarch-system-development-guide" || \
                   echo "$file" | grep -Eq "nablarch-single-module-archetype/.*/README\.md$"; then
                    include=true
                fi
                ;;
            xml)
                # Include only pom.xml from archetype projects (exclude build parent poms)
                if echo "$file" | grep -q "nablarch-single-module-archetype"; then
                    # Exclude build parent poms
                    if ! echo "$file" | grep -q "nablarch-archetype-build-parent" && \
                       ! echo "$file" | grep -q "nablarch-archetype-parent"; then
                        include=true
                    fi
                fi
                ;;
            config)
                # Include only .config from spotbugs/published-config directory
                if echo "$file" | grep -q "spotbugs/published-config"; then
                    include=true
                fi
                ;;
            txt)
                # Include only config.txt from jspanalysis or toolbox directories
                if echo "$file" | grep -Eq "(jspanalysis|JspStaticAnalysis)/config\.txt$"; then
                    include=true
                fi
                ;;
        esac

        if [ "$include" = true ]; then
            echo "$file" >> "$temp_typed"
        fi
    done < "$input_file"

    local typed_count=$(wc -l < "$temp_typed" 2>/dev/null || echo 0)
    echo "  After file type filter: $typed_count files"

    # Step 2: Apply language priority
    > "$report_file"

    # Group files by language-agnostic path and select
    python3 - "$temp_typed" "$output_file" "$report_file" << 'PYTHON_SCRIPT'
import sys
from collections import defaultdict

input_file = sys.argv[1]
output_file = sys.argv[2]
report_file = sys.argv[3]

# Read all files
files = []
with open(input_file, 'r') as f:
    files = [line.strip() for line in f if line.strip()]

# Group by language-agnostic path
groups = defaultdict(lambda: {'en': None, 'ja': None, 'none': None})

for file_path in files:
    # Determine language
    if '/en/' in file_path:
        lang = 'en'
        agnostic = file_path.replace('/en/', '/LANG/')
    elif '/ja/' in file_path:
        lang = 'ja'
        agnostic = file_path.replace('/ja/', '/LANG/')
    else:
        lang = 'none'
        agnostic = file_path

    groups[agnostic][lang] = file_path

# Select by priority: en > ja > none
selected = []
report_lines = []

for agnostic, langs in sorted(groups.items()):
    if langs['en']:
        selected.append(langs['en'])
        if langs['ja']:
            report_lines.append(f"Selected EN: {langs['en']} (skipped JA: {langs['ja']})")
    elif langs['ja']:
        selected.append(langs['ja'])
        report_lines.append(f"Selected JA (no EN): {langs['ja']}")
    elif langs['none']:
        selected.append(langs['none'])

# Write output
with open(output_file, 'w') as f:
    for file_path in sorted(selected):
        f.write(file_path + '\n')

with open(report_file, 'w') as f:
    for line in report_lines:
        f.write(line + '\n')

print(f"  After language selection: {len(selected)} files")
PYTHON_SCRIPT

    rm -f "$temp_typed"
    echo ""
}

# Process v6
process_files "$WORK_DIR/files-v6-all.txt" \
              "$WORK_DIR/files-v6-filtered.txt" \
              "$WORK_DIR/language-selection-v6.txt" \
              "v6"

# Process v5
process_files "$WORK_DIR/files-v5-all.txt" \
              "$WORK_DIR/files-v5-filtered.txt" \
              "$WORK_DIR/language-selection-v5.txt" \
              "v5"

# Generate summary report
cat > "$WORK_DIR/language-selection.md" <<EOF
# Language Selection and File Type Filtering Report

**Date**: $(date -Iseconds)

## Selection Rules

1. **Language Priority**: English (/en/) preferred, Japanese (/ja/) fallback if no English version
2. **File Type Filtering**:
   - .rst: All files included
   - .md: From nablarch-system-development-guide OR archetype README.md
   - .xml: Only pom.xml from archetypes (exclude build parent poms)
   - .config: Only from spotbugs/published-config directories
   - .txt: Only config.txt from jspanalysis/JspStaticAnalysis directories

## Nablarch v6

Before filtering: $(wc -l < "$WORK_DIR/files-v6-all.txt") files
After filtering: $(wc -l < "$WORK_DIR/files-v6-filtered.txt") files

By file type (after filtering):
  - .rst: $(grep '\.rst$' "$WORK_DIR/files-v6-filtered.txt" | wc -l)
  - .md: $(grep '\.md$' "$WORK_DIR/files-v6-filtered.txt" | wc -l)
  - .xml: $(grep '\.xml$' "$WORK_DIR/files-v6-filtered.txt" | wc -l)
  - .config: $(grep '\.config$' "$WORK_DIR/files-v6-filtered.txt" | wc -l)
  - .txt: $(grep '\.txt$' "$WORK_DIR/files-v6-filtered.txt" | wc -l)

By language (after filtering):
  - /en/: $(grep "/en/" "$WORK_DIR/files-v6-filtered.txt" | wc -l)
  - /ja/: $(grep "/ja/" "$WORK_DIR/files-v6-filtered.txt" | wc -l)
  - (no lang dir): $(grep -v "/en/" "$WORK_DIR/files-v6-filtered.txt" | grep -v "/ja/" | wc -l)

Selection details: See language-selection-v6.txt

## Nablarch v5

Before filtering: $(wc -l < "$WORK_DIR/files-v5-all.txt") files
After filtering: $(wc -l < "$WORK_DIR/files-v5-filtered.txt") files

By file type (after filtering):
  - .rst: $(grep '\.rst$' "$WORK_DIR/files-v5-filtered.txt" | wc -l)
  - .md: $(grep '\.md$' "$WORK_DIR/files-v5-filtered.txt" | wc -l)
  - .xml: $(grep '\.xml$' "$WORK_DIR/files-v5-filtered.txt" | wc -l)
  - .config: $(grep '\.config$' "$WORK_DIR/files-v5-filtered.txt" | wc -l)
  - .txt: $(grep '\.txt$' "$WORK_DIR/files-v5-filtered.txt" | wc -l)

By language (after filtering):
  - /en/: $(grep "/en/" "$WORK_DIR/files-v5-filtered.txt" | wc -l)
  - /ja/: $(grep "/ja/" "$WORK_DIR/files-v5-filtered.txt" | wc -l)
  - (no lang dir): $(grep -v "/en/" "$WORK_DIR/files-v5-filtered.txt" | grep -v "/ja/" | wc -l)

Selection details: See language-selection-v5.txt
EOF

echo "=== Phase 3 Complete ==="
echo ""
echo "Output files:"
echo "  - $WORK_DIR/files-v6-filtered.txt ($(wc -l < "$WORK_DIR/files-v6-filtered.txt") files)"
echo "  - $WORK_DIR/files-v5-filtered.txt ($(wc -l < "$WORK_DIR/files-v5-filtered.txt") files)"
echo "  - $WORK_DIR/language-selection.md"
echo ""
echo "Summary:"
cat "$WORK_DIR/language-selection.md"
echo ""
echo "Validation: Run doc/scripts/03-validate-language.sh"
echo "Next step: Run doc/scripts/04-generate-mappings.sh"
