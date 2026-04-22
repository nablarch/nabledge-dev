# Stage 1 Round 1

**Date**: 2026-04-22
**Stage**: 1 (AI keyword extraction, tool-less)
**Scope**: 5 sample scenarios (pattern coverage)

## 計測条件

| 項目 | 値 |
|------|-----|
| scenarios file | `tools/benchmark/scenarios/qa-v6-sample5.json` |
| scenarios | review-01, review-04, impact-01, req-02, req-09 |
| prompt | `tools/benchmark/prompts/stage1_extract.md` |
| model | `sonnet` |
| output format | `json` |
| max-turns | 2 |
| tools | disabled (`--tools ""`) |
| permission-mode | `bypassPermissions` |
| prompt 渡し | stdin |
| results dir | `tools/benchmark/.results/20260422-083910-stage1-current/` |

### 使用プロンプト (`stage1_extract.md`)

```
# Stage 1: Keyword Extraction

Extract 3-10 search keywords (Japanese or English) from the user's question.

## Rules

- Output ONLY the structured JSON defined by the schema.
- No tool calls needed — this is a pure extraction task.
- Keywords should be concise terms (single words or short compounds) useful for full-text search against a knowledge base about the Nablarch framework.
- Include both Japanese terms the user wrote and any likely technical synonyms.

## Question

{{question}}
```

### JSON Schema

```json
{
  "type": "object",
  "properties": {
    "keywords": {"type": "array", "items": {"type": "string"}}
  },
  "required": ["keywords"]
}
```

### 判定方法（script）

`score_stage1()` in `run.py`:
- 小文字化したうえで `any(expected in extracted OR extracted in expected)` の **substring 双方向マッチ**
- recall = matched / expected, precision = matched / extracted

## 結果サマリ

| 指標 | mean | median | min | max |
|------|------|--------|-----|-----|
| wall_s | 9.4s | 8.9s | 7.7s | 12.8s |
| cost_usd | $0.104 | $0.096 | $0.094 | $0.140 |
| turns | 2 | 2 | 2 | 2 |
| **recall** | **0.76** | 0.80 | 0.40 | 1.00 |
| precision | 0.39 | 0.40 | 0.20 | 0.50 |

### 個別結果

| id | recall | missed | extracted |
|----|--------|--------|-----------|
| review-01 | 0.40 | ファイル入出力, データバインド, データベースアクセス | バッチ, ファイル読み込み, チャンク, DataReader, ItemWriter, フラットファイル, UniversalDao, ETL, 都度起動バッチ, 明細レコード |
| review-04 | 1.00 | — | バリデーション, 入力チェック, 必須, 桁数, 形式チェック, アノテーション, Bean Validation, ドメイン, Required, Length |
| impact-01 | 0.80 | ロールバック | トランザクション, コミット, トランザクション境界, バッチ, DB更新, CommitLogger, トランザクション制御, commit interval, フレームワーク制御, InputDataReader |
| req-02 | 0.80 | permission | 権限チェック, アクセス制限, 認可, 権限, ロール, 認証, セキュリティ, 画面制限, アクセス制御 |
| req-09 | 0.80 | restfulウェブサービス | レート制限, rate limit, スロットリング, throttling, REST API, リクエスト制限, アクセス制限, JAX-RS, 過負荷, 呼び出し回数 |

### 所見（計測実行者）

1. **review-01 の低 recall (0.40)** — 期待側は抽象語（「ファイル入出力」「データバインド」「データベースアクセス」）、抽出側は具象語（`DataReader`, `フラットファイル`, `UniversalDao`）。AI の抽出は悪くないが **期待値側の粒度**と噛み合っていない。
2. **req-02 の missed=`permission`** — 抽出側に `Permission` (大文字) がない。小文字化しても `permission` の substring が抽出側にない。実際には「認可」「権限」等で意味的にはカバー済み。判定の純粋な文字列照合が厳しすぎる。
3. **req-09 の missed=`restfulウェブサービス`** — 抽出側に `REST API` / `JAX-RS` はあるが、連結した複合語 `restfulウェブサービス` がない。これも semantic には一致、判定方法の限界。
4. **impact-01 の missed=`ロールバック`** — これは真の抜け。トランザクション制御の文脈で `ロールバック` は落としてはいけない。
5. **precision mean 0.39** — 10個抽出中 4個が期待キーワードと一致。precision が低いのは AI が多めに出しているため（害はないが search 側のノイズになる可能性）。

## Expert Review (Prompt Engineer)

詳細: [review-by-prompt-engineer-stage1-round1.md](../review-by-prompt-engineer-stage1-round1.md) — **Rating 3/5**

### 主な指摘

| # | 優先度 | 内容 |
|---|-------|------|
| H1 | High | Prompt にナレッジベース語彙への anchor なし → 粒度ズレ (review-01) |
| H2 | High | 判定ロジックが lexical-rigid すぎる (req-02 permission 擬陽性) |
| M1 | Medium | schema 無制限 → precision 低下 |
| M2 | Medium | 対概念の明示なし (impact-01 ロールバック miss) |
| L1 | Low | `--max-turns 2` は tool-less では過剰 |
| L2 | Low | 日本語＋英語の両方が必要な場面で任意表現 |
| L3 | Low | BM25 feed という downstream への明示なし |

### Round 2 変更候補（ユーザー承認待ち）

1. **Prompt**: H1 の guidance block 追加（4軸＋対概念）→ review-01/impact-01 対策
2. **Judging**: H2.1 適用 — `expected_keywords` を NFKC + lowercase 正規化して保存
3. **Options**: L1 — `--max-turns 1` に変更
4. **Schema**: M1 — `primary_keywords (max 5)` + `synonyms (max 5)` に分割
5. **Prompt追記**: L2/L3 — 日本語+英語両記載、BM25 明示

### 期待効果

- review-01 recall: 0.40 → ≥0.80
- req-02 recall: 0.80 → 1.00
- precision: 0.39 → primary_keywords ベースで 0.60+
- time/cost: 若干低下 (max-turns 削減)

