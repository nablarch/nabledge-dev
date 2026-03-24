# Nabledge Dev Metrics

> Last updated: 2026-03-24 (auto-generated weekly — [view source](tools/metrics/collect.py))

## DORA Scorecard

| Metric | Latest | Level |
|--------|-------:|:-----:|
| Deployment Frequency | 27 PRs/week | **Elite** |
| Lead Time for Changes | 11.3h | High |
| Change Failure Rate | 30% | Low |
| MTTR | 42.0h | Medium |

<details><summary>Benchmark criteria</summary>

- **Deployment Frequency** — Elite: ≥7/week · High: ≥1/week · Medium: ≥1/month · Low: <1/month
- **Lead Time for Changes** — Elite: <1h · High: <1 week · Medium: <1 month · Low: ≥1 month
- **Change Failure Rate** — Elite: ≤5% · High: ≤10% · Medium: ≤15% · Low: >15%
- **MTTR** — Elite: <1h · High: <1 day · Medium: <1 week · Low: ≥1 week

</details>

## Development Productivity

```mermaid
xychart-beta
  title "Deployment Frequency (PRs merged to main per week)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16"]
  y-axis "PRs / week" 0 --> 33
  bar [0, 2, 25, 9, 20, 27, 0]
```

```mermaid
xychart-beta
  title "Lead Time for Changes (avg hours: first commit to merge)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16"]
  y-axis "Hours" 0 --> 24
  line [0, 2.7, 8.9, 14.8, 19.6, 11.3, 0]
```

```mermaid
xychart-beta
  title "Change Failure Rate (bug or fix labeled PRs / all merged PRs %)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16"]
  y-axis "% of PRs" 0 --> 36
  bar [0, 0, 16, 11.1, 25, 29.6, 0]
```

> **Change Failure Rate**: bug/fix ラベル付き PR 数 ÷ mainへマージされた全 PR 数 × 100

```mermaid
xychart-beta
  title "Mean Time to Recovery (avg hours: bug issue opened to closed)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16"]
  y-axis "Hours" 0 --> 51
  line [0, 0, 2, 4.3, 6.8, 42, 0]
```

> **Mean Time to Recovery**: bug ラベル付き Issue の closed_at − created_at の平均（時間）

## Activity

> Issues/PRs の開閉ペース・コントリビューター数を週次で追跡します。
> 開いた数と閉じた数のバランスが崩れていると、未解決の積み残しが増えているサインです。

```mermaid
xychart-beta
  title "Issues (bar=Opened  line=Closed)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16"]
  y-axis "Count" 0 --> 38
  bar [0, 6, 26, 3, 25, 31, 0]
  line [0, 3, 24, 5, 21, 29, 0]
```

```mermaid
xychart-beta
  title "Pull Requests (bar=Opened  line=Merged)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16"]
  y-axis "Count" 0 --> 45
  bar [0, 13, 37, 9, 27, 30, 0]
  line [0, 2, 25, 9, 20, 27, 0]
```

```mermaid
xychart-beta
  title "Active Contributors (unique PR authors per week)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16"]
  y-axis "Contributors" 0 --> 2
  bar [0, 1, 1, 1, 1, 1, 0]
```

## Code Size (SLOC)

> Scripts: statement lines (blank and comment lines excluded) / Prompts: non-blank lines

```mermaid
xychart-beta
  title "Total SLOC Trend (all categories)"
  x-axis ["02-02", "02-09", "02-16", "02-23", "03-02", "03-13", "03-24"]
  y-axis "Lines" 0 --> 13936
  line [0, 789, 1503, 1293, 10339, 11613, 11613]
```

### Nabledge v6

```mermaid
pie title "Nabledge v6 SLOC (Scripts vs Prompts)"
  "Scripts (.sh)" : 948
  "Prompts (.md)" : 983
```

### Knowledge Creator

```mermaid
pie title "Knowledge Creator SLOC (Production / Test / Prompts)"
  "Production (.py)" : 4109
  "Test (.py)" : 5064
  "Prompts (.md)" : 509
```

```mermaid
xychart-beta
  title "KC Scripts Trend (upper=Production  lower=Test)"
  x-axis ["02-02", "02-09", "02-16", "02-23", "03-02", "03-13", "03-24"]
  y-axis "Lines" 0 --> 6077
  line [0, 0, 0, 0, 3183, 4109, 4109]
  line [0, 0, 0, 0, 4802, 5064, 5064]
```

## Nabledge Adoption (nablarch/nabledge)

_Skipped: NABLEDGE_SYNC_TOKEN not available._
