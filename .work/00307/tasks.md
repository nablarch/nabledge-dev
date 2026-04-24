# Tasks: Benchmark + streamlined search flow

**Issue**: #307
**Branch**: 307-benchmark-search-flow
**PR**: #310 (draft)
**Updated**: 2026-04-24 (Step 2/3 done)

## ゴール

ids flow の L1 以下を 0 にする (Nabledge 品質基準: 1% リスク排除 / 品質は二値)。

## アプローチ

検索 → 回答 の連鎖問題を一気に追うと原因が混線する。まず **検索** (Phase 1) を完成させ、次に **回答** (Phase 2) を改善する。**Phase 2 は必須**、検索だけでは L1=0 到達不可。

## 検索フロー (改善後)

```
1. スクリプトが質問から term_queries を機械抽出 (ASCII 4+ のみ)
2. AI-1 が index-llm.md を読む (各セクション行末に採用キーワードが付いている)
3. term_queries を本文 grep、AI-1 selections と merge → read-sections
4. AI-3 が回答生成
5. judge
```

## 進捗

### 完了 (Phase 1 準備)

- [x] **Step 0**: `docs/index-enrichment.md` 書き換え — `93af2c75d`
- [x] **Step 1**: stoplist 確定 (51 語) — `254816140` + `8959cb76d`
  - `section_df_ja.py` 新規 (TDD 18 テスト GREEN)
  - section_df ≥ 100 全員 stoplist / 50-99 で 19/31 / 30-49 で 18/43 / <30 全員残す
  - 判定過程: `stoplist-judgment.md`
- [x] **パラメータ凍結** — `ed115b132`
  - 採用語: tf≥2 で上位 5、候補 0 なら fallback tf=1 df≤20 で上位 3
  - 凍結根拠: `index-params-decision.md` (コーパス統計のみで決定、出来レース回避)
- [x] **10 件シミュレーション** — L1 検索漏れ 10 件で効果を LLM 視点で判定
  - 決定的 3 件 (impact-07, impact-03, req-05)
  - 確度上がる 5 件 (impact-01, req-04, review-08, impact-10, review-01)
  - 効果薄 2 件 (impact-08, req-10)

### Phase 1 残タスク

#### Step 2: classify_terms.py 書き直し (セクション単位 TF) ✅

- [x] 入力: knowledge JSON + stoplist
- [x] 各セクションで tokenize → TF 計算 → stoplist / ページ・セクションタイトル重複除外
  - 識別子パターンは日本語 tokenizer が 4+ 字 JP のみを拾うため明示除外不要
- [x] tf≥2 上位 5 語、候補 0 なら fallback tf=1 df≤20 で上位 3 語
- [x] 出力: `tools/benchmark/data/index-keywords-ja.json` — 生成済 (`c75a99c71`)
- [x] 既存 `classify_terms.py` のページ単位 TF-IDF ロジックを完全置き換え
- [x] TDD: `tests/test_classify_terms.py` 書き直し (22 tests GREEN)

#### Step 3: build_index.py 書き直し ✅

- [x] 入力: `--allowlist` → `--keywords`、`index-keywords-ja.json` を読む
- [x] 各セクション行末に ` — keyword / keyword / ...` 形式で付記
- [x] index-llm.md 生成 — 1411 sections / 3196 placements (`c75a99c71`)
- [x] TDD: `tests/test_build_index.py` 更新 (10 tests GREEN)

#### Step 4: 計測

- [ ] 10 件 search-only (失敗 9 + 成功 1)
- [ ] `search_coverage.py` で旧 vs 新 index 比較
- [ ] L1 件数の変化を記録 (現状 12 件)
- [ ] パラメータは動かさない (出来レース回避)

#### Step 5: 結論と Phase 2 移行

- [ ] 結果を文書化
- [ ] 検索改善が十分 or 不十分でも Phase 2 へ進む

### Phase 2 (必須): AI-3 回答プロンプト改善

L1=0 到達には検索改善だけでは不十分。`l1-root-cause-analysis.md` で既に特定済の AI-3 側の問題を解消する。

**既知の課題**:
- **over-reach**: 候補セクションから余計なトピックを拾う (C claim 過剰)
- **under-reach**: s1 overview に寄って本体セクションを引用しない
- **主役誤認**: 複数ハンドラ retrieved 時の主役取り違え (impact-10 など)

**タスク**:
- [ ] AI-3 `answer.md` 改訂
- [ ] PE レビュー + 実行ログ添付 (`.claude/rules/development.md`)
- [ ] 30 件 rerun で L1 件数測定
- [ ] judge 非決定性対策 (揺れが多ければ)

## 測定結果 (参考)

| 測定 | mean | L3 | L1 | 備考 |
|---|---|---|---|---|
| 旧 search + 旧 a_facts | 2.10 | 16 | 13+1 | 初回 30 件 |
| 旧 current | 2.17 | 18 | 11+1 | 比較用 |
| 新 search + 新 a_facts (30 件) | 2.20 | 18 | 12 | 前回 baseline |
| **新 index 10 件 search-only** | — | — | — | **Step 4 で測定** |

## スコープ外

- current variant の改善
- 他バージョン (v1.2/1.3/1.4/5) 適用
- knowledge file の hints 追加・title 書き換え (出来レース禁止)

## 方針確認済み

- 合格ライン = L2 以上
- 改善ターゲットは ids のみ
- AI-1 recall 優先、AI-3 precision 側で絞る
- hints 調整はしない (出来レース禁止)
- 変数を増やさない (計測中は AI-3 を変更しない、Phase 2 で独立改善)
