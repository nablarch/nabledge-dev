# Tasks: fix: broken link in v6 docs README for Nablarch 6u2 release note

**PR**: #331
**Issue**: #326
**Updated**: 2026-05-08

## In Progress

### 再現検証: docs.py変更がv1.x差分の原因か確認

**目的**: origin/main の状態で create/verify して差分ゼロを確認 → ブランチの修正を入れて create/verify → 想定外差分が出れば修正影響確定

**Steps:**
- [x] PRを origin/main と差分ゼロの状態にした（7ファイルをリバート、PR本文もクリア）
- [ ] origin/main 状態で create + verify 全5バージョン (6, 5, 1.4, 1.3, 1.2) 実行
- [ ] `git diff origin/main --stat` で差分ゼロを確認
- [ ] ブランチの修正（README.md, docs.py, test_docs.py）を再適用
- [ ] create + verify 全5バージョン 再実行
- [ ] `git diff origin/main --stat` で差分確認 → 想定外差分があれば報告

## Done

(なし — 全変更をリバート済み。再検証から再スタート)
