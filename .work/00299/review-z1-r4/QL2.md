# Expert Review: QA Engineer — QL2 (外部リンク)

**Date**: 2026-04-23
**Reviewer**: Independent QA Engineer (bias-avoidance stance, r4)
**Scope**: QL2 external link verification, per `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2
**Spec authority**: AST-only extraction — RST `reference.refuri`, MD `link_open[href]` (which also covers CommonMark autolinks). Regex-based URL extraction explicitly forbidden.

## Overall Assessment

**Rating**: 4.5 / 5
**Summary**: Implementation strictly adheres to the AST-only principle; zero regex URL extraction in QL2 paths. Test coverage handles http/https, query/fragment, CJK trailing punctuation, parentheses, autolink, substitution-body exclusion, and RST backtick trim. The r3 review's Medium (parens circularity, RST bare-URL) and Low (duplicate-miss failure case, Visitor-level autolink) findings appear unchanged — still applicable in r4.

## Key Issues

### High Priority

None found.

### Medium Priority

1. **Parentheses-in-path test is circular (unchanged from r3)**
   - Description: `test_pass_md_url_with_parentheses_in_path` (`tests/ut/test_verify.py:770-782`) derives the expected URL by calling the same extractor QL2 uses: `md_ast_visitor.extract_document(md_ast.parse(src)).external_urls[0]`, then uses that exact string as JSON content. This asserts AST round-trip self-consistency, not spec-conforming behaviour. If markdown-it silently changes how it slices `https://example.com/foo(bar)` (include/exclude trailing `)`), the test still passes because JSON is rebuilt from the same AST output — the test cannot detect the regression it was written to guard against.
   - Proposed fix: Replace with two deterministic cases — (a) percent-encoded parens `https://example.com/foo%28bar%29` with full URL hard-coded as expected; (b) raw `)` case with a hard-coded expected URL substring based on markdown-it's documented CommonMark behaviour. Keep a separate AST sanity precondition, but the pass/fail contract must not be derived from the code under test.

2. **No RST bare-URL (standalone URL in prose) unit test (unchanged from r3)**
   - Description: Spec §3-2 specifies `reference.refuri` for RST. docutils emits `nodes.reference` for standalone URLs (e.g., bare `https://foo.example` appearing in running text), but no unit test pins this path. Backtick-trim in inline literals is covered; bare-URL promotion is not. A silent regression in docutils' standalone-URL recognition would go undetected.
   - Proposed fix: Add `test_pass_rst_bare_url_collected` (source: `詳細は https://bare.example/x を参照` with URL in JSON → PASS) and `test_fail_rst_bare_url_missing` (same source, URL absent → FAIL with `[QL2]`). Locks the docutils `reference.refuri` path for the bare-URL form.

### Low Priority

3. **Duplicate-handling test only covers the PASS side (unchanged from r3)**
   - Description: `test_pass_duplicate_url_reported_once` (`test_verify.py:684-689`) uses JSON containing the URL, so "reported once" is vacuously satisfied — the `seen` set's dedup-on-failure path is never exercised. If the `seen` guard were removed, the test would still pass.
   - Proposed fix: Add a sibling case: URL appears twice in source, absent from JSON; assert `sum(1 for i in issues if "[QL2]" in i) == 1`. This actually tests the dedup logic in `verify.py:437-442`.

4. **No Visitor-level unit test for MD autolink (unchanged from r3)**
   - Description: `test_md_ast_visitor.py:161-163` covers inline `[text](url)` collection into `external_urls`, but has no dedicated Visitor test for CommonMark autolink form `<https://...>`. QL2 integration test (`test_fail_md_autolink_url_missing`) covers it, but a Visitor-layer test pins behaviour at the lowest layer — cheaper to diagnose when markdown-it changes.
   - Proposed fix: Add one Visitor test asserting `md_ast_visitor.extract_document(md_ast.parse("<https://x.example>")).external_urls == ["https://x.example"]`.

## Positive Aspects

- **Zero regex URL extraction in QL2 paths**: Searches across `scripts/` for `_URL_RE`, `findall.*http`, `re\.search.*http`, `re\.match.*http` return no matches in QL2 code paths. AST-only principle strictly upheld at `verify.py:382-414`, `md_ast_visitor.py:394-415`, `rst_ast_visitor.py`.
- **`_source_urls` cleanly delegates**: RST → `doctree.findall(nodes.reference)` filtered by `refuri.startswith(("http://", "https://"))`; MD → `md_ast_visitor.extract_document(...).external_urls`. Single parser source, no config drift risk.
- **CommonMark autolink auto-covered**: markdown-it emits `link_open` for `<https://...>`, captured by the existing `link_open` handler without special-casing (`md_ast_visitor.py:395-412`).
- **http vs https distinction correct**: Exact-string substring check (`verify.py:441`) naturally distinguishes the two schemes — test `test_fail_md_http_vs_https_distinguished` confirms (`test_verify.py:792-799`).
- **CJK trailing punctuation not absorbed**: `test_pass_md_url_followed_by_japanese_punct_not_absorbed` (`test_verify.py:784-790`) locks the AST boundary behaviour — the classic regex bug is structurally impossible here.
- **Substitution-body URLs excluded**: `test_pass_rst_substitution_only_url_skipped` confirms source-side collection does not leak converter-dropped URLs → no false QL2 FAIL.
- **Query/fragment preserved byte-exact**: `test_pass_md_url_with_query_and_fragment` covers `?x=1&y=2#frag` without truncation.
- **All 18 QL2 unit tests pass**; full UT suite 208/208 passes (up from 194 in r3).
- **v6 runtime verify PASS** (`bash rbkc.sh verify 6` → `All files verified OK`).

## Recommendations

- Apply Medium-priority fixes (de-circularize parens test; add RST bare-URL coverage) before declaring "100% AST-path coverage". These are the same items flagged in r3 and remain unaddressed.
- Apply Low-priority fixes opportunistically — they are cheap (a few lines each) and close small but real blind spots in the test suite.
- Consider annotating spec §3-2: "MD `link_open[href]` subsumes both inline `[text](url)` and CommonMark autolink `<url>`" — prevents future readers from adding a redundant autolink extractor.
- Optional: property-style test over a curated URL list (query, fragment, CJK boundary, parens, port, IPv6-literal, percent-encoding) asserting byte-exact round-trip through `_source_urls`.

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source) — QL2 at lines 378-443
- `tools/rbkc/scripts/common/md_ast.py` (source) — MD parser wrapper
- `tools/rbkc/scripts/common/md_ast_visitor.py` (source) — `link_open` at 395-419
- `tools/rbkc/scripts/common/rst_ast_visitor.py` (source)
- `tools/rbkc/tests/ut/test_verify.py` (tests) — `TestVerifyFileQL2` at 666-799
- `tools/rbkc/tests/ut/test_md_ast_visitor.py` (tests) — `external_urls` at 161-163
- `tools/rbkc/docs/rbkc-verify-quality-design.md` (spec) — §3-2

## Runtime Evidence

- `pytest tests/ut/test_verify.py::TestVerifyFileQL2` → **18 passed**
- `pytest tests/ut/` → **208 passed**
- `bash rbkc.sh verify 6` → `All files verified OK`

## Bias-Avoidance Notes

- Spec is authoritative. v6 PASS is explicitly weighted low: it only shows current output is self-consistent with current RBKC, not that QL2 spec conformance is complete.
- Medium #1 (circular parens test) flagged because asserting code-under-test output back against itself is structurally incapable of catching regressions — this is a QA anti-pattern independent of current pass status.
- Medium #2 (bare-URL) flagged on spec §3-2 grounds, not on "would be nice". docutils' bare-URL recognition is a silent dependency of QL2 correctness.
- No code modifications made (review-only, per instructions).
