#!/bin/bash
# Extract file hints from index.toon and score against keywords
# Input: JSON with query and keywords (stdin or file)
# Output: JSON with scored files (stdout)

set -euo pipefail

# Read input JSON
if [ $# -eq 1 ]; then
  input=$(cat "$1")
else
  input=$(cat)
fi

# Extract query and keywords
query=$(echo "$input" | jq -r '.query')
l1_keywords=$(echo "$input" | jq -r '.keywords.l1[]' | tr '\n' '|' | sed 's/|$//')
l2_keywords=$(echo "$input" | jq -r '.keywords.l2[]' | tr '\n' '|' | sed 's/|$//')

# Read index.toon and extract files with hints
index_file=".claude/skills/nabledge-6/knowledge/index.toon"

# Parse index.toon: extract title, hints, path for each entry
files_json=$(awk '
BEGIN { in_files=0; }
/^files\[/ { in_files=1; next; }
in_files && /^  [A-Z]/ {
  # Extract title, hints, path
  title=$0
  sub(/^  /, "", title)
  sub(/,.*$/, "", title)

  getline
  hints=$0
  sub(/^  /, "", hints)
  sub(/,$/, "", hints)

  getline
  path=$0
  sub(/^  /, "", path)

  # Output as JSON
  gsub(/"/, "\\\"", title)
  gsub(/"/, "\\\"", hints)
  print "{\"title\":\"" title "\",\"hints\":\"" hints "\",\"path\":\"" path "\"}"
}
' "$index_file" | jq -s .)

# Score each file
echo "$files_json" | jq --arg l1 "$l1_keywords" --arg l2 "$l2_keywords" --arg query "$query" '{
  query: $query,
  keywords: {
    l1: ($l1 | split("|")),
    l2: ($l2 | split("|"))
  },
  files: map({
    path: .path,
    title: .title,
    hints: (.hints | split(" ")),
    score: (
      # L1 keyword matches (score +2 each)
      ([.hints | split(" ")[] | select(. as $hint | ($l1 | split("|")[] | test($hint; "i")))] | length * 2) +
      # L2 keyword matches (score +1 each)
      ([.hints | split(" ")[] | select(. as $hint | ($l2 | split("|")[] | test($hint; "i")))] | length)
    )
  }) | sort_by(-.score) | map(select(.score >= 2))
}'
