# Tasks: fix: broken link in v6 docs README for Nablarch 6u2 release note

**PR**: #331
**Issue**: #326
**Updated**: 2026-05-07

## In Progress

### Investigate and commit create/verify results
**Steps:**
- [ ] Understand what docs.py change actually affects (which versions, which files)
- [ ] Confirm whether 919 unstaged file changes are expected or unexpected
- [ ] Investigate actual diff content to identify root cause
- [ ] Commit result or revert as appropriate

## Done

- [x] Fix broken link in `.claude/skills/nabledge-6/docs/README.md` line 371 — URL-encoded space as `%20` — committed `55bba1da2`
- [x] Fix `docs.py` to URL-encode spaces permanently (prevent create regression) — committed `7c9b1baf9`
- [x] Add expert reviews (Software Engineer + QA Engineer) — committed `a7ec6dd10`
- [x] Run create/verify for all 5 versions — all passed OK
