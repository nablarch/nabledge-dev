# Prompt Engineer Design Review: Stage 1 Round 2

**Date**: 2026-04-22
**Reviewer**: AI Agent as Prompt Engineer
**Target**: Round 2 prompt design for H-A (index.toon 語彙 anchor)
**Verdict**: Design approved with specific choices below.

## Executive Recommendation

**H-A 採用 × 圧縮形式 (c) category + representative titles × H1 残すが短縮 × schema split は Round 3 に遅延**

review-01 の失敗は「AI に推論力がない」ではなく「ドキュメント語彙が見えない」こと。H1（抽象 axes）だけでは `ファイル入出力` という literal string は出ない。index がそれを見せる役目。

## Q1. Index 圧縮戦略

| 案 | tokens | recall | precision | 判定 |
|---|---|---|---|---|
| (a) 全295行 | ~9K | +高 | -中（parroting リスク） | ❌ cost |
| (b) カテゴリ＋件数のみ | ~100 | ~0 | ~0 | ❌ H1 と同等 |
| **(c) カテゴリ＋代表タイトル** | **~1.2-1.5K** | **+高** | **+中** | ✅ **採用** |
| (d) token抽出＋重複排除 | ~1K | +中 | -高（複合語破壊） | ❌ `ファイル入出力` が `ファイル`+`入出力` に分解されると BM25 失敗 |
| (e) embedding top-K | 変動 | +最高 | +高 | 後回し（infra 変更必要） |

**(c) の format 例**（`index_compact.md` として事前生成）:

```
# Nablarch Knowledge Index (295 files, 24 categories)
# Titles below are the actual headings used in the knowledge base.
# Prefer terms that appear here or their direct synonyms.

## nablarch-batch (11)
- アーキテクチャ
- 機能詳細 (都度起動バッチ / 常駐バッチ / ファイル入出力 / データバインド / データベースアクセス)
- 運用
...

## handlers (56) — showing 10
- トランザクション管理ハンドラ
- データベース接続管理ハンドラ
- 権限チェックハンドラ (Permission)
...
```

**キーテクニック**: generic タイトル（`機能詳細`, `アーキテクチャ`）のファイルには **section-level subterms** を括弧内に手動追記。`nablarch-batch-feature_details.json` のタイトルは `機能詳細` だが、そのセクション見出しに `都度起動バッチ`, `ファイル入出力`, `データバインド` がある。BM25 が実際に照合する語はこれらなので、ここで露出させる。一度だけ人手で作る静的アーティファクト。

**サイズ**: 24カテゴリ × (~50 tokens header + ~10 titles × ~15 tokens) ≈ 1.5K tokens。

## Q2. H-A と H1 の統合

**H-A は H1 を補完。H1 は短い前置きに降格、H-A がメイン。**

- H1 単独: 抽象 axes しか出せない → `データバインド` のような literal は出ない（review-01 の失敗再現）
- H-A 単独: index を menu として parroting → 質問特有の同義語を落とす
- 併用: H1 が「どの axis で出すか」、H-A が「どの語彙から選ぶか」を担う

## Q3. Round 2 プロンプト全文

```markdown
# Stage 1: Keyword Extraction

Extract 3–8 search keywords from the user's question. These keywords will feed
a BM25 full-text search over the Nablarch knowledge base, so they must be
terms that appear **verbatim** in Nablarch documentation.

## How to choose keywords

1. Read the question and identify which Nablarch axes it touches:
   - **機能カテゴリ** (what feature area — batch / web / validation / auth / etc.)
   - **実行形態** (execution form — 都度起動 / 常駐 / REST / messaging)
   - **対概念** (the contrast the question implies — 同期/非同期, 必須/任意, 認証/認可)
   - **実装手段** (concrete mechanism — ハンドラ / ライブラリ / アダプタ / アノテーション)

2. Consult the knowledge index below. Prefer titles and parenthesized
   subterms that appear in it — these are the exact strings BM25 will match.

3. Include the user's own Japanese wording only when it also appears in the
   index or is a well-known Nablarch term (e.g., `Permission`, `@UseToken`).

4. Do NOT pad to 10 keywords. Emit 3–8, ordered by specificity (most
   distinctive first). If the question is vague, emit fewer broad keywords
   rather than many speculative ones.

5. Keep Japanese compound nouns intact — do not split `ファイル入出力` into
   `ファイル` + `入出力`.

## Output

Output ONLY the JSON defined by the schema. No tool calls.

## Knowledge Index

{{index_compact}}

## Question

{{question}}
```

## Q4. Schema 変更

**Round 3 に延期**。理由：
- Round 1 の precision 低下は「10個に padding」が原因、構造不足ではない
- 新 prompt のルール4 (padding 禁止) + `maxItems: 8` で直接対処
- `synonyms` スロット追加は padding を裏口で再導入するリスク
- Round 2 で recall 改善しても precision が 0.6 未満なら、そのとき split する

**Round 2 の schema 変更（最小）**: `keywords` に `minItems: 3, maxItems: 8` を追加するだけ。

## Q5. コスト / レイテンシ見込み

| 項目 | Round 1 | Round 2 (予想) |
|------|---------|---------------|
| 追加 input | — | +1.65K tokens (index + 拡張指示) |
| cost/call | $0.10 | $0.11-0.13 (caching 有効なら +$0.003) |
| wall/call | 9.4s | 10.5-11.5s |

**前提**: prompt caching が index_compact 部分に効くこと。run.py の subprocess 呼び出しで effective か要確認。効かなくても +25% は許容範囲。

## Q6. 監視すべき pitfall

1. **Index parroting 率**: 抽出キーワードの何%が index_compact に verbatim 含まれるか測定。>95% なら anchor 過剰。目標 60-85%。
2. **Category bias**: handlers=56, libraries=46 が大きいのでその語彙に偏る可能性。`expected_sections` の category と突き合わせてログ。
3. **req-09 レート制限 の回帰**: 「Nablarch にこの機能なし」系は index に無い語なので、質問側から出さないといけない。Round 1 より recall 落ちたら anchor 過剰サイン → ルール3 強化。
4. **複合語分割**: BM25 の tokenizer が `ファイル入出力` をどう扱うかは Stage 2 で検証事項。rule 5 の正しさは Stage 2 で最終判定。
5. **Cache invalidation**: `index_compact.md` を run 途中で編集すると部分 cache hit でレイテンシが noisy に。benchmark run ごとに SHA 記録。
6. **抽象質問 over-constrain**: 「推奨構成は？」に verbatim 強制で `アーキテクチャ` が出なくなる懸念 → `アーキテクチャ` は index に複数ヒットするので実際は問題ないが、abstract-style シナリオ（review-02 等）で 1件は確認推奨。

## Deliverables

1. `tools/benchmark/build_index_compact.py` — `index.toon` → `index_compact.md` 生成スクリプト（category group / 10 titles cap / SHA ログ）
2. `tools/benchmark/prompts/index_compact.md` — 生成 + generic タイトルの subterms 手動追記版
3. `tools/benchmark/prompts/stage1_extract.md` — Q3 の新 prompt
4. `run.py` — index_compact.md を起動時に1回読み込み、`{{index_compact}}` 置換
5. Schema: `keywords` に `minItems: 3, maxItems: 8`
