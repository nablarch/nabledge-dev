# Notes

## 2026-05-07

### Scope analysis

Two checks are missing from `check_ql1_link_targets()`:

1. **JSON side anchor check** (l.1869 in verify.py): `_anchor` is extracted from cross-doc links but silently discarded. When non-empty, must verify that target JSON's `sections[].title` maps to a slug matching the anchor.

2. **docs MD side anchor check** (l.1897 in verify.py): same pattern. When anchor is non-empty, must read target docs MD headings and confirm `github_slug(heading_text)` matches anchor.

Design spec §3-2-3 already covers both checks fully — no design doc changes needed before implementation. `github_slug.py` is available in `scripts/common/`.

Design doc §4 test correspondence table expects:
- `TestCheckSourceLinks_JsonSide` — for JSON side
- `TestCheckSourceLinks_DocsMdSide` — for docs MD side

These classes do not yet exist in `test_verify.py`.

## 2026-05-07 (implementation)

### Implementation

Both anchor checks implemented in `check_ql1_link_targets()`:

- JSON side: load target JSON, extract `sections[].title`, compute `github_slug(title)` for each, check if anchor matches any slug. Helper: `_json_section_slugs()`.
- Docs MD side: read target docs MD, extract ATX headings via regex `^#{1,6}\s+(.+?)...`, compute `github_slug(heading_text)` for each, check if anchor matches any slug. Helper: `_heading_slugs()`.

Dedup: file-level key `(type_, category, file_id)` for target existence; per-anchor key `(type_, category, file_id, anchor)` for anchor checks (avoids re-checking the same anchor in the same target when referenced from multiple source sections).

Existing test `test_pass_existing_target` was updated to remove `#foo` anchor (that test was about file existence, not anchor resolution; the `#foo` was incidental and now correctly triggers an anchor FAIL since the fixture JSON has empty sections).

### FAIL diff (all 5 versions)

Pre-change baseline: 0 new QL1 anchor FAILs (anchor check did not exist).

Post-change FAIL counts (new anchor FAILs only):
- v6: 656 FAIL lines total (all are new anchor FAILs — previous baseline had 0 QL1 anchor FAILs)
- v5: 658
- v1.4: 613
- v1.3: 578
- v1.2: 588

These are genuine RBKC bugs: anchors in JSON content referencing section titles that don't exist in the target JSON, or headings that don't exist in target docs MD. All are expected increases — the check was missing before. No unexpected increases.
