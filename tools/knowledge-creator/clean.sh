#!/bin/bash
# Clean all generated files (final outputs and intermediate artifacts)

set -e

# Detect repository root
if [ -f "tools/knowledge-creator/run.py" ]; then
    # Running from repository root
    REPO_ROOT="$(pwd)"
elif [ -f "run.py" ]; then
    # Running from tools/knowledge-creator directory
    REPO_ROOT="$(cd ../.. && pwd)"
else
    # Use provided argument or fail
    if [ -n "$1" ]; then
        REPO_ROOT="$1"
    else
        echo "Error: Cannot detect repository root. Please run from repository root or tools/knowledge-creator/"
        exit 1
    fi
fi

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
