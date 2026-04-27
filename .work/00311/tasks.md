# Tasks: Excel-derived docs MD readability improvement

**PR**: TBD
**Issue**: #311
**Updated**: 2026-04-27

## In Progress

### [A] Excel table detection investigation
**Steps:**
- [ ] Review all P2 sheets in `.work/00299/phase22/sheet-classification.md` (or locate equivalent classification data)
- [ ] Categorize each P2 sheet as:
  - (a) Should be P1 but misclassified (e.g., `3.PCIDSS対応表` — 2-column table caught by §8-2 `useful_width ≤ 2 → P2`)
  - (b) Correctly P2 but readability is poor (in-cell line breaks / section headings collapsed)
  - (c) Correctly P2 and no readability issue
- [ ] Quantify counts for (a) and (b)
- [ ] Propose improvement for (a): relax §8-2 rule / mapping override / status quo
- [ ] Present proposal to user, wait for approval

## Not Started

### [B] P2 in-cell line break / heading investigation
**Steps:**
- [ ] Identify P2 sheets where in-cell line breaks or heading-like cells are lost in docs MD
- [ ] Propose how to preserve them (paragraph breaks, promote `##`, etc.)
- [ ] Present proposal to user, wait for approval

### [C] Implementation — table misclassification fix (after [A] approved)
**Steps:**
- [ ] Update `tools/rbkc/scripts/create/converters/xlsx_common.py` (P1/P2 classify logic)
- [ ] Update `tools/rbkc/docs/rbkc-converter-design.md` §8 if rule changed
- [ ] Write verify TDD tests (if new verify check needed)
- [ ] Run create → verify for all 5 versions, confirm FAIL count diff is expected
- [ ] Verify docs MD visually

### [D] Implementation — P2 readability fix (after [B] approved)
**Steps:**
- [ ] Update `tools/rbkc/scripts/create/converters/xlsx_common.py` (P2 rendering logic)
- [ ] Update specs as needed
- [ ] Write verify TDD tests if new checks needed
- [ ] Run create → verify for all 5 versions
- [ ] Verify docs MD visually

### [E] Expert review & PR creation
**Steps:**
- [ ] Expert review (Software Engineer + QA Engineer)
- [ ] Fix any Findings
- [ ] Create PR via `/pr create`

## Done

- [x] Created feature branch `311-excel-docs-md-readability`
- [x] Created `.work/00311/tasks.md`
