# Tasks: Fix dynamic check false positives in test-setup.sh

**PR**: TBD
**Issue**: #358
**Updated**: 2026-05-27

## Ground Rules

- 推測で判断しない。変更前に対象コードを Read で確認し、事実として確認してから実装する
- 影響範囲は grep で実測する。「おそらく影響しない」は根拠にならない
- 各タスク完了後、テストで確認してから次に進む

## Not Started

### Task 1: Fix `_has_sections` — match section headings only, not body text occurrences

**What**: `_has_sections` currently matches the first byte offset of any occurrence of 「参照」.
Body text like「`$OPTIONALNAME$`で参照するカラム名」is matched before the「**参照**」heading,
causing `n_chuui > n_sansho` and answered=0 (false FAIL).

**Scope**: `tools/tests/test-setup.sh` — `_has_sections()` only.
No other files affected (confirmed: `_has_sections` is defined and called only inside `verify_dynamic`).

**Fix**: Change regex to match only heading forms:
- `\*\*結論\*\*` or `## 結論` (and same for 根拠/注意点/参照)

**Steps**:
- [ ] Read `_has_sections` in `tools/tests/test-setup.sh` (lines ~473–484) and confirm current regex
- [ ] Confirm the GHC answer format by reading `.tmp/nabledge-test/dynamic-check-v1.3-test-ghc-nabledge-1.3.log` — verify section headings use `**結論**` form
- [ ] Update `_has_sections` to use heading-only pattern
- [ ] Run `bash tools/tests/test-setup.sh v1.3` (v1.3 only, cheapest reproduction) and confirm v1.3/test-ghc goes from FAIL to OK
- [ ] Commit: `fix: match section headings only in _has_sections to eliminate false positives`

### Task 2: Introduce WARN level for "sections out of order" dynamic check results

**What**: When `final_answer_text` contains all four section keywords but in wrong order,
the current code reports FAIL. This is a detection ambiguity — the answer may be correct
but formatted differently. It should be WARN (not FAIL, not OK) so operators can inspect.

**Scope**: `tools/tests/test-setup.sh` — `verify_dynamic()` result classification block (~lines 503–528).
`verify_fail` counter must NOT be incremented for WARN (WARN does not cause exit code 1).

**Steps**:
- [ ] Read the result classification block (lines ~503–528) and confirm current FAIL conditions
- [ ] Add WARN branch: all four sections present in `final_answer_text` but out of order → `[WARN]`, result_status="WARN", do NOT set `verify_fail=1`
- [ ] Add WARN to the exit summary block (line ~690) so "X WARN(s)" is reported at the end
- [ ] Confirm that a genuine no-answer case (e.g. empty `final_answer_text`) still produces FAIL
- [ ] Commit: `feat: add WARN level for sections-out-of-order dynamic check results`

### Task 3: Add FAIL/WARN investigation procedure to README

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

### Task 4: Diff check and confirmation

**What**: Verify the full diff contains only the three intended changes and nothing extraneous.

**Steps**:
- [ ] Run `git diff main...HEAD -- tools/tests/test-setup.sh README.md` and review
- [ ] Confirm: only `_has_sections` regex, WARN branch, and README subsection changed
- [ ] Save diff check result to `.work/00358/diff-check.md`
- [ ] Commit diff-check.md: `docs: add diff check result for #358`
- [ ] Report to user for confirmation before creating PR

## Done

