# Expert Review: Software Engineer

**Date**: 2026-03-30
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 1 file

## Overall Assessment

**Rating**: 4/5
**Summary**: The fix correctly aligns SLOC trend chart x-axis labels with the ISO week Monday convention used by DORA/Activity charts. Deduplication logic is sound. Minor code quality improvements were applied based on review feedback.

## Key Issues

### Medium Priority

1. **Silent truncation of legacy data on first run**
   - Description: When `sloc_history` contained multiple legacy entries mapping to the same ISO week Monday (e.g., `2026-03-25` and `2026-03-28` both becoming `03/23`), the render-side deduplication would silently discard one entry, while the snapshot retained both as wasted slots (reducing effective 8-week window).
   - Suggestion: Normalize `sloc_history` by ISO week Monday key in `main()` on write, not just in `render_sloc_section` on read.
   - Decision: Implement Now
   - Reasoning: Clean fix; eliminates the inconsistency window between snapshot and rendered chart. The `seen_by_monday` dict approach is idiomatic and no-op once legacy data ages out.

### Low Priority

2. **Nested function `_week_label_for` adds cognitive overhead**
   - Description: Two-line helper defined inside `render_sloc_section` with no reuse outside.
   - Suggestion: Inline as a lambda.
   - Decision: Implement Now
   - Reasoning: Simple change, reduces indentation level and removes a named function that serves no structural purpose.

3. **Variable name `hist_labels_all` misleading**
   - Description: The `_all` suffix implies a superset, but there is no counterpart. It is simply the single label list for all charts.
   - Suggestion: Rename to `hist_labels` and remove per-block reassignment.
   - Decision: Implement Now
   - Reasoning: Cleaner and consistent with usage.

## Positive Aspects

- Root cause correctly identified: two different x-axis normalization strategies
- Defense-in-depth: deduplication on both read (render) and write (snapshot) paths
- Reuses existing `iso_week_monday` and `week_label` helpers
- `oldest-first; later entries overwrite` comment makes deduplication intent explicit

## Recommendations

- The snapshot will self-heal legacy non-Monday entries on the next scheduled run — no manual migration needed. Worth noting in the PR description.

## Files Reviewed

- `tools/metrics/collect.py` (source code)
