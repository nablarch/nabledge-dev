#!/bin/bash
# Generate section-level index.toon from knowledge JSON files
# Usage: cd .claude/skills/nabledge-6/knowledge && bash /path/to/regenerate-index.sh
#   or:  bash regenerate-index.sh (if running from .pr/00053/)

set -e

# Determine knowledge directory based on script location
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/index.toon" ]; then
  # Running from knowledge directory
  KNOWLEDGE_DIR="$SCRIPT_DIR"
else
  # Running from .pr/00053/ or elsewhere
  KNOWLEDGE_DIR="$SCRIPT_DIR/../../.claude/skills/nabledge-6/knowledge"
fi

cd "$KNOWLEDGE_DIR"

echo "Generating section-level index.toon..."

# Create jq script for extraction
cat > /tmp/generate_section_index.jq <<'EOF'
# Generate section-level index entries
# Input: knowledge JSON file
# Output: Lines in format "file.json#section_id, hint1 hint2 hint3 ..."

.id as $file_id |
.title as $title |
.index[] |
"\($file_id).json#\(.id), \(.hints | join(" "))"
EOF

# Generate index.toon
{
  echo "# Nabledge-6 Knowledge Index (Section-Level)"
  echo ""
  echo "sections[147,]{reference,hints}:"
  find . -name "*.json" -type f | sort | while read file; do
    jq -r -f /tmp/generate_section_index.jq "$file"
  done | sed 's/^/  /'
} > index.toon

# Count entries
ENTRY_COUNT=$(grep -c "\.json#" index.toon || true)
echo "Generated $ENTRY_COUNT section-level entries"

# Verify format
if grep -q "^sections\[" index.toon; then
  echo "✓ Format verified"
else
  echo "✗ Format error: missing header"
  exit 1
fi

echo "✓ index.toon regenerated successfully"
