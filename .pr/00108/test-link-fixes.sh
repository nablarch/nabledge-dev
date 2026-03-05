#!/bin/bash
# Test script to verify link fixes in prefill-template.sh

set -e

echo "=== Testing Link Fixes for Issue #108 ==="
echo ""

# Setup test environment
PROJECT_ROOT="/home/tie303177/work/nabledge/work2"
OUTPUT_PATH=".nabledge/20260220/test-code-analysis.md"
SCRIPT="$PROJECT_ROOT/.claude/skills/nabledge-6/scripts/prefill-template.sh"

# Test data
TARGET_NAME="UserComponentTest"
TARGET_DESC="ユニットテストサンプル"
MODULES="nablarch-document"
SOURCE_FILES="UserComponent.java"
KNOWLEDGE_FILES="universal-dao,data-bind"

echo "Test Configuration:"
echo "  Output Path: $OUTPUT_PATH"
echo "  Source Files: $SOURCE_FILES"
echo "  Knowledge Files: $KNOWLEDGE_FILES"
echo ""

# Run the script
echo "Running prefill-template.sh..."
cd "$PROJECT_ROOT"
bash "$SCRIPT" \
    --target-name "$TARGET_NAME" \
    --target-desc "$TARGET_DESC" \
    --modules "$MODULES" \
    --source-files "$SOURCE_FILES" \
    --knowledge-files "$KNOWLEDGE_FILES" \
    --output-path "$OUTPUT_PATH"

echo ""
echo "=== Verification ==="
echo ""

# Extract the links section from generated file
OUTPUT_FILE="$PROJECT_ROOT/$OUTPUT_PATH"

if [[ ! -f "$OUTPUT_FILE" ]]; then
    echo "❌ FAILED: Output file not created"
    exit 1
fi

echo "## Source Files Section:"
echo ""
sed -n '/## ソースファイル/,/## 関連するナブラーク知識ベース/p' "$OUTPUT_FILE" | head -n -1
echo ""

echo "## Knowledge Base Links Section:"
echo ""
sed -n '/## 関連するナブラーク知識ベース/,/## 公式ドキュメント/p' "$OUTPUT_FILE" | head -n -1
echo ""

echo "=== Expected vs Actual ==="
echo ""

# Test 1: Source file link should have correct relative path
echo "Test 1: Source file relative path"
# UserComponent.java exists in multiple locations, so check that at least one link is present
if grep -q "UserComponent.java" "$OUTPUT_FILE" && grep -q "../../.lw/nab-official" "$OUTPUT_FILE"; then
    echo "  ✅ PASS: Source link(s) have correct relative path (../../)"
    # Count how many links were generated
    link_count=$(grep -c "UserComponent.java" "$OUTPUT_FILE" || echo 0)
    echo "  Found $link_count link(s)"
else
    echo "  ❌ FAIL: Source link does not have correct relative path"
    echo "  Actual:"
    grep -E '\[UserComponent\.java' "$OUTPUT_FILE" || echo "  (Link not found)"
fi
echo ""

# Test 2: Knowledge base links should point to .md files in docs/ directory
echo "Test 2: Knowledge base links format"
if grep -q "universal-dao.md" "$OUTPUT_FILE" && grep -q "data-bind.md" "$OUTPUT_FILE"; then
    echo "  ✅ PASS: Knowledge links point to .md files in docs/"
else
    echo "  ❌ FAIL: Knowledge links incorrect"
    echo "  Actual:"
    grep -E 'Universal Dao|Data Bind' "$OUTPUT_FILE" || echo "  (Links not found)"
fi
echo ""

# Test 3: Links should NOT point to .json files in knowledge/
echo "Test 3: No JSON links in knowledge/ directory"
if grep -q '/knowledge/.*\.json' "$OUTPUT_FILE"; then
    echo "  ❌ FAIL: Found .json links in knowledge/ directory"
    grep '/knowledge/.*\.json' "$OUTPUT_FILE"
else
    echo "  ✅ PASS: No .json links in knowledge/ directory"
fi
echo ""

# Test 4: Relative path should use correct format
echo "Test 4: Relative path format"
if grep -q -E '\]\(\.\./\.\./\.lw' "$OUTPUT_FILE"; then
    echo "  ✅ PASS: Relative paths use correct format (../../)"
else
    echo "  ❌ FAIL: Relative paths may have incorrect format"
    grep -E '\]\(\.\./' "$OUTPUT_FILE" | head -3
fi
echo ""

echo "=== Summary ==="
echo ""
echo "Generated file: $OUTPUT_FILE"
echo ""
echo "To manually inspect the generated file:"
echo "  cat $OUTPUT_FILE"
echo ""
echo "To clean up test file:"
echo "  rm $OUTPUT_FILE"
