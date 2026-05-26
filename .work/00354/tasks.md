# Tasks: test-setup.sh — branch selection, metrics collection, and persistent report files

**PR**: #355
**Issue**: #354
**Updated**: 2026-05-26

## Fact-Based Work Rule

すべての調査・実装・判断は事実ベースで行う。推測・仮定で進めない。
- 実装前に対象ファイルを実際に読んで構造を確認する
- stream-json の出力フィールドは実機確認済み（`type:result` 行に `total_cost_usd` / `usage.input_tokens` / `usage.output_tokens` / `duration_ms` が含まれる）
- jq 利用可能確認済み（/usr/bin/jq 1.7）
- `tools/tests/reports/` は `.gitignore` に記載なし → git-tracked になる

## In Progress

### Task 11: Generate final reports (main + develop, v6 first then all)

**Steps:**
- [ ] Run `NABLEDGE_BRANCH=main bash tools/tests/test-setup.sh v6` — confirm CC/GHC PASS, metrics complete, report generated
- [ ] Run `NABLEDGE_BRANCH=develop bash tools/tests/test-setup.sh v6` — confirm CC/GHC PASS, metrics complete, report generated
- [ ] Show both reports to user for approval
- [ ] After approval: run full pass for main (all versions)
- [ ] After approval: run full pass for develop (all versions)
- [ ] Commit all final reports and push

## Not Started

---

## Done

- [x] Task 1: Create `tools/tests/reports/` directory with `.gitkeep` — committed `738c5175e`
- [x] Task 2: Add metrics collection to `verify_dynamic` in `test-setup.sh` — committed `e03a125bc`
- [x] Task 3: Add static check results collection to `verify_env` in `test-setup.sh` — committed `e03a125bc`
- [x] Task 4: Add report generation function and write report file — committed `e03a125bc`, fixed `a53aaf51d`
- [x] Task 5: Preview report Markdown rendering — committed `18fc71f3e`
- [x] Task 6: Update README to document `main` branch testing and before/after comparison — committed `3858608d0`
- [x] Task 7: Diff check — committed `c644d86cd`
- [x] Task 8: Expert review (Software Engineer + QA Engineer) — 2 Findings found and fixed in `a53aaf51d`, committed `58f2de046`
- [x] Task 9: Fix answered/keyword detection for JSON log formats (CC + GHC) — committed `26b2a9655`
- [x] Task 10: Request user PR review
