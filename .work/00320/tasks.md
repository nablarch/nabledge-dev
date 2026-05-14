# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-14 (rev41)

## In Progress

（なし）

## Not Started

（なし）

## Done

- [x] Issue #320 fetched and analyzed
- [x] Branch `320-verify-ql1-link-targets` created
- [x] PR #330 created
- [x] Tasks 1–14: 初回実装（verify QL1 チェック + RBKC heading 修正） — **リバート済み** `8673f77a5`
- [x] エキスパート（Software Engineer）相談 — Option C (common/labels.py) を推奨
- [x] Task 15: 設計完了・ユーザー承認済み
- [x] Task 16: verify check_source_links() cross-doc 実装 — SE: 1 Finding fixed, QA: 0 Findings
- [x] Task 17: `_scan_rst_labels` docutils AST 化 + subtitle sections[0] 修正 — 全5バージョン 0 FAIL
- [x] 設計書 P2-4 記述を復元 — `21fd36c59`
- [x] Task 18: 横並びチェック完了
- [x] 最終エキスパートレビュー完了 — SE: 0 Findings、QA: 0 Findings — `f9b694bf5`
- [x] Task 19: Bug 1 修正 — label_map lookup の case normalization — 全5バージョン 0 FAIL
- [x] Task 20: Bug 2 修正 — `_next_section_for_node` multi-level climb — 全5バージョン 0 FAIL
- [x] Task 21: Bug 3 修正 — anchor 検証実装 — 全5バージョン 0 FAIL — SE: 1 Finding fixed, QA: 2 Findings fixed
- [x] Task 22: 横並びチェック・再生成・差分確認・PR 更新 — 全5バージョン 0 FAIL
- [x] PR #330 レビューFB対応 — コメント4件処理済み `21e4b8fec`
  - #3217245104: `#特殊なリクエスト処理`（手動編集、後に Task 23 で RBKC 修正に置換）
- [x] Task 23: `21e4b8fec` を RBKC create 側修正に置換 — `8d7769977`
  - `_next_section_for_node` で `transition` ノードをスキップして次の section を探すよう修正
  - v1.2/v1.3/v1.4 の `RequestPathJavaPackageMapping` リンク先 → `#リクエストの識別と業務処理の実行`
  - 設計書 §3-2-2 にルール5として transition スキップルールを追記
  - 全5バージョン FAIL 0、532 tests passed
  - PR #330 コメント #3217245104 に返信済み
- [x] Task 24: QL1 アンカー → 非見出しノード調査完了 — 全5バージョン 1,126 非見出しアンカー特定、notes.md に記録
- [x] Task 26: `\X)` パターン paragraph anchor 対応 — `e95823f2d` / `9447309f6` / `359a1415e`
  - `_paragraph_anchor_title` に letter/digit+`)` パターン追加（設計書 §3-2-2 Rule 6）
  - v1.2/v1.3/v1.4 の 38 知識ファイル更新（v5/v6: 変更なし）
  - SE: 1 Finding 修正（docstring 更新）、QA: 0 Findings
  - 全5バージョン FAIL 0、548 tests passed
- [x] Task 27: entry-parent ラベルの paragraph anchor 解決 — `ecce586e1` / `910f2585d` / `dd3f0c8c4`
  - `_entry_parent_xparen_title()` 追加（設計書 §3-2-2 Rule 7）
  - `target + X) paragraph` ペアが前提条件（_walk_section の合成セクション生成条件と一致）
  - テスト 3 件追加（happy path + 2 fallback ケース、branch 8 カバレッジ含む）
  - v1.2/v1.3/v1.4 の 7 知識ファイル更新（v5/v6: 変更なし）
  - SE: 0 Findings、QA: 1 Finding 修正（branch 8 テスト追加）
  - 全5バージョン FAIL 0、548 tests passed
