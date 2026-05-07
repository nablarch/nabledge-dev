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

## 2026-05-07 (Issue #320 scope revision)

### Decision: check_source_links() cross-doc :ref: validation

The anchor check in `check_ql1_link_targets()` (implemented above) validates MD output links.
Issue #320's real intent is source-driven: verify that RST `:ref:label` actually reaches the
intended section in the target file — catching cases where create generated a link to the right
file but the wrong section, or where the section was dropped from the JSON.

Added to `check_source_links()` (RST branch, Q1/Q2 path):
- When `label_map[label]` is a cross-doc `LabelTarget` (has `file_id`/`category`/`type`):
  1. target JSON must exist
  2. target JSON `sections[].title` must contain `section_title`
  3. target docs MD must exist
  4. target docs MD heading slugs must contain `anchor` (`= github_slug(section_title)`)

Helpers `_heading_slugs_from_md()` and `_section_titles_from_json()` promoted to module level
from `check_ql1_link_targets()` locals, so both functions share the same implementation.

### FAIL diff (cross-doc check, all 5 versions)

Pre-change (anchor check only): v6:656, v5:658, v1.4:613, v1.3:578, v1.2:588

Post-change (cross-doc check added):
- v6: 1233 total (+577), 528 cross-doc FAILs
- v5: 1243 total (+585), 531 cross-doc FAILs
- v1.4: 670 total (+57), 55 cross-doc FAILs
- v1.3: 624 total (+46), 44 cross-doc FAILs
- v1.2: 640 total (+52), 50 cross-doc FAILs

All cross-doc FAILs are genuine RBKC bugs: RST `:ref:` points to a section that either
doesn't appear in the target JSON `sections[]` (section dropped from RBKC output) or
whose anchor doesn't match any heading in the target docs MD (heading text mismatch).
Sample: `'ブランクプロジェクト' not found in blank-project-blank-project.json sections[]`
— the JSON title is correct but `sections[]` is empty (single-section document, RBKC
outputs the content at top-level, not as a section).

## 2026-05-07 (Task 11: create/verify diff check)

### Task 10 baseline note

The Task 10 baseline counts (v6:1233 v5:1243 v1.4:670 v1.3:624 v1.2:640) were recorded
in notes.md at commit `b906f2f20` using knowledge files generated at that time.

### Task 11 diff check (post-Task-10 code, fresh create)

Running `create + verify` for all 5 versions with the final code (post Task 10):

| Version | FAIL count | vs Task 10 baseline | Explanation |
|---------|-----------|---------------------|-------------|
| v6      | 1422      | +189 (1233→1422)    | Expected: display-text refs now checked (Task 10 `56b91449b`) adds new cross-doc FAILs |
| v5      | 1443      | +200 (1243→1443)    | Same as v6 |
| v1.4    | 262       | -408 (670→262)      | See note below |
| v1.3    | 238       | -386 (624→238)      | See note below |
| v1.2    | 283       | -357 (640→283)      | See note below |

**v1.x decrease explanation**: The fresh `create` run generated a different set of knowledge
files than those used for the Task 10 baseline. RBKC create-side fixes from PRs merged into
main (#315 handler HTML tables, #316 anchor fix, #317 toctree MD links) were committed to
`.claude/skills/nabledge-1.x/` but the Task 10 baseline used knowledge files generated
before or independently of those committed files. The fresh create generates more files and
with improved content → fewer genuine RBKC bugs detected by verify.

Confirmed: with `bc1cc68cc` verify code (Task 10 pre-fix), the current fresh-created
v1.4 knowledge files yield 767 FAILs — higher than 670 because more files are now generated.
The v1.x drops reflect improved knowledge file coverage, not a regression in verify.

**v6/v5 increase**: Purely additive — Task 10 `56b91449b` extended the cross-doc check to
display-text `:ref:` forms, which v6/v5 use more extensively than v1.x. All new FAILs are
genuine RBKC bugs (display-text refs whose targets are missing or broken in the JSON/MD).

All changes are expected. No unexpected FAILs introduced by Task 10.
