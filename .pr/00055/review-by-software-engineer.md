# Expert Review: Software Engineer

**Date**: 2026-02-20
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 3 files

## Overall Assessment

**Rating**: 3.5/5
**Summary**: Functional shell scripts with clear purpose and decent documentation, but lacking critical error handling, proper quoting, and some fragile parsing patterns that could fail on edge cases.

## Key Issues

### High Priority

1. **Missing error handling for file operations**
   - Description: Both scripts perform file operations (reading, writing) without checking for permission errors or I/O failures. The `set -e` only catches exit codes, not partial failures or permission issues.
   - Suggestion: Add explicit error checks after critical operations:
   ```bash
   if ! cp "$TEMP_FILE" "$OUTPUT_PATH"; then
       echo "Error: Failed to write output file: $OUTPUT_PATH" >&2
       rm -f "$TEMP_FILE"
       exit 1
   fi
   ```

2. **Unsafe variable substitution in sed operations**
   - Description: In `prefill-template.sh`, the `escape_sed()` function only escapes `&`, `/`, and `\` but misses other sed special characters like newlines in multi-line variables. The subsequent awk approach for multi-line is better but inconsistent.
   - Suggestion: Use a consistent approach for all replacements. Either use `awk` for all (not just multi-line) or use a here-document approach with proper escaping:
   ```bash
   # More robust approach
   perl -pe "s/\Q{{placeholder}}\E/\Q$ESCAPED_VALUE\E/g" "$TEMP_FILE"
   ```

3. **Fragile Java parsing with grep/sed**
   - Description: `generate-mermaid-skeleton.sh` uses regex patterns that assume specific Java code formatting (e.g., class declarations on one line, specific whitespace patterns). This will break with multi-line class declarations, annotations, or comments.
   - Suggestion: Add warnings about limitations in documentation, or use a proper Java parser (e.g., `jq` with a Java AST tool, or Python with `javalang`). At minimum, add fallback handling:
   ```bash
   if [[ -z "$class_name" ]]; then
       echo "Warning: Could not parse class name from $file" >&2
       continue
   fi
   ```

4. **Unquoted variable expansions**
   - Description: Multiple instances of unquoted variables that could cause word splitting or glob expansion issues (e.g., `dirname "$OUTPUT_PATH"` is quoted but later uses like `for file in "${FILES[@]}"` are good, but `file=$(echo "$file" | xargs)` could be replaced with parameter expansion).
   - Suggestion: Apply shellcheck and fix all SC2086 warnings. Example:
   ```bash
   # Instead of: file=$(echo "$file" | xargs)
   file="${file#"${file%%[![:space:]]*}"}"  # trim leading
   file="${file%"${file##*[![:space:]]}"}"  # trim trailing
   ```

### Medium Priority

1. **Inconsistent error output**
   - Description: Some errors go to stdout, others to stderr. In `prefill-template.sh`, validation errors use `echo "Error: ..."` (stdout) but should use stderr. `generate-mermaid-skeleton.sh` correctly uses `>&2` for some errors but not all.
   - Suggestion: Consistently send all error messages to stderr:
   ```bash
   echo "Error: Missing required arguments" >&2
   ```

2. **No input validation for file paths**
   - Description: Scripts accept file paths but don't validate they exist or are readable before processing. `generate-mermaid-skeleton.sh` checks in `parse_java_file()` but only after starting processing.
   - Suggestion: Add upfront validation:
   ```bash
   IFS=',' read -ra FILES <<< "$SOURCE_FILES"
   for file in "${FILES[@]}"; do
       file=$(echo "$file" | xargs)
       if [[ ! -f "$file" ]]; then
           echo "Error: File not found: $file" >&2
           exit 1
       fi
       if [[ ! -r "$file" ]]; then
           echo "Error: File not readable: $file" >&2
           exit 1
       fi
   done
   ```

3. **Hardcoded heuristics without configuration**
   - Description: `generate-mermaid-skeleton.sh` uses hardcoded patterns like `(Dao|Service|Form|Entity|Util|Manager|Handler)` and Nablarch prefix matching. These won't work for projects with different naming conventions.
   - Suggestion: Add optional configuration file or command-line options for custom patterns:
   ```bash
   --participant-patterns "Dao,Service,Custom"
   --framework-prefixes "Universal,Business,MyFramework"
   ```

4. **Temporary file cleanup not guaranteed**
   - Description: `prefill-template.sh` creates a temp file but only removes it on success path. If the script is interrupted or fails after temp file creation, it's left behind.
   - Suggestion: Use trap to ensure cleanup:
   ```bash
   TEMP_FILE=$(mktemp)
   trap 'rm -f "$TEMP_FILE" "$TEMP_FILE.tmp"' EXIT INT TERM
   ```

5. **Complex bash associative arrays in sequence diagram**
   - Description: The sequence diagram generation uses bash associative arrays and complex parsing logic that's hard to maintain and debug. The heuristics for guessing method calls are fragile.
   - Suggestion: Consider documenting this is a "best effort" skeleton that requires manual review, or simplify to just output participants without guessing call sequences.

### Low Priority

1. **Magic numbers without explanation**
   - Description: Line like `LEVEL_COUNT=$(echo "$OUTPUT_DIR" | tr -cd '/' | wc -c)` calculates directory depth but assumes a specific project structure without documentation.
   - Suggestion: Add comments explaining the calculation:
   ```bash
   # Count directory depth to calculate relative path
   # e.g., .nabledge/20260220 = 2 levels, needs ../../
   LEVEL_COUNT=$(echo "$OUTPUT_DIR" | tr -cd '/' | wc -c)
   ```

2. **Inconsistent string processing**
   - Description: Mix of `sed`, `awk`, `xargs`, and parameter expansion for string manipulation. While functional, this makes the code harder to read and maintain.
   - Suggestion: Standardize on parameter expansion where possible for clarity and portability:
   ```bash
   # Instead of: filename=$(basename "$file" .java)
   filename="${file##*/}"
   filename="${filename%.java}"
   ```

3. **No logging or debug mode**
   - Description: Scripts have no verbose/debug mode for troubleshooting. When something goes wrong, users can't easily see what the script is doing.
   - Suggestion: Add optional debug mode:
   ```bash
   DEBUG=${DEBUG:-0}
   debug() { [[ $DEBUG -eq 1 ]] && echo "[DEBUG] $*" >&2; }

   # Usage: DEBUG=1 ./script.sh --args
   ```

4. **README examples lack error handling guidance**
   - Description: `scripts/README.md` shows usage examples but doesn't mention error handling, exit codes, or what to do when scripts fail.
   - Suggestion: Add troubleshooting section:
   ```markdown
   ## Troubleshooting

   Scripts exit with code 0 on success, non-zero on failure:
   - Exit code 1: Invalid arguments or file not found
   - Exit code 2: Processing error

   Enable debug output: `DEBUG=1 ./script.sh`
   ```

## Positive Aspects

- **Clear single responsibility**: Each script has a well-defined purpose and doesn't try to do too much
- **Good argument parsing**: Uses standard long-form arguments with clear validation
- **Helpful usage messages**: Both scripts provide comprehensive help text with examples
- **Consistent style**: Code follows similar patterns and conventions across both scripts
- **Documentation integration**: README clearly explains how scripts fit into the workflow and expected time savings
- **Practical optimization**: Scripts address a real problem (100s → 45-55s) with measurable benefits
- **Reasonable assumptions**: The heuristics in diagram generation are sensible for the target domain (Nablarch framework)

## Recommendations

1. **Short term**: Run `shellcheck` on both scripts and fix all warnings (especially SC2086 for unquoted variables)

2. **Error handling**: Add trap-based cleanup and explicit error checks for all file operations

3. **Testing**: Create a test suite with edge cases:
   - Empty input files
   - Files with special characters in names
   - Multi-line Java class declarations
   - Non-existent files
   - Permission errors

4. **Documentation**: Add a "Limitations" section to README explaining:
   - Java parsing assumes standard formatting
   - Diagrams are skeletons requiring manual refinement
   - Scripts designed for Nablarch conventions

5. **Future enhancement**: Consider rewriting the Java parser in Python with `javalang` library for more robust parsing, while keeping the shell script as a wrapper for the workflow integration.

## Files Reviewed

- `/home/tie303177/work/nabledge/work7/scripts/prefill-template.sh` (shell script - 224 lines)
- `/home/tie303177/work/nabledge/work7/scripts/generate-mermaid-skeleton.sh` (shell script - 282 lines)
- `/home/tie303177/work/nabledge/work7/scripts/README.md` (documentation - 124 lines)
