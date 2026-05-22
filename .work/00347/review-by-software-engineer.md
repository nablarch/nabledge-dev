# Expert Review: Software Engineer

**Date**: 2026-05-22
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: xlsx_common.py, verify.py, docs.py (source code changes)

## Summary

0 Findings

## Findings

None.

## Observations

- **O1** — `docs.py` `_render_full`: the `P1-merged` branch and the plain `P1` branch call `_render_xlsx_p1(data)` with identical arguments, making the first branch dead code by effect. Not a spec violation — both branches produce correct output. A cleanup to a single `if sheet_type == "P1": return _render_xlsx_p1(data)` would be clearer, but the explicit branch matches the established P2-1/P2-3/P2-4 pattern and documents the intent.
- **O2** — `verify.py`: `from collections import Counter` was deferred inside the `if sheet_subtype == "P1-merged":` block, deviating from the module-level import style. **Fixed in follow-up commit** (moved to top-level imports).
- **O3** — `_read_title_col_merge_groups` (verify) does not skip empty rows unlike `_build_merge_groups` (converter). Safe because verify callers apply `non_empty_groups` filter. Worth documenting in the function docstring.
- **O4** — No test for inter-group empty row in verify's P1-merged path. The `non_empty_groups` filter logic is correct; this is an optional coverage improvement.

## Positive Aspects

1. verify independence is correctly maintained — `_read_title_col_merge_groups` is a complete reimplementation from the openpyxl spec.
2. Both QP and QC1/QC3 are correctly extended for P1-merged; the token stream emits title + per-row column-value pairs in the correct JSON-text order.
3. Test quality is high — covers correct output, missing tail-row value, missing group title, QP section-count pass and fail, and standard P1 regression guard.
4. `_build_merge_groups` correctly clips merged ranges that partially precede `data_start` using `start = max(min_row, data_start)`.
5. docs.py correctly routes P1-merged through `_render_xlsx_p1` which uses all-rows `data_rows`, ensuring QO2 containment for tail-row values.

## Files Reviewed

- `tools/rbkc/scripts/create/converters/xlsx_common.py` (source code)
- `tools/rbkc/scripts/verify/verify.py` (source code)
- `tools/rbkc/scripts/create/docs.py` (source code)
