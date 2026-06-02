# Tasks: Add Javadoc knowledge to nabledge skills

**PR**: #365
**Issue**: #363
**Updated**: 2026-06-02 (session 14)

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

### Task 3-B: linkfmt.py を .json 出力に変更（GREEN）
- **前提**: Task 3-A 完了（RED） — `061507687`
- **完了条件**: Task 3-A テストが GREEN、全 pytest GREEN
- [x] `emit_crossdoc_link` の `.md` を `.json` に変更
- [x] `emit_javadoc_link` の `.md` を `.json` に変更
- [x] `CROSSDOC_LINK_RE` の `\.md` を `\.json` に変更
- [x] `JAVADOC_LINK_RE` の `\.md` を `\.json` に変更
- [ ] pytest GREEN 確認 → コミット

**Status**: linkfmt.py 変更済・未コミット。pytest 14件 FAIL（linkfmt `.md→.json` 変更の波及）。
波及修正が必要なテスト:
- test_labels_doc_map.py::TestMDRelativeLinkInsideNestedBlock::test_rewrite_inside_list_item
- test_rst_ast_visitor.py::TestVisitContainerToctree::test_toctree_resolved_entries_become_md_links
- test_rst_ast_visitor.py::TestExtdocRoleResolution::test_pass_nablarch_fqcn_in_map_emits_link
- test_rst_ast_visitor.py::TestExtdocRoleResolution::test_pass_method_suffix_resolved_via_class
- test_verify.py::TestCheckQL1LinkTargets (8件)
- test_verify.py::TestVerifyFile_ExtdocQC_Symmetrised (2件)
これらのテストが `.md` 期待値を持っているため更新が必要。

---

## Not Started

### Task 3: 検索フロー検証・改善（リンク拡張子規約是正が前提）
- **前提**: Task 2-J 完了 + リンク拡張子規約是正（設計書更新済 `77761ce5b`）が実装完了すること
- **完了条件**: Javadoc 参照質問で javadoc リンクが検索フローで使われることを確認。使われなければワークフローに手順追加
- [x] 「UniversalDao#exists の使い方」等で Javadoc リンクが使われるか確認 → **使われない**（設計上 index.md に Javadoc 未登録）
- [x] Session 12 調査・ユーザー指摘の設計問題を解決 → リンク拡張子規約是正（設計書改訂）が実施された（Session 13）
- [ ] リンク拡張子規約是正の実装（Task 3-A〜E）完了後、semantic-search に Step 3b を追加（Javadoc リンク検出 → .json 読み込み）

**Session 12-13 経緯**:
- リンクが `.md` を指しているのに `.json` を読むのは不整合 → 「JSON は .json リンク・docs MD は .md リンク」に規約変更
- 設計書改訂承認済（ユーザー確認 Session 13）、設計書更新コミット `77761ce5b`
- 規約是正の実装（Task 3-A〜E、下記）が完了してから semantic-search 改修を行う

### Task 3-A: test_linkfmt.py に .json 出力テスト追加（RED）
- **前提**: 設計書更新済 `77761ce5b`
- **完了条件**: テスト追加コミット済、pytest RED 確認
- [ ] `emit_crossdoc_link` / `emit_javadoc_link` の出力が `.json` であることを期待するテストを追加
- [ ] `CROSSDOC_LINK_RE` / `JAVADOC_LINK_RE` が `.json` パスにマッチすることのテストを追加
- [ ] pytest RED 確認（現行は `.md` 出力なのでテストが落ちること）

### Task 3-B: linkfmt.py を .json 出力に変更（GREEN）
- **前提**: Task 3-A 完了（RED）
- **完了条件**: Task 3-A テストが GREEN、全 pytest GREEN
- [ ] `emit_crossdoc_link` の `.md` を `.json` に変更
- [ ] `emit_javadoc_link` の `.md` を `.json` に変更
- [ ] `CROSSDOC_LINK_RE` の `\.md` を `\.json` に変更
- [ ] `JAVADOC_LINK_RE` の `\.md` を `\.json` に変更
- [ ] pytest GREEN 確認

### Task 3-C: test_docs.py に .json→.md 変換テスト追加（RED）
- **前提**: Task 3-B 完了
- **完了条件**: テスト追加コミット済、pytest RED 確認
- [ ] docs.py が内部相対リンク `.json` → `.md` に変換することのテストを追加
- [ ] `../`-prefix のリンクのみ変換し、`http(s)://` 外部 URL は変換しないテストを追加
- [ ] anchor (`#...`) が保持されることのテストを追加
- [ ] pytest RED 確認

### Task 3-D: docs.py に .json→.md 変換追加（GREEN）
- **前提**: Task 3-C 完了（RED）
- **完了条件**: Task 3-C テストが GREEN、全 pytest GREEN
- [ ] `_rewrite_internal_link_ext(text: str) -> str` 関数を追加（`CROSSDOC_LINK_RE` / `JAVADOC_LINK_RE` で `.json` → `.md` 変換、anchor 保持）
- [ ] `_render_full` の `_rewrite_asset_links` 呼び出し後に適用
- [ ] pytest GREEN 確認

### Task 3-E: verify.py の QO2・QL1 を .json/.md 基準に更新（TDD）
- **前提**: Task 3-D 完了
- **完了条件**: テスト RED → GREEN、全バージョン verify FAIL 差分が想定どおり（新規 FAIL 0）
- [ ] test_verify.py に QO2 リンク拡張子正規化テストを追加（RED）
- [ ] verify.py の QO2 比較に正規化を追加（GREEN）
- [ ] QL1 の内部リンク照合を `.json` 基準に更新
- [ ] 全バージョン knowledge 再生成（`bash rbkc.sh create v6` 等）
- [ ] 全バージョン verify 実行・新規 FAIL 0 確認

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
- [x] Task 2-J-pre: verify QC1/QC2 対称化（_build_javadoc_map） — `4ee4e4571`
- [x] Task 2-J: 統合 verify 確認（QC1/QC2=0、照合B OK） — `1eeb96e89` / `1fb952523` / `cb56a0602`
- [x] Task 2-J-follow: QL1 254件対処 — 設計書追記 `b0c4f3b11` / 共通モジュール実装 `d1fa3c75d` / v6 knowledge 再生成 `a9fd984bf`
- [x] リンク拡張子規約是正 設計書更新 — verify/converter 設計書改訂（承認済）`77761ce5b`
