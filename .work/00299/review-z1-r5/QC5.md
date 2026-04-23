# Expert Review: QA Engineer — QC5 形式純粋性 (R5)

**Date**: 2026-04-23
**Reviewer**: AI Agent as independent QA Engineer (bias-avoidance)
**Scope**: QC5 (format purity) — implementation + unit tests + verify runtime
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 "QC5 形式純粋性（独立チェック）"
**Files reviewed**:
- `tools/rbkc/scripts/verify/verify.py` (lines 314–375, QC5 block)
- `tools/rbkc/tests/ut/test_verify.py` (lines 488–659, `TestVerifyFileQC5`, 22 cases)
- R4 predecessor review: `.work/00299/review-z1-r4/QC5.md`

---

## Bias-avoidance posture

- The spec text (§3-1 QC5) is the single source of truth. Implementation was evaluated against the spec; tests were evaluated for circularity independently.
- I did not use R4's verdict as evidence — R4's findings were re-checked empirically.
- Regex behaviour was verified by running each regex against positive/negative inputs in a standalone Python session, not by reading the source alone.
- No code modified.

---

## Overall Assessment

**Rating**: 5/5

**Summary**: QC5 implementation matches every spec-listed pattern, with each regex anchored correctly (role requires backtick; directive is line-start-anchored; label is directive-shaped; title-only underline gate is enforced at the call site; MD raw HTML matches self-closing variants `<br/>`, `<hr/>`, `<img/>` and attribute-bearing tags; backslash escape list matches MD specials). All 22 unit tests pass; full verify unit test file is 156/156 green. Tests are not circular: each fixture contains a hand-authored remnant string and asserts a semantic keyword from the issue message, with no regex re-import or implementation-derived expected value. Two Low-priority items from R4 (3-char underline threshold; top-level-field coverage) remain open but are non-blocking.

---

## Evaluation against the three requested axes

### (1) Implementation regexes vs spec

Spec §3-1 QC5 pattern list (authoritative):
- RST: `:role:\`text\`` / `.. directive::` / `.. _label:`
- RST (title only): heading underline `====`, `----` etc. Content excluded (code blocks may legitimately contain `===`).
- MD: `<[a-zA-Z]`-prefixed raw HTML (incl. `<details>`, `<summary>`, `<br>`); backslash escapes `\*`, `\_`, etc.

Regex-by-regex empirical verdict (`verify.py:318–323`):

| Spec element | Regex | Anchor | Empirical result | Verdict |
|---|---|---|---|---|
| RST role | `:[a-zA-Z][a-zA-Z0-9_.-]*:\`` | backtick-required | `:ref:\`x\`` TRUE; `:name:` FALSE; `ref:\`x\`` FALSE | correct |
| RST directive | `^\.\.\s+[A-Za-z][\w:-]*::` (MULTILINE) | line-start | `.. note::` TRUE; `.. code-block:: python` TRUE; `表記 .. foo::` FALSE; `    .. note::` FALSE | correct (line-anchored as requested) |
| RST label | `\.\.\s+_[a-zA-Z0-9_-]+:` | — | `.. _my-label:` TRUE | correct |
| RST heading underline (title-only) | `^[=\-~^"'\`#*+<>]{4,}\s*$` (MULTILINE) | line-anchored, gated by `is_title=True` at call site | `====` TRUE; `=====` TRUE; `---` FALSE; `==` FALSE | correct for ≥4; narrow Low on ≥3 (L-1) |
| MD self-closing / attributed HTML | `<[a-zA-Z][a-zA-Z0-9]*(?:\s[^>]*)?/?>` | — | `<br>` `<br/>` `<br />` `<details>` `<a href="x">` `<img src=x alt=y/>` all TRUE; `<1abc>` FALSE; `a<b` FALSE | **correct — self-closing explicitly handled by `/?>`** |
| MD backslash escape | `\\[*_\`\[\](){}#+\-.!|]` | — | `\*` `\_` `\[` TRUE; `path\file` FALSE | correct |

**Title-only gate**: implemented at the API boundary (`_rst_syntax_issues(..., is_title=bool)`) and invoked with `is_title=True` for titles and `is_title=False` (default) for content (`verify.py:358, 364, 365`). This matches the spec's explicit rule "content excluded — code blocks may legitimately contain `===`".

No over-reach observed (field list `:name:` not flagged as role; Japanese `注意：` not flagged; indented directive not flagged; mid-text `x <b` not flagged as HTML).

### (2) Unit tests — coverage + circularity

**Positive (FAIL expected) cases — all spec patterns including self-closing**:

| Pattern | Test | Line |
|---|---|---|
| RST `:ref:\`x\`` | `test_fail_rst_role_in_content` | 512 |
| RST `.. note::` | `test_fail_rst_directive_in_content` | 519 |
| RST `.. _label:` | `test_fail_rst_label_in_content` | 526 |
| RST title `====` | `test_fail_rst_heading_underline_in_title` | 533 |
| MD `<details>` | `test_fail_md_raw_html_in_content` | 545 |
| MD `<summary>` | `test_fail_md_summary_tag` | 602 |
| MD `<br>` | `test_fail_md_br_tag` | 608 |
| MD `<a href=…>` (attributed) | `test_fail_md_a_tag` | 614 |
| **MD `<br/>` self-closing** | `test_fail_md_self_closing_br` | 643 |
| **MD `<hr/>` self-closing** | `test_fail_md_self_closing_hr` | 649 |
| **MD `<img/>` self-closing** | `test_fail_md_self_closing_img` | 655 |
| MD `\*` | `test_fail_md_backslash_escape_in_content` | 552 |
| MD `\_` | `test_fail_md_escaped_underscore` | 620 |
| MD `\[` | `test_fail_md_escaped_bracket` | 626 |
| MD raw HTML inside inline code (spec-pinning) | `test_fail_md_raw_html_inside_inline_code_still_detected` | 632 |

**Negative (no-FAIL expected) / false-positive probes**:

| Case | Test | Line |
|---|---|---|
| Clean RST content | `test_pass_rst_clean_content` | 538 |
| Clean MD content | `test_pass_md_clean_content` | 559 |
| xlsx short-circuit | `test_pass_xlsx_no_qc5` | 565 |
| `no_knowledge_content` short-circuit | `test_pass_no_knowledge_content_skipped` | 571 |
| **Underline `===` inside fenced code block (content, not title)** | `test_pass_rst_heading_underline_in_code_block_content` | 577 |
| **RST field list `:name:` (no backtick) not flagged as role** | `test_pass_rst_field_list_syntax_is_not_qc5_role` | 585 |
| **Japanese colon `：` not flagged as role** | `test_pass_rst_japanese_punctuation_not_confused_with_role` | 595 |

**Raw HTML in inline code** — explicitly pinned as FAIL by `test_fail_md_raw_html_inside_inline_code_still_detected` (L632) with a comment referencing §3-1. This is the correct bias-avoidance resolution of a spec ambiguity: pin the behaviour via test rather than allow the detector to make an implicit decision. This matches the Target's requested interpretation.

**Circularity analysis** — NOT circular:
- Each test constructs a fixture with a hand-authored remnant literal (e.g. `":ref:\`x\`"`, `"<br/>"`, `r"\*"`, `"===="`).
- Expected value is `"QC5"` + a semantic keyword (`"RST role"`, `"directive"`, `"label"`, `"underline"`, `"HTML"`, `"backslash"`) — both are stable behavioural contracts, not regex-derived.
- No test imports `_RST_ROLE_RE`, `_MD_RAW_HTML_RE`, etc. and re-applies them against its own fixture.
- Replacing the regex with an equivalent implementation (same boolean output + same keyword in the message) leaves every test green. Tests specify *behaviour*, not *implementation*.

### (3) verify + pytest runtime

- `pytest tests/ut/test_verify.py::TestVerifyFileQC5` → **22 passed, 0 failed, 0 skipped** in 0.14 s.
- `pytest tests/ut/test_verify.py` (whole file) → **156 passed** in 1.08 s.
- v6 verify FAIL count: per tasks.md (`Phase 21-Y Y-3b complete (v6 FAIL 0)`) the full-dataset run is FAIL 0. Per bias-avoidance, this is *corroborating* evidence only; primary evidence is the spec-vs-regex table above.

---

## Key Issues

### High Priority

_None._

### Medium Priority

_None._ Both R3/R4 Mediums remain resolved:
- Directive regex is line-anchored (`^\.\.\s+…`, MULTILINE) — confirmed empirically.
- Raw HTML inside inline code is explicitly pinned as FAIL by L632.

### Low Priority

**L-1. RST heading-underline threshold is `{4,}`, not `{3,}`** (unchanged from R4)
- Description: valid RST allows 3-char underlines for 1–2 char titles. `verify.py:320` uses `{4,}`. Title-only gate limits scope.
- Proposed fix: either lower to `{3,}` with a new failing test, or pin `{4,}` with a comment + negative test (`"==="` in a title → no FAIL) to make the decision explicit.
- Decision: keep as Low — non-blocking for Phase 21-Z.

**L-2. No test places a remnant at top-level `title` / top-level `content`** (unchanged from R4)
- Description: `_check_format_purity` checks top-level title, top-level content, and every section title/content (`verify.py:357–374`). Current tests place remnants only in `sections[*]`. A refactor that accidentally dropped the top-level branches would not fail any test.
- Proposed fix: add two tests — RST `title="===="` (top level), MD `content="<br>"` (top level).
- Decision: keep as Low — ~5 lines to close; strictly improves regression safety.

---

## Positive Aspects

- **Every pattern in the Target list has a dedicated failing test**, including all three self-closing variants (`<br/>`, `<hr/>`, `<img/>`) and the attributed form (`<a href="x">`).
- **False-positive probes are explicit**: field list `:name:`, Japanese colon `：`, fenced-code `===` in content body. Tests define what is *not* a residue, not only what is.
- **Spec ambiguity resolved via an explicit spec-pinning test** (inline-code HTML → FAIL, L632), with a doc-comment citing §3-1. This is the right engineering discipline.
- **Title-only gate is architectural, not string-matched**: `is_title: bool` parameter in `_rst_syntax_issues` (`verify.py:326`) invoked only for title fields.
- **Not circular**: tests anchor on `[QC5]` tag + semantic keyword; regex internals are a replaceable implementation detail.
- **xlsx and `no_knowledge_content` short-circuits are tested**, preventing accidental over-reach into non-applicable inputs.
- Full pytest: **156 passed** in 1.08 s.

---

## Recommendations

1. (Optional, Low) Add the two top-level-field regression-safety tests (L-2). Trivial, strictly additive.
2. (Optional, Low) Decide explicitly on the 3-char underline threshold (L-1) — either lower it or pin it.
3. **No blockers for marking QC5 ✅ in Phase 21-Z.** The four mechanical criteria are all met:
   - All spec patterns are regex-matched and anchored correctly (including self-closing HTML).
   - Every pattern has a failing test; false-positive probes exist.
   - Tests are not circular.
   - verify + pytest are green (156/156 unit; v6 full-dataset FAIL 0 per tasks.md).

---

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source, lines 314–375)
- `tools/rbkc/tests/ut/test_verify.py` (tests, `TestVerifyFileQC5`, 22 cases)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 (spec)
- `.work/00299/review-z1-r4/QC5.md` (predecessor review, for delta check)
