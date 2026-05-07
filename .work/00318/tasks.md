# Tasks: fix: setting_guide files misclassified as about-nablarch due to wrong mapping pattern

**PR**: #328
**Issue**: #318
**Updated**: 2026-05-07

## In Progress

(none)

## Not Started

(none)

## Done

- [x] Task 1: Fix mapping pattern in v6.json and v5.json — committed `2dbd32f6b`
  - Corrected `application_framework/setting_guide/` → `application_framework/application_framework/setting_guide/`
  - v6: 353 files generated, verify OK
  - v5: 533 files generated, verify OK
  - v1.4/v1.3/v1.2: no mapping change needed (no setting_guide entries)
  - setting_guide files now under `setup/setting-guide/` (not `about/about-nablarch/`)
- [x] Task 2: Check PR diff — diff-check.md created, 63 files all expected
- [x] Task 3: Expert review and PR creation — 0 Findings, PR #328 updated — committed `6f2ec2d72`
