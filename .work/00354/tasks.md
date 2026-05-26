# Tasks: test-setup.sh — branch selection, metrics collection, and persistent report files

**PR**: #355
**Issue**: #354
**Updated**: 2026-05-26 (complete)

## Fact-Based Work Rule

すべての調査・実装・判断は事実ベースで行う。推測・仮定で進めない。
- 実装前に対象ファイルを実際に読んで構造を確認する
- stream-json の出力フィールドは実機確認済み（`type:result` 行に `total_cost_usd` / `usage.input_tokens` / `usage.output_tokens` / `duration_ms` が含まれる）
- jq 利用可能確認済み（/usr/bin/jq 1.7）
- `tools/tests/reports/` は `.gitignore` に記載なし → git-tracked になる

## In Progress

### Task 11: Apply user feedback + generate final reports

**Feedback implemented (v6 confirmed, not yet committed):**
- Report: add Commit row (`gh api repos/.../commits/{branch}` → 7-char SHA)
- Report: Static Checks table add Notes column (FAIL detail text)
- Dynamic: GHC output tokens from `assistant.message.data.outputTokens` sum (input still N/A — not in GHC JSON output, confirmed via docs research)

**v6 run results (not yet user-approved):**
- main v6: `main-20260526-171030.md` — Static FAIL (knowledge/ 9 files, expected 10), Dynamic CC FAIL (answered: no — missing 根拠/参照), GHC PASS
- develop v6: `develop-20260526-170500.md` — Static PASS, Dynamic CC PASS, GHC PASS

**Open question from user:**
- main CC FAIL (answered: no) is under investigation — CC returned answer without 根拠/参照 sections; GHC returned correct format. Root cause unclear (LLM variance? knowledge deficit?). User was reviewing when session ended.

**Steps:**
- [x] Implement 3 feedback items in test-setup.sh
- [x] Run main v6 and develop v6 — reports generated
- [x] Show reports to user
- [x] [DECISION: main CC FAIL (answered: no) — expected behavior (knowledge file shortage), proceed]
- [x] Add FAIL detail notes to Dynamic Checks (missing sections / out of order)
- [x] Run `NABLEDGE_BRANCH=main bash tools/tests/test-setup.sh` (all versions)
- [x] Run `NABLEDGE_BRANCH=develop bash tools/tests/test-setup.sh` (all versions)
- [x] Commit test-setup.sh changes + all final reports and push — committed `4175549c0`

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
