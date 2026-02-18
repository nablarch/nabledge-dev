#!/bin/bash
# Phase 4: Generate Initial Mappings
# Creates mapping entries with id, source_file, title

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR"
TMP_DIR="$WORK_DIR/tmp"

echo "=== Phase 4: Generate Initial Mappings ==="
echo ""

if [ ! -f "$TMP_DIR/files-v6-grouped.txt" ]; then
    echo "❌ Error: Run 03.5-group-duplicates.sh first"
    exit 1
fi

# Function to generate mappings
generate_mappings() {
    local grouped_file=$1
    local alternatives_file=$2
    local mapping_file=$3
    local version=$4

    echo "Generating $version mappings..."

    # Extract title from .rst file
    extract_title() {
        local file=$1
        local ext="${file##*.}"

        if [ "$ext" = "rst" ]; then
            # Try to get first non-empty line as title
            local title=$(head -20 "$file" 2>/dev/null | grep -v "^$" | grep -v "^====" | grep -v "^----" | grep -v "^\.\." | head -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' || echo "")
            if [ -n "$title" ]; then
                echo "$title"
            else
                basename "$file" .rst
            fi
        elif [ "$ext" = "md" ]; then
            # Try to get first # heading
            local title=$(head -20 "$file" 2>/dev/null | grep "^#" | head -1 | sed 's/^#*[[:space:]]*//' || echo "")
            if [ -n "$title" ]; then
                echo "$title"
            else
                basename "$file" .md
            fi
        else
            basename "$file"
        fi
    }

    # Generate entries using Python
    python3 - "$grouped_file" "$alternatives_file" "$mapping_file" "$version" << 'PYTHON_SCRIPT'
import sys
import json
import os

grouped_file = sys.argv[1]
alternatives_file = sys.argv[2]
mapping_file = sys.argv[3]
version = sys.argv[4]

# Read existing mapping to get schema
with open(mapping_file, 'r') as f:
    mapping_data = json.load(f)

# Read grouped files
with open(grouped_file, 'r') as f:
    files = [line.strip() for line in f if line.strip()]

# Read alternatives mapping
alternatives_map = {}
if os.path.exists(alternatives_file):
    with open(alternatives_file, 'r') as f:
        alternatives_map = json.load(f)

# Generate entries
entries = []
for idx, file_path in enumerate(files, start=1):
    # Remove .lw/ prefix for source_file
    source_file = file_path
    if source_file.startswith('.lw/'):
        source_file = source_file[len('.lw/'):]

    # Extract title (simple: use basename for now, AI will refine later)
    title = file_path.split('/')[-1].rsplit('.', 1)[0].replace('-', ' ').replace('_', ' ').title()

    # Create entry
    entry = {
        "id": f"v{version}-{idx:04d}",
        "source_file": source_file,
        "title": title,
        "categories": [],
        "target_files": []
    }

    # Add alternatives if exists
    if file_path in alternatives_map:
        # Remove .lw/ prefix from alternatives
        alts = []
        for alt in alternatives_map[file_path]:
            if alt.startswith('.lw/'):
                alts.append(alt[len('.lw/'):])
            else:
                alts.append(alt)
        entry["source_file_alternatives"] = alts

    entries.append(entry)

# Update mapping data
mapping_data['mappings'] = entries

# Write back
with open(mapping_file, 'w') as f:
    json.dump(mapping_data, f, indent=2, ensure_ascii=False)

print(f"  Generated {len(entries)} entries")
with_alts = sum(1 for e in entries if "source_file_alternatives" in e)
print(f"  Entries with alternatives: {with_alts}")
PYTHON_SCRIPT

    echo ""
}

# Generate v6 mappings
generate_mappings "$TMP_DIR/files-v6-grouped.txt" \
                   "$TMP_DIR/files-v6-alternatives.json" \
                   "$WORK_DIR/mapping-v6.json" \
                   "6"

# Generate v5 mappings
generate_mappings "$TMP_DIR/files-v5-grouped.txt" \
                   "$TMP_DIR/files-v5-alternatives.json" \
                   "$WORK_DIR/mapping-v5.json" \
                   "5"

echo "=== Phase 4 Complete ==="
echo ""
echo "Output:"
echo "  - $WORK_DIR/mapping-v6.json ($(jq '.mappings | length' "$WORK_DIR/mapping-v6.json") entries)"
echo "  - $WORK_DIR/mapping-v5.json ($(jq '.mappings | length' "$WORK_DIR/mapping-v5.json") entries)"
echo ""
echo "Validation: Run doc/scripts/04-validate-mappings.sh"
echo "Next step: Phase 5 - Categorize entries (AI Agent work)"
