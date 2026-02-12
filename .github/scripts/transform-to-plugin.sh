#!/bin/bash
set -e

# Transform nabledge-6 skill from development format to plugin format
# Usage: ./transform-to-plugin.sh <source-dir> <dest-dir>

SOURCE_DIR="${1:-.}"
DEST_DIR="${2:-nabledge-repo}"

echo "Transforming nabledge-6 skill to plugin format..."
echo "Source: $SOURCE_DIR"
echo "Destination: $DEST_DIR"

# Validate source directory
if [ ! -d "$SOURCE_DIR/.claude/skills/nabledge-6" ]; then
  echo "Error: Source directory does not contain .claude/skills/nabledge-6"
  exit 1
fi

# Create plugin directories
echo "Creating plugin directory structure..."
mkdir -p "$DEST_DIR/.claude-plugin"
mkdir -p "$DEST_DIR/skills/nabledge-6"

# Move SKILL.md to skills/nabledge-6/
echo "Copying SKILL.md..."
cp "$SOURCE_DIR/.claude/skills/nabledge-6/SKILL.md" "$DEST_DIR/skills/nabledge-6/"

# Move supporting directories to root
echo "Copying workflows..."
cp -r "$SOURCE_DIR/.claude/skills/nabledge-6/workflows" "$DEST_DIR/"

echo "Copying assets..."
cp -r "$SOURCE_DIR/.claude/skills/nabledge-6/assets" "$DEST_DIR/"

echo "Copying knowledge..."
cp -r "$SOURCE_DIR/.claude/skills/nabledge-6/knowledge" "$DEST_DIR/"

echo "Copying docs..."
cp -r "$SOURCE_DIR/.claude/skills/nabledge-6/docs" "$DEST_DIR/"

# Move plugin files to root
echo "Copying plugin files..."
cp "$SOURCE_DIR/.claude/skills/nabledge-6/plugin/plugin.json" "$DEST_DIR/.claude-plugin/"
cp "$SOURCE_DIR/.claude/skills/nabledge-6/plugin/README.md" "$DEST_DIR/"
cp "$SOURCE_DIR/.claude/skills/nabledge-6/plugin/LICENSE" "$DEST_DIR/"
cp "$SOURCE_DIR/.claude/skills/nabledge-6/plugin/CHANGELOG.md" "$DEST_DIR/"

echo "Transformation complete!"
echo ""
echo "Plugin structure created in: $DEST_DIR"
