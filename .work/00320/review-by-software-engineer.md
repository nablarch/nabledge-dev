# Expert Review: Software Engineer

**Date**: 2026-05-07
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 3 files (Task 10 changes)

## Summary

0 Findings (after fix applied)

## Findings (original — all fixed)

### Finding 1: Display-text `:ref:` form skips cross-doc target validation

**Violated clause**: Spec §3-2-3 table, row 2: `| inline role=ref | 同上 (label 側から解決) | ... | verify 検証 (JSON side) 同上 | verify 検証 (docs MD side) 同上 |` — "同上" means the same cross-doc check applies to all `inline role=ref` nodes, not only bare-label form.

**Description**: The entire cross-doc block sat inside `if not display and label not in seen_labels:`. When `:ref:`My Title <cross-doc-label>`` is used, `display` is non-empty, so target JSON existence, section_title, and anchor slug are never validated. A dangling cross-doc ref with explicit display text silently passes.

**Fix applied**:
- Extracted cross-doc validation into nested helper `_check_crossdoc_target(tgt)` inside `check_source_links()`, replacing the inline block.
- Display-text path now resolves `label_map.get(label)` and calls `_check_crossdoc_target()` for non-`UNRESOLVED` targets (guarded by `seen_crossdoc_labels` for deduplication).
- Bare-label path calls the same `_check_crossdoc_target()` helper.
- Added `seen_crossdoc_labels` to prevent double-reporting when the same label appears in both forms.
- Added test `test_fail_crossdoc_ref_display_text_form_json_missing` — confirmed RED before fix, GREEN after.

## Observations

1. **`_section_titles_from_json` docstring inconsistency**: Line 1793 says "(lowercased for matching)" while line 1795 says "Returns titles as-is (not slugged)". The function body is correct; the first docstring line is a residue. No behavioral impact.

2. **Silent exception swallowing**: `_section_titles_from_json` uses bare `except Exception: return set()`. A corrupt target JSON returns empty set, causing "section_title not found in sections[]" rather than "JSON failed to parse". No false negative — still produces a FAIL — but the diagnostic quality is reduced.

3. **Thin wrapper functions in `check_ql1_link_targets`**: `_heading_slugs()` and `_json_section_slugs()` are now one-liners that delegate to module-level helpers. Could be inlined for less indirection. No behavioral impact.

## Positive Aspects

- The promotion of `_heading_slugs_from_md` and `_section_titles_from_json` to module level correctly eliminates duplication between the two check functions.
- The `_check_crossdoc_target` helper follows the principle of sharing logic via a single path — future changes to the four-check cascade need to be made in one place only.
- `seen_crossdoc_labels` dedup is architecturally correct — it is keyed on label (the stable identifier), not on file_id, so same-file references with different display texts are still deduplicated.
- The `run.py` change is minimal: reuses the already-computed `docs_dir` value with no new logic.
- 313/313 tests pass.

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source code)
- `tools/rbkc/tests/ut/test_verify.py` (tests)
- `tools/rbkc/scripts/run.py` (plumbing)
