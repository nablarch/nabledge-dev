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

## 2026-04-07

### 根本原因（事実ベース）

テスト実行 20260331T171824 でエラーが発生: `libraries-04_Permission--s10`

**事実1: prior_round_findings は正しく渡されている**
- R2 Phase D プロンプトに Prior Round Findings セクション (Line 413-419) が存在
- BusinessDateProvider, Initializable のfindingsが含まれている

**事実2: プロンプト指示は明確**
- "Do NOT report new findings for locations that were not flagged before"
- "If a location was clean and content has not changed, do not report"

**事実3: 同じ findings が再報告されている（Prompt Compliance Failure）**
- R1 findings: hints_missing (BusinessDateProvider), hints_missing (Initializable)
- R2 findings: 全く同じfindings が再報告
- LLM が prior_round_findings 指示を無視している

**事実4: 知識ファイルは修正済み**
- R2 Phase E の出力JSON (line 25-26):
  - 'BusinessDateProvider' ✅ hints に含まれている
  - 'Initializable' ✅ hints に含まれている
- つまり R1 Phase E で修正が成功していた

**事実5: ソースファイル（RST）は変わっていない**
- source_evidence に記録されたテキスト内容は R1 → R2 で同じ
- ソース側での追加・削除・変更がない

### 発生メカニズム

```
R1 Phase D: findings を報告 (hints_missing 2件)
  ↓ (prior_round_findings に記録される)
R2 Phase D: 同じfindings を再報告 ← ❌ LLM が指示を無視
  ↓ (Phase E が「修正が必要」と判定)
R2 Phase E: hints を修正しようとするが、実際のキャッシュは既に修正済み
  ↓
diff guard が「変更がない」と検出 → ERROR: Diff guard: no changes in allowed sections
  ↓
キャッシュは修正済み状態で更新されない
R3 Phase D: 既に修正済みなので clean
```

### あるべき姿

R2 Phase D で：
1. prior_round_findings に (hints_missing, sections.s1/.../index[0].hints) が存在
2. 知識ファイル内容がR1から変わっていない
3. ソースファイル（RST）も変わっていない
4. → findings をスキップ（報告しない）
5. 結果: R2 Phase D findings = 空（clean）

### 対応案

content_check.md の prior_round_findings ロジックを強化：

1. **コンテンツ変更の定義を明確化**
   - 「ソース変更」= RST に行が追加・削除・変更されること
   - 「知識ファイル更新」≠ ソース変更（hints 追加等は修正によるもの）
   - ソースが変わらない → prior_round_findings は完全スキップ

2. **prior_round_findings チェックの明示化**
   - location + category で完全一致するfindings を明示的にリスト化
   - 一致したら必ずスキップ（条件なし）

3. **具体例を追加**
   - 「前回のR1: hints_missing で BusinessDateProvider を報告」
   - 「今回のR2: ソースRST を見直す → BusinessDateProvider 関連の行は変わっていない」
   - 「判断: 知識ファイルは修正済み、ソース変わらず → 報告しない」
