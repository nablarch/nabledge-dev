# Expert Review: Software Engineer

**Date**: 2026-04-10
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 2 files

## Overall Assessment

**Rating**: 4/5
**Summary**: The `verify_dynamic` function has been successfully enhanced to replace stub implementation with real CLI invocations. Well-structured with good separation of concerns and proper error handling. The single-source-of-truth approach for scenarios.json and marker-based extraction are particularly strong. Several areas could be hardened with better error handling and defensive programming.

## Key Issues

### High Priority

1. **Python error handling missing in `_scenario_field`**
   - Description: No try-except — if scenarios.json is missing, ID not found, or JSON malformed, a Python traceback is silently captured into `$Q_V6` / `$KW_V6`, causing cryptic failures downstream
   - Proposed fix: Add try-except with clear error messages and `sys.exit(1)`
   - Decision: Implement Now

2. **No validation that marker extraction produces non-empty prompt**
   - Description: If sed extraction (lines ~324, ~359) produces empty output, empty prompts are passed to CLI tools. The 100-byte check catches this after wasting 120s timeout
   - Proposed fix: Validate `[ -z "$prompt" ]` immediately after extraction
   - Decision: Implement Now

3. **sed replacement with `$query` may break on special characters**
   - Description: `sed "s|\$ARGUMENTS|${query}|g"` — if query contains `|`, `\`, or `&`, sed replacement fails or produces incorrect output
   - Proposed fix: Use bash native substitution `${prompt//\$ARGUMENTS/$query}` instead of sed
   - Decision: Defer (queries come from controlled scenarios.json; Japanese text has no sed metacharacters — low practical risk)

### Medium Priority

4. **50% detection rate threshold undocumented**
   - Description: `min_threshold=50` has a comment but no explanation of the basis for the value
   - Proposed fix: Expand comment to reference nabledge-test baseline rationale
   - Decision: Implement Now (easy, improves maintainability)

5. **GHC temp file not cleaned up on early exit**
   - Description: If the `cp` or `echo` fails mid-function, temp file in `$project_dir` is orphaned
   - Proposed fix: Add error handling around temp file creation
   - Decision: Defer (existing `|| true` and EXIT trap cover normal failures; edge case)

### Low Priority

6. **Model name difference between CC and GHC undocumented**
   - Description: CC uses `--model haiku`, GHC uses `--model claude-haiku-4.5` — no comment explaining why they differ
   - Proposed fix: Add inline comment
   - Decision: Implement Now (trivial)

## Positive Aspects

- Strong separation of concerns: `verify_env` / `verify_dynamic` / `_scenario_field` have clean boundaries
- Single source of truth: scenarios.json extraction eliminates hardcoded duplication
- Marker-based extraction is maintainable and documented in `.claude/rules/nabledge-skill.md`
- Comprehensive error detection per function (missing files, missing markers, response length, keyword rate)
- Timeout protection on all CLI invocations (120s)
- Upgrade scenario (two-version coexistence) expands coverage meaningfully

## Recommendations

- Extract `CC_MARKER` / `GHC_MARKER` as script-top constants (currently defined inline)
- Consider `VERBOSE=1` mode to log extracted prompts for debugging
- Normalize model version references (haiku vs claude-haiku-4.5) into a single constant

## Files Reviewed

- `tools/tests/test-setup.sh` (shell script)
- `.claude/rules/nabledge-skill.md` (documentation)
