# Diff Check — PR #332 (Issue #327)

**Date**: 2026-05-08
**Branch**: `327-format-pcidss-table` vs `main`

## Changed Files (this PR)

| File | Change | Expected? |
|------|--------|-----------|
| `.claude/skills/nabledge-6/docs/check/security-check/security-check-3.PCIDSS対応表.md` | フラットテキスト → Markdownテーブル＋脚注スタイル | ✅ |
| `.claude/skills/nabledge-5/docs/check/security-check/security-check-3.PCIDSS対応表.md` | 同上（v5/v6 同一内容） | ✅ |
| `.work/00327/preview-security-check-3.md` | 新規作成（プレビュー用） | ✅ |
| `.work/00327/tasks.md` | 新規作成（タスク管理） | ✅ |

## Content Integrity Check

- 10要件（6.5.1〜6.5.10）全件保持: ✅
- 脚注※1〜※3 全件保持: ✅
- v5/v6 ファイル内容が同一: ✅（`git diff` でindex同一 `502915387 → ab9797ad5`）

## Unexpected Changes

なし。変更は上記4ファイルのみ。
