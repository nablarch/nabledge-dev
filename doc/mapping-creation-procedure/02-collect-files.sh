#!/bin/bash
# Phase 2: Collect Source Files (Whitelist Approach)
# Only collects files explicitly included in mapping scope

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR"
TMP_DIR="$WORK_DIR/tmp"

echo "=== Phase 2: Collect Source Files (Whitelist) ==="
echo ""

if [ ! -d "$WORK_DIR" ]; then
    echo "❌ Error: $WORK_DIR not found. Run 01-init-mapping.sh first."
    exit 1
fi

# Create tmp directory if it doesn't exist
mkdir -p "$TMP_DIR"

# Collect v6 files
echo "Collecting v6 files..."
echo ""

V6_DOCS=".lw/nab-official/v6/nablarch-document"
V6_GUIDE=".lw/nab-official/v6/nablarch-system-development-guide"

{
    # 1. nablarch-document: All files
    echo "  - From nablarch-document..."
    find "$V6_DOCS" -type f \( -name "*.rst" -o -name "*.md" -o -name "config.txt" \) 2>/dev/null || true

    # 2. nablarch-system-development-guide: nablarch-patterns only
    echo "  - From nablarch-patterns..."
    find "$V6_GUIDE" -path "*/nablarch-patterns/*.md" 2>/dev/null || true

    # 3. Security mapping (xlsx)
    echo "  - Security mapping..."
    if [ -f "$V6_GUIDE/Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx" ]; then
        echo "$V6_GUIDE/Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx"
    fi
} | grep -v "^  -" | sort > "$TMP_DIR/files-v6-all.txt"

v6_count=$(wc -l < "$TMP_DIR/files-v6-all.txt")
echo "Found $v6_count v6 files"
echo ""

# Collect v5 files
echo "Collecting v5 files..."
echo ""

V5_DOCS=".lw/nab-official/v5/nablarch-document"
V5_GUIDE=".lw/nab-official/v5/nablarch-system-development-guide"

{
    # 1. nablarch-document: All files
    echo "  - From nablarch-document..."
    find "$V5_DOCS" -type f \( -name "*.rst" -o -name "*.md" -o -name "config.txt" \) 2>/dev/null || true

    # 2. nablarch-system-development-guide: nablarch-patterns only (if exists)
    if [ -d "$V5_GUIDE" ]; then
        echo "  - From nablarch-patterns..."
        find "$V5_GUIDE" -path "*/nablarch-patterns/*.md" 2>/dev/null || true

        # 3. Security mapping (xlsx) (if exists)
        echo "  - Security mapping..."
        if [ -f "$V5_GUIDE/Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx" ]; then
            echo "$V5_GUIDE/Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx"
        fi
    fi
} | grep -v "^  -" | sort > "$TMP_DIR/files-v5-all.txt"

v5_count=$(wc -l < "$TMP_DIR/files-v5-all.txt")
echo "Found $v5_count v5 files"
echo ""

# Generate statistics
echo "Generating statistics..."

cat > "$TMP_DIR/stats.md" <<EOF
# File Collection Statistics (Whitelist Approach)

**Date**: $(date -Iseconds)

## Nablarch v6

Total files: $v6_count

By file type:
  - .rst: $(grep -c '\.rst$' "$TMP_DIR/files-v6-all.txt" || echo 0)
  - .md: $(grep -c '\.md$' "$TMP_DIR/files-v6-all.txt" || echo 0)
  - .xlsx: $(grep -c '\.xlsx$' "$TMP_DIR/files-v6-all.txt" || echo 0)
  - .txt: $(grep -c '\.txt$' "$TMP_DIR/files-v6-all.txt" || echo 0)

By source:
  - nablarch-document: $(grep -c "nablarch-document" "$TMP_DIR/files-v6-all.txt" || echo 0)
  - nablarch-patterns: $(grep -c "nablarch-patterns" "$TMP_DIR/files-v6-all.txt" || echo 0)
  - Security mapping: $(grep -c "セキュリティ対応表" "$TMP_DIR/files-v6-all.txt" || echo 0)

By language:
  - /en/: $(grep -c "/en/" "$TMP_DIR/files-v6-all.txt" || echo 0)
  - /ja/: $(grep -c "/ja/" "$TMP_DIR/files-v6-all.txt" || echo 0)
  - (no lang dir): $(grep -v "/en/" "$TMP_DIR/files-v6-all.txt" | grep -cv "/ja/" || echo 0)

## Nablarch v5

Total files: $v5_count

By file type:
  - .rst: $(grep -c '\.rst$' "$TMP_DIR/files-v5-all.txt" || echo 0)
  - .md: $(grep -c '\.md$' "$TMP_DIR/files-v5-all.txt" || echo 0)
  - .xlsx: $(grep -c '\.xlsx$' "$TMP_DIR/files-v5-all.txt" || echo 0)
  - .txt: $(grep -c '\.txt$' "$TMP_DIR/files-v5-all.txt" || echo 0)

By source:
  - nablarch-document: $(grep -c "nablarch-document" "$TMP_DIR/files-v5-all.txt" || echo 0)
  - nablarch-patterns: $(grep -c "nablarch-patterns" "$TMP_DIR/files-v5-all.txt" || echo 0)
  - Security mapping: $(grep -c "セキュリティ対応表" "$TMP_DIR/files-v5-all.txt" || echo 0)

By language:
  - /en/: $(grep -c "/en/" "$TMP_DIR/files-v5-all.txt" || echo 0)
  - /ja/: $(grep -c "/ja/" "$TMP_DIR/files-v5-all.txt" || echo 0)
  - (no lang dir): $(grep -v "/en/" "$TMP_DIR/files-v5-all.txt" | grep -cv "/ja/" || echo 0)

## Excluded via Whitelist

- nablarch-single-module-archetype (entire directory)
- nablarch-system-development-guide/docs/ (project-specific guides)
- Sample_Project/ (except security mapping)
- .textlint/test/ (documentation tooling)
- license.rst (legal information)
EOF

echo "✅ Created: $TMP_DIR/stats.md"
echo ""

echo "=== Phase 2 Complete ==="
echo ""
echo "Output files:"
echo "  - $TMP_DIR/files-v6-all.txt ($v6_count files)"
echo "  - $TMP_DIR/files-v5-all.txt ($v5_count files)"
echo "  - $TMP_DIR/stats.md"
echo ""
echo "Statistics:"
cat "$TMP_DIR/stats.md"
echo ""
echo "Validation: Run doc/mapping-creation-procedure/02-validate-files.sh"
echo "Next step: Run doc/mapping-creation-procedure/03-filter-language.sh"
