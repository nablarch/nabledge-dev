#!/bin/bash
# Library: verify_dynamic function for deterministic knowledge search verification
# Source this file to use verify_dynamic() in tests.
#
# Prerequisites:
#   - jq command available
#   - verify_fail variable initialized before calling verify_dynamic
#
# Usage:
#   source lib-verify-dynamic.sh
#   verify_fail=0
#   verify_dynamic "label" "/absolute/path/to/project" "6" "keyword1,keyword2"

# verify_dynamic: deterministic dynamic check by running knowledge search scripts directly
# Executes full-text-search.sh and read-sections.sh to validate knowledge content.
# No LLM or CLI authentication required.
# Args:
#   $1 - label (e.g. "v6/test-cc")
#   $2 - project dir (absolute path)
#   $3 - nabledge version to query (e.g. "6", "5", "1.4")
#   $4 - comma-separated keywords to search for
verify_dynamic() {
    local label="$1"
    local project_dir="$2"
    local v="$3"
    local keywords_str="$4"

    # Check jq dependency
    if ! command -v jq &>/dev/null; then
        echo "  [FAIL] ${label} nabledge-${v}: jq not found (required for knowledge search scripts)"
        verify_fail=1
        return
    fi

    # Locate scripts (can be in v6, v5, v1.4, v1.3, or v1.2 directory)
    local search_script="$project_dir/.claude/skills/nabledge-${v}/scripts/full-text-search.sh"
    local read_script="$project_dir/.claude/skills/nabledge-${v}/scripts/read-sections.sh"

    if [ ! -x "$search_script" ]; then
        echo "  [FAIL] ${label} nabledge-${v}: full-text-search.sh not found or not executable"
        verify_fail=1
        return
    fi

    if [ ! -x "$read_script" ]; then
        echo "  [FAIL] ${label} nabledge-${v}: read-sections.sh not found or not executable"
        verify_fail=1
        return
    fi

    echo "  [RUN]  ${label} nabledge-${v}: running deterministic knowledge search..."

    # Search for keywords using full-text-search.sh
    # Convert comma-separated keywords to arguments
    local old_ifs="$IFS"
    IFS=',' read -ra keywords <<< "$keywords_str"
    IFS="$old_ifs"

    local search_results
    search_results=$("$search_script" "${keywords[@]}" 2>/dev/null) || true

    if [ -z "$search_results" ]; then
        echo "  [FAIL] ${label} nabledge-${v}: no search results for keywords: ${keywords[*]}"
        verify_fail=1
        return
    fi

    # Extract file:section pairs and read actual content
    local read_pairs=()
    old_ifs="$IFS"
    IFS='|'
    while read -r file section; do
        if [ -n "$file" ] && [ -n "$section" ]; then
            read_pairs+=("${file}:${section}")
        fi
    done <<< "$search_results"
    IFS="$old_ifs"

    if [ ${#read_pairs[@]} -eq 0 ]; then
        echo "  [FAIL] ${label} nabledge-${v}: search returned no valid file:section pairs"
        verify_fail=1
        return
    fi

    # Read section content and verify all keywords are present
    local section_content
    section_content=$("$read_script" "${read_pairs[@]}" 2>&1)
    local read_exit=$?
    if [ $read_exit -ne 0 ]; then
        echo "  [FAIL] ${label} nabledge-${v}: read-sections.sh failed: $section_content"
        verify_fail=1
        return
    fi

    local missing_keywords=()
    for kw in "${keywords[@]}"; do
        if ! echo "$section_content" | grep -qiF "$kw"; then
            missing_keywords+=("$kw")
        fi
    done

    if [ "${#missing_keywords[@]}" -gt 0 ]; then
        echo "  [FAIL] ${label} nabledge-${v}: missing keywords in content: ${missing_keywords[*]}"
        verify_fail=1
    else
        local result_count=$(echo "$search_results" | wc -l)
        echo "  [OK]   ${label} nabledge-${v}: deterministic check ok (${result_count} sections found, all keywords verified)"
    fi
}
