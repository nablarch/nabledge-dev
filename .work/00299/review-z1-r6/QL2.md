# Expert Review: QA Engineer — QL2 (外部リンク)

**Date**: 2026-04-23
**Reviewer**: Independent QA Engineer (bias-avoidance stance, r6)
**Scope**: QL2 external link verification, per `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2
**Spec authority (§3-2)**: AST-only extraction — RST via `reference.refuri`, MD via `link_open[href]` (CommonMark autolink `<url>` subsumed). Regex URL extraction explicitly forbidden (`_URL_RE` etc.).

## Overall Assessment

**Rating**: 4.5 / 5
**Summary**: QL2 implementation continues to hold strictly to the AST-only principle — no regex URL extraction anywhere in the QL2 code path. Test suite grew to 218 UTs (216 → 218) and all QL2 tests (18/18) still pass, v6 verify runtime PASS. However, the three open review items inherited from r3 / r4 / r5 (circular parentheses test, missing RST bare-URL lock, PASS-only duplicate-handling test) remain unaddressed in r6 — re-flagged.

## Key Issues

### High Priority

None found.

### Medium Priority

1. **Parentheses-in-path test remains circular (unchanged from r3/r4/r5)**
   - Description: `test_pass_md_url_with_parentheses_in_path` (`tools/rbkc/tests/ut/test_verify.py:804-816`) derives the expected URL by calling the *same* extractor QL2 uses — `md_ast_visitor.extract_document(md_ast.parse(src)).external_urls[0]` at lines 811-814 — and writes that string back into the JSON fixture at line 815. The pass/fail contract is therefore AST self-consistency, not spec-conforming behaviour. If markdown-it changes how it slices `(bar)` inside the URL, both sides of the assertion drift together and the test continues to pass silently.
   - Proposed fix: Replace with two deterministic cases with hard-coded expected strings —
     (a) percent-encoded `https://example.com/foo%28bar%29` (spec-unambiguous);
     (b) a raw `)` case where the expected extractor substring is documented from CommonMark spec §6.3 and hard-coded, not computed.
     Keep an AST sanity assertion in a separate test if desired, but the pass contract must not be derived from the code under test.

2. **No RST bare-URL (standalone URL in prose) unit test (unchanged from r3/r4/r5)**
   - Description: Spec §3-2 prescribes `reference.refuri` for RST; docutils emits `nodes.reference` for standalone URLs in running text (e.g., `詳細は https://foo.example を参照`). `verify.py:399-402` relies on this promotion, but no UT pins the path. Inline-literal backtick-trim is tested (`test_verify.py:761-765`); bare-URL promotion is not. A docutils-level regression in standalone-URL recognition would be silent.
   - Proposed fix: Add `test_pass_rst_bare_url_collected` (URL appears as bare text in source and present in JSON → PASS) and `test_fail_rst_bare_url_missing` (same source, URL absent from JSON → FAIL with `[QL2]`). Locks the `reference.refuri` bare-URL promotion path at the QL2 boundary.

### Low Priority

3. **Duplicate-handling test exercises only the trivially-passing side (unchanged from r3/r4/r5)**
   - Description: `test_pass_duplicate_url_reported_once` (`test_verify.py:718-723`) puts the URL into JSON — "reported once" is vacuously satisfied; the `seen` dedup guard at `verify.py:437-442` is never exercised. Removing that guard would not break this test.
   - Proposed fix: Add a sibling test — URL appears twice in source, absent from JSON — and assert `sum(1 for i in issues if "[QL2]" in i) == 1`. This actually tests the dedup logic.

4. **No Visitor-level unit test for MD autolink (unchanged from r3/r4/r5)**
   - Description: `tools/rbkc/tests/ut/test_md_ast_visitor.py` covers inline `[text](url)` collection, but no dedicated Visitor-layer assertion for CommonMark autolink `<https://...>`. The integration test `test_fail_md_autolink_url_missing` (`test_verify.py:790-795`) covers it end-to-end, but a Visitor-layer assertion pins the behaviour at the lowest layer and is cheaper to diagnose on markdown-it drift.
   - Proposed fix: Add `assert md_ast_visitor.extract_document(md_ast.parse("<https://x.example>")).external_urls == ["https://x.example"]`.

## Positive Aspects

- **Zero regex URL extraction in QL2 paths.** Repo-wide grep for `_URL_RE`, `findall.*http`, `re.(search|match|findall).*http` under `tools/rbkc/scripts/` returns no matches. AST-only principle strictly upheld at `verify.py:383-415`, `scripts/common/md_ast_visitor.py`, `scripts/common/rst_ast_visitor.py`.
- **`_source_urls` cleanly delegates to a single AST per format** (`verify.py:383-415`). RST: `doctree.findall(nodes.reference)` filtered on `refuri.startswith(("http://", "https://"))` (`verify.py:399-402`). MD: `md_ast_visitor.extract_document(...).external_urls` (`verify.py:410-413`). No drift risk — single source of truth per format.
- **CommonMark autolink auto-covered.** markdown-it emits `link_open` for `<https://...>`; captured by the existing `link_open` handler with no special case. Locked by `test_fail_md_autolink_url_missing`.
- **http vs https correctly distinguished.** Exact-string substring check (`verify.py:442`); `test_fail_md_http_vs_https_distinguished` (`test_verify.py:826-833`) confirms scheme substitution FAILs.
- **CJK trailing punctuation not absorbed.** `test_pass_md_url_followed_by_japanese_punct_not_absorbed` (`test_verify.py:818-824`) locks AST boundary behaviour. The classic regex-boundary bug is structurally impossible.
- **Substitution-body URLs excluded.** `test_pass_rst_substitution_only_url_skipped` (`test_verify.py:767-775`) keeps source-side collection aligned with converter drops — no spurious FAIL.
- **Query + fragment preserved byte-exact.** `test_pass_md_url_with_query_and_fragment` (`test_verify.py:797-802`) covers `?x=1&y=2#frag` intact.
- **RST inline-code trailing backtick trimmed.** `test_pass_rst_inline_code_url_trailing_backtick_trimmed` (`test_verify.py:761-765`).
- **All 18 QL2 unit tests pass**; full UT suite **218 / 218** passes (up from 216 in r5).
- **v6 runtime verify PASS** (`bash rbkc.sh verify 6` → `All files verified OK`).

## Recommendations

- Apply Medium-priority fixes (de-circularize parens test; add RST bare-URL PASS / FAIL pair) before declaring 100% AST-path coverage. They have now been flagged in r3, r4, r5 and r6 — four consecutive reviews with no action.
- Apply Low-priority fixes opportunistically (few lines each); they close real blind spots in dedup and Visitor-layer autolink.
- Spec annotation to §3-2: "MD `link_open[href]` subsumes both inline `[text](url)` and CommonMark autolink `<url>`" — prevents future readers from adding a redundant autolink extractor.
- Optional: property-style test over a curated URL list (query, fragment, CJK boundary, parens, port, IPv6-literal, percent-encoding) asserting byte-exact round-trip through `_source_urls`.

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source) — QL2 at lines 378-444
- `tools/rbkc/scripts/common/md_ast.py` (source)
- `tools/rbkc/scripts/common/md_ast_visitor.py` (source) — `link_open` handler
- `tools/rbkc/scripts/common/rst_ast_visitor.py` (source)
- `tools/rbkc/tests/ut/test_verify.py` (tests) — `TestVerifyFileQL2` at 700-833
- `tools/rbkc/tests/ut/test_md_ast_visitor.py` (tests)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` (spec) — §3-2 at lines 228-263

## Runtime Evidence

- `pytest tests/ut/test_verify.py::TestVerifyFileQL2 -q` → **18 passed in 0.11s**
- `pytest tests/ut -q` → **218 passed in 0.84s** (up from 216 in r5)
- `bash rbkc.sh verify 6` → `All files verified OK`
- `grep -rn '_URL_RE\|findall.*http\|re\.(search|match|findall).*http' tools/rbkc/scripts/` → **no matches**

## Bias-Avoidance Notes

- Spec is the authority. Runtime PASS is weighted low: it only demonstrates current JSON and current QL2 are self-consistent, not that QL2 is spec-complete.
- Medium #1 (circular parens) re-flagged for the fourth consecutive round. Asserting code-under-test output against itself is structurally incapable of detecting regressions in that code. Current green status does not reduce the validity of the finding.
- Medium #2 (RST bare-URL) re-flagged on spec §3-2 grounds — docutils' standalone-URL recognition is a silent dependency of QL2 correctness and deserves an explicit test lock, independent of current runtime state.
- No code modifications made (review-only, per instructions).
