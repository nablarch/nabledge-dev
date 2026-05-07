# Tasks: verify QL1 link target validation

**PR**: #330
**Issue**: #320
**Updated**: 2026-05-07

## Not Started

### Task 2: TDD — test for JSON side anchor check (RED)
Write failing tests for `check_ql1_link_targets()` — JSON side anchor validation.
New class: `TestCheckSourceLinks_JsonSide` (per design doc §4 test correspondence table).

**Steps:**
- [ ] Add `TestCheckSourceLinks_JsonSide` class in `tests/ut/test_verify.py`
- [ ] `test_pass_json_anchor_exists`: link `#foo` → target JSON sections contain title that slugs to `foo` → PASS
- [ ] `test_fail_json_anchor_missing`: link `#nosuch` → no matching section title in target JSON → FAIL `[QL1] JSON link anchor not found`
- [ ] `test_pass_json_link_no_anchor`: link without `#` → file exists → PASS (existing behavior unchanged)
- [ ] `test_fail_json_target_missing_with_anchor`: target JSON missing (anchor irrelevant) → FAIL `JSON link target missing` only
- [ ] Confirm all new tests are RED (implementation not yet done)

### Task 3: TDD — test for docs MD side anchor check (RED)
Write failing tests for `check_ql1_link_targets()` — docs MD side anchor slug match.
New class: `TestCheckSourceLinks_DocsMdSide` (per design doc §4 test correspondence table).

**Steps:**
- [ ] Add `TestCheckSourceLinks_DocsMdSide` class in `tests/ut/test_verify.py`
- [ ] `test_pass_docs_md_anchor_slug_match`: link `#foo` → target docs MD has heading `## Foo` → `github_slug("Foo") == "foo"` → PASS
- [ ] `test_fail_docs_md_anchor_slug_mismatch`: link `#bar` → target docs MD heading slugs to `foo` only → FAIL `[QL1] docs MD link anchor not found`
- [ ] `test_pass_docs_md_link_no_anchor`: link without `#` → file exists → PASS (existing behavior unchanged)
- [ ] Confirm all new tests are RED

### Task 4: Implement JSON side anchor check (GREEN)
Implement anchor validation in `check_ql1_link_targets()` for JSON side.

**Steps:**
- [ ] In `check_ql1_link_targets()`, after confirming target JSON exists, load target JSON
- [ ] Extract `sections[].title` from target JSON
- [ ] If anchor is non-empty, compute `github_slug(sec_title)` for each section title and check if anchor matches any
- [ ] If no match: append `[QL1] JSON link anchor not found: ...` to issues
- [ ] Run Task 2 tests → confirm GREEN
- [ ] Run all 5 versions: `bash rbkc.sh create v6 && bash rbkc.sh verify v6` (etc.) — record FAIL diff

### Task 5: Implement docs MD side anchor check (GREEN)
Implement anchor validation in `check_ql1_link_targets()` for docs MD side.

**Steps:**
- [ ] In `check_ql1_link_targets()`, after confirming target docs MD exists, read it
- [ ] Extract all headings using `_HEADING_RE` or similar
- [ ] For each heading, compute `github_slug(heading_text)` 
- [ ] If anchor is non-empty and no slug matches: append `[QL1] docs MD link anchor not found: ...` to issues
- [ ] Run Task 3 tests → confirm GREEN
- [ ] Run all 5 versions: `bash rbkc.sh create <v> && bash rbkc.sh verify <v>` — record FAIL diff

### Task 6: Run verify on all 5 versions and record FAIL diff
Baseline before/after FAIL comparison for all 5 versions.

**Steps:**
- [ ] Run `bash rbkc.sh verify v6` (and v5, v1.4, v1.3, v1.2) on main baseline
- [ ] Run same after Task 4+5 implementation
- [ ] Record per-version FAIL count diff in `.work/00320/notes.md`
- [ ] Confirm: zero unexpected increases

### Task 7: Update design doc §4 matrix
Update `rbkc-verify-quality-design.md` §4 matrix QL1 rows from ⚠️ to ✅.
Wait for QA expert review approval before updating.

**Steps:**
- [ ] After expert review approves the implementation (zero Findings)
- [ ] Update §4 matrix QL1 rows to ✅
- [ ] Commit design doc update

### Task 8: Expert review (QA Engineer + Software Engineer)
Run expert review per `.claude/rules/expert-review.md`.

**Steps:**
- [ ] Launch QA Engineer review
- [ ] Launch Software Engineer review
- [ ] Address all Findings
- [ ] Save results to `.work/00320/review-by-qa-engineer.md` and `review-by-software-engineer.md`

### Task 9: Diff check — verify PR changes match expected scope
Check PR diff contains only expected changes.

**Steps:**
- [ ] Run `git diff main...HEAD --stat`
- [ ] Expected: `verify.py` (anchor check logic), `test_verify.py` (new test classes), `rbkc-verify-quality-design.md` (QL1 ✅), `.work/00320/` (notes, tasks, reviews)
- [ ] Confirm no unexpected files are changed
- [ ] Record result in `.work/00320/diff-check.md`

## Done

- [x] Issue #320 fetched and analyzed
- [x] Branch `320-verify-ql1-link-targets` created
- [x] PR #330 created
- [x] Existing implementation in `check_ql1_link_targets()` confirmed: `_anchor` extracted but silently discarded at l.1869 and l.1897
- [x] Design spec §3-2-3 confirmed: two missing checks identified
- [x] `github_slug.py` confirmed available in `scripts/common/`
- [x] Test correspondence table in §4 confirmed: `TestCheckSourceLinks_JsonSide` and `TestCheckSourceLinks_DocsMdSide` are the planned test classes
- [x] Task 1: Design review completed — §3-2-3 fully covers both checks; no design doc changes needed pre-implementation; dedup key stays file-level (anchor validation is per-file, not per-anchor); FAIL message formats confirmed as `[QL1] JSON link anchor not found` and `[QL1] docs MD link anchor not found`
