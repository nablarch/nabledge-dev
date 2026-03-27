#!/bin/bash
set -e

# ============================================================
# Nabledge Test Environment Setup Script
# ============================================================
#
# Sets up test environments for all version x tool combinations.
#
# Creates the following directories relative to the current directory:
#   v6/test-cc/   - nabledge-6 x Claude Code
#   v6/test-ghc/  - nabledge-6 x GitHub Copilot
#   v5/test-cc/   - nabledge-5 x Claude Code
#   v5/test-ghc/  - nabledge-5 x GitHub Copilot
#   v1.4/test-cc/  - nabledge-1.4 x Claude Code
#   v1.4/test-ghc/ - nabledge-1.4 x GitHub Copilot
#   all/test-cc/  - all versions x Claude Code
#   all/test-ghc/ - all versions x GitHub Copilot
#
# Prerequisites:
#   Run setup.sh first to populate .lw/nab-official/ with source projects.
#   For v1.4, also run setup-svn.sh to check out the tutorial project.
#
# Usage:
#   cd /path/to/test-workspace
#   bash /path/to/tools/tests/test-setup.sh
#
# Environment variables (optional):
#   NABLEDGE_REPO    GitHub repository (default: nablarch/nabledge)
#   NABLEDGE_BRANCH  Branch to install skill content from (default: develop)
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NABLEDGE_DEV_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LW_DIR="${NABLEDGE_DEV_ROOT}/.lw/nab-official"

V6_PROJECT_SRC="${LW_DIR}/v6/nablarch-example-batch"
V5_PROJECT_SRC="${LW_DIR}/v5/nablarch-example-batch"
V14_PROJECT_SRC="${LW_DIR}/v1.4/tutorial/tutorial"

NABLEDGE_REPO="${NABLEDGE_REPO:-nablarch/nabledge}"
NABLEDGE_BRANCH="${NABLEDGE_BRANCH:-develop}"
NABLEDGE_REPO_URL="https://github.com/${NABLEDGE_REPO}"

OUTPUT_DIR="${NABLEDGE_DEV_ROOT}/.tmp/nabledge-test"

# Single temp dir for downloaded setup scripts
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "============================================================"
echo "Nabledge Test Environment Setup"
echo "============================================================"
echo "Nabledge repository: ${NABLEDGE_REPO}"
echo "Nabledge branch:     ${NABLEDGE_BRANCH}"
echo "Output directory:    ${OUTPUT_DIR}"
echo ""

# Extract setup script URLs from GUIDE files on NABLEDGE_BRANCH
# This ensures we use the same URL as users, and detects if the URL changes in the guide.
echo "[Setup] Fetching setup script URLs from GUIDE files (branch: ${NABLEDGE_BRANCH})..."
GUIDE_CC_URL="https://raw.githubusercontent.com/${NABLEDGE_REPO}/${NABLEDGE_BRANCH}/plugins/nabledge-6/GUIDE-CC.md"
GUIDE_GHC_URL="https://raw.githubusercontent.com/${NABLEDGE_REPO}/${NABLEDGE_BRANCH}/plugins/nabledge-6/GUIDE-GHC.md"
SETUP_CC_URL=$(curl -sSfL "$GUIDE_CC_URL" | grep -m1 'curl -sSL.*setup-cc\.sh' | grep -oP 'https://\S+setup-cc\.sh')
SETUP_GHC_URL=$(curl -sSfL "$GUIDE_GHC_URL" | grep -m1 'curl -sSL.*setup-ghc\.sh' | grep -oP 'https://\S+setup-ghc\.sh')
if [ -z "$SETUP_CC_URL" ] || [ -z "$SETUP_GHC_URL" ]; then
    echo "ERROR: Could not extract setup script URLs from GUIDE files."
    echo "  GUIDE-CC.md: ${GUIDE_CC_URL}"
    echo "  GUIDE-GHC.md: ${GUIDE_GHC_URL}"
    exit 1
fi
echo "[Setup] Setup CC script URL:  ${SETUP_CC_URL}"
echo "[Setup] Setup GHC script URL: ${SETUP_GHC_URL}"
curl -sSfL "$SETUP_CC_URL" -o "$TEMP_DIR/setup-cc.sh"
curl -sSfL "$SETUP_GHC_URL" -o "$TEMP_DIR/setup-ghc.sh"
echo "[Setup] Setup scripts downloaded."
echo ""

# ------------------------------------------------------------
# Helper: setup one test environment
#
# Args:
#   $1 - target directory (e.g. "v6/test-cc")
#   $2 - source project directory in .lw/ (e.g. "$V6_PROJECT_SRC")
#   $3 - project directory name inside target (e.g. "nablarch-example-batch")
#   $4 - setup script path (e.g. "$TEMP_DIR/setup-cc.sh")
#   $5 - version flag value for -v (e.g. "6", "5", "1.4", "all")
#   $6 - setup hint shown when source is missing (e.g. "Run setup.sh first")
# ------------------------------------------------------------
setup_env() {
    local target_dir="$1"
    local src_dir="$2"
    local project_name="$3"
    local setup_script="$4"
    local version_flag="$5"
    local setup_hint="$6"

    echo "------------------------------------------------------------"
    echo "[${target_dir}] Setting up..."

    # Pre-flight: verify source project exists
    if [ ! -d "$src_dir" ]; then
        echo "ERROR: Source project not found: ${src_dir}"
        echo "  ${setup_hint}"
        exit 1
    fi

    mkdir -p "$target_dir"

    # Copy source project
    echo "[${target_dir}] Copying ${src_dir}..."
    cp -r "$src_dir" "$target_dir/$project_name"

    # Run setup script inside the copied project
    echo "[${target_dir}] Running setup script (version: ${version_flag}, branch: ${NABLEDGE_BRANCH})..."
    (
        cd "$target_dir/$project_name"
        NABLEDGE_BRANCH="$NABLEDGE_BRANCH" bash "$setup_script" -v "$version_flag"
    )

    echo "[${target_dir}] Done."
    echo ""
}

# ------------------------------------------------------------
# Set up all 8 environments
# ------------------------------------------------------------

HINT_V6="Run setup.sh to clone .lw/nab-official/v6/nablarch-example-batch."
HINT_V5="Run setup.sh to clone .lw/nab-official/v5/nablarch-example-batch."
HINT_V14="Run setup.sh (SVN section) to check out .lw/nab-official/v1.4/tutorial."

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

setup_env "v6/test-cc"   "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-cc.sh"  "6"   "$HINT_V6"
setup_env "v6/test-ghc"  "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-ghc.sh" "6"   "$HINT_V6"
setup_env "v5/test-cc"   "$V5_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-cc.sh"  "5"   "$HINT_V5"
setup_env "v5/test-ghc"  "$V5_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-ghc.sh" "5"   "$HINT_V5"
setup_env "v1.4/test-cc"  "$V14_PROJECT_SRC" "tutorial"               "$TEMP_DIR/setup-cc.sh"  "1.4" "$HINT_V14"
setup_env "v1.4/test-ghc" "$V14_PROJECT_SRC" "tutorial"               "$TEMP_DIR/setup-ghc.sh" "1.4" "$HINT_V14"
# "all" uses the v6 project as base; all skill versions are installed by setup-cc.sh (-v all).
setup_env "all/test-cc"   "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-cc.sh"  "all" "$HINT_V6"
setup_env "all/test-ghc"  "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-ghc.sh" "all" "$HINT_V6"

# ------------------------------------------------------------
# Verification
# ------------------------------------------------------------
echo "============================================================"
echo "Verifying installations..."
echo ""

verify_fail=0

# verify_env: static check for one test environment
# Args:
#   $1 - label (e.g. "v6/test-cc")
#   $2 - project dir relative to OUTPUT_DIR (e.g. "v6/test-cc/nablarch-example-batch")
#   $3 - comma-separated versions installed (e.g. "6", "1.4", "6,5,1.4")
#   $4 - tool type: "cc" or "ghc"
#
# Checks per version:
#   - SKILL.md exists          (detects: setup script failed to copy skill)
#   - knowledge/ exists        (detects: knowledge directory missing entirely)
#   - knowledge/ file count    (detects: empty knowledge directory)
#   - knowledge/ count matches expected from nabledge-dev repo (detects: files missing)
#   - docs/ exists             (detects: docs directory missing entirely)
#   - docs/ entry count matches expected from nabledge-dev repo (detects: entries missing)
#   - /n{v} command file exists (detects: command not installed)
#   - .github/prompts/n{v}.prompt.md (GHC only: detects prompt not installed)
#
# Does NOT detect:
#   - Corrupt or incorrect file contents
#   - Runtime errors during nabledge skill execution
#   - Wrong knowledge file content or missing entries
#   → Use dynamic check (verify_dynamic) for runtime verification
verify_env() {
    local label="$1"
    local project_dir="${OUTPUT_DIR}/$2"
    local versions_str="$3"
    local tool="$4"
    local fail=0

    IFS=',' read -ra versions <<< "$versions_str"
    for v in "${versions[@]}"; do
        local skill_dir="$project_dir/.claude/skills/nabledge-${v}"
        local cmd_file="$project_dir/.claude/commands/n${v}.md"

        if [ ! -f "$skill_dir/SKILL.md" ]; then
            echo "  [FAIL] ${label} nabledge-${v}: SKILL.md not found (skill not installed)"
            fail=1
            continue
        fi

        # knowledge/ check
        local knowledge_dir="$skill_dir/knowledge"
        local knowledge_count=0
        if [ -d "$knowledge_dir" ]; then
            knowledge_count=$(ls "$knowledge_dir" | wc -l)
        else
            echo "  [FAIL] ${label} nabledge-${v}: knowledge/ directory not found"
            fail=1
            continue
        fi

        local expected_knowledge_count
        expected_knowledge_count=$(ls "${NABLEDGE_DEV_ROOT}/.claude/skills/nabledge-${v}/knowledge" 2>/dev/null | wc -l)
        if [ "$knowledge_count" -ne "$expected_knowledge_count" ]; then
            echo "  [FAIL] ${label} nabledge-${v}: knowledge/ has ${knowledge_count} files, expected ${expected_knowledge_count}"
            fail=1
        fi

        # docs/ check
        local docs_dir="$skill_dir/docs"
        local docs_count=0
        if [ -d "$docs_dir" ]; then
            docs_count=$(ls "$docs_dir" | wc -l)
        else
            echo "  [FAIL] ${label} nabledge-${v}: docs/ directory not found"
            fail=1
        fi

        local expected_docs_count
        expected_docs_count=$(ls "${NABLEDGE_DEV_ROOT}/.claude/skills/nabledge-${v}/docs" 2>/dev/null | wc -l)
        if [ -d "$docs_dir" ] && [ "$docs_count" -ne "$expected_docs_count" ]; then
            echo "  [FAIL] ${label} nabledge-${v}: docs/ has ${docs_count} entries, expected ${expected_docs_count}"
            fail=1
        fi

        # command file check
        local cmd_status="ok"
        [ ! -f "$cmd_file" ] && cmd_status="WARN: /n${v} command missing"

        # GHC prompt file check
        local ghc_status=""
        if [ "$tool" = "ghc" ]; then
            local prompt_file="$project_dir/.github/prompts/n${v}.prompt.md"
            if [ -f "$prompt_file" ]; then
                ghc_status=", prompt ok"
            else
                ghc_status=", WARN: n${v}.prompt.md missing"
            fi
        fi

        echo "  [OK]   ${label} nabledge-${v}: SKILL.md ok, knowledge/ ${knowledge_count} files, docs/ ${docs_count} entries, command ${cmd_status}${ghc_status}"
    done

    if [ "$fail" -eq 1 ]; then verify_fail=1; fi
}

# verify_dynamic: dynamic check by running a knowledge search
# CC environments use claude -p; GHC environments use copilot -p.
# Args:
#   $1 - label (e.g. "v6/test-cc")
#   $2 - project dir relative to OUTPUT_DIR (e.g. "v6/test-cc/nablarch-example-batch")
#   $3 - nabledge version to query (e.g. "6", "5", "1.4")
#   $4 - test query to ask nabledge
#   $5 - comma-separated keywords expected in the response
#   $6 - tool type: "cc" or "ghc"
verify_dynamic() {
    local label="$1"
    local project_dir="${OUTPUT_DIR}/$2"
    local v="$3"
    local query="$4"
    local keywords_str="$5"
    local tool="$6"

    if [ "$tool" = "ghc" ]; then
        if ! command -v copilot &>/dev/null; then
            echo "  [FAIL] ${label} nabledge-${v}: copilot CLI not found"
            verify_fail=1
            return
        fi
        echo "  [RUN]  ${label} nabledge-${v}: running knowledge search via copilot -p..."
        local output
        output=$(cd "$project_dir" && copilot -p "nabledge-${v} \"${query}\"" 2>&1) || true
    else
        if ! command -v claude &>/dev/null; then
            echo "  [FAIL] ${label} nabledge-${v}: claude CLI not found"
            verify_fail=1
            return
        fi
        echo "  [RUN]  ${label} nabledge-${v}: running knowledge search via claude -p..."
        local output
        output=$(cd "$project_dir" && claude -p "nabledge-${v} \"${query}\"" 2>&1) || true
    fi

    local byte_count=${#output}
    if [ "$byte_count" -lt 1000 ]; then
        echo "  [FAIL] ${label} nabledge-${v}: dynamic check response too short (${byte_count} bytes, expected >= 1000)"
        verify_fail=1
        return
    fi

    local missing_keywords=()
    IFS=',' read -ra keywords <<< "$keywords_str"
    for kw in "${keywords[@]}"; do
        if ! echo "$output" | grep -q "$kw"; then
            missing_keywords+=("$kw")
        fi
    done

    if [ "${#missing_keywords[@]}" -gt 0 ]; then
        echo "  [FAIL] ${label} nabledge-${v}: dynamic check missing keywords: ${missing_keywords[*]} (output: ${byte_count} bytes)"
        verify_fail=1
    else
        echo "  [OK]   ${label} nabledge-${v}: dynamic check ok (output: ${byte_count} bytes, all keywords found)"
    fi
}

echo "[Static checks]"
verify_env "v6/test-cc"    "v6/test-cc/nablarch-example-batch"    "6"       "cc"
verify_env "v6/test-ghc"   "v6/test-ghc/nablarch-example-batch"   "6"       "ghc"
verify_env "v5/test-cc"    "v5/test-cc/nablarch-example-batch"    "5"       "cc"
verify_env "v5/test-ghc"   "v5/test-ghc/nablarch-example-batch"   "5"       "ghc"
verify_env "v1.4/test-cc"  "v1.4/test-cc/tutorial"                "1.4"     "cc"
verify_env "v1.4/test-ghc" "v1.4/test-ghc/tutorial"               "1.4"     "ghc"
verify_env "all/test-cc"   "all/test-cc/nablarch-example-batch"   "6,5,1.4" "cc"
verify_env "all/test-ghc"  "all/test-ghc/nablarch-example-batch"  "6,5,1.4" "ghc"

echo ""
echo "[Dynamic checks]"
# Queries and keywords derived from nabledge-test benchmark scenarios (qa-002 for v6/v5, qa-001 for v1.4)
verify_dynamic "v6/test-cc"    "v6/test-cc/nablarch-example-batch"    "6"   "UniversalDaoでページング検索を実装するには？" "findAllBySqlFile,page,per,Pagination,getPagination" "cc"
verify_dynamic "v6/test-ghc"   "v6/test-ghc/nablarch-example-batch"   "6"   "UniversalDaoでページング検索を実装するには？" "findAllBySqlFile,page,per,Pagination,getPagination" "ghc"
verify_dynamic "v5/test-cc"    "v5/test-cc/nablarch-example-batch"    "5"   "UniversalDaoでページング検索を実装するには？" "findAllBySqlFile,page,per,Pagination,getPagination" "cc"
verify_dynamic "v5/test-ghc"   "v5/test-ghc/nablarch-example-batch"   "5"   "UniversalDaoでページング検索を実装するには？" "findAllBySqlFile,page,per,Pagination,getPagination" "ghc"
verify_dynamic "v1.4/test-cc"  "v1.4/test-cc/tutorial"                "1.4" "コードリストのプルダウン入力を実装するには？" "n:codeSelect,codeId,コード値" "cc"
verify_dynamic "v1.4/test-ghc" "v1.4/test-ghc/tutorial"               "1.4" "コードリストのプルダウン入力を実装するには？" "n:codeSelect,codeId,コード値" "ghc"
verify_dynamic "all/test-cc"   "all/test-cc/nablarch-example-batch"   "6"   "UniversalDaoでページング検索を実装するには？" "findAllBySqlFile,page,per,Pagination,getPagination" "cc"
verify_dynamic "all/test-cc"   "all/test-cc/nablarch-example-batch"   "5"   "UniversalDaoでページング検索を実装するには？" "findAllBySqlFile,page,per,Pagination,getPagination" "cc"
verify_dynamic "all/test-cc"   "all/test-cc/nablarch-example-batch"   "1.4" "コードリストのプルダウン入力を実装するには？" "n:codeSelect,codeId,コード値" "cc"
verify_dynamic "all/test-ghc"  "all/test-ghc/nablarch-example-batch"  "6"   "UniversalDaoでページング検索を実装するには？" "findAllBySqlFile,page,per,Pagination,getPagination" "ghc"
verify_dynamic "all/test-ghc"  "all/test-ghc/nablarch-example-batch"  "5"   "UniversalDaoでページング検索を実装するには？" "findAllBySqlFile,page,per,Pagination,getPagination" "ghc"
verify_dynamic "all/test-ghc"  "all/test-ghc/nablarch-example-batch"  "1.4" "コードリストのプルダウン入力を実装するには？" "n:codeSelect,codeId,コード値" "ghc"

echo ""
if [ "$verify_fail" -eq 0 ]; then
    echo "All environments verified successfully."
else
    echo "ERROR: Some environments failed verification. See [FAIL] entries above."
    exit 1
fi

# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------
echo "============================================================"
echo "Test environment setup complete!"
echo ""
echo "Output: ${OUTPUT_DIR}"
echo ""
echo "Environments:"
echo "  v6/test-cc/nablarch-example-batch    - nabledge-6 x Claude Code"
echo "  v6/test-ghc/nablarch-example-batch   - nabledge-6 x GitHub Copilot"
echo "  v5/test-cc/nablarch-example-batch    - nabledge-5 x Claude Code"
echo "  v5/test-ghc/nablarch-example-batch   - nabledge-5 x GitHub Copilot"
echo "  v1.4/test-cc/tutorial                - nabledge-1.4 x Claude Code"
echo "  v1.4/test-ghc/tutorial               - nabledge-1.4 x GitHub Copilot"
echo "  all/test-cc/nablarch-example-batch   - all versions x Claude Code"
echo "  all/test-ghc/nablarch-example-batch  - all versions x GitHub Copilot"
echo "============================================================"
