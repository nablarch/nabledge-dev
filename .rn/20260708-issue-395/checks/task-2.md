# task-2 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| `参照:` instruction in `nabledge-6/workflows/qa.md` specifies the new path+section-title format | OK | Line 190-205: instruction now reads "For each cited section, grouped by file" with Page title, Path, and Section title format, plus example output | | |
| Anchor algorithm not present (no `#anchor` in the instruction) | OK | No `#anchor` text appears anywhere in the new instruction block (lines 190-205) | | |
| No existing QA instruction content removed or altered beyond the citation format change | OK | Lines 185-189 (preceding content) and line 207 onward (following content) are unchanged; only line 190 was replaced with the expanded instruction | | |

## Overall Verdict

- Self-check: OK

---

## Fix round 1 (2026-07-08)

Two defects found and fixed in the path derivation rules:

**Defect 1 (qa.md + code-analysis.md): Wrong path derivation rule**
- Old rule said "replace `knowledge/` with `docs/`" — dead operation because JSON paths from `read-sections.sh` are relative paths like `component/libraries/libraries-database.json` (no `knowledge/` prefix).
- Fixed: now says "prepend `.claude/skills/nabledge-6/docs/`" (qa.md) and "prepend `../../.claude/skills/nabledge-6/docs/`" (code-analysis.md), with concrete examples.

**Defect 2 (qa.md only): `Path: ` label inconsistency**
- Template description had `Path: .claude/...` label but the example omitted it.
- Fixed: removed `Path: ` label from the template description to match the example (the example is the authority).

**Additional improvement (qa.md): multi-section example and restructured instruction**
- Added a second entry to the example showing two sections from the same file (`条件を指定して検索する` under ユニバーサルDAO).
- Restructured the instruction block: "One entry per cited file, in this format:" followed by the format, then "Path derivation:" as a separate labeled rule.
