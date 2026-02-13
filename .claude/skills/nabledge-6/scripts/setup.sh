#!/bin/bash
set -e

# Navigate to repository root (or current directory if not in git repo)
if git rev-parse --show-toplevel &>/dev/null; then
  PROJECT_ROOT="$(git rev-parse --show-toplevel)"
else
  PROJECT_ROOT="$(pwd)"
fi

echo "Setting up Nabledge-6 skill for GitHub Copilot..."
echo "Project root: $PROJECT_ROOT"

# Download nabledge-6 plugin from nablarch/nabledge repository
REPO_URL="https://github.com/nablarch/nabledge"
BRANCH="dummy-to"
TEMP_DIR=$(mktemp -d)

echo "Downloading nabledge-6 plugin from $REPO_URL (branch: $BRANCH)..."
cd "$TEMP_DIR"
git clone --depth 1 --filter=blob:none --sparse --branch "$BRANCH" "$REPO_URL"
cd nabledge
git sparse-checkout set plugins/nabledge-6

# Create .claude/skills directory
echo "Creating .claude/skills directory..."
mkdir -p "$PROJECT_ROOT/.claude/skills"

# Copy skills/nabledge-6 directory as-is
echo "Copying nabledge-6 skill to project..."
cp -r "$TEMP_DIR/nabledge/plugins/nabledge-6/skills/nabledge-6" "$PROJECT_ROOT/.claude/skills/"

# Clean up
rm -rf "$TEMP_DIR"

echo ""
echo "Setup complete! The nabledge-6 skill is now available in your project."
echo "Location: $PROJECT_ROOT/.claude/skills/nabledge-6"
echo ""
echo "You can use it with GitHub Copilot by typing '/nabledge-6' in your editor."
