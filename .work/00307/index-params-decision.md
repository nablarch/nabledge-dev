# Index enrichment parameters — decision before measurement (#307)

**Date**: 2026-04-24
**Status**: FROZEN — do not retune against scenario results

## Decision

- **tf threshold**: 2 (drop tf=1 terms)
- **section top-N**: 5 (per-section cap after stoplist + title-overlap + tf filter)
- **page cap**: none

## Rule

These parameters are decided using **corpus statistics only**, before any
benchmark measurement. They are frozen. If the measurement in Step C fails,
we do NOT adjust these parameters to make the failure go away. Instead we
record Phase 1 limitation and move to Phase 2 (embedding).

Rationale for this rule: tuning parameters against the 10 scenarios is
"出来レース" (rigged game) — the index gets optimized for the exact cases it
will be evaluated against, giving a false positive signal. See
`.claude/rules/benchmark.md` and `.work/00307/notes.md`.

## Evidence (corpus-only, v6)

Source: `/tmp/section-df-ja-v6.json` (6653 JA 4+ char terms across 1411
sections) + per-section tokenization with stoplist + page/section-title
overlap filter.

### TF distribution across all candidate term occurrences

| tf | occurrences | cumulative |
|---:|---:|---:|
| 1 | 6730 (47.2%) | 47.2% |
| 2 | 5463 (38.3%) | 85.5% |
| 3 | 447 (3.1%) | 88.6% |
| 4 | 930 (6.5%) | 95.2% |
| ≥5 | 691 | 100% |

tf=1 is ~47% of all occurrences. Of those, 40.2% are also df=1 globally
(single mention in the corpus) — clearly one-off noise.

### Per-section candidate count by tf filter

| filter | median | p75 | p90 | p95 | max |
|---:|---:|---:|---:|---:|---:|
| no tf filter | 6 | 13 | 23 | 35 | 206 |
| **tf ≥ 2** | **3** | **7** | **13** | **18** | **128** |
| tf ≥ 3 | 0 | 2 | 4 | 6 | 41 |

tf≥3 drops the median to 0 — most sections would have no keywords. tf≥2
preserves keywords on the majority of sections while cutting noise.

### Total placements by (tf, N)

| | N=3 | N=5 | N=8 | N=10 | N=∞ |
|---:|---:|---:|---:|---:|---:|
| tf≥1 | 3364 | 5093 | 7098 | 8134 | 14261 |
| **tf≥2** | 2815 | **3961** | 5073 | 5573 | 7531 |
| tf≥3 | 1283 | 1574 | 1762 | 1838 | 2068 |

Current page-level TF-IDF index has 2898 placements. tf≥2 N=5 = 3961 (+37%)
is a modest, justifiable expansion; N=8+ is +75% with diminishing signal
(most sections don't have 8 good terms).

### Page skew (top-5% of pages' share of total placements)

At tf≥2 N=5: 14 top pages own 17.7% of placements.
Maximum seen: tf≥3 N=8 → 27.0%.

libraries-tag alone has 270 tf≥2 terms (extreme outlier), but per-section
top-N cap of 5 keeps it in check without a separate page cap.

## What this decision is NOT based on

- Benchmark scenario content (question text, a_facts, expected_sections)
- Failure case analysis
- Any "this parameter gets case X to pass" logic

## Measurement plan (Step B/C/D)

1. **Step B**: Implement classify_terms.py (section TF, stoplist+title filter, tf≥2, top-N=5) and build_index.py. Generate index-llm.md once.
2. **Step C**: Simulate 10-case sanity check — for each failing case's question, check whether the a_fact's expected section line now contains overlapping keywords. No LLM.
3. **Step D**: Record result. Do not adjust parameters.
