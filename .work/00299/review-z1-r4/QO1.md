# Expert Review: QA Engineer — QO1 (docs MD 構造整合性)

**Date**: 2026-04-23
**Reviewer**: AI Agent as QA Engineer (independent, bias-avoidance stance)
**Round**: Z-1 R-4
**Scope**: QO1 only — `check_json_docs_md_consistency` title/section-title/order logic per spec §3-3

## Overall Assessment

**Rating**: 5/5
**Summary**: R-4 resolves the three Medium-priority gaps flagged in R-3 (greedy order matcher, extra-H2 when JSON has sections, H2 regex looseness) and adds the R-3 Low-priority fenced-code-block protection. The implementation now matches spec §3-3 QO1 bullets exactly: title equality against the first `#`, section-title list equality (entries + order + no extras), and `##`/`###` restriction. Tests are genuinely bias-free (docs MD built as string literals, not via RBKC converters) and cover each spec-derived failure mode plus the adversarial cases from R-3.

Runtime verification:
- `./rbkc.sh verify 6` → `All files verified OK`
- `pytest tools/rbkc` → **211 passed**
- `pytest tests/ut/test_verify.py::TestCheckJsonDocsMdConsistency_QO1` → **15/15 passed**

## Three Condition Audit

### 1. Implementation (verify.py)

| Spec bullet (§3-3, lines 287–291) | Code evidence | Verdict |
|---|---|---|
| JSON `title` == docs MD first `#` | `verify.py:128–131` `_H1_RE.search(docs_scan)` → exact string equality against `json_title` | ✅ |
| Section titles match JSON list exactly (entries + order + no extras) | `verify.py:134–155` `docs_h2_titles != json_sec_titles` → separate branches for missing / extra / order-only | ✅ |
| `sections == []` means docs MD has no `##` | `verify.py:137–138` `if not sections and docs_h2_titles` → FAIL | ✅ |
| `##` / `###` are section headings | `verify.py:48` `_H2_RE = r'^#{2,3}\s+(.+)$'` — restricted to H2/H3 per spec (R-3 fix applied) | ✅ |
| Fenced code blocks must not be scanned for headings | `verify.py:51, 54–65, 123` `_strip_fenced_code` masks fence bodies before `_H1_RE` / `_H2_RE` run | ✅ |

Circularity check: no imports from `converters/`, `resolver/`, `run.py`, or `docs.py` except for the asset-link path rewrite helper that is QO2-scoped (lines 71–96). QO1 logic itself reads only `data` dict fields and docs MD text. verify therefore cannot be "satisfied by construction" — it is testing the output against a spec-derived rule, not against RBKC's own promises.

### 2. Tests (test_verify.py `TestCheckJsonDocsMdConsistency_QO1`, 15 cases)

| Spec failure mode | Test case(s) | Covered |
|---|---|---|
| Title mismatch | `test_fail_title_mismatch` | ✅ |
| Section title missing | `test_fail_section_title_missing` | ✅ |
| Section order reversed | `test_fail_section_order_reversed` | ✅ |
| Extra H2 when JSON has no sections | `test_fail_extra_h2_in_docs_md` | ✅ |
| Extra H2 when JSON has sections | `test_fail_extra_h2_when_sections_present` | ✅ (R-3 gap closed) |
| Duplicate H2 hiding order violation | `test_fail_duplicate_h2_order_violation` | ✅ (R-3 gap closed) |
| H1 missing entirely | `test_fail_h1_missing` | ✅ |
| Empty JSON title vs non-empty docs H1 | `test_fail_empty_title_vs_nonempty_docs_h1` | ✅ |
| Markdown special chars in title | `test_title_with_markdown_special_chars_exact_match` | ✅ |
| Multiple `#` in docs MD (first wins) | `test_multiple_h1_in_docs_md_first_wins` | ✅ |
| `no_knowledge_content` short-circuit | `test_pass_no_knowledge_content_skipped` | ✅ |
| `sections=[]` happy path (no H2) | `test_pass_no_sections_no_h2` | ✅ |
| Title + sections happy path | `test_pass_title_and_sections_match` | ✅ |
| Fenced code with `##` inside — must not be read as section | *not directly asserted as a QO1 unit test* | ⚠️ see Medium #1 |

Non-circularity: each test constructs `docs` as a literal string; none of them route through `docs.py` or a converter. This is the correct independence stance per `.claude/rules/rbkc.md`. Assertions are tight — most check both `"QO1"` prefix and a substring of the message, so a regression that fires the wrong check would be caught.

### 3. Runtime

- `./rbkc.sh verify 6` → `All files verified OK`
- `pytest` (211 tests) → all pass
- `pytest` QO1 class (15 tests) → all pass

## Key Issues

### High Priority

None.

### Medium Priority

1. **No direct unit test that `## inside fenced code block` does not trigger a false-positive extra-H2 FAIL**
   - Description: `_strip_fenced_code` is implemented (`verify.py:51–65`) and is obviously needed, but there is no QO1 unit test that exercises the adversarial case: JSON has `sections=[]`, docs MD contains a fenced block whose body contains `## something`. Without such a test, a future refactor that removes the fence-stripping call (line 123) would silently break QO1 without any test going RED. Real v6 output may or may not contain such patterns today — we cannot rely on v6 to cover this path.
   - Proposed fix: Add `test_pass_hash_inside_fenced_code_block_ignored` — `data = {title: "T", sections: []}`, docs `"# T\n\n\`\`\`md\n## Fake heading\n\`\`\`\n"`, assert `issues == []`. Pair with `test_pass_hash_inside_fenced_section_body_not_counted_as_section` for the sections-present variant.

### Low Priority

2. **`test_fail_top_level_content_below_first_h2_not_directly_under_h1` is a QO2 case placed under `TestCheckJsonDocsMdConsistency_QO1`**
   - Description: `test_verify.py:85–93` asserts `"QO2"` in the message but lives inside the `TestCheckJsonDocsMdConsistency_QO1` class. Minor organisational issue — makes the QO1 coverage count (15) slightly misleading.
   - Proposed fix: Move to `TestCheckJsonDocsMdConsistency_QO2`. Low-priority because it does not affect correctness, only report readability.

3. **`test_fail_readme_missing_page_declaration` is a QO3 case under QO1 class**
   - Description: `test_verify.py:118–128` asserts on `check_docs_coverage` output (QO3), but lives in `TestCheckJsonDocsMdConsistency_QO1`. Same organisational issue as #2.
   - Proposed fix: Move to `TestCheckDocsCoverage` / QO3 test class.

## Positive Aspects

- **Strict list-equality on section titles** (`docs_h2_titles != json_sec_titles`) — single comparison catches missing/extra/order in one branch; no off-by-one or greedy-pointer surface area remains.
- **Failure messages are differentiated** — missing / extra / order-differ each emit distinct strings, so tests can target the specific failure mode.
- **Fenced-code-block stripping preserves byte offsets** (`_strip_fenced_code` substitutes spaces/newlines, not removal) — so the `##` offset used for QO2 top-content range (lines 171–174) stays valid. Non-trivial detail, done right.
- **R-3 feedback fully addressed** — all three Medium-priority items from round 3 are closed with corresponding tests (`test_fail_extra_h2_when_sections_present`, `test_fail_duplicate_h2_order_violation`, and `_H2_RE` tightened to `#{2,3}`).
- **Independence preserved** — verify does not import from RBKC implementation modules for QO1 logic; tests build docs MD as literal strings.

## Recommendations

1. Add the fenced-code-block QO1 tests (Medium #1) — this is the only remaining spec-derived case without explicit unit coverage. Cheap (≈10 lines) and directly protects the `_strip_fenced_code` invocation from silent removal.
2. Reorganise QO2/QO3 tests out of the QO1 class (Low #2 and #3) — purely cosmetic but improves the "15 QO1 cases" count honesty.
3. Continue treating "v6 verify passes" as a smoke test only — adversarial cases (duplicate H2, extra H2, H3, fenced-block headings, multi-H1) must come from unit tests because v6 is a cooperating producer.

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (lines 42–155, 54–65 fence stripping)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (lines 11–150)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 lines 270–291

## Runtime Verification

- `./rbkc.sh verify 6` → **All files verified OK**
- `pytest tools/rbkc` → **211 passed**
- `pytest tests/ut/test_verify.py::TestCheckJsonDocsMdConsistency_QO1` → **15/15 passed**
