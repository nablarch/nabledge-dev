# Notes

## 2026-03-31

### Bugs fixed today

#### Bug 1: Round 3 (Final Verification) runs on all files instead of targets (`run.py`)

`_run_final_verification()` に `effective_target` が渡されていなかった。
Phase C/D ともに全ファイルを対象にしていた。
→ `target_ids` パラメータを追加し、Phase C/D 両方に渡すよう修正。コミット `2885a33f`。

#### Bug 2: diff guard が `index`-only な修正を誤って拒否する (`phase_e_fix.py`)

`hints_missing` findingの場合、Phase E は `index[sN].hints` を修正するが
`sections` は変わらない。diff guard の「変更なし」チェックが `sections` しか
見ていなかったため、正しい修正を拒否していた。
→ `index` エントリの変更も確認するよう修正。コミット `2885a33f`。

### 残課題: Phase D false positive による diff guard エラー

**症状**: `libraries-04_Permission--s10` が Round 2 で diff guard エラー

**再現の流れ**:
1. Round 1: Phase D が `hints_missing` (BusinessDateProvider, Initializable) を検出 → Phase E が修正 → `[FIXED]`
2. Round 2: Phase D が同じ hints_missing を**また報告**（すでに hints 配列に存在するのに）
3. Phase E: 修正不要と判断して何も変更しない → diff guard が「変更なし」として拒否

**確認済み**: Round 2 終了時点のキャッシュに `BusinessDateProvider`, `Initializable` は
すでに存在している。Phase D の誤検知（false positive）が根本原因。

**次のアクション**:
- Phase D が Round 1 で修正済みの hints を Round 2 で再検知する原因を調査
- Phase D の findingsロジック（content_check.md プロンプトまたは検証ロジック）を修正
- `libraries-07_TagReference--s1` も Round 3 で 2 findings 残存しており関連する可能性あり

## 2026-04-03

### Investigation Result: Phase D False Positive Root Cause (Confirmed)

**The issue is NOT a false positive — it's a prompt compliance failure.**

**R1 State**:
- Hints array (38 items): Contains `businessDateProvider` (lowercase) but NOT `BusinessDateProvider` (PascalCase)
- Phase D detection: Correctly identifies `BusinessDateProvider` as missing → findings reported

**R2 State**:
- Hints array (40 items): Now contains BOTH `businessDateProvider` AND `BusinessDateProvider` ✅
- Prior round findings: Passed to Phase D with R1 findings (BusinessDateProvider + Initializable missing)
- Phase D instruction in prompt: "If a location was clean in the previous round and the knowledge file content at that location has not changed, do not report a new finding for it now."
  
**Problem Identified**:
- Phase D prompt correctly receives prior_round_findings (JSON with BusinessDateProvider missing)
- BUT: Phase D ignores the guidance and re-reports the same finding in R2 findings
- Likely cause: LLM disregards the "do not report findings that were in prior_round_findings" instruction
  - The current phrasing uses negative framing ("do NOT report")
  - LLM may interpret this as "check if content changed" rather than "skip if already reported"

**Actual cache state**:
- R1 cache after fix: index[0].hints includes BusinessDateProvider, Initializable
- R2 cache read: Same hints array (no change to cache)
- R2 Phase D input: Receives the updated cache with BusinessDateProvider present
- R2 findings: Still reports BusinessDateProvider as missing (false positive)

**Why diff guard fails**:
1. R2 Phase D: "BusinessDateProvider is missing" (false)
2. R2 Phase E: Receives finding, has nothing to fix (already in index)
3. Phase E diff guard: "No changes in allowed sections" → rejects with error

### Root Cause Determination

**The root cause is: Phase D prompt fails to exclude findings that appear in prior_round_findings**

This is NOT a cache merge issue or a finding format issue — it's a **prompt compliance issue**.

The prompt says "do NOT report" but should explicitly say:
- "For each finding in prior_round_findings, skip re-reporting it unless the knowledge file content at that location has CHANGED"
- Need to identify locations from prior_round_findings and actively exclude them from new findings

### Remediation Tasks Required

1. **Explicit exclusion rule in Phase D prompt** (content_check.md)
   - Current phrasing: Negative ("do NOT")
   - Required phrasing: Positive list of locations to skip
   - Add: "Extract all (location, category) pairs from prior_round_findings. Skip any finding whose (location, category) matches a prior finding UNLESS the section content has demonstrably changed."

2. **Content change detection** (optional, but important)
   - Current check: "knowledge file content at that location has not changed"
   - Need to clarify: What counts as a change?
   - For hints_missing: The hints array changing should NOT count as "content change" if the original section text is unchanged
   - For section_count issues: Section structure changing = content changed

3. **Add test case to verify fix**
   - Scenario: hints_missing in R1 → fixed in cache → R2 should not re-report
   - Verify: phase_d_content_check.py correctly skips prior findings

### TODO

- [ ] Update content_check.md Phase D prompt with explicit prior_round_findings exclusion logic
- [ ] Add logic/documentation to clarify what "content change" means for each finding category
- [ ] Add test case in test_severity_flip.py for prior_round_findings handling
- [ ] Re-run v1.4 with fixed prompt to verify false positive is eliminated
- [ ] Update PR task list after fix is confirmed
