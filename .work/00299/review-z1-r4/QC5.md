# Expert Review: QA Engineer — QC5 形式純粋性 (R4)

**Date**: 2026-04-23
**Reviewer**: AI Agent as independent QA Engineer (bias-avoidance)
**Scope**: QC5 (format purity) — implementation + unit tests + verify runtime
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 "QC5 形式純粋性（独立チェック）"
**Files reviewed**:
- `tools/rbkc/scripts/verify/verify.py` (lines 314–375, QC5 block)
- `tools/rbkc/tests/ut/test_verify.py` (lines 488–659, `TestVerifyFileQC5`)
- R3 predecessor review: `.work/00299/review-z1-r3/QC5.md`

---

## Bias-avoidance posture

- The spec (§3-1 "QC5 形式純粋性") is the single source of truth. Implementation and tests were evaluated against the spec text, not against each other.
- v6 verify PASS is **weak evidence** — absence of FAILs can mean either "output is clean" or "detector missed them". The regex-vs-spec coverage analysis below is the primary evidence.
- No code was modified. Regex behaviour was verified empirically with a standalone script (not by reading the source alone).
- R3's unresolved findings were independently re-checked against the current code rather than assumed to still hold.

---

## Overall Assessment

**Rating**: 5/5

**Summary**: Every spec-listed pattern has a failing test; every failing test uses the same verify entry point callers use; and the two Medium findings raised in R3 have both been resolved — M-2 (directive regex too loose) was tightened to a line-anchored form with character-class `[A-Za-z][\w:-]*`, and the R3 concern about raw HTML inside backticks was explicitly pinned by `test_fail_md_raw_html_inside_inline_code_still_detected` (L632), i.e. the spec interpretation is now **"raw HTML in inline code FAILs"**, which matches the Target condition for this review. Self-closing tags (`<br/>`, `<hr/>`, `<img/>`) are each covered by an explicit FAIL test. Tests are not circular. 22/22 pass. One narrow residual gap (RST `---` 3-dash underline) is noted below as Low.

---

## Evaluation against the three requested axes

### (1) Implementation patterns vs spec

Spec §3-1 QC5 pattern list (authoritative):
- RST: `:role:\`text\`` / `.. directive::` / `.. _label:`
- RST (title only): heading underline `====`, `----` etc. Content excluded (code blocks may legitimately contain `===`).
- MD: `<[a-zA-Z]`-prefixed raw HTML tags (incl. `<details>`, `<summary>`, `<br>`); backslash escapes `\*`, `\_`, etc.

Regex-by-regex verdict (`verify.py:318–323`):

| Spec element | Regex | Anchored? | Empirical result | Overreach? | Underreach? |
|---|---|---|---|---|---|
| RST role | `:[a-zA-Z][a-zA-Z0-9_.-]*:\`` | backtick-required | `:ref:\`x\`` ✅, `:name:` ✖ (field list), `注意：` ✖ | No | No |
| RST directive | `^\.\.\s+[A-Za-z][\w:-]*::` (MULTILINE) | line-start | `.. note::` ✅, `.. code-block:: python` ✅, `表記 .. foo::` ✖, `    .. note::` ✖ (indented) | No | Narrow: indented directive lines; not observed in RBKC output |
| RST label | `\.\.\s+_[a-zA-Z0-9_-]+:` | not anchored | `.. _my-label:` ✅ | Mid-line `text .. _x: end` matches — acceptable; that IS a label remnant | No |
| RST heading underline (title-only) | `^[=\-~^"'\`#*+<>]{4,}\s*$` (MULTILINE) | line-anchored | `====` ✅, `---` (3 char) ✖ | No | **Narrow: 3-character underlines (`---`, `===`) are valid RST for 1–2 char titles and are missed.** See L-1. |
| MD raw HTML (incl. self-closing) | `<[a-zA-Z][a-zA-Z0-9]*(?:\s[^>]*)?/?>` | not anchored | `<br>`, `<br/>`, `<br />`, `<img src="x"/>`, `<details>`, `<a href="x">` all ✅; `a<b`, `<1abc>`, `< br>` all ✖ | No | No |
| MD backslash escape | `\\[*_\`\[\](){}#+\-.!|]` | not anchored | `\*`, `\_`, `\[` ✅; `path\file` ✖ | No | No |

**Overreach**: none material. **Underreach**: only the 3-character heading underline case, which is a narrow RST form.

**Spec-behaviour pinning**: §3-1 does not say "except inside code". R3 flagged this as Medium (M-1). The current test suite resolves the ambiguity by pinning the spec as "raw HTML in inline code FAILs" — `test_fail_md_raw_html_inside_inline_code_still_detected` (L632). This matches the Target's explicit condition for this review. The RST side already distinguishes title vs content for the underline check (title-only), which is correct and independent from the MD decision.

### (2) Unit tests

**RST** coverage (`test_verify.py:511–542`):

| Spec element | Test | Line |
|---|---|---|
| `:ref:\`x\`` (role) | `test_fail_rst_role_in_content` | 512 |
| `.. note::` (directive) | `test_fail_rst_directive_in_content` | 519 |
| `.. _my-label:` (label) | `test_fail_rst_label_in_content` | 526 |
| Title `====` (heading underline) | `test_fail_rst_heading_underline_in_title` | 533 |
| Clean content → no FAIL | `test_pass_rst_clean_content` | 538 |

**RST false-positive probes** (`test_verify.py:577–600`):
- Underline inside fenced code block (content) → no FAIL (L577) — guards title-only restriction
- Field list `:name:` (no backtick) → not a role (L585)
- Japanese colon `：` → not a role (L595)

**MD** coverage (`test_verify.py:545–659`):

| Spec element | Test | Line |
|---|---|---|
| `<details>` | `test_fail_md_raw_html_in_content` | 545 |
| `<summary>` | `test_fail_md_summary_tag` | 602 |
| `<br>` | `test_fail_md_br_tag` | 608 |
| `<a href=…>` (with attrs) | `test_fail_md_a_tag` | 614 |
| `<br/>` self-closing | `test_fail_md_self_closing_br` | 643 |
| `<hr/>` self-closing | `test_fail_md_self_closing_hr` | 649 |
| `<img/>` self-closing | `test_fail_md_self_closing_img` | 655 |
| `\*` | `test_fail_md_backslash_escape_in_content` | 552 |
| `\_` | `test_fail_md_escaped_underscore` | 620 |
| `\[` | `test_fail_md_escaped_bracket` | 626 |
| Clean content → no FAIL | `test_pass_md_clean_content` | 559 |
| Raw HTML inside inline code → **FAIL** (spec-pinning) | `test_fail_md_raw_html_inside_inline_code_still_detected` | 632 |

**Cross-format**:
- `test_pass_xlsx_no_qc5` (L565): QC5 skipped for xlsx — matches spec "— for Excel".
- `test_pass_no_knowledge_content_skipped` (L571): `no_knowledge_content: true` skipped — matches guard at `verify.py:349`.

**Circular-test analysis**: NO circularity. Each test constructs a JSON payload with a hand-authored remnant string (`":ref:\`x\`"`, `"<br/>"`, `r"\*"`, `"===="`, …) and asserts the produced issue string contains `"QC5"` and a semantic keyword (`"HTML"`, `"backslash"`, `"role"`, `"directive"`, `"label"`, `"underline"`). No test imports a private regex and re-applies it against the same fixture; no test's expected value is produced by running the detector. Replace the regex with any equivalent (same boolean verdict, same human keyword) and every test still passes — the tests specify behaviour, not implementation.

**Pytest run**:
```
tests/ut/test_verify.py::TestVerifyFileQC5  22 passed in 0.17s
```

### (3) verify + pytest runtime

- `pytest tests/ut/test_verify.py::TestVerifyFileQC5 -v` → 22 passed, 0 failed, 0 skipped.
- Full file verify runtime (`./rbkc.sh verify 6`) is reported as FAIL 0 in the current branch per tasks.md. Per the bias-avoidance posture, this is corroborating, not primary, evidence.

---

## Key Issues

### High Priority

_None._

### Medium Priority

_None._ Both R3 Mediums are now resolved:

- **R3 M-1** (MD inline-code false positive): resolved by an explicit spec-pinning test (`test_fail_md_raw_html_inside_inline_code_still_detected`, L632) that states, with a doc-comment referencing §3-1, that raw HTML in backticks FAILs. This is the correct bias-avoidance answer to an ambiguous spec: pin the behaviour, don't silently allow or silently deny.
- **R3 M-2** (directive regex too loose): resolved at `verify.py:319` — regex is now `^\.\.\s+[A-Za-z][\w:-]*::` with MULTILINE. Empirically verified: `表記 .. foo::` no longer matches.

### Low Priority

**L-1. RST 3-character heading underline not detected (narrow gap)**
- Description: `_RST_HEADING_UNDERLINE_RE` at `verify.py:320` requires `{4,}`. Valid RST underlines can be 3 characters (for a 1–2 character title, as long as underline ≥ title length). A title field containing a stray 3-character residue like `"==="` would not be caught.
- Proposed fix: change `{4,}` to `{3,}`, OR add a test confirming the 4+ threshold is intentional. Given this is title-only and titles are short by nature, the 4+ threshold may be deliberate to avoid false positives on typographic `---` em-dash runs. Document the decision with a comment + test.
- Decision: keep as Low; does not block Phase 21-Z.

**L-2. No test exercises QC5 on top-level `title` / top-level `content` fields**
- Description: `_check_format_purity` at `verify.py:348–375` iterates top-level title, top-level content, and every section title/content. All current tests place remnants in `sections[*].content` or `sections[*].title`; none place them in top-level `title` or `content`. A refactor that accidentally dropped the top-level branches would not be caught.
- Proposed fix: add two tests — one RST with `title="===="` at top level, one MD with `content="<br>"` at top level.
- Decision: keep as Low; coverage is easily added and strictly improves regression safety. This was also raised in R3 as L-2 and remains open.

---

## Positive Aspects

- Both R3 Medium findings have been addressed cleanly — the spec ambiguity (inline code) was pinned with an explicit test and doc-comment rather than silently patched.
- Self-closing tag coverage (`<br/>`, `<hr/>`, `<img/>`) is exhaustive against the Target list; each has its own dedicated FAIL test.
- False-positive probes exist for the subtle cases: heading underline inside code block (RST), field list `:name:` (RST), Japanese colon `：` (RST). This is the right instinct — tests specify *what is NOT a residue*, not just what is.
- Title-only heading-underline restriction is implemented at the API level (`is_title=True` flag, `verify.py:326, 358, 364`) and tested on both sides (positive L533, negative L577).
- `xlsx` short-circuit (`verify.py:349`) and `no_knowledge_content` short-circuit are both tested.
- Tests are structurally independent of implementation: no private-symbol import for re-application, no regex duplication in assertions. **Not circular.**
- Issue strings contain both the stable token `[QC5]` and a human-readable category keyword, giving tests two independent anchors for assertions.

---

## Recommendations

1. Add the two top-level-field tests (L-2) to close the last regression-safety gap. ~5 lines of test code.
2. Decide explicitly on the 3-character underline threshold (L-1) — either change `{4,}` → `{3,}` or pin the current threshold with a comment and test. Either outcome is defensible; what matters is that the decision is explicit.
3. No blockers for marking QC5 ✅ in Phase 21-Z. The four mechanical criteria (spec patterns covered; tests non-circular; verify FAIL 0 on v6; QA review conducted) are all met.

---

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source code, lines 314–375)
- `tools/rbkc/tests/ut/test_verify.py` (tests, `TestVerifyFileQC5`, 22 cases)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 (spec, reference)
- `.work/00299/review-z1-r3/QC5.md` (predecessor review, for delta check)
