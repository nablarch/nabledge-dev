# Nabledge Dev Metrics

> Last updated: 2026-03-13 (auto-generated weekly — [view source](tools/metrics/collect.py))

## DORA Scorecard

```mermaid
xychart-beta
  title "DORA Score (4=Elite  3=High  2=Medium  1=Low)"
  x-axis ["Deploy Freq", "Lead Time", "CFR", "MTTR"]
  y-axis "Score" 0 --> 4
  bar [4, 3, 4, 3]
```

| Metric | Latest | Level | Elite | High | Medium | Low |
|--------|-------:|:-----:|:-----:|:----:|:------:|:---:|
| Deployment Frequency | 20 PRs/week | **Elite** | ≥7/week | ≥1/week | ≥1/month | <1/month |
| Lead Time for Changes | 19.6h | High | <1h | <1 week | <1 month | ≥1 month |
| Change Failure Rate | 0% | **Elite** | ≤5% | ≤10% | ≤15% | >15% |
| MTTR | 8.9h | High | <1h | <1 day | <1 week | ≥1 week |

## Development Productivity

```mermaid
xychart-beta
  title "Deployment Frequency (PRs merged to main per week)"
  x-axis ["01/12", "01/19", "01/26", "02/02", "02/09", "02/16", "02/23", "03/02"]
  y-axis "PRs / week" 0 --> 30
  bar [0, 0, 0, 0, 2, 25, 9, 20]
```

```mermaid
xychart-beta
  title "Lead Time for Changes (avg hours: first commit to merge)"
  x-axis ["01/12", "01/19", "01/26", "02/02", "02/09", "02/16", "02/23", "03/02"]
  y-axis "Hours" 0 --> 24
  line [0, 0, 0, 0, 2.7, 8.9, 14.8, 19.6]
```

```mermaid
xychart-beta
  title "Change Failure Rate (bug or fix labeled PRs / all merged PRs %)"
  x-axis ["01/12", "01/19", "01/26", "02/02", "02/09", "02/16", "02/23", "03/02"]
  y-axis "% of PRs" 0 --> 5
  bar [0, 0, 0, 0, 0, 0, 0, 0]
```

> **Change Failure Rate**: bug/fix ラベル付き PR 数 ÷ mainへマージされた全 PR 数 × 100

```mermaid
xychart-beta
  title "Mean Time to Recovery (avg hours: bug issue opened to closed)"
  x-axis ["01/12", "01/19", "01/26", "02/02", "02/09", "02/16", "02/23", "03/02"]
  y-axis "Hours" 0 --> 11
  line [0, 0, 0, 0, 0, 2.5, 4.3, 8.9]
```

> **Mean Time to Recovery**: bug ラベル付き Issue の closed_at − created_at の平均（時間）

## Activity

> Issues/PRs の開閉ペース・コントリビューター数を週次で追跡します。
> 開いた数と閉じた数のバランスが崩れていると、未解決の積み残しが増えているサインです。

```mermaid
xychart-beta
  title "Issues Opened (count per week)"
  x-axis ["01/12", "01/19", "01/26", "02/02", "02/09", "02/16", "02/23", "03/02"]
  y-axis "Count" 0 --> 32
  bar [0, 0, 0, 0, 6, 26, 3, 25]
```

```mermaid
xychart-beta
  title "Issues Closed (count per week)"
  x-axis ["01/12", "01/19", "01/26", "02/02", "02/09", "02/16", "02/23", "03/02"]
  y-axis "Count" 0 --> 29
  bar [0, 0, 0, 0, 3, 24, 5, 21]
```

```mermaid
xychart-beta
  title "PRs Opened (count per week)"
  x-axis ["01/12", "01/19", "01/26", "02/02", "02/09", "02/16", "02/23", "03/02"]
  y-axis "Count" 0 --> 45
  bar [0, 0, 0, 0, 13, 37, 9, 27]
```

```mermaid
xychart-beta
  title "PRs Merged (count per week)"
  x-axis ["01/12", "01/19", "01/26", "02/02", "02/09", "02/16", "02/23", "03/02"]
  y-axis "Count" 0 --> 30
  bar [0, 0, 0, 0, 2, 25, 9, 20]
```

```mermaid
xychart-beta
  title "Active Contributors (unique PR authors per week)"
  x-axis ["01/12", "01/19", "01/26", "02/02", "02/09", "02/16", "02/23", "03/02"]
  y-axis "Contributors" 0 --> 2
  bar [0, 0, 0, 0, 1, 1, 1, 1]
```

## Code Size (SLOC)

> Scripts: statement lines (blank and comment lines excluded) / Prompts: non-blank lines

```mermaid
xychart-beta
  title "Total SLOC Trend (all categories)"
  x-axis ["02-02", "02-09", "02-16", "02-23", "03-02", "03-13"]
  y-axis "Lines" 0 --> 13936
  line [0, 789, 1503, 1293, 10339, 11613]
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
  x-axis ["02-02", "02-09", "02-16", "02-23", "03-02", "03-13"]
  y-axis "Lines" 0 --> 6077
  line [0, 0, 0, 0, 3183, 4109]
  line [0, 0, 0, 0, 4802, 5064]
```

## Nabledge Adoption (nablarch/nabledge)

_Skipped: NABLEDGE_SYNC_TOKEN not available._
