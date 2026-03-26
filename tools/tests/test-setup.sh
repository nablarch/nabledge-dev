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
#   NABLEDGE_BRANCH  Branch or tag (default: develop)
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

# Download setup scripts once
echo "[Setup] Downloading setup scripts from ${NABLEDGE_BRANCH}..."
SETUP_CC_URL="https://raw.githubusercontent.com/${NABLEDGE_REPO}/${NABLEDGE_BRANCH}/setup-cc.sh"
SETUP_GHC_URL="https://raw.githubusercontent.com/${NABLEDGE_REPO}/${NABLEDGE_BRANCH}/setup-ghc.sh"
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

    # Idempotency: skip if directory already exists and is non-empty
    if [ -d "$target_dir" ] && [ -n "$(ls -A "$target_dir" 2>/dev/null)" ]; then
        echo "[${target_dir}] WARNING: Directory already exists and is non-empty. Skipping."
        echo ""
        return
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

verify_env() {
    local label="$1"
    local skills_dir="${OUTPUT_DIR}/$2"
    if [ -d "$skills_dir" ] && [ -n "$(ls -A "$skills_dir" 2>/dev/null)" ]; then
        echo "  [OK]   ${label}: $(ls "$skills_dir" | tr '\n' ' ')"
    else
        echo "  [FAIL] ${label}: .claude/skills/ not found or empty"
        verify_fail=1
    fi
}

verify_env "v6/test-cc"   "v6/test-cc/nablarch-example-batch/.claude/skills"
verify_env "v6/test-ghc"  "v6/test-ghc/nablarch-example-batch/.claude/skills"
verify_env "v5/test-cc"   "v5/test-cc/nablarch-example-batch/.claude/skills"
verify_env "v5/test-ghc"  "v5/test-ghc/nablarch-example-batch/.claude/skills"
verify_env "v1.4/test-cc"  "v1.4/test-cc/tutorial/.claude/skills"
verify_env "v1.4/test-ghc" "v1.4/test-ghc/tutorial/.claude/skills"
verify_env "all/test-cc"  "all/test-cc/nablarch-example-batch/.claude/skills"
verify_env "all/test-ghc" "all/test-ghc/nablarch-example-batch/.claude/skills"

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
