# Tasks: Move scan_sources and classify_sources to scripts/common/ for §2-2 compliance

**PR**: #329
**Issue**: #322
**Updated**: 2026-05-07

## In Progress

### Task 8: Fix expert review Findings (SE-F1 + QA-F1〜F4)

Expert review conducted this session. 5 Findings must be fixed before PR is shippable.

**SE-F1** — `common/sources.py` の `classify_sources` が `from scripts.create.converters.xlsx_common import list_sheet_names` をインポート → §2-2 違反。`list_sheet_names` を `common/sources.py` に移動して解決。

**QA-F1** — xlsx 単一シート（`len==1`）分岐のテストなし。mock で `list_sheet_names` を固定してテスト。

**QA-F2** — `classify_sources([])` 空入力テストなし。

**QA-F3** — 全テストが v6 のみ。v1.x パス（`iterdir()` + all-releasenote）未確認。

**QA-F4** — `scan_sources` の絶対パス入力成功パスのテストなし。

**Steps:**
- [ ] Write RED tests for SE-F1 (`from scripts.common.sources import list_sheet_names` fails), QA-F1〜F4
- [ ] Confirm all new tests RED
- [ ] Move `list_sheet_names` into `common/sources.py`; add re-export shim in `xlsx_common.py`; update `classify_sources` to use the local import
- [ ] Confirm all tests GREEN; run full suite (483+ pass)
- [ ] Save review results to `.work/00322/review-by-software-engineer.md` and `review-by-qa-engineer.md`
- [ ] Update PR #329 body Expert Review section with links

## Done

- [x] Created tasks.md — committed `a8c90fe71`
- [x] Task 1: Write TDD tests for scripts/common/sources module (RED) — committed `2a0881af1`
- [x] Task 2: Create scripts/common/sources.py (GREEN) — committed `2a0881af1`
- [x] Task 3: Update scripts/create/scan.py to re-export from scripts/common/sources — committed `571fd1c23`
- [x] Task 4: Update scripts/create/classify.py to re-export from scripts/common/sources — committed `571fd1c23`
- [x] Task 5: Update scripts/create/differ.py to import FileInfo from scripts/common/sources — committed `571fd1c23`
- [x] Task 6: Update scripts/run.py imports and run full test suite — committed `571fd1c23`
- [x] Task 7: Diff check and user confirmation before PR review request — diff-check.md created, all 483 tests pass
