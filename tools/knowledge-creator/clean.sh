#!/bin/bash
# Clean all generated files (final outputs and intermediate artifacts)

set -e

REPO_ROOT="${1:-$(pwd)/../..}"

echo "=================================================="
echo "Knowledge Creator - Clean Generated Files"
echo "=================================================="
echo ""
echo "Repository: $REPO_ROOT"
echo ""

# Function to remove directory if it exists
remove_if_exists() {
    local path="$1"
    if [ -d "$path" ]; then
        echo "  Removing: $path"
        rm -rf "$path"
    else
        echo "  (not found: $path)"
    fi
}

# Function to remove file if it exists
remove_file_if_exists() {
    local path="$1"
    if [ -f "$path" ]; then
        echo "  Removing: $path"
        rm -f "$path"
    else
        echo "  (not found: $path)"
    fi
}

echo "=== Removing Final Outputs ==="
echo ""

for version in 5 6; do
    echo "Version $version:"
    remove_if_exists "$REPO_ROOT/.claude/skills/nabledge-$version/knowledge"
    remove_if_exists "$REPO_ROOT/.claude/skills/nabledge-$version/docs"
    echo ""
done

echo "=== Removing Intermediate Artifacts ==="
echo ""

for version in 5 6; do
    echo "Version $version logs:"
    remove_if_exists "$REPO_ROOT/tools/knowledge-creator/logs/v$version"
    echo ""
done

echo "=== Summary ==="
echo ""
echo "Removed:"
echo "  - .claude/skills/nabledge-{5,6}/knowledge/"
echo "  - .claude/skills/nabledge-{5,6}/docs/"
echo "  - tools/knowledge-creator/logs/v{5,6}/"
echo ""
echo "Clean complete. Ready for fresh run."
echo ""
