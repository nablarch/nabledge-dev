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
./run.py --version 6 --test test-files-largest3.json

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
