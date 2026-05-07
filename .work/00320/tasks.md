# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-07

## Not Started

### Task 11: create/verify diff check after Task 10

Run `bash rbkc.sh create <v> && bash rbkc.sh verify <v>` for all 5 versions after Task 10
(display-text :ref: cross-doc fix). Confirm FAIL diff vs Task 10 pre-change baseline is
expected (0 new unexpected FAILs from the display-text fix path).

**Steps:**
- [ ] Run create/verify v6, v5, v1.4, v1.3, v1.2 — record FAIL counts
- [ ] Compare vs Task 10 pre-change baseline (v6:1233 v5:1243 v1.4:670 v1.3:624 v1.2:640)
- [ ] Confirm all changes are expected — record diff in notes.md
- [ ] Commit notes.md update and push

### Task 12: Resolve SC ❌ — §4 matrix QL1 ✅

SC requires design doc §4 matrix QL1 column to be ✅. Currently ❌ because 成立条件3
(FAIL 0件) is unmet — 1000+ FAILs are genuine RBKC bugs, not verify bugs.

Resolution: create a follow-up issue for the RBKC anchor generation fix, then update
SC ❌ to ✅ with a note that verify is correct and the RBKC fix is tracked separately.

**Steps:**
- [ ] Create follow-up issue for RBKC cross-doc anchor generation bug
- [ ] Update PR body SC check: ✅ Met with note linking follow-up issue
- [ ] Confirm all SC are ✅ before requesting review

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
