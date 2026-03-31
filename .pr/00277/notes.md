# Notes

## 2026-03-31

### Root cause analysis: v1.2 vs v1.3 CA gap

v1.2 and v1.3 share identical `code-analysis.md` (path substitution only), yet v1.3 scores 34/36 on ca-001 vs v1.2's 28/36.
This confirms root cause is NOT purely prompt-side — input context differences also determine output.

15 miss items classified:
- Context-dependent (Overview): 5 items → defer investigation (v1.3 succeeds with same prompt, root cause unclear)
- Prompt-fixable (Processing Flow helper methods): ~2 items
- Skeleton format (Sequence diagram `POST RW` → `doRW`): 2 items
- Structural (template `.nabledge/` path): 2 items
- Other (call depth 2, parent class method, knowledge search miss): ~4 items (not all fixable)

### Decision: Defer Overview class list fix

v1.3 correctly includes MailRequester/MessageSender etc. with the same prompt.
The difference must be input context (source file content differences, knowledge search hits).
Fixing requires understanding what context v1.3 has that v1.2 doesn't — document here as investigation is done.

### Investigation: Overview class list gap (v1.2 vs v1.3)

**Symptom**: ca-001 Overview misses `MailRequester`, `MessageSender`, `ValidatableFileDataReader`, `BusinessDateUtil`, `UserInfoTempEntity` in v1.2, but v1.3 correctly includes some of them.

**Key findings**:
- v1.2 and v1.3 use identical `code-analysis.md` (only path substitution differs)
- v1.3 ca-001 scores 34/36 vs v1.2's 28/36 — both miss `checkLoginId` and some Sequence diagram items
- For Overview specifically: v1.3 includes MailRequester/MessageSender (the service classes) while v1.2 does not

**Hypothesis (unverified)**: Input context differs between versions:
1. Knowledge search hits differ — v1.3 knowledge files may reference MailRequester/MessageSender in a more prominent way, causing the agent to surface them in Overview
2. Source file content: v1.2 and v1.3 source files for W11AC02Action may differ in comments/structure, affecting LLM comprehension

**Why not fixed now**: Reproducing this deterministically requires:
- Running both v1.2 and v1.3 CA on same file with same seed
- Diffing knowledge search results for both runs
- Identifying which knowledge file causes the gap

This investigation is deferred to a follow-up issue. The current PR focuses on the structural/prompt-fixable issues (output_path, doRW format, helper methods).

---

## 2026-03-31（後半：ベースライン再取得・劣化評価）

### 全バージョン ベースライン再取得結果（commit 1efd23e8）

| Version | 前回 | 今回 | 判定 |
|---------|------|------|------|
| v6 (20260331-152005) | 96.6% | 97.3% | 改善 |
| v5 (20260331-154059) | 90.8% | 87.2% | 見かけ上低下（後述） |
| v1.4 (20260331-160735) | 85.6% | 80.4% | 見かけ上低下（後述） |
| v1.3 (20260331-162647) | 83.7% | 89.1% | 改善（ca-001: 30/36→35/36） |
| v1.2 (20260331-165313) | 83.7% | 78.3% | LLM分散（後述） |

### v5 QA 低下の原因

QA が 92.5% → 82.5% (-10pp) に見えるが、これは#242の expectations 修正がこのブランチ未マージのため。
現ブランチの期待値は旧仕様（`n:select`, `listName`, `withNoneOption` 含む）のまま。
#242マージ後に QA 90%+ に回復予定。スキルの実力低下ではない。

### v1.2 ca-001 の LLM 分散

前回中間ベースライン (20260331-144453) で 30/36 だったものが今回 26/36 に。
PR #277 の効果（checkLoginId, doRW11AC0204, .nabledge/ が新規検出）は確認済み。
MailRequester 関連の 7 項目が今回未検出になったのは、v1.2 知識ファイルが SyncMessage/MailRequester を
カバーしていないため検索結果に依存するから（LLM 分散）。PR #277 の変化起因ではない。

### v1.4 ca-002 の grading バグ発見（重要）

**表面**: 82.4% → 67.6% (-14.8pp、有意）

**比較レポートの診断（誤り）**: "file path 解決失敗"
→ シナリオの target_file は最初から tutorial パスを正しく指定している。ファイルパスは無関係。

**本当の原因**: CA エージェントが brief response を返した

- v1.4 ca-002 の response.md は 1,354 文字（`## Summary` のみ）
- v1.3 ca-002 の response.md は 13,869 文字（フル CA 出力を含む）
- nabledge-test のグレーディングは `response.md` を読んでセクション検出する
- response.md に `## Nablarch Framework Usage` がないため 5 項目すべて "Not found as heading"
- 一方、実際の出力ファイル `code-analysis-B11AC014Action.md` には `### FileBatchAction` 等が正しく存在

**証拠**: 全 3 試行が全く同一の 23/34（ランダムではなくシステマティックな grading 失敗）

**真の実力推定**: 約 27/34 (79%) — 前回 28/34 (82.4%) と誤差範囲内

**構造的課題**: nabledge-test grading が response.md のみ参照しており、
CA エージェントが外部ファイルに出力した場合に section-based grading が機能しない。

### 未着手の課題（次セッション向け）

1. **nabledge-test grading バグの修正**:
   `response.md` に加えて `code-analysis-*.md` 出力ファイルも grading 対象にする
   → v1.4 ca-002 の真のスコアが正確に計測できるようになる

2. **PR #277 のマージ判断**:
   PR #277 の変更起因の劣化はなし。v1.4 ca-002 の見かけ上の低下は grading バグによるもの。
   マージ可能な状態と判断されるが、grading バグを先に直すかどうかは議論余地あり。
