# Expert Review: QA Engineer — QL2 (外部リンク)

**Date**: 2026-04-23
**Reviewer**: Independent QA Engineer (bias-avoidance stance, r5)
**Scope**: QL2 external link verification, per `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2
**Spec authority**: AST-only extraction — RST `reference.refuri`, MD `link_open[href]` (also covers CommonMark autolinks). Regex-based URL extraction explicitly forbidden.

## Overall Assessment

**Rating**: 4.5 / 5
**Summary**: QL2 implementation holds strictly to the AST-only principle — zero regex URL extraction anywhere in the QL2 paths. Test coverage handles http vs https, inline link / autolink, query+fragment, CJK trailing punctuation, parentheses, substitution-body exclusion, and RST backtick trim. Runtime state healthy: 18/18 QL2 UTs and 216/216 full UT suite pass, v6 verify PASS. The three review items from r3/r4 (parens circularity, RST bare-URL coverage, duplicate-miss FAIL case) remain unaddressed in r5 — re-flagged.

## Key Issues

### High Priority

None found.

### Medium Priority

1. **Parentheses-in-path test is circular (unchanged from r3/r4)**
   - Description: `test_pass_md_url_with_parentheses_in_path` (`tests/ut/test_verify.py:770-782`) derives the expected URL by calling the same extractor QL2 uses (`md_ast_visitor.extract_document(md_ast.parse(src)).external_urls[0]`) and puts that string into JSON. The pass/fail contract is AST self-consistency, not spec-conforming behaviour. A silent markdown-it change to parens slicing would still pass because both sides use the same AST output.
   - Proposed fix: Replace with two deterministic cases — (a) percent-encoded `https://example.com/foo%28bar%29` with URL hard-coded; (b) a raw `)` case with a hard-coded expected URL substring based on documented CommonMark behaviour. Keep an AST sanity assertion separately, but the pass contract must not be derived from the code under test.

2. **No RST bare-URL (standalone URL in prose) unit test (unchanged from r3/r4)**
   - Description: Spec §3-2 prescribes `reference.refuri` for RST. docutils emits `nodes.reference` for standalone URLs in running text (e.g., `詳細は https://foo.example を参照`), but no unit test pins this code path. Backtick-trim in inline literals is covered; bare-URL promotion is not. A docutils-level regression in standalone-URL recognition would be silent.
   - Proposed fix: Add `test_pass_rst_bare_url_collected` (URL appears as bare text in source, present in JSON → PASS) and `test_fail_rst_bare_url_missing` (same source, URL absent from JSON → FAIL with `[QL2]`). Locks the `reference.refuri` bare-URL path.

### Low Priority

3. **Duplicate-handling test only covers the PASS side (unchanged from r3/r4)**
   - Description: `test_pass_duplicate_url_reported_once` (`test_verify.py:684-689`) uses JSON containing the URL — "reported once" is vacuously satisfied; the `seen` dedup path (`verify.py:437-442`) is not exercised. Removing the `seen` guard would not break this test.
   - Proposed fix: Add a sibling: URL appears twice in source, absent from JSON; assert `sum(1 for i in issues if "[QL2]" in i) == 1`. This actually tests the dedup logic.

4. **No Visitor-level unit test for MD autolink (unchanged from r3/r4)**
   - Description: `test_md_ast_visitor.py:161-163` covers inline `[text](url)` collection; no dedicated Visitor test for CommonMark autolink `<https://...>`. QL2 integration test (`test_fail_md_autolink_url_missing`) covers it, but a Visitor-layer test pins behaviour at the lowest layer — cheaper to diagnose on markdown-it drift.
   - Proposed fix: Add `assert md_ast_visitor.extract_document(md_ast.parse("<https://x.example>")).external_urls == ["https://x.example"]`.

## Positive Aspects

- **Zero regex URL extraction in QL2 paths.** Repo-wide grep for `_URL_RE`, `findall.*http`, `re\.(search|match|findall).*http` under `tools/rbkc/scripts/` returns no matches. AST-only principle strictly upheld at `verify.py:382-414`, `md_ast_visitor.py`, `rst_ast_visitor.py`.
- **`_source_urls` cleanly delegates.** RST → `doctree.findall(nodes.reference)` filtered on `refuri.startswith(("http://", "https://"))`; MD → `md_ast_visitor.extract_document(...).external_urls`. Single parser as source of truth per format — no drift risk.
- **CommonMark autolink auto-covered.** markdown-it emits `link_open` for `<https://...>`, captured by the existing `link_open` handler without special-casing.
- **http vs https correctly distinguished.** Exact-string substring check (`verify.py:441`); `test_fail_md_http_vs_https_distinguished` (`test_verify.py:792-799`) confirms substitution of one scheme for the other FAILs.
- **CJK trailing punctuation not absorbed.** `test_pass_md_url_followed_by_japanese_punct_not_absorbed` (`test_verify.py:784-790`) locks AST boundary behaviour. The classic regex boundary bug is structurally impossible.
- **Substitution-body URLs excluded.** `test_pass_rst_substitution_only_url_skipped` keeps source-side collection aligned with converter drops — no spurious FAIL.
- **Query+fragment preserved byte-exact.** `test_pass_md_url_with_query_and_fragment` covers `?x=1&y=2#frag` intact.
- **All 18 QL2 unit tests pass**; full UT suite **216/216** passes (up from 208 in r4).
- **v6 runtime verify PASS** (`bash rbkc.sh verify 6` → `All files verified OK`).

## Recommendations

- Apply Medium-priority fixes (de-circularize parens; add RST bare-URL PASS/FAIL pair) before declaring 100% AST-path coverage. They have been flagged in r3 and r4 and remain open.
- Apply Low-priority fixes opportunistically (few lines each), closing real blind spots.
- Annotate spec §3-2: "MD `link_open[href]` subsumes both inline `[text](url)` and CommonMark autolink `<url>`" — prevents future readers from adding a redundant autolink extractor.
- Optional: property-style test over a curated URL list (query, fragment, CJK boundary, parens, port, IPv6-literal, percent-encoding) asserting byte-exact round-trip through `_source_urls`.

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source) — QL2 at lines 378-443
- `tools/rbkc/scripts/common/md_ast.py` (source)
- `tools/rbkc/scripts/common/md_ast_visitor.py` (source) — `link_open` handler
- `tools/rbkc/scripts/common/rst_ast_visitor.py` (source)
- `tools/rbkc/tests/ut/test_verify.py` (tests) — `TestVerifyFileQL2` at 666-799
- `tools/rbkc/tests/ut/test_md_ast_visitor.py` (tests)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` (spec) — §3-2

## Runtime Evidence

- `pytest tests/ut/test_verify.py::TestVerifyFileQL2` → **18 passed**
- `pytest tests/ut/` → **216 passed** (up from 208 in r4)
- `bash rbkc.sh verify 6` → `All files verified OK`
- Repo grep for regex URL extraction in QL2 scope → **no matches**

## Bias-Avoidance Notes

- Spec is the authority. Runtime PASS is explicitly weighted low: it only proves current output and current RBKC are self-consistent — not that QL2 is spec-complete.
- Medium #1 (circular parens) re-flagged: asserting code-under-test output back against itself is structurally incapable of catching regressions; this is a QA anti-pattern independent of current green status.
- Medium #2 (RST bare-URL) re-flagged on spec §3-2 grounds — docutils' standalone-URL recognition is a silent dependency of QL2 correctness and deserves an explicit test lock.
- No code modifications made (review-only, per instructions).
