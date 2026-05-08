# Tasks: fix: broken link in v6 docs README for Nablarch 6u2 release note

## Rules

- **推測しない**: 「〜のはず」「〜と思われる」で判断しない。必ず事実（コード・git diff・実行結果）を確認してから結論を出す

**PR**: #331
**Issue**: #326
**Updated**: 2026-05-08

## In Progress

### 再現検証: docs.py変更がv1.x差分の原因か確認

**目的**: origin/main ベースと このブランチ適用後で create/verify 全5バージョンを実行し、差分を比較する

**Steps:**
- [x] untracked files（1629件）を Python スクリプトで除去（git clean 相当）
- [ ] `git diff main..HEAD -- <3ファイル>` をパッチファイルに保存 → `git checkout main -- <3ファイル>` で main 状態に戻す
- [ ] create + verify 全5バージョン (6, 5, 1.4, 1.3, 1.2) 実行（main ベース）
- [ ] `git diff --stat` で差分を記録
- [ ] `git apply` でパッチを適用してブランチの変更を復元
- [ ] create + verify 全5バージョン 再実行（このブランチ適用後）
- [ ] `git diff --stat` で差分を記録 → 2回の結果を比較して原因を特定
- [ ] untracked files を除去して作業ツリーをクリーンに戻す

## Done

- [x] Fix broken link in `.claude/skills/nabledge-6/docs/README.md` line 371 — URL-encoded space as `%20` — committed `55bba1da2`
- [x] Fix `docs.py` to URL-encode spaces permanently (prevent create regression) — committed `7c9b1baf9`
- [x] Add expert reviews (Software Engineer + QA Engineer) — committed `a7ec6dd10`
- [x] Run create/verify for all 5 versions — all passed OK
- [x] Investigate 919 unstaged changes — root cause: quote() encoded Japanese chars; narrowed to .replace(" ", "%20") — committed `4e5643273`
