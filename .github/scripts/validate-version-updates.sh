#!/bin/bash
set -e
set -u
set -o pipefail

# Validate that version files are updated when non-infrastructure files change
# Usage: ./validate-version-updates.sh

echo "Validating version updates..."

# Get list of changed files
CHANGED_FILES=$(git diff HEAD~1 HEAD --name-only)

# Check if only infrastructure files were changed
INFRA_ONLY=true
while IFS= read -r file; do
  if [[ ! "$file" =~ ^\.github/ ]] && \
     [[ ! "$file" =~ ^\.claude/marketplace ]] && \
     [[ ! "$file" =~ ^\.claude/rules/ ]] && \
     [[ "$file" != *"transform-to-plugin.sh"* ]]; then
    INFRA_ONLY=false
    break
  fi
done <<< "$CHANGED_FILES"

# If non-infrastructure files changed, require version update
if [ "$INFRA_ONLY" = false ]; then
  if ! echo "$CHANGED_FILES" | grep -q "plugin/plugin.json\|plugin/CHANGELOG.md\|marketplace/.claude-plugin/marketplace.json"; then
    echo "Error: plugin.json, CHANGELOG.md, or marketplace.json must be updated before sync"
    exit 1
  fi
  echo "Version files updated - validation passed"
else
  echo "Infrastructure-only changes detected, skipping version validation"
fi

echo "Version validation completed successfully"
