# Nabledge Dev Metrics

> Last updated: 2026-03-25 (auto-generated weekly — [view source](tools/metrics/collect.py))

## DORA Scorecard

| Metric | Latest | Level |
|--------|-------:|:-----:|
| Deployment Frequency | 27 PRs/week | **Elite** |
| Lead Time for Changes | 11.3h | High |
| Change Failure Rate | 30% | Low |
| MTTR | 42.0h | Medium |

<details><summary>Benchmark criteria</summary>

**Deployment Frequency**
- Elite: ≥7/week
- High: ≥1/week
- Medium: ≥1/month
- Low: <1/month

**Lead Time for Changes**
- Elite: <1h
- High: <1 week
- Medium: <1 month
- Low: ≥1 month

**Change Failure Rate**
- Elite: ≤5%
- High: ≤10%
- Medium: ≤15%
- Low: >15%

**MTTR**
- Elite: <1h
- High: <1 day
- Medium: <1 week
- Low: ≥1 week

</details>

> 🟢 Elite · 🟡 High · 🟠 Medium · 🔴 Low  (threshold lines)

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'xyChart': {'plotColorPalette': '#4C82C3,#00C853'}}}}%%
xychart-beta
  title "Deployment Frequency (PRs merged to main per week)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16"]
  y-axis "PRs / week" 0 --> 33
  bar [0, 2, 25, 9, 20, 27, 0]
  line [7, 7, 7, 7, 7, 7, 7]
```

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'xyChart': {'plotColorPalette': '#4C82C3,#00C853'}}}}%%
xychart-beta
  title "Lead Time for Changes (avg hours: first commit to merge)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16"]
  y-axis "Hours" 0 --> 24
  line [0, 2.7, 8.9, 14.8, 19.6, 11.3, 0]
  line [1, 1, 1, 1, 1, 1, 1]
```

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'xyChart': {'plotColorPalette': '#4C82C3,#00C853,#FFD600,#FF4444'}}}}%%
xychart-beta
  title "Change Failure Rate (bug labeled PRs / all merged PRs %)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16"]
  y-axis "% of PRs" 0 --> 36
  bar [0, 0, 16, 11.1, 25, 29.6, 0]
  line [5, 5, 5, 5, 5, 5, 5]
  line [10, 10, 10, 10, 10, 10, 10]
  line [15, 15, 15, 15, 15, 15, 15]
```

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'xyChart': {'plotColorPalette': '#4C82C3,#00C853,#FFD600'}}}}%%
xychart-beta
  title "Mean Time to Recovery (avg hours: bug issue opened to closed)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16"]
  y-axis "Hours" 0 --> 51
  line [0, 0, 2, 4.3, 6.8, 42, 0]
  line [1, 1, 1, 1, 1, 1, 1]
  line [24, 24, 24, 24, 24, 24, 24]
```


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
  y-axis "Contributors" 0 --> 5
  bar [0, 1, 1, 1, 1, 1, 0]
```

## Code Size (SLOC)

> Scripts: statement lines (blank and comment lines excluded) / Prompts: non-blank lines

```mermaid
xychart-beta
  title "Total SLOC Trend (all categories)"
  x-axis ["02-02", "02-09", "02-16", "02-23", "03-02", "03-13", "03-25"]
  y-axis "Lines" 0 --> 14045
  line [0, 789, 1503, 1293, 10339, 11613, 11704]
```

```mermaid
pie title Nabledge v6 SLOC
  "Scripts (.sh)" : 948
  "Prompts (.md)" : 983
```

```mermaid
pie title Knowledge Creator SLOC
  "Production (.py)" : 4119
  "Test (.py)" : 5145
  "Prompts (.md)" : 509
```

```mermaid
xychart-beta
  title "KC Scripts Trend (upper=Production  lower=Test)"
  x-axis ["02-02", "02-09", "02-16", "02-23", "03-02", "03-13", "03-25"]
  y-axis "Lines" 0 --> 6174
  line [0, 0, 0, 0, 3183, 4109, 4119]
  line [0, 0, 0, 0, 4802, 5064, 5145]
```

## Nabledge Adoption (nablarch/nabledge)

_Skipped: NABLEDGE_TOKEN not available._
