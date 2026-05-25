# Tasks: fix setup-ghc.sh .vscode/ mkdir missing

**PR**: #351
**Issue**: #350
**Updated**: 2026-05-25


## Done

- [x] 動的チェック: 回答完走確認を追加（合否判定に使用）— `30d622b74`
- [x] タイムアウトを 120s → 240s に変更 — `{TBD}`
- [x] 動的チェッククエリを処理方式・目的入り質問文に変更 — `7eae854b4`
- [x] Fix `add_skill_permissions` to create `.vscode/` before writing `settings.json` — `37bb0d509`
- [x] Add `LOCAL_SETUP_GHC`/`LOCAL_SETUP_CC` env var support to `test-setup.sh` for local fix testing — `37bb0d509`
- [x] v6 先行確認: Exit 0, static [OK], dynamic [OK]
- [x] 全バージョン確認 (v6/v5/v1.4/v1.3/v1.2/upgrade × CC+GHC): Exit 0, 全 [OK]
