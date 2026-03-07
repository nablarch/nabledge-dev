# Knowledge Creator

Development rules for the knowledge-creator tool.

## Intermediate Artifacts

**Policy**: Intermediate artifacts (logs) are excluded from git and regenerated on each execution.

**Rationale**:
- Logs are large and not needed for code review
- Each developer can regenerate them locally
- Reduces repository size and PR noise

### Locations

Intermediate artifacts are stored under:
- `tools/knowledge-creator/.logs/v6/phase-a/` - Source list and classification
- `tools/knowledge-creator/.logs/v6/phase-b/traces/` - Generation traces
- `tools/knowledge-creator/.logs/v6/phase-b/executions/` - Generation execution logs with metrics
- `tools/knowledge-creator/.logs/v6/phase-c/` - Structure check results
- `tools/knowledge-creator/.logs/v6/phase-d/findings/` - Content check findings
- `tools/knowledge-creator/.logs/v6/phase-d/executions/` - Content check execution logs
- `tools/knowledge-creator/.logs/v6/phase-e/executions/` - Fix execution logs
- `tools/knowledge-creator/.logs/v6/phase-f/patterns/` - Pattern classification
- `tools/knowledge-creator/.logs/v6/phase-f/executions/` - Pattern classification execution logs
- `tools/knowledge-creator/.logs/v6/phase-g/resolved/` - Link-resolved knowledge files
- `tools/knowledge-creator/.logs/v6/summary.json` - Overall summary

### Workflow

```bash
# Run generation (logs are automatically created in .logs/ directory)
cd tools/knowledge-creator
./run.py --version 6 --test test-files-top3.json

# Logs are gitignored and will be regenerated on next execution
```

## Execution Logs

Each Phase B/D/E/F execution saves metrics to `executions/` directory:
- `{file_id}_{timestamp}.json` - Full Claude CLI response including:
  - `num_turns` - Number of agentic turns
  - `duration_ms` - Execution time in milliseconds
  - `total_cost_usd` - API cost in USD
  - `structured_output` - Generated knowledge file content

**Purpose**: Performance analysis, cost tracking, and debugging.

## Bug Reproduction Tests

When a bug is found, add a reproduction test before fixing it.

**File naming**: `tools/knowledge-creator/tests/test_fix_issue_<number>.py`

**Header**: Include the GitHub issue URL at the top for traceability.

**Pattern**: Call `main()` via the real entry point, not internal classes (Step1Classify, Step2Classify, PhaseB, etc.) directly.
Use `_run_main()` from `test_run_phases.py` if testing with fixtures, or patch `argparse`/`sys.argv` to call `main()` directly when testing against real sources.

**Real v6 sources**: Tests against `.lw/nab-official/v6/` must assert the sources exist
and fail with a clear error message if they are not available. Do not use `pytest.mark.skipif`
— silently skipping means the test provides no safety guarantee in that environment.
