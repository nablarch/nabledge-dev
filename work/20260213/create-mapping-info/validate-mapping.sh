#!/bin/bash
# Validation script for mapping files

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SUCCESS_COUNT=0
FAILURE_COUNT=0

check() {
    local message="$1"
    if [ "$2" -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $message"
        ((SUCCESS_COUNT++))
    else
        echo -e "${RED}✗${NC} $message"
        ((FAILURE_COUNT++))
    fi
}

echo "======================================"
echo "Mapping Validation"
echo "======================================"
echo ""

# Check 1: All source files are accounted for
echo "1. Checking file coverage..."

V6_ACTUAL=$(jq '.total_files' sources-v6.json)
V6_MAPPED=$(jq '.statistics.total' mapping-v6.json)
V5_ACTUAL=$(jq '.total_files' sources-v5.json)
V5_MAPPED=$(jq '.statistics.total' mapping-v5.json)

if [ "$V6_ACTUAL" -eq "$V6_MAPPED" ]; then
    check "V6: All $V6_ACTUAL source files mapped" 0
else
    check "V6: File count mismatch (actual: $V6_ACTUAL, mapped: $V6_MAPPED)" 1
fi

if [ "$V5_ACTUAL" -eq "$V5_MAPPED" ]; then
    check "V5: All $V5_ACTUAL source files mapped" 0
else
    check "V5: File count mismatch (actual: $V5_ACTUAL, mapped: $V5_MAPPED)" 1
fi

# Check 2: All categories are defined
echo ""
echo "2. Checking category definitions..."

# Get unique categories from mappings
V6_CATS=$(jq -r '.mappings[].categories[]' mapping-v6.json | sort -u)
V6_UNDEFINED=""
for cat in $V6_CATS; do
    if ! jq -e ".categories[] | select(.id == \"$cat\")" categories-v6.json > /dev/null 2>&1; then
        V6_UNDEFINED="$V6_UNDEFINED $cat"
    fi
done

if [ -z "$V6_UNDEFINED" ]; then
    check "V6: All categories defined" 0
else
    check "V6: Undefined categories found:$V6_UNDEFINED" 1
fi

V5_CATS=$(jq -r '.mappings[].categories[]' mapping-v5.json | sort -u)
V5_UNDEFINED=""
for cat in $V5_CATS; do
    if ! jq -e ".categories[] | select(.id == \"$cat\")" categories-v5.json > /dev/null 2>&1; then
        V5_UNDEFINED="$V5_UNDEFINED $cat"
    fi
done

if [ -z "$V5_UNDEFINED" ]; then
    check "V5: All categories defined" 0
else
    check "V5: Undefined categories found:$V5_UNDEFINED" 1
fi

# Check 3: In-scope files have target_files
echo ""
echo "3. Checking in-scope files have targets..."

V6_NO_TARGETS=$(jq '[.mappings[] | select(.in_scope == true and (.target_files | length) == 0)] | length' mapping-v6.json)
V5_NO_TARGETS=$(jq '[.mappings[] | select(.in_scope == true and (.target_files | length) == 0)] | length' mapping-v5.json)

check "V6: In-scope files with targets ($V6_NO_TARGETS files missing targets)" $V6_NO_TARGETS
check "V5: In-scope files with targets ($V5_NO_TARGETS files missing targets)" $V5_NO_TARGETS

# Check 4: Out-of-scope files have reason_for_exclusion
echo ""
echo "4. Checking out-of-scope files have reasons..."

V6_NO_REASON=$(jq '[.mappings[] | select(.in_scope == false and (.reason_for_exclusion == null or .reason_for_exclusion == ""))] | length' mapping-v6.json)
V5_NO_REASON=$(jq '[.mappings[] | select(.in_scope == false and (.reason_for_exclusion == null or .reason_for_exclusion == ""))] | length' mapping-v5.json)

check "V6: Out-of-scope files with reasons ($V6_NO_REASON files missing reasons)" $V6_NO_REASON
check "V5: Out-of-scope files with reasons ($V5_NO_REASON files missing reasons)" $V5_NO_REASON

# Check 5: Statistics match actual counts
echo ""
echo "5. Verifying statistics..."

V6_IN_SCOPE=$(jq '[.mappings[] | select(.in_scope == true)] | length' mapping-v6.json)
V6_OUT_SCOPE=$(jq '[.mappings[] | select(.in_scope == false)] | length' mapping-v6.json)
V6_STAT_IN=$(jq '.statistics.in_scope' mapping-v6.json)
V6_STAT_OUT=$(jq '.statistics.out_of_scope' mapping-v6.json)

if [ "$V6_IN_SCOPE" -eq "$V6_STAT_IN" ] && [ "$V6_OUT_SCOPE" -eq "$V6_STAT_OUT" ]; then
    check "V6: Statistics match (in: $V6_IN_SCOPE, out: $V6_OUT_SCOPE)" 0
else
    check "V6: Statistics mismatch (actual in: $V6_IN_SCOPE, stat: $V6_STAT_IN, actual out: $V6_OUT_SCOPE, stat: $V6_STAT_OUT)" 1
fi

V5_IN_SCOPE=$(jq '[.mappings[] | select(.in_scope == true)] | length' mapping-v5.json)
V5_OUT_SCOPE=$(jq '[.mappings[] | select(.in_scope == false)] | length' mapping-v5.json)
V5_STAT_IN=$(jq '.statistics.in_scope' mapping-v5.json)
V5_STAT_OUT=$(jq '.statistics.out_of_scope' mapping-v5.json)

if [ "$V5_IN_SCOPE" -eq "$V5_STAT_IN" ] && [ "$V5_OUT_SCOPE" -eq "$V5_STAT_OUT" ]; then
    check "V5: Statistics match (in: $V5_IN_SCOPE, out: $V5_OUT_SCOPE)" 0
else
    check "V5: Statistics mismatch (actual in: $V5_IN_SCOPE, stat: $V5_STAT_IN, actual out: $V5_OUT_SCOPE, stat: $V5_STAT_OUT)" 1
fi

# Summary
echo ""
echo "======================================"
echo "Validation Summary"
echo "======================================"
echo -e "${GREEN}✓ Passed: $SUCCESS_COUNT${NC}"
if [ "$FAILURE_COUNT" -gt 0 ]; then
    echo -e "${RED}✗ Failed: $FAILURE_COUNT${NC}"
    echo ""
    echo "Please fix the errors above before proceeding."
    exit 1
else
    echo ""
    echo "All validation checks passed!"
fi
