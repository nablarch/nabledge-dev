# Expert Review: QA Engineer — Step 2/3 (#307)

**Date**: 2026-04-24
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: `tools/benchmark/tests/test_classify_terms.py`, `tools/benchmark/tests/test_build_index.py`

## Overall Assessment

**Rating**: 3.5/5 → 4.5/5 after fixes.
**Summary**: Happy path and first-order edge cases covered well. Frozen
parameter boundaries and filter-interaction invariants were not pinned,
leaving room for silent regressions. Addressed High-priority tests below.

## Key Issues

### High Priority

1. **fallback_df_max boundary not pinned** (`<=` vs `<` regression risk).
   - Decision: **Implement Now** — `test_select_fallback_df_max_is_inclusive`.
2. **tf_threshold boundary not pinned** (`>=` vs `>` regression risk).
   - Decision: **Implement Now** — `test_select_primary_tf_threshold_is_inclusive` + higher-value variant.
3. **Primary empty AND fallback empty path** (multi-term) not tested.
   - Decision: **Implement Now** — `test_select_both_paths_empty_returns_empty`.
4. **df-respects-filters test did not exercise "survives in one section, filtered in another"**.
   - Decision: **Implement Now** — `test_compute_candidates_df_excludes_section_where_term_filtered`.

### Medium Priority

5. **Double-exclusion (stoplist AND title overlap)** — **Implement Now**
   (`test_compute_candidates_double_exclusion_stoplist_and_title`).
6. **iter_sections shape variants** (string body / non-string body / malformed
   JSON / non-dict sections value) — **Implement Now** (4 tests).
7. **tokenize test used `set()` and lost order contract** — **Implement Now**
   (`test_tokenize_mixed_and_atomic_in_stable_order` + preserves document order).
8. **Adjacent / repeated katakana** — **Defer** (covered by repeated-occurrence test).
9. **All-equal-TF top-N cutoff determinism** — **Implement Now**
   (`test_select_primary_tie_break_at_top_n_cutoff`).
10. **build_index.collect — keyword_map extra keys silently ignored** — **Implement Now**
    (`test_collect_ignores_unmapped_keyword_keys`).

### Low Priority

- **L11** `collect` index-entry shape variants — **Implement Now**
  (`test_collect_skips_bad_index_entries`).
- **L12** `top_n=0` corner case — **Defer** (not a real use case).
- **L13** Header count assertion — **Defer**.

## Positive Aspects

- `_sel` helper binds frozen defaults; tests pin the frozen contract.
- `test_compute_candidates_skips_no_knowledge_content` checks both per_sec and df.
- `test_select_primary_wins_over_fallback_when_any_primary_exists` pins a key invariant.
- No `pytest.mark.skip` / `importorskip`.

## Recommendations

- High + most Medium addressed in this PR.
- Added a module-level docstring note pointing at `.work/00307/index-params-decision.md`
  so future edits know these tests pin a frozen contract.
- Final test count: 96 passing (up from 78 before Step 2/3 started).
