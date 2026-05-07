# Tasks: fix docs MD page anchors — use heading text slug

**PR**: #323
**Issue**: #316
**Updated**: 2026-05-07 (session 2)

## In Progress

(なし — 全タスク完了)

## Done

- [x] ブランチ作成: `316-fix-docs-md-anchor-heading-slug`
- [x] tasks.md 作成・コミット
- [x] Task 0: サンプル変換 (1ページ) → 動作確認 — `labels.py` を変更して `libraries-universal-dao.md` 再生成、全67リンク (OK: 7 self + 60 cross, MISS: 0) 確認
- [x] Task 1: TDD RED — `TestHeadingTextAnchor` (5テスト) 追加、全5件 FAIL 確認 — committed `4c0aa40`
- [x] Task 2: GREEN — `_anchor_for_title(title)` 実装、432テスト全PASS — committed `a87e78b`
- [x] Task 3: 設計書更新 — §3-2-2 anchor slug 規則 + Sphinx 追従例外を追記 — committed `0571024`
- [x] Task 4: verify before/after — 全5バージョン FAIL 0→0 (差分なし) — notes.md に記録
- [x] Task 5: PR差分チェック — コードファイルは `labels.py` + `test_labels_doc_map.py` のみ確認、PR #323 body 更新完了
- [x] リベース — origin/main (5a34f258) にリベース、471ファイルのコンフリクト解消（自分のブランチ版を採用）、force-push済み
- [x] リベース後 create+verify — 全5バージョン FAIL 0 (変化なし) 確認
- [x] コンフリクト解消の正確性確認 — labels.py / test_labels_doc_map.py / rbkc-verify-quality-design.md の3ファイルはコンフリクトなしでリベース済み・内容正確であることをdiffで確認
