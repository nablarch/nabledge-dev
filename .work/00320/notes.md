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
