#!/bin/bash
# Unit tests for verify_dynamic function
#
# Tests the actual verify_dynamic() function from lib-verify-dynamic.sh.
# Uses production scripts (full-text-search.sh / read-sections.sh) with
# test knowledge files to verify the complete pipeline.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NABLEDGE_DEV_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Source the function under test
source "${SCRIPT_DIR}/lib-verify-dynamic.sh"

# Create temporary test workspace
TEST_WORKSPACE=$(mktemp -d)
trap 'rm -rf "$TEST_WORKSPACE"' EXIT

# Initialize test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test output format
test_case() {
    local name="$1"
    echo ""
    echo "==== Test: $name ===="
    ((TESTS_RUN++))
}

pass() {
    echo "✓ PASS"
    ((TESTS_PASSED++))
}

fail() {
    local reason="$1"
    echo "✗ FAIL: $reason"
    ((TESTS_FAILED++))
}

# Helper: Create test project with production scripts and optional knowledge files
# Args:
#   $1 - version (e.g. "6")
#   $2 - content type: "paging" | "codelist" | "empty"
setup_project() {
    local version="$1"
    local content_type="$2"
    local unique_id="${RANDOM}"

    local project_dir="${TEST_WORKSPACE}/project-${version}-${content_type}-${unique_id}"
    local skill_dir="${project_dir}/.claude/skills/nabledge-${version}"
    local knowledge_dir="${skill_dir}/knowledge"
    local scripts_dir="${skill_dir}/scripts"

    mkdir -p "$knowledge_dir" "$scripts_dir"

    # Copy PRODUCTION scripts from repository (not mocks)
    cp "${NABLEDGE_DEV_ROOT}/.claude/skills/nabledge-6/scripts/full-text-search.sh" "$scripts_dir/"
    cp "${NABLEDGE_DEV_ROOT}/.claude/skills/nabledge-6/scripts/read-sections.sh" "$scripts_dir/"
    chmod +x "$scripts_dir/"*.sh

    case "$content_type" in
        paging)
            cat > "$knowledge_dir/universal-dao.json" <<'EOF'
{
  "sections": {
    "paging": "UniversalDao#per メソッドと UniversalDao#page メソッドでページングが使用可能。findAllBySqlFile で検索し、Pagination オブジェクトを getPagination で取得する。"
  }
}
EOF
            ;;
        codelist)
            cat > "$knowledge_dir/codelist.json" <<'EOF'
{
  "sections": {
    "input": "n:codeSelect タグで codeId を指定してプルダウン入力を実装する。コードリストからの値選択。"
  }
}
EOF
            ;;
        empty)
            # No knowledge files
            ;;
    esac

    echo "$project_dir"
}

# ===== Tests =====

# Test 1: 正常系 - 全キーワードが見つかる
test_case "Normal case: all keywords found → [OK]"
PROJECT=$(setup_project "6" "paging")
verify_fail=0
verify_dynamic "test/normal" "$PROJECT" "6" "findAllBySqlFile,page,per,Pagination,getPagination"
# After calling verify_dynamic (not in subshell), check verify_fail
if [ "$verify_fail" -eq 0 ]; then
    pass
else
    fail "Expected verify_fail=0"
fi

# Test 2: 異常系 - 知識ファイルなし（検索結果ゼロ）
test_case "Zero hits: empty knowledge dir → [FAIL]"
PROJECT=$(setup_project "6" "empty")
verify_fail=0
verify_dynamic "test/empty" "$PROJECT" "6" "findAllBySqlFile"
if [ "$verify_fail" -eq 1 ]; then
    pass
else
    fail "Expected verify_fail=1"
fi

# Test 3: 異常系 - キーワードが内容に含まれない
test_case "Missing keyword: keyword not in content → [FAIL]"
PROJECT=$(setup_project "6" "paging")
verify_fail=0
verify_dynamic "test/missing-kw" "$PROJECT" "6" "findAllBySqlFile,NONEXISTENT_KEYWORD_XYZ"
if [ "$verify_fail" -eq 1 ]; then
    pass
else
    fail "Expected verify_fail=1"
fi

# Test 4: 異常系 - スクリプトが存在しない
test_case "Missing scripts: no search script → [FAIL]"
BAD_PROJECT="${TEST_WORKSPACE}/no-scripts-${RANDOM}"
mkdir -p "$BAD_PROJECT/.claude/skills/nabledge-6/scripts"
verify_fail=0
verify_dynamic "test/no-script" "$BAD_PROJECT" "6" "anything"
if [ "$verify_fail" -eq 1 ]; then
    pass
else
    fail "Expected verify_fail=1"
fi

# Test 5: 正常系 - コロン含みキーワード (n:codeSelect)
test_case "Colon in keyword: n:codeSelect,codeId → [OK]"
PROJECT=$(setup_project "6" "codelist")
verify_fail=0
verify_dynamic "test/colon" "$PROJECT" "6" "n:codeSelect,codeId"
if [ "$verify_fail" -eq 0 ]; then
    pass
else
    fail "Expected verify_fail=0"
fi

# Test 6: 結合テスト - 複数セクション → キーワード検証パイプライン
test_case "Integration: multi-section search → read → keyword verify pipeline"
PROJECT=$(setup_project "6" "paging")
cat > "$PROJECT/.claude/skills/nabledge-6/knowledge/another.json" <<'EOF'
{
  "sections": {
    "extra": "This section also contains per and page references for UniversalDao."
  }
}
EOF
verify_fail=0
verify_dynamic "test/multi" "$PROJECT" "6" "per,page"
if [ "$verify_fail" -eq 0 ]; then
    pass
else
    fail "Expected verify_fail=0"
fi

# Test 7: jq 依存チェック
test_case "Dependency: jq available"
if command -v jq &>/dev/null; then
    pass
else
    fail "jq not found (required for all tests)"
fi

# Print summary
echo ""
echo "======================================"
echo "Test Summary"
echo "======================================"
echo "Tests run:    $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo ""

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo "✓ All tests passed"
    exit 0
else
    echo "✗ Some tests failed"
    exit 1
fi
