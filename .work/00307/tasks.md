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

### Stage 1 Round 2（準備中）

**Status**: Round 1 完了（5件, recall mean 0.76 / precision 0.39, review-01 が 0.40 で外れ値）。Prompt Engineer Expert Review 完了（Rating 3/5）。ユーザーとの議論で **H-A（index.toon 語彙 anchor）** 採用方針が固まった。

**Round 1 → Round 2 の変更仮説（ユーザー合意待ち）**:
- **H-A（主仮説）**: `index.toon` の category+title を圧縮した context を prompt に同梱 → 抽出キーワードが Nablarch ドキュメント語彙に寄り recall up
- **H-C（従仮説）**: Expert Review H1 の guidance block（機能カテゴリ/実行形態/具象クラス/対概念 の4軸）は H-A 適用後も必要かは見てから判断（Round 3 以降で）
- **Judging**: Expert Review H2.1（`expected_keywords` を NFKC+lowercase 正規化）は独立した判定側改善。Round 2 と同時に入れる

**Steps:**
- [x] Round 1: 5件実行 → `.work/00307/rounds/stage1-round1.md`
- [x] Round 1: Prompt Engineer Expert Review → `.work/00307/review-by-prompt-engineer-stage1-round1.md`
- [x] Round 1: 改善提案をユーザーに提示、議論
- [ ] `index.toon` → `index-compact.md`（category + title 圧縮版）を生成する仕組み作成
- [ ] `prompts/stage1_extract.md` に index-compact を埋め込む prompt template に更新
- [ ] `expected_keywords` 正規化（NFKC + lowercase）を scenarios JSON または判定ロジックに適用
- [ ] Round 2 計測（5件）
- [ ] Round 2 結果を `.work/00307/rounds/stage1-round2.md` に記録
- [ ] Round 1 との比較表作成（recall/precision/cost/time の差分）
- [ ] Prompt Engineer Expert Review（prompt 変更が Round 1 expert 由来なら不要、H-A は新仮説なので必須）
- [ ] ユーザーに提示 → 合意なら次 Round or 次 Stage へ

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

### qa.md に「情報不足時の1回ヒアリング」追加（H-B, ユーザー指示スコープ内）

**仮説**: 漠然とした質問（「ざっくり推奨構成を知りたい」等）に対しては、キーワード抽出前に 1 回だけヒアリングして対象範囲を絞ると回答精度・満足度が上がる。頻繁なヒアリングはユーザー負担なので「情報不足と判断した時のみ」発動。

**Steps:**
- [ ] 「情報不足」判定基準を設計（例: 質問がトピック単独で具体文脈なし、対象（web/batch/REST）不明、など）
- [ ] `qa.md` に Step 0 として追加する案を設計 → Prompt Engineer レビュー
- [ ] 実装（全5バージョン: 1.2/1.3/1.4/5/6 — cross-version consistency rule）
- [ ] Stage 3 benchmark に hearing 挙動の計測シナリオを追加して比較

### tools/benchmark/README.md 作成

**目的**: 開発者＆AI が後から読めるよう、ベンチマークツールの目的・実行方法・運用規則を一箇所にまとめる。

**Steps:**
- [ ] README.md を作成、以下を含める:
  - 目的: なぜ作ったか、何を測るか
  - 3 Stage の定義（Stage 1 / 2 / 3 が何をするか）
  - 実行方法（`python3 run.py --stage N --scenarios-file ... --scenario ... --limit N`）
  - scenarios JSON スキーマ（expected_question / expected_keywords / expected_sections / etc.）
  - prompt ファイルと各 Stage の対応
  - `.results/` vs `baseline/` の運用（gitignore と commit 方針）
  - Round 制ワークフロー（計測 → expert review → 合意 → 修正 → 次 Round）の説明
  - 再現性の担保範囲（AI 非決定性のみブレる、他はすべて固定）
  - 改善記録ファイル（`.work/00307/rounds/stage{N}-round{M}.md`）の読み方

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
- [x] Stage 1 Round 1（5件）計測・記録・expert review 完了
- [x] `.claude/rules/development.md` に「プロンプト変更は expert-review 起点でない場合必ず Prompt Engineer レビュー」を追記
