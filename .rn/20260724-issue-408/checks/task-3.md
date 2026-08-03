# task-3 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| `.work/00408/notes.md` にファイル比較結果が記録されており、リリース必須ファイルの漏れがない | OK | `notes.md` に "Verification against previous release PR" セクションを追記。PR #400 の release-essential ファイル12件と今回の12件が完全一致することを確認。 | OK | `gh pr diff 400 --name-only` と `git diff 658679e8..270f64f4 --name-only` で両リストを実測し12件完全一致を確認 |

## QA Expert Review

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Verification approach meaningful to the objective (checks the right thing, not just "passed") | OK | 既知の正解セット（前回PR）との差分比較という有意義な検証アプローチ |

## Expert Reviews (axes the task needs)

### Craft Expert (writing)

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Medium-specific best practice | N/A | 追記箇所は表と箇条書きのみ — task #1 で同じファイルのスタイルが PASS 済み |
| Consistency with existing style | N/A | 同上 |

### Verification Expert (fact-check)

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Artifact actually checked (claims verified against source) | OK | PR タイトル・PR #400 変更ファイル・現在の diff ファイル全てを実測で確認 |
| Coverage (all claims verified) | OK | 3つの主張（PR番号・前回ファイルリスト・今回ファイルリスト）を全て検証 |

## Overall Verdict

- Self-check: OK
- QA: OK
- Design expert: N/A
- Craft expert: N/A
- Verification expert: OK
- Ready to check off: Yes
