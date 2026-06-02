# Tasks: Add Javadoc knowledge to nabledge skills

**PR**: #365
**Issue**: #363
**Updated**: 2026-06-02 (session 9)

## Rules（全タスク共通）

- 1コミット = 1タスク
- 推測せず事実ベースで作業・判断する（実物・全件を確認し、確認範囲を明示する）
- RBKC の create/verify を変更する場合は実装前に設計書を更新してユーザーに確認する
- 各タスクは TDD 順（RED → GREEN）。1タスク=1コミット
- 1タスク完了後に必ず `python -m pytest tests/ut/ -q`（`tools/rbkc/` で実行）を行い全 GREEN を確認してからコミットする
- 統合 verify を変化させるタスクは、完了時に検知ゲートで FAIL 集合の差分を確認する

## 検知設計

QL1（2-C）有効化後、パイプライン（2-E〜2-I）完成まで `rbkc.sh verify` は意図的に FAIL する。本物の FAIL を見落とさないため:
1. 2-C2 で extdoc FAIL を FQCN 全件 + 他カテゴリ0件で `.work/00363/verify-baseline.md` に固定
2. 2-J で FAIL 集合を取得し、照合A（ベースラインの extdoc 全件消滅）+ 照合B（ベースライン外0件）で判定

設計書: `tools/rbkc/docs/rbkc-converter-design.md` §5-1 / §5-2、`rbkc-verify-quality-design.md` §3-2-3 / §3-3

---

## In Progress

### Task 2-J-pre: verify QC1/QC2 対称化（_build_javadoc_map 共通ヘルパー + 経路配線）
- **背景**: create が javadoc_map を渡して extdoc を内部リンク展開するが、verify の QC1/QC2 は javadoc_map なしで normalise_rst を呼ぶため出力が非対称 → 39,587件の false-positive QC1/QC2 FAIL が発生（session 8 で確認）
- **方針**: verify 経路でも同じ javadoc_map を visitor に渡して create と対称化。_norm 後正規化禁止原則(§3-1)を維持したまま normalise_rst 経路に javadoc_map を通す
- **設計決定（session 8 ユーザー指示）**: `knowledge/javadoc/` 逐引きで javadoc_map を再構築。`_build_javadoc_map(knowledge_dir)` 共通ヘルパーを verify.py に切り出し、`check_source_links` と `verify_file` の両方から呼ぶ
- **完了条件**: (1) `create 6 && verify 6` で QC1/QC2 false-positive 0件 (2) 照合B（ベースライン外 FAIL 0件） (3) `_norm` 後正規化なし

**変更箇所（全 TDD）:**
1. `_build_javadoc_map(knowledge_dir)` ヘルパーを verify.py に追加（共通ロジック切り出し）
2. `check_source_links` 内のインライン javadoc_map 構築を `_build_javadoc_map` 呼び出しに置換
3. `_normalize_rst_source` / `normalise_rst` / `extract_document` に `javadoc_map=None` 追加
4. `verify_file` → `_check_rst_content_completeness` 経路で `javadoc_map` を通す
5. `verify_file` 内で `_build_javadoc_map(knowledge_dir)` を呼んで経路に注入

- [x] テスト追加（RED）: `_build_javadoc_map` の単体テスト + QC1/QC2 false-positive が解消されることのテスト
- [x] 実装（GREEN）→ `pytest tests/ut/ -q` 全 PASS (639 passed)
- [x] コミット: `fix: verify — symmetrise QC1/QC2 with javadoc_map via _build_javadoc_map helper (#363)` — `4ee4e4571`

### Task 2-J: 統合 verify 確認（ベースライン照合）
- **前提**: Task 2-J-pre 完了
- **完了条件**: v6 を create→verify し QC1/QC2 FAIL = 0、ベースライン外の新規 FAIL 0 件。他バージョンも FAIL 増加なし。生成知識をコミット
- **検知ゲート**: 照合A（QC1/QC2 FAIL = 0）+ 照合B（ベースライン外0件）。照合B で FAIL が出たら原因タスクを特定し 2-x に戻る
- **結果（session 9）**:
  - QC1/QC2 FAIL = 0 ✅（完了条件 (1) クリア）
  - 照合B: ベースライン外 FAIL = 0 ✅
  - QL1 extdoc 残存 FAIL = 254件（method-level FQCN、ベースライン内の既知 FAIL）
  - QO3: README.md カウント不一致 1件（既存の既知 FAIL）

- [x] `bash rbkc.sh create 6 && bash rbkc.sh verify 6` を実行し FAIL 集合を取得
- [x] 照合A: QC1/QC2 FAIL = 0 確認
- [x] 照合B: ベースライン外 FAIL 0 件を確認。差分を `.work/00363/verify-2j-diff.md` に記録
- [ ] v5 / v1.4 / v1.3 / v1.2 も `create && verify` し FAIL 増加なしを確認
- [ ] 生成知識を `.claude/skills/nabledge-6/` にコミット
- [ ] コミット: `feat: regenerate v6 knowledge with javadoc files (#363)`

---

## Not Started

### Task 3: 検索フロー検証・改善
- **前提**: Task 2-J 完了
- **完了条件**: Javadoc 参照質問で javadoc リンクが検索フローで使われることを確認。使われなければワークフローに手順追加
- [ ] 「UniversalDao#exists の使い方」等で Javadoc リンクが使われるか確認
- [ ] 使われない場合は qa.md / semantic-search.md に明示手順を追加

### Task 4: ベンチマークシナリオ追加
- **前提**: Task 2-J 完了
- **完了条件**: Javadoc 参照を要する新規シナリオ追加 + expectations 設定。既存シナリオが javadoc 非参照と確認済み
- [ ] 既存シナリオで Javadoc 知識ファイルが参照されないことを確認
- [ ] Javadoc 参照質問のシナリオを新規追加
- [ ] 期待値（expectations）を設定

### Task 5: v6 検証（新シナリオ1件 → 既存スコア確認）
- **前提**: Task 3 / 4 完了
- **完了条件**: 新シナリオ正答 + 既存スコア低下なし（逐次実行）
- [ ] 新シナリオ1件を v6 で実行し正答を確認
- [ ] v6 既存ベンチマークを実行しスコア低下なしを確認（逐次実行）
- [ ] 問題あれば Task 2 に戻って修正

### Task 6: 差分チェック + PR レビュー依頼
- **前提**: Task 5 完了
- **完了条件**: 全変更差分が想定どおりと記録、Expert review 通過、PR 更新
- [ ] `git diff main...HEAD --stat` で変更ファイルを全件確認
- [ ] 想定外変更がないかをチェックし `.work/00363/diff-check.md` に記録
- [ ] ユーザーに確認依頼
- [ ] Expert review（Software Engineer + QA Engineer）
- [ ] PR を更新

---

## Done

- [x] `.work/00363/tasks.md` と `notes.md` 作成 — `521ac200d`
- [x] PR #365 作成
- [x] jar ツール動作確認・設計方針合意
- [x] Task 1: 設計書更新 → ユーザー承認 — `12053d029` / `f771ecbfa` / `fb631766c`
- [x] 実装コミット（session 3-5）を revert — `f2dd8fc2a`
- [x] Task 2-A: emit_javadoc_link / JAVADOC_LINK_RE — `d019f2f4d`
- [x] Task 2-B: QO4 javadoc 除外 — `ae830a3b1`
- [x] Task 2-C: QL1 extdoc チェック — `c053dab00` / `6fe6646dc`
- [x] Task 2-C2: QL1 ベースライン記録 (813 FQCNs) — `5eeb73d89`
- [x] Task 2-D: jar 復元 — `c9d6a66a0`
- [x] Task 2-E: javadoc.py 実装 — `7f37cdb36`
- [x] Task 2-G: rst_ast_visitor extdoc 内部リンク化 — `426046d34`
- [x] Task 2-H: rst_ast_visitor javadoc_url 外部リンク化 — `da4ce9b21`
- [x] Task 2-F: run.py javadoc_generate 配線 — `0886687ba`
- [x] Task 2-I: docs.py + index.py javadoc/ 除外 — `5742f62e2`
