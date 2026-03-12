# Knowledge Creator

Development rules for the knowledge-creator tool.

## Phase Naming Convention

When referring to phases, always use the full format: **Phase A: Preparation**, **Phase B: Generation**, etc.

| Phase | Name |
|-------|------|
| A | Preparation |
| B | Generation |
| C | Structure Check |
| D | Content Check |
| E | Fix |
| M | Finalization |

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

## Test Policy

### Principles

- Write only the minimum tests that improve quality
- E2E tests cover the main flows; unit tests cover only complex logic not covered by E2E

### Test Structure

    tests/
    ├── e2e/                     # E2E tests
    │   ├── test_e2e.py          # kc command tests by use case (single file)
    │   ├── conftest.py          # TestContext, _make_cc_mock, etc.
    │   └── generate_expected.py # Independent expected value generation
    └── ut/                      # Unit tests
        ├── conftest.py          # Shared fixtures (ctx, mock_claude, load_fixture)
        ├── fixtures/            # Test data
        ├── mode/                # --test mode files
        └── test_<module>.py

### E2E Tests (tests/e2e/test_e2e.py)

- One test per kc command use case: gen / gen --resume / regen --target / fix / fix --target
- Call run.py facade functions (kc_gen / kc_fix, etc.); do not hardcode phase strings
- CC is mocked so all output is deterministic; assert with exact equality
- Assert file counts and other quantities
- Assert CC call counts (cost-critical)
- Use TestContext to redirect all outputs under log_dir

### Unit Tests (tests/ut/)

- Test only complex logic that is hard to verify through E2E
- Write for: split criteria, merge edge cases, validation rules, link resolution, boundary values, error cases not reachable via E2E
- Skip: Context properties, simple delegation, E2E happy path coverage

### Pre-PR Requirement

Before requesting PR review for any kc change, all automated tests must pass:

```bash
cd tools/knowledge-creator
pytest
```

If any test fails, fix all failures — including pre-existing ones — before creating the PR. Do not leave known failures unresolved.
