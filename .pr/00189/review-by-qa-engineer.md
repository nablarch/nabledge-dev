# Expert Review: QA Engineer

**Date**: 2026-03-13
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 1 file

## Overall Assessment

**Rating**: 4/5
**Summary**: `TestV1xVersions` is well-structured and consistent with existing test patterns. Tests are clear, focused, and exercise correct routing logic for all three v1.x versions.

## Key Issues

### Medium Priority

1. **Missing `--resume` coverage for v1.x gen**
   - Description: `TestGenCommand` has `test_gen_resume_skips_clean` for v6 but no equivalent for v1.x.
   - Suggestion: Add parametrized `test_gen_v1x_resume_skips_clean` asserting 1 command with `scripts/run.py`.
   - Decision: **Implement Now** — added `test_gen_v1x_resume_skips_clean` test.
   - Reasoning: Closes a real behavioral gap with minimal effort.

2. **regen/fix tests don't assert `scripts/run.py`**
   - Description: Assertions check flags but not which script is called, unlike gen test.
   - Suggestion: Add `assert "scripts/run.py" in lines[0]` to regen and fix tests.
   - Decision: **Implement Now** — added to both tests.
   - Reasoning: Tightens routing verification consistently with gen test.

### Low Priority

3. **Split dual assertion in test_gen_v1x_calls_clean_then_run**
   - Description: Single `and`-joined assertion makes failure messages less specific.
   - Suggestion: Split into two separate assertions.
   - Decision: **Defer** — correct behavior, style preference only.
   - Reasoning: Low value change; existing test pattern uses same style.

4. **No `returncode` assertion in success cases**
   - Description: Tests pass even if kc.sh exits with error after printing CMD lines.
   - Suggestion: Add `assert result.returncode == 0` — ideally backported to whole file.
   - Decision: **Defer** — whole-file refactor; follow-up.
   - Reasoning: Existing tests have same gap; out of scope for this PR.

## Positive Aspects

- Parametrize approach efficiently covers all three versions without duplication.
- Version argument assertion in regen/fix is an improvement over existing v6 tests.
- New class is self-contained and doesn't interfere with existing classes.
- Test naming follows established `test_{command}_{context}_{behavior}` convention.
- Failure message in gen test includes version for clear parametrized failure diagnosis.

## Recommendations

- Add `returncode` assertions as a follow-up for the whole file.

## Files Reviewed

- `tools/knowledge-creator/tests/ut/test_kc_sh.py` (tests)
