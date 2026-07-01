# Task #1 Self-Check

**Date**: 2026-07-01

## Completion Criteria

| Criterion | Status | Evidence |
|-----------|--------|----------|
| `tools/benchmark/scenarios/code-analysis.json` exists with ≥3 scenarios, each with ≥2 `must` facts | OK | 3 scenarios, each with 3 `must` facts |
| `tools/benchmark/scripts/run_code_analysis.py` exists and exits 0 on dry-run | OK | `--dry-run` exits 0, prints 3 scenarios |
| `tools/benchmark/scripts/check_format_code_analysis.py` detects unreplaced placeholders, missing sections, absent Mermaid blocks | OK | 42 tests pass including all edge cases |
| `tools/benchmark/HOW-TO-RUN-CODE-ANALYSIS.md` exists with sufficient commands | OK | Covers dry-run, single run, full run, format check, output interpretation |

## Test Results

```
42 passed in 0.07s
```

## Notes

- `evaluate_scenario` from `evaluate.py` passes empty `retrieval_context=[]` — works as-is (DeepEval handles empty list)
- `project_dir` defaults to parent of `skill_dir` so `find-file.sh` can discover Java files
- Java fixtures from `.claude/skills/nabledge-1.4/knowledge/assets/` used as known inputs
