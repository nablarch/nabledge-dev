# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-08

## In Progress

### Task 13: Fix RBKC create — cross-doc section_title missing from sections[]

verify FAIL 0件 は §4 マトリクス ✅ 成立条件 3。現在 v6:1422, v5:1443, v1.x:238-283 FAIL。

**Root cause (確定):**
- h1 直前ラベルに `section_title=h1_title` / `anchor=github_slug(h1_title)` が設定されていた
- JSON スキーマ上 h1 は `title` のみ（`sections[]` に入らない）→ verify が誤って FAIL
- fix: `labels.py` `build_label_doc_map()` で `title == doc_title` なら `section_title=""` / `anchor=""`

**Steps:**
- [x] v6 FAIL パターンを列挙・分類（root cause 特定）
- [x] RBKC create 修正（TDD: RED→GREEN、484件全テスト GREEN）
- [x] 全5バージョン create + verify — v6:38, v5:48, v1.4:32, v1.3:28, v1.2:32
- [ ] 残存 38/48/32/28/32 FAIL の root cause 調査・修正（ラベルが非見出しコンテンツを取得するケース）
- [ ] 全5バージョン create + verify — FAIL 0件確認
- [ ] 設計書 §4 マトリクス QL1 を正しく ✅ に更新
- [ ] PR #330 SC を ✅ に更新
- [ ] commit & push

## Done

- [x] Issue #320 fetched and analyzed
- [x] Branch `320-verify-ql1-link-targets` created
- [x] PR #330 created
- [x] Task 1: Design review completed
- [x] Task 2: `TestCheckSourceLinks_JsonSide` added — committed `197bc96`
- [x] Task 3: `TestCheckSourceLinks_DocsMdSide` added — committed `197bc96`
- [x] Task 4: JSON side anchor check in `check_ql1_link_targets()` implemented — committed `38e18cc`
- [x] Task 5: Docs MD side anchor check in `check_ql1_link_targets()` implemented — committed `38e18cc`
- [x] Task 6: FAIL diff recorded (v6:656 v5:658 v1.4:613 v1.3:578 v1.2:588) — committed `3928aa4`
- [x] Task 8: Expert review (QA + SE) — 2 Findings fixed — committed `3928aa4`
- [x] Task 9: Diff check — committed `267caa7`
- [x] Issue #320 SC revised + design doc §3-2-3 updated + §4 matrix ✅
- [x] Task 10: cross-doc :ref: validation in check_source_links() + expert review (1 Finding fixed) — committed `56b91449b`
- [x] Task 11: create/verify diff check — v6:1422, v5:1443, v1.4:262, v1.3:238, v1.2:283 — all expected — committed `3f217acf5`
- [x] Task 12: Issue #333 作成→クローズ（#320 スコープ内と判明）、PR #330 SC を ❌ Blocked に戻す
