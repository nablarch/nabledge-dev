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

(なし — 全タスク完了)

---

## Done

- [x] T1: 調査 — DeepEvalのジャッジLLM接続方式確認とLLMTestCase入力マッピング — notes.md に記録済み — `5530ab20`
- [x] T2: tools/benchmark/requirements.txt 新設 + setup.sh にインストールステップ追加 — `93669a7b`
- [x] T3: テスト追加（RED） — DeepEval 3指標計算のunit test — `1efc394e`
- [x] T4: evaluate.py 実装（GREEN） — DeepEval 3指標計算関数追加 — `1c7a6a0e`
- [x] T5: report.py — レポートにDeepEval指標列を追加 — `d87da7de`
- [x] T6: docs/benchmark-design.md — DeepEval指標設計追記 — `93101e85`
- [x] T7: 動作確認（1件実行） — pre-01でDeepEval 3指標出力確認、SSL修正 — `77a43974`
- [x] T8: 動作確認（3件実行） — pre-01/pre-02/qa-01全てDeepEval 3指標出力確認 — (実行のみ、コミットなし)
- [x] T9: 全件実行 + 相関分析（SC2） — 28/30シナリオ完了、deepeval-validation.md作成 — `bbcc37a50`
- [x] T10: HOW-TO-RUN.md更新 — --with-deepeval手順追加 — `f6195085c`
- [x] T11: 変更差分チェック — 意図しない変更なし確認 — `7d1a0d52d`

---

## SCとタスクの対応

| Success Criteria | 対応タスク |
|---|---|
| SC1: 3指標を各シナリオで計算しレポートに含める | T3, T4, T5 |
| SC2: 現行LLMジャッジとの相関・不一致ケース文書化 | T9 |
| SC3: レポートに標準指標スコアを表示 | T5 |
| SC4: 指標選定根拠とPASS/FAILしきい値をbenchmark-design.mdに記載 | T6 |
| SC5: 既存ベンチマークテストが全てPASS | T3, T4, T5（各タスクで既存テストのPASS確認） |
