# Expert Review: QA Engineer

**Date**: 2026-05-07
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 2 files

## Summary

0 Findings (after fixes applied)

## Findings (original — all fixed)

### Finding 1: Deduplication by file skips anchor validation for second-and-later links to the same file

**Violated clause**: `.claude/rules/development.md` — "Edge cases: ... A test suite that only covers the happy path is incomplete." Also spec §3-2-3: "target JSON の `sections[]` に section_title が実在" — must apply to every anchor-bearing link.

**Description**: The `seen` 3-tuple set deduplicated at file level. When the same file was linked first without anchor, subsequent links to the same file with an anchor hit `continue` and skipped the anchor check silently.

**Fix applied**: Separated file-existence dedup (`seen` / `missing_json`) from anchor dedup (`seen_anchors`). Anchor check now fires independently for every distinct `(type, cat, file_id, anchor)` regardless of whether the file was already seen. Added regression tests `TestCheckSourceLinks_JsonSideDedup` and `TestCheckSourceLinks_DocsMdSideDedup`.

### Finding 2: Missing test cases for the anchor-silenced-by-file-dedup scenario

**Violated clause**: `.claude/rules/development.md` — "Bug-revealing cases: Input that exercises each specific failure mode."

**Fix applied**: Added `TestCheckSourceLinks_JsonSideDedup::test_fail_anchor_missing_when_same_file_linked_no_anchor_first` and `TestCheckSourceLinks_DocsMdSideDedup::test_fail_docs_md_anchor_missing_when_same_file_linked_no_anchor_first` — confirmed RED before fix, GREEN after.

## Observations

- `_json_section_slugs` catches `json.JSONDecodeError` with `except Exception: return set()`. Over-reports (false FAIL) rather than under-reports — acceptable from a ゼロトレランス perspective.
- `_heading_slugs` uses ATX-only regex. RBKC docs.py emits ATX headings exclusively — no real-world risk.
- Deduplication intent for `seen` (avoid re-checking file existence) is architecturally sound.

## Positive Aspects

- Circular-avoidance architecture correctly implemented: `_heading_slugs` recomputes slugs from heading text via shared `github_slug.py`, independent of create side.
- `_json_section_slugs` correctly reads `sections[].title` without reusing create-side data structures.
- All test assertions are spec-derived, not implementation-derived.
- `test_fail_json_target_missing_with_anchor` correctly verifies no double-reporting on missing files.

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source code)
- `tools/rbkc/tests/ut/test_verify.py` (tests)
