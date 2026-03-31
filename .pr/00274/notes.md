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

### TODO

- [ ] Investigate and fix Phase D false positive: re-detecting already-fixed hints in subsequent rounds
