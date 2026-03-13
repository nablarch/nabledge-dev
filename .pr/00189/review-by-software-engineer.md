# Expert Review: Software Engineer

**Date**: 2026-03-13
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 5 files

## Overall Assessment

**Rating**: 4/5
**Summary**: Changes correctly add infrastructure for Nablarch v1.x with a well-designed fallback path strategy. Core logic is sound, backward-compatible, and avoids invasive refactoring.

## Key Issues

### Medium Priority

1. **`--version all` silently excludes v1.x**
   - Description: `run.py` and `clean.py` expand `all` to only `["6", "5"]`. Help text now lists 1.4/1.3/1.2 as valid choices alongside `all`, which could mislead users into thinking `all` processes everything.
   - Suggestion: Add documentation to help text clarifying `all` covers v5 and v6 only.
   - Decision: **Implement Now** — updated help text in both `run.py` and `clean.py`.
   - Reasoning: Prevents user confusion at no implementation cost.

2. **Path style inconsistency between step1 and generate_expected**
   - Description: `step1_list_sources.py` uses f-strings while `generate_expected.py` uses `os.path.join` for equivalent logic.
   - Suggestion: Align styles across both files.
   - Decision: **Defer** — cosmetic, no bug risk on Linux; these files have always had divergent styles.
   - Reasoning: Low risk, not worth churn in this PR.

### Low Priority

3. **No warning when neither RST path exists**
   - Description: When docs aren't cloned, both paths fail silently with 0 sources and no user feedback.
   - Suggestion: Add `logger.warning` when neither path resolves.
   - Decision: **Implement Now** — added `else` branch with descriptive warning.
   - Reasoning: Surfaces setup errors early for v1.x users.

4. **No unit test for fallback path logic**
   - Description: The `{version}_maintain` fallback in `step1_list_sources.py` isn't directly tested.
   - Suggestion: Add a focused unit test using a temporary directory.
   - Decision: **Defer to Future** — requires temp directory scaffolding; follow-up issue.
   - Reasoning: Covered indirectly by E2E when docs are present; adequate for this PR.

## Positive Aspects

- The two-step fallback design preserves full backward compatibility for v5/v6.
- `releases_dir` derived from `rst_base` is the correct fix — old code would silently mismatch.
- Regex in `generate_expected.py` generalizes to any `*_maintain` directory pattern.
- `generate_expected.py` and `step1_list_sources.py` implement identical fallback logic.
- Symlink creation in `setup.sh` is idempotent and uses relative symlink target.
- Mapping files are in place, completing a coherent feature.

## Recommendations

- Add unit test for fallback path logic in a follow-up issue.

## Files Reviewed

- `tools/knowledge-creator/scripts/run.py` (source code)
- `tools/knowledge-creator/scripts/clean.py` (source code)
- `tools/knowledge-creator/scripts/step1_list_sources.py` (source code)
- `tools/knowledge-creator/tests/e2e/generate_expected.py` (source code)
- `setup.sh` (configuration/script)
