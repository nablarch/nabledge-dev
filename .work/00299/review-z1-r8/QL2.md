# QL2 Bias-Avoidance Review (Z-1 r8)

**Target**: `tools/rbkc/scripts/verify/verify.py` — `check_external_urls`, `_source_urls`
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2 QL2 (lines 265–270)
**Tests**: `tools/rbkc/tests/ut/test_verify.py` — `TestVerifyFileQL2`

## Verdict

**PASS** — no blocking findings.

## Findings

None.

## Observations

### O1. AST-only principle is correctly enforced
Spec clause: *「正規表現でソース全体から URL を抽出することは禁止」*
`_source_urls` extracts from AST attributes only — RST `reference.refuri` via `doctree.findall(nodes.reference)`, MD via `md_ast_visitor.extract_document(...).external_urls` which is populated on `link_open` tokens (verify.py:550–566; md_ast_visitor.py:395–412). No regex scan of raw source. Matches spec §3-2 lines 267–268.

### O2. Substitution-body exclusion uses AST-attribute check
Spec clause: *「raw node として AST に現れるため、対象から除外する場合は AST ノードの属性で判定する」* (§3-2 line 268)
`_in_substitution` walks `node.parent` ancestors and checks `isinstance(cur, nodes.substitution_definition)` (verify.py:538–548). This is the spec-mandated AST-attribute mechanism — not a text-based filter. Test `test_pass_rst_substitution_replace_with_embedded_url_skipped` exercises the `replace::` form which produces a `reference` under `substitution_definition`, and `test_pass_rst_substitution_only_url_skipped` covers the `raw:: html` form.

### O3. Parens URL test is now source-pinned (r7 F1 resolved)
`test_pass_md_url_with_parentheses_in_path` asserts against the literal URL `https://example.com/foo(bar)` written in the source, and `test_fail_md_url_with_parentheses_truncated_in_json` verifies the FAIL path when the JSON truncates at `)`. The oracle is the source literal, not AST output — a truncating extractor regression would be caught by the FAIL test. Circularity resolved.

### O4. Autolink has both FAIL and PASS coverage (r7 F3 resolved)
`test_fail_md_autolink_url_missing` and `test_pass_md_autolink_url_present` form a bidirectional pair over the CommonMark `<https://…>` autolink form. The FAIL test is not vacuous.

### O5. Trailing-slash distinction covered (r7 F5 resolved)
`test_fail_md_trailing_slash_distinguished` pins that `https://example.com/a/` is not a substring of a JSON that only contains `https://example.com/a`. Substring-presence check (verify.py:595) correctly distinguishes — guards against slash-stripping regressions.

### O6. RST parens (Javadoc anchor) covered (r7 F4 resolved)
`test_pass_rst_url_with_parens_javadoc_anchor` exercises `https://example.com/Class.html#m(java.lang.String)` via `` `text <url>`_ `` inline form. This is the most common v6-corpus shape; covered.

### O7. Scheme distinction (http vs https)
`test_fail_md_http_vs_https_distinguished` proves substring check does not conflate schemes. Reasonable (substring of `https://...` contains `s://...` but not `http://...` as a standalone substring since `https` superset match is fine — the test asserts the http-source URL is NOT substring of https-only JSON, which is correct).

### O8. xlsx / no_knowledge / no-URL early-outs
All three early-return branches (verify.py:580, 584) have explicit PASS tests (`test_pass_xlsx_skipped`, `test_pass_no_knowledge_content_skipped`, `test_pass_no_source_urls`). Branch coverage is complete.

## Scope Notes

- QL2 implementation is fully AST-driven on both RST and MD sides and respects the spec §3-2 clauses verbatim.
- Test suite covers: happy PASS, missing FAIL, dedup, xlsx skip, no_knowledge skip, section-level nesting, inline-code trailing backtick, both substitution forms (raw::/replace::), MD inline link, autolink (FAIL+PASS), query+fragment, parens in path (PASS+FAIL), CJK-punct boundary, scheme distinction, trailing-slash distinction, RST Javadoc-anchor parens.
- No circular tests remain. No regex-based extraction remains. Substitution exclusion is AST-attribute-based per spec.
