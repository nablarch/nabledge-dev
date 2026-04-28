# benchmark

Accuracy benchmark for nabledge-6 knowledge-search flows.

Given a set of curated questions with human-written reference answers, measure
how well a search flow answers them. An LLM judge scores each answer 0-3
against the reference.

## Layout

```
run.py                  CLI + orchestration
bench/                  library: claude.py, search_next.py, search_current.py, judge.py, io.py, types.py
build_index.py          regenerates knowledge/index-llm.md + index-script.json from knowledge/**/*.json
prompts/                search_next.md, search_current.md, answer.md, judge.md
scenarios/
  qa-v6.json            30 scenarios
  qa-v6-answers/*.md    per-scenario reference answer + citations
baseline/               latest committed run per variant
tests/                  unit tests (no CLI/claude calls)
```

## Flows

- `next` — AI-1 selects `file_id|sid` from `index-llm.md`, script resolves to `path:sid`, sections are fetched, AI-3 composes the answer from that content.
- `current` — single agent with Bash access to the production skill scripts (`full-text-search.sh` / `get-hints.sh` / `read-sections.sh`), reproduces the production behavior.

Both flows emit `{answer, cited}`; both are scored by the same judge.

## Usage

```bash
# Full run
python3 run.py --variant next
python3 run.py --variant current

# Subset
python3 run.py --variant next --scenario review-09
python3 run.py --variant next --limit 5

# Re-score an existing run with the current judge prompt
python3 run.py --rejudge --results-dir .results/20260423-120000-next-sonnet
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

## Evaluation workflow

### Step 1: Run

```bash
python3 run.py --variant next
python3 run.py --variant current
```

### Step 2: Human review (both variants)

The LLM judge has a known limitation: it penalizes claims that are architecturally
obvious but not literally stated in the KB (e.g. "implement auth in a handler" when
the KB only says "not provided by the framework"). These are false positives.

After each run, review each scenario where `judge level < 3` together with the
human reviewer. For each false positive, record an override in `human_review.json`.

**Create `.results/{ts}-next-sonnet/human_review.json`:**

```json
{
  "reviewed_at": "YYYY-MM-DD",
  "reviewers": ["kiyotis", "claude"],
  "overrides": [
    {
      "scenario_id": "review-03",
      "judge_level": 1,
      "human_level": 3,
      "reason": "Why this is a false positive"
    }
  ],
  "adjusted_mean": 2.93
}
```

`adjusted_mean` = mean level after applying overrides.

### Step 3: Compare with previous baseline

Check `docs/results-history.md` for the previous `next` baseline row.
Compare `adjusted_mean` (next) and `judge_mean` (current).

### Step 4: Promote to baseline

When a run represents a stable improvement:

```bash
cp -r .results/{ts}-next-sonnet/ baseline/next-sonnet/
```

Copy `human_review.json` alongside. Then update `docs/results-history.md`.

---

## Results history

See `docs/results-history.md` for the full comparison table.

## Operational rules

- Run one `run.py` invocation at a time. Parallel claude-CLI usage causes 240s timeouts. See `.claude/rules/benchmark.md`.
- Do not weaken the judge prompt to make a flow pass. Fix the flow; the judge is the quality gate.
- Both `next` and `current` require human review after LLM judging.
