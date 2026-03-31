#!/bin/bash
# Unit tests for verify_dynamic in test-setup.sh
#
# Tests verify_dynamic logic using mock scripts without actual test environments.
# Covers: normal (pass), 0-hit search, keyword-missing, script-missing,
#         read-sections empty output, version path (v1.4).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_WORKSPACE=$(mktemp -d)
trap 'rm -rf "$TEST_WORKSPACE"' EXIT

# Source test-setup.sh to get the verify_dynamic function
NABLEDGE_TEST_SOURCE_ONLY=1 source "$SCRIPT_DIR/test-setup.sh"

pass=0; fail=0

check() {
    local desc="$1"; local expected="$2"; local actual="$3"
    if [ "$actual" = "$expected" ]; then
        echo "[PASS] $desc"
        pass=$((pass+1))
    else
        echo "[FAIL] $desc"
        echo "       expected: $expected"
        echo "       actual:   $actual"
        fail=$((fail+1))
    fi
}

# Set up globals that verify_dynamic uses
OUTPUT_DIR="$TEST_WORKSPACE"

# ---- Test: normal (search hits, all keywords found) ----
dir="$TEST_WORKSPACE/normal/proj"
scripts_dir="$dir/.claude/skills/nabledge-6/scripts"
mkdir -p "$scripts_dir"
cat > "$scripts_dir/full-text-search.sh" <<'MOCK'
#!/bin/bash
printf 'component/foo.json|s1\n'
MOCK
cat > "$scripts_dir/read-sections.sh" <<'MOCK'
#!/bin/bash
printf '=== component/foo.json : s1 ===\nfindAllBySqlFile page per Pagination getPagination\n=== END ===\n'
MOCK
chmod +x "$scripts_dir/full-text-search.sh" "$scripts_dir/read-sections.sh"

verify_fail=0
normal_output_file=$(mktemp)
verify_dynamic "test/cc" "normal/proj" "6" "findAllBySqlFile,Pagination" "findAllBySqlFile,page,per,Pagination,getPagination" > "$normal_output_file" 2>&1 || true
check "normal: verify_fail=0"        "0" "$verify_fail"
check "normal: output contains [OK]" "1" "$(grep -c '\[OK\]' "$normal_output_file")"
rm -f "$normal_output_file"

# ---- Test: 0-hit (search returns empty) ----
dir="$TEST_WORKSPACE/zerohit/proj"
scripts_dir="$dir/.claude/skills/nabledge-6/scripts"
mkdir -p "$scripts_dir"
cat > "$scripts_dir/full-text-search.sh" <<'MOCK'
#!/bin/bash
printf ''
MOCK
# read-sections.sh is not installed: function should return before calling it
chmod +x "$scripts_dir/full-text-search.sh"

verify_fail=0
zerohit_output_file=$(mktemp)
verify_dynamic "test/cc" "zerohit/proj" "6" "findAllBySqlFile,Pagination" "findAllBySqlFile,page,per,Pagination,getPagination" > "$zerohit_output_file" 2>&1 || true
check "0-hit: verify_fail=1"          "1" "$verify_fail"
check "0-hit: output contains [FAIL]" "1" "$(grep -c '\[FAIL\]' "$zerohit_output_file")"
rm -f "$zerohit_output_file"

# ---- Test: keyword missing in content ----
dir="$TEST_WORKSPACE/kwmiss/proj"
scripts_dir="$dir/.claude/skills/nabledge-6/scripts"
mkdir -p "$scripts_dir"
cat > "$scripts_dir/full-text-search.sh" <<'MOCK'
#!/bin/bash
printf 'component/foo.json|s1\n'
MOCK
cat > "$scripts_dir/read-sections.sh" <<'MOCK'
#!/bin/bash
printf '=== component/foo.json : s1 ===\nfindAllBySqlFile Pagination only partial content\n=== END ===\n'
MOCK
chmod +x "$scripts_dir/full-text-search.sh" "$scripts_dir/read-sections.sh"

verify_fail=0
kwmiss_output_file=$(mktemp)
verify_dynamic "test/cc" "kwmiss/proj" "6" "findAllBySqlFile,Pagination" "findAllBySqlFile,page,per,Pagination,getPagination" > "$kwmiss_output_file" 2>&1 || true
check "keyword-missing: verify_fail=1"         "1" "$verify_fail"
check "keyword-missing: FAIL mentions missing" "1" "$(grep -c 'missing keywords' "$kwmiss_output_file")"
rm -f "$kwmiss_output_file"

# ---- Test: script missing ----
dir="$TEST_WORKSPACE/missing/proj"
mkdir -p "$dir"
# No scripts installed at all

verify_fail=0
missing_output_file=$(mktemp)
verify_dynamic "test/cc" "missing/proj" "6" "findAllBySqlFile,Pagination" "findAllBySqlFile,page,per,Pagination,getPagination" > "$missing_output_file" 2>&1 || true
check "script-missing: verify_fail=1"           "1" "$verify_fail"
check "script-missing: FAIL mentions not found" "1" "$(grep -c 'not found' "$missing_output_file")"
rm -f "$missing_output_file"

# ---- Test: read-sections.sh returns empty content ----
dir="$TEST_WORKSPACE/readempty/proj"
scripts_dir="$dir/.claude/skills/nabledge-6/scripts"
mkdir -p "$scripts_dir"
cat > "$scripts_dir/full-text-search.sh" <<'MOCK'
#!/bin/bash
printf 'component/foo.json|s1\n'
MOCK
cat > "$scripts_dir/read-sections.sh" <<'MOCK'
#!/bin/bash
printf ''
MOCK
chmod +x "$scripts_dir/full-text-search.sh" "$scripts_dir/read-sections.sh"

verify_fail=0
readempty_output_file=$(mktemp)
verify_dynamic "test/cc" "readempty/proj" "6" "findAllBySqlFile,Pagination" "findAllBySqlFile,page,per,Pagination,getPagination" > "$readempty_output_file" 2>&1 || true
check "read-sections empty: verify_fail=1"      "1" "$verify_fail"
check "read-sections empty: FAIL missing kws"   "1" "$(grep -c 'missing keywords' "$readempty_output_file")"
rm -f "$readempty_output_file"

# ---- Test: version 1.4 path construction ----
dir="$TEST_WORKSPACE/v14/proj"
scripts_dir="$dir/.claude/skills/nabledge-1.4/scripts"
mkdir -p "$scripts_dir"
cat > "$scripts_dir/full-text-search.sh" <<'MOCK'
#!/bin/bash
printf 'component/codelist.json|s1\n'
MOCK
cat > "$scripts_dir/read-sections.sh" <<'MOCK'
#!/bin/bash
printf '=== component/codelist.json : s1 ===\nn:codeSelect codeId form\n=== END ===\n'
MOCK
chmod +x "$scripts_dir/full-text-search.sh" "$scripts_dir/read-sections.sh"

verify_fail=0
v14_output_file=$(mktemp)
verify_dynamic "test/cc" "v14/proj" "1.4" "n:codeSelect,codeId" "n:codeSelect,codeId" > "$v14_output_file" 2>&1 || true
check "v1.4 path: verify_fail=0"        "0" "$verify_fail"
check "v1.4 path: output contains [OK]" "1" "$(grep -c '\[OK\]' "$v14_output_file")"
rm -f "$v14_output_file"

echo ""
echo "Results: ${pass} passed, ${fail} failed"
[ "$fail" -eq 0 ]
