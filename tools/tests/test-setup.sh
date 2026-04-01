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
#   v1.3/test-cc/  - nabledge-1.3 x Claude Code
#   v1.3/test-ghc/ - nabledge-1.3 x GitHub Copilot
#   v1.2/test-cc/  - nabledge-1.2 x Claude Code
#   v1.2/test-ghc/ - nabledge-1.2 x GitHub Copilot
#   all/test-cc/  - all versions x Claude Code
#   all/test-ghc/ - all versions x GitHub Copilot
#
# Prerequisites:
#   Run setup.sh first to populate .lw/nab-official/ with source projects.
#   For v1.4, v1.3, and v1.2, also run setup.sh (SVN section) to check out the tutorial project.
#
# Usage:
#   cd /path/to/test-workspace
#   bash /path/to/tools/tests/test-setup.sh [version]
#
# Arguments (optional):
#   version  Version to set up: v6, v5, v1.4, v1.3, v1.2, all (default: run all versions)
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
V13_PROJECT_SRC="${LW_DIR}/v1.3/tutorial"
V12_PROJECT_SRC="${LW_DIR}/v1.2/tutorial"

NABLEDGE_REPO="${NABLEDGE_REPO:-nablarch/nabledge}"
NABLEDGE_BRANCH="${NABLEDGE_BRANCH:-develop}"
NABLEDGE_REPO_URL="https://github.com/${NABLEDGE_REPO}"

VERSION_FILTER="${1:-}"
if [ -n "$VERSION_FILTER" ] && [[ ! "$VERSION_FILTER" =~ ^(v6|v5|v1\.4|v1\.3|v1\.2|all)$ ]]; then
    echo "ERROR: Invalid version '${VERSION_FILTER}'. Valid values: v6, v5, v1.4, v1.3, v1.2, all"
    exit 1
fi

# Returns 0 if the given version label should be processed
should_run() { [ -z "$VERSION_FILTER" ] || [ "$1" = "$VERSION_FILTER" ]; }

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
echo "Version filter:      ${VERSION_FILTER:-all}"
echo ""

# Extract setup script URLs from GUIDE files on NABLEDGE_BRANCH
# This ensures we use the same URL as users, and detects if the URL changes in the guide.
echo "[Setup] Fetching setup script URLs from GUIDE files (branch: ${NABLEDGE_BRANCH})..."
GUIDE_CC_URL="https://raw.githubusercontent.com/${NABLEDGE_REPO}/${NABLEDGE_BRANCH}/plugins/nabledge-6/GUIDE-CC.md"
GUIDE_GHC_URL="https://raw.githubusercontent.com/${NABLEDGE_REPO}/${NABLEDGE_BRANCH}/plugins/nabledge-6/GUIDE-GHC.md"
# Extract script filename from GUIDE (detects filename changes), then replace branch with NABLEDGE_BRANCH
SETUP_CC_FILENAME=$(curl -sSfL "$GUIDE_CC_URL" | grep -m1 'curl -sSL.*setup-cc\.sh' | grep -oP 'setup-cc\.sh')
SETUP_GHC_FILENAME=$(curl -sSfL "$GUIDE_GHC_URL" | grep -m1 'curl -sSL.*setup-ghc\.sh' | grep -oP 'setup-ghc\.sh')
if [ -z "$SETUP_CC_FILENAME" ] || [ -z "$SETUP_GHC_FILENAME" ]; then
    echo "ERROR: Could not extract setup script filenames from GUIDE files."
    echo "  GUIDE-CC.md: ${GUIDE_CC_URL}"
    echo "  GUIDE-GHC.md: ${GUIDE_GHC_URL}"
    exit 1
fi
SETUP_CC_URL="https://raw.githubusercontent.com/${NABLEDGE_REPO}/${NABLEDGE_BRANCH}/${SETUP_CC_FILENAME}"
SETUP_GHC_URL="https://raw.githubusercontent.com/${NABLEDGE_REPO}/${NABLEDGE_BRANCH}/${SETUP_GHC_FILENAME}"
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

    # Run setup script inside the copied project.
    # GIT_CEILING_DIRECTORIES prevents setup scripts from walking up to a parent git repo
    # (e.g. when the project is not a git repo itself, like the v1.4 SVN tutorial project).
    echo "[${target_dir}] Running setup script (version: ${version_flag}, branch: ${NABLEDGE_BRANCH})..."
    (
        cd "$target_dir/$project_name"
        GIT_CEILING_DIRECTORIES="$(dirname "$(pwd)")" NABLEDGE_BRANCH="$NABLEDGE_BRANCH" bash "$setup_script" -v "$version_flag"
    )

    echo "[${target_dir}] Done."
    echo ""
}

# ------------------------------------------------------------
# Set up all 10 environments
# ------------------------------------------------------------

HINT_V6="Run setup.sh to clone .lw/nab-official/v6/nablarch-example-batch."
HINT_V5="Run setup.sh to clone .lw/nab-official/v5/nablarch-example-batch."
HINT_V14="Run setup.sh (SVN section) to check out .lw/nab-official/v1.4/tutorial."
HINT_V13="Run setup.sh (SVN section) to check out .lw/nab-official/v1.3/tutorial."
HINT_V12="Run setup.sh (SVN section) to check out .lw/nab-official/v1.2/tutorial."

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

should_run "v6"   && setup_env "v6/test-cc"    "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-cc.sh"  "6"   "$HINT_V6"
should_run "v6"   && setup_env "v6/test-ghc"   "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-ghc.sh" "6"   "$HINT_V6"
should_run "v5"   && setup_env "v5/test-cc"    "$V5_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-cc.sh"  "5"   "$HINT_V5"
should_run "v5"   && setup_env "v5/test-ghc"   "$V5_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-ghc.sh" "5"   "$HINT_V5"
should_run "v1.4" && setup_env "v1.4/test-cc"  "$V14_PROJECT_SRC" "tutorial"               "$TEMP_DIR/setup-cc.sh"  "1.4" "$HINT_V14"
should_run "v1.4" && setup_env "v1.4/test-ghc" "$V14_PROJECT_SRC" "tutorial"               "$TEMP_DIR/setup-ghc.sh" "1.4" "$HINT_V14"
should_run "v1.3" && setup_env "v1.3/test-cc"  "$V13_PROJECT_SRC" "tutorial"               "$TEMP_DIR/setup-cc.sh"  "1.3" "$HINT_V13"
should_run "v1.3" && setup_env "v1.3/test-ghc" "$V13_PROJECT_SRC" "tutorial"               "$TEMP_DIR/setup-ghc.sh" "1.3" "$HINT_V13"
should_run "v1.2" && setup_env "v1.2/test-cc"  "$V12_PROJECT_SRC" "tutorial"               "$TEMP_DIR/setup-cc.sh"  "1.2" "$HINT_V12"
should_run "v1.2" && setup_env "v1.2/test-ghc" "$V12_PROJECT_SRC" "tutorial"               "$TEMP_DIR/setup-ghc.sh" "1.2" "$HINT_V12"
# "all" uses the v6 project as base; all skill versions are installed by setup-cc.sh (-v all).
should_run "all"  && setup_env "all/test-cc"   "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-cc.sh"  "all" "$HINT_V6"
should_run "all"  && setup_env "all/test-ghc"  "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-ghc.sh" "all" "$HINT_V6"

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

        # command file check (CC only; GHC uses .github/prompts/ instead)
        local cmd_status=""
        if [ "$tool" = "ghc" ]; then
            cmd_status="N/A (GHC)"
        elif [ -f "$cmd_file" ]; then
            cmd_status="ok"
        else
            echo "  [FAIL] ${label} nabledge-${v}: /n${v} command missing"
            fail=1
            cmd_status="FAIL"
        fi

        # GHC prompt file check
        local ghc_status=""
        if [ "$tool" = "ghc" ]; then
            local prompt_file="$project_dir/.github/prompts/n${v}.prompt.md"
            if [ -f "$prompt_file" ]; then
                ghc_status=", prompt ok"
            else
                echo "  [FAIL] ${label} nabledge-${v}: n${v}.prompt.md missing"
                fail=1
                ghc_status=", prompt FAIL"
            fi
        fi

        echo "  [OK]   ${label} nabledge-${v}: SKILL.md ok, knowledge/ ${knowledge_count} files, docs/ ${docs_count} entries, command ${cmd_status}${ghc_status}"
    done

    if [ "$fail" -eq 1 ]; then verify_fail=1; fi
}

# verify_dynamic: deterministic dynamic check by running knowledge search scripts directly
# Executes full-text-search.sh and read-sections.sh to validate knowledge content.
# No LLM or CLI authentication required.
# Args:
#   $1 - label (e.g. "v6/test-cc")
#   $2 - project dir relative to OUTPUT_DIR (e.g. "v6/test-cc/nablarch-example-batch")
#   $3 - nabledge version to query (e.g. "6", "5", "1.4")
#   $4 - comma-separated keywords to search for
verify_dynamic() {
    local label="$1"
    local project_dir="${OUTPUT_DIR}/$2"
    local v="$3"
    local keywords_str="$4"

    # Check jq dependency
    if ! command -v jq &>/dev/null; then
        echo "  [FAIL] ${label} nabledge-${v}: jq not found (required for knowledge search scripts)"
        verify_fail=1
        return
    fi

    # Locate scripts (can be in v6, v5, v1.4, v1.3, or v1.2 directory)
    local search_script="$project_dir/.claude/skills/nabledge-${v}/scripts/full-text-search.sh"
    local read_script="$project_dir/.claude/skills/nabledge-${v}/scripts/read-sections.sh"

    if [ ! -x "$search_script" ]; then
        echo "  [FAIL] ${label} nabledge-${v}: full-text-search.sh not found or not executable"
        verify_fail=1
        return
    fi

    if [ ! -x "$read_script" ]; then
        echo "  [FAIL] ${label} nabledge-${v}: read-sections.sh not found or not executable"
        verify_fail=1
        return
    fi

    echo "  [RUN]  ${label} nabledge-${v}: running deterministic knowledge search..."

    # Search for keywords using full-text-search.sh
    # Convert comma-separated keywords to arguments
    IFS=',' read -ra keywords <<< "$keywords_str"
    local search_results
    search_results=$("$search_script" "${keywords[@]}" 2>/dev/null) || true

    if [ -z "$search_results" ]; then
        echo "  [FAIL] ${label} nabledge-${v}: no search results for keywords: ${keywords[*]}"
        verify_fail=1
        return
    fi

    # Extract file:section pairs and read actual content
    local all_keywords_found=1
    local read_pairs=""
    while IFS='|' read -r file section; do
        if [ -n "$file" ] && [ -n "$section" ]; then
            read_pairs="$read_pairs ${file}:${section}"
        fi
    done <<< "$search_results"

    if [ -z "$read_pairs" ]; then
        echo "  [FAIL] ${label} nabledge-${v}: search returned no valid file:section pairs"
        verify_fail=1
        return
    fi

    # Read section content and verify all keywords are present
    local section_content
    section_content=$("$read_script" $read_pairs 2>/dev/null) || true

    local missing_keywords=()
    for kw in "${keywords[@]}"; do
        if ! echo "$section_content" | grep -qi "$(echo "$kw" | sed 's/[[\.*^$/]/\\&/g')"; then
            missing_keywords+=("$kw")
        fi
    done

    if [ "${#missing_keywords[@]}" -gt 0 ]; then
        echo "  [FAIL] ${label} nabledge-${v}: missing keywords in content: ${missing_keywords[*]}"
        verify_fail=1
    else
        local result_count=$(echo "$search_results" | wc -l)
        echo "  [OK]   ${label} nabledge-${v}: deterministic check ok (${result_count} sections found, all keywords verified)"
    fi
}

echo "[Static checks]"
should_run "v6"   && verify_env "v6/test-cc"    "v6/test-cc/nablarch-example-batch"    "6"               "cc"
should_run "v6"   && verify_env "v6/test-ghc"   "v6/test-ghc/nablarch-example-batch"   "6"               "ghc"
should_run "v5"   && verify_env "v5/test-cc"    "v5/test-cc/nablarch-example-batch"    "5"               "cc"
should_run "v5"   && verify_env "v5/test-ghc"   "v5/test-ghc/nablarch-example-batch"   "5"               "ghc"
should_run "v1.4" && verify_env "v1.4/test-cc"  "v1.4/test-cc/tutorial"                "1.4"             "cc"
should_run "v1.4" && verify_env "v1.4/test-ghc" "v1.4/test-ghc/tutorial"               "1.4"             "ghc"
should_run "v1.3" && verify_env "v1.3/test-cc"  "v1.3/test-cc/tutorial"                "1.3"             "cc"
should_run "v1.3" && verify_env "v1.3/test-ghc" "v1.3/test-ghc/tutorial"               "1.3"             "ghc"
should_run "v1.2" && verify_env "v1.2/test-cc"  "v1.2/test-cc/tutorial"                "1.2"             "cc"
should_run "v1.2" && verify_env "v1.2/test-ghc" "v1.2/test-ghc/tutorial"               "1.2"             "ghc"
should_run "all"  && verify_env "all/test-cc"   "all/test-cc/nablarch-example-batch"   "6,5,1.4,1.3,1.2" "cc"
should_run "all"  && verify_env "all/test-ghc"  "all/test-ghc/nablarch-example-batch"  "6,5,1.4,1.3,1.2" "ghc"

echo ""
echo "[Dynamic checks]"
# Keywords derived from nabledge-test benchmark scenarios (qa-002 for v6/v5, qa-001 for v1.4/v1.3/v1.2)
# verify_dynamic now uses deterministic checks via full-text-search.sh and read-sections.sh
# No LLM or CLI authentication required; runs in CI without credentials
should_run "v6"   && verify_dynamic "v6/test-cc"    "v6/test-cc/nablarch-example-batch"    "6"   "findAllBySqlFile,page,per,Pagination,getPagination"
should_run "v6"   && verify_dynamic "v6/test-ghc"   "v6/test-ghc/nablarch-example-batch"   "6"   "findAllBySqlFile,page,per,Pagination,getPagination"
should_run "v5"   && verify_dynamic "v5/test-cc"    "v5/test-cc/nablarch-example-batch"    "5"   "findAllBySqlFile,page,per,Pagination,getPagination"
should_run "v5"   && verify_dynamic "v5/test-ghc"   "v5/test-ghc/nablarch-example-batch"   "5"   "findAllBySqlFile,page,per,Pagination,getPagination"
should_run "v1.4" && verify_dynamic "v1.4/test-cc"  "v1.4/test-cc/tutorial"                "1.4" "n:codeSelect,codeId"
should_run "v1.4" && verify_dynamic "v1.4/test-ghc" "v1.4/test-ghc/tutorial"               "1.4" "n:codeSelect,codeId"
should_run "v1.3" && verify_dynamic "v1.3/test-cc"  "v1.3/test-cc/tutorial"                "1.3" "n:codeSelect,codeId"
should_run "v1.3" && verify_dynamic "v1.3/test-ghc" "v1.3/test-ghc/tutorial"               "1.3" "n:codeSelect,codeId"
should_run "v1.2" && verify_dynamic "v1.2/test-cc"  "v1.2/test-cc/tutorial"                "1.2" "n:codeSelect,codeId"
should_run "v1.2" && verify_dynamic "v1.2/test-ghc" "v1.2/test-ghc/tutorial"               "1.2" "n:codeSelect,codeId"
should_run "all"  && verify_dynamic "all/test-cc"   "all/test-cc/nablarch-example-batch"   "6"   "findAllBySqlFile,page,per,Pagination,getPagination"
should_run "all"  && verify_dynamic "all/test-cc"   "all/test-cc/nablarch-example-batch"   "5"   "findAllBySqlFile,page,per,Pagination,getPagination"
should_run "all"  && verify_dynamic "all/test-cc"   "all/test-cc/nablarch-example-batch"   "1.4" "n:codeSelect,codeId"
should_run "all"  && verify_dynamic "all/test-cc"   "all/test-cc/nablarch-example-batch"   "1.3" "n:codeSelect,codeId"
should_run "all"  && verify_dynamic "all/test-cc"   "all/test-cc/nablarch-example-batch"   "1.2" "n:codeSelect,codeId"
should_run "all"  && verify_dynamic "all/test-ghc"  "all/test-ghc/nablarch-example-batch"  "6"   "findAllBySqlFile,page,per,Pagination,getPagination"
should_run "all"  && verify_dynamic "all/test-ghc"  "all/test-ghc/nablarch-example-batch"  "5"   "findAllBySqlFile,page,per,Pagination,getPagination"
should_run "all"  && verify_dynamic "all/test-ghc"  "all/test-ghc/nablarch-example-batch"  "1.4" "n:codeSelect,codeId"
should_run "all"  && verify_dynamic "all/test-ghc"  "all/test-ghc/nablarch-example-batch"  "1.3" "n:codeSelect,codeId"
should_run "all"  && verify_dynamic "all/test-ghc"  "all/test-ghc/nablarch-example-batch"  "1.2" "n:codeSelect,codeId"

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
should_run "v6"   && echo "  v6/test-cc/nablarch-example-batch    - nabledge-6 x Claude Code"
should_run "v6"   && echo "  v6/test-ghc/nablarch-example-batch   - nabledge-6 x GitHub Copilot"
should_run "v5"   && echo "  v5/test-cc/nablarch-example-batch    - nabledge-5 x Claude Code"
should_run "v5"   && echo "  v5/test-ghc/nablarch-example-batch   - nabledge-5 x GitHub Copilot"
should_run "v1.4" && echo "  v1.4/test-cc/tutorial                - nabledge-1.4 x Claude Code"
should_run "v1.4" && echo "  v1.4/test-ghc/tutorial               - nabledge-1.4 x GitHub Copilot"
should_run "v1.3" && echo "  v1.3/test-cc/tutorial                - nabledge-1.3 x Claude Code"
should_run "v1.3" && echo "  v1.3/test-ghc/tutorial               - nabledge-1.3 x GitHub Copilot"
should_run "v1.2" && echo "  v1.2/test-cc/tutorial                - nabledge-1.2 x Claude Code"
should_run "v1.2" && echo "  v1.2/test-ghc/tutorial               - nabledge-1.2 x GitHub Copilot"
should_run "all"  && echo "  all/test-cc/nablarch-example-batch   - all versions x Claude Code"
should_run "all"  && echo "  all/test-ghc/nablarch-example-batch  - all versions x GitHub Copilot"
echo "============================================================"
