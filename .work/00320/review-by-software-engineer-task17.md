# Expert Review: Software Engineer (Task 17 — subtitle fix)

**Date**: 2026-05-11
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 2 files

## Summary

0 Findings

## Findings

None.

## Observations

- **Observation 1** — Comment in `elif subtitle_title:` branch says "DocTitle collapsed them out of their original section node" but pre-biblio items (comment, system_message, target, substitution_definition) also appear here. No content impact. Clarifying the comment is optional.

- **Observation 2** — h3 subsections of the promoted subtitle are walked as level=2 (pre-existing behavior, not introduced by this change). Spec §2-2 requires level to match heading depth. Separate issue if it affects real corpus files.

- **Observation 3** — `test_subtitle_with_subsequent_sections` does not assert `sections[1].level`, leaving the pre-existing level-for-subtitle-children behavior undocumented in tests.

## Positive Aspects

- Fix is logically sound: subtitle→sections[0] correctly resolves verify QL1 FAIL for labels targeting subtitle headings.
- The `not parts.top_title` guard prevents double-processing of subtitle content.
- Multiple subtitles are impossible by docutils design — no guard needed.
- `visit_subtitle` for subtitle inside admonitions/topics/sidebars is unaffected.

## Files Reviewed

- `tools/rbkc/scripts/common/rst_ast_visitor.py` (source code)
- `tools/rbkc/tests/ut/test_rst_ast_visitor.py` (tests)
