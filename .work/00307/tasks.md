# Tasks: Benchmark + streamlined search flow

**Issue**: #307
**Branch**: 307-benchmark-search-flow
**PR**: #310 (draft)
**Updated**: 2026-04-24 (Step 4 partial, pivot to Read-based AI-1)

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

#### Step 4: 初回計測 (完了、悪化 3 件判明)

- [x] 10 件 search-only 実施 (`$4.10`, 4 分)
- [x] `search_coverage.py` で旧 vs 新 index 比較
- [x] 結果: expected_full 3/10 → 5/10、ref_full 2/10 → 4/10 (ネット改善)
- [x] ただし **悪化 3 件** 判明:
  - `req-05`: satisficing。`libraries-message` で満足し `libraries-code|s3` (タイトルに「多言語化」) を取らず
  - `review-01 s2`: タイトル「リクエストパス指定」だが本文は DataReader カタログ → title のみでは救えない
  - `review-08 s8`: タイトル「例外振る舞い」だが本文に DBCM ハンドラ/排他に直結 → title のみでは救えない
- [x] パラメータは動かさない (凍結維持、出来レース回避)
- [x] エキスパート再評価: 2/3 が Read 必須 → **4 ステップ Read 方式へ pivot**

#### Step 5: 4 ステップ Read-based AI-1 実装 (新規・最優先)

**設計合意 (`.work/00307/review-by-prompt-engineer-*` 系 PE 相談で確定)**:

- 4 ステップ手続き:
  1. intent 抽出 (質問から内容語と意図)
  2. index sweep → ファイル単位で候補列挙
  3. 各候補を Read → セクション本文で判断、evidence 引用
  4. 最終セクション選定 (10-15)
- `allowed_tools=["Read"]`、knowledge ディレクトリ限定
- `max_turns=8`
- schema は `intent` / `candidate_files` / `read_notes` / `selections` を全部返す
- evidence は **verbatim substring** (本文コピペ) 必須、事後に部分文字列一致検証
- `selections[].matched_on` enum (`title`/`keyword`/`body`) で分析用シグナル

**合格基準** (`review-by-prompt-engineer-*` 最新):
- 全体精度 ≥ baseline
- `review-01 s2` / `mth s8` 回復
- evidence 不一致率 ≤ 5%
- schema 検証失敗 ≤ 2%
- 中央値 wall time が 2 倍以内

**実装タスク**:
- [ ] `build_index.py`: index-llm.md のヘッダ行にファイルパスを埋め込む
- [ ] `search_ids.py`: `allowed_tools=["Read"]`、`max_turns=8`、evidence 事後検証
- [ ] `prompts/search_ids.md`: 4 ステップ手続き型に書き換え、verbatim 引用ルール追記
- [ ] schema 差し替え (intent/candidate_files/read_notes/selections)
- [ ] `search_coverage.py`: matched_on 集計 / evidence 不一致レポート
- [ ] **まず 1 件で試走** (低コストで挙動確認、悪化 3 件から 1 件選ぶ)
- [ ] 1 件で挙動が安定したら **3 件で試走** (悪化 3 件)
- [ ] 悪化 3 件が全て回復 + 安定 7 件が回帰しなければ 10 件、次に 30 件へ

**コスト予測**:
- 現状: $0.40/Q × 30 = $12/run
- Read 方式: $1.2-$2.0/Q × 30 = $36-$60/run (3-5 倍)

#### Step 6: 検索が安定したら回答統合の検討 (条件付き次期)

検索が安定して evidence も取れているなら、**本文は既に読んでいる**。
AI-3 を別呼び出しにせず、AI-1 に回答生成まで含める案を検討。

- [ ] 安定後、AI-1 プロンプトに回答生成ステップ追加を評価
- [ ] ファイル出力 (answer.md / search.json 等) は**呼び出し側のスクリプト**で実施 (AI-1 は JSON 返却のみ)
- [ ] 呼び出し側分離の意図: AI-1 の責務を「探す+答える」に閉じ、保存形式は外で決める

#### Step 7: 結論と Phase 2 移行

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
| 新 index 10 件 search-only | — | — | — | exp_full 3/10→5/10, ref_full 2/10→4/10、悪化 3 件 (req-05/review-01 s2/mth s8) |
| **4-step Read AI-1 1 件試走** | — | — | — | **Step 5 で測定予定** |

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
