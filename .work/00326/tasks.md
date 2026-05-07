# Tasks: fix: broken link in v6 docs README for Nablarch 6u2 release note

**PR**: #331
**Issue**: #326
**Updated**: 2026-05-07 (resumed)

## Not Started

### Investigate 917-file diff in v1.2/1.3/1.4/v5 after create

**Steps:**
- [ ] create全バージョン実行後のgit diffをサンプリングして変更内容を確認
- [ ] 確認結果次第で対応内容をこのタスクファイルに追加する

## Done

- [x] Fix broken link in `.claude/skills/nabledge-6/docs/README.md` line 371 — URL-encoded space as `%20` — committed `55bba1da2`
- [x] Fix `docs.py` to URL-encode spaces permanently (prevent create regression) — committed `7c9b1baf9`
- [x] Add expert reviews (Software Engineer + QA Engineer) — committed `a7ec6dd10`
- [x] Run create/verify for all 5 versions — all passed OK
- [x] Investigate 919 unstaged changes — root cause: quote() encoded Japanese chars; narrowed to .replace(" ", "%20") — committed `4e5643273`
