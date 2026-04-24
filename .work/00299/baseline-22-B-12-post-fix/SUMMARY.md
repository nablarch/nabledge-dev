# Baseline: 22-B-12 post-fix (session 64)

**Date**: 2026-04-24
**Commit**: `8a606cf57` (working tree clean)
**Purpose**: 5-version FAIL count baseline after 22-B-12 two fixes (section-title `_flatten_ws`, include `source_path`).

## Results

| Version | create | verify | Total FAIL | QL1 | QO2 | QC1 | QC2 | QC5 |
|---------|--------|--------|-----------:|----:|----:|----:|----:|----:|
| v6      | OK     | OK     |   0 |   0 |   0 |   0 |    0 |   0 |
| v5      | OK     | OK     |   0 |   0 |   0 |   0 |    0 |   0 |
| v1.4    | OK     | OK     |   0 |   0 |   0 |   0 |    0 |   0 |
| v1.3    | OK     | FAIL   | 120 | 118 |   1 |   1 |    0 |   0 |
| v1.2    | OK     | FAIL   | 8299| 116 |   1 | 668 | 4342 |   0 |

## v1.3 (120 FAIL)

- **QL1 × 118** — asset missing. 58 RST referencing `.. include:: ../api/link.rst` → image inside include not copied by resolver.
- **QO2 × 1** — `nablarch-ライブラリ-1.3.0-releasenote-detail.xls` URL reserved chars value not found in docs MD (MD table escape).
- **QC1 × 1** — `07_BasicRules.rst` Unknown target name "nablarch" (target collision via include).

## v1.2 (8299 FAIL) — NEW, larger than v1.3

- **QL1 × 116** — asset missing (same include-not-followed pattern as v1.3).
- **QO2 × 1** — `nablarch-ライブラリ-1.2.1-releasenote-detail.xls` section '10.0' URL reserved chars value not found.
- **QC1 × 668** — mostly Excel cell values missing from JSON (converter gap) + 1 RST Unknown target.
- **QC2 × 4342** — all in 9 Excel releasenote files (1.2.0 / 1.2.1 / 1.2.2). JSON tokens not found in Excel source — massive Excel converter regression for v1.2.
- **Distinct failing files**: 68 (9 xls + 59 rst).

## Interpretation

- v6 / v5 / v1.4 clean — ws1 confirms the 22-B-12 fixes did not regress these.
- v1.3 matches the task description (118 QL1 + 1 QO2 + 1 QC1). resolver AST walk (ws3) should clear the 118.
- v1.2 is substantially worse than tasks.md claimed ("未実行" but assumed similar shape). The 4342 QC2 and 668 QC1 in Excel releasenotes indicate a v1.2-specific Excel converter gap independent of resolver/MD-escape. Needs fresh investigation.

## Raw logs

- `v{version}-create.log`
- `v{version}-verify.log`
