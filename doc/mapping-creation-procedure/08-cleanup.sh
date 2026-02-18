#!/bin/bash
# Phase 8: Clean Up Intermediate Files
# Removes tmp/ directory containing all intermediate files

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR"
TMP_DIR="$WORK_DIR/tmp"

echo "=== Phase 8: Clean Up Intermediate Files ==="
echo ""

# Check if tmp directory exists
if [ ! -d "$TMP_DIR" ]; then
    echo "  (No tmp/ directory found)"
    echo ""
    echo "=== Phase 8 Complete ==="
    exit 0
fi

# Count files in tmp directory
file_count=$(find "$TMP_DIR" -type f | wc -l)

if [ "$file_count" -eq 0 ]; then
    echo "  (tmp/ directory is empty)"
    rmdir "$TMP_DIR"
    echo "✅ Removed empty tmp/ directory"
    echo ""
    echo "=== Phase 8 Complete ==="
    exit 0
fi

echo "Directory to be deleted:"
echo "  - tmp/ ($file_count files)"
echo ""
echo "Contents:"
find "$TMP_DIR" -type f -exec basename {} \; | sort | sed 's/^/    /'

echo ""
read -p "Delete tmp/ directory and all its contents? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$TMP_DIR"
    echo ""
    echo "✅ Deleted tmp/ directory with $file_count files"
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
