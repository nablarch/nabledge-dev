# Nabledge Dev Metrics

> Last updated: 2026-03-13 (auto-generated weekly — [view source](tools/metrics/collect.py))

## DORA Scorecard

| Metric | Latest | Level | Elite | High | Medium | Low |
|--------|-------:|:-----:|:-----:|:----:|:------:|:---:|
| Deployment Frequency | 20 PRs/week | **Elite** | ≥7/week | ≥1/week | ≥1/month | <1/month |
| Lead Time for Changes | 19.6h | High | <1h | <1 week | <1 month | ≥1 month |
| Change Failure Rate | 0% | **Elite** | ≤5% | ≤10% | ≤15% | >15% |
| MTTR | 8.9h | High | <1h | <1 day | <1 week | ≥1 week |

## Development Productivity

### Deployment Frequency (PRs merged to main / week)

```mermaid
xychart-beta
  title "Deployment Frequency"
  x-axis ["01/12", "01/19", "01/26", "02/02", "02/09", "02/16", "02/23", "03/02"]
  y-axis "PRs / week" 0 --> 30
  bar [0, 0, 0, 0, 2, 25, 9, 20]
```

### Lead Time for Changes (avg hours: first commit → merge)

```mermaid
xychart-beta
  title "Lead Time for Changes"
  x-axis ["01/12", "01/19", "01/26", "02/02", "02/09", "02/16", "02/23", "03/02"]
  y-axis "Hours" 0 --> 24
  line [0, 0, 0, 0, 2.7, 8.9, 14.8, 19.6]
```

### Change Failure Rate (%)

```mermaid
xychart-beta
  title "Change Failure Rate"
  x-axis ["01/12", "01/19", "01/26", "02/02", "02/09", "02/16", "02/23", "03/02"]
  y-axis "% of PRs" 0 --> 5
  bar [0, 0, 0, 0, 0, 0, 0, 0]
```

### Mean Time to Recovery (avg hours)

```mermaid
xychart-beta
  title "Mean Time to Recovery"
  x-axis ["01/12", "01/19", "01/26", "02/02", "02/09", "02/16", "02/23", "03/02"]
  y-axis "Hours" 0 --> 11
  line [0, 0, 0, 0, 0, 2.5, 4.3, 8.9]
```

## Activity

### Issues

```mermaid
xychart-beta
  title "Issues (bar: opened / line: closed)"
  x-axis ["01/12", "01/19", "01/26", "02/02", "02/09", "02/16", "02/23", "03/02"]
  y-axis "Count" 0 --> 32
  bar [0, 0, 0, 0, 6, 26, 3, 25]
  line [0, 0, 0, 0, 3, 24, 5, 21]
```

### Pull Requests

```mermaid
xychart-beta
  title "Pull Requests (bar: opened / line: merged)"
  x-axis ["01/12", "01/19", "01/26", "02/02", "02/09", "02/16", "02/23", "03/02"]
  y-axis "Count" 0 --> 45
  bar [0, 0, 0, 0, 13, 37, 9, 27]
  line [0, 0, 0, 0, 2, 25, 9, 20]
```

### Active Contributors

```mermaid
xychart-beta
  title "Active Contributors"
  x-axis ["01/12", "01/19", "01/26", "02/02", "02/09", "02/16", "02/23", "03/02"]
  y-axis "Contributors" 0 --> 2
  bar [0, 0, 0, 0, 1, 1, 1, 1]
```

| Week | Issues Opened | Issues Closed | PRs Opened | PRs Merged | Contributors |
|------|:---:|:---:|:---:|:---:|:---:|
| 01/12 | 0 | 0 | 0 | 0 | 0 |
| 01/19 | 0 | 0 | 0 | 0 | 0 |
| 01/26 | 0 | 0 | 0 | 0 | 0 |
| 02/02 | 0 | 0 | 0 | 0 | 0 |
| 02/09 | 6 | 3 | 13 | 2 | 1 |
| 02/16 | 26 | 24 | 37 | 25 | 1 |
| 02/23 | 3 | 5 | 9 | 9 | 1 |
| 03/02 | 25 | 21 | 27 | 20 | 1 |

## Code Size (SLOC)

> Scripts: statement lines (blank and comment lines excluded)  
> Prompts: non-blank lines

### Current Breakdown by Category

```mermaid
xychart-beta
  title "SLOC by Category"
  x-axis ["Nabledge scripts", "Nabledge prompts", "KC prod", "KC test", "KC prompts"]
  y-axis "Lines" 0 --> 6077
  bar [1452, 1966, 4705, 5064, 509]
```

### Summary

| Category | Lines | Change |
|----------|------:|-------:|
| Nabledge scripts | 1,452 | — |
| Nabledge prompts | 1,966 | — |
| KC scripts (prod) | 4,705 | — |
| KC scripts (test) | 5,064 | — |
| KC prompts | 509 | — |
| **Total** | **13,696** | **—** |

### Nabledge Scripts by Extension

| Extension | Lines | Change |
|-----------|------:|-------:|
| `.sh` | 1,452 | — |

### KC Scripts by Extension

| Extension | Prod | Prod Change | Test | Test Change |
|-----------|-----:|:-----------:|-----:|:-----------:|
| `.py` | 4,705 | — | 5,064 | — |

## Nabledge Adoption (nablarch/nabledge)

_Skipped: NABLEDGE_SYNC_TOKEN not available._
