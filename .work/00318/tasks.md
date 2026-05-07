# Tasks: fix: setting_guide files misclassified as about-nablarch due to wrong mapping pattern

**PR**: (TBD)
**Issue**: #318
**Updated**: 2026-05-07

## In Progress

### Task 1: Fix mapping pattern in v6.json and v5.json

Fix `application_framework/setting_guide/` → `application_framework/application_framework/setting_guide/` in both v6.json and v5.json.

Water horizontal check confirmed: v1.4/v1.3/v1.2 have no setting_guide entry → no change needed.

**Steps:**
- [ ] Edit `tools/rbkc/mappings/v6.json`: correct the setting-guide pattern
- [ ] Edit `tools/rbkc/mappings/v5.json`: correct the setting-guide pattern (same bug)
- [ ] Run `bash rbkc.sh create 6 && bash rbkc.sh verify 6` — confirm 0 FAILs
- [ ] Run `bash rbkc.sh create 5 && bash rbkc.sh verify 5` — confirm 0 FAILs
- [ ] Run verify for v1.4/v1.3/v1.2 (create not needed; mapping not changed)
- [ ] Confirm setting_guide files now appear under `setup/setting-guide/` (not `about/about-nablarch/`)
- [ ] Push trial result for MD readability review (閲覧用MD確認)
- [ ] Commit the mapping fix

## Not Started

### Task 2: Check PR diff

Check that the PR diff contains only the expected changes.

**Steps:**
- [ ] Run `git diff main` and verify only mapping files and regenerated knowledge files are changed
- [ ] Output diff check result to `.work/00318/diff-check.md`
- [ ] Confirm with user

### Task 3: Expert review and PR creation

**Steps:**
- [ ] Run expert review (Prompt Engineer for mapping config change)
- [ ] Save review to `.work/00318/review-by-prompt-engineer.md`
- [ ] Create PR via `/pr create`

## Done

(none yet)
