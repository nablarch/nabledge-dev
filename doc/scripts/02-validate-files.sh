#!/bin/bash
# Phase 2 Validation: Validate Collected Files
# Checks that all collected files exist

set -euo pipefail

DATE=$(date +%Y%m%d)
WORK_DIR="work/$DATE/mapping"

echo "=== Phase 2 Validation: File Existence Check ==="
echo ""

if [ ! -f "$WORK_DIR/files-v6-all.txt" ]; then
    echo "❌ Error: $WORK_DIR/files-v6-all.txt not found"
    exit 1
fi

if [ ! -f "$WORK_DIR/files-v5-all.txt" ]; then
    echo "❌ Error: $WORK_DIR/files-v5-all.txt not found"
    exit 1
fi

# Check v6 files
echo "Checking v6 files..."
missing_v6=0
while IFS= read -r file; do
    if [ ! -f "$file" ]; then
        echo "  ❌ Missing: $file"
        ((missing_v6++))
    fi
done < "$WORK_DIR/files-v6-all.txt"

if [ $missing_v6 -eq 0 ]; then
    echo "✅ All v6 files exist"
else
    echo "❌ $missing_v6 v6 files are missing"
fi
echo ""

# Check v5 files
echo "Checking v5 files..."
missing_v5=0
while IFS= read -r file; do
    if [ ! -f "$file" ]; then
        echo "  ❌ Missing: $file"
        ((missing_v5++))
    fi
done < "$WORK_DIR/files-v5-all.txt"

if [ $missing_v5 -eq 0 ]; then
    echo "✅ All v5 files exist"
else
    echo "❌ $missing_v5 v5 files are missing"
fi
echo ""

# Summary
if [ $missing_v6 -eq 0 ] && [ $missing_v5 -eq 0 ]; then
    echo "=== Validation Passed ==="
    exit 0
else
    echo "=== Validation Failed ==="
    exit 1
fi
