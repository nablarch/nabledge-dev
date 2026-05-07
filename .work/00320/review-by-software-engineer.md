# Expert Review: Software Engineer

**Date**: 2026-05-07
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 1 file

## Summary

0 Findings (after fixes applied)

## Findings (original — all fixed)

### Finding 1: Dedup bug — file-level `seen` set suppresses anchor validation when no-anchor link appears first

**Violated clause**: Spec `rbkc-verify-quality-design.md` §3-2-3: "target JSON の `sections[]` に section_title が実在" and "target docs MD の heading slug と anchor が一致" — checks must fire for every anchor in a cross-document link.

**Description**: `seen` (3-tuple) deduplicated at file level. A subsequent anchor-bearing link to an already-seen file hit `continue` and skipped anchor validation. Confirmed with RBKC-generated JSON that routinely links the same file multiple times from different sections.

**Fix applied**: `seen` now guards file-existence check only. `missing_json` / `missing_md` track files confirmed absent so anchor check is skipped for them. Anchor check uses `seen_anchors` / `seen_md_anchors` (4-tuple) operating independently — fires for every distinct anchor regardless of prior file-level hits.

### Finding 2: `_heading_slugs` did not strip fenced code blocks — phantom slugs suppress true anchor FAILs

**Violated clause**: Spec §3-2-3 "target docs MD の heading slug と anchor が一致" — applies to rendered headings only; fenced-block `## Heading` is not a rendered heading and produces no GitHub anchor.

**Description**: Raw docs MD text was scanned without stripping fenced code blocks. A `## Fake Heading` inside ` ``` ` was matched and its slug added to the set — false-negative that hides RBKC anchor bugs.

**Fix applied**: `_heading_slugs` now calls `_strip_fenced_code(md_text)` before scanning. The helper already exists at module level and is used by `check_json_docs_md_consistency`. Added test `TestCheckSourceLinks_DocsMdSide::test_fail_docs_md_heading_in_fenced_block_not_an_anchor` — confirmed RED before fix, GREEN after.

## Observations

- `_heading_slugs` and `_json_section_slugs` are closures with no dependency on closure state. Could be module-level helpers for independent testability. Not a spec violation.
- `_json_section_slugs` `except Exception: return set()` may confuse diagnosis for corrupt JSON. Not a QL1 scope issue since `check_index_coverage` handles corrupt JSON separately.
- `_heading_slugs` does not pass `seen` dict to `github_slug` for duplicate-heading collision handling. Conservative behavior (strict direction). Not a spec violation.

## Positive Aspects

- Reuse of `_strip_fenced_code` (module-level helper) in `_heading_slugs` is architecturally clean.
- The `missing_json` / `missing_md` set approach cleanly separates "file not found" from "anchor not found" without double-reporting.
- Per-anchor `seen_anchors` 4-tuple deduplication correctly avoids duplicate error reports for repeated identical anchored links.
- `scripts.common.github_slug` reuse on both sides maintains the circular-avoidance architecture per spec §3-2-3.

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source code)
