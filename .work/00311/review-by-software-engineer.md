# Expert Review: Software Engineer

**Date**: 2026-04-28
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 2 design docs (rbkc-converter-design.md §8, rbkc-verify-quality-design.md §3-3)

## Summary

2 Findings identified — both resolved in the design update.

## Findings (All Resolved)

### Finding 1: QO1 will FAIL for P2-1 docs MD headings

**Violated clause**: `rbkc-verify-quality-design.md §3-3 QO1` — "sections が空で top-level content のみの場合: docs MD に `##` 見出しが出現しない"

**Description**: P2-1 docs MD emits `##`/`###`/`####` headings from column-indent structure, but JSON has `sections: []`. Verify's QO1 check for non-P1 sheets fires on the `##` headings — a false positive.

**Fix Applied**: Added `sheet_subtype: "P2-1"` to JSON schema (§8-4). Added P2-1 QO1 exception in `rbkc-verify-quality-design.md §3-3` (same pattern as P1 exception). Updated `check_json_docs_md_consistency` condition to skip the assertion for P2-1.

---

### Finding 2: QO2 token-mismatch for P2-3 docs MD is unresolved

**Violated clause**: `rbkc-verify-quality-design.md §3-3 QO2` — "JSON top-level content が docs MD の `#` 見出し直下に完全一致で含まれている"; `.claude/rules/rbkc.md §verify is the quality gate`

**Description**: P2-3 JSON `content` is flat (e.g. `"1.SQLインジェクション 7.HTTP..."`), but docs MD contains `"1.SQLインジェクション  \n7.HTTP..."`. Verbatim substring check fails — false positive.

**Fix Applied**: Added P2-3 QO2 exception in `rbkc-verify-quality-design.md §3-3`: normalize `  \n` in docs MD text to single space before verbatim comparison. Added `sheet_subtype: "P2-3"` to JSON schema (§8-4). Change is classified as false positive fix per `.claude/rules/rbkc.md §Acceptable changes`.

## Observations

- P2-1 absolute-column heading mapping (col0=H2, col1=H3, col2=H4) is unambiguous for all 16 corpus sheets.
- JSON content staying flat for P2-1/P2-3 is correct — AI keyword search depends on flat text.
- Sheet-mapping override mechanism (explicit enumeration in xlsx-sheet-mapping.md) is the right strategy over heuristic detection.
- `nablarch5u15 標準プラグインの変更点`: LF in header cells (not data cells) — correctly treated as P2-2, not P2-3. Implicit but correct.
- `nablarch5u5 認可データ設定ツールのバージョンアップ方法`: P2-3 with ~25-line XML in one cell — `  \n` treatment produces multi-line paragraph (not code block). Acceptable within scope.

## Positive Aspects

- Exhaustive corpus investigation with empirical classification and explicit false-positive correction.
- Clean JSON/docs-MD split: flat for AI search, formatted for human reading.
- Sheet-mapping override eliminates heuristic ambiguity.
- P2-1 and P2-3 confirmed disjoint — no interaction complexity.

## Files Reviewed

- `tools/rbkc/docs/rbkc-converter-design.md` §8 (design spec)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 (verify spec)
