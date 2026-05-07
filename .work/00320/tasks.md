# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-07

## Not Started

### Task 7: Update design doc §4 matrix
Update `rbkc-verify-quality-design.md` §4 matrix QL1 rows from ⚠️ to ✅.

**Blocked**: ✅ 成立条件3 — "v6 実データに対して verify FAIL 0 件" — が未達。
v6で656件のanchor FAILが新たに検出された。これはRBKCの出力バグであり、
verify実装は正しい。design doc ✅ 更新はRBKC anchor修正後（別Issue）。

## Done

- [x] Issue #320 fetched and analyzed
- [x] Branch `320-verify-ql1-link-targets` created
- [x] PR #330 created
- [x] Existing implementation in `check_ql1_link_targets()` confirmed: `_anchor` extracted but silently discarded
- [x] Design spec §3-2-3 confirmed: two missing checks identified
- [x] `github_slug.py` confirmed available in `scripts/common/`
- [x] Test correspondence table in §4 confirmed: `TestCheckSourceLinks_JsonSide` and `TestCheckSourceLinks_DocsMdSide` are the planned test classes
- [x] Task 1: Design review completed — §3-2-3 fully covers both checks; no design doc changes needed pre-implementation
- [x] Task 2: `TestCheckSourceLinks_JsonSide` added (4 tests, confirmed RED) — committed `197bc96`
- [x] Task 3: `TestCheckSourceLinks_DocsMdSide` added (4 tests including fenced-block test, confirmed RED) — committed `197bc96`
- [x] Task 4: JSON side anchor check implemented — `_json_section_slugs()`, dedup via `missing_json` + `seen_anchors` — committed `38e18cc`
- [x] Task 5: Docs MD side anchor check implemented — `_heading_slugs()` with `_strip_fenced_code`, dedup via `missing_md` + `seen_md_anchors` — committed `38e18cc`
- [x] Task 6: FAIL diff recorded — v6:656 v5:658 v1.4:613 v1.3:578 v1.2:588 (all new, genuine RBKC bugs, no unexpected increase) — committed `3928aa4`
- [x] Task 8: Expert review (QA + SE) — 2 Findings each, all fixed (dedup bug + fenced-block phantom slug) — committed `3928aa4`
- [x] Task 9: Diff check — only `verify.py`, `test_verify.py`, `.work/00320/` changed (expected scope)
