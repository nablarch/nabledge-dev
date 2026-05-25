# Tasks: fix setup-ghc.sh .vscode/ mkdir missing

**PR**: #TBD
**Issue**: #350
**Updated**: 2026-05-25

## Done

- [x] Fix `add_skill_permissions` to create `.vscode/` before writing `settings.json` — committed
- [x] Add `LOCAL_SETUP_GHC`/`LOCAL_SETUP_CC` env var support to `test-setup.sh` for local fix testing — committed
- [x] v6 先行確認: Exit 0, static [OK], dynamic [OK]
- [x] 全バージョン確認 (v6/v5/v1.4/v1.3/v1.2/upgrade × CC+GHC): Exit 0, 全 [OK]
