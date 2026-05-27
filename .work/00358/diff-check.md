# Diff Check: #358

**Date**: 2026-05-27
**Branch**: 358-fix-dynamic-check-false-positives vs main

## Summary

The diff contains exactly the two intended changes and nothing extraneous.

## tools/tests/test-setup.sh

**Expected change**: Add WARN level for "sections out of order" dynamic check results.

**Actual changes**:
1. Added `verify_warn=0` counter initialization (line ~190)
2. Updated DYNAMIC_RESULTS comment to include WARN state
3. Added `sections_out_of_order` local variable and detection logic
4. Added WARN branch in result classification: `skill_read=1` && `answered=0` && `sections_out_of_order=1` → `[WARN]`, `verify_warn=1`, `result_status="WARN"` — does NOT set `verify_fail=1`
5. Updated exit summary: WARN-only produces exit 0 with message; FAIL+WARN reports both

**Verdict**: ✅ Only the intended WARN classification change. No extraneous changes.

## README.md

**Expected change**: Add FAIL/WARN investigation procedure subsection.

**Actual changes**:
1. Added "**FAIL / WARN が出た場合**" subsection after the dynamic check description
   - Log file location: `.tmp/nabledge-test/dynamic-check-*.log`
   - FAIL — SKILL.md not read: setup failure
   - FAIL — missing sections: skill malfunction
   - WARN — sections out of order: formatting variation, check answer text for correct section order

**Verdict**: ✅ Only the intended README subsection. No extraneous changes.

## Overall

Both files contain only the changes described in tasks.md. No unrelated code touched.
