# Notes: Issue #307 - streamlined search flow + script-based benchmark

## 2026-04-21

### 決定事項（ユーザー確認済み）

- PR は 1 本で進める（ディレクトリ分離＋変更ファイル少で十分）
- ベースラインは **A案**: `tools/benchmark/baseline/{timestamp}/` に git コミット
- 質問側 UX 改善は **スコープ外**
- シナリオは**ベンチマークツール最適化**で設計（nabledge-test 互換性なし）
- シナリオ 30件は `.pr/00307/scenarios-all-30.json` に配置済み（`tools/benchmark/scenarios/qa-v6.json` にコピー済み）
- 検索フロー簡素化は**ユーザー判断に委ねず自分で設計**（指示待ちしすぎると怒られた）
- `full-text-search.sh` は **`keyword-search.sh` にリネーム**して新エントリーポイントとして公開
  - GUIDE でユーザーに「キーワード検索」としてスクリプトを教える形
- Judge は LLM (Haiku) のみ、決定論的突合せはしない
- ベンチマーク実装は **1件確実に動く形を先に確立してから複数件**

### 自分で決めた設計（ユーザーに要確認ポイント）

**フロー簡素化方針** — stop されていないので暗黙承認とみなしているが要再確認:
- `_section-judgement.md` 削除
- route 2（`_file-search.md` / `_section-search.md` / `_index-based-search.md` / `_knowledge-search/_full-text-search.md` 薄ラッパー）削除
- 新フロー: `質問 → AIキーワード抽出 → keyword-search.sh（スコア順）→ 上位10件本文読み込み → AI回答生成`
- 全文検索ヒット0件なら「情報なし」で終了（AIフォールバックなし）
- 削除されるスクリプト: `scripts/get-hints.sh`

**ベンチマークツール設計** — ユーザーに要確認:
- nabledge-6 スキル経由ではなく、ベンチマークツール内に prompt ファイルで「検索エージェント」を定義し、`claude -p` で起動
- 理由: skill 起動 overhead を避ける、新旧フロー切り替えが楽、並列化容易
- ただし「nabledge-6 スキル自体を叩いた方が本物の計測になる」という反論もあり得る

### 問題発生中: 検索時間が長すぎる

**現象**: `review-04` の現行フロー実行で 13 turns / $0.39 / **452 秒** (7.5 分)

**ユーザー指摘**: 「検索時間が長すぎます、何が起きてるんですかね？」

**仮説**:
1. セッション毎に system prompt + tool 定義を毎回 cache-create している（最初の hello world テストでも cache_creation_input_tokens=32822）
2. ツール実行が逐次でターン数が多い（キーワード抽出→全文検索→get-hints×N→read-sections→判定→回答）
3. Sonnet が thinking に時間をかけている
4. 1 turn あたり約 35 秒 = 異常に遅い（通常の Sonnet call は 5-10 秒）

**次セッションでの調査方針**:
- `--output-format stream-json --verbose` で turn 毎の内訳を取る（1 件を 90秒程度で kill して tail を見る）
- `--bare` で CLAUDE.md / hooks / plugin sync / auto-memory を切って overhead 削減できるか試す
- 初期 test_current の `cache_creation_input_tokens=32822` の正体を確認（大きな system prompt or tool schema）
- プロンプトを短くしてみる（`search_current.md` を圧縮）
- `--max-turns` を 30 → 10 に減らして forced early termination の挙動を見る

### 作業記録

**完了**:
- [x] 現状の検索フロー把握（`qa.md` / `_knowledge-search.md` / `_section-judgement.md` / `code-analysis.md`）
- [x] シナリオ JSON スキーマ確定（既存 scenarios-all-30.json をそのまま利用）
- [x] `tools/benchmark/` scaffolding 作成
  - `scenarios/qa-v6.json`
  - `prompts/search_current.md` / `prompts/search_new.md`
  - `run.py`（`claude -p --json-schema --output-format json` で実行、結果を `.results/{timestamp}/results.jsonl` に保存）
- [x] 1件実行検証（`review-04` with current flow）— 動くが遅い

**中断中のタスク**:
- [ ] 検索時間が遅い原因の特定 ← ここから再開
- [ ] 1 件を高速に動かす形の確定
- [ ] 30件ベースライン測定
- [ ] 検索フロー改修（全5バージョン: 1.2 / 1.3 / 1.4 / 5 / 6）
  - `_section-judgement.md` 削除
  - `_knowledge-search.md` から route 2 削除
  - `code-analysis.md` の Step 2 修正
  - `full-text-search.sh` → `keyword-search.sh` リネーム
  - `get-hints.sh` 削除
- [ ] キーワード検索公開（GUIDE-CC.md / GUIDE-GHC.md への追記、全バージョン）
- [ ] 改修後 30件再測定 + ベースラインと比較
- [ ] CHANGELOG.md 更新
- [ ] Expert review
- [ ] PR 作成

### 再開手順

1. まず `git status` で未コミット状態を確認
2. 検索時間調査: `claude -p --output-format stream-json --verbose --max-turns 15 --allowedTools Bash --permission-mode bypassPermissions "簡単な検索クエリ"` を 60-90秒で kill して内訳確認
3. 高速化方針を決めてから `run.py` / `prompts/` を調整
4. まず `--flow current --scenario review-04` で 1 分以内に動くか確認
5. 動いたら 30 件ベースライン測定

### 参考情報

**現行 nabledge-6 検索フロー** (`.claude/skills/nabledge-6/workflows/_knowledge-search.md`):
```
Step 1: Keyword extraction (AI)
Step 2: Full-text search (script: full-text-search.sh)
Step 3: Branch decision (AI)
Step 4-5: File selection + Section selection (route 2, AI)
Step 6: Section judgement (AI) ← 削除対象
Step 7: Return pointer JSON
```

**`claude -p` CLI 調査結果**:
- `--output-format json` で `duration_ms` / `num_turns` / `total_cost_usd` / `usage` / `modelUsage` 取得可
- `--json-schema` は最低 `max-turns 2` 必要（1 turn で tool_use 構造化出力、2 turn で finalize）
- `structured_output` フィールドに schema validated JSON が入る（`result` は空になる）
- hello world テストで 18.7秒（cache_creation_input_tokens=32822）

**ユーザーの働き方メモ**:
- 指示待ちすぎると怒られる（「何も考えてくれないの？」）
- 自分で設計判断して、必要なら確認だけ取る
- 会話は日本語
