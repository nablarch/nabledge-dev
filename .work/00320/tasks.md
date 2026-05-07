# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-07

## In Progress

### Task 10: Issue #320 scope revision + reimplementation
Issue SCが不完全だった。現在の実装（anchor存在確認）では不十分で、
「RSTの`:ref:`が解決した先のsectionに、生成されたanchorが実際に到達できるか」
の検証が必要。

**Decision made this session**:
- 現在の実装「anchorが任意headingに存在するか」は弱すぎる
- 正しいチェック: `:ref:label` → `label_map` で解決した section title → `github_slug(section_title)` が JSON/docs MD のリンク anchor と一致するか
- これは `check_source_links()`（RST パースと label_map がある場所）で行うのが正しい設計
- Issue #320 の SC 自体を見直す必要がある

**Steps:**
- [DECISION: Issue #320のSCを見直してから実装方針を確定する] Issue SC改訂 + 実装設計
- [ ] Issue #320 のSCを更新（anchor存在確認 → 意図した場所への到達可能確認）
- [ ] 実装設計: `check_source_links()` 側での `:ref:` 解決先 anchor 照合設計
- [ ] TDD: 失敗テスト追加
- [ ] 実装
- [ ] 全5バージョン verify FAIL diff 記録
- [ ] 現在の「anchor存在確認」実装の扱いを決める（残す/削除/スコープ変更）

## Done

- [x] Issue #320 fetched and analyzed
- [x] Branch `320-verify-ql1-link-targets` created
- [x] PR #330 created
- [x] Task 1: Design review completed
- [x] Task 2: `TestCheckSourceLinks_JsonSide` added — committed `197bc96`
- [x] Task 3: `TestCheckSourceLinks_DocsMdSide` added — committed `197bc96`
- [x] Task 4: JSON side anchor check implemented — committed `38e18cc`
- [x] Task 5: Docs MD side anchor check implemented — committed `38e18cc`
- [x] Task 6: FAIL diff recorded (v6:656 v5:658 v1.4:613 v1.3:578 v1.2:588) — committed `3928aa4`
- [x] Task 8: Expert review (QA + SE) — 2 Findings fixed — committed `3928aa4`
- [x] Task 9: Diff check — committed `267caa7`
- [x] **Session discovery**: 現在の実装（anchor存在確認）はIssue本来の意図を満たさない。「意図した場所への到達可能確認」が必要 → Issue SC見直しと実装再設計が必要
