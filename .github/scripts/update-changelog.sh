#!/bin/bash
set -e
set -u
set -o pipefail

# Append sync entry to CHANGELOG.md with date and commit reference
# Usage: ./update-changelog.sh <changelog-file> <commit-sha> <repo-full-name>

# Validate required parameters
CHANGELOG_FILE="${1:-}"
COMMIT_SHA="${2:-}"
REPO_FULL_NAME="${3:-}"

if [ -z "$CHANGELOG_FILE" ]; then
  echo "Error: Changelog file path required"
  echo "Usage: $0 <changelog-file> <commit-sha> <repo-full-name>"
  exit 1
fi

if [ -z "$COMMIT_SHA" ]; then
  echo "Error: Commit SHA required"
  echo "Usage: $0 <changelog-file> <commit-sha> <repo-full-name>"
  exit 1
fi

if [ -z "$REPO_FULL_NAME" ]; then
  echo "Error: Repository full name required"
  echo "Usage: $0 <changelog-file> <commit-sha> <repo-full-name>"
  exit 1
fi

# Validate changelog file exists
if [ ! -f "$CHANGELOG_FILE" ]; then
  echo "Error: Changelog file does not exist: $CHANGELOG_FILE"
  exit 1
fi

echo "Updating CHANGELOG: $CHANGELOG_FILE"

COMMIT_URL="https://github.com/${REPO_FULL_NAME}/commit/${COMMIT_SHA}"
DATE=$(date +%Y-%m-%d)
TEMP_FILE=$(mktemp)

# Read first line (# Changelog)
head -n 1 "$CHANGELOG_FILE" > "$TEMP_FILE"

# Add new unreleased section using printf
printf "\n## [Unreleased] - %s\n\n### Changed\n- Synced from: %s\n\n" "$DATE" "$COMMIT_URL" >> "$TEMP_FILE"

# Append rest of original file
tail -n +2 "$CHANGELOG_FILE" >> "$TEMP_FILE"

# Replace original file
mv "$TEMP_FILE" "$CHANGELOG_FILE"

echo "CHANGELOG updated successfully"
