# Diff Check — Issue #335

## 変更ファイル（このissueの変更）

| File | 変更内容 |
|------|---------|
| `tools/rbkc/scripts/verify/verify.py` | `_MD_SYNTAX_RE` 削除 + P1限定コロン除外に置換 |
| `tools/rbkc/tests/ut/test_verify.py` | 2テスト追加（`|`, `---` FAIL検証）、捏造specテスト削除 |
| `tools/rbkc/docs/rbkc-verify-quality-design.md` | §3-1 P1コロン例外を明記 |
| `.work/00335/notes.md` | 調査結果記録 |
| `.work/00335/tasks.md` | タスクリスト |
| `.work/00335/rbkc-verify-diff.md` | verify実行結果記録 |

## 想定外の変更ファイル

- `.work/00320/tasks.md` — main からのリベース時に取り込んだ別issue (#320) のワークファイル。このissueの変更ではない。
- `.claude/skills/nabledge-*/` — main からのリベース時に取り込んだ PR #337 (v1.x knowledge refresh) の生成ファイル。このissueの変更ではない。

## 判定

想定外の変更は全て「リベース時に取り込んだ他PRの変更」であり、このissueで変更したファイルではない。**問題なし。**
