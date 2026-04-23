# Expert Review: QA Engineer — QO1 構造整合性 (Z1-R6)

**Date**: 2026-04-23
**Reviewer**: Independent QA Engineer (bias-avoidance, no prior R5 context reuse)
**Scope**: Verify that QO1 implementation and tests satisfy spec §3-3:
1. Title exact match (JSON top-level `title` == docs MD `#` H1)
2. Section title list strict equality (same entries, same order, no extras, no omissions)
3. Fence stripping before H1/H2 scan for BOTH ` ``` ` AND ` ~~~ ` (r5 gap fix)
4. `_H2_RE` restricted to `##` / `###` (spec wording: 「`##`/`###` に存在」)
5. Circular test check
6. v6 actual data + pytest

## Overall Assessment

**Rating**: 5/5
**Summary**: Implementation and tests correctly enforce §3-3 for all three structural checks, including the previously-missing tilde-fence case. Tests are non-circular (hand-authored MD literals, verify.py imported alone). All 17 QO1 unit tests pass; v6 full verify reports `All files verified OK`.

## Evidence

### 1. Title exact match — PASS

- Regex: `scripts/verify/verify.py:46` — `_H1_RE = re.compile(r'^#\s+(.+)$', re.MULTILINE)` matches exactly one leading `#` followed by whitespace. Correctly rejects `##` because `\s` consumes the mandatory space.
- Equality check: `scripts/verify/verify.py:131` — `if docs_title != json_title` — strict string equality, no normalisation, no tolerance.
- Empty-title-vs-nonempty-H1: `scripts/verify/verify.py:130` returns empty string when no H1 found; equality still applied. Covered by `test_fail_empty_title_vs_nonempty_docs_h1` (`tests/ut/test_verify.py:130-138`) and `test_fail_h1_missing` (`tests/ut/test_verify.py:79-83`).
- First-H1-wins semantics confirmed by `test_multiple_h1_in_docs_md_first_wins` (`tests/ut/test_verify.py:145-150`).
- Special chars verbatim: `test_title_with_markdown_special_chars_exact_match` (`tests/ut/test_verify.py:140-143`).

### 2. Section list strict equality — PASS

- Regex: `scripts/verify/verify.py:48` — `_H2_RE = re.compile(r'^#{2,3}\s+(.+)$', re.MULTILINE)`. Bounded quantifier `{2,3}` **correctly restricts to `##` and `###` only**, matching spec §3-3 line 293 「`##`/`###` に存在」. `####` and deeper are excluded.
- Order/presence/extras logic: `scripts/verify/verify.py:143-156` — FAIL emitted for missing, extra, or reordered entries. Plain list equality `docs_h2_titles != json_sec_titles` enforces order.
- Tests:
  - Happy path: `test_pass_title_and_sections_match` (`:22-30`)
  - Missing: `test_fail_section_title_missing` (`:38-46`)
  - Extra (no-sections case): `test_fail_extra_h2_in_docs_md` (`:70-75`)
  - Extra (sections-present case): `test_fail_extra_h2_when_sections_present` (`:95-103`)
  - Order swap: `test_fail_section_order_reversed` (`:48-58`)
  - Duplicate-with-order-violation: `test_fail_duplicate_h2_order_violation` (`:105-116`)
  - sections=[] + no H2 (happy): `test_pass_no_sections_no_h2` (`:64-68`)

### 3. Fence stripping for BOTH ``` and ~~~ — PASS (R5 gap closed)

- Regex: `scripts/verify/verify.py:52` — `_FENCE_BLOCK_RE = re.compile(r'^(```|~~~).*?^\1', re.MULTILINE | re.DOTALL)`. The backreference `\1` requires the closing fence to match the opening fence type exactly — a ``` cannot close a ~~~ block and vice versa. Correct per CommonMark §4.5.
- Masking (`:63-66`) replaces fence bodies with spaces while preserving newlines, keeping byte offsets stable — required for the QO2 top-content window (`:171-176`) to remain correct after masking.
- Tests:
  - Tilde fence: `test_pass_tilde_fenced_code_block_with_heading_inside` (`tests/ut/test_verify.py:152-169`) — contains `## fake heading inside tilde fence` inside `~~~md ... ~~~`; QO1 must not report an extra section. Passes.
  - Backtick fence (regression guard): `test_pass_backtick_fenced_code_block_with_heading_inside` (`:171-184`).

### 4. Non-circularity — PASS

- `tests/ut/test_verify.py` imports only `scripts.verify.verify` (see lines 19, 121, 195, 245, 265, 317, 436, 530, 539, 601, 704). It does **not** import `scripts.create.docs` or any create-side module. All docs-MD inputs are hand-authored inline literals (string constants in each test), never the output of `docs.py`. Therefore QO1 tests do not assert "docs.py output round-trips through verify"; they assert the spec contract directly.
- verify.py itself does not import create-side modules for QO1 logic (see module imports at `scripts/verify/verify.py:18-22`, with only lazy docutils/md_ast imports for QL2 — unrelated). verify remains independent per `.claude/rules/rbkc.md`.

### 5. v6 + pytest — PASS

- `cd tools/rbkc && python -m pytest tests/ut/test_verify.py::TestCheckJsonDocsMdConsistency_QO1 -v` → **17 passed** in 0.03s (all 17 cases including both fence variants).
- `bash rbkc.sh verify 6` → **All files verified OK** (no QO1 findings across the full v6 corpus).

## Key Issues

### High Priority
None.

### Medium Priority
None.

### Low Priority

1. **Info-level observation — not a defect**
   - Description: `_FENCE_BLOCK_RE` lacks a leading-whitespace allowance. CommonMark permits up to 3 leading spaces before a fence (`    ```` is a 4-space indented code block, but `   ```` with 3 spaces is still a fence). Current regex anchors with `^` and requires the fence at column 0.
   - Proposed fix: If this ever appears in real docs MD output, widen to `r'^ {0,3}(```|~~~).*?^ {0,3}\1'`. Not required today because `docs.py` always emits fences at column 0; v6 FAIL 0 confirms no practical impact.
   - Decision: Defer — the risk is zero against the actual writer and v6 data.

2. **Info-level observation — not a defect**
   - Description: Fences with trailing info string after the opener close tag (e.g., ```` ```md ```` ) are handled by `.*?` consuming the rest of the line. Backreference `\1` matches only the three-character opener `'```'` or `'~~~'`, not the info string, so closing ` ``` ` matches correctly. Verified by `test_pass_backtick_fenced_code_block_with_heading_inside` using ` ```md ` opener and ` ``` ` closer.

## Positive Aspects

- Regex boundaries are deliberately tight (`#{2,3}` not `#+`) and explicitly match the spec wording; a single-line comment at `verify.py:47` documents the spec tie-in.
- Tests cover every branch of the structural logic (missing, extra in both sections-present and sections-empty states, reordered, duplicated-with-order-violation, no-H1, empty-title, multi-H1, special chars, tilde fence, backtick fence, sections=[] + H2 absent).
- Non-circular by construction: tests use string literals and assert against spec, not against writer output.
- Byte-preserving fence mask keeps QO2 top-content slicing correct even when fences precede the first `##`.

## Recommendations

- Keep the spec-citation comments (`verify.py:47`, `:50-52`) — they make future maintenance easier when auditing strictness claims.
- If docs.py ever emits indented fences, add a test first (TDD per `.claude/rules/rbkc.md`) before widening `_FENCE_BLOCK_RE`.

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source)
- `tools/rbkc/tests/ut/test_verify.py` (tests)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` (spec §3-3)

## Conclusion

QO1 passes independent QA review. §3-3's title / section-list / order / fence-stripping requirements are each bound to a specific line in verify.py and at least one dedicated test; both tilde and backtick fence cases are now explicitly guarded, closing the R5 gap. v6 FAIL 0 and 17/17 unit tests green confirm the checks function correctly on real data.
