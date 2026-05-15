# Expert Review: Software Engineer (Phase A)

**Date**: 2026-05-15
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 35 files (Phase A diff against main)

## Summary

1 Finding — fixed in `819677fe9`

## Findings

1. **Stale path in search-design.md**
   - Violated clause: `.claude/rules/work-notes.md` — design docs reflect current state only
   - Description: Line 11 referenced `tools/benchmark/prompts/` instead of `tools/benchmark/components/prompts/`
   - Fix: Updated to correct `components/` paths

## Observations

- `benchmark-design.md` judge prompt references (`prompts/c-claim-judge.md`, `prompts/hallucination-judge.md`) are correct — they remain at `prompts/`

## Positive Aspects

- PROMPTS_DIR split is clean and correct across all scripts
- jq fix pattern `([...][0])` correctly handles empty-match
- RBKC revert is complete — zero diff against main for skills/RBKC
- TDD discipline followed throughout

## Files Reviewed

- tools/benchmark/scripts/*.py (source code)
- tools/benchmark/components/scripts/*.sh (shell scripts)
- .work/00343/design/*.md (design docs)
