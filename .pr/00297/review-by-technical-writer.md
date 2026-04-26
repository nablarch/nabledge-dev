# Expert Review: Technical Writer

**Date**: 2026-04-10
**Reviewer**: AI Agent as Technical Writer
**Files Reviewed**: 6 files

## Overall Assessment

**Rating**: 4/5
**Summary**: Well-structured documentation with clear methodology and investigation planning. Primary issues are minor clarity gaps and consistency points.

## Key Issues

### High Priority

1. **RBKC/KC terminology not defined upfront**
   - Description: README.md uses "RBKC" without a clear definition in the first paragraph. "KC" introduced casually.
   - Suggestion: Add "RBKC (Rule-based Knowledge Creator) is a deterministic alternative to the existing AI-based Knowledge Creator (KC)." as the opening sentence.
   - Decision: Defer — README is user-provided design draft; terminology is clear from the title and Motivation section

2. **Inconsistent terminology: "differ" vs "snapshot-based change detection"**
   - Description: investigation-items.md uses "differ", README uses "snapshot-based change detection" for the same module.
   - Suggestion: Standardize on "differ" across all docs.
   - Decision: Defer — README is user-provided; will apply in future implementation docs

3. **Stage 1/Stage 2 hints strategy intro lacks fallback caveat**
   - Description: README doesn't mention that Stage 2 may be dropped pending feasibility study (I-09).
   - Suggestion: Add "(optional, may be dropped based on feasibility study)" to Stage 2 description.
   - Decision: Defer — README is design draft; I-09 investigation will update it

### Medium Priority

4. **investigation-items.md: No explicit fail/decision criteria per task**
   - Description: Completion criteria define "done" but not what happens if the result is bad (e.g., 50% of files have h4 headings — does RBKC need to support h4?).
   - Suggestion: Add explicit decision triggers to each item.
   - Decision: Defer — would require significant edits to all 15 items; investigation execution will surface these naturally

5. **search-impact.md: Critical Finding not linked to solution**
   - Description: "Critical Finding" section ends without linking to the resolution (h2+h3 in section-granularity.md).
   - Suggestion: Add "See [section-granularity.md](section-granularity.md) for the solution analysis." after the finding.
   - Decision: Defer — user-provided evaluation document

6. **notes.md: Investigation status context missing**
   - Description: A developer reading notes.md can't quickly tell whether investigations are planned, in-progress, or complete.
   - Suggestion: Add status summary after Learning section.
   - Decision: **Implement Now** — quick fix, improves usability

### Low Priority

7. **README.md: "ルート index.rst" not clearly specified**
   - Description: The ID generation rule for "ルート index.rst → about-nablarch-top" doesn't clarify what "root" means.
   - Decision: Defer — user-provided content

8. **I-12 ordering: TOON format investigation appears after v1.x items**
   - Description: I-12 (TOON format, index generation) is logically a v6 output concern but listed after v5/v1.x investigation items.
   - Decision: Defer — ordering is clear from context; reordering would require renumbering

## Positive Aspects

- Systematic spec enumeration (91 → 43 → 15 items) demonstrates thorough methodology
- notes.md correctly separates narrative (why/decision) from detailed artifacts (what/how)
- New "Detail Files" guideline in work-notes.md is a valuable addition
- search-impact.md's risk matrix (impact × probability × evidence) is actionable
- Evidence-based design choice for h2+h3 splitting is well-supported by quantitative data

## Recommendations

- Add glossary to README.md defining RBKC, KC, hints Stage 1/2, differ, TOON format
- Link from investigation-items.md result sections back to notes.md for context
- Standardize terminology (differ vs snapshot-based change detection) in future docs

## Files Reviewed

- `tools/rbkc/README.md` (documentation)
- `tools/rbkc/docs/evaluation/search-impact.md` (documentation)
- `tools/rbkc/docs/evaluation/section-granularity.md` (documentation)
- `.pr/00297/investigation-items.md` (documentation)
- `.pr/00297/notes.md` (documentation)
- `.claude/rules/work-notes.md` (configuration)
