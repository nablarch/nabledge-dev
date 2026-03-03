# Knowledge Creator

Development rules for the knowledge-creator tool.

## Intermediate Artifacts

**Policy**: Include intermediate artifacts (logs) in git for investigation when issues are found in knowledge files.

### Before Generation

1. Delete existing intermediate artifacts
2. Commit and push deletions
3. Run knowledge-creator
4. Review diff to verify new artifacts

**Rationale**: Clean state enables clear diff review of generated artifacts.

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
# 1. Clean intermediate artifacts
rm -rf tools/knowledge-creator/.logs/v6/
git add -u tools/knowledge-creator/.logs/
git commit -m "chore: Clean intermediate artifacts before generation"
git push

# 2. Run generation
cd tools/knowledge-creator
./run.py --version 6 --test test-files-top3.json

# 3. Review and commit new artifacts
git status
git add tools/knowledge-creator/.logs/
git commit -m "chore: Add intermediate artifacts from generation"
```

## Execution Logs

Each Phase B/D/E/F execution saves metrics to `executions/` directory:
- `{file_id}_{timestamp}.json` - Full Claude CLI response including:
  - `num_turns` - Number of agentic turns
  - `duration_ms` - Execution time in milliseconds
  - `total_cost_usd` - API cost in USD
  - `structured_output` - Generated knowledge file content

**Purpose**: Performance analysis, cost tracking, and debugging.
