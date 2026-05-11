# Expert Review: Software Engineer

**Date**: 2026-05-11
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 3 files

## Summary

0 Findings (after fix applied)

Original review had 1 Finding (json_key dedup bug) — fixed before this record.

## Findings

### Finding 1 (FIXED): `json_key` dedup silently skipped `section_title` checks

- Violated clause: Spec `rbkc-verify-quality-design.md §3-2-3`: "target JSON の `sections[]` に section_title が実在" — verify 検証 (JSON side)
- Description: `_cross_doc_json_seen` used a single set for both `json_key` (3-tuple: type/category/file_id) and `st_key` (4-tuple: + section_title). Once `json_key` was seen, all subsequent labels pointing to the same file_id — with different section_title values — skipped both the existence check and section_title check.
- Fix applied: Separated into three distinct dedup sets — `_cross_doc_file_seen` (file existence), `_cross_doc_st_seen` (section_title), `_cross_doc_md_seen` (anchor). Section_title check now always runs when the file exists, guarded only by `st_key`.
- Regression test added: `test_fail_different_labels_same_file_id_different_section_titles`

## Observations

- `_section_titles_from_json` uses `import json as _json` inside function body while module already imports `json`. Redundant but harmless.
- `_heading_slugs_from_md` compiles `_ATX_RE` on every call (local constant). Negligible for this use case.
- `_ATX_RE` correctly handles optional trailing ATX close sequence (`## Foo ##`).
- `test_pass_display_text_ref_with_valid_target` only tests PASS path; no FAIL test for "display-text :ref: where target JSON exists but section_title not found" — not reachable as a gap after Finding 1 fix.

## Positive Aspects

- Architecture: `_check_cross_doc_target` closure centralizes all cross-doc checks, avoiding duplication across display-text and bare-label branches.
- Circular-avoidance: `_heading_slugs_from_md` independently computes slugs via `github_slug.py` rather than trusting create-side output.
- Independence: `_section_titles_from_json` reads JSON directly, no create-side imports.
- Dedup design intent is sound with three separate sets after fix.
- `run.py` wiring is correct.

## Files Reviewed

- tools/rbkc/scripts/verify/verify.py (source code)
- tools/rbkc/scripts/run.py (source code)
- tools/rbkc/tests/ut/test_verify.py (test code)
