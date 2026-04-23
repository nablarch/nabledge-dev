# QA Review — QO1 構造整合性 (spec §3-3)

**Reviewer**: Independent QA Engineer (bias-avoidance mode)
**Scope**: `scripts/verify/verify.py` QO1 logic + `tests/ut/test_verify.py::TestCheckJsonDocsMdConsistency_QO1`
**Date**: 2026-04-23

## Overall Assessment

**Rating**: 4/5

QO1 implementation and tests are tight, aligned with spec §3-3, and decoupled
from RBKC internals (no circular dependency). Full verify test suite:
**156 passed**. The spec-required gap cases (title mismatch, missing/extra/
out-of-order sections, missing H1, empty-title, MD special chars, multiple H1,
fenced code with `##` inside, duplicate-H2 order violation) are all covered.

One real gap remains: tilde-delimited (`~~~`) fenced code blocks are not
stripped, so `## ...` inside a `~~~` sample is misread as a section heading
(reproduced below).

## Implementation Review

### 1. H1 exact match — PASS
`_H1_RE = r'^#\s+(.+)$'` with `re.MULTILINE`. Requires space after `#` (so
`#X` does not match) and anchors to column 0 (indented `  # X` does not match).
Strip + `==` compare against `json_title`. Correct.

### 2. Section title list strict equality — PASS
Line 142: `if docs_h2_titles != json_sec_titles:` — full list equality, order
sensitive. Reports missing / extra / order-differs separately. Matches spec
§3-3 requirement of exact same entries in exact same order. The
"duplicate-H2 order violation" case `JSON=[B,A]` vs `docs=[A,B,A]` is
correctly caught as an extra `A` (test `test_fail_duplicate_h2_order_violation`
passes).

### 3. Fenced code stripped before scan — PARTIAL
`_FENCE_BLOCK_RE = r'^```.*?^```'` with `MULTILINE | DOTALL` correctly masks
triple-backtick (and 4+ backtick) fences while preserving byte positions
(spaces + newlines). `## fake` inside ``` ``` ``` is correctly ignored.

**Gap**: tilde fences `~~~ ... ~~~` are not stripped. CommonMark / GFM allow
`~~~` as an alternative fence delimiter. A `##` line inside a `~~~` block is
currently read as a section heading.

### 4. `_H2_RE` restricted to `##`/`###` — PASS
`r'^#{2,3}\s+(.+)$'`. `####` and deeper are not matched (verified empirically:
an `#### deep` line produces no QO1 issue, while `### extra` does produce
FAIL). Matches spec §3-3 "## or ###".

### 5. Circularity — PASS
`grep` on `scripts/verify/` for imports from `scripts.create` or
`scripts.run` returns empty. `verify.py` imports only `json`, `re`, `pathlib`,
and `scripts.common.labels.build_label_map`. verify is independent of RBKC
implementation, satisfying `.claude/rules/rbkc.md`.

## Test Review

All 15 QO1 tests pass. Coverage is strong across the spec's failure modes:

| Case | Test | Status |
|---|---|---|
| Title mismatch | `test_fail_title_mismatch` | Covered |
| Section missing | `test_fail_section_title_missing` | Covered |
| Section order reversed | `test_fail_section_order_reversed` | Covered |
| Extra H2 (sections empty) | `test_fail_extra_h2_in_docs_md` | Covered |
| Extra H2 (sections non-empty) | `test_fail_extra_h2_when_sections_present` | Covered |
| H1 missing | `test_fail_h1_missing` | Covered |
| Empty JSON title vs H1 | `test_fail_empty_title_vs_nonempty_docs_h1` | Covered |
| MD special chars | `test_title_with_markdown_special_chars_exact_match` | Covered |
| Multiple H1 | `test_multiple_h1_in_docs_md_first_wins` | Covered |
| Duplicate H2 order violation | `test_fail_duplicate_h2_order_violation` | Covered |
| Fenced code (`\`\`\``) with ## inside | (no explicit test; behavior verified empirically) | **Missing test** |

## Key Issues

### High Priority

**[High] Tilde-fenced code blocks not stripped**
- Description: `_FENCE_BLOCK_RE` only matches ``` ... ``` fences. CommonMark
  also recognises `~~~` as a fence delimiter. If source RST/MD (or future
  converter output) emits a `~~~md` block containing a `## ...` line, QO1
  will raise a false FAIL for an "extra section title".
  Reproduced: `docs="# T\n\n## A\n\nc\n\n~~~md\n## fake\n~~~\n"` →
  `[QO1] f: docs MD has extra section title not in JSON: 'fake'`.
- Proposed fix: extend `_FENCE_BLOCK_RE` to also match `~~~` fences, e.g.
  `r'^(?:```|~~~).*?^\1'` (with backreference) or two alternation patterns
  stripped in sequence. Add test
  `test_pass_tilde_fenced_code_with_hash_inside`.

### Medium Priority

**[Medium] No explicit test for backtick-fenced `##` being ignored**
- Description: The core invariant "`##` inside a fenced code block must not
  be treated as a section heading" is only verified indirectly (via QO2
  fenced-code content tests). Behavior works empirically, but a direct QO1
  test would pin the invariant against future regression of `_FENCE_BLOCK_RE`.
- Proposed fix: add
  `test_pass_fenced_code_with_hash_hash_inside` that asserts
  `check_json_docs_md_consistency(data_with_one_section_A, docs_with_one_H2_A_and_fenced_##fake) == []`.

### Low Priority

**[Low] Empty JSON title + no H1 returns no issue**
- Description: When `json_title == ""` and docs MD has no `#` heading,
  `docs_title == json_title == ""` so no QO1 FAIL is emitted. This is only
  reachable when `no_knowledge_content` is not set but title is empty — an
  arguably malformed JSON. Spec §3-3 implies a valid knowledge file always
  has a title; the `no_knowledge_content` gate already handles the legitimate
  empty case.
- Proposed fix (defer): add a schema-level check elsewhere that rejects
  `title == ""` when `no_knowledge_content` is falsy. Not a QO1 gap per the
  current spec wording.

## Positive Aspects

- verify is fully decoupled from RBKC implementation (no import from
  `scripts.create` / `scripts.run`). Satisfies the non-negotiable "verify is
  the quality gate" constraint.
- Fenced-code masking preserves byte positions so H1/H2 offsets remain valid
  for the QO2 top-region extraction — this is a non-obvious correctness point
  and the implementation gets it right.
- Section-title comparison uses strict list equality, not greedy containment,
  which correctly catches the `[A,B,A]` vs `[B,A]` ordering gap that a subset
  check would miss.
- Test names clearly describe the failure mode; the "Z-1 gap fill" comment
  block traces which cases were added to close the earlier review gap.

## Recommendations

1. Close the tilde-fence gap (High) before release. It is a latent false-FAIL
   risk whose blast radius is every docs MD containing a `~~~` code sample.
2. Add the explicit backtick-fenced-`##` QO1 test (Medium) as a regression
   pin for `_FENCE_BLOCK_RE`.
3. Consider documenting in `rbkc-verify-quality-design.md` which fence
   delimiters are recognised, so future contributors know where the contract
   boundary is.

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py`
  (lines 1–189, QO1 + shared helpers — source code)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py`
  (lines 1–150, `TestCheckJsonDocsMdConsistency_QO1` — tests)

## Verification

```
$ cd tools/rbkc && python -m pytest tests/ut/test_verify.py -q
156 passed in 0.73s
```

QO1 subset (15 tests): all green.
