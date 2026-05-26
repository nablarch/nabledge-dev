# Nabledge Test Setup Report

| Item | Value |
| ---- | ----- |
| Branch | `develop` |
| Repository | `nablarch/nabledge` |
| Run datetime | 2026-05-26 15:00:00 |
| Version filter | all |

## Static Checks

| Environment | Result |
| ----------- | ------ |
| v6/test-cc | PASS |
| v6/test-ghc | PASS |
| v5/test-cc | PASS |
| v5/test-ghc | PASS |
| v1.4/test-cc | PASS |
| v1.4/test-ghc | PASS |
| v1.3/test-cc | PASS |
| v1.3/test-ghc | PASS |
| v1.2/test-cc | FAIL |
| v1.2/test-ghc | PASS |
| upgrade/test-cc | PASS |
| upgrade/test-ghc | PASS |

## Dynamic Checks

| Environment | Version | Tool | Result | Time (s) | Input tokens | Output tokens | Cost (USD) | Keywords |
| ----------- | ------- | ---- | ------ | -------- | ------------ | ------------- | ---------- | -------- |
| v6/test-cc | 6 | cc | PASS | 45 | 128450 | 3210 | 0.014230 | 2/2 |
| v6/test-ghc | 6 | ghc | PASS | 38 | N/A | N/A | N/A | 2/2 |
| v5/test-cc | 5 | cc | PASS | 52 | 135200 | 3890 | 0.015820 | 2/2 |
| v5/test-ghc | 5 | ghc | PASS | 41 | N/A | N/A | N/A | 2/2 |
| v1.4/test-cc | 1.4 | cc | PASS | 49 | 121300 | 2980 | 0.013050 | 2/2 |
| v1.4/test-ghc | 1.4 | ghc | PASS | 36 | N/A | N/A | N/A | 2/2 |
| v1.3/test-cc | 1.3 | cc | PASS | 48 | 119800 | 2840 | 0.012730 | 2/2 |
| v1.3/test-ghc | 1.3 | ghc | PASS | 37 | N/A | N/A | N/A | 2/2 |
| v1.2/test-cc | 1.2 | cc | FAIL | 60 | N/A | N/A | N/A | 0/2 |
| v1.2/test-ghc | 1.2 | ghc | PASS | 39 | N/A | N/A | N/A | 2/2 |
| upgrade/test-cc | 6 | cc | PASS | 44 | 127100 | 3100 | 0.013950 | 2/2 |
| upgrade/test-cc | 5 | cc | PASS | 50 | 132500 | 3650 | 0.015200 | 2/2 |
| upgrade/test-ghc | 1.4 | ghc | PASS | 35 | N/A | N/A | N/A | 2/2 |
| upgrade/test-ghc | 5 | ghc | PASS | 40 | N/A | N/A | N/A | 2/2 |

### Totals

| Metric | Value |
| ------ | ----- |
| Total time (s) | 614 |
| Total tokens | 784020 (in: 764350, out: 19670) |
| Total estimated cost | $0.084980 |
