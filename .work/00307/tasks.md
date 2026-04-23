# Tasks: Benchmark + streamlined search flow

**Issue**: #307
**Branch**: 307-benchmark-search-flow
**PR**: #310 (draft)
**Updated**: 2026-04-23 (phase split: search → answer)

## ゴール (この PR の本質)

ids flow の L1 以下を 0 にする。Nabledge 品質基準 (1% リスク排除 / 品質は二値) に沿う。

## アプローチ: 段階分離

検索 → 回答 → 判定 の連鎖問題を一気に追うと原因が混線する。Phase 1 で検索だけを完成させ、その後 Phase 2 で回答に進む。

### Phase 1: 検索 LLM (AI-1) の精度向上 ← 今ここ

**目的**: a_fact の根拠 section が必ず selections に入る状態にする。

**測定**: 検索 LLM のみ実行し `selections` と `term_queries` のマージ集合で coverage 判定する。回答 LLM / judge は呼ばない (1 件 10〜20 秒 / $0.05 程度)。

**指標**: "必要な section がすべて selections に含まれているか" の 0/1 / 30 件で 100% を目指す。

### Phase 2: 回答 LLM (AI-3) の改善 (Phase 1 完了後)

Phase 1 が 100% に届いたら着手。under-reach / over-reach の双方に対策を入れ、judge で level 測定を再開する。

## Phase 1 で Phase 1 を進めるステップ

### Step 1: 用語検索 (term_queries) 機構の追加

**背景**: 現行 search_ids.md は title 字面のみで選ばせる設計で、LLM が質問を狭く解釈すると肝心の section (MTH s5 の concurrentNumber 等) が落ちる。LLM に固有名 (API/プロパティ/アノテーション) を 1〜3 個返してもらい、スクリプト側で body substring grep して selections にマージする。

- [ ] search_ids.md に `term_queries` フィールド追加 (固有名のみ、最大 3 個、自然文禁止)
- [ ] search_ids.py: grep 実装 (全 knowledge JSON の body に substring match、term あたり section 上限 3)
- [ ] run.py: `SCHEMA_STAGE1_IDS` に `term_queries` 追加
- [ ] search.json 出力に `term_queries` / `term_hits` を記録
- [ ] PE レビュー (プロンプト変更)、実行ログ添付

### Step 2: 検索専用の coverage 測定ツール

- [ ] `tools/benchmark/search_only.py` (または `run.py --search-only`) を作る: 全 scenario の search_ids のみ実行
- [ ] `expected_sections` と selections+term_hits を比較し coverage を計算
- [ ] 30 件で実測、L1 原因だった 9 件の漏れ section が救われたか確認

### Step 3: 検索 100% まで回す

- [ ] Step 2 の結果から未解決を特定
- [ ] 原因別 (LLM 解釈狭い / term で救えない / expected_sections 側の問題) に対策
- [ ] 100% 到達でフェーズ完了

## Phase 2 (先送り)

- [ ] AI-3 answer.md 改訂 (over-reach / under-reach 両面)
- [ ] PE レビュー + 実行ログ添付
- [ ] 30 件 rerun で L1 件数を測定
- [ ] judge の非決定性対策 (実測揺れが多ければ)

## やらないこと (スコープ外)

- current variant の改善
- 他バージョン (v1.2/1.3/1.4/5) 適用
- knowledge file の hints 追加・title 書き換え (benchmark 失敗を受けた個別調整はいたちごっこ、禁止)

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

30 件全件での Phase 1 完了後の目標: coverage 100%。その上で Phase 2 を測定する。

## Done (直近)

- [x] search_ids.md を recall-first に書き直し (PE review 4/5 approve、M1/M2 反映)
- [x] a_facts 横並びチェック (30 件) → 8 件修正 (5 削除 / 4 追加)
- [x] 新 search + 新 a_facts で 30 件再計測 → mean=2.20, L3=18, L1=12
- [x] L1 12 件の検索 vs 回答 切り分け → 検索 OK 9 件 / 検索漏れ 3 件 (review-08 MTH s5 / impact-08 bean_validation s8 / req-05 libraries-code)
- [x] 検索漏れ 3 件の LLM 思考ログ確認 → 「質問を狭く解釈」が共通原因
- [x] term 検索シミュレーション → 固有名は ~1 ヒットで精度高い、概念語は誤爆

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
