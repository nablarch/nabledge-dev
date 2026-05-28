# Tasks: Replace LLM judge with DeepEval RAG metrics in QA benchmark

**PR**: #362
**Issue**: #361
**Updated**: 2026-05-28

## ルール（今日の追加事項）
- `.claude/settings.json` に `DEEPEVAL_TELEMETRY_OPT_OUT=true` を追加済み（Apache 2.0ライセンス、オプトアウト許可）

## ルール

- 推測せず事実ベースで調査・作業・判断する。コードを読まずに影響範囲を推測しない。grepで確認してから書く。
- 1タスク = 1コミット（調査タスクはnotesへの記録で完結）
- 実装前にテストを書く（TDD: RED → GREEN）
- 各タスク完了後すぐにtasks.mdをコミット・プッシュする

---

## Not Started

### T19: QAベンチマーク全件実行・新ベースライン取得（3 run）

**目的**: 評価ロジックがDeepEvalに置き換わったため、旧ベースライン（accuracy/hallucination）は無効。新しいベースラインを取得する。

**注意**:
- キーワード検索ベンチマークはLLMジャッジ未使用のため取り直し不要
- 既存の `baseline-current/` は旧指標のものなので上書きしない。新ディレクトリに保存する

**作業**:
- [x] run-1完了: `tools/benchmark/results/baseline-deepeval/run-1/` (30件全成功、qa-09/qa-11bは再実行で回収)
- [ ] run-2実行: `python3 -m tools.benchmark.scripts.run_qa --scenarios tools/benchmark/scenarios/qa.json --skill-dir .claude/skills/nabledge-6` → `mv tools/benchmark/results/YYYYMMDD-HHMMSS tools/benchmark/results/baseline-deepeval/run-2`
- [ ] run-3実行: 同上 → `run-3`
- [ ] `report.py --compare` で3 run集計
- [ ] `baseline-current/` の代替として `baseline-deepeval/` を新ベースラインとして記録
- [ ] 結果を `.work/00361/notes.md` に追記

**受入条件**: 3 run全て正常完了、DeepEval3指標のレポートが出力される

**コミット**: `chore: save baseline-deepeval QA benchmark results (3 runs)`

---

### T20: 変更差分チェック + diff-check.md 更新

**コミット**: `docs: update diff check for LLM judge removal`

---

## Done

- [x] T1: 調査 — DeepEvalのジャッジLLM接続方式確認とLLMTestCase入力マッピング — `5530ab20`
- [x] T2: requirements.txt 新設 + setup.sh — `93669a7b`
- [x] T3: テスト追加（RED） — DeepEval 3指標計算のunit test — `1efc394e`
- [x] T4: evaluate.py 実装（GREEN） — DeepEval 3指標計算関数追加 — `1c7a6a0e`
- [x] T5: report.py — レポートにDeepEval指標列を追加 — `d87da7de`
- [x] T6: docs/benchmark-design.md — DeepEval指標設計追記 — `93101e85`
- [x] T7: 動作確認（1件実行）・SSL修正 — `77a43974`
- [x] T8: 動作確認（3件実行） — (実行のみ)
- [x] T9: 全件実行 + 相関分析（SC2） — `bbcc37a50`
- [x] T10: HOW-TO-RUN.md更新（T13で上書き予定） — `f6195085c`
- [x] T11: 変更差分チェック（T19で更新予定） — `7d1a0d52d`
- [x] T12: docs/benchmark-design.md 更新 — `4682e518`
- [x] T13: tools/benchmark/HOW-TO-RUN.md 更新 — `03206b0b`
- [x] T14: テスト更新（RED） — `e202bbb9`
- [x] T15: evaluate.py 実装変更（GREEN） — `00bcd0e1`
- [x] T16: report.py 実装変更 — `5513641a`
- [x] T17: run_qa.py から --with-deepeval フラグ削除 — `4d97f74d`
- [x] T18: 動作確認（1件実行）— 実行のみ、コミットなし
