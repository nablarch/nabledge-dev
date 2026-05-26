#!/bin/bash
set -e

# ============================================================
# Nabledge Test Environment Setup Script
# ============================================================
#
# Sets up test environments for all version x tool combinations.
#
# Creates the following directories relative to the current directory:
#   v6/test-cc/   - nabledge-6 x Claude Code
#   v6/test-ghc/  - nabledge-6 x GitHub Copilot
#   v5/test-cc/   - nabledge-5 x Claude Code
#   v5/test-ghc/  - nabledge-5 x GitHub Copilot
#   v1.4/test-cc/  - nabledge-1.4 x Claude Code
#   v1.4/test-ghc/ - nabledge-1.4 x GitHub Copilot
#   v1.3/test-cc/  - nabledge-1.3 x Claude Code
#   v1.3/test-ghc/ - nabledge-1.3 x GitHub Copilot
#   v1.2/test-cc/  - nabledge-1.2 x Claude Code
#   v1.2/test-ghc/ - nabledge-1.2 x GitHub Copilot
#   upgrade/test-cc/  - nabledge-6+5 x Claude Code (version upgrade scenario)
#   upgrade/test-ghc/ - nabledge-1.4+5 x GitHub Copilot (version upgrade scenario)
#
# Prerequisites:
#   Run setup.sh first to populate .lw/nab-official/ with source projects.
#   For v1.4, v1.3, and v1.2, the setup will use the v6 nablarch-example-batch as the base project.
#
# Usage:
#   cd /path/to/test-workspace
#   bash /path/to/tools/tests/test-setup.sh [version]
#
# Arguments (optional):
#   version  Version to set up: v6, v5, v1.4, v1.3, v1.2, upgrade (default: run all versions)
#
# Environment variables (optional):
#   NABLEDGE_REPO    GitHub repository (default: nablarch/nabledge)
#   NABLEDGE_BRANCH  Branch to install skill content from (default: develop)
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NABLEDGE_DEV_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LW_DIR="${NABLEDGE_DEV_ROOT}/.lw/nab-official"

V6_PROJECT_SRC="${LW_DIR}/v6/nablarch-example-batch"
V5_PROJECT_SRC="${LW_DIR}/v5/nablarch-example-batch"

NABLEDGE_REPO="${NABLEDGE_REPO:-nablarch/nabledge}"
NABLEDGE_BRANCH="${NABLEDGE_BRANCH:-develop}"
NABLEDGE_REPO_URL="https://github.com/${NABLEDGE_REPO}"

VERSION_FILTER="${1:-}"
if [ -n "$VERSION_FILTER" ] && [[ ! "$VERSION_FILTER" =~ ^(v6|v5|v1\.4|v1\.3|v1\.2|upgrade)$ ]]; then
    echo "ERROR: Invalid version '${VERSION_FILTER}'. Valid values: v6, v5, v1.4, v1.3, v1.2, upgrade"
    exit 1
fi

# Returns 0 if the given version label should be processed
should_run() { [ -z "$VERSION_FILTER" ] || [ "$1" = "$VERSION_FILTER" ]; }

OUTPUT_DIR="${NABLEDGE_DEV_ROOT}/.tmp/nabledge-test"

# Single temp dir for downloaded setup scripts
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "============================================================"
echo "Nabledge Test Environment Setup"
echo "============================================================"
echo "Nabledge repository: ${NABLEDGE_REPO}"
echo "Nabledge branch:     ${NABLEDGE_BRANCH}"
echo "Output directory:    ${OUTPUT_DIR}"
echo "Version filter:      ${VERSION_FILTER:-all versions}"
echo ""

# Allow local overrides for setup scripts (for testing local fixes before release)
LOCAL_SETUP_CC="${LOCAL_SETUP_CC:-}"
LOCAL_SETUP_GHC="${LOCAL_SETUP_GHC:-}"

# Extract setup script URLs from GUIDE files on NABLEDGE_BRANCH
# This ensures we use the same URL as users, and detects if the URL changes in the guide.
echo "[Setup] Fetching setup script URLs from GUIDE files (branch: ${NABLEDGE_BRANCH})..."
GUIDE_CC_URL="https://raw.githubusercontent.com/${NABLEDGE_REPO}/${NABLEDGE_BRANCH}/plugins/nabledge-6/GUIDE-CC.md"
GUIDE_GHC_URL="https://raw.githubusercontent.com/${NABLEDGE_REPO}/${NABLEDGE_BRANCH}/plugins/nabledge-6/GUIDE-GHC.md"
# Extract script filename from GUIDE (detects filename changes), then replace branch with NABLEDGE_BRANCH
SETUP_CC_FILENAME=$(curl -sSfL "$GUIDE_CC_URL" | grep -m1 'curl -sSL.*setup-cc\.sh' | grep -oP 'setup-cc\.sh')
SETUP_GHC_FILENAME=$(curl -sSfL "$GUIDE_GHC_URL" | grep -m1 'curl -sSL.*setup-ghc\.sh' | grep -oP 'setup-ghc\.sh')
if [ -z "$SETUP_CC_FILENAME" ] || [ -z "$SETUP_GHC_FILENAME" ]; then
    echo "ERROR: Could not extract setup script filenames from GUIDE files."
    echo "  GUIDE-CC.md: ${GUIDE_CC_URL}"
    echo "  GUIDE-GHC.md: ${GUIDE_GHC_URL}"
    exit 1
fi
SETUP_CC_URL="https://raw.githubusercontent.com/${NABLEDGE_REPO}/${NABLEDGE_BRANCH}/${SETUP_CC_FILENAME}"
SETUP_GHC_URL="https://raw.githubusercontent.com/${NABLEDGE_REPO}/${NABLEDGE_BRANCH}/${SETUP_GHC_FILENAME}"
echo "[Setup] Setup CC script URL:  ${SETUP_CC_URL}"
echo "[Setup] Setup GHC script URL: ${SETUP_GHC_URL}"
curl -sSfL "$SETUP_CC_URL" -o "$TEMP_DIR/setup-cc.sh"
curl -sSfL "$SETUP_GHC_URL" -o "$TEMP_DIR/setup-ghc.sh"
if [ -n "$LOCAL_SETUP_CC" ]; then
    echo "[Setup] Overriding setup-cc.sh with local file: ${LOCAL_SETUP_CC}"
    cp "$LOCAL_SETUP_CC" "$TEMP_DIR/setup-cc.sh"
fi
if [ -n "$LOCAL_SETUP_GHC" ]; then
    echo "[Setup] Overriding setup-ghc.sh with local file: ${LOCAL_SETUP_GHC}"
    cp "$LOCAL_SETUP_GHC" "$TEMP_DIR/setup-ghc.sh"
fi
echo "[Setup] Setup scripts downloaded."
echo ""

# ------------------------------------------------------------
# Helper: setup one test environment
#
# Args:
#   $1 - target directory (e.g. "v6/test-cc")
#   $2 - source project directory in .lw/ (e.g. "$V6_PROJECT_SRC")
#   $3 - project directory name inside target (e.g. "nablarch-example-batch")
#   $4 - setup script path (e.g. "$TEMP_DIR/setup-cc.sh")
#   $5 - version flag value for -v (e.g. "6", "5", "1.4", "all")
#   $6 - setup hint shown when source is missing (e.g. "Run setup.sh first")
# ------------------------------------------------------------
setup_env() {
    local target_dir="$1"
    local src_dir="$2"
    local project_name="$3"
    local setup_script="$4"
    local version_flag="$5"
    local setup_hint="$6"

    echo "------------------------------------------------------------"
    echo "[${target_dir}] Setting up..."

    # Pre-flight: verify source project exists
    if [ ! -d "$src_dir" ]; then
        echo "ERROR: Source project not found: ${src_dir}"
        echo "  ${setup_hint}"
        exit 1
    fi

    mkdir -p "$target_dir"

    # Copy source project
    echo "[${target_dir}] Copying ${src_dir}..."
    cp -r "$src_dir" "$target_dir/$project_name"

    # Run setup script inside the copied project.
    # GIT_CEILING_DIRECTORIES prevents setup scripts from walking up to a parent git repo.
    echo "[${target_dir}] Running setup script (version: ${version_flag}, branch: ${NABLEDGE_BRANCH})..."
    (
        cd "$target_dir/$project_name"
        GIT_CEILING_DIRECTORIES="$(dirname "$(pwd)")" NABLEDGE_BRANCH="$NABLEDGE_BRANCH" bash "$setup_script" -v "$version_flag"
    )

    echo "[${target_dir}] Done."
    echo ""
}

# ------------------------------------------------------------
# Set up all 10 environments
# ------------------------------------------------------------

HINT_V6="Run setup.sh to clone .lw/nab-official/v6/nablarch-example-batch."
HINT_V5="Run setup.sh to clone .lw/nab-official/v5/nablarch-example-batch."

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

should_run "v6"   && setup_env "v6/test-cc"    "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-cc.sh"  "6"   "$HINT_V6"
should_run "v6"   && setup_env "v6/test-ghc"   "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-ghc.sh" "6"   "$HINT_V6"
should_run "v5"   && setup_env "v5/test-cc"    "$V5_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-cc.sh"  "5"   "$HINT_V5"
should_run "v5"   && setup_env "v5/test-ghc"   "$V5_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-ghc.sh" "5"   "$HINT_V5"
should_run "v1.4" && setup_env "v1.4/test-cc"  "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-cc.sh"  "1.4" "$HINT_V6"
should_run "v1.4" && setup_env "v1.4/test-ghc" "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-ghc.sh" "1.4" "$HINT_V6"
should_run "v1.3" && setup_env "v1.3/test-cc"  "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-cc.sh"  "1.3" "$HINT_V6"
should_run "v1.3" && setup_env "v1.3/test-ghc" "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-ghc.sh" "1.3" "$HINT_V6"
should_run "v1.2" && setup_env "v1.2/test-cc"  "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-cc.sh"  "1.2" "$HINT_V6"
should_run "v1.2" && setup_env "v1.2/test-ghc" "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-ghc.sh" "1.2" "$HINT_V6"
# "upgrade" uses the v6 project as base; two skill versions are installed by setup-cc.sh for version upgrade scenario.
should_run "upgrade"  && setup_env "upgrade/test-cc"   "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-cc.sh"  "6,5"   "$HINT_V6"
should_run "upgrade"  && setup_env "upgrade/test-ghc"  "$V6_PROJECT_SRC"  "nablarch-example-batch" "$TEMP_DIR/setup-ghc.sh" "1.4,5" "$HINT_V6"

# ------------------------------------------------------------
# Verification
# ------------------------------------------------------------
echo "============================================================"
echo "Verifying installations..."
echo ""

verify_fail=0
STATIC_RESULTS=()   # each entry: "label|PASS" or "label|FAIL"
DYNAMIC_RESULTS=()  # each entry: "label|v|tool|PASS/FAIL|time_s|input_tokens|output_tokens|cost_usd|keywords|notes"

# verify_env: static check for one test environment
# Args:
#   $1 - label (e.g. "v6/test-cc")
#   $2 - project dir relative to OUTPUT_DIR (e.g. "v6/test-cc/nablarch-example-batch")
#   $3 - comma-separated versions installed (e.g. "6", "1.4", "6,5,1.4")
#   $4 - tool type: "cc" or "ghc"
#
# Checks per version:
#   - SKILL.md exists          (detects: setup script failed to copy skill)
#   - knowledge/ exists        (detects: knowledge directory missing entirely)
#   - knowledge/ file count    (detects: empty knowledge directory)
#   - knowledge/ count matches expected from nabledge-dev repo (detects: files missing)
#   - docs/ exists             (detects: docs directory missing entirely)
#   - docs/ entry count matches expected from nabledge-dev repo (detects: entries missing)
#   - /n{v} command file exists (detects: command not installed)
#   - .github/prompts/n{v}.prompt.md (GHC only: detects prompt not installed)
#
# Does NOT detect:
#   - Corrupt or incorrect file contents
#   - Runtime errors during nabledge skill execution
#   - Wrong knowledge file content or missing entries
#   → Use dynamic check (verify_dynamic) for runtime verification
verify_env() {
    local label="$1"
    local project_dir="${OUTPUT_DIR}/$2"
    local versions_str="$3"
    local tool="$4"
    local fail=0

    IFS=',' read -ra versions <<< "$versions_str"
    for v in "${versions[@]}"; do
        local skill_dir="$project_dir/.claude/skills/nabledge-${v}"
        local cmd_file="$project_dir/.claude/commands/n${v}.md"

        _static_note() { _static_fail_notes="${_static_fail_notes:+${_static_fail_notes}; }$1"; }

        if [ ! -f "$skill_dir/SKILL.md" ]; then
            local msg="nabledge-${v}: SKILL.md not found (skill not installed)"
            echo "  [FAIL] ${label} ${msg}"
            _static_note "$msg"
            fail=1
            continue
        fi

        # knowledge/ check
        local knowledge_dir="$skill_dir/knowledge"
        local knowledge_count=0
        if [ -d "$knowledge_dir" ]; then
            knowledge_count=$(ls "$knowledge_dir" | wc -l)
        else
            local msg="nabledge-${v}: knowledge/ directory not found"
            echo "  [FAIL] ${label} ${msg}"
            _static_note "$msg"
            fail=1
            continue
        fi

        local expected_knowledge_count
        expected_knowledge_count=$(ls "${NABLEDGE_DEV_ROOT}/.claude/skills/nabledge-${v}/knowledge" 2>/dev/null | wc -l)
        if [ "$knowledge_count" -ne "$expected_knowledge_count" ]; then
            local msg="nabledge-${v}: knowledge/ has ${knowledge_count} files, expected ${expected_knowledge_count}"
            echo "  [FAIL] ${label} ${msg}"
            _static_note "$msg"
            fail=1
        fi

        # docs/ check
        local docs_dir="$skill_dir/docs"
        local docs_count=0
        if [ -d "$docs_dir" ]; then
            docs_count=$(ls "$docs_dir" | wc -l)
        else
            local msg="nabledge-${v}: docs/ directory not found"
            echo "  [FAIL] ${label} ${msg}"
            _static_note "$msg"
            fail=1
        fi

        local expected_docs_count
        expected_docs_count=$(ls "${NABLEDGE_DEV_ROOT}/.claude/skills/nabledge-${v}/docs" 2>/dev/null | wc -l)
        if [ -d "$docs_dir" ] && [ "$docs_count" -ne "$expected_docs_count" ]; then
            local msg="nabledge-${v}: docs/ has ${docs_count} entries, expected ${expected_docs_count}"
            echo "  [FAIL] ${label} ${msg}"
            _static_note "$msg"
            fail=1
        fi

        # command file check (CC only; GHC uses .github/prompts/ instead)
        local cmd_status=""
        if [ "$tool" = "ghc" ]; then
            cmd_status="N/A (GHC)"
        elif [ -f "$cmd_file" ]; then
            cmd_status="ok"
        else
            local msg="nabledge-${v}: /n${v} command missing"
            echo "  [FAIL] ${label} ${msg}"
            _static_note "$msg"
            fail=1
            cmd_status="FAIL"
        fi

        # GHC prompt file check
        local ghc_status=""
        if [ "$tool" = "ghc" ]; then
            local prompt_file="$project_dir/.github/prompts/n${v}.prompt.md"
            if [ -f "$prompt_file" ]; then
                ghc_status=", prompt ok"
            else
                local msg="nabledge-${v}: n${v}.prompt.md missing"
                echo "  [FAIL] ${label} ${msg}"
                _static_note "$msg"
                fail=1
                ghc_status=", prompt FAIL"
            fi
        fi

        echo "  [OK]   ${label} nabledge-${v}: SKILL.md ok, knowledge/ ${knowledge_count} files, docs/ ${docs_count} entries, command ${cmd_status}${ghc_status}"
    done

    if [ "$fail" -eq 1 ]; then
        verify_fail=1
        STATIC_RESULTS+=("${label}|FAIL|${_static_fail_notes:-}")
    else
        STATIC_RESULTS+=("${label}|PASS|")
    fi
    unset _static_fail_notes
}

# verify_dynamic: dynamic check by running a knowledge search
# CC environments use claude -p; GHC environments use copilot -p.
# Args:
#   $1 - label (e.g. "v6/test-cc")
#   $2 - project dir relative to OUTPUT_DIR (e.g. "v6/test-cc/nablarch-example-batch")
#   $3 - nabledge version to query (e.g. "6", "5", "1.4")
#   $4 - test query to ask nabledge
#   $5 - comma-separated keywords expected in the response
#   $6 - tool type: "cc" or "ghc"
verify_dynamic() {
    local label="$1"
    local project_dir="${OUTPUT_DIR}/$2"
    local v="$3"
    local query="$4"
    local keywords_str="$5"
    local tool="$6"

    local start_time=$SECONDS
    local elapsed_s=0
    local input_tokens="N/A"
    local output_tokens="N/A"
    local cost_usd="N/A"
    local ghc_log_dir=""

    if [ "$tool" = "ghc" ]; then
        if ! command -v copilot &>/dev/null; then
            echo "  [FAIL] ${label} nabledge-${v}: copilot CLI not found"
            verify_fail=1
            DYNAMIC_RESULTS+=("${label}|${v}|${tool}|FAIL|N/A|N/A|N/A|N/A|N/A|copilot CLI not found")
            return
        fi
        local prompt_file="$project_dir/.github/prompts/n${v}.prompt.md"
        if [ ! -f "$prompt_file" ]; then
            echo "  [FAIL] ${label} nabledge-${v}: GHC prompt file not found: ${prompt_file}"
            verify_fail=1
            DYNAMIC_RESULTS+=("${label}|${v}|${tool}|FAIL|N/A|N/A|N/A|N/A|N/A|GHC prompt file not found")
            return
        fi
        echo "  [RUN]  ${label} nabledge-${v}: running knowledge search via copilot -p..."
        local ghc_content
        ghc_content=$(cat "$prompt_file")
        ghc_content="${ghc_content//\$ARGUMENTS/$query}"
        local ghc_prompt_file
        ghc_prompt_file=$(mktemp "${OUTPUT_DIR}/ghc-prompt-XXXXXX.md")
        echo "$ghc_content" > "$ghc_prompt_file"
        local ghc_prompt_basename
        ghc_prompt_basename=$(basename "$ghc_prompt_file")
        # Copy temp prompt file into project dir so copilot can find it
        cp "$ghc_prompt_file" "$project_dir/$ghc_prompt_basename"
        ghc_log_dir="${OUTPUT_DIR}/dynamic-check-${label//\//-}-nabledge-${v}.ghc-logs"
        mkdir -p "$ghc_log_dir"
        local output
        output=$(script -qc "cd '$project_dir' && timeout 240 copilot -p '${ghc_prompt_basename}' --model claude-sonnet-4.6 --yolo --output-format json --log-dir '$ghc_log_dir' --log-level debug" /dev/null 2>&1) || true
        rm -f "$ghc_prompt_file" "$project_dir/$ghc_prompt_basename"
        elapsed_s=$(( SECONDS - start_time ))
        # Extract totalApiDurationMs and output tokens from GHC JSON output
        local ghc_api_ms
        ghc_api_ms=$(echo "$output" | grep '"type":"result"' | tail -1 | jq -r '.usage.totalApiDurationMs // empty' 2>/dev/null || true)
        if [ -n "$ghc_api_ms" ] && [ "$ghc_api_ms" != "null" ]; then
            elapsed_s=$(( ghc_api_ms / 1000 ))
        fi
        # Sum outputTokens from all assistant.message events (input tokens not available in GHC JSON output)
        local ghc_out_sum
        ghc_out_sum=$(echo "$output" | grep '"type":"assistant.message"' | jq -r '.data.outputTokens // 0' 2>/dev/null | paste -sd+ | bc 2>/dev/null || true)
        if [[ "$ghc_out_sum" =~ ^[0-9]+$ ]] && [ "$ghc_out_sum" -gt 0 ]; then
            output_tokens="$ghc_out_sum"
        fi
    else
        if ! command -v claude &>/dev/null; then
            echo "  [FAIL] ${label} nabledge-${v}: claude CLI not found"
            verify_fail=1
            DYNAMIC_RESULTS+=("${label}|${v}|${tool}|FAIL|N/A|N/A|N/A|N/A|N/A|claude CLI not found")
            return
        fi
        local cmd_file="$project_dir/.claude/commands/n${v}.md"
        if [ ! -f "$cmd_file" ]; then
            echo "  [FAIL] ${label} nabledge-${v}: CC command file not found: ${cmd_file}"
            verify_fail=1
            DYNAMIC_RESULTS+=("${label}|${v}|${tool}|FAIL|N/A|N/A|N/A|N/A|N/A|CC command file not found")
            return
        fi
        echo "  [RUN]  ${label} nabledge-${v}: running knowledge search via claude -p (timeout: 240s)..."
        local output
        # CC uses short model alias "sonnet"; GHC uses full model ID "claude-sonnet-4-6" (copilot requirement)
        # stream-json+verbose outputs full conversation including tool_use events with file paths
        local cc_log_file="${OUTPUT_DIR}/dynamic-check-${label//\//-}-nabledge-${v}.log"
        timeout 240 bash -c "cd $(printf '%q' "$project_dir") && claude -p $(printf '%q' "/n${v} ${query}") --model sonnet --dangerously-skip-permissions --output-format stream-json --verbose < /dev/null" > "$cc_log_file" 2>&1 || true
        output=$(cat "$cc_log_file")
        elapsed_s=$(( SECONDS - start_time ))
        # Extract metrics from the {"type":"result"} line in stream-json output
        local cc_result_line
        cc_result_line=$(grep '"type":"result"' "$cc_log_file" | tail -1)
        if [ -n "$cc_result_line" ]; then
            local cc_duration_ms
            cc_duration_ms=$(echo "$cc_result_line" | jq -r '.duration_ms // empty' 2>/dev/null || true)
            # Sum input_tokens + cache_creation_input_tokens + cache_read_input_tokens for actual total
            local cc_in cc_cache_create cc_cache_read
            cc_in=$(echo "$cc_result_line" | jq -r '.usage.input_tokens // 0' 2>/dev/null || echo 0)
            cc_cache_create=$(echo "$cc_result_line" | jq -r '.usage.cache_creation_input_tokens // 0' 2>/dev/null || echo 0)
            cc_cache_read=$(echo "$cc_result_line" | jq -r '.usage.cache_read_input_tokens // 0' 2>/dev/null || echo 0)
            if [[ "$cc_in" =~ ^[0-9]+$ ]]; then
                input_tokens=$(( cc_in + cc_cache_create + cc_cache_read ))
            fi
            output_tokens=$(echo "$cc_result_line" | jq -r '.usage.output_tokens // empty' 2>/dev/null || true)
            cost_usd=$(echo "$cc_result_line" | jq -r '.total_cost_usd // empty' 2>/dev/null || true)
            if [ -n "$cc_duration_ms" ] && [ "$cc_duration_ms" != "null" ]; then
                elapsed_s=$(( cc_duration_ms / 1000 ))
            fi
        fi
        [ -z "$input_tokens" ]  && input_tokens="N/A"
        [ -z "$output_tokens" ] && output_tokens="N/A"
        [ -z "$cost_usd" ]      && cost_usd="N/A"
    fi

    local log_file="${OUTPUT_DIR}/dynamic-check-${label//\//-}-nabledge-${v}.log"
    if [ "$tool" != "cc" ]; then
        echo "$output" > "$log_file"
    fi

    # Check if SKILL.md was read during the knowledge search.
    # Both CC (stream-json) and GHC (--output-format json) include SKILL.md path in their stdout log.
    local skill_read=0
    grep -q 'SKILL\.md' "$log_file" && skill_read=1 || true

    # Extract final answer text for section and keyword checks.
    # For CC: {"type":"result"} .result contains the full final answer.
    # For GHC: the last assistant.message_delta stream; concatenate all deltaContent of the last messageId.
    local final_answer_text=""
    if [ "$tool" = "cc" ]; then
        final_answer_text=$(grep '"type":"result"' "$log_file" | tail -1 | jq -r '.result // ""' 2>/dev/null || true)
    else
        local last_msg_id
        last_msg_id=$(grep '"type":"assistant.message_delta"' "$log_file" | jq -r '.data.messageId' 2>/dev/null | tail -1)
        if [ -n "$last_msg_id" ]; then
            # Concatenate all deltaContent fragments into a single string (deltas can split mid-word)
            final_answer_text=$(grep '"type":"assistant.message_delta"' "$log_file" \
                | jq -r --arg id "$last_msg_id" 'select(.data.messageId == $id) | .data.deltaContent // ""' 2>/dev/null \
                | paste -sd '' || true)
        fi
    fi

    # Check if a conclusion was produced (i.e., the workflow ran to completion).
    # Detect the four required sections in order: 結論, 根拠, 注意点, 参照
    local answered=0
    _has_sections() {
        local text="$1"
        local n_ketsuron n_konkyo n_chuui n_sansho
        # Use byte offsets (-bo) so the check works whether text is single-line or multi-line
        n_ketsuron=$(echo "$text" | grep -bo '結論' | head -1 | cut -d: -f1)
        n_konkyo=$(echo "$text"   | grep -bo '根拠' | head -1 | cut -d: -f1)
        n_chuui=$(echo "$text"    | grep -bo '注意点' | head -1 | cut -d: -f1)
        n_sansho=$(echo "$text"   | grep -bo '参照' | head -1 | cut -d: -f1)
        [ -n "$n_ketsuron" ] && [ -n "$n_konkyo" ] && [ -n "$n_chuui" ] && [ -n "$n_sansho" ] \
            && [ "$n_ketsuron" -lt "$n_konkyo" ] && [ "$n_konkyo" -lt "$n_chuui" ] && [ "$n_chuui" -lt "$n_sansho" ]
    }
    _has_sections "$final_answer_text" && answered=1 || true

    # Keyword detection (reference only, not used for pass/fail)
    local detected_count=0
    local total_count=0
    IFS=',' read -ra keywords <<< "$keywords_str"
    for kw in "${keywords[@]}"; do
        total_count=$((total_count + 1))
        echo "$final_answer_text" | grep -q "$kw" && detected_count=$((detected_count + 1)) || true
    done

    local answered_label
    [ "$answered" -eq 1 ] && answered_label="yes" || answered_label="no"

    # Build FAIL detail notes
    local dynamic_notes=""
    if [ "$skill_read" -eq 0 ]; then
        dynamic_notes="SKILL.md not read"
    fi
    if [ "$answered" -eq 0 ]; then
        # Identify which required sections are missing or out of order
        local missing_sections=""
        for sec in '結論' '根拠' '注意点' '参照'; do
            if ! echo "$final_answer_text" | grep -q "$sec"; then
                missing_sections="${missing_sections:+${missing_sections}, }${sec}"
            fi
        done
        local answered_note
        if [ -n "$missing_sections" ]; then
            answered_note="missing sections: ${missing_sections}"
        else
            answered_note="sections out of order"
        fi
        dynamic_notes="${dynamic_notes:+${dynamic_notes}; }${answered_note}"
    fi

    local result_status
    if [ "$skill_read" -eq 0 ] || [ "$answered" -eq 0 ]; then
        echo "  [FAIL] ${label} nabledge-${v}: SKILL.md read: $([ "$skill_read" -eq 1 ] && echo yes || echo no), answered: ${answered_label}; keywords: ${detected_count}/${total_count}"
        echo "         Log: ${log_file}"
        verify_fail=1
        result_status="FAIL"
    else
        echo "  [OK]   ${label} nabledge-${v}: SKILL.md read, answered: ${answered_label}; keywords: ${detected_count}/${total_count}"
        result_status="PASS"
    fi

    DYNAMIC_RESULTS+=("${label}|${v}|${tool}|${result_status}|${elapsed_s}|${input_tokens}|${output_tokens}|${cost_usd}|${detected_count}/${total_count}|${dynamic_notes}")
}

echo "[Static checks]"
should_run "v6"   && verify_env "v6/test-cc"    "v6/test-cc/nablarch-example-batch"    "6"               "cc"
should_run "v6"   && verify_env "v6/test-ghc"   "v6/test-ghc/nablarch-example-batch"   "6"               "ghc"
should_run "v5"   && verify_env "v5/test-cc"    "v5/test-cc/nablarch-example-batch"    "5"               "cc"
should_run "v5"   && verify_env "v5/test-ghc"   "v5/test-ghc/nablarch-example-batch"   "5"               "ghc"
should_run "v1.4" && verify_env "v1.4/test-cc"  "v1.4/test-cc/nablarch-example-batch"  "1.4"             "cc"
should_run "v1.4" && verify_env "v1.4/test-ghc" "v1.4/test-ghc/nablarch-example-batch" "1.4"             "ghc"
should_run "v1.3" && verify_env "v1.3/test-cc"  "v1.3/test-cc/nablarch-example-batch"  "1.3"             "cc"
should_run "v1.3" && verify_env "v1.3/test-ghc" "v1.3/test-ghc/nablarch-example-batch" "1.3"             "ghc"
should_run "v1.2" && verify_env "v1.2/test-cc"  "v1.2/test-cc/nablarch-example-batch"  "1.2"             "cc"
should_run "v1.2" && verify_env "v1.2/test-ghc" "v1.2/test-ghc/nablarch-example-batch" "1.2"             "ghc"
should_run "upgrade"  && verify_env "upgrade/test-cc"   "upgrade/test-cc/nablarch-example-batch"   "6,5"   "cc"
should_run "upgrade"  && verify_env "upgrade/test-ghc"  "upgrade/test-ghc/nablarch-example-batch"  "1.4,5" "ghc"

if [ "$verify_fail" -ne 0 ]; then
    echo ""
    echo "ERROR: Static checks failed. Fix the setup issues above before running dynamic checks."
    exit 1
fi

echo ""
echo "[Dynamic checks]"
Q_V6="ウェブアプリケーションで入力チェックを実装するには？"
KW_V6="InjectForm"
Q_V5="ウェブアプリケーションで入力チェックを実装するには？"
KW_V5="InjectForm"
Q_V14="ウェブアプリケーションでコードリストのプルダウン入力を実装するには？"
KW_V14="n:codeSelect,codeId"
Q_V13="ウェブアプリケーションでコードリストのプルダウン入力を実装するには？"
KW_V13="n:codeSelect,codeId"
Q_V12="ウェブアプリケーションでコードリストのプルダウン入力を実装するには？"
KW_V12="n:codeSelect,codeId"
should_run "v6"   && verify_dynamic "v6/test-cc"    "v6/test-cc/nablarch-example-batch"    "6"   "$Q_V6"  "$KW_V6"  "cc"
should_run "v6"   && verify_dynamic "v6/test-ghc"   "v6/test-ghc/nablarch-example-batch"   "6"   "$Q_V6"  "$KW_V6"  "ghc"
should_run "v5"   && verify_dynamic "v5/test-cc"    "v5/test-cc/nablarch-example-batch"    "5"   "$Q_V5"  "$KW_V5"  "cc"
should_run "v5"   && verify_dynamic "v5/test-ghc"   "v5/test-ghc/nablarch-example-batch"   "5"   "$Q_V5"  "$KW_V5"  "ghc"
should_run "v1.4" && verify_dynamic "v1.4/test-cc"  "v1.4/test-cc/nablarch-example-batch"  "1.4" "$Q_V14" "$KW_V14" "cc"
should_run "v1.4" && verify_dynamic "v1.4/test-ghc" "v1.4/test-ghc/nablarch-example-batch" "1.4" "$Q_V14" "$KW_V14" "ghc"
should_run "v1.3" && verify_dynamic "v1.3/test-cc"  "v1.3/test-cc/nablarch-example-batch"  "1.3" "$Q_V13" "$KW_V13" "cc"
should_run "v1.3" && verify_dynamic "v1.3/test-ghc" "v1.3/test-ghc/nablarch-example-batch" "1.3" "$Q_V13" "$KW_V13" "ghc"
should_run "v1.2" && verify_dynamic "v1.2/test-cc"  "v1.2/test-cc/nablarch-example-batch"  "1.2" "$Q_V12" "$KW_V12" "cc"
should_run "v1.2" && verify_dynamic "v1.2/test-ghc" "v1.2/test-ghc/nablarch-example-batch" "1.2" "$Q_V12" "$KW_V12" "ghc"
should_run "upgrade"  && verify_dynamic "upgrade/test-cc"   "upgrade/test-cc/nablarch-example-batch"   "6"   "$Q_V6"  "$KW_V6"  "cc"
should_run "upgrade"  && verify_dynamic "upgrade/test-cc"   "upgrade/test-cc/nablarch-example-batch"   "5"   "$Q_V5"  "$KW_V5"  "cc"
should_run "upgrade"  && verify_dynamic "upgrade/test-ghc"  "upgrade/test-ghc/nablarch-example-batch"  "1.4" "$Q_V14" "$KW_V14" "ghc"
should_run "upgrade"  && verify_dynamic "upgrade/test-ghc"  "upgrade/test-ghc/nablarch-example-batch"  "5"   "$Q_V5"  "$KW_V5"  "ghc"

echo ""

# ------------------------------------------------------------
# Report generation
# ------------------------------------------------------------
generate_report() {
    local report_dir="${NABLEDGE_DEV_ROOT}/tools/tests/reports"
    mkdir -p "$report_dir"
    local branch_slug="${NABLEDGE_BRANCH//\//-}"
    local report_file="${report_dir}/${branch_slug}-$(date +%Y%m%d-%H%M%S).md"
    local run_datetime
    run_datetime=$(date +"%Y-%m-%d %H:%M:%S")
    local repo_commit
    repo_commit=$(gh api "repos/${NABLEDGE_REPO}/commits/${NABLEDGE_BRANCH}" --jq '.sha' 2>/dev/null | cut -c1-7 || echo "N/A")

    {
        echo "# Nabledge Test Setup Report"
        echo ""
        echo "| Item | Value |"
        echo "| ---- | ----- |"
        echo "| Branch | \`${NABLEDGE_BRANCH}\` |"
        echo "| Commit | \`${repo_commit}\` |"
        echo "| Repository | \`${NABLEDGE_REPO}\` |"
        echo "| Run datetime | ${run_datetime} |"
        echo "| Version filter | ${VERSION_FILTER:-all} |"
        echo ""

        echo "## Static Checks"
        echo ""
        echo "| Environment | Result |"
        echo "| ----------- | ------ |"
        for entry in "${STATIC_RESULTS[@]}"; do
            IFS='|' read -r s_label s_result s_notes <<< "$entry"
            echo "| ${s_label} | ${s_result} |"
        done
        echo ""

        echo "## Dynamic Checks"
        echo ""
        echo "| Environment | Version | Tool | Result | Time (s) | Input tokens | Output tokens | Cost (USD) | Keywords | Notes |"
        echo "| ----------- | ------- | ---- | ------ | -------- | ------------ | ------------- | ---------- | -------- | ----- |"
        local total_time=0
        local total_input=0
        local total_output=0
        local total_cost=0
        local has_cost=0
        for entry in "${DYNAMIC_RESULTS[@]}"; do
            IFS='|' read -r d_label d_v d_tool d_result d_time d_input d_output d_cost d_kw d_notes <<< "$entry"
            echo "| ${d_label} | ${d_v} | ${d_tool} | ${d_result} | ${d_time} | ${d_input} | ${d_output} | ${d_cost} | ${d_kw} | ${d_notes} |"
            if [[ "$d_time" =~ ^[0-9]+$ ]]; then
                total_time=$(( total_time + d_time ))
            fi
            if [[ "$d_input" =~ ^[0-9]+$ ]]; then
                total_input=$(( total_input + d_input ))
            fi
            if [[ "$d_output" =~ ^[0-9]+$ ]]; then
                total_output=$(( total_output + d_output ))
            fi
            if [[ "$d_cost" =~ ^[0-9.]+$ ]]; then
                total_cost=$(awk "BEGIN{printf \"%.6f\", ${total_cost}+${d_cost}}")
                has_cost=1
            fi
        done
        echo ""
        echo "### Totals"
        echo ""
        echo "| Metric | Value |"
        echo "| ------ | ----- |"
        echo "| Total time (s) | ${total_time} |"
        local total_tokens_display="N/A"
        if [ "$total_input" -gt 0 ] || [ "$total_output" -gt 0 ]; then
            total_tokens_display="$(( total_input + total_output )) (in: ${total_input}, out: ${total_output})"
        fi
        echo "| Total tokens | ${total_tokens_display} |"
        local total_cost_display="N/A"
        [ "$has_cost" -eq 1 ] && total_cost_display="\$${total_cost}"
        echo "| Total estimated cost | ${total_cost_display} |"
    } > "$report_file"

    echo ""
    echo "Report: ${report_file}"
}

generate_report

if [ "$verify_fail" -eq 0 ]; then
    echo "All environments verified successfully."
else
    echo "ERROR: Some environments failed verification. See [FAIL] entries above."
    exit 1
fi

# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------
echo "============================================================"
echo "Test environment setup complete!"
echo ""
echo "Output: ${OUTPUT_DIR}"
echo ""
echo "Environments:"
should_run "v6"   && echo "  v6/test-cc/nablarch-example-batch    - nabledge-6 x Claude Code"
should_run "v6"   && echo "  v6/test-ghc/nablarch-example-batch   - nabledge-6 x GitHub Copilot"
should_run "v5"   && echo "  v5/test-cc/nablarch-example-batch    - nabledge-5 x Claude Code"
should_run "v5"   && echo "  v5/test-ghc/nablarch-example-batch   - nabledge-5 x GitHub Copilot"
should_run "v1.4" && echo "  v1.4/test-cc/nablarch-example-batch  - nabledge-1.4 x Claude Code"
should_run "v1.4" && echo "  v1.4/test-ghc/nablarch-example-batch - nabledge-1.4 x GitHub Copilot"
should_run "v1.3" && echo "  v1.3/test-cc/nablarch-example-batch  - nabledge-1.3 x Claude Code"
should_run "v1.3" && echo "  v1.3/test-ghc/nablarch-example-batch - nabledge-1.3 x GitHub Copilot"
should_run "v1.2" && echo "  v1.2/test-cc/nablarch-example-batch  - nabledge-1.2 x Claude Code"
should_run "v1.2" && echo "  v1.2/test-ghc/nablarch-example-batch - nabledge-1.2 x GitHub Copilot"
should_run "upgrade"  && echo "  upgrade/test-cc/nablarch-example-batch   - nabledge-6+5 x Claude Code (version upgrade)"
should_run "upgrade"  && echo "  upgrade/test-ghc/nablarch-example-batch  - nabledge-1.4+5 x GitHub Copilot (version upgrade)"
echo "============================================================"
