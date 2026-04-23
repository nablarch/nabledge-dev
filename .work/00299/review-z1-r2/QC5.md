# Expert Review: QA Engineer — QC5 形式純粋性

**Date**: 2026-04-23
**Reviewer**: Independent QA Engineer (no prior review context)
**Target**: QC5 implementation, tests, and v6 runtime
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1, lines 197–205

## Overall Assessment

**Rating**: 4/5
**Summary**: Implementation is aligned with the spec for all named items; title-only gating of the heading-underline check is correctly enforced; unit tests cover the full spec inventory plus documented false-positive cases. v6 verify passes. One concrete detection gap (self-closing void HTML tags like `<br/>`) and one circular-looking test were found.

## Condition 1 — Implementation

File: `tools/rbkc/scripts/verify/verify.py:225-282`

| Spec item (§3-1) | Regex | Location | Verdict |
|---|---|---|---|
| RST `:role:\`text\`` | `r':[a-zA-Z][a-zA-Z0-9_.-]*:\`'` | verify.py:225 | OK — requires the backtick, so lone `:name:` won't false-fire |
| RST `.. directive::` | `r'\.\.\s+\S+.*::'` | verify.py:226 | OK |
| RST `.. _label:` | `r'\.\.\s+_[a-zA-Z0-9_-]+:'` | verify.py:228 | OK |
| RST heading underline, **title only** | `r'^[=\-~^"\'\`#*+<>]{4,}\s*$'` MULTILINE | verify.py:227, gated by `is_title` at verify.py:241 | OK — content path does not invoke the underline check; code-block `====` in content is safe |
| MD raw HTML `<[a-zA-Z]` | `r'(?<![a-zA-Z])<[a-zA-Z][a-zA-Z0-9]*[\s>]'` | verify.py:229 | Partial — see High #1 |
| MD backslash escapes `\*` `\_` `\[` etc. | `r'\\[*_\`\[\](){}#+\-.!\|]'` | verify.py:230 | OK — covers the spec characters and common neighbors |

Dispatch (`_check_format_purity` verify.py:255-282) iterates top-level title/content and every section title/content for RST and MD; passes `is_title=True` correctly at verify.py:265 and verify.py:271; skips xlsx and `no_knowledge_content` (verify.py:256). Integration at verify.py:953.

## Condition 2 — Unit Tests

File: `tools/rbkc/tests/ut/test_verify.py:418-554` (`TestVerifyFileQC5`, 18 cases)

Coverage vs. required matrix:

- RST: `:ref:\`\`` (line 438-443), `:class:\`\`` — not named but `:role:` covered generically, directive `.. note::` (445-450), `.. _lbl:` (452-457), heading underline in title (459-462) — **all present**
- RST PASS: underline inside fenced code block in content (503-509), `:name:` without backtick arg (511-517), Japanese punctuation `：` (519-524) — **false-positive guards present**
- MD FAIL: `<summary>` (526-530), `<br>` (532-536), `<a>` (538-542), `\*` (478-483), `\_` (544-548), `\[` (550-554) — **all present**
- XLSX / no_knowledge skip paths: 491-499

**Test quality findings:**

- **Circular test risk (Low)** — `test_pass_rst_role_marker_without_backtick_arg` (test_verify.py:511-517) and its test docstring both cite the same spec phrase ("`:role:\`text\`` パターン"). The test passes because the regex happens to require a backtick, not because an independent spec-derived oracle was applied. This is borderline circular (test mirrors regex). Recommend restating the oracle as: "a lone `:name:` followed by non-backtick is valid RST field/option syntax and must not be flagged." Behaviorally correct, but rationale is thin.
- **Missing negative: inline code containing role syntax (Medium)** — spec lists `:role:\`text\`` as the target, but there is no test for the case "JSON content contains a backticked substring that *looks* like a role because of upstream formatting" (e.g., `\`:ref:\`foo\`\``). verify operates on JSON plaintext where inline backticks are content, so a literal `:ref:\`foo\`` in content would (correctly per spec) FAIL. A test clarifying this non-exemption would harden the contract.
- **No assertion on non-title underline content path (Low)** — `test_pass_rst_heading_underline_in_code_block_content` uses a fenced code block but the implementation does not parse fences; the test effectively asserts only that *content* is exempt regardless of shape. Fine, but the test name over-promises "code block" semantics.

## Condition 3 — v6 Runtime

- Unit tests: `pytest tests/ut/test_verify.py::TestVerifyFileQC5` → **18 passed**
- v6 verify: `./rbkc.sh verify 6` → **All files verified OK**

No QC5 failures on current v6 output. v6 passing is weak evidence of correctness on its own; the test suite + spec-mapped regex table above is the stronger signal.

## Key Issues

### High

1. **Self-closing HTML tags without whitespace evade detection**
   - Description: `_MD_RAW_HTML_RE` requires `[\s>]` after the tag name (verify.py:229). `<br/>`, `<hr/>`, `<img/>` (no space before `/>`) do **not** match. Empirical check: `re.search(r'(?<![a-zA-Z])<[a-zA-Z][a-zA-Z0-9]*[\s>]', '<br/>')` → `None`. The spec (line 203) targets "`<[a-zA-Z]` で始まる raw HTML タグ (`<details>`, `<summary>`, `<br>` 等)" — the `/` before `>` form is clearly in scope.
   - Proposed fix: change character class to `[\s/>]` (or use `[\s>/]`). Add unit test `test_fail_md_self_closing_br_no_space` asserting `<br/>` and `<hr/>` FAIL.

### Medium

2. **No test for role syntax appearing inside backtick-wrapped content**
   - Description: The spec treats `:role:\`text\`` as always a QC5 violation when present in JSON (content should be plaintext). No test asserts that a content string like `"see :ref:\`foo\` for details"` FAILs. The existing role test uses content = `":ref:\`something\`"` alone, which is equivalent but doesn't document the "embedded in prose" case.
   - Proposed fix: add `test_fail_rst_role_embedded_in_prose` with content `"本文 :ref:\`x\` の続き"`.

3. **Borderline circular test for `:name:` without backtick**
   - Description: `test_pass_rst_role_marker_without_backtick_arg` (test_verify.py:511) — the PASS behavior exactly mirrors the regex's backtick requirement. The oracle (spec) is the same text the regex encodes, so the test confirms the implementation matches itself.
   - Proposed fix: reframe the test around an independent RST semantic — e.g., "field lists (`:author: name`) are valid RST and legal in plaintext; QC5 only targets roles which require backtick delimiters." Add an adjacent FAIL test with an actual role to show the boundary is meaningful.

### Low

4. **3-character heading underlines are allowed**
   - Description: `_RST_HEADING_UNDERLINE_RE` requires `{4,}`. RST syntactically allows `===` (3 chars) as a heading underline when the title is short. Spec example uses `====`/`----` (4+) so this matches the spec literally, but short titles could slip through.
   - Proposed fix: discuss with user whether to relax to `{3,}`. Low priority because RBKC's own titles are typically long CJK strings and underline remnants in output would almost certainly be longer.

5. **No test asserting section-title path for QC5**
   - Description: `_check_format_purity` calls `_md_syntax_issues` on section titles (verify.py:280) but no test triggers a QC5 violation via section *title* (only section *content*). A simple addition would lock in that code path.
   - Proposed fix: add `test_fail_md_html_in_section_title`.

## Positive Aspects

- Title-only gating of the heading-underline check is implemented cleanly via the `is_title` kwarg (verify.py:233, 241, 265, 271), preventing false positives from code blocks in content — this matches the spec line 202 carve-out exactly.
- False-positive PASS cases (Japanese punctuation, `:name:` without backtick, underline in content) are explicitly tested, showing awareness of locale and non-role colon syntax.
- MD backslash-escape regex covers the full CommonMark ASCII punctuation class that can legally be escaped, not just the two examples in the spec.
- `xlsx` and `no_knowledge_content` short-circuits are tested (test_verify.py:491-499).
- verify does not import from create-side; independence per `.claude/rules/rbkc.md` is preserved.

## Recommendations

1. Fix High #1 immediately — self-closing void tags without space are a realistic output from MD normalisers and would pass undetected today.
2. Add the Medium tests to remove circularity and lock in embedded-role and section-title code paths.
3. Consider a brief comment block above the regex definitions at verify.py:225-230 citing spec §3-1 line numbers so future edits don't drift from the spec.

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (source code — lines 221-282, 953)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (tests — lines 415-554)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` (spec — §3-1, lines 197-205)
