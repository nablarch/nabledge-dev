#!/bin/bash
# Sort sections by relevance score and filter threshold
# Input: JSON with sections array (stdin or file)
# Output: JSON with sorted, filtered sections (stdout)

set -euo pipefail

# Read input JSON
if [ $# -eq 1 ]; then
  input=$(cat "$1")
else
  input=$(cat)
fi

# Sort by relevance (descending) and filter relevance >= 2
echo "$input" | jq '{
  query: .query,
  keywords: .keywords,
  sections: (.sections | sort_by(-.relevance) | map(select(.relevance >= 2)))
}'
