#!/bin/bash

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd')
model=$(echo "$input" | jq -r '.model.display_name // empty')
context_used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

# Shorten model name (e.g., "Sonnet 4.5" → "S4.5" or "claude-sonnet-4-5-..." → "S4.5")
if [ -n "$model" ]; then
  # Try display name format first: "Sonnet 4.5" → "S4.5"
  short_model=$(echo "$model" | sed -E 's/^([A-Z])[a-z]* ([0-9]+\.[0-9]+).*/\1\2/')

  # If that didn't match, try model ID format: "claude-sonnet-4-5-..." → "S4.5"
  # Use awk for portable case conversion (BSD sed doesn't support \U\E)
  if [ "$short_model" = "$model" ]; then
    short_model=$(echo "$model" | sed -E 's/.*claude-(sonnet|opus|haiku)-([0-9]+)-([0-9]+).*/\1 \2.\3/' | awk '{if (NF==2) print toupper(substr($1,1,1)) $2}')
  fi

  # Fallback: if transformation failed (empty or unchanged), keep original
  if [ -n "$short_model" ] && [ "$short_model" != "$model" ]; then
    model="$short_model"
  fi
fi

# Git branch
git_branch=""
if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
  branch=$(git -C "$cwd" -c core.useBuiltinFSMonitor=false -c core.fsmonitor=false branch --show-current 2>/dev/null)
  [ -n "$branch" ] && git_branch=" ($branch)"
fi

# Context info
context_info=""
[ -n "$context_used" ] && context_info=" [ctx: ${context_used}%]"

# Model info
model_info=""
[ -n "$model" ] && model_info=" [${model}]"

# Output
cwd_name=$(basename "$cwd")
printf "\033[01;34m%s\033[00m%s%s%s" "$cwd_name" "$git_branch" "$model_info" "$context_info"
