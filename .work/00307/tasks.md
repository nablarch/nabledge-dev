# Tasks: Benchmark + streamlined search flow

**Issue**: #307
**Branch**: 307-benchmark-search-flow
**PR**: #310 (draft)
**Updated**: 2026-04-24 (Step A 完了)

## ゴール (この PR の本質)

ids flow の L1 以下を 0 にする。Nabledge 品質基準 (1% リスク排除 / 品質は二値) に沿う。

## アプローチ: 段階分離

検索 → 回答 → 判定 の連鎖問題を一気に追うと原因が混線する。Phase 1 で検索だけを完成させ、その後 Phase 2 で回答に進む。

### Phase 1: 検索 LLM (AI-1) の精度向上 ← 今ここ

**目的**: a_fact の根拠 section が必ず selections に入る状態にする。

### Phase 2: 回答 LLM (AI-3) の改善 (Phase 1 完了後)

Phase 1 が 100% に届いたら着手。

## 検索フロー (今回の変更後の姿)

```
1. スクリプトが質問から term_queries を機械抽出
   - @Annotation, CamelCase, camelCase, カタカナ4+, 漢字4+
   - df_pct > 20% は grep 対象外

2. AI-1 が index-llm.md を読む
   - 各セクション行末に採用語が付いている
     例: `s3:制約 — スレッド / トランザクション管理`
   - AI-1 は selections のみ返す (term_queries 生成タスクは削除)

3. スクリプトが処理
   - term_queries を本文 grep
   - selections と grep ヒットを merge → read-sections

4. AI-3 が回答生成 (今回は変更しない)

5. judge (今回は走らせない、search-only モード)
```

## 今セッションの成果 (Phase 1 Step 3)

### 設計・ドキュメント ✅

- [x] 検索フロー 2 経路の役割分担を確定
  - index-llm.md 経路: 日本語概念語で意味マッチ
  - term_queries 経路: 識別子 + 4字以上語で本文 grep
- [x] `tools/benchmark/docs/index-enrichment.md` に全体フロー記録
- [x] `.claude/rules/benchmark.md` に「シミュレーションで手応え確認」追加
- [x] `setup.sh` に scikit-learn 追加

### classify_terms.py + 人間・エージェント判定 ✅

- [x] `classify_terms.py` 実装 (TF-IDF + 自動分類 + stop_title_overlap)
- [x] スコア帯別段階判定
  - 0.50+ (92語): 手動 → 67 採用
  - 0.40-0.50 (82語): メインエージェント → 52 採用
  - 0.35-0.40 (71語): 3 エージェント並列 → 25 採用 (title_overlap 除外後)
  - 0.30-0.35 (76語): 3 エージェント並列 → 35 採用
  - 0.25-0.30 (115語): 3 エージェント並列 → 35 採用
  - 0.20-0.25 (174語): 3 エージェント並列 → 81 採用
  - 0.15-0.20 (304語): 3 エージェント並列 → メインで刈り込み → 133 採用
- [x] title_overlap 重複 58 語を除外
- [x] **最終 MANUAL_ALLOWLIST_JA: 361 語**
  - `.work/00307/manual-allowlist-ja-361.json` に保存

### build_index.py 改修 ✅

- [x] セクション単位配置: 各採用語について本文にヒットする全セクション行末に付与
- [x] ヒットなしはエラー報告 (結果: 361 語すべて本文にヒット)
- [x] 新 index-llm.md 生成完了
  - サイズ: 148 KB (元 80 KB、+68 KB)
  - 配置数: 2,898 箇所 (1 語平均 8 セクション)
- [x] 失敗 9 件の target セクションに keyword が付いていることを目視確認
  - 効きそう: review-01, req-09, impact-02 (複数の関連語あり)
  - 弱い: review-10, impact-01 (該当本文に質問語が無いので TF-IDF では救えない)
  - 残りは term_queries 経路で補完する想定

## 次ステップ: term_queries 機械抽出 + 10 件 search-only 計測

### Step A: term_queries 機械抽出の実装 ✅

- [x] `tools/benchmark/bench/term_extract.py` を新設
  - `extract_terms(text)` が `@Annotation`, CamelCase, camelCase, カタカナ/漢字/混合 4+ を抽出
  - `filter_terms` で df_pct stopset 適用
  - パターンは `classify_terms.py` の `JAVA_STOPLIST` を共有
- [x] `tools/benchmark/build_term_stopset.py` を新設 → `data/term_stopset-v6.json` 生成 (16 語)
- [x] `search_ids.py` が質問から機械抽出して filter_terms 経由で grep 実行
  - AI-1 の `term_queries` は schema/prompt から完全削除
- [x] `prompts/search_ids.md` から term_queries 生成セクション削除
- [x] `tests/test_term_extract.py` 追加 (9 ケース GREEN)
- [x] 既存 test_build_index.py の pre-existing failure 6 件も修正 (allowlist 対応)
- [x] 全 34 テスト GREEN

### Step B: 10 件 search-only 計測

- [ ] 失敗 9 件 (review-01/10, impact-01/02/03/09, req-09/10, review-05) + 成功 1 件 の計 10 件
- [ ] `run.py --variant ids --search-only --limit 10` で実行
- [ ] `search_coverage.py` で coverage 算出
- [ ] 期待: 前回 30 件 (ref 70% / expected 77%) と比較して改善
- [ ] 10 件中での成功/失敗を詳細分析

### Step C: 結果次第で判断

- 効果あり → 30 件フル search-only → Phase 2 へ
- 効果なし → term_queries の追加改善 / index 配置ロジック見直し

## Phase 2 (先送り、判断材料)

今回は AI-3 は変更しない。既知の課題は記録しておく:

- **over-reach**: C claim が多い。候補セクションから余計なトピックを拾って回答に混ぜる
- **C-claim 過剰**: 質問されていない注意点を埋める
- **under-reach**: s1 overview に寄りがちで、本体セクションを引用しない

Phase 2 で着手予定:
- [ ] AI-3 answer.md 改訂 (over-reach / under-reach 両面)
- [ ] PE レビュー + 実行ログ添付
- [ ] 30 件 rerun で L1 件数を測定
- [ ] judge の非決定性対策 (実測揺れが多ければ)

## やらないこと (スコープ外)

- current variant の改善
- 他バージョン (v1.2/1.3/1.4/5) 適用
- knowledge file の hints 追加・title 書き換え (いたちごっこ、禁止)
- セクション単位 TF-IDF (今回はページ単位 TF-IDF + セクション配置)

## 方針確認済み

- 合格ライン = L2 以上。L1 は Nabledge 品質基準で失格
- 改善ターゲットは ids のみ
- 設計意図: AI-1 は recall 優先、AI-3 は precision 側で絞る
- 検索精度を上げるのに hints 調整はしない
- **変数を増やさない**: 今回の計測中は AI-3 は変更しない。原因切り分けのため

## 現在地の測定結果 (参考)

| 測定 | mean | L3 | L1 | 備考 |
|---|---|---|---|---|
| 旧 search + 旧 a_facts | 2.10 | 16 | 13+1 | 初回 30 件 |
| 旧 current | 2.17 | 18 | 11+1 | 比較用 |
| 旧 search + 新 a_facts (rejudge) | — | — | — | 8 件対象、judge 非決定性で不安定 |
| 新 search + 新 a_facts (30 件) | 2.20 | 18 | 12 | 4 件劣化 (C over-reach 混入) |
| 旧 index (既存) 30 件 search-only | — | — | — | ref 70% / expected 77% |
| **新 index 10 件 search-only** | — | — | — | **次セッションで測定** |

## Done (過去セッション)

- [x] search_ids.md を recall-first に書き直し (PE review 4/5 approve、M1/M2 反映)
- [x] a_facts 横並びチェック (30 件) → 8 件修正 (5 削除 / 4 追加)
- [x] 新 search + 新 a_facts で 30 件再計測 → mean=2.20, L3=18, L1=12
- [x] L1 12 件の検索 vs 回答 切り分け → 検索 OK 9 件 / 検索漏れ 3 件
- [x] 検索漏れ 3 件の LLM 思考ログ確認 → 「質問を狭く解釈」が共通原因
- [x] term 検索シミュレーション → 固有名は ~1 ヒットで精度高い、概念語は誤爆
- [x] term_queries 実装 + PE review (`960bfef3f`, `d4316f851`)
- [x] search-only mode + coverage 測定ツール (`9baf22051`)
- [x] 30 件 search-only 実測 (ref coverage 70%)
- [x] ファイル未選択 4 件のサブエージェント自由 grep 実験
- [x] a_fact 代替経路の直接 grep 確認 (3/4 件は模範回答 citation 唯一解ではない)

## 既知の bug / 対処済

- judge tool_use 壊れた input → `_is_well_formed_tool_input` フィルタで除外
- max_turns 2 で A 長いと切れる → 4 に引き上げ
- `list(string)` で char-list 化する事故 → `_facts()` type ガード

## 初期タスク群 (完了済)

- [x] 30 シナリオ + 模範回答 30件作成
- [x] 2-flow 比較基盤 (ids / current)
- [x] Haiku vs Sonnet 比較 → Sonnet 固定
- [x] 30件 × 2 flow 初回計測
- [x] AI-3 answer プロンプト改訂 (Use only what you need, PE レビュー反映済み)
- [x] `.claude/rules/benchmark.md` 新設 (並列実行禁止ルール)
- [x] 試行錯誤削除 / ベンチマークツール全面リファクタ (1572 → 1130行)
- [x] notes.md を設計判断のみに整理
- [x] baseline を新レイアウトに変換 / 全テスト 19件 GREEN
- [x] answer.md 改訂で ids 30件再計測
- [x] current variant は旧 baseline 流用と判断 (answer.md 非依存を確認)
- [x] `.claude/rules/development.md` 追記 (実出力目視・レビューに実行ログ添付)
- [x] judge 方式確定: A 事前準備 / B,C は KB (ref∪retrieved) 基準
- [x] scenarios JSON に `a_facts` フィールド追加、io/types/judge.py 改修
- [x] 30 scenario に A-fact を書いた (手書き 1 + Agent 草案 29 → 17件は私がレビュー修正)
