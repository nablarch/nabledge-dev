# Tasks: fix docs MD page anchors — use heading text slug

**PR**: #TBD
**Issue**: #316
**Updated**: 2026-04-28

## Not Started

### Task 1: TDD — 見出しテキストベースのアンカーテスト追加 (RED)
`test_labels_doc_map.py` に、`_anchor_for_label` の代わりに見出しテキストから GitHub アンカーを生成することを検証するテストを追加する。
- 日本語見出し (`ユニバーサルDAO`) → `github_slug("ユニバーサルDAO")` = `"ユニバーサルdao"`
- 英語見出し (`Universal DAO`) → `github_slug("Universal DAO")` = `"universal-dao"`
- 既存 `TestSphinxAnchorParity` の期待値修正: ラベル名スラグ → 見出しテキストスラグ
- RED 確認後コミット

### Task 2: `labels.py` の `_anchor_for_label` を見出しテキストベースに修正 (GREEN)
- `_anchor_for_label(label)` を `_anchor_for_title(title)` に置き換える
- `build_label_map` / `build_label_doc_map` の呼び出し側で `title` を渡す
- 既存テスト (`test_labels_doc_map.py` の anchor 関連) が全て GREEN になることを確認
- コミット

### Task 3: 全バージョン verify (v6/v5/v1.4/v1.3/v1.2) — before/after FAIL差分確認
- 変更前後で `bash rbkc.sh create <v> && bash rbkc.sh verify <v>` を全5バージョン実行
- FAIL 差分を記録し、意図しない増加がないことを確認
- コミット (verify 結果を `.work/00316/notes.md` に記録)

## Done

- [x] ブランチ作成: `316-fix-docs-md-anchor-heading-slug`
- [x] tasks.md 作成・コミット
