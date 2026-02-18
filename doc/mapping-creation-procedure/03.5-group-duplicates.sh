#!/bin/bash
# Phase 3.5: Group Duplicate .config Files
# Groups identical .config files to reduce redundancy

set -euo pipefail

DATE=$(date +%Y%m%d)
WORK_DIR="work/$DATE/mapping"

echo "=== Phase 3.5: Group Duplicate Files ==="
echo ""

if [ ! -f "$WORK_DIR/files-v6-filtered.txt" ] || [ ! -f "$WORK_DIR/files-v5-filtered.txt" ]; then
    echo "❌ Error: Run 03-filter-language.sh first"
    exit 1
fi

# Function to group duplicates by MD5 hash
group_duplicates() {
    local input_file=$1
    local output_file=$2
    local report_file=$3
    local version=$4

    echo "Processing $version files..."

    # Separate .config files from others
    local config_files="$WORK_DIR/temp-${version}-config.txt"
    local other_files="$WORK_DIR/temp-${version}-other.txt"

    grep '\.config$' "$input_file" > "$config_files" || true
    grep -v '\.config$' "$input_file" > "$other_files" || true

    local config_count=$(wc -l < "$config_files" 2>/dev/null || echo 0)
    local other_count=$(wc -l < "$other_files" 2>/dev/null || echo 0)

    echo "  .config files: $config_count"
    echo "  Other files: $other_count"

    if [ "$config_count" -eq 0 ]; then
        # No config files, just copy input to output
        cp "$input_file" "$output_file"
        echo "No .config files to group" > "$report_file"
        return
    fi

    # Calculate MD5 for each .config file
    local hash_file="$WORK_DIR/temp-${version}-hashes.txt"
    > "$hash_file"

    while IFS= read -r file; do
        if [ -f "$file" ]; then
            hash=$(md5sum "$file" | awk '{print $1}')
            echo "$hash|$file" >> "$hash_file"
        fi
    done < "$config_files"

    # Group by hash and select representative
    python3 - "$hash_file" "$output_file" "$report_file" "$other_files" << 'PYTHON_SCRIPT'
import sys
from collections import defaultdict

hash_file = sys.argv[1]
output_file = sys.argv[2]
report_file = sys.argv[3]
other_files = sys.argv[4]

# Read hash mappings
groups = defaultdict(list)
with open(hash_file, 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        hash_val, file_path = line.split('|', 1)
        groups[hash_val].append(file_path)

# Select representative for each group (alphabetically first)
representatives = []
alternatives_map = {}

for hash_val, files in groups.items():
    sorted_files = sorted(files)
    representative = sorted_files[0]
    representatives.append(representative)

    if len(sorted_files) > 1:
        alternatives_map[representative] = sorted_files[1:]

# Write output (representatives + other files)
with open(output_file, 'w') as out:
    # Write representatives
    for rep in sorted(representatives):
        out.write(rep + '\n')

    # Write other files
    try:
        with open(other_files, 'r') as f:
            for line in f:
                out.write(line)
    except FileNotFoundError:
        pass

# Write report
with open(report_file, 'w') as report:
    report.write(f'# Duplicate Grouping Report\n\n')
    report.write(f'Total unique groups: {len(groups)}\n')
    report.write(f'Total files before: {sum(len(files) for files in groups.values())}\n')
    report.write(f'Total files after: {len(representatives)}\n')
    report.write(f'Reduction: {sum(len(files) for files in groups.values()) - len(representatives)} files\n\n')

    report.write('## Groups with Duplicates\n\n')
    for hash_val, files in sorted(groups.items(), key=lambda x: len(x[1]), reverse=True):
        if len(files) > 1:
            report.write(f'### Group (hash: {hash_val[:8]}..., {len(files)} files)\n\n')
            report.write(f'**Representative**: {files[0]}\n\n')
            report.write('**Alternatives**:\n')
            for alt in files[1:]:
                report.write(f'- {alt}\n')
            report.write('\n')

# Write alternatives mapping (for Phase 4)
alternatives_file = output_file.replace('grouped.txt', 'alternatives.json')
import json
with open(alternatives_file, 'w') as f:
    json.dump(alternatives_map, f, indent=2)
PYTHON_SCRIPT

    local final_count=$(wc -l < "$output_file")
    echo "  After grouping: $final_count files"

    # Cleanup temp files
    rm -f "$config_files" "$other_files" "$hash_file"
    echo ""
}

# Process v6
group_duplicates "$WORK_DIR/files-v6-filtered.txt" \
                 "$WORK_DIR/files-v6-grouped.txt" \
                 "$WORK_DIR/grouping-report-v6.md" \
                 "v6"

# Process v5
group_duplicates "$WORK_DIR/files-v5-filtered.txt" \
                 "$WORK_DIR/files-v5-grouped.txt" \
                 "$WORK_DIR/grouping-report-v5.md" \
                 "v5"

# Generate summary
cat > "$WORK_DIR/grouping-summary.md" <<EOF
# Duplicate Grouping Summary

**Date**: $(date -Iseconds)

## Grouping Strategy

Identical .config files (same MD5 hash) are grouped together:
- **Representative**: The alphabetically first file in each group
- **Alternatives**: All other files in the group (tracked but not separately mapped)

This reduces redundancy while maintaining full traceability.

## Results

### Nablarch v6

Before grouping: $(wc -l < "$WORK_DIR/files-v6-filtered.txt") files
After grouping: $(wc -l < "$WORK_DIR/files-v6-grouped.txt") files
Reduction: $(( $(wc -l < "$WORK_DIR/files-v6-filtered.txt") - $(wc -l < "$WORK_DIR/files-v6-grouped.txt") )) files

See: grouping-report-v6.md

### Nablarch v5

Before grouping: $(wc -l < "$WORK_DIR/files-v5-filtered.txt") files
After grouping: $(wc -l < "$WORK_DIR/files-v5-grouped.txt") files
Reduction: $(( $(wc -l < "$WORK_DIR/files-v5-filtered.txt") - $(wc -l < "$WORK_DIR/files-v5-grouped.txt") )) files

See: grouping-report-v5.md

## Impact on Mapping

- Mapping entries will be created only for representative files
- \`source_file_alternatives\` field will list duplicate files
- Total mapping entries reduced while maintaining full coverage
EOF

echo "=== Phase 3.5 Complete ==="
echo ""
echo "Output files:"
echo "  - $WORK_DIR/files-v6-grouped.txt ($(wc -l < "$WORK_DIR/files-v6-grouped.txt") files)"
echo "  - $WORK_DIR/files-v5-grouped.txt ($(wc -l < "$WORK_DIR/files-v5-grouped.txt") files)"
echo "  - $WORK_DIR/grouping-summary.md"
echo ""
echo "Summary:"
cat "$WORK_DIR/grouping-summary.md"
echo ""
echo "Next step: Run doc/mapping-creation-procedure/04-generate-mappings.sh"
