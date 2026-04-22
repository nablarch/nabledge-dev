# Tasks: Benchmark + streamlined search flow

**Issue**: #307
**Branch**: 307-benchmark-search-flow
**PR**: #310 (draft)
**Updated**: 2026-04-22 (judge v2 実装完了、3件パイロット OK。30件再採点は ids 11/30・current 10/30 で中断、再開待ち)

## 現在地（一言）

**旧 judge が模範回答を見ずに採点していた重大欠陥を発見。v2 judge（模範回答＋参照本文ベース）を実装**。
3件パイロットは妥当な判定が出た。30件再採点を途中で中断（ids 11/30, current 10/30 完了）。
再採点完了後に真の比較結果が出る。旧比較 (ids 97% vs current 100%) は無効。

## 検索フローは 2 つだけ

| フロー | 内容 | 状態 |
|-------|------|------|
| **現行** (本番 skill) | AI キーワード抽出 → BM25 全文検索 → AI section 判定 | 本番稼働、30件ベースライン未計測 |
| **新** (ids) | AI-1 が LLM index 全文を読み `file_id\|sid` 直接返却 → read-sections → AI-3 → judge | 本PRで実装、Haiku 5件実測済み |

旧 facet 検索 (AI-1 type/category 抽出 + 機械 filter + AI-2 section 選択) は取り止め・削除対象。
コード残骸 (`stage1_facet.md` / `run_stage3` facet 版 / `facet_filter.py`) は採用判断後にまとめて削除。

## 測り方

- Stage 2 **スクリプト判定** — 模範回答の citation パスが filter 候補に含まれるか (`in`)
- Stage 3 **LLM judge** — 模範回答と生成回答を並べて 4段階判定 (別 sub-agent)
  - level 3: 完全に答えられる / 2: 主要部は答えられる / 1: 情報不足 / 0: 関連情報なし
- 合格基準なし。結果を見てユーザーと認識合わせ。

## 自律実行の流れ（ユーザー判断不要の範囲）

1. [x] Haiku 5件 (mean level 2.20)
2. [x] Sonnet 5件 (mean level 3.00)
3. [x] モデル固定 → Sonnet
4. [x] 新フロー (ids) 30件実測 (`20260422-185308-stage3-ids-sonnet`)
5. [x] 現行フロー 30件実測 (`20260422-185953-stage3-current-sonnet`)
6. [x] 旧 judge 設計欠陥を発見（模範回答未参照、自己推定採点）
7. [x] v2 judge 実装（模範回答＋参照本文ベース、OVER-REACH/HALLUCINATION検出、Prompt Engineer 提案をそのまま採用）
8. [x] 3件パイロット — req-09/impact-06/review-01 で妥当な判定確認
9. [ ] **30件再採点（残作業）**: ids 11/30, current 10/30 完了、残り 19-20件 × 2フロー
   - 再開コマンド:
     ```
     python3 tools/benchmark/run.py --judge-only \
       --results-dir tools/benchmark/.results/20260422-185308-stage3-ids-sonnet \
       --scenarios-file tools/benchmark/scenarios/qa-v6.json --model sonnet
     python3 tools/benchmark/run.py --judge-only \
       --results-dir tools/benchmark/.results/20260422-185953-stage3-current-sonnet \
       --scenarios-file tools/benchmark/scenarios/qa-v6.json --model sonnet
     ```
   - 既存 `judge_v2_result.json` は上書きされるが結果は同じなので実害なし
   - 将来改善: skip-existing モードを追加すれば純粋な resume 可能
- [ ] 30件再採点完了後、比較表を新規作成 → ユーザーに採用可否判断を仰ぐ

## 📢 ユーザー判断待ち（再採点後に再提示）

旧 judge の比較（ids 97% vs current 100%）は**無効**と判明。v2 judge 再採点完了後、
真の比較結果を出してから以下を改めて判断:
- 採用可否（ids / current）
- req-09 (out-of-scope) の扱い — v2 では ids=0 current=2 と差が出る想定
- 本番反映タイミング

## ユーザー判断が必要

- 30件実測後の **採用可否** (精度 + UX + 他バージョン適用タイミング)
- **模範回答の citation 粒度見直し** (期待セクションが狭すぎないか)
- **本番 skill への反映タイミング** (別 PR のロールベース KC 完了待ちとの調整)
- 他バージョン (v1.2/1.3/1.4/5) 適用は **別 PR ロールベース KC 側で実施** (本 PR は v6 のみ)

## In Progress

### 新フロー (ids) 性能検証

**Steps:**
- [x] `tools/benchmark/build_index.py` 作成、v6 で index-llm.md / index-script.json 生成
- [x] `stage1_ids.md` 作成、Prompt Engineer レビュー反映 (`review-by-prompt-engineer-stage1-ids.md`)
- [x] `run.py --variant ids` 実装 (AI-1 → script resolve → AI-3 → judge)
- [x] 全 40 tests GREEN
- [x] 脱落5件 Haiku 実測 (`20260422-183823-stage3-ids-haiku`) — mean level 2.20
- [x] 脱落5件 Sonnet 実測 (`20260422-184621-stage3-ids-sonnet`) — mean level **3.00** (全件 level=3)
- [x] Haiku vs Sonnet 比較 → **Sonnet 固定** (精度差 +0.80、コスト 2.2倍 $0.53/件、時間同等 68s/件)

### 新旧フロー比較ベンチマーク (30件)

**Steps:**
- [x] 新フロー (ids) 30件実測 (`20260422-185308-stage3-ids-sonnet`)
- [x] 現行フロー 30件実測 (`20260422-185953-stage3-current-sonnet`)
- [x] 旧 judge 比較 → **無効**（旧 judge は模範回答を見ていなかった）
- [ ] **v2 judge で 30件再採点（ids 11/30, current 10/30 完了、残り中断）**
- [ ] 再採点後、新比較表を作成
- [ ] ユーザーに採用可否判断を提示

### Stage 3 Judge v2 (fact-coverage grading)

**背景**: 旧 judge は {question, generated_answer, cited} のみで採点し、模範回答を参照しなかった。
結果として Sonnet の Nablarch 知識の曖昧な推定で「Expected core」を作り、自己採点していた。
これにより req-09 の current フロー回答が `ServiceAvailabilityCheckHandler` を誤って代替提示しても level=3 評価された。

**v2 設計** (Prompt Engineer 提案をそのまま採用):
- 入力: {question, reference_answer, reference_sources (模範回答 citation の本文), generated_answer, generated_cited}
- 4ステップ採点: required_facts 抽出 → COVERED/PARTIAL/MISSING/CONTRADICTED 判定 → OVER-REACH/HALLUCINATION 検出 → レベル決定
- CRITICAL RULE: 「ビルトインなし、最近傍は Y」の質問で Z を提示したら level≤1

**Steps:**
- [x] Prompt Engineer 相談 → Option B (全4入力を渡す) 採用
- [x] `prompts/judge_stage3_v2.md` 作成
- [x] `run.py` に `--judge-only` mode + `run_judge_v2_for_scenario` 追加（新 SCHEMA_JUDGE_STAGE3_V2）
- [x] 3件パイロット (req-09 / impact-06 / review-01, ids/current 両方)
  - req-09: ids=0 current=2 (OVER-REACH 検出)
  - impact-06: ids=3 current=2
  - review-01: ids=2 current=1
  - 旧 judge の level=3 量産と異なり、実態を反映
- [ ] 30件再採点（未完了、次セッションで再開）
- [ ] 採点結果から真の比較表作成

### 採用後の作業（ユーザー決定後）

**Steps:**
- [ ] 本番 skill `_knowledge-search.md` を ids フローに書き換え (v6)
- [ ] 旧 facet コード削除 (`stage1_facet.md` / `run_stage2` / `run_stage3` facet版 / `facet_filter.py` / `test_facet_filter.py`)
- [ ] 模範回答の citation 粒度再検討
- [ ] 他バージョン適用 — 別 PR ロールベース KC 側で実施 (本 PR では v6 のみ)
- [ ] `tools/benchmark/README.md` 作成
- [ ] CHANGELOG 更新
- [ ] PR 仕上げ (expert review + pr create)

## Done (this session)

- [x] Stage 2 スクリプト判定実装 (`grading/reference_answer.py` + `score_stage2.py`) — 15 tests GREEN
- [x] Stage 2 全 30件実行 (facet 版) → level=3 率 25/30、脱落5件特定
  - 結果: `tools/benchmark/.results/20260422-143411-stage3-sonnet/stage2_script.json`
- [x] 脱落5件分析 → AI-1 はカテゴリ名と1行説明しか見ていない情報設計欠陥を特定
- [x] LLM用index / スクリプト用index 分離方針決定 (ユーザー合意 2026-04-22)
- [x] ids フロー実装 (上記 In Progress の完了分参照)

## Done (previous sessions)

- [x] 計測設計: 3段階 × 別コンテキスト独立判定
- [x] Round 制ワークフロー合意
- [x] 30件シナリオ JSON 配置
- [x] `tools/benchmark/` scaffolding
- [x] Stage 1 facet 抽出 Round 1〜3 (facet フロー、後に取り止め)
- [x] Stage 2 機械 filter (facet_filter.py + Round 1) — 取り止め対象
- [x] Stage 3 section 選択 + 最終回答 + judge 実装
- [x] 模範回答 30件作成 (review-01..10 / impact-01..10 / req-01..10)
- [x] Prompt Engineer レビュー複数回
- [x] `.claude/rules/development.md` にプロンプト変更レビュールール追記
