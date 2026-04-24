# Tasks: Benchmark + streamlined search flow

**Issue**: #307
**Branch**: 307-benchmark-search-flow
**PR**: #310 (draft)
**Updated**: 2026-04-24

## ゴール (この PR の本質)

ids flow の L1 以下を 0 にする。Nabledge 品質基準 (1% リスク排除 / 品質は二値) に沿う。

## アプローチ: 段階分離

検索 → 回答 → 判定 の連鎖問題を一気に追うと原因が混線する。Phase 1 で検索だけを完成させ、その後 Phase 2 で回答に進む。

### Phase 1: 検索 LLM (AI-1) の精度向上 ← 今ここ

**目的**: a_fact の根拠 section が必ず selections に入る状態にする。

**今セッションでの進化**: 失敗 5 件の真因は「ページ本文にユーザー質問語が存在しない / ページタイトルから質問語に気づけない」にあると判明。対策として **index-llm.md に TF-IDF 抽出キーワードを付記する Index Enrichment ワークフロー** を構築した。

### Phase 2: 回答 LLM (AI-3) の改善 (Phase 1 完了後)

Phase 1 が 100% に届いたら着手。

## Phase 1 Step 3 以降: Index Enrichment (今セッションの成果)

### 設計・方針確定 ✅

- [x] 検索フロー全体像を整理:
  - 経路1: index-llm.md 意味マッチ (AI-1 が `selections` 返す)
  - 経路2: term_queries 本文 grep (スクリプトが質問から機械抽出)
- [x] **index-llm.md には日本語・漢字 4 字以上の概念語のみ入れる**と決定
  (識別子 `@Annotation / CamelCase / camelCase` は term_queries が拾うので
  index に入れても重複のみ、index サイズを肥大化させる)
- [x] term_queries は **AI-1 生成をやめてスクリプト機械抽出** に統一
  (抽出ルールは TF-IDF 側と完全一致: カタカナ/漢字 4 字以上、CamelCase 2-hump、
  camelCase、@Annotation)
- [x] index 形式は Option B (PE 推奨): `keywords:` ラベル付き 2 行目
- [x] エキスパート相談 (SE / PE) 反映済み
- [x] ドキュメント化: `tools/benchmark/docs/index-enrichment.md`

### 手動/エージェント判定 ✅

スコア帯別に段階判定を実施。

- [x] classify_terms.py 実装 (TF-IDF + 自動分類)
- [x] JAVA_STOPLIST / stop_title_overlap 自動除外
- [x] 0.90+ (3語 → 1採用) 手動判定
- [x] 0.80-0.90 (15 → 10) 手動判定
- [x] 0.70-0.80 (13 → 10) 手動判定
- [x] 0.60-0.70 (23 → 20) 手動判定 (ユーザー修正: 上限設定/適宜カスタマイズ)
- [x] 0.50-0.60 (38 → 26) 手動判定
- [x] 0.40-0.50 (82 → 52) メインエージェント判定
- [x] 0.35-0.40 (71) **3 エージェント並列判定** → 3-0 ○ 36、title_overlap 除外後 25
- [x] 0.30-0.35 (76) 3 エージェント並列 → 3-0 ○ 35
- [x] 0.25-0.30 (115) 3 エージェント並列 → 3-0 ○ 35
- [x] 0.20-0.25 (174) 3 エージェント並列 → 3-0 ○ 81
- [x] 0.15-0.20 (304) 3 エージェント並列 → 3-0 ○ 160、メインエージェント刈り込みで 133
- [x] title_overlap 重複 58 語を除外
- [x] **最終採用: 361 語**

### 次ステップ: 実装と計測

- [ ] `MANUAL_ALLOWLIST_JA` (361 語) を classify_terms.py に定数埋め込み
  - 419 語採用のうち title_overlap 58 を除いた正味 361 語のみ
- [ ] `build_index.py` を Option B 形式に改修
  - `keywords:` 行を 2 行目に追加 (0 語のページは行を出さない)
  - ヘッダに 1 行説明追加 ("`keywords:` lines list additional terms...")
  - 並び順: 日本語語 TF-IDF 降順
- [ ] `search_ids.py` / `search_ids.md` 改修
  - AI-1 の term_queries 生成タスクを削除
  - スクリプトで質問文から 4 字以上 + 識別子を機械抽出
  - df_pct > 20% の語は grep 対象外
- [ ] 新 index-llm.md を生成してサイズと中身を目視確認
- [ ] 30 件 search-only で本計測 → ページ発見率と expected coverage 変化
- [ ] ベースラインと比較して効果確定

## 決定事項まとめ (今セッション)

- **機械抽出 term_queries と手動採用 index を分離**。識別子は term_queries、
  日本語概念語は index で拾う (役割分担)
- **抽出ルールは両経路で 4 字以上に統一** (カタカナ 3 字以下 / 漢字 3 字以下は
  一般語が多く複合語で代替可能)
- **ページタイトル/セクションタイトルと重複する語は除外** (`stop_title_overlap`)
- **ベンチマークシナリオに合わせた hints 追加は禁止** (出来レース防止)
- **ページ単位 TF-IDF を採用**。セクション単位は次 PR で段階導入検討

## Phase 2 (先送り)

- [ ] AI-3 answer.md 改訂 (over-reach / under-reach 両面)
- [ ] PE レビュー + 実行ログ添付
- [ ] 30 件 rerun で L1 件数を測定
- [ ] judge の非決定性対策 (実測揺れが多ければ)

## やらないこと (スコープ外)

- current variant の改善
- 他バージョン (v1.2/1.3/1.4/5) 適用
- knowledge file の hints 追加・title 書き換え (いたちごっこ、禁止)
- セクション単位 TF-IDF (次 PR で検討)

## 方針確認済み

- 合格ライン = L2 以上。L1 は Nabledge 品質基準で失格
- 改善ターゲットは ids のみ
- 設計意図: AI-1 は recall 優先、AI-3 は precision 側で絞る
- 検索精度を上げるのに hints 調整はしない (プロンプトと index 生成ロジックだけで戦う)

## 現在地の測定結果 (参考)

| 測定 | mean | L3 | L1 | 備考 |
|---|---|---|---|---|
| 旧 search + 旧 a_facts | 2.10 | 16 | 13+1 | 初回 30 件 |
| 旧 current | 2.17 | 18 | 11+1 | 比較用 |
| 新 search (recall-first) + 旧 a_facts | — | — | — | 6 件のみ測定、1 件 L3 改善 |
| 旧 search + 新 a_facts (rejudge) | — | — | — | 8 件対象、judge 非決定性で不安定 |
| 新 search + 新 a_facts (30 件) | 2.20 | 18 | 12 | 4 件劣化 (C over-reach 混入) |
| 新 index + 機械 term_queries (30 件) | — | — | — | 次セッションで測定 |

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
