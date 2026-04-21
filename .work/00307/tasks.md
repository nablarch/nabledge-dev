# Tasks: Benchmark + streamlined search flow

**Issue**: #307
**Branch**: 307-benchmark-search-flow
**PR**: 未作成
**Updated**: 2026-04-22

## 計測設計（ユーザー合意済み）

### 3段階の粒度で別コンテキスト独立判定

| 段階 | 実行内容 | 判定方法 | 判定コンテキスト |
|------|---------|----------|----------------|
| Stage 1 | AIでキーワード抽出（ツール不使用） | script: `expected_keywords` との recall/precision | メイン内完結 |
| Stage 2 | Stage 1 + `keyword-search.sh` 実行 | LLM judge: 検索結果が質問に適切か | 別sub-agent |
| Stage 3 | n6 skill フル実行（回答生成まで） | LLM judge: 最終回答が質問に適切か | 別sub-agent |

### 反復ループ（Round制）

各Stageは **Round単位** で回す。1 Round = 計測 → レビュー → 改善提案 → ユーザー合意 → 修正 → 次Round。

```
Round N
  1. 計測実行（5件 × 対象Stage）
  2. プロンプト・実行方法・結果を記録: .work/00307/rounds/stage{N}-round{M}.md
  3. Prompt Engineer Expert レビュー (.claude/rules/expert-review.md 参照)
  4. 改善提案をユーザーに提示 → 合意
  5. 修正 → Round N+1 の計測へ
```

### パターン網羅サンプル 5件（ユーザー承認済み）

| id | カテゴリ | 狙い |
|----|---------|------|
| review-01 | review / アーキテクチャ | 失敗ケース再現性（前回 recall 40% 粒度ズレ） |
| review-04 | review / セキュリティ | 遅延主原因（前回 452秒） |
| impact-01 | impact / 影響分析 | 横断トピック（Tx/DB接続） |
| req-02 | req / 要件 | 単純な機能問い合わせ |
| req-09 | req | expected_sections 0件（「情報なし」挙動） |

### スケーリング段取り

1. **5件でパターン網羅** — Stage 1 → Stage 2 → Stage 3 各Roundを回し改善
2. **15件で中間確認** — 5件で確定したプロンプトで拡張
3. **30件ベースライン** — 最終計測

### 共通実行パラメータ

- Model: `sonnet`
- Output: `--output-format json`
- Schema: `--json-schema '{...}'`
- Permission: `--permission-mode bypassPermissions`
- Tool restriction: `--tools` で stage 別に制御
- Prompt 渡し: **stdin 経由**（`--tools` variadic が positional prompt を食う問題の回避）

### 改善記録ファイル

`.work/00307/rounds/stage{N}-round{M}.md` に Stage/Round ごとの記録を残す。構成：

1. 計測条件（date / sample / model / options / prompt ファイル）
2. 結果サマリ（accuracy / time / cost / 個別結果）
3. Expert Review（Prompt Engineer）
4. 改善提案と判断（Implement / Defer / Reject）
5. 次Roundへの変更

## In Progress

### Stage 1 Round 1 → 2

**Status**: Round 1 試行計測済み（3件, recall=80% mean, review-01 で 40%）。5件パターン網羅でやり直し、Prompt Engineer Expert Review して改善に入る。

**Steps:**
- [ ] 5件（review-01/review-04/impact-01/req-02/req-09）で Stage 1 を実行
- [ ] 結果を `.work/00307/rounds/stage1-round1.md` に記録（条件・プロンプト・結果）
- [ ] Prompt Engineer Expert Review を実施（`.work/00307/review-by-prompt-engineer-stage1-round1.md`）
- [ ] 改善提案をユーザーに提示、合意を取る
- [ ] 合意内容を `prompts/stage1_extract.md` / 判定ロジックに反映
- [ ] Round 2 計測 → 再レビュー → 収束するまで繰り返し

## Not Started

### Stage 2 Round制

**Steps:**
- [ ] Stage 2 実行スクリプト実装（Stage 1 キーワード → `keyword-search.sh` → 結果記録）
- [ ] `prompts/judge_stage2.md` 作成（別sub-agent LLM judge）
- [ ] 5件 Stage 2 Round 1 計測
- [ ] Prompt Engineer Expert Review → 改善 → 収束するまで繰り返し

### Stage 3 Round制

**Steps:**
- [ ] Stage 3 実行スクリプト実装（n6 skill フル呼び出し）
- [ ] `prompts/judge_stage3.md` 作成（別sub-agent LLM judge）
- [ ] 5件 Stage 3 Round 1 計測（current flow）
- [ ] Prompt Engineer Expert Review → 改善 → 収束するまで繰り返し
- [ ] 5件で current/new 両フロー比較

### 15件で中間確認

**Steps:**
- [ ] 5件で確定したプロンプト・パラメータで 15件実行（Stage 1/2/3）
- [ ] 分散・異常値チェック

### 30件ベースライン測定

**Steps:**
- [ ] 30件実行（Stage 1/2/3, current/new）
- [ ] `summary.json` に段階別 accuracy/time(mean,median)/cost(mean,median) 出力
- [ ] 妥当なら `tools/benchmark/baseline/{timestamp}/` にコピーして git commit

### 検索フロー改修（全5バージョン: 1.2 / 1.3 / 1.4 / 5 / 6）

**設計（ユーザー承認済み）**:
- `_section-judgement.md` 削除
- `_knowledge-search.md` から route 2（`_file-search.md`/`_section-search.md`/`_index-based-search.md`/`_knowledge-search/_full-text-search.md` 薄ラッパー）削除
- 新フロー: `質問 → AIキーワード抽出 → keyword-search.sh（スコア順）→ 上位10件本文読み込み → AI回答生成`
- 全文検索ヒット0件 → 「情報なし」で終了（AIフォールバックなし）
- `scripts/get-hints.sh` 削除
- `full-text-search.sh` → `keyword-search.sh` にリネーム（新エントリーポイント公開）

**Steps:**
- [ ] nabledge-6 で改修
- [ ] 1.2 / 1.3 / 1.4 / 5 に同じ変更を適用（cross-version consistency rule）
- [ ] 改修PR1本で全バージョン一括コミット（nabledge-skill rule）

### キーワード検索の公開（新エントリーポイント）

**Steps:**
- [ ] `plugin/GUIDE-CC.md` に「キーワード検索」追記（全5バージョン）
- [ ] `plugin/GUIDE-GHC.md` に同じく追記（全5バージョン）

### 改修後 Stage 1/2/3 再測定 + ベースライン比較

**Steps:**
- [ ] 30件で Stage 1/2/3 改修後計測
- [ ] baseline と比較
- [ ] 改善/同等 → 採用、後退 → 原因分析

### 仕上げ

**Steps:**
- [ ] `tools/benchmark/README.md` 作成
- [ ] `CHANGELOG.md` に新エントリーポイント「キーワード検索」追加
- [ ] Expert review 実施 → `.work/00307/review-by-*.md`
- [ ] `Skill(skill: "pr", args: "create")` でPR作成

## Done

- [x] 現状検索フロー把握
- [x] シナリオJSONスキーマ確定
- [x] 30件シナリオを `.work/00307/scenarios-all-30.json` と `tools/benchmark/scenarios/qa-v6.json` に配置
- [x] `tools/benchmark/` scaffolding
- [x] 1件実行検証（`review-04` with current flow）— 452秒問題確認
- [x] 計測設計合意: 3段階 × 別コンテキスト独立判定
- [x] Round制ワークフロー合意
- [x] 5件サンプル選定合意（review-01/review-04/impact-01/req-02/req-09）
- [x] Stage 1 `run.py` 実装（stdin prompt, recall/precision script判定）
- [x] Stage 1 試行計測（3件）— 動作確認OK
