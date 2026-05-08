# Tasks: fix: broken link in v6 docs README for Nablarch 6u2 release note

**PR**: #331
**Issue**: #326
**Updated**: 2026-05-08

## In Progress

### PRレビュー依頼

**Steps:**
- [ ] PRレビュー依頼（expert review済み）

## Done

- [x] PRを origin/main と差分ゼロの状態にした（7ファイルをリバート）
- [x] .lw を最新化した
- [x] origin/main へのリベース完了（20コミット適用）
- [x] v1.x知識ファイル再生成を main 側で対応 (#337)、リベースで取り込み済み
- [x] ブランチの修正（README.md, docs.py, test_docs.py）を再適用 — committed `b3247a8`, `6d957fb`
- [x] create + verify 全5バージョン 再実行 — 全 OK
- [x] PRレビュー依頼前差分チェック — スコープ内4ファイルのみ（範囲外なし）
