# task-3 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence |
|---|---|---|
| `generate_fts_hints_md` added to `index.py` | OK | Function defined at bottom of `tools/rbkc/scripts/create/index.py`; filters `component/{libraries,processing-pattern,development-tools,guide,setup}`; excludes `assets/`, `javadoc/`, `no_knowledge_content: true` |
| `run.py` imports and calls `generate_fts_hints_md` in 3 places | OK | Import updated to `from scripts.create.index import generate_index_md, generate_fts_hints_md`; 3 calls added in `create()`, `update()`, `delete()` — each outputs to `output_dir.parent / "scripts" / "fts-hints.md"` |
| `fts-hints.md` generated at correct path | OK | `.claude/skills/nabledge-6/scripts/fts-hints.md` exists after `rbkc create 6`; contains `### libraries-bean-validation` (file-stem format, fixed from initial Japanese-title version) |
| verify v6 passes with no regressions | OK | `python -m scripts.run verify 6` → `All files verified OK` (only pre-existing WARNs for javadoc_map miss) |
| `full-text-search.md` updated to use `cat scripts/fts-hints.md` | OK | Static "Component page title list" block removed; replaced with `cat scripts/fts-hints.md` bash command before the Process steps |
