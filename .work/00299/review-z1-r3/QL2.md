# Expert Review: QA Engineer — QL2 (外部リンク)

**Date**: 2026-04-23
**Reviewer**: Independent QA Engineer (bias-avoidance stance)
**Scope**: QL2 external link verification, per `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2
**Spec authority**: AST-only extraction — RST `reference.refuri`, MD `link_open[href]` (which also covers CommonMark autolinks). Regex-based URL extraction explicitly forbidden.

## Overall Assessment

**Rating**: 4.5 / 5
**Summary**: Implementation adheres strictly to the AST-only principle; regex URL extraction is fully eliminated from QL2 paths. Unit tests cover the Z-1 gap-fill edge cases (http/https distinction, CJK trailing punctuation, query/fragment, parentheses, autolink, substitution-body exclusion). One minor circularity and one spec-coverage gap noted.

## Key Issues

### High Priority

None found.

### Medium Priority

1. **Partial circular assertion in parentheses test**
   - Description: `test_pass_md_url_with_parentheses_in_path` (`tests/ut/test_verify.py:714-726`) derives the expected URL by calling the same AST extractor (`md_ast_visitor.extract_document(...).external_urls[0]`) that QL2 itself uses, then asserts JSON containing that string passes. This does not test behaviour against the spec — it only asserts self-consistency (AST round-trip). If markdown-it changes its parse of `https://example.com/foo(bar)` (e.g., includes or excludes the trailing `)`), the test still passes because JSON is built from the same AST output.
   - Proposed fix: Split into two deterministic assertions anchored on markdown-it's documented CommonMark behaviour — one for a URL with percent-encoded parens (`%28`/`%29`) where full URL is expected, and one for a raw `)` case with a hard-coded expected URL substring (the spec-correct slice). Keep the AST sanity assertion as a precondition, but the pass/fail expectation must not be derived from the code under test.

2. **No RST autolink / bare-URL coverage**
   - Description: Spec §3-2 states RST uses `reference.refuri`. docutils emits `nodes.reference` for standalone URLs (e.g., bare `https://foo.example` in body), but there is no unit test verifying this path. RST inline-literal backtick trim is covered, but bare-URL promotion is not.
   - Proposed fix: Add `test_pass_rst_bare_url_collected` (source: `詳細は https://bare.example/x を参照` with JSON containing the URL → PASS) and `test_fail_rst_bare_url_missing` (same source, JSON without URL → FAIL). Confirms docutils `reference.refuri` path actually captures bare URLs, not just explicit `\`text <url>\`_` forms.

### Low Priority

3. **Duplicate-handling test asserts only the "both-present" case**
   - Description: `test_pass_duplicate_url_reported_once` (`test_verify.py:628-633`) uses JSON that *contains* the URL, so the "reported once" claim is vacuously satisfied — the loop's `seen` set is never exercised under failure.
   - Proposed fix: Add a sibling case where the URL appears twice in source but is absent from JSON; assert exactly one `[QL2]` issue is produced (not two).

4. **No explicit Visitor-level unit test for MD autolink**
   - Description: `test_md_ast_visitor.py:161` covers inline link collection into `external_urls`, but there is no dedicated Visitor test for the CommonMark autolink form `<https://...>`. The QL2 end-to-end test (`test_fail_md_autolink_url_missing`, `test_verify.py:700-705`) covers it integrationally, but a Visitor-level test pins the behaviour at the lowest layer.
   - Proposed fix: Add one Visitor test asserting `<https://x>` yields `external_urls == ["https://x"]`.

## Positive Aspects

- **No regex URL extraction anywhere in QL2 paths**: `grep` across `scripts/` for `_URL_RE`, `re\.findall.*http`, `re\.search.*http` returns zero matches. AST-only principle strictly upheld (`verify.py:337-367`, `md_ast_visitor.py:394-415`, `rst_ast_visitor.py:631-647`).
- **`_source_urls` cleanly delegates** to docutils `findall(nodes.reference)` for RST and to `md_ast_visitor.extract_document(...).external_urls` for MD — no parser config drift risk (single source in `md_ast.py`).
- **CommonMark autolink is automatically covered** by markdown-it emitting `link_open` tokens for `<https://...>` — the Visitor's `link_open` handler (`md_ast_visitor.py:394-411`) captures it without special-casing.
- **Exact-match substring check** (`verify.py:396`) avoids the classic regex boundary bug: http vs https distinction is naturally correct (test confirmed, `test_verify.py:736-743`).
- **Substitution-body URLs are excluded** from source-side collection via converter-side handling (`test_pass_rst_substitution_only_url_skipped`, `test_verify.py:677-685`) — consistent with "URLs actually visible to readers".
- **All 18 QL2 unit tests pass**; full UT suite 194/194 passes.
- **v6 runtime verify PASS** (`bash rbkc.sh verify 6` → `All files verified OK`).

## Recommendations

- Apply Medium-priority fixes (circular parens test + RST bare-URL coverage) before claiming "100% AST-path coverage".
- Consider documenting in the spec (§3-2) that "MD `link_open[href]` subsumes both inline `[text](url)` and CommonMark autolink `<url>`" so future readers do not add redundant autolink extractors.
- Consider adding a property-style test: for a hand-curated list of URLs (with query/fragment/CJK boundary/parens/port/IPv6-literal/percent-encoded), assert round-trip through the extractor preserves byte-exact URL. Low cost, high confidence.

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source code) — QL2 core at lines 333-398
- `tools/rbkc/scripts/common/md_ast.py` (source code) — MD parser wrapper
- `tools/rbkc/scripts/common/md_ast_visitor.py` (source code) — `link_open` handler at 394-415
- `tools/rbkc/scripts/common/rst_ast_visitor.py` (source code) — `inline_reference` at 631-647
- `tools/rbkc/tests/ut/test_verify.py` (tests) — `TestVerifyFileQL2` at 605-743
- `tools/rbkc/tests/ut/test_md_ast_visitor.py` (tests) — external_urls at 161-163
- `tools/rbkc/docs/rbkc-verify-quality-design.md` (spec) — §3-2

## Runtime Evidence

- `pytest tests/ut/test_verify.py::TestVerifyFileQL2` → 18 passed
- `pytest tests/ut/` → 194 passed
- `bash rbkc.sh verify 6` → `All files verified OK`

## Bias-Avoidance Notes

- Spec was treated as authoritative; v6 PASS is explicitly discounted as weak evidence (it only proves current output is self-consistent, not that QL2 detection is complete).
- Circular test flagged above (Medium #1) — asserting AST output against itself does not verify spec conformance.
- No code modifications made (review-only, per instructions).
