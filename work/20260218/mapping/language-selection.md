# Language Selection and File Type Filtering Report

**Date**: 2026-02-18T13:35:07+09:00

## Selection Rules

1. **Language Priority**: English (/en/) preferred, Japanese (/ja/) fallback if no English version
2. **File Type Filtering**:
   - .rst: All files included
   - .md: From nablarch-system-development-guide OR archetype README.md
   - .xml: Only pom.xml from archetypes (exclude build parent poms)
   - .config: Only from spotbugs/published-config directories
   - .txt: Only config.txt from jspanalysis/JspStaticAnalysis directories

## Nablarch v6

Before filtering: 942 files
After filtering: 605 files

By file type (after filtering):
  - .rst: 336
  - .md: 167
  - .xml: 9
  - .config: 90
  - .txt: 3

By language (after filtering):
  - /en/: 412
  - /ja/: 3
  - (no lang dir): 190

Selection details: See language-selection-v6.txt

## Nablarch v5

Before filtering: 889 files
After filtering: 544 files

By file type (after filtering):
  - .rst: 433
  - .md: 9
  - .xml: 9
  - .config: 90
  - .txt: 3

By language (after filtering):
  - /en/: 341
  - /ja/: 92
  - (no lang dir): 111

Selection details: See language-selection-v5.txt
