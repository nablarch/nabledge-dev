#!/bin/bash
# Tests for read-sections.sh
#
# Usage: bash tools/tests/test-read-sections.sh [skill_version]
# Default skill version: nabledge-6

SKILL_VERSION="${1:-nabledge-6}"
SCRIPT=".claude/skills/$SKILL_VERSION/scripts/read-sections.sh"

PASS=0
FAIL=0

assert_contains() {
  local test_name="$1"
  local expected="$2"
  local actual="$3"
  if echo "$actual" | grep -qF "$expected"; then
    echo "[PASS] $test_name"
    PASS=$((PASS + 1))
  else
    echo "[FAIL] $test_name"
    echo "  Expected to contain: $expected"
    echo "  Actual output: $actual"
    FAIL=$((FAIL + 1))
  fi
}

assert_not_contains() {
  local test_name="$1"
  local unexpected="$2"
  local actual="$3"
  if echo "$actual" | grep -qF "$unexpected"; then
    echo "[FAIL] $test_name"
    echo "  Expected NOT to contain: $unexpected"
    echo "  Actual output: $actual"
    FAIL=$((FAIL + 1))
  else
    echo "[PASS] $test_name"
    PASS=$((PASS + 1))
  fi
}

echo "=== test-read-sections.sh ($SKILL_VERSION) ==="

# Find a file with sections:[]
SECTIONS_EMPTY_FILE=$(grep -rl '"sections": \[\]' ".claude/skills/$SKILL_VERSION/knowledge/" | head -1 | sed "s|\.claude/skills/$SKILL_VERSION/knowledge/||")
if [ -z "$SECTIONS_EMPTY_FILE" ]; then
  echo "SKIP: No sections:[] files found in $SKILL_VERSION"
  exit 0
fi

# Find a file with actual sections
SECTIONS_FILE=$(grep -rl '"sections"' ".claude/skills/$SKILL_VERSION/knowledge/" | while read f; do
  count=$(jq '.sections | length' "$f" 2>/dev/null)
  if [ -n "$count" ] && [ "$count" -gt 0 ]; then
    echo "$f" | sed "s|\.claude/skills/$SKILL_VERSION/knowledge/||"
    break
  fi
done)

echo "Using sections:[] file: $SECTIONS_EMPTY_FILE"
echo "Using sections file: $SECTIONS_FILE"
echo ""

# Test 1: sections:[] file returns content (not SECTION_NOT_FOUND)
out1=$(bash "$SCRIPT" "$SECTIONS_EMPTY_FILE:overview" 2>&1)
assert_not_contains "sections:[] file does not return SECTION_NOT_FOUND" "SECTION_NOT_FOUND" "$out1"

# Test 2: sections:[] file returns content field
out2=$(bash "$SCRIPT" "$SECTIONS_EMPTY_FILE:overview" 2>&1)
assert_not_contains "sections:[] file does not return FILE_NOT_FOUND" "FILE_NOT_FOUND" "$out2"

# Test 3: sections:[] file with any section ID returns content
out3=$(bash "$SCRIPT" "$SECTIONS_EMPTY_FILE:any-section-id" 2>&1)
assert_not_contains "sections:[] file with arbitrary section ID does not return SECTION_NOT_FOUND" "SECTION_NOT_FOUND" "$out3"

# Test 4: sections:[] file output contains the title
TITLE=$(jq -r '.title' ".claude/skills/$SKILL_VERSION/knowledge/$SECTIONS_EMPTY_FILE")
out4=$(bash "$SCRIPT" "$SECTIONS_EMPTY_FILE:overview" 2>&1)
assert_contains "sections:[] file output contains page title" "$TITLE" "$out4"

# Test 5: sections:[] file output contains content text
CONTENT_SNIPPET=$(jq -r '.content[0:20]' ".claude/skills/$SKILL_VERSION/knowledge/$SECTIONS_EMPTY_FILE")
out5=$(bash "$SCRIPT" "$SECTIONS_EMPTY_FILE:overview" 2>&1)
assert_contains "sections:[] file output contains content snippet" "$CONTENT_SNIPPET" "$out5"

# Test 6: normal sections file still works (regression)
if [ -n "$SECTIONS_FILE" ]; then
  FIRST_SECTION_ID=$(jq -r '.sections[0].id' ".claude/skills/$SKILL_VERSION/knowledge/$SECTIONS_FILE")
  out6=$(bash "$SCRIPT" "$SECTIONS_FILE:$FIRST_SECTION_ID" 2>&1)
  assert_not_contains "normal sections file still works (no SECTION_NOT_FOUND)" "SECTION_NOT_FOUND" "$out6"
  assert_not_contains "normal sections file still works (no FILE_NOT_FOUND)" "FILE_NOT_FOUND" "$out6"
fi

# Test 7: invalid file still returns FILE_NOT_FOUND
out7=$(bash "$SCRIPT" "nonexistent/file.json:overview" 2>&1)
assert_contains "nonexistent file returns FILE_NOT_FOUND" "FILE_NOT_FOUND" "$out7"

# Test 8: invalid section in file WITH sections returns SECTION_NOT_FOUND
if [ -n "$SECTIONS_FILE" ]; then
  out8=$(bash "$SCRIPT" "$SECTIONS_FILE:nonexistent-section-id" 2>&1)
  assert_contains "invalid section in sections file returns SECTION_NOT_FOUND" "SECTION_NOT_FOUND" "$out8"
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && exit 0 || exit 1
