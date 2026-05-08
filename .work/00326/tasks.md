# Tasks: fix: broken link in v6 docs README for Nablarch 6u2 release note

## Rules

- **推測しない**: 「〜のはず」「〜と思われる」で判断しない。必ず事実（コード・git diff・実行結果）を確認してから結論を出す

**PR**: #331
**Issue**: #326
**Updated**: 2026-05-08

## In Progress

### 再現検証: docs.py変更がv1.x差分の原因か確認

**Steps:**
- [ ] `git stash` でこのブランチの全変更を退避（docs.py、README.md、レビューファイル含む）
- [ ] create v1.2/1.3/1.4 実行して差分確認 → 差分ゼロなら報告して次へ
- [ ] docs.py変更のみ `git stash show -p | git apply` で適用（または手動復元）
- [ ] create v1.2/1.3/1.4 再実行して差分確認 → 差分あれば原因確定
- [ ] stash pop で全変更を戻す

## Done

- [x] Fix broken link in `.claude/skills/nabledge-6/docs/README.md` line 371 — URL-encoded space as `%20` — committed `55bba1da2`
- [x] Fix `docs.py` to URL-encode spaces permanently (prevent create regression) — committed `7c9b1baf9`
- [x] Add expert reviews (Software Engineer + QA Engineer) — committed `a7ec6dd10`
- [x] Run create/verify for all 5 versions — all passed OK
- [x] Investigate 919 unstaged changes — root cause: quote() encoded Japanese chars; narrowed to .replace(" ", "%20") — committed `4e5643273`
- [x] Investigate 917-file diff in v1.2/1.3/1.4 after create — root cause: pre-existing ID collision bug (not caused by this PR); out of scope for #326
