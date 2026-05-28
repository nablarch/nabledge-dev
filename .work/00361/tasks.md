# Tasks: Replace LLM judge with DeepEval RAG metrics in QA benchmark

**PR**: #362
**Issue**: #361
**Updated**: 2026-05-28

## ルール

- 推測せず事実ベースで調査・作業・判断する。コードを読まずに影響範囲を推測しない。grepで確認してから書く。
- 1タスク = 1コミット（調査タスクはnotesへの記録で完結）
- 実装前にテストを書く（TDD: RED → GREEN）
- 各タスク完了後すぐにtasks.mdをコミット・プッシュする

---

## In Progress

### T12: 既存LLMジャッジ削除 + DeepEvalへの完全置き換え

**目的**: Issue #361の正しい方針「置き換え」を実装する。LLMジャッジを2系統並存させると評価コストが倍になるため、DeepEvalに一本化する。

**影響ファイル（要grep確認）**:
- `tools/benchmark/scripts/evaluate.py` — claim-judge / hallucination-judge 呼び出し削除、DeepEvalを常時計算に変更
- `tools/benchmark/scripts/report.py` — accuracy/hallucination 列削除、DeepEval列のみに変更
- `tools/benchmark/scripts/run_qa.py` — `--with-deepeval` フラグ削除（常時計算）
- `tools/benchmark/tests/test_evaluate.py` — 削除した関数のテスト削除、置き換えに伴うテスト更新
- `tools/benchmark/tests/test_report.py` — accuracy/hallucination 列テスト削除
- `docs/benchmark-design.md` — 旧LLMジャッジの記述を削除、DeepEval中心の設計に更新
- `tools/benchmark/HOW-TO-RUN.md` — `--with-deepeval` フラグの記述を削除

**作業ステップ**:
- [ ] 影響ファイルと削除対象をgrepで特定・リストアップ
- [ ] テストを先に更新（RED）: accuracy/hallucination 関連テストを削除、DeepEvalを常時計算前提のテストに更新
- [ ] evaluate.py から claim-judge / hallucination-judge を削除し、DeepEvalを常時計算に変更（GREEN）
- [ ] report.py から accuracy/hallucination 列を削除、DeepEval列のみ残す
- [ ] run_qa.py から `--with-deepeval` フラグを削除
- [ ] HOW-TO-RUN.md から `--with-deepeval` の記述を削除
- [ ] docs/benchmark-design.md を DeepEval 中心の設計に更新
- [ ] 全テスト PASS 確認
- [ ] コミット

**受入条件**:
- `evaluate_scenario` が LLM judge を呼ばず DeepEval 3指標のみ返す
- `--with-deepeval` フラグが存在しない
- 全テスト PASS

**コミット**: `feat: replace LLM judge with DeepEval metrics in benchmark pipeline (#361)`

---

## Not Started

### T13: 動作確認（1件実行）

**作業**:
- `python3 -m tools.benchmark.scripts.run_qa --scenarios ... --scenario-ids pre-01` を実行（フラグなし）
- `evaluation.json` に `answer_correctness`, `answer_relevancy`, `faithfulness` が出力されることを確認
- `report.md` に DeepEval 3指標が表示され accuracy/hallucination 列がないことを確認

**コミット**: なし（動作確認タスク）

---

### T14: 変更差分チェック

**作業**:
- `git diff main...HEAD --stat` で変更ファイル一覧確認
- 意図しない変更がないかチェック
- `.work/00361/diff-check.md` を更新

**コミット**: `docs: update diff check for LLM judge removal`

---

## Done

- [x] T1: 調査 — DeepEvalのジャッジLLM接続方式確認とLLMTestCase入力マッピング — notes.md に記録済み — `5530ab20`
- [x] T2: tools/benchmark/requirements.txt 新設 + setup.sh にインストールステップ追加 — `93669a7b`
- [x] T3: テスト追加（RED） — DeepEval 3指標計算のunit test — `1efc394e`
- [x] T4: evaluate.py 実装（GREEN） — DeepEval 3指標計算関数追加 — `1c7a6a0e`
- [x] T5: report.py — レポートにDeepEval指標列を追加 — `d87da7de`
- [x] T6: docs/benchmark-design.md — DeepEval指標設計追記 — `93101e85`
- [x] T7: 動作確認（1件実行） — pre-01でDeepEval 3指標出力確認、SSL修正 — `77a43974`
- [x] T8: 動作確認（3件実行） — pre-01/pre-02/qa-01全てDeepEval 3指標出力確認 — (実行のみ)
- [x] T9: 全件実行 + 相関分析（SC2） — 28/30シナリオ完了、deepeval-validation.md作成 — `bbcc37a50`
- [x] T10: HOW-TO-RUN.md更新（後でT12で修正予定） — `f6195085c`
- [x] T11: 変更差分チェック（後でT14で更新予定） — `7d1a0d52d`

---

## 方針変更メモ

T1〜T11は「DeepEvalを既存LLMジャッジに追加する」実装だったが、Issue #361の正しい方針は「置き換え」。T12〜で既存LLMジャッジを削除しDeepEvalに一本化する。
