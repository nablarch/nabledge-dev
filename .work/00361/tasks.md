# Tasks: Add standard RAG metrics (DeepEval) to QA benchmark

**PR**: #362
**Issue**: #361
**Updated**: 2026-05-28 (T7完了)

## ルール

- 推測せず事実ベースで調査・作業・判断する。コードを読まずに影響範囲を推測しない。grepで確認してから書く。
- 1タスク = 1コミット（調査タスクはnotesへの記録で完結）
- 実装前にテストを書く（TDD: RED → GREEN）
- 各タスク完了後すぐにtasks.mdをコミット・プッシュする

---

## In Progress

(なし)

---

## Not Started

### T8: 動作確認（3件実行）

**目的**: 複数シナリオで安定動作することを確認する。

**作業**:
- `pre-01`, `pre-02`, `qa-01` の3件を実行
- 3件とも evaluation.json に DeepEval 3指標が含まれることを確認
- レポートのサマリーテーブルに3指標の集計が出ることを確認

**受入条件**: 3件全て正常完了、レポートに3指標集計あり

**コミット**: なし（動作確認タスク）

---

### T9: 全件実行 + 相関分析（SC1・SC2）

**目的**: 全30シナリオでDeepEval指標を取得し、既存LLMジャッジとの相関・不一致ケースを文書化する。

**注意**: 既存の `tools/benchmark/results/baseline-current/` には一切触れない。新規の run ディレクトリに結果を保存する。

**作業**:
- 全シナリオを `--with-deepeval` で実行し、`tools/benchmark/results/deepeval-validation/run-1/` に保存
- 相関分析: 各シナリオの `accuracy`（既存）と `answer_correctness`（DeepEval）、`hallucination`（既存）と `faithfulness`（DeepEval）の一致率を計算
- 不一致ケース（既存PASS→DeepEvalFAIL、またはその逆）を列挙して原因を分析
- 結果を `.work/00361/deepeval-validation.md` に記録

**受入条件**: 30シナリオ全て完了、不一致ケースが文書化される

**コミット**: `docs: add DeepEval validation results (SC2)`

---

### T10: HOW-TO-RUN.md 更新

**目的**: DeepEval追加後も手順書通りにベンチマークが実行できることを保証する。

**影響ファイル**:
- `tools/benchmark/HOW-TO-RUN.md`

**作業**:
- 前提セクションに `deepeval` のインストール確認手順を追加
- ステップ1〜2の実行コマンドに `--with-deepeval` フラグの説明を追加
- 出力ファイル早見表に DeepEval 3指標列の説明を追記
- T7/T8の動作確認手順通りに実際に実行して、手順書との齟齬がないことを確認

**受入条件**: HOW-TO-RUN.md の手順通りに実行して `--with-deepeval` フラグ付きで正常完了する

**コミット**: `docs: update HOW-TO-RUN.md for DeepEval integration`

---

### T11: 変更差分チェック

**目的**: PRレビュー依頼前に変更差分が想定した変更のみかを確認する。

**作業**:
- `git diff main...HEAD --stat` で変更ファイル一覧を確認
- 各変更ファイルについて「想定した変更か」を1行ずつ確認
- 意図しない変更（自動生成ファイル、無関係なファイル）がないかチェック
- 結果を `.work/00361/diff-check.md` に記録

**コミット**: `docs: add diff check results`

---

## Done

- [x] T1: 調査 — DeepEvalのジャッジLLM接続方式確認とLLMTestCase入力マッピング — notes.md に記録済み — `5530ab20`
- [x] T2: tools/benchmark/requirements.txt 新設 + setup.sh にインストールステップ追加 — `93669a7b`
- [x] T3: テスト追加（RED） — DeepEval 3指標計算のunit test — `1efc394e`
- [x] T4: evaluate.py 実装（GREEN） — DeepEval 3指標計算関数追加 — `1c7a6a0e`
- [x] T5: report.py — レポートにDeepEval指標列を追加 — `d87da7de`
- [x] T6: docs/benchmark-design.md — DeepEval指標設計追記 — `93101e85`
- [x] T7: 動作確認（1件実行） — pre-01でDeepEval 3指標出力確認、SSL修正 — `77a43974`

---

## SCとタスクの対応

| Success Criteria | 対応タスク |
|---|---|
| SC1: 3指標を各シナリオで計算しレポートに含める | T3, T4, T5 |
| SC2: 現行LLMジャッジとの相関・不一致ケース文書化 | T9 |
| SC3: レポートに標準指標スコアを表示 | T5 |
| SC4: 指標選定根拠とPASS/FAILしきい値をbenchmark-design.mdに記載 | T6 |
| SC5: 既存ベンチマークテストが全てPASS | T3, T4, T5（各タスクで既存テストのPASS確認） |
