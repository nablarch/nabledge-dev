# Tasks: Benchmark + streamlined search flow

**Issue**: #307
**Branch**: 307-benchmark-search-flow
**PR**: 未作成
**Updated**: 2026-04-22

## 計測設計（ユーザー合意済み）

3段階の粒度で計測し、各段階を**別コンテキスト**で独立判定する（バイアス排除）。

| 段階 | 実行 | 判定方法 | 判定コンテキスト |
|------|------|----------|----------------|
| ① キーワード抽出 | AIでキーワード抽出 | script: `expected_keywords` 一致率 | メインで完結 |
| ② 検索まで | ① + `keyword-search.sh` | LLM judge: 検索結果が適切か | 別sub-agent |
| ③ フル | n6 skill 丸ごと | LLM judge: 最終回答が適切か | 別sub-agent |

**効率化**:
- ②実行時に①の抽出キーワードも記録 → AIコール1回で①②両方の計測データ取得
- ①はscript判定のみなのでほぼノーコスト
- ②③はそれぞれ isolated sub-agent で flat に judge

**スケーリング**:
1. 3-5件（パターン網羅: QA/CA/benchmark）で ①②③ 動作確認・判定基準調整
2. 問題なければ 15件
3. 問題なければ 30件で確定ベースライン

## In Progress

### 計測ハーネス再設計（3段階対応）

**Status**: 現状の `tools/benchmark/run.py` は「フロー全体を1エージェントで動かす」前提の scaffolding のみ。3段階対応へ再設計が必要。

**Steps:**
- [ ] シナリオJSON拡張: 各シナリオに `expected_keywords`（①用）、`expected_answer` or 判定基準（②③用）を追加
- [ ] `run.py` を3段階対応に再設計:
  - Stage1: AI でキーワード抽出だけ実行 → script で expected_keywords と比較
  - Stage2: keyword-search.sh を Stage1 のキーワードで実行 → 検索結果を sub-agent で judge
  - Stage3: n6 skill フル実行 → 最終回答を sub-agent で judge
- [ ] judge prompt を作成（`prompts/judge_stage2.md` / `prompts/judge_stage3.md`）
- [ ] 3件（QA/CA/benchmarkから1本ずつ）で動作確認・判定基準調整
- [ ] time/cost/accuracy を `summary.json` に出力する構造を決定

**Context**:
- 前セッションで 1件を current flow で走らせたら 452秒 (7.5分) / $0.39 / 13 turns と異常に遅い → 段階分割で原因切り分け可能に
- ③ が一番コストかかるので、①②で問題なければ ③ に進む運用

### 計測速度の調査（必要なら）

**Status**: ③ フル実行が遅すぎる場合のみ調査。①②が速ければ後回し。

**Steps:**
- [ ] `claude -p --output-format stream-json --verbose` で turn 毎の内訳確認
- [ ] 初期 `cache_creation_input_tokens=32822` の正体を確認（system prompt か tool schema か）
- [ ] `--max-turns` チューニング

## Not Started

### パターン網羅3-5件で ①②③ 動作確認

**Steps:**
- [ ] QA/CA/benchmark から代表3件選定
- [ ] 3件で ①②③ 全段階実行、accuracy/time/cost を観察
- [ ] 判定基準の妥当性を検証、必要なら evaluator prompt 調整

### 15件で中間確認

**Steps:**
- [ ] ①②③ 全段階実行
- [ ] 異常値・分散を確認

### 30件ベースライン測定

**Steps:**
- [ ] ①②③ 全段階実行し `.results/{timestamp}/` に保存
- [ ] `summary.json` に段階別 accuracy/time(mean,median)/cost(mean,median) 出力
- [ ] 妥当な結果なら `tools/benchmark/baseline/{timestamp}/` にコピーして git コミット（A案、ユーザー確認済み）

### 検索フロー改修（全5バージョン: 1.2 / 1.3 / 1.4 / 5 / 6）

**設計（ユーザー承認済み）**:
- `_section-judgement.md` 削除
- `_knowledge-search.md` から route 2（`_file-search.md`/`_section-search.md`/`_index-based-search.md`/`_knowledge-search/_full-text-search.md` 薄ラッパー）削除
- 新フロー: `質問 → AIキーワード抽出 → keyword-search.sh（スコア順）→ 上位10件本文読み込み → AI回答生成`
- 全文検索ヒット0件 → 「情報なし」で終了（AIフォールバックなし）
- `scripts/get-hints.sh` 削除
- `full-text-search.sh` → `keyword-search.sh` にリネーム（新エントリーポイント公開）

**Steps:**
- [ ] nabledge-6 で改修（後述の各バージョンの雛形として）
- [ ] 1.2 / 1.3 / 1.4 / 5 に同じ変更を適用（cross-version consistency rule）
- [ ] 改修PR1本で全バージョン一括コミット（nabledge-skill rule）

### キーワード検索の公開（新エントリーポイント）

**Steps:**
- [ ] `plugin/GUIDE-CC.md` に「キーワード検索」の使い方を追記（全5バージョン）
- [ ] `plugin/GUIDE-GHC.md` に同じく追記（全5バージョン）
- [ ] 既存の「知識検索」「コード分析」の user-facing interface は不変なので記述の整合性チェックのみ

### 改修後 ①②③ 再測定 + ベースライン比較

**Steps:**
- [ ] 改修後の ①②③ で30件実行
- [ ] baseline と比較（accuracy 維持 + time/cost 削減か？）
- [ ] 改善/同等 → 採用
- [ ] 後退 → 原因分析してユーザーに改善案提示

### 仕上げ

**Steps:**
- [ ] `tools/benchmark/README.md` 作成（使い方、結果の読み方）
- [ ] `CHANGELOG.md` に新エントリーポイント「キーワード検索」追加（nabledge-6/nabledge-5 plugin）— developer docs は changelog 対象外なのでベンチマーク自体は含めない
- [ ] Expert review 実施（Software Engineer / Prompt Engineer / DevOps 想定）→ `.work/00307/review-by-*.md`
- [ ] `Skill(skill: "pr", args: "create")` でPR作成
- [ ] 未コミットの `tools/benchmark/` と `.work/00307/` を purpose 別に split commit（`.claude/rules/commit.md`）

## Done

- [x] 現状検索フロー把握（`qa.md` / `_knowledge-search.md` / `_section-judgement.md` / `code-analysis.md`）
- [x] シナリオJSONスキーマ確定（既存 `scenarios-all-30.json` をそのまま利用）
- [x] 30件シナリオを `.work/00307/scenarios-all-30.json` と `tools/benchmark/scenarios/qa-v6.json` に配置
- [x] `tools/benchmark/` scaffolding（`run.py` / `prompts/search_current.md` / `prompts/search_new.md` / `scenarios/qa-v6.json`）
- [x] 1件実行検証（`review-04` with current flow）— 動くが遅い（13 turns / $0.39 / 452秒）
- [x] 計測設計合意: 3段階（①抽出/②検索/③フル）× 別コンテキスト独立判定
