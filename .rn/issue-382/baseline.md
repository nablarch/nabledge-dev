# Benchmark Baseline for Issue-382

## Run Label

`20260612-1404-baseline-current`

Source: `tools/benchmark/results/20260612-1404-baseline-current/`

This is the most recent completed benchmark run that precedes issue-382 work. It has both
`crossrun-summary.md` and `baseline.json`, making it the authoritative pre-change reference.

## Metrics (3 runs × 34 scenarios = 102 evaluations)

| Metric | Value |
|---|---|
| Scenario pass count (answer_correctness = 1.0) | 25 / 34 |
| P50 cost per query | $0.682 |
| P50 execution time | 118s |

### Scenario pass count derivation

Scenarios with answer_correctness mean < 1.0 (9 scenarios):

| Scenario | answer_correctness mean |
|---|---|
| qa-19 | 0.067 |
| qa-17 | 0.100 |
| qa-01 | 0.667 |
| qa-12 | 0.800 |
| qa-18 | 0.900 |
| oos-qa-01 | 0.933 |
| impact-01 | 0.967 |
| impact-06 | 0.967 |
| pre-03 | 0.933 |

Passing = 34 - 9 = **25 / 34**

### Full performance summary

| Metric | Mean | P50 | P95 | Max |
|---|---|---|---|---|
| Execution time | 141s | 118s | 266s | 347s |
| Cost per query | $0.733 | $0.682 | $1.132 | $1.438 |

Source: `tools/benchmark/results/20260612-1404-baseline-current/crossrun-summary.md`
