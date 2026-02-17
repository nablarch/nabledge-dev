#!/bin/bash
# Test script for Issue #27 - nabledge-6 plugin recognition on first startup
# This script verifies that the direct skill copy method works correctly

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEST_BASE_DIR="/tmp/nabledge-test-issue-27-$$"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Test: Issue #27 - Plugin Recognition"
echo "=========================================="
echo ""

# Function to check if skill is recognized (SKILL.md exists)
check_skill_recognition() {
    local test_dir="$1"
    local test_name="$2"

    if [ -f "$test_dir/.claude/skills/nabledge-6/SKILL.md" ]; then
        echo -e "${GREEN}✅${NC} $test_name: Skill immediately available (SKILL.md exists)"
        return 0
    else
        echo -e "${YELLOW}⚠️${NC}  $test_name: Skill NOT immediately available (SKILL.md not found)"
        return 1
    fi
}

# Function to check if marketplace config exists (old method)
check_marketplace_config() {
    local test_dir="$1"
    local test_name="$2"

    if [ -f "$test_dir/.claude/settings.json" ] && grep -q "extraKnownMarketplaces" "$test_dir/.claude/settings.json" 2>/dev/null; then
        echo -e "${YELLOW}⚠️${NC}  $test_name: Marketplace configuration found (old method)"
        return 0
    else
        echo -e "${GREEN}✅${NC} $test_name: No marketplace configuration (new method)"
        return 1
    fi
}

# Create test base directory
mkdir -p "$TEST_BASE_DIR"
echo "Test directory: $TEST_BASE_DIR"
echo ""

# Test 1: Old method (marketplace configuration)
# This would have been created by the old setup-6-cc.sh
echo "=========================================="
echo "Test 1: Old Method (Marketplace Config)"
echo "=========================================="
OLD_METHOD_DIR="$TEST_BASE_DIR/old-method"
mkdir -p "$OLD_METHOD_DIR"
cd "$OLD_METHOD_DIR"

# Simulate old method: create settings.json with marketplace config
mkdir -p .claude
cat > .claude/settings.json << 'EOF'
{
  "extraKnownMarketplaces": {
    "nabledge": {
      "source": {
        "source": "github",
        "repo": "nablarch/nabledge",
        "ref": "main"
      }
    }
  },
  "enabledPlugins": {
    "nabledge-6@nabledge": true
  }
}
EOF

echo "Created marketplace configuration in .claude/settings.json"
echo ""

# Check if skill is recognized
OLD_METHOD_RESULT=1
if check_skill_recognition "$OLD_METHOD_DIR" "Old method"; then
    OLD_METHOD_RESULT=0
fi

# Check if marketplace config exists
if check_marketplace_config "$OLD_METHOD_DIR" "Old method"; then
    echo "  → This is expected for the old method (marketplace config)"
fi

echo ""

# Test 2: New method (direct skill copy)
# This uses the updated setup-6-cc.sh
echo "=========================================="
echo "Test 2: New Method (Direct Skill Copy)"
echo "=========================================="
NEW_METHOD_DIR="$TEST_BASE_DIR/new-method"
mkdir -p "$NEW_METHOD_DIR"
cd "$NEW_METHOD_DIR"

# Run the updated setup script
echo "Running updated setup-6-cc.sh..."
echo ""

# Initialize as git repo (setup script expects git repo)
git init > /dev/null 2>&1

# Capture setup output for debugging
SETUP_OUTPUT_FILE="$TEST_BASE_DIR/setup-output.log"

# Run setup script from within test directory with environment overrides
cd "$NEW_METHOD_DIR"
if NABLEDGE_REPO="nablarch/nabledge" NABLEDGE_BRANCH="main" bash "$SCRIPT_DIR/setup-6-cc.sh" > "$SETUP_OUTPUT_FILE" 2>&1; then
    echo "Setup script completed successfully"
    echo "(See $SETUP_OUTPUT_FILE for full output)"
else
    echo -e "${RED}❌${NC} Setup script failed"
    echo ""
    echo "Setup output:"
    cat "$SETUP_OUTPUT_FILE"
    exit 1
fi

echo ""

# Check if skill is recognized
NEW_METHOD_RESULT=1
if check_skill_recognition "$NEW_METHOD_DIR" "New method"; then
    NEW_METHOD_RESULT=0
fi

# Check if marketplace config exists
if ! check_marketplace_config "$NEW_METHOD_DIR" "New method"; then
    echo "  → This is expected for the new method (direct copy)"
fi

echo ""

# Additional verification for new method
echo "Additional verification:"
if [ -d "$NEW_METHOD_DIR/.claude/skills/nabledge-6" ]; then
    echo -e "${GREEN}✅${NC} .claude/skills/nabledge-6/ directory exists"

    if [ -f "$NEW_METHOD_DIR/.claude/skills/nabledge-6/SKILL.md" ]; then
        echo -e "${GREEN}✅${NC} SKILL.md file exists"
    else
        echo -e "${RED}❌${NC} SKILL.md file missing"
    fi

    if [ -d "$NEW_METHOD_DIR/.claude/skills/nabledge-6/knowledge" ]; then
        echo -e "${GREEN}✅${NC} knowledge/ directory exists"
    else
        echo -e "${RED}❌${NC} knowledge/ directory missing"
    fi

    if [ -d "$NEW_METHOD_DIR/.claude/skills/nabledge-6/workflows" ]; then
        echo -e "${GREEN}✅${NC} workflows/ directory exists"
    else
        echo -e "${RED}❌${NC} workflows/ directory missing"
    fi
else
    echo -e "${RED}❌${NC} .claude/skills/nabledge-6/ directory does not exist"
    NEW_METHOD_RESULT=1
fi

echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""

if [ $OLD_METHOD_RESULT -eq 0 ]; then
    echo -e "Old method (marketplace): ${GREEN}✅ PASS${NC} (unexpected - skill immediately available)"
else
    echo -e "Old method (marketplace): ${YELLOW}⚠️  EXPECTED${NC} (skill not immediately available)"
fi

if [ $NEW_METHOD_RESULT -eq 0 ]; then
    echo -e "New method (direct copy): ${GREEN}✅ PASS${NC} (skill immediately available)"
else
    echo -e "New method (direct copy): ${RED}❌ FAIL${NC} (skill not immediately available)"
fi

echo ""
echo "Test directories preserved for inspection:"
echo "  Old method: $OLD_METHOD_DIR"
echo "  New method: $NEW_METHOD_DIR"
echo ""

# Exit with appropriate code
if [ $NEW_METHOD_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Fix confirmed working${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Fix not working as expected${NC}"
    echo ""
    exit 1
fi
