#!/bin/bash
# Test link fixes with different output directory depths

set -e

echo "=== Testing Different Directory Depths ==="
echo ""

PROJECT_ROOT="/home/tie303177/work/nabledge/work2"
SCRIPT="$PROJECT_ROOT/.claude/skills/nabledge-6/scripts/prefill-template.sh"
cd "$PROJECT_ROOT"

# Test data
TARGET_NAME="TestAction"
TARGET_DESC="テスト"
MODULES="test-module"
SOURCE_FILES="src/main/java/Test.java"
KNOWLEDGE_FILES=".claude/skills/nabledge-6/knowledge/features/processing/nablarch-batch.json"

# Test different depths
declare -a DEPTHS=(
    ".nabledge/test.md:../"
    ".nabledge/20260220/test.md:../../"
    ".nabledge/20260220/subdir/test.md:../../../"
    "test.md:"
)

echo "Testing relative path generation for different depths:"
echo ""

for test in "${DEPTHS[@]}"; do
    IFS=':' read -ra PARTS <<< "$test"
    OUTPUT_PATH="${PARTS[0]}"
    EXPECTED="${PARTS[1]}"

    echo "Test: $OUTPUT_PATH"
    echo "  Expected prefix: $EXPECTED"

    # Run script
    bash "$SCRIPT" \
        --target-name "$TARGET_NAME" \
        --target-desc "$TARGET_DESC" \
        --modules "$MODULES" \
        --source-files "$SOURCE_FILES" \
        --knowledge-files "$KNOWLEDGE_FILES" \
        --output-path "$OUTPUT_PATH" > /dev/null 2>&1

    # Extract generated link
    ACTUAL=$(grep -oP '\[Nablarch Batch\]\(\K[^)]+' "$OUTPUT_PATH" || echo "LINK_NOT_FOUND")

    # Check if it starts with expected prefix
    if [[ "$ACTUAL" == "$EXPECTED"* ]]; then
        echo "  ✅ PASS: Generated link starts with $EXPECTED"
    else
        echo "  ❌ FAIL: Expected prefix $EXPECTED but got: $ACTUAL"
    fi

    # Clean up
    rm -f "$OUTPUT_PATH"
    echo ""
done

echo "=== All Depth Tests Complete ==="
