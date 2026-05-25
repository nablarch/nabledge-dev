# Tasks: fix setup-ghc.sh .vscode/ mkdir missing

**PR**: #351
**Issue**: #350
**Updated**: 2026-05-25

## Not Started

### 全バージョン動作確認（answered チェック追加後）

answered チェック追加後、全バージョンで Exit 0 かつ全 [OK] であることを確認する。

**Steps:**
- [ ] `LOCAL_SETUP_CC=tools/setup/setup-cc.sh LOCAL_SETUP_GHC=tools/setup/setup-ghc.sh bash tools/tests/test-setup.sh v6` — Exit 0, 全 [OK]
- [ ] 同上 v5
- [ ] 同上 v1.4
- [ ] 同上 v1.3
- [ ] 同上 v1.2
- [ ] 同上 upgrade

## Done

- [x] 動的チェック: 回答完走確認を追加（合否判定に使用）— `30d622b74`
- [x] タイムアウトを 120s → 240s に変更 — `{TBD}`
- [x] 動的チェッククエリを処理方式・目的入り質問文に変更 — `7eae854b4`
- [x] Fix `add_skill_permissions` to create `.vscode/` before writing `settings.json` — `37bb0d509`
- [x] Add `LOCAL_SETUP_GHC`/`LOCAL_SETUP_CC` env var support to `test-setup.sh` for local fix testing — `37bb0d509`
- [x] v6 先行確認: Exit 0, static [OK], dynamic [OK]
- [x] 全バージョン確認 (v6/v5/v1.4/v1.3/v1.2/upgrade × CC+GHC): Exit 0, 全 [OK]
