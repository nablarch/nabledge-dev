# Mermaid Pie Chart Color Test

Verify that `%%{init}%%` color specification works for pie charts on GitHub.

## Without color specification (default)

```mermaid
pie title Nabledge v6 SLOC
  "Scripts (.sh)" : 951
  "Prompts (.md)" : 1010
```

```mermaid
pie title Knowledge Creator SLOC
  "Production (.py)" : 4347
  "Test (.py)" : 5736
  "Prompts (.md)" : 509
```

## With explicit color specification

`Prompts (.md)` should be the same orange (`#FF9800`) in both charts.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'pie1': '#4CAF50', 'pie2': '#FF9800'}}}%%
pie title Nabledge v6 SLOC
  "Scripts (.sh)" : 951
  "Prompts (.md)" : 1010
```

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'pie1': '#4CAF50', 'pie2': '#2196F3', 'pie3': '#FF9800'}}}%%
pie title Knowledge Creator SLOC
  "Production (.py)" : 4347
  "Test (.py)" : 5736
  "Prompts (.md)" : 509
```
