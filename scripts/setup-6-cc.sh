#!/bin/bash
set -e

# Navigate to repository root (or current directory if not in git repo)
if git rev-parse --show-toplevel &>/dev/null; then
  PROJECT_ROOT="$(git rev-parse --show-toplevel)"
else
  PROJECT_ROOT="$(pwd)"
fi

echo "Setting up Nabledge-6 plugin for Claude Code..."
echo "Project root: $PROJECT_ROOT"

# Configuration
REPO_OWNER="nablarch"
REPO_NAME="nabledge"
BRANCH="main"
MARKETPLACE_NAME="nabledge"
PLUGIN_NAME="nabledge-6"

# Create .claude directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/.claude"

SETTINGS_FILE="$PROJECT_ROOT/.claude/settings.json"

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed."
    echo "Please install jq:"
    echo "  - Ubuntu/Debian: sudo apt-get install jq"
    echo "  - macOS: brew install jq"
    echo "  - Windows (WSL): sudo apt-get install jq"
    exit 1
fi

# Initialize settings.json if it doesn't exist
if [ ! -f "$SETTINGS_FILE" ]; then
    echo "Creating new settings.json..."
    echo '{}' > "$SETTINGS_FILE"
fi

# Read current settings
CURRENT_SETTINGS=$(cat "$SETTINGS_FILE")

# Build marketplace configuration
MARKETPLACE_CONFIG=$(jq -n \
  --arg repo "$REPO_OWNER/$REPO_NAME" \
  --arg branch "$BRANCH" \
  '{
    "source": {
      "source": "github",
      "repo": $repo,
      "ref": $branch
    }
  }')

# Build plugin configuration
PLUGIN_KEY="${PLUGIN_NAME}@${MARKETPLACE_NAME}"

# Merge configurations
UPDATED_SETTINGS=$(echo "$CURRENT_SETTINGS" | jq \
  --arg marketplace_name "$MARKETPLACE_NAME" \
  --argjson marketplace_config "$MARKETPLACE_CONFIG" \
  --arg plugin_key "$PLUGIN_KEY" \
  '
  .extraKnownMarketplaces = (.extraKnownMarketplaces // {}) |
  .extraKnownMarketplaces[$marketplace_name] = $marketplace_config |
  .enabledPlugins = (.enabledPlugins // {}) |
  .enabledPlugins[$plugin_key] = true
  ')

# Write updated settings
echo "$UPDATED_SETTINGS" > "$SETTINGS_FILE"

echo ""
echo "Setup complete! The nabledge-6 plugin configuration has been added to:"
echo "$SETTINGS_FILE"
echo ""
echo "Next steps:"
echo "1. Commit .claude/settings.json to your repository"
echo "2. When team members clone the repository and start Claude Code,"
echo "   they will be prompted to install the marketplace and plugin"
echo ""
echo "You can verify the configuration with:"
echo "  cat $SETTINGS_FILE"
