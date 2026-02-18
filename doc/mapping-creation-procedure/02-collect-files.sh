#!/bin/bash
# Phase 2: Collect All Source Files
# Finds all .rst, .md, .xml files in official documentation

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR/output"

echo "=== Phase 2: Collect All Source Files ==="
echo ""

if [ ! -d "$WORK_DIR" ]; then
    echo "❌ Error: $WORK_DIR not found. Run 01-init-mapping.sh first."
    exit 1
fi

# Collect v6 files
echo "Collecting v6 files..."
echo ""

V6_DOCS=".lw/nab-official/v6/nablarch-document"
V6_GUIDE=".lw/nab-official/v6/nablarch-system-development-guide"
V6_ARCHETYPE=".lw/nab-official/v6/nablarch-single-module-archetype"

{
    find "$V6_DOCS" -name "*.rst" 2>/dev/null || true
    find "$V6_DOCS" -name "*.md" 2>/dev/null || true
    find "$V6_DOCS" -name "config.txt" 2>/dev/null || true
    find "$V6_GUIDE" -name "*.rst" 2>/dev/null || true
    find "$V6_GUIDE" -name "*.md" 2>/dev/null || true
    find "$V6_ARCHETYPE" -name "*.rst" 2>/dev/null || true
    find "$V6_ARCHETYPE" -name "*.md" 2>/dev/null || true
    find "$V6_ARCHETYPE" -name "pom.xml" 2>/dev/null || true
    find "$V6_ARCHETYPE" -path "*/spotbugs/published-config/*.config" 2>/dev/null || true
    find "$V6_ARCHETYPE" -path "*/jspanalysis/config.txt" 2>/dev/null || true
} | sort > "$WORK_DIR/files-v6-all.txt"

v6_count=$(wc -l < "$WORK_DIR/files-v6-all.txt")
echo "Found $v6_count v6 files"
echo ""

# Collect v5 files
echo "Collecting v5 files..."
echo ""

V5_DOCS=".lw/nab-official/v5/nablarch-document"
V5_ARCHETYPE=".lw/nab-official/v5/nablarch-single-module-archetype"

{
    find "$V5_DOCS" -name "*.rst" 2>/dev/null || true
    find "$V5_DOCS" -name "*.md" 2>/dev/null || true
    find "$V5_DOCS" -name "config.txt" 2>/dev/null || true
    find "$V5_ARCHETYPE" -name "*.rst" 2>/dev/null || true
    find "$V5_ARCHETYPE" -name "*.md" 2>/dev/null || true
    find "$V5_ARCHETYPE" -name "pom.xml" 2>/dev/null || true
    find "$V5_ARCHETYPE" -path "*/spotbugs/published-config/*.config" 2>/dev/null || true
    find "$V5_ARCHETYPE" -path "*/jspanalysis/config.txt" 2>/dev/null || true
} | sort > "$WORK_DIR/files-v5-all.txt"

v5_count=$(wc -l < "$WORK_DIR/files-v5-all.txt")
echo "Found $v5_count v5 files"
echo ""

# Generate statistics
echo "Generating statistics..."

cat > "$WORK_DIR/stats.md" <<EOF
# File Collection Statistics

**Date**: $(date -Iseconds)

## Nablarch v6

Total files: $v6_count

By file type:
EOF

echo "  - .rst: $(grep '\.rst$' "$WORK_DIR/files-v6-all.txt" | wc -l)" >> "$WORK_DIR/stats.md"
echo "  - .md: $(grep '\.md$' "$WORK_DIR/files-v6-all.txt" | wc -l)" >> "$WORK_DIR/stats.md"
echo "  - .xml: $(grep '\.xml$' "$WORK_DIR/files-v6-all.txt" | wc -l)" >> "$WORK_DIR/stats.md"
echo "  - .config: $(grep '\.config$' "$WORK_DIR/files-v6-all.txt" | wc -l)" >> "$WORK_DIR/stats.md"
echo "  - .txt: $(grep '\.txt$' "$WORK_DIR/files-v6-all.txt" | wc -l)" >> "$WORK_DIR/stats.md"

cat >> "$WORK_DIR/stats.md" <<EOF

By source:
  - nablarch-document: $(grep "nablarch-document" "$WORK_DIR/files-v6-all.txt" | wc -l)
  - nablarch-system-development-guide: $(grep "nablarch-system-development-guide" "$WORK_DIR/files-v6-all.txt" | wc -l)
  - nablarch-single-module-archetype: $(grep "nablarch-single-module-archetype" "$WORK_DIR/files-v6-all.txt" | wc -l)

By language:
  - /en/: $(grep "/en/" "$WORK_DIR/files-v6-all.txt" | wc -l)
  - /ja/: $(grep "/ja/" "$WORK_DIR/files-v6-all.txt" | wc -l)
  - (no lang dir): $(grep -v "/en/" "$WORK_DIR/files-v6-all.txt" | grep -v "/ja/" | wc -l)

## Nablarch v5

Total files: $v5_count

By file type:
EOF

echo "  - .rst: $(grep '\.rst$' "$WORK_DIR/files-v5-all.txt" | wc -l)" >> "$WORK_DIR/stats.md"
echo "  - .md: $(grep '\.md$' "$WORK_DIR/files-v5-all.txt" | wc -l)" >> "$WORK_DIR/stats.md"
echo "  - .xml: $(grep '\.xml$' "$WORK_DIR/files-v5-all.txt" | wc -l)" >> "$WORK_DIR/stats.md"
echo "  - .config: $(grep '\.config$' "$WORK_DIR/files-v5-all.txt" | wc -l)" >> "$WORK_DIR/stats.md"
echo "  - .txt: $(grep '\.txt$' "$WORK_DIR/files-v5-all.txt" | wc -l)" >> "$WORK_DIR/stats.md"

cat >> "$WORK_DIR/stats.md" <<EOF

By source:
  - nablarch-document: $(grep "nablarch-document" "$WORK_DIR/files-v5-all.txt" | wc -l)
  - nablarch-single-module-archetype: $(grep "nablarch-single-module-archetype" "$WORK_DIR/files-v5-all.txt" | wc -l)

By language:
  - /en/: $(grep "/en/" "$WORK_DIR/files-v5-all.txt" | wc -l)
  - /ja/: $(grep "/ja/" "$WORK_DIR/files-v5-all.txt" | wc -l)
  - (no lang dir): $(grep -v "/en/" "$WORK_DIR/files-v5-all.txt" | grep -v "/ja/" | wc -l)
EOF

echo "✅ Created: $WORK_DIR/stats.md"
echo ""

echo "=== Phase 2 Complete ==="
echo ""
echo "Output files:"
echo "  - $WORK_DIR/files-v6-all.txt ($v6_count files)"
echo "  - $WORK_DIR/files-v5-all.txt ($v5_count files)"
echo "  - $WORK_DIR/stats.md"
echo ""
echo "Statistics:"
cat "$WORK_DIR/stats.md"
echo ""
echo "Validation: Run doc/scripts/02-validate-files.sh"
echo "Next step: Run doc/scripts/03-filter-language.sh"
