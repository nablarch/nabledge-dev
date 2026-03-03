#!/bin/bash
# Pre-fill deterministic placeholders in code analysis template
# This script reduces LLM generation time by pre-filling 8 deterministic placeholders

set -e

# Usage message
usage() {
    cat << EOF
Usage: $0 --target-name <name> --target-desc <description> --modules <modules> --source-files <files> --knowledge-files <files> --output-path <path>

Pre-fill deterministic placeholders in code analysis template.

Required arguments:
  --target-name <name>        Target name (e.g., "LoginAction", "ログイン機能")
  --target-desc <description> One-line description of the target
  --modules <modules>         Affected modules (e.g., "proman-web, proman-common")
  --source-files <files>      Comma-separated source file paths or basenames
                              - Full path: "src/main/java/LoginAction.java" (pass-through)
                              - Basename: "LoginAction.java" (auto-search from project root)
  --knowledge-files <files>   Comma-separated knowledge file paths or basenames
                              - Full path: ".claude/skills/nabledge-6/knowledge/features/universal-dao.json"
                              - Basename: "universal-dao" or "universal-dao.json" (auto-search)
  --output-path <path>        Output file path

Optional arguments:
  --official-docs <docs>      Comma-separated official documentation URLs (default: none)

Examples:
  # Using basenames (auto-search)
  $0 --target-name "LoginAction" \\
     --target-desc "ログイン認証処理" \\
     --modules "proman-web" \\
     --source-files "LoginAction.java,LoginForm.java" \\
     --knowledge-files "universal-dao,web-application" \\
     --output-path ".nabledge/20260220/code-analysis-login-action.md"

  # Using full paths (pass-through)
  $0 --target-name "LoginAction" \\
     --target-desc "ログイン認証処理" \\
     --modules "proman-web" \\
     --source-files "proman-web/src/main/java/LoginAction.java,proman-web/src/main/java/LoginForm.java" \\
     --knowledge-files ".claude/skills/nabledge-6/knowledge/features/libraries/universal-dao.json" \\
     --output-path ".nabledge/20260220/code-analysis-login-action.md"
EOF
    exit 1
}

# Parse arguments
TARGET_NAME=""
TARGET_DESC=""
MODULES=""
SOURCE_FILES=""
KNOWLEDGE_FILES=""
OFFICIAL_DOCS=""
OUTPUT_PATH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --target-name)
            TARGET_NAME="$2"
            shift 2
            ;;
        --target-desc)
            TARGET_DESC="$2"
            shift 2
            ;;
        --modules)
            MODULES="$2"
            shift 2
            ;;
        --source-files)
            SOURCE_FILES="$2"
            shift 2
            ;;
        --knowledge-files)
            KNOWLEDGE_FILES="$2"
            shift 2
            ;;
        --official-docs)
            OFFICIAL_DOCS="$2"
            shift 2
            ;;
        --output-path)
            OUTPUT_PATH="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Error: Unknown option $1" >&2
            usage
            ;;
    esac
done

# Validate required arguments
if [[ -z "$TARGET_NAME" || -z "$TARGET_DESC" || -z "$MODULES" || -z "$SOURCE_FILES" || -z "$KNOWLEDGE_FILES" || -z "$OUTPUT_PATH" ]]; then
    echo "Error: Missing required arguments" >&2
    usage
fi

# Find project root
if git rev-parse --show-toplevel &>/dev/null; then
    PROJECT_ROOT="$(git rev-parse --show-toplevel)"
else
    PROJECT_ROOT="$(pwd)"
fi

# Template file location
TEMPLATE_FILE="$PROJECT_ROOT/.claude/skills/nabledge-6/assets/code-analysis-template.md"

# Validate template file exists and is readable
if [[ ! -f "$TEMPLATE_FILE" ]]; then
    echo "Error: Template file not found at $TEMPLATE_FILE" >&2
    exit 1
fi

if [[ ! -r "$TEMPLATE_FILE" ]]; then
    echo "Error: Template file is not readable: $TEMPLATE_FILE" >&2
    exit 1
fi

# Get current date and time
GENERATION_DATE=$(date '+%Y-%m-%d')
GENERATION_TIME=$(date '+%H:%M:%S')

# Resolve file path: supports both basename (search) and full path (pass-through)
# Usage: resolve_file <file_pattern> <search_dir> <file_type>
# Returns: full path on stdout, or empty if not found
# Exit codes: 0=success, 1=multiple matches found
resolve_file() {
    local file_pattern="$1"
    local search_dir="$2"
    local file_type="$3"  # "source" or "knowledge"

    # If pattern contains '/', treat as full path (pass-through)
    if [[ "$file_pattern" == */* ]]; then
        if [[ -f "$file_pattern" ]]; then
            echo "$file_pattern"
            return 0
        else
            echo "Warning: ${file_type} file not found: '$file_pattern' (full path) - link will be omitted" >&2
            return 0
        fi
    fi

    # Basename mode: search for file
    local matches
    if [[ "$file_type" == "knowledge" ]]; then
        # For knowledge files, search for .json files
        local basename="${file_pattern%.json}"  # Remove .json if present
        matches=$(find "$search_dir" -type f -name "${basename}.json" 2>/dev/null)
    else
        # For source files, search by exact basename
        matches=$(find "$search_dir" -type f -name "$file_pattern" 2>/dev/null)
    fi

    # Check if matches is empty
    if [[ -z "$matches" ]]; then
        echo "Warning: ${file_type} file not found: '$file_pattern' (searched in: $search_dir) - link will be omitted" >&2
        return 0
    fi

    # Count matches (only count non-empty lines)
    local match_count=$(echo "$matches" | wc -l)

    if [[ $match_count -eq 1 ]]; then
        echo "$matches"
        return 0
    else
        echo "Error: Multiple ${file_type} files found for '$file_pattern':" >&2
        echo "$matches" | while IFS= read -r match; do
            echo "  - $match" >&2
        done
        echo "" >&2
        echo "Solution: Use full path instead of basename:" >&2
        if [[ "$file_type" == "source" ]]; then
            echo "  --source-files 'path/to/$file_pattern'" >&2
        else
            echo "  --knowledge-files 'path/to/$file_pattern'" >&2
        fi
        return 1
    fi
}

# Calculate relative path from output directory to project root
OUTPUT_DIR=$(dirname "$OUTPUT_PATH")
# Count directory levels: Number of path components = slashes + 1
# Example: ".nabledge/20260220" has 1 slash → 2 levels → requires "../../" prefix
LEVEL_COUNT=$(( $(echo "$OUTPUT_DIR" | tr -cd '/' | wc -c) + 1 ))
RELATIVE_PREFIX=""
for ((i=0; i<LEVEL_COUNT; i++)); do
    # Append ../ at end (was prepending incorrectly before fix)
    RELATIVE_PREFIX="${RELATIVE_PREFIX}../"
done

# Build source files links
SOURCE_FILES_LINKS=""
IFS=',' read -ra FILES <<< "$SOURCE_FILES"
for file in "${FILES[@]}"; do
    file=$(echo "$file" | xargs) # trim whitespace
    [[ -z "$file" ]] && continue

    # Resolve file path (supports basename and full path)
    resolved_path=$(resolve_file "$file" "." "source")
    exit_code=$?

    # If multiple matches found, exit with error
    if [[ $exit_code -ne 0 ]]; then
        exit $exit_code
    fi

    # If file not found, skip (warning already printed)
    if [[ -z "$resolved_path" ]]; then
        continue
    fi

    filename=$(basename "$resolved_path")
    relative_path="${RELATIVE_PREFIX}${resolved_path}"
    # Extract simple description from filename (remove extension)
    desc=$(basename "$resolved_path" | sed 's/\.[^.]*$//')
    SOURCE_FILES_LINKS+="- [${filename}](${relative_path}) - ${desc}"$'\n'
done
SOURCE_FILES_LINKS=$(echo "$SOURCE_FILES_LINKS" | sed 's/^$//')

# Build knowledge base links
KNOWLEDGE_BASE_LINKS=""
IFS=',' read -ra FILES <<< "$KNOWLEDGE_FILES"
for file in "${FILES[@]}"; do
    file=$(echo "$file" | xargs) # trim whitespace
    [[ -z "$file" ]] && continue

    # Resolve file path (supports basename and full path)
    resolved_path=$(resolve_file "$file" ".claude/skills/nabledge-6/knowledge" "knowledge")
    exit_code=$?

    # If multiple matches found, exit with error
    if [[ $exit_code -ne 0 ]]; then
        exit $exit_code
    fi

    # If file not found, skip (warning already printed)
    if [[ -z "$resolved_path" ]]; then
        continue
    fi

    # Convert knowledge JSON paths to docs MD paths
    # Example: .claude/skills/nabledge-6/knowledge/features/X.json
    #       → .claude/skills/nabledge-6/docs/features/X.md
    doc_file="${resolved_path/\/knowledge\//\/docs\/}"
    doc_file="${doc_file/.json/.md}"

    filename=$(basename "$doc_file" .md)
    relative_path="${RELATIVE_PREFIX}${doc_file}"
    # Use filename as description (capitalize first letter)
    desc=$(echo "$filename" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')
    KNOWLEDGE_BASE_LINKS+="- [${desc}](${relative_path})"$'\n'
done
KNOWLEDGE_BASE_LINKS=$(echo "$KNOWLEDGE_BASE_LINKS" | sed 's/^$//')

# Build official docs links (if provided)
OFFICIAL_DOCS_LINKS=""
if [[ -n "$OFFICIAL_DOCS" ]]; then
    IFS=',' read -ra DOCS <<< "$OFFICIAL_DOCS"
    for doc in "${DOCS[@]}"; do
        doc=$(echo "$doc" | xargs) # trim whitespace
        # Extract title from URL (last segment before .html)
        title=$(basename "$doc" .html | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')
        OFFICIAL_DOCS_LINKS+="- [${title}](${doc})"$'\n'
    done
else
    OFFICIAL_DOCS_LINKS="(No official documentation links available)"
fi
OFFICIAL_DOCS_LINKS=$(echo "$OFFICIAL_DOCS_LINKS" | sed 's/^$//')

# Create output directory if it doesn't exist
mkdir -p "$(dirname "$OUTPUT_PATH")"

# Copy template and replace placeholders
# Use temporary file in output directory to avoid environment dependencies
OUTPUT_DIR_REAL=$(dirname "$OUTPUT_PATH")
TEMP_FILE="$OUTPUT_DIR_REAL/.prefill-template-$$.tmp"

# Set up cleanup trap to remove temp files on exit/error
trap 'rm -f "$TEMP_FILE" "$TEMP_FILE.tmp"' EXIT INT TERM

cp "$TEMPLATE_FILE" "$TEMP_FILE"

# Escape special characters for sed
# Handles: & / \ [ ] * . ^ $ and newlines
escape_sed() {
    echo "$1" | sed 's/[&/\[\]*.\^$]/\\&/g; s/\\/\\\\/g'
}

TARGET_NAME_ESC=$(escape_sed "$TARGET_NAME")
TARGET_DESC_ESC=$(escape_sed "$TARGET_DESC")
MODULES_ESC=$(escape_sed "$MODULES")
GENERATION_DATE_ESC=$(escape_sed "$GENERATION_DATE")
GENERATION_TIME_ESC=$(escape_sed "$GENERATION_TIME")
SOURCE_FILES_LINKS_ESC=$(escape_sed "$SOURCE_FILES_LINKS")
KNOWLEDGE_BASE_LINKS_ESC=$(escape_sed "$KNOWLEDGE_BASE_LINKS")
OFFICIAL_DOCS_LINKS_ESC=$(escape_sed "$OFFICIAL_DOCS_LINKS")

# Replace placeholders (one by one to avoid conflicts)
sed -i "s/{{target_name}}/$TARGET_NAME_ESC/g" "$TEMP_FILE"
sed -i "s/{{target_description}}/$TARGET_DESC_ESC/g" "$TEMP_FILE"
sed -i "s/{{modules}}/$MODULES_ESC/g" "$TEMP_FILE"
sed -i "s/{{generation_date}}/$GENERATION_DATE_ESC/g" "$TEMP_FILE"
sed -i "s/{{generation_time}}/$GENERATION_TIME_ESC/g" "$TEMP_FILE"

# For multi-line replacements, use a different approach
# Replace source_files_links
awk -v links="$SOURCE_FILES_LINKS" '{gsub(/\{\{source_files_links\}\}/, links); print}' "$TEMP_FILE" > "$TEMP_FILE.tmp" && mv "$TEMP_FILE.tmp" "$TEMP_FILE"

# Replace knowledge_base_links
awk -v links="$KNOWLEDGE_BASE_LINKS" '{gsub(/\{\{knowledge_base_links\}\}/, links); print}' "$TEMP_FILE" > "$TEMP_FILE.tmp" && mv "$TEMP_FILE.tmp" "$TEMP_FILE"

# Replace official_docs_links
awk -v links="$OFFICIAL_DOCS_LINKS" '{gsub(/\{\{official_docs_links\}\}/, links); print}' "$TEMP_FILE" > "$TEMP_FILE.tmp" && mv "$TEMP_FILE.tmp" "$TEMP_FILE"

# Copy to output path
cp "$TEMP_FILE" "$OUTPUT_PATH"

# Trap will clean up temp files automatically

echo "Pre-filled template written to: $OUTPUT_PATH"
echo ""
echo "Pre-filled placeholders (8/16):"
echo "  ✓ target_name: $TARGET_NAME"
echo "  ✓ generation_date: $GENERATION_DATE"
echo "  ✓ generation_time: $GENERATION_TIME"
echo "  ✓ target_description: $TARGET_DESC"
echo "  ✓ modules: $MODULES"
echo "  ✓ source_files_links: $(echo "$SOURCE_FILES" | tr ',' '\n' | wc -l) files"
echo "  ✓ knowledge_base_links: $(echo "$KNOWLEDGE_FILES" | tr ',' '\n' | wc -l) files"
echo "  ✓ official_docs_links: $(if [[ -n "$OFFICIAL_DOCS" ]]; then echo "$OFFICIAL_DOCS" | tr ',' '\n' | wc -l; else echo 0; fi) links"
echo ""
echo "Remaining placeholders for LLM (8/16):"
echo "  - analysis_duration (to be filled after Write completes)"
echo "  - overview_content"
echo "  - dependency_graph"
echo "  - component_summary_table"
echo "  - flow_content"
echo "  - flow_sequence_diagram"
echo "  - components_details"
echo "  - nablarch_usage"
