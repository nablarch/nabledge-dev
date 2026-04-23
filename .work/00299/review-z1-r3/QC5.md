# Expert Review: QA Engineer — QC5 形式純粋性

**Date**: 2026-04-23
**Reviewer**: AI Agent as QA Engineer (independent, bias-avoidance)
**Scope**: QC5 (format purity) — implementation + unit tests + v6 runtime
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 "QC5 形式純粋性（独立チェック）"
**Files reviewed**:
- `tools/rbkc/scripts/verify/verify.py` (lines 269-335, QC5 block)
- `tools/rbkc/tests/ut/test_verify.py` (lines 443-603, `TestVerifyFileQC5`)

---

## Bias-avoidance posture

- Spec is authoritative. Implementation and tests were evaluated against the spec text, not against each other.
- v6 verify PASS is explicitly treated as **weak evidence**: absence of QC5 FAILs on v6 can mean either "RBKC output is clean" or "detector missed them". The spec-vs-regex gap analysis below is the primary evidence.
- I did not modify code. Findings are cited `file:line`.

---

## Overall Assessment

**Rating**: 4/5

**Summary**: The QC5 implementation and its unit tests cover every pattern the spec lists (RST role / directive / label / title-only heading underline; MD raw HTML including self-closing `<br/>` `<hr/>` `<img/>`; MD backslash escapes). Self-closing tag detection works correctly (verified below). The main residual risks are (a) the RST directive regex is greedier than the spec reads, (b) there is no false-positive test for inline-code / fenced-code content in MD, where `<br>` or `\*` appearing **inside** backticks would currently FAIL even though they are legitimate inline literals. Tests are not circular.

---

## Evaluation by the three requested axes

### (1) Implementation — does `_MD_RAW_HTML_RE` catch self-closing tags?

**Yes.** `verify.py:277`:

```
_MD_RAW_HTML_RE = re.compile(r'<[a-zA-Z][a-zA-Z0-9]*(?:\s[^>]*)?/?>')
```

Empirical check (`<br>`, `<br/>`, `<br />`, `<hr/>`, `<img/>`, `<img src="x"/>`, `<details>`, `<a href="x">`, `<br  />`) all match. The optional `/?` just before the closing `>` together with `(?:\s[^>]*)?` covers both `<br/>` (no attributes, no space) and `<img src="x"/>` (attributes + self-close).

One narrow gap worth flagging (Medium, not High): the `\s` (single space) requirement before attributes means a tag like `<br\t/>` (tab before `/`) still matches via `\s`, but a form like `<tag\n/>` across a newline would match only because `\s` includes `\n`. Not a real gap.

### (2) Unit tests

**RST** (`test_verify.py:467-497, 532-555`):

| Spec pattern | Test | Status |
|---|---|---|
| `:role:\`text\`` | `test_fail_rst_role_in_content` (L467) | PASS |
| `.. directive::` | `test_fail_rst_directive_in_content` (L474) | PASS |
| `.. _label:` | `test_fail_rst_label_in_content` (L481) | PASS |
| Title-only heading underline | `test_fail_rst_heading_underline_in_title` (L488) | PASS |
| Clean content → no FAIL | `test_pass_rst_clean_content` (L493) | PASS |
| Underline in code block (content) → no FAIL | `test_pass_rst_heading_underline_in_code_block_content` (L532) | PASS |
| Field-list marker `:name:` is not a role | `test_pass_rst_field_list_syntax_is_not_qc5_role` (L540) | PASS |
| Japanese colon `：` is not a role | `test_pass_rst_japanese_punctuation_not_confused_with_role` (L550) | PASS |

All 4 spec patterns are covered plus three well-chosen false-positive probes.

**MD** (`test_verify.py:500-603`):

| Spec pattern | Test | Status |
|---|---|---|
| `<details>` / `<summary>` / `<br>` (raw HTML, open tags) | L500, L557, L563 | PASS |
| `<a href='x'>` (attributes) | L569 | PASS |
| `<br/>` self-closing | `test_fail_md_self_closing_br` (L587) | PASS |
| `<hr/>` self-closing | `test_fail_md_self_closing_hr` (L593) | PASS |
| `<img/>` self-closing | `test_fail_md_self_closing_img` (L599) | PASS |
| `\*` backslash-star | L507 | PASS |
| `\_` backslash-underscore | L575 | PASS |
| `\[` backslash-bracket | L581 | PASS |
| Clean content → no FAIL | L514 | PASS |

All three self-closing forms explicitly called out in the Target section are present as failing tests.

**Cross-format**:
- `test_pass_xlsx_no_qc5` (L520) asserts QC5 is skipped on xlsx (spec: "— for Excel"). Good.
- `test_pass_no_knowledge_content_skipped` (L526) asserts `no_knowledge_content: true` JSON is skipped. Matches `_check_format_purity` guard at `verify.py:304`.

**Circular-test check**: NO. Each test constructs a JSON payload with a hand-written remnant (`":ref:\`x\`"`, `"<br/>"`, `r"\*"`, …) and asserts the issue string contains `"QC5"` and a human-readable keyword (`"HTML"`, `"backslash"`, `"role"`, `"directive"`, `"label"`, `"underline"`). Expected values are derived from the spec wording, not from what `verify.py` happens to emit — the tests would still pass if the regex were replaced by an equivalent one that produces the same boolean verdict with the same issue-string keyword. No test imports a private regex and re-applies it (no tautology).

**Pytest run**:

```
tests/ut/test_verify.py::TestVerifyFileQC5  21 passed
tests/ut/test_verify.py                    134 passed in 0.59s
```

### (3) v6 runtime

`./rbkc.sh verify 6` → `All files verified OK` (no FAILs). Per the bias-avoidance posture, this alone does not prove QC5 is correct — only that RBKC's current output does not trip the current detector. The structural evidence (spec-vs-regex coverage above) is what carries weight.

---

## Key Issues

### High Priority

_None._

### Medium Priority

**M-1. MD inline-code / fenced-code false positive (untested gap)**
- Description: `_MD_RAW_HTML_RE` and `_MD_BACKSLASH_ESCAPE_RE` are applied to the raw JSON `content` string without excluding inline-code spans (`` `…` ``) or fenced code blocks (```` ``` ````). A JSON content legitimately containing `` `<br>` `` (as a literal HTML example inside inline code) or `` `\*` `` (as a literal escape example inside inline code) would FAIL QC5. I confirmed this behaviour empirically. The current test suite has no probe for this case, so a regression here would go undetected.
- Spec basis: §3-1 QC5 defines the pattern as "MD: `<[a-zA-Z]` で始まる raw HTML タグ … `\*`・`\_` 等のバックスラッシュエスケープ". The spec does not explicitly say "outside inline code", but the intent of QC5 is "unprocessed format remnants" — a literal `<br>` inside a backtick span is **processed** MD, not residue. This is analogous to the RST heading-underline-in-code-block false-positive probe that already exists at `test_verify.py:532`.
- Proposed fix: add two false-positive tests (one for inline-code, one for fenced-code) mirroring the RST probe at L532:
  - content = `"HTMLタグ例: \`<br>\` を使う"` → expect no QC5 HTML issue
  - content = ```"```\n<br>\n```"``` → expect no QC5 HTML issue
  - content = `"エスケープ例: \`\\*\` はアスタリスク"` → expect no QC5 backslash issue
  If these RED, strip code spans/fences before scanning (a small helper that removes ``` `[^`]*` ``` and ```` ```…``` ```` regions) is the minimum fix.
- Decision for the developer: **investigate whether v6 output actually contains such code-span examples**. If it does, this is a latent false positive waiting to surface; if it does not today, still add the tests to lock the behaviour before RBKC learns to emit them.

**M-2. RST directive regex is broader than the spec text**
- Description: `_RST_DIRECTIVE_RE = re.compile(r'\.\.\s+\S+.*::')` at `verify.py:274` matches any line fragment of the form `..  something ... ::`. It correctly catches `.. note::` but will also match contrived strings like `"表記 ..  foo ::"` — any substring starting with `.. ` and ending with `::` on the same span. The spec pattern is `.. directive::` (i.e. `..` + whitespace + identifier + `::`). There is no test exercising a tricky near-match (e.g. Japanese sentence containing `…::` or `．．foo::`).
- Proposed fix: either tighten the regex to `^\.\.\s+[A-Za-z][\w-]*::` with `re.MULTILINE` (matches RST directive line start; spec-aligned), or add a false-positive test showing the current regex does not misfire on realistic Japanese content. Tightening is preferred because the current regex is overly permissive.

### Low Priority

**L-1. Issue-string assertion keywords are lightly coupled to wording**
- Description: tests assert `"HTML" in i`, `"backslash" in i`, `"role" in i` etc. If a future refactor renames `"raw HTML tag detected"` to `"unprocessed inline HTML"` the MD self-closing tests would silently become non-asserting (still pass because the wrong branch produces a different message that happens to contain… actually no, they would fail — false alarm for coupling, not for brittleness). Worth documenting in a test file comment that these keyword tokens are load-bearing. No fix required.

**L-2. No test exercises QC5 on top-level `title` / top-level `content`**
- Description: `_check_format_purity` at `verify.py:309-334` iterates top-level title, top-level content, and every section title/content. Tests cover section title (title-only underline at L488) and section content exhaustively, but do not exercise a QC5 failure placed in the **top-level** `title` or **top-level** `content` fields. A refactor that accidentally dropped the top-level loop would not be caught.
- Proposed fix: add one test with `title="==="` (RST) and one with `content="<br>"` at top level.

---

## Positive Aspects

- Self-closing tag coverage is explicit and complete (`<br/>`, `<hr/>`, `<img/>`) — matches the Target exactly.
- False-positive probes exist for the subtle RST cases (heading underline in code block, field list `:name:`, Japanese `：` punctuation) — this is the right instinct and shows the author understood the difference between residue and legitimate text.
- Title-only heading-underline restriction is implemented (`is_title=True` flag at `verify.py:289, 313, 319`) and tested (L488 positive, L532 negative). This matches spec §3-1 exactly.
- `xlsx` short-circuit and `no_knowledge_content` short-circuit are both tested.
- Tests are structurally independent of the implementation: no private-symbol import for re-application, no regex duplication in assertions. Not circular.
- v6 runtime is green — no QC5 FAIL.

---

## Recommendations

1. Close the inline-code / fenced-code false-positive gap for MD (M-1) — highest-value follow-up.
2. Tighten `_RST_DIRECTIVE_RE` to a line-anchored form and add a Japanese-text false-positive probe (M-2).
3. Add top-level title/content QC5 tests (L-2) to guard against regression in the field enumeration.
4. None of the above block Phase 21-Z marking QC5 as ✅ per the spec's ✅-rules, **provided** M-1 is either confirmed non-occurring on v6 or fixed. Current state: spec patterns covered, tests non-circular, v6 FAIL 0 — meets the three mechanical ✅ criteria; the QA review (this document) is the fourth.

---

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source code)
- `tools/rbkc/tests/ut/test_verify.py` (tests)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 (spec, reference)
