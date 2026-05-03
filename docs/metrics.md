# Nabledge Dev Metrics

> Last updated: 2026-05-04 (auto-generated weekly — [view source](tools/metrics/collect.py))

## DORA Scorecard

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

> 🔵 Actual  ·  🟢 Elite · 🟡 High · 🟠 Medium (threshold lines; beyond 🟠 = Low)

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'xyChart': {'plotColorPalette': '#4C82C3,#00C853,#FFD600,#FF8C00'}}}}%%
xychart-beta
  title "Deployment Frequency (PRs merged to main per week)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16", "03/23", "03/30", "04/06", "04/13", "04/20", "04/27"]
  y-axis "PRs / week" 0 --> 35
  bar [0, 2, 25, 9, 20, 27, 0, 29, 12, 3, 6, 2, 3]
  line [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]
  line [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
  line [0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25]
```

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'xyChart': {'plotColorPalette': '#4C82C3,#00C853,#FFD600,#FF8C00'}}}}%%
xychart-beta
  title "Lead Time for Changes (avg hours: first commit to merge)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16", "03/23", "03/30", "04/06", "04/13", "04/20", "04/27"]
  y-axis "Hours" 0 --> 876
  bar [0, 2.7, 8.9, 14.8, 19.6, 11.3, 0, 13.1, 20.6, 66, 58.4, 0.1, 46.7]
  line [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
  line [168, 168, 168, 168, 168, 168, 168, 168, 168, 168, 168, 168, 168]
  line [730, 730, 730, 730, 730, 730, 730, 730, 730, 730, 730, 730, 730]
```

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'xyChart': {'plotColorPalette': '#4C82C3,#00C853,#FFD600,#FF8C00'}}}}%%
xychart-beta
  title "Change Failure Rate (bug labeled PRs / all merged PRs %)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16", "03/23", "03/30", "04/06", "04/13", "04/20", "04/27"]
  y-axis "% of PRs" 0 --> 36
  bar [0, 0, 16, 11.1, 25, 29.6, 0, 13.8, 25, 0, 16.7, 0, 0]
  line [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
  line [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
  line [15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15]
```

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'xyChart': {'plotColorPalette': '#4C82C3,#00C853,#FFD600,#FF8C00'}}}}%%
xychart-beta
  title "Mean Time to Recovery (avg hours: bug issue opened to closed)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16", "03/23", "03/30", "04/06", "04/13", "04/20", "04/27"]
  y-axis "Hours" 0 --> 434
  bar [0, 0, 2, 4.3, 6.8, 42, 0, 2.3, 67.9, 0, 361.1, 0, 0]
  line [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
  line [24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24]
  line [168, 168, 168, 168, 168, 168, 168, 168, 168, 168, 168, 168, 168]
```


## Activity

> Issues/PRs の開閉ペース・コントリビューター数を週次で追跡します。
> 開いた数と閉じた数のバランスが崩れていると、未解決の積み残しが増えているサインです。

```mermaid
xychart-beta
  title "Issues (bar=Opened  line=Closed)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16", "03/23", "03/30", "04/06", "04/13", "04/20", "04/27"]
  y-axis "Count" 0 --> 38
  bar [0, 6, 26, 3, 25, 31, 0, 19, 5, 2, 1, 4, 7]
  line [0, 3, 24, 5, 21, 29, 0, 15, 8, 2, 4, 0, 5]
```

```mermaid
xychart-beta
  title "Pull Requests (bar=Opened  line=Merged)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16", "03/23", "03/30", "04/06", "04/13", "04/20", "04/27"]
  y-axis "Count" 0 --> 45
  bar [0, 13, 37, 9, 27, 30, 0, 33, 19, 5, 5, 3, 4]
  line [0, 2, 25, 9, 20, 27, 0, 29, 12, 3, 6, 2, 3]
```

```mermaid
xychart-beta
  title "Active Contributors (unique PR authors per week)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16", "03/23", "03/30", "04/06", "04/13", "04/20", "04/27"]
  y-axis "Contributors" 0 --> 5
  bar [0, 1, 1, 1, 1, 1, 0, 2, 2, 1, 2, 2, 2]
```

## Code Size (SLOC)

> Scripts: statement lines (blank and comment lines excluded) / Prompts: non-blank lines

```mermaid
xychart-beta
  title "Total SLOC Trend (Total / RBKC / Nabledge v6)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16", "03/23", "03/30", "04/13", "05/04"]
  y-axis "Lines" 0 --> 15891
  line [0, 789, 1503, 1293, 10339, 11613, 11613, 11704, 12523, 12553, 13242]
  line [0, 0, 0, 0, 8533, 9682, 9682, 9773, 10592, 10592, 11264]
  line [0, 789, 1503, 1293, 1806, 1931, 1931, 1931, 1931, 1961, 1978]
```
> Lines (top to bottom): Total — RBKC (prod+test) — Nabledge v6

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'pie2': '#FF9800'}}}%%
pie title Nabledge v6 SLOC
  "Scripts (.sh)" : 1056
  "Prompts (.md)" : 922
```

```mermaid
pie title RBKC SLOC
  "Create (.py)" : 1296
  "Verify (.py)" : 1606
  "Common (.py)" : 2834
```

```mermaid
xychart-beta
  title "RBKC Production SLOC Trend (Create / Verify / Common)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16", "03/23", "03/30", "04/13", "05/04"]
  y-axis "Lines" 0 --> 3401
  line [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1296]
  line [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1606]
  line [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2834]
```
> Lines (top to bottom): Common — Verify — Create

## Nabledge Adoption (nablarch/nabledge)

> Traffic data collection started: week of 03/09

```mermaid
xychart-beta
  title "Page Views (weekly)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16", "03/23", "03/30", "04/06", "04/13", "04/20", "04/27"]
  y-axis "Views" 0 --> 515
  bar [0, 0, 0, 0, 0, 2, 278, 429, 319, 126, 184, 126, 216]
```

```mermaid
xychart-beta
  title "Unique Visitors (weekly)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16", "03/23", "03/30", "04/06", "04/13", "04/20", "04/27"]
  y-axis "Visitors" 0 --> 87
  bar [0, 0, 0, 0, 0, 1, 40, 63, 72, 45, 55, 42, 47]
```

```mermaid
xychart-beta
  title "Unique Cloners (weekly)"
  x-axis ["02/02", "02/09", "02/16", "02/23", "03/02", "03/09", "03/16", "03/23", "03/30", "04/06", "04/13", "04/20", "04/27"]
  y-axis "Cloners" 0 --> 130
  bar [0, 0, 0, 0, 0, 10, 87, 108, 90, 81, 87, 106, 72]
```
