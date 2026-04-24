# Baseline: 22-B-12 final (session 65)

**Date**: 2026-04-24
**Commit**: `3dd3d483f`
**Purpose**: 22-B-12 完了確認 — 全 5 バージョンで verify FAIL 0。

## Results

| Version | create | verify | Total FAIL | QL1 | QO2 | QC1 | QC2 | QC5 |
|---------|--------|--------|-----------:|----:|----:|----:|----:|----:|
| v6      | OK     | OK     |   0 |   0 |   0 |   0 |    0 |   0 |
| v5      | OK     | OK     |   0 |   0 |   0 |   0 |    0 |   0 |
| v1.4    | OK     | OK     |   0 |   0 |   0 |   0 |    0 |   0 |
| v1.3    | OK     | OK     |   0 |   0 |   0 |   0 |    0 |   0 |
| v1.2    | OK     | OK     |   0 |   0 |   0 |   0 |    0 |   0 |

## 22-B-12 内訳 (session 65)

| Finding | 件数 before → after | 修正内容 | commit |
|---------|---------------------|---------|--------|
| Finding A: v1.2 Excel preamble-as-parent | v1.2 8299 → 118 (Δ -8181) | `_looks_like_sub_header` に `len(parents) ≥ 2` guard (xlsx_common + verify) | `4b6d598f1` |
| Finding B: QO2 pipe-escape false-positive | v1.3 1 → 0 / v1.2 1 → 0 | QO2 P1 で JSON value にも `_md_table_cell` 変換を適用 (verify false-positive fix) | `9b3d5d032` |
| Finding C: "Unknown target name" QC1 FAIL | v1.3 1 → 0 / v1.2 1 → 0 | Sphinx 追従原則に従い WARNING 化 (rst_normaliser + rst_ast_visitor) | `2e45cea4d` |
| ws3: resolver AST walk | v1.3 118 → 0 / v1.2 116 → 0 | `collect_asset_refs` を rst_ast.parse → AST walk に書き換え。include を自動追従 | `3dd3d483f` |

合計: v1.2 8299→0 / v1.3 120→0. v6 / v5 / v1.4 は全修正で 0 維持 (横展開の regression なし)。

## Tests

- 372 → 377 tests GREEN (新規 5 件)
  - `TestVerifyP1SinglecellPreambleNotParent` × 2
  - `TestCheckJsonDocsMdConsistency_QO2_ExcelP1::test_pass_p1_value_with_pipe_char_md_escaped` × 2
  - `TestCheckContentCompleteness::test_pass_qc1_rst_unknown_target_name_not_promoted_to_fail`

## Raw logs

- `v{version}-create.log`
- `v{version}-verify.log`
