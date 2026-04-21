#!/bin/bash
# Temporary test script for setup-cc.sh and setup-ghc.sh
# Tests that installed files match expected content (not just exit code)
# See PR #171 review comment by @kiyotis

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
# Use /tmp to avoid being inside the nabledge-dev git repo
# (setup scripts use git rev-parse --show-toplevel for PROJECT_ROOT)
WORK_DIR="/tmp/nabledge-setup-test-$$"
FAKE_NABLEDGE="$WORK_DIR/fake-nabledge"

trap 'rm -rf "$WORK_DIR"' EXIT
PASS=0
FAIL=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

pass() { echo -e "${GREEN}PASS${NC}: $1"; PASS=$((PASS+1)); }
fail() { echo -e "${RED}FAIL${NC}: $1"; FAIL=$((FAIL+1)); }

# ============================================================
# Setup fake nabledge repository
# ============================================================
setup_fake_nabledge() {
    rm -rf "$FAKE_NABLEDGE"
    mkdir -p "$FAKE_NABLEDGE"
    cd "$FAKE_NABLEDGE"
    git init -q
    git checkout -q -b main

    for v in 6 5; do
        # skills directory
        mkdir -p "plugins/nabledge-${v}/skills/nabledge-${v}/knowledge"
        mkdir -p "plugins/nabledge-${v}/skills/nabledge-${v}/workflows"
        echo "# SKILL nabledge-${v}" > "plugins/nabledge-${v}/skills/nabledge-${v}/SKILL.md"
        echo "knowledge file v${v}" > "plugins/nabledge-${v}/skills/nabledge-${v}/knowledge/sample.md"
        echo "workflow file v${v}" > "plugins/nabledge-${v}/skills/nabledge-${v}/workflows/qa.md"

        # CC command
        mkdir -p "plugins/nabledge-${v}/commands"
        echo "# /n${v} command" > "plugins/nabledge-${v}/commands/n${v}.md"

        # GHC prompt
        mkdir -p "plugins/nabledge-${v}/.github/prompts"
        echo "# n${v} prompt" > "plugins/nabledge-${v}/.github/prompts/n${v}.prompt.md"
    done

    git add .
    git commit -q -m "init"
    cd "$REPO_ROOT"
}

# ============================================================
# Helper: run script against a fresh project directory
# ============================================================
run_in_project() {
    local script="$1"
    local project_dir="$2"
    shift 2
    local args=("$@")

    mkdir -p "$project_dir"
    cd "$project_dir"

    NABLEDGE_REPO_URL="file://$FAKE_NABLEDGE" \
    NABLEDGE_REPO="fake/fake-nabledge" \
    NABLEDGE_BRANCH="main" \
        bash "$REPO_ROOT/tools/setup/$script" "${args[@]}" 2>&1

    cd "$REPO_ROOT"
}

# ============================================================
# Assertion helpers
# ============================================================
assert_file_exists() {
    local path="$1" label="$2"
    if [ -f "$path" ]; then
        pass "$label: file exists ($path)"
    else
        fail "$label: file not found ($path)"
    fi
}

assert_dir_exists() {
    local path="$1" label="$2"
    if [ -d "$path" ]; then
        pass "$label: dir exists ($path)"
    else
        fail "$label: dir not found ($path)"
    fi
}

assert_file_contains() {
    local path="$1" pattern="$2" label="$3"
    if [ -f "$path" ] && grep -q "$pattern" "$path"; then
        pass "$label: '$pattern' found in $path"
    else
        fail "$label: '$pattern' not found in $path"
    fi
}

assert_file_not_exists() {
    local path="$1" label="$2"
    if [ ! -e "$path" ]; then
        pass "$label: correctly absent ($path)"
    else
        fail "$label: should not exist ($path)"
    fi
}

assert_exit_nonzero() {
    local code="$1" label="$2"
    if [ "$code" -ne 0 ]; then
        pass "$label: correctly exited with error (code $code)"
    else
        fail "$label: should have exited with error but got code 0"
    fi
}

assert_json_key() {
    local path="$1" key="$2" expected="$3" label="$4"
    local actual
    actual=$(jq -r ".[\"$key\"]" "$path" 2>/dev/null)
    if [ "$actual" = "$expected" ]; then
        pass "$label: $key=$actual"
    else
        fail "$label: $key expected '$expected', got '$actual'"
    fi
}

# ============================================================
# setup-cc.sh tests
# ============================================================
test_cc() {
    local desc="$1" project="$WORK_DIR/project-cc-$2"
    shift 2
    local args=("$@")
    echo ""
    echo "--- [CC] $desc ---"
    run_in_project setup-cc.sh "$project" "${args[@]}"

    # For valid scenarios: verify installed content
    if [[ "$desc" != *"invalid"* ]]; then
        for v in "${EXPECTED_VERSIONS[@]}"; do
            assert_file_exists "$project/.claude/skills/nabledge-${v}/SKILL.md" "$desc: SKILL.md v${v}"
            assert_dir_exists  "$project/.claude/skills/nabledge-${v}/knowledge"  "$desc: knowledge/ v${v}"
            assert_dir_exists  "$project/.claude/skills/nabledge-${v}/workflows"  "$desc: workflows/ v${v}"
            assert_file_contains "$project/.claude/skills/nabledge-${v}/SKILL.md" "SKILL nabledge-${v}" "$desc: SKILL.md content v${v}"
            assert_file_exists "$project/.claude/commands/n${v}.md" "$desc: n${v}.md"
            assert_file_contains "$project/.claude/commands/n${v}.md" "/n${v} command" "$desc: n${v}.md content"
        done
    fi
}

# Initialize fake nabledge repo
setup_fake_nabledge

echo "=============================="
echo "setup-cc.sh tests"
echo "=============================="

EXPECTED_VERSIONS=(6 5)
test_cc "New setup, all versions (default)" "all-default"

EXPECTED_VERSIONS=(6 5)
test_cc "New setup, -v all (explicit)" "all-explicit" -v all

EXPECTED_VERSIONS=(6)
test_cc "New setup, -v 6 only" "v6" -v 6

EXPECTED_VERSIONS=(5)
test_cc "New setup, -v 5 only" "v5" -v 5

EXPECTED_VERSIONS=(6 5)
test_cc "New setup, -v 5,6 (multiple)" "v5v6" -v 5,6

# Re-run on existing (update): verify files are overwritten, not duplicated
echo ""
echo "--- [CC] Re-run on existing setup (update) ---"
PROJECT_RERUN="$WORK_DIR/project-cc-rerun"
mkdir -p "$PROJECT_RERUN"; cd "$PROJECT_RERUN"
NABLEDGE_REPO_URL="file://$FAKE_NABLEDGE" NABLEDGE_REPO="fake/fake-nabledge" NABLEDGE_BRANCH="main" \
    bash "$REPO_ROOT/tools/setup/setup-cc.sh" 2>&1
# Modify a file to verify it gets overwritten
echo "MODIFIED" > "$PROJECT_RERUN/.claude/skills/nabledge-6/SKILL.md"
NABLEDGE_REPO_URL="file://$FAKE_NABLEDGE" NABLEDGE_REPO="fake/fake-nabledge" NABLEDGE_BRANCH="main" \
    bash "$REPO_ROOT/tools/setup/setup-cc.sh" 2>&1
cd "$REPO_ROOT"
assert_file_contains "$PROJECT_RERUN/.claude/skills/nabledge-6/SKILL.md" "SKILL nabledge-6" "Re-run: SKILL.md overwritten correctly"

# Invalid version
echo ""
echo "--- [CC] Invalid version -v 7 ---"
PROJECT_INV="$WORK_DIR/project-cc-invalid"
mkdir -p "$PROJECT_INV"; cd "$PROJECT_INV"
set +e
NABLEDGE_REPO_URL="file://$FAKE_NABLEDGE" NABLEDGE_REPO="fake/fake-nabledge" NABLEDGE_BRANCH="main" \
    bash "$REPO_ROOT/tools/setup/setup-cc.sh" -v 7 2>&1
EXIT_CODE=$?
set -e
cd "$REPO_ROOT"
assert_exit_nonzero "$EXIT_CODE" "Invalid version -v 7"
assert_file_not_exists "$PROJECT_INV/.claude/skills/nabledge-7/SKILL.md" "Invalid version: no nabledge-7 installed"

# ============================================================
# setup-ghc.sh tests
# ============================================================
test_ghc() {
    local desc="$1" project="$WORK_DIR/project-ghc-$2"
    shift 2
    local args=("$@")
    echo ""
    echo "--- [GHC] $desc ---"
    run_in_project setup-ghc.sh "$project" "${args[@]}"

    if [[ "$desc" != *"invalid"* ]]; then
        for v in "${EXPECTED_VERSIONS[@]}"; do
            assert_file_exists "$project/.claude/skills/nabledge-${v}/SKILL.md" "$desc: SKILL.md v${v}"
            assert_dir_exists  "$project/.claude/skills/nabledge-${v}/knowledge"  "$desc: knowledge/ v${v}"
            assert_dir_exists  "$project/.claude/skills/nabledge-${v}/workflows"  "$desc: workflows/ v${v}"
            assert_file_contains "$project/.claude/skills/nabledge-${v}/SKILL.md" "SKILL nabledge-${v}" "$desc: SKILL.md content v${v}"
            assert_file_exists "$project/.github/prompts/n${v}.prompt.md" "$desc: n${v}.prompt.md"
            assert_file_contains "$project/.github/prompts/n${v}.prompt.md" "n${v} prompt" "$desc: prompt content v${v}"
        done
        # settings.json
        assert_file_exists "$project/.vscode/settings.json" "$desc: settings.json created"
        assert_json_key "$project/.vscode/settings.json" "chat.useAgentSkills" "true" "$desc: chat.useAgentSkills=true"
    fi
}

echo ""
echo "=============================="
echo "setup-ghc.sh tests"
echo "=============================="

EXPECTED_VERSIONS=(6 5)
test_ghc "New setup, all versions (default)" "all-default"

EXPECTED_VERSIONS=(6)
test_ghc "New setup, -v 6 only" "v6" -v 6

EXPECTED_VERSIONS=(5)
test_ghc "New setup, -v 5 only" "v5" -v 5

EXPECTED_VERSIONS=(6 5)
test_ghc "New setup, -v 5,6 (multiple)" "v5v6" -v 5,6

# Re-run (update): files overwritten
echo ""
echo "--- [GHC] Re-run on existing setup (update) ---"
PROJECT_GHC_RERUN="$WORK_DIR/project-ghc-rerun"
mkdir -p "$PROJECT_GHC_RERUN"; cd "$PROJECT_GHC_RERUN"
NABLEDGE_REPO_URL="file://$FAKE_NABLEDGE" NABLEDGE_REPO="fake/fake-nabledge" NABLEDGE_BRANCH="main" \
    bash "$REPO_ROOT/tools/setup/setup-ghc.sh" 2>&1
echo "MODIFIED" > "$PROJECT_GHC_RERUN/.claude/skills/nabledge-6/SKILL.md"
NABLEDGE_REPO_URL="file://$FAKE_NABLEDGE" NABLEDGE_REPO="fake/fake-nabledge" NABLEDGE_BRANCH="main" \
    bash "$REPO_ROOT/tools/setup/setup-ghc.sh" 2>&1
cd "$REPO_ROOT"
assert_file_contains "$PROJECT_GHC_RERUN/.claude/skills/nabledge-6/SKILL.md" "SKILL nabledge-6" "Re-run: SKILL.md overwritten correctly"

# settings.json: existing file without chat.useAgentSkills
echo ""
echo "--- [GHC] Existing settings.json without chat.useAgentSkills ---"
PROJECT_GHC_EXISTING="$WORK_DIR/project-ghc-existing-settings"
mkdir -p "$PROJECT_GHC_EXISTING/.vscode"
echo '{"editor.fontSize": 14, "editor.tabSize": 2}' > "$PROJECT_GHC_EXISTING/.vscode/settings.json"
cd "$PROJECT_GHC_EXISTING"
NABLEDGE_REPO_URL="file://$FAKE_NABLEDGE" NABLEDGE_REPO="fake/fake-nabledge" NABLEDGE_BRANCH="main" \
    bash "$REPO_ROOT/tools/setup/setup-ghc.sh" 2>&1
cd "$REPO_ROOT"
assert_json_key "$PROJECT_GHC_EXISTING/.vscode/settings.json" "chat.useAgentSkills" "true" "Existing settings: chat.useAgentSkills added"
assert_json_key "$PROJECT_GHC_EXISTING/.vscode/settings.json" "editor.fontSize" "14" "Existing settings: editor.fontSize preserved"

# settings.json: existing file with chat.useAgentSkills already set (no duplication)
echo ""
echo "--- [GHC] Existing settings.json with chat.useAgentSkills already set ---"
PROJECT_GHC_ALREADY="$WORK_DIR/project-ghc-already-set"
mkdir -p "$PROJECT_GHC_ALREADY/.vscode"
echo '{"chat.useAgentSkills": true, "editor.fontSize": 16}' > "$PROJECT_GHC_ALREADY/.vscode/settings.json"
cd "$PROJECT_GHC_ALREADY"
NABLEDGE_REPO_URL="file://$FAKE_NABLEDGE" NABLEDGE_REPO="fake/fake-nabledge" NABLEDGE_BRANCH="main" \
    bash "$REPO_ROOT/tools/setup/setup-ghc.sh" 2>&1
cd "$REPO_ROOT"
assert_json_key "$PROJECT_GHC_ALREADY/.vscode/settings.json" "chat.useAgentSkills" "true" "Already set: chat.useAgentSkills still true"
assert_json_key "$PROJECT_GHC_ALREADY/.vscode/settings.json" "editor.fontSize" "16" "Already set: editor.fontSize preserved"
# Ensure no duplicate keys (jq returns single value if unique)
KEY_COUNT=$(jq '[to_entries[] | select(.key == "chat.useAgentSkills")] | length' "$PROJECT_GHC_ALREADY/.vscode/settings.json")
if [ "$KEY_COUNT" -eq 1 ]; then
    pass "Already set: no duplicate chat.useAgentSkills key"
else
    fail "Already set: duplicate chat.useAgentSkills key found ($KEY_COUNT)"
fi

# ============================================================
# Summary
# ============================================================
echo ""
echo "=============================="
echo "Results: PASS=$PASS, FAIL=$FAIL"
echo "=============================="
if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
