# Expert Review: Prompt Engineer

**Date**: 2026-03-06
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 3 files

## Overall Assessment

**Rating**: 4/5
**Summary**: The SKILL.md is well-structured and operationally complete. The 10-step workflow is logically ordered, the sub-agent prompt is adequately constrained, and the baseline comparison logic is sound. The main weakness is a timestamp variable collision that could break the baseline copy step.

## Key Issues

### High Priority

1. **Scenario ID prefix consistency (qa-* vs ks-*)**
   - Description: SKILL.md and scenarios.json both use `qa-*` (in sync), but the task document specified `ks-*`. No action needed if `qa-*` is intentional — currently consistent.
   - Decision: Defer (SKILL.md and scenarios.json agree on `qa-*`; task doc was aspirational)
   - Reasoning: Both files match; the rename was intentional

2. **Timestamp variable collision between Step 5 workspace and Step 9 baseline copy**
   - Description: Step 5 workspace uses a timestamp captured at run start. Step 9a captures a NEW `TIMESTAMP=$(date +%Y%m%d-%H%M%S)` at baseline start (after scenarios complete). Step 9c then tries to copy from `.tmp/nabledge-test/run-${TIMESTAMP}/` using this NEW timestamp — pointing to a non-existent directory.
   - Suggestion: Capture `RUN_TIMESTAMP` once before Step 4 and use it consistently for workspace path and baseline copy path.
   - Decision: **Implement Now**

### Medium Priority

3. **Sub-agent prompt lacks working directory context**
   - Description: Task tool prompt uses relative paths (`read .claude/skills/nabledge-<version>/SKILL.md`) but sub-agents may not inherit parent cwd.
   - Suggestion: Add working directory instruction to sub-agent prompt.
   - Decision: Defer (Claude Code sub-agents inherit cwd from parent in practice)

4. **Detection logic for ca-* expectations is underspecified**
   - Description: Heuristic pattern matching for ca-* expectations may miss strings not matching listed patterns.
   - Suggestion: Add catch-all rule for unmatched expectations.
   - Decision: Defer to future

5. **`--trials N` averaging logic unspecified**
   - Description: How per-trial files are saved and averaged is not defined.
   - Decision: Defer to future (trials feature is secondary to baseline)

### Low Priority

6. **Step 2 fallback warning message not specified** — Defer
7. **Comparison report missing 時間CV row** — Defer
8. **date command inconsistency (local vs UTC)** — Defer (local time matches user expectation in practice)
9. **Output delimiter could collide with markdown headings** — Defer

## Positive Aspects

- "Measure everything, judge nothing" principle clearly stated with 5 concrete prohibitions
- Sequential execution requirement correctly motivated and justified
- workspace-to-baseline separation (`.tmp/` vs `baseline/`) is architecturally clean
- `latest` symlink uses relative path (portable)
- 目視判定 table acknowledges limits of automated detection
- 総合評価 section provides concrete guidance for third-party assessment
- `grading.json` evidence field requires quoted text (prevents false positives)

## Recommendations

1. Fix timestamp collision (implement now — single-line fix, high impact)
2. Resolve qa-* vs ks-* naming intent in project documentation
3. Future: specify `--trials N` averaging logic
4. Future: consider `--dry-run` mode

## Files Reviewed

- `.claude/skills/nabledge-test/SKILL.md` (workflow/prompt specification)
- `.pr/00129/nabledge-test-v2-task.md` (task specification)
- `.claude/skills/nabledge-test/scenarios/nabledge-6/scenarios.json` (scenario data)
