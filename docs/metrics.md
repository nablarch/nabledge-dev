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

## Nabledge Adoption (nablarch/nabledge)

_Skipped: NABLEDGE_SYNC_TOKEN not available._
