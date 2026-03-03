# Improvement Decisions: Step 52-53 Expert Reviews

**Date**: 2026-03-03
**Reviews**: Prompt Engineer (4/5), Software Engineer (4/5)
**Total Issues**: 7 items (0 High, 5 Medium, 2 Low)

## Summary

Evaluated all 7 improvement suggestions from expert reviews. **Decision: Implement 5 items** addressing validation, logging, and prompt clarity. Defer 2 items that are polish improvements not critical for current scope.

## Decisions by Priority

### High Priority: 0 items

No high priority issues identified.

### Medium Priority: 5 items

| # | Issue | Expert | Decision | Reasoning |
|---|-------|--------|----------|-----------|
| M1 | "not empty" check ambiguity in generate.md | Prompt Engineer | **Defer to Future** | Current wording "If this list is not empty" is sufficient for Claude to interpret. Field testing has not revealed confusion. Incremental improvement, not critical. |
| M2 | Missing section count validation in generate.md | Prompt Engineer | **Implement Now** | Adds defensive validation to catch section skipping bugs. Directly addresses original issue (missing sections). Low cost, high value. |
| M3 | No structural validation in content_check.md | Prompt Engineer | **Defer to Future** | Out of scope for current bug fix. Current checklist is comprehensive for knowledge file validation. Prompt file hygiene is valuable but not urgent. |
| M4 | Missing error handling for section_range structure in phase_b_generate.py | Software Engineer | **Implement Now** | Prevents KeyError/TypeError if `section_range` exists but `sections` key missing. Defensive programming best practice. |
| M5 | Inconsistent handling of empty sections list in phase_b_generate.py | Software Engineer | **Implement Now** | Included in M4 fix. Check `isinstance(list)` and `len > 0` before formatting. Prevents empty bullet list in prompt. |
| M6 | No logging of sections count in phase_b_generate.py | Software Engineer | **Implement Now** | Adds observability for large files (65 sections in tag_reference.rst). Log only when count > 10 to reduce noise. Helps debugging. |

### Low Priority: 2 items

| # | Issue | Expert | Decision | Reasoning |
|---|-------|--------|----------|-----------|
| L1 | Variable naming `sections_md` could be more descriptive | Software Engineer | **Defer to Future** | Current name follows markdown suffix pattern. Acceptable clarity. Renaming has no functional benefit. |
| L2 | Comment could explain "why" more clearly | Software Engineer | **Implement Now** | Small improvement, easy to implement. Changes "Pass expected sections list if file was split" to "Pass detected section list to prevent Claude from missing sections (especially for large split files)". |

## Implementation Plan

### Change 1: Add section count validation to generate.md (M2)

**File**: `tools/knowledge-creator/prompts/generate.md`
**Location**: "Final self-checks before output" section (near end of file)
**Change**: Add checklist item:
```markdown
- [ ] If Expected Sections was provided, section count equals expected count
```

### Change 2: Add validation and logging to phase_b_generate.py (M4, M5, M6, L2)

**File**: `tools/knowledge-creator/steps/phase_b_generate.py`
**Location**: Lines 104-110 in `_build_prompt()` method

**Before**:
```python
# Pass expected sections list if file was split
if "section_range" in file_info and "sections" in file_info["section_range"]:
    sections_list = file_info["section_range"]["sections"]
    sections_md = "\n".join(f"- {s}" for s in sections_list)
    prompt = prompt.replace("{EXPECTED_SECTIONS}", sections_md)
else:
    prompt = prompt.replace("{EXPECTED_SECTIONS}", "(empty - scan the source yourself)")
```

**After**:
```python
# Pass detected section list to prevent Claude from missing sections (especially for large split files)
if "section_range" in file_info and "sections" in file_info["section_range"]:
    sections_list = file_info["section_range"]["sections"]
    if isinstance(sections_list, list) and sections_list:
        if len(sections_list) > 10:
            print(f"    Passing {len(sections_list)} detected sections to Claude")
        sections_md = "\n".join(f"- {s}" for s in sections_list)
        prompt = prompt.replace("{EXPECTED_SECTIONS}", sections_md)
    else:
        prompt = prompt.replace("{EXPECTED_SECTIONS}", "(empty - scan the source yourself)")
else:
    prompt = prompt.replace("{EXPECTED_SECTIONS}", "(empty - scan the source yourself)")
```

## Deferred Items (2)

| Issue | Reasoning |
|-------|-----------|
| M1: "not empty" check ambiguity | Current wording sufficient. Can refine if field testing reveals confusion. |
| M3: content_check.md structural validation | Out of scope. Prompt file hygiene valuable but not urgent for bug fix. |
| L1: Variable naming improvement | No functional benefit. Current name acceptable. |

## Testing Plan

After implementing changes:
1. Run full test suite: `cd tools/knowledge-creator && python -m pytest tests/ -v`
2. Verify logging output for files with >10 sections (use test-files-top3.json)
3. Verify section count validation appears in prompt template

## Impact Assessment

**Prompt Engineer improvements**: Strengthens validation to catch section skipping bugs. No breaking changes.

**Software Engineer improvements**: Adds defensive programming (validation) and observability (logging). No breaking changes. Backward compatible with files lacking section_range field.

**Risk**: Low - All changes are additive safeguards. Existing functionality preserved via fallback logic.
