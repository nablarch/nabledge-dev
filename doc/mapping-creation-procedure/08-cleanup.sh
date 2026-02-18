#!/bin/bash
# Phase 8: Clean Up Intermediate Files
# Removes intermediate files and keeps only final mapping files

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR"

echo "=== Phase 8: Clean Up Intermediate Files ==="
echo ""

# List files to be deleted
echo "Files to be deleted:"
echo ""

# Intermediate file patterns
patterns=(
    "files-*.txt"
    "*-alternatives.json"
    "*-report*.md"
    "stats.md"
    "language-selection.md"
    "grouping-summary.md"
    "validation-report.md"
    "progress-*.txt"
    "*-log.md"
    "mapping-*-backup*.json"
)

files_to_delete=()
for pattern in "${patterns[@]}"; do
    for file in "$WORK_DIR"/$pattern; do
        if [ -f "$file" ]; then
            echo "  - $(basename "$file")"
            files_to_delete+=("$file")
        fi
    done
done

if [ ${#files_to_delete[@]} -eq 0 ]; then
    echo "  (No intermediate files found)"
    echo ""
    echo "=== Phase 8 Complete ==="
    exit 0
fi

echo ""
read -p "Delete these ${#files_to_delete[@]} files? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    for file in "${files_to_delete[@]}"; do
        rm -f "$file"
    done
    echo ""
    echo "✅ Deleted ${#files_to_delete[@]} intermediate files"
else
    echo ""
    echo "❌ Cleanup cancelled"
    exit 1
fi

echo ""
echo "=== Phase 8 Complete ==="
echo ""
echo "Final files remaining in $WORK_DIR:"
echo "  - mapping-v6.json (final confirmed mapping)"
echo "  - mapping-v6.xlsx (Excel version for review)"
echo "  - mapping-v5.json (final confirmed mapping)"
echo "  - mapping-v5.xlsx (Excel version for review)"
echo "  - categories-v6.json (category definitions)"
echo "  - categories-v5.json (category definitions)"
echo "  - 01-init-mapping.sh through 08-cleanup.sh (scripts)"
echo "  - mapping-creation-procedure.md (documentation)"
echo ""
echo "Ready to commit: git add doc/mapping-creation-procedure/ && git commit"
