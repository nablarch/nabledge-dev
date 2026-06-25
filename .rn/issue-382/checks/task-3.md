# task-3 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| bm25-search.sh in allowedTools | OK | `run_qa.py` line 192: `"Bash(bash scripts/bm25-search.sh *)"` added to `--allowedTools`; `test_uses_allowed_tools_as_specified` asserts it and passes | | |
| e2e-prompt.md step numbers match new qa.md | OK | Step 1 (skip hearing), Step 2 (BM25 search), Step 3 (check-answerable), Step 4 (semantic-search, conditional), Step 7 (output) — matches new qa.md flow | | |
| workflow_details schema updated to new structure | OK | `SAMPLE_WORKFLOW_DETAILS` updated to step2/step3/step4/step5/step6; `test_parses_workflow_details`, `test_parses_bm25_sections`, `test_parses_check_answerable_result`, `test_returns_workflow_details` all assert new keys | | |
| All tests pass | OK | `python3 -m pytest tools/benchmark/tests/ -x -q` → 168 passed after fixes | | |

## QA Expert Review

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Meaningful tests/verification | OK | Cascade fallback test added (step5 absent→bm25 fallback, all-empty→0); step6 FAIL+regenerated test added; 168 tests pass |
| Edge case coverage | OK | 4 findings raised; 3 fixed (cascade test, regeneration test, qa.md "Otherwise" wording); 1 invalid (early-stop→MarkerError is existing behavior, not regression) |

## Overall Verdict

- Self-check: OK
- QA: OK (after fix round)
- Ready for user review: Yes
