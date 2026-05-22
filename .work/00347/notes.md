# Notes: Fix security checklist Excel merged-row grouping (#347)

## 2026-05-22

### Baseline: verify FAIL counts before fix

All 5 versions passed with 0 FAILs (all "All files verified OK"):

| Version | FAIL count |
|---------|-----------|
| v6      | 0         |
| v5      | 0         |
| v1.4    | 0         |
| v1.3    | 0         |
| v1.2    | 0         |

Commands run from `tools/rbkc/`:
```
bash rbkc.sh verify 6
bash rbkc.sh verify 5
bash rbkc.sh verify 1.4
bash rbkc.sh verify 1.3
bash rbkc.sh verify 1.2
```
