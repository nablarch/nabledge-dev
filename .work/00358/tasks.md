# Tasks: Fix dynamic check false positives in test-setup.sh

**PR**: #359
**Issue**: #358
**Updated**: 2026-05-27

## Ground Rules

- 推測で判断しない。変更前に対象コードを Read で確認し、事実として確認してから実装する
- 影響範囲は grep で実測する。「おそらく影響しない」は根拠にならない
- 各タスク完了後、テストで確認してから次に進む

## Done

- [x] Task 1: Introduce WARN level for "sections out of order" dynamic check results — committed `648b4ecfb`
- [x] Task 2: Add FAIL/WARN investigation procedure to README — committed `47599d200`
- [x] Task 3: Diff check and confirmation — committed `b12c73c38`
