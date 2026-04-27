# benchmark

Accuracy benchmark for nabledge-6 knowledge-search flows.

Given a set of curated questions with human-written reference answers, measure
how well a search flow answers them. An LLM judge scores each answer 0-3
against the reference.

## Layout

```
run.py                  CLI + orchestration
bench/                  library: claude.py, search_ids.py, search_current.py, judge.py, io.py, types.py
build_index.py          regenerates knowledge/index-llm.md + index-script.json from knowledge/**/*.json
prompts/                search_ids.md, search_current.md, answer.md, judge.md
scenarios/
  qa-v6.json            30 scenarios
  qa-v6-answers/*.md    per-scenario reference answer + citations
baseline/               latest committed run per variant
tests/                  unit tests (no CLI/claude calls)
```

## Flows

- `ids` — AI-1 selects `file_id|sid` from `index-llm.md`, script resolves to `path:sid`, sections are fetched, AI-3 composes the answer from that content.
- `current` — single agent with Bash access to the production skill scripts (`full-text-search.sh` / `get-hints.sh` / `read-sections.sh`), reproduces the production behavior.

Both flows emit `{answer, cited}`; both are scored by the same judge.

## Usage

```bash
# Full run
python3 run.py --variant ids
python3 run.py --variant current

# Subset
python3 run.py --variant ids --scenario review-09
python3 run.py --variant ids --limit 5

# Re-score an existing run with the current judge prompt
python3 run.py --rejudge --results-dir .results/20260423-120000-ids-sonnet
```

Default model is `sonnet`. Override with `--model haiku` etc.

## Output

Each run creates `.results/{ts}-{variant}-{model}/` with:

```
run.json                  {variant, model, started_at, scenarios[]}
summary.csv               one row per scenario
summary.json              mean level, distribution, total cost
{scenario_id}/
  search.json             SearchResult (answer + cited + per-variant steps)
  answer.md               answer text (human-readable)
  judge.json              JudgeVerdict (level + required_facts + over_reach + reasoning)
  stream/                 raw stream-json logs for each claude call
```

`.results/` is gitignored. Commit-worthy runs go under `baseline/`.

## Operational rules

- Run one `run.py` invocation at a time. Parallel claude-CLI usage causes 240s timeouts. See `.claude/rules/benchmark.md`.
- Do not weaken the judge prompt to make a flow pass. Fix the flow; the judge is the quality gate.
