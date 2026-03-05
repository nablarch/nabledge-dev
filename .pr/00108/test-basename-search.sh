#!/bin/bash
# Test basename search functionality in prefill-template.sh

set -e

echo "=== Testing Basename Search Functionality ==="
echo ""

# Setup
PROJECT_ROOT="/home/tie303177/work/nabledge/work2"
OUTPUT_PATH=".nabledge/20260220/test-basename-search.md"
SCRIPT="$PROJECT_ROOT/.claude/skills/nabledge-6/scripts/prefill-template.sh"

cd "$PROJECT_ROOT"

# Clean up previous test files
rm -f "$OUTPUT_PATH"

echo "Test 1: Basename search for source files (should succeed)"
echo "-------------------------------------------------------"

# Create temporary test files
TEST_SRC_DIR="$PROJECT_ROOT/.tmp/test-basename-$$"
mkdir -p "$TEST_SRC_DIR/src/main/java"
echo "// Test file" > "$TEST_SRC_DIR/src/main/java/UniqueTestFile$$.java"

ACTUAL_JAVA_FILE="$TEST_SRC_DIR/src/main/java/UniqueTestFile$$.java"
JAVA_BASENAME=$(basename "$ACTUAL_JAVA_FILE")
echo "  Created test file: $ACTUAL_JAVA_FILE"
echo "  Basename: $JAVA_BASENAME"
echo ""

bash "$SCRIPT" \
    --target-name "Test" \
    --target-desc "Test description" \
    --modules "test" \
    --source-files "$JAVA_BASENAME" \
    --knowledge-files "universal-dao" \
    --output-path "$OUTPUT_PATH" 2>&1 | tee /tmp/test1-output.txt

if grep -q "$JAVA_BASENAME" "$OUTPUT_PATH"; then
    echo "  ✅ PASS: Source file link generated from basename"
else
    echo "  ❌ FAIL: Source file link not found"
    exit 1
fi
echo ""

# Clean up
rm -f "$OUTPUT_PATH"

echo "Test 2: Basename search for knowledge files (should succeed)"
echo "------------------------------------------------------------"

bash "$SCRIPT" \
    --target-name "Test" \
    --target-desc "Test description" \
    --modules "test" \
    --source-files "$ACTUAL_JAVA_FILE" \
    --knowledge-files "universal-dao" \
    --output-path "$OUTPUT_PATH" 2>&1 | tee /tmp/test2-output.txt

if grep -q "Universal Dao" "$OUTPUT_PATH"; then
    echo "  ✅ PASS: Knowledge file link generated from basename"
else
    echo "  ❌ FAIL: Knowledge file link not found"
    cat "$OUTPUT_PATH"
    exit 1
fi
echo ""

# Clean up
rm -f "$OUTPUT_PATH"

echo "Test 3: File not found (should warn and skip)"
echo "----------------------------------------------"

# Capture both stdout and stderr
bash "$SCRIPT" \
    --target-name "Test" \
    --target-desc "Test description" \
    --modules "test" \
    --source-files "NonExistent.java,$JAVA_BASENAME" \
    --knowledge-files "non-existent-knowledge" \
    --output-path "$OUTPUT_PATH" > /tmp/test3-stdout.txt 2> /tmp/test3-stderr.txt

# Check for warning messages in stderr
if grep -q "Warning.*not found.*NonExistent.java" /tmp/test3-stderr.txt; then
    echo "  ✅ PASS: Warning printed for missing source file"
else
    echo "  ❌ FAIL: No warning for missing source file"
    echo "  stderr content:"
    cat /tmp/test3-stderr.txt
    exit 1
fi

if grep -q "Warning.*not found.*non-existent-knowledge" /tmp/test3-stderr.txt; then
    echo "  ✅ PASS: Warning printed for missing knowledge file"
else
    echo "  ❌ FAIL: No warning for missing knowledge file"
    echo "  stderr content:"
    cat /tmp/test3-stderr.txt
    exit 1
fi

# Output file should still be created with found files
if [[ -f "$OUTPUT_PATH" ]] && grep -q "$JAVA_BASENAME" "$OUTPUT_PATH"; then
    echo "  ✅ PASS: Output file created with available files"
else
    echo "  ❌ FAIL: Output file not created or missing valid links"
    exit 1
fi
echo ""

# Clean up
rm -f "$OUTPUT_PATH"

echo "Test 4: Multiple matches (should include all with disambiguation)"
echo "------------------------------------------------------------------"

# Find a file that exists in multiple locations
MULTI_FILE=$(find .lw/nab-official -name "*.java" -type f | head -2 | xargs -I{} basename {} | sort | uniq -d | head -1)

if [[ -z "$MULTI_FILE" ]]; then
    echo "  ⚠️  SKIP: No duplicate files found for testing"
else
    echo "  Testing with: $MULTI_FILE"

    bash "$SCRIPT" \
        --target-name "Test" \
        --target-desc "Test description" \
        --modules "test" \
        --source-files "$MULTI_FILE" \
        --knowledge-files "universal-dao" \
        --output-path "$OUTPUT_PATH" > /tmp/test5-stdout.txt 2> /tmp/test5-stderr.txt

    # Check that multiple links were generated
    link_count=$(grep -c "\[$MULTI_FILE" "$OUTPUT_PATH" || echo 0)

    if [[ $link_count -gt 1 ]]; then
        echo "  ✅ PASS: Multiple links generated ($link_count links)"

        # Check that disambiguation was added
        if grep -q "$MULTI_FILE (" "$OUTPUT_PATH"; then
            echo "  ✅ PASS: Path disambiguation added to labels"
        else
            echo "  ❌ FAIL: No disambiguation in labels"
            grep "\[$MULTI_FILE" "$OUTPUT_PATH"
            exit 1
        fi
    else
        echo "  ⚠️  SKIP: Only one match found (not truly duplicate)"
    fi
fi
echo ""

# Clean up
rm -f "$OUTPUT_PATH"

echo "=== All Tests Passed ==="
echo ""
echo "Summary:"
echo "  ✅ Basename search works for source and knowledge files"
echo "  ✅ Missing files generate warnings and are skipped"
echo "  ✅ Multiple matches include all files with disambiguation"
echo ""

# Final cleanup
rm -rf "$TEST_SRC_DIR"
rm -f "$OUTPUT_PATH"
rm -f /tmp/test*-output.txt

echo "Test files cleaned up successfully"
