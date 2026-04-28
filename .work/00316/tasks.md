# Tasks: fix docs MD page anchors — use heading text slug

**PR**: #323
**Issue**: #316
**Updated**: 2026-04-28

## Not Started

### Task 0: サンプル変換 (1ページ) → ユーザー確認
実装着手前に1ページ分だけアンカーを見出しテキストベースで生成し、GitHub上でページ内遷移が正しく動作することをユーザーに確認してもらう。
- `labels.py` の `_anchor_for_label` を一時的に `github_slug(title)` に変更して1ページ生成
- 生成した docs MD を一時的にプッシュし、レビュアーにリンク確認を依頼
- 確認 OK → Task 1 へ進む

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

### Task 3: 設計書 (`rbkc-verify-quality-design.md`) 更新
本修正により §3-2-1 (Line 328) の anchor slug 規則が変わる。変更前後の影響を確認し設計書を更新する。
- 変更前: `github_slug(label_name)` (ラベル名ベース)
- 変更後: `github_slug(title)` (見出しテキストベース)
- `rbkc-verify-quality-design.md` §3-2-1 の該当記述を修正
- verify 設計 (QL1 anchor 一致検証、circular 回避) への影響を確認し、verify 側の変更が必要かを判定
- コミット

### Task 4: 全バージョン verify (v6/v5/v1.4/v1.3/v1.2) — before/after FAIL差分確認
- 変更前後で `bash rbkc.sh create <v> && bash rbkc.sh verify <v>` を全5バージョン実行
- FAIL 差分を記録し、意図しない増加がないことを確認
- コミット (verify 結果を `.work/00316/notes.md` に記録)

### Task 5: PR変更差分チェック
- `git diff main...HEAD` で想定した変更のみが含まれていることを確認
- 意図しないファイル変更が含まれていないことを検証
- 確認後 PR を作成

## Done

- [x] ブランチ作成: `316-fix-docs-md-anchor-heading-slug`
- [x] tasks.md 作成・コミット
