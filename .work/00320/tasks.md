# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-07

## In Progress

### Task 10: Add cross-doc `:ref:` target validation to `check_source_links()`

Issue SC revised. The correct check is: when a RST `:ref:label` resolves via `label_map`
to a cross-document target `(file_id, section_title, anchor)`, verify that:
1. target JSON exists on disk
2. target JSON `sections[].title` contains `section_title`
3. target docs MD exists on disk
4. target docs MD heading slugs contain `anchor` (= `github_slug(section_title)`)

This is distinct from `check_ql1_link_targets()` which checks anchors in MD output links.
Both checks are needed (see design doc §3-2-3 implementation note).

**Context**:
- `check_source_links()` in `verify.py` — RST `:ref:` processing at line ~2122
- `label_map` entries with `file_id` set = cross-doc targets
- Helper `_json_section_slugs()` and `_heading_slugs()` already exist in `check_ql1_link_targets()`
- Need to extract as shared helpers or duplicate inline
- Design doc §3-2-3 updated, §4 matrix updated to ✅

**Steps:**
- [x] Issue #320 SC revised (cross-doc `:ref:` target + anchor reach validation)
- [x] Design doc §3-2-3 updated with implementation note + §4 matrix updated to ✅
- [x] TDD: `TestCheckSourceLinks_CrossDoc` (6 tests) added — RED confirmed
- [x] Implement cross-doc target validation in `check_source_links()` — 480 tests GREEN
- [x] Run verify on all 5 versions, record FAIL diff (notes.md)
- [ ] Expert review (QA + SE)
- [ ] Commit and push

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
