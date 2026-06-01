# Expert Review: Software Engineer / QA Engineer

**Date**: 2026-06-01
**Reviewer**: AI Agent as Software Engineer + QA Engineer
**Files Reviewed**: evaluate.py, report.py, run_qa.py, test_evaluate.py, test_report.py, test_run_qa.py, benchmark-design.md, HOW-TO-RUN.md, e2e-prompt.md (9 files)

## Summary

0 Findings

## Findings

None.

## Observations

1. **`call_llm` is dead code** — `call_llm` and `extract_json_from_result` (evaluate.py lines 85–132) are no longer invoked by any production path after LLM-judge removal. They are tested and not broken; deferring removal is a reasonable tradeoff since the test captured a real historical bug (OSError on long argv).

2. **`test_sets_aws_ca_bundle` asserts inside patched env scope** — Slightly unusual pattern; an explicit captured-variable pattern would be clearer. Correct as-is.

3. **`_run_deepeval_metric` silent None path in env-setup test** — The env-var test patches `_run_deepeval_metric` to return a bare float, causing a silent TypeError caught by `except Exception`. Test intent is env-var propagation only, not score computation — passes correctly but a docstring note would help.

4. **Summary report missing minimum score** — `benchmark-design.md` lists "最低スコア" in the summary format, but `format_summary_report` only outputs average and pass-count. Minor divergence introduced in this PR; not blocking.

5. **`LLMTestCaseParams` deprecation warning** — 10 warnings emitted during test run. Will become an error in a future DeepEval release. Migration to `SingleTurnParams` is recommended.

6. **`TestRunE2eScenario` does not use `### Answer` marker** — Integration tests exercise legacy fallback path, not the new marker path. The marker path is well-covered by `TestParseE2eResponse`; adding one end-to-end test through `run_qa_scenario` with the marker would give full coverage.

## Positive Aspects

- Clean architecture: `build_deepeval_test_case` / `compute_deepeval_metrics` / `evaluate_scenario` separation follows single-responsibility. Each function is independently testable.
- Dual-format runner output support: fallback from `diagnostics.search_sections` to `workflow_details.step3.selected_sections` handles both formats without calling-code changes.
- Error isolation in `compute_deepeval_metrics`: individual metric failures return `None` rather than propagating, preventing one flaky metric from invalidating the full evaluation.
- `### Answer` marker design: fallback to full-text-before-`### Workflow Details` for legacy format is correct and tested.
- Test completeness: 143 tests, all passing. `TestRunE2eAllErrorHandling` is particularly thorough.
- Threshold rationale documented: `benchmark-design.md` explicitly documents threshold values with per-metric rationale tied to mission-critical quality standard.
- SSL/CA-bundle auto-setup: `AWS_CA_BUNDLE ← SSL_CERT_FILE` fallback is a practical corporate-environment affordance, fully specified by two tests.

## Files Reviewed

- tools/benchmark/scripts/evaluate.py (source code)
- tools/benchmark/scripts/report.py (source code)
- tools/benchmark/scripts/run_qa.py (source code)
- tools/benchmark/tests/test_evaluate.py (tests)
- tools/benchmark/tests/test_report.py (tests)
- tools/benchmark/tests/test_run_qa.py (tests)
- docs/benchmark-design.md (documentation)
- tools/benchmark/HOW-TO-RUN.md (documentation)
- tools/benchmark/prompts/e2e-prompt.md (configuration)
