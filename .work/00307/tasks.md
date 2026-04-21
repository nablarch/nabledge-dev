# Tasks: Benchmark + streamlined search flow

**Issue**: #307
**Branch**: 307-benchmark-search-flow
**PR**: 未作成
**Updated**: 2026-04-22

**Note**: このセッションでは #307 本体の進捗はなく、PR #308（.pr/→.work/ rename含むルール整備）をmergeして本branchを `origin/main` にrebaseしただけ。

## In Progress

### ベンチマーク1件を1分以内で動かす

**Status**: `review-04` with current flow を試したら 13 turns / $0.39 / **452 秒 (7.5分)** で異常に遅い。1件を高速に動かす形を確立してから30件に進む方針。

**仮説（notes.md より）**:
1. セッション毎に system prompt + tool 定義を毎回 cache-create（hello world でも cache_creation=32822 tokens）
2. ツール実行が逐次でターン数が多い
3. Sonnet の thinking 時間
4. 1 turn あたり約35秒 = 通常 5-10秒より異常に遅い

**Steps:**
- [ ] `claude -p --output-format stream-json --verbose --max-turns 15 --allowedTools Bash --permission-mode bypassPermissions "簡単な検索クエリ"` を 60-90秒で kill して turn 毎の内訳を確認
- [ ] `--bare` オプションで CLAUDE.md / hooks / plugin sync / auto-memory を切って overhead が減るか試す
- [ ] 初期 `cache_creation_input_tokens=32822` の正体を確認（system prompt か tool schema か）
- [ ] `prompts/search_current.md` を圧縮して効果を見る
- [ ] `--max-turns` を 30→10 に減らして forced early termination の挙動を見る
- [ ] `run.py` / `prompts/` を調整し、`--flow current --scenario review-04` が1分以内で動くことを確認

**Context**:
- 現行 v6 検索フロー: Step 1 キーワード抽出(AI) → Step 2 全文検索(script) → Step 3 分岐判断(AI) → Step 4-5 ファイル/セクション選択(AI, route 2) → Step 6 セクション判定(AI) ← 削除対象 → Step 7 pointer JSON
- `claude -p --output-format json` で `duration_ms`/`num_turns`/`total_cost_usd`/`usage` 取得可
- `--json-schema` は最低 `--max-turns 2` 必要
- ベンチマークツール設計: nabledge-6 スキル経由ではなく `tools/benchmark/prompts/` 内に検索エージェントを定義して `claude -p` 起動（skill overhead 回避、新旧切り替え容易） — ただし「スキル自体を叩いた方が本物の計測」という反論もあり得る、ユーザーに要確認

## Not Started

### 30件ベースライン測定

**Steps:**
- [ ] `--flow current` で30件実行し `.results/{timestamp}/` に保存
- [ ] `summary.json` に accuracy/time(mean,median)/cost(mean,median) 出力
- [ ] 妥当な結果なら `tools/benchmark/baseline/{timestamp}/` にコピーして git コミット（A案、ユーザー確認済み）

### 検索フロー改修（全5バージョン: 1.2 / 1.3 / 1.4 / 5 / 6）

**設計（自分で決めた、ユーザーへの暗黙承認 — stop されていないが再確認推奨）**:
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

### 改修後30件再測定 + ベースライン比較

**Steps:**
- [ ] `--flow new` で30件実行
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

## ユーザーへの要確認ポイント

再開時に最初に擦り合わせるべき事項:

1. **ベンチマーク設計**: `claude -p` で独自検索エージェントを起動する方式で良いか？それとも nabledge-6 skill 自体を叩く方が「本物の計測」として妥当か？
2. **フロー簡素化方針**（暗黙承認中）:
   - `_section-judgement.md` / route 2 削除
   - `full-text-search.sh` → `keyword-search.sh` リネームで新エントリーポイント公開
   - ヒット0件はAIフォールバックなしで「情報なし」終了
