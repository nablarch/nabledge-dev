#!/bin/bash
set -e

# Transform nabledge skills from development format to marketplace format
# Usage: ./transform-to-plugin.sh <source-dir> <dest-dir>

SOURCE_DIR="${1:-.}"
DEST_DIR="${2:-nabledge-repo}"

echo "Transforming nabledge skills to marketplace format..."
echo "Source: $SOURCE_DIR"
echo "Destination: $DEST_DIR"

# Validate source directory
if [ ! -d "$SOURCE_DIR/.claude/skills/nabledge-6" ]; then
  echo "Error: Source directory does not contain .claude/skills/nabledge-6"
  exit 1
fi

if [ ! -d "$SOURCE_DIR/.claude/marketplace" ]; then
  echo "Error: Source directory does not contain .claude/marketplace"
  exit 1
fi

# Create marketplace directories
echo "Creating marketplace directory structure..."
mkdir -p "$DEST_DIR/.claude-plugin"
mkdir -p "$DEST_DIR/plugins/nabledge-6/.claude-plugin"
mkdir -p "$DEST_DIR/plugins/nabledge-6/skills/nabledge-6"

# Copy marketplace.json to root
echo "Copying marketplace.json..."
cp "$SOURCE_DIR/.claude/marketplace/.claude-plugin/marketplace.json" "$DEST_DIR/.claude-plugin/"

# Copy marketplace README, CHANGELOG, and LICENSE to root
echo "Copying marketplace README, CHANGELOG, and LICENSE..."
cp "$SOURCE_DIR/.claude/marketplace/README.md" "$DEST_DIR/README.md"
cp "$SOURCE_DIR/.claude/marketplace/CHANGELOG.md" "$DEST_DIR/CHANGELOG.md"
cp "$SOURCE_DIR/.claude/marketplace/LICENSE" "$DEST_DIR/"

# Copy nabledge-6 plugin files
echo "Copying nabledge-6 plugin..."

# Plugin metadata
cp "$SOURCE_DIR/.claude/skills/nabledge-6/plugin/plugin.json" "$DEST_DIR/plugins/nabledge-6/.claude-plugin/"

# Copy skill content (SKILL.md and supporting directories)
cp "$SOURCE_DIR/.claude/skills/nabledge-6/SKILL.md" "$DEST_DIR/plugins/nabledge-6/skills/nabledge-6/"
cp -r "$SOURCE_DIR/.claude/skills/nabledge-6/workflows" "$DEST_DIR/plugins/nabledge-6/skills/nabledge-6/"
cp -r "$SOURCE_DIR/.claude/skills/nabledge-6/assets" "$DEST_DIR/plugins/nabledge-6/skills/nabledge-6/"
cp -r "$SOURCE_DIR/.claude/skills/nabledge-6/knowledge" "$DEST_DIR/plugins/nabledge-6/skills/nabledge-6/"
cp -r "$SOURCE_DIR/.claude/skills/nabledge-6/docs" "$DEST_DIR/plugins/nabledge-6/skills/nabledge-6/"
cp -r "$SOURCE_DIR/.claude/skills/nabledge-6/scripts" "$DEST_DIR/plugins/nabledge-6/skills/nabledge-6/"

# Plugin-specific files
cp "$SOURCE_DIR/.claude/skills/nabledge-6/plugin/README.md" "$DEST_DIR/plugins/nabledge-6/"
cp "$SOURCE_DIR/.claude/skills/nabledge-6/plugin/CHANGELOG.md" "$DEST_DIR/plugins/nabledge-6/"
cp "$SOURCE_DIR/.claude/skills/nabledge-6/plugin/GUIDE-CC.md" "$DEST_DIR/plugins/nabledge-6/"
cp "$SOURCE_DIR/.claude/skills/nabledge-6/plugin/GUIDE-GHC.md" "$DEST_DIR/plugins/nabledge-6/"

# Copy CC-specific command
echo "Copying CC command..."
mkdir -p "$DEST_DIR/plugins/nabledge-6/commands"
cp "$SOURCE_DIR/.claude/commands/n6.md" "$DEST_DIR/plugins/nabledge-6/commands/n6.md"

# Copy GHC-specific .github/prompts directory (whitelist approach)
#
# Why whitelist only .github/prompts?
# - User-facing content: GitHub Copilot prompt files for /n6 skill
# - Excluded: Development infrastructure (.github/workflows, .github/scripts)
#   These are for maintaining the nabledge-dev repository and should not
#   be distributed to end users
# - Security: Whitelist prevents accidental distribution of future dev files
#
# Issue #112: Exclude development infrastructure from plugin distribution
echo "Copying GHC .github/prompts directory..."
if [ -f "$SOURCE_DIR/.github/prompts/n6.prompt.md" ]; then
    mkdir -p "$DEST_DIR/plugins/nabledge-6/.github/prompts"
    # Copy only n6.prompt.md to avoid including unwanted files
    cp "$SOURCE_DIR/.github/prompts/n6.prompt.md" "$DEST_DIR/plugins/nabledge-6/.github/prompts/n6.prompt.md"
    echo "  n6.prompt.md copied"
else
    echo "Warning: .github/prompts/n6.prompt.md not found in source"
fi

# Copy setup scripts to root
echo "Copying setup scripts to root..."
cp "$SOURCE_DIR/tools/setup/setup-6-cc.sh" "$DEST_DIR/"
cp "$SOURCE_DIR/tools/setup/setup-6-ghc.sh" "$DEST_DIR/"

echo "Transformation complete!"
echo ""
echo "Marketplace structure created in: $DEST_DIR"
echo "  - Marketplace: $DEST_DIR/.claude-plugin/marketplace.json"
echo "  - Plugin: $DEST_DIR/plugins/nabledge-6/"
