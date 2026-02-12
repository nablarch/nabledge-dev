#!/bin/bash
set -e

# Navigate to repository root
cd "$(git rev-parse --show-toplevel)"

echo "Setting up Nabledge-6 skill for GitHub Copilot..."

# Download .claude directory from nablarch/nabledge repository
REPO_URL="https://github.com/nablarch/nabledge"
TEMP_DIR=$(mktemp -d)

echo "Downloading .claude directory from $REPO_URL..."
cd "$TEMP_DIR"
git clone --depth 1 --filter=blob:none --sparse "$REPO_URL"
cd nabledge
git sparse-checkout set .claude

# Copy .claude directory to project root
echo "Copying .claude directory to project..."
cd -
cp -r "$TEMP_DIR/nabledge/.claude" .

# Clean up
rm -rf "$TEMP_DIR"

echo "Setup complete! The nabledge-6 skill is now available in your project."
echo "You can use it with GitHub Copilot by typing '/nabledge-6' in your editor."
