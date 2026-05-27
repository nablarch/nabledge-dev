# Tasks: Fix dynamic check false positives in test-setup.sh

**PR**: #359
**Issue**: #358
**Updated**: 2026-05-27

## Ground Rules

- 推測で判断しない。変更前に対象コードを Read で確認し、事実として確認してから実装する
- 影響範囲は grep で実測する。「おそらく影響しない」は根拠にならない
- 各タスク完了後、テストで確認してから次に進む

## Not Started

### Task 1: Introduce WARN level for "sections out of order" dynamic check results

**What**: When `final_answer_text` contains all four section keywords but in wrong order,
the current code reports FAIL. This is a detection ambiguity — the answer may be correct
but formatted differently. It should be WARN (not FAIL, not OK) so operators can inspect.

**Background**: Re-running `NABLEDGE_BRANCH=main bash tools/tests/test-setup.sh` with the
updated script (post-main-merge) produced all OK. Bug 1 (CC: stream-json log preamble) and
Bug 2 (GHC: 「参照」verb in body) are already fixed in main. The remaining gap is that
"sections out of order" still maps to FAIL rather than WARN.

**Scope**: `tools/tests/test-setup.sh` — `verify_dynamic()` result classification block (~lines 503–528).
`verify_fail` counter must NOT be incremented for WARN (WARN does not cause exit code 1).

**Steps**:
- [ ] Read the result classification block (lines ~503–528) and confirm current FAIL conditions
- [ ] Add WARN branch: all four sections present in `final_answer_text` but out of order → `[WARN]`, result_status="WARN", do NOT set `verify_fail=1`
- [ ] Add WARN to the exit summary block (line ~690) so "X WARN(s)" is reported at the end
- [ ] Confirm that a genuine no-answer case (e.g. empty `final_answer_text`) still produces FAIL
- [ ] Commit: `feat: add WARN level for sections-out-of-order dynamic check results`

### Task 2: Add FAIL/WARN investigation procedure to README

**What**: README has no guidance on what to do when a dynamic check produces FAIL or WARN.
Operators must know: where is the log, what to look for, when to treat WARN as a true failure.

**Scope**: `README.md` — add a subsection under「動的チェック」or「開発バージョンのテスト」.

**Steps**:
- [ ] Read README.md lines ~64–95 (「開発バージョンのテスト」section) to understand current structure
- [ ] Write a subsection「FAIL / WARN が出た場合」covering:
  - Log file location (`.tmp/nabledge-test/dynamic-check-*.log`)
  - FAIL: SKILL.md not read → setup failure; answer missing → skill malfunction
  - WARN: sections detected but out of order → read log and confirm answer text contains 結論/根拠/注意点/参照 in correct order; if yes, it is a formatting variation, not a failure
  - True failure indicators: `final_answer_text` is empty, or keywords 0/N
- [ ] Commit: `docs: add FAIL/WARN investigation procedure to README`

### Task 3: Diff check and confirmation

**What**: Verify the full diff contains only the two intended changes and nothing extraneous.

**Steps**:
- [ ] Run `git diff main...HEAD -- tools/tests/test-setup.sh README.md` and review
- [ ] Confirm: only WARN branch and README subsection changed
- [ ] Save diff check result to `.work/00358/diff-check.md`
- [ ] Commit diff-check.md: `docs: add diff check result for #358`
- [ ] Report to user for confirmation before PR review request

## Done

