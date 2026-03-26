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
# Usage:
#   cd /path/to/test-workspace
#   bash /path/to/tools/tests/test-setup.sh
#
# Environment variables (optional):
#   NABLEDGE_REPO    GitHub repository (default: nablarch/nabledge)
#   NABLEDGE_BRANCH  Branch or tag (default: develop)
# ============================================================

NABLEDGE_REPO="${NABLEDGE_REPO:-nablarch/nabledge}"
NABLEDGE_BRANCH="${NABLEDGE_BRANCH:-develop}"
NABLEDGE_REPO_URL="https://github.com/${NABLEDGE_REPO}"

EXAMPLE_REPO_URL="https://github.com/nablarch/nablarch-example-batch"
EXAMPLE_REPO_V6_BRANCH="main"
EXAMPLE_REPO_V5_BRANCH="v5-main"
EXAMPLE_REPO_V14_BRANCH="v5-main"

# Single temp dir for downloaded setup scripts
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "============================================================"
echo "Nabledge Test Environment Setup"
echo "============================================================"
echo "Nabledge repository: ${NABLEDGE_REPO}"
echo "Nabledge branch:     ${NABLEDGE_BRANCH}"
echo "Output directory:    $(pwd)"
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
#   $2 - example repo branch (e.g. "main" or "v5-main")
#   $3 - setup script path (e.g. "$TEMP_DIR/setup-cc.sh")
#   $4 - version flag value for -v (e.g. "6", "5", "all")
# ------------------------------------------------------------
setup_env() {
    local target_dir="$1"
    local repo_branch="$2"
    local setup_script="$3"
    local version_flag="$4"

    echo "------------------------------------------------------------"
    echo "[${target_dir}] Setting up..."

    # Idempotency: skip if directory already exists and is non-empty
    if [ -d "$target_dir" ] && [ -n "$(ls -A "$target_dir" 2>/dev/null)" ]; then
        echo "[${target_dir}] WARNING: Directory already exists and is non-empty. Skipping."
        echo ""
        return
    fi

    mkdir -p "$target_dir"

    # Clone example repo
    echo "[${target_dir}] Cloning nablarch-example-batch (branch: ${repo_branch})..."
    git clone --depth 1 --branch "$repo_branch" "$EXAMPLE_REPO_URL" "$target_dir/nablarch-example-batch"

    # Run setup script inside the cloned repo
    echo "[${target_dir}] Running setup script (version: ${version_flag}, branch: ${NABLEDGE_BRANCH})..."
    (
        cd "$target_dir/nablarch-example-batch"
        NABLEDGE_BRANCH="$NABLEDGE_BRANCH" bash "$setup_script" -v "$version_flag"
    )

    echo "[${target_dir}] Done."
    echo ""
}

# ------------------------------------------------------------
# Set up all 8 environments
# ------------------------------------------------------------

setup_env "v6/test-cc"   "$EXAMPLE_REPO_V6_BRANCH"  "$TEMP_DIR/setup-cc.sh"  "6"
setup_env "v6/test-ghc"  "$EXAMPLE_REPO_V6_BRANCH"  "$TEMP_DIR/setup-ghc.sh" "6"
setup_env "v5/test-cc"   "$EXAMPLE_REPO_V5_BRANCH"  "$TEMP_DIR/setup-cc.sh"  "5"
setup_env "v5/test-ghc"  "$EXAMPLE_REPO_V5_BRANCH"  "$TEMP_DIR/setup-ghc.sh" "5"
# nabledge-1.4 uses v5-main as base project: no v1.4-specific branch exists in nablarch-example-batch.
setup_env "v1.4/test-cc"  "$EXAMPLE_REPO_V14_BRANCH" "$TEMP_DIR/setup-cc.sh"  "1.4"
setup_env "v1.4/test-ghc" "$EXAMPLE_REPO_V14_BRANCH" "$TEMP_DIR/setup-ghc.sh" "1.4"
# "all" uses v6 repo branch: nabledge-5 and nabledge-1.4 content is installed by the setup script (-v all),
# but nablarch-example-batch only has a v6 (main) branch as the base project.
setup_env "all/test-cc"   "$EXAMPLE_REPO_V6_BRANCH"  "$TEMP_DIR/setup-cc.sh"  "all"
setup_env "all/test-ghc"  "$EXAMPLE_REPO_V6_BRANCH"  "$TEMP_DIR/setup-ghc.sh" "all"

# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------
echo "============================================================"
echo "Test environment setup complete!"
echo ""
echo "Directories created:"
echo "  v6/test-cc/nablarch-example-batch    - nabledge-6 x Claude Code"
echo "  v6/test-ghc/nablarch-example-batch   - nabledge-6 x GitHub Copilot"
echo "  v5/test-cc/nablarch-example-batch    - nabledge-5 x Claude Code"
echo "  v5/test-ghc/nablarch-example-batch   - nabledge-5 x GitHub Copilot"
echo "  v1.4/test-cc/nablarch-example-batch  - nabledge-1.4 x Claude Code"
echo "  v1.4/test-ghc/nablarch-example-batch - nabledge-1.4 x GitHub Copilot"
echo "  all/test-cc/nablarch-example-batch   - all versions x Claude Code"
echo "  all/test-ghc/nablarch-example-batch  - all versions x GitHub Copilot"
echo ""
echo "Verify with:"
echo "  ls v6/test-cc/nablarch-example-batch/.claude/skills/"
echo "  ls v6/test-ghc/nablarch-example-batch/.claude/skills/"
echo "============================================================"
