# QA Review: QL2 外部リンクの一致

**Reviewer**: Independent QA Engineer (Z-1 R2, no prior-review context)
**Date**: 2026-04-23
**Target**: `check_external_urls` / `_source_urls` + `TestVerifyFileQL2`
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2 "QL2（外部リンク）"

## Overall Assessment

**Rating**: 4/5

**Summary**: Implementation is faithful to the AST-only principle — RST URLs come
from `docutils` `reference.refuri`, MD URLs come from the markdown-it-py AST visitor
which handles both `[text](href)` inline links and CommonMark autolinks
`<https://...>` via the same `link_open` token path. No regex-based URL extraction
exists in the QL2 code path. The 18 unit tests cover the required edge-cases (query
strings, fragments, parens in path, trailing Japanese punctuation, http vs https,
duplicates, substitution-body-only URLs, xlsx skip, no-knowledge skip, section-
nested content). v6 `rbkc.sh verify 6` returns `All files verified OK`; full verify
pytest suite: 127 passed. Minor gaps: (a) no explicit PASS test for MD autolink
(only FAIL side), (b) the parens-in-path test has mild circularity — it builds the
expected JSON from the AST's own output, so it verifies "verify accepts whatever
the AST emits" rather than a spec-derived expectation. Neither blocks quality-gate
correctness.

## Implementation Audit

**`scripts/verify/verify.py:289-321` `_source_urls`**
- RST branch (L297-309): iterates `doctree.findall(nodes.reference)` and collects
  `ref.get("refuri")` when it starts with `http://`/`https://`. Pure AST attribute
  access — spec-compliant.
- MD branch (L311-319): delegates to `md_ast_visitor.extract_document(...)` and
  returns `parts.external_urls`. No raw-text scanning.
- Defensive exception handling returns `[]` on parse failure (non-fatal, reasonable).

**`scripts/verify/verify.py:324-350` `check_external_urls`**
- Early-outs on `xlsx` and `no_knowledge_content` (appropriate — aligned with
  §3-2 scope and top-level skip rules).
- Substring presence check against `_all_text(data)`. Deduplicates via `seen: set`
  so a URL appearing N times in source is reported at most once (L343-347).

**`scripts/common/md_ast_visitor.py:394-413`**
- Single `link_open` handler collects `href` when prefix is `http(s)://`. Because
  markdown-it-py represents CommonMark autolinks `<https://...>` as `link_open`
  tokens with the href populated, the same branch covers inline links and
  autolinks — confirmed empirically (autolink + inline extraction output
  `['https://example.com/auto', 'https://example.com/link']`).

**Regex-URL check**: `grep "re\.\|regex"` filtered by url/http in verify.py returns
only `scripts/verify/verify.py:518` which is an RST skip-line classifier for
anonymous hyperlink targets (`^__\s+https?://`), not URL extraction. No regex URL
extraction anywhere in the QL2 path.

## Key Issues

### High Priority

None.

### Medium Priority

**[Medium] Missing MD autolink PASS case**
- **Description**: `test_fail_md_autolink_url_missing` (test_verify.py:651-656)
  confirms FAIL detection, but no symmetric PASS test exercises the autolink path
  when the URL is present in JSON. Inline-link PASS
  (`test_pass_md_inline_link_url_present`, L646-649) exists. Because autolinks
  and inline links share the `link_open` handler in md_ast_visitor.py:394-411,
  risk is low — but by the "every branch in verify needs a test" rule
  (`.claude/rules/rbkc.md` Test coverage policy), both success and failure
  outcomes of each input shape should be asserted independently.
- **Proposed fix**: Add a test that puts the autolink URL inside JSON content and
  asserts `check_external_urls` returns `[]`:
  ```python
  def test_pass_md_autolink_url_present(self):
      src = "# T\n\nvisit <https://auto.example.com/path>\n"
      data = {"id": "f", "title": "T",
              "content": "visit https://auto.example.com/path", "sections": []}
      assert self._check_ql2(src, data, "md") == []
  ```

**[Medium] Mild circularity in `test_pass_md_url_with_parentheses_in_path`**
- **Description**: `test_verify.py:665-677` builds the expected JSON content by
  calling `md_ast_visitor.extract_document(...)` at test-time and embedding the
  AST's first URL (`expected`) into `data["content"]`. This means the test
  asserts "verify accepts whatever the AST produces," not "the URL matches the
  source-format spec." If the AST ever truncates `foo(bar)` incorrectly, this
  test still passes.
- **Proposed fix**: Either (a) hard-code the expected URL (spec-derived, from
  CommonMark 0.30 §6.3 which defines `(` / `)` balance rules) and assert the AST
  returns it, then check verify; or (b) move the circular portion into a separate
  AST-visitor unit test and leave QL2 with a spec-fixed URL only. Option (a) is
  the lighter fix.

### Low Priority

**[Low] `test_pass_no_knowledge_content_skipped` does not assert the reason**
- **Description**: `test_verify.py:602-605` passes `no_knowledge_content=True` but
  also lacks URLs in JSON — the test would still pass even if the skip were
  removed (because the check finds no JSON URL to flag and the source URL would
  fail — actually would fail; keeping this as Low). Minor ambiguity, not a
  correctness gap.
- **Proposed fix**: None required; optional documentation-comment tightening.

## Positive Aspects

- Strict AST-only extraction for both RST and MD — no regex URL parsing anywhere
  in the QL2 path (verified by grep + manual read of verify.py:289-321 and
  md_ast_visitor.py:394-413).
- Real-world edge cases covered: trailing backticks in RST inline code
  (L622-626), Japanese closing quote `」` after an inline link (L679-685),
  substitution-body-only URLs (L628-636), http vs https distinction (L687-694),
  query+fragment preservation (L658-663).
- Duplicate-URL deduplication is tested (L579-584) and implemented correctly
  via `seen: set` (verify.py:343-347).
- Section-level content (not only top-level `content`) is checked via
  `_all_text(data)`, with both FAIL and PASS tests (L607-620).
- v6 runtime clean (`All files verified OK`), 127/127 verify unit tests pass.

## Recommendations

1. Add the MD autolink PASS test (Medium #1) — 6 lines, eliminates a coverage gap.
2. Replace the circular portion of the parens test with a spec-derived expected
   value (Medium #2).
3. Consider a docstring on `_source_urls` noting that CommonMark autolinks are
   intentionally captured via the same `link_open` branch, so future maintainers
   do not add a second (regex-based) code path by mistake.

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (L285-350 — QL2 implementation)
- `tools/rbkc/scripts/common/md_ast_visitor.py` (L380-416 — MD URL extraction)
- `tools/rbkc/tests/ut/test_verify.py` (L558-694 — `TestVerifyFileQL2`, 18 tests)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2 (spec)

## Runtime Evidence

- `cd tools/rbkc && ./rbkc.sh verify 6` → `All files verified OK`
- `pytest tests/ut/test_verify.py::TestVerifyFileQL2 -v` → 18 passed
- `pytest tests/ut/test_verify.py -q` → 127 passed
- Autolink AST probe (inline python): `external_urls: ['https://example.com/auto', 'https://example.com/link']` — confirms CommonMark autolink is emitted as `link_open` token with href populated.
