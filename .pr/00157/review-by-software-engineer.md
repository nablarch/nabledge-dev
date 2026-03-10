# Expert Review: Software Engineer

**Date**: 2026-03-10
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 5 files

## Overall Assessment

**Rating**: 4/5
**Summary**: The refactoring is well-executed. Moving 37+ hardcoded Python constants to JSON files is the right architectural decision — it separates data from logic, enables version-specific overrides with a clean merge strategy, and removes a significant barrier to adding v5 support. The implementation is disciplined and consistent between the two modified files.

## Key Issues

### Medium Priority

1. **Stale error messages reference old RST_MAPPING and wrong file path**
   - Description: Lines in step2_classify.py still reference `RST_MAPPING` constant and `tools/knowledge-creator/steps/step2_classify.py` (non-existent path)
   - Suggestion: Update error messages to point to `mappings/common.json` or `vN.json`
   - Decision: Implement Now
   - Reasoning: Misleads developers trying to fix unmapped files

2. **`load_mappings` in step2_classify.py accepts `repo_dir` but never uses it**
   - Description: The function uses `__file__` for path resolution, making the `repo_dir` parameter misleading
   - Suggestion: Remove the parameter or document clearly it's unused
   - Decision: Implement Now
   - Reasoning: Misleading signature creates maintenance risk

### Low Priority

3. **Duplication between step2_classify.py and generate_expected.py `load_mappings`**
   - Description: Two implementations with slightly different path resolution (by design — generate_expected cannot import kc modules)
   - Decision: Defer — acceptable given the constraint, should be documented

4. **No error handling for malformed JSON**
   - Decision: Defer — acceptable for a dev tool with controlled input

## Positive Aspects

- Clean separation of data from logic
- Version-specific override design (prepend + merge) is intuitive
- Script-relative path resolution makes the tool self-contained
- Both implementations are consistent in their merge strategy

## Recommendations

- Document in generate_expected.py why load_mappings is duplicated (constraint: no kc imports)
- Consider adding JSON schema validation for mapping files in a future iteration
