# QL2 Bias-Avoidance Review (Z-1 r7)

Target: `check_external_urls` / `_source_urls` in `tools/rbkc/scripts/verify/verify.py`
Spec: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2 (QL2)
Tests: `tools/rbkc/tests/ut/test_verify.py` → `TestVerifyFileQL2`

Format: Findings / Observations only. No priority, no rating (ゼロトレランス — binary).

---

## Findings

### F1. Circular expected value in parens URL test

Spec §3-2:
> QL2（外部リンク）: ソース AST から `http://` / `https://` で始まる URL を AST ノード属性として列挙し、URL 文字列が JSON content 内に完全一致で含まれているかを確認する。

`test_pass_md_url_with_parentheses_in_path` (test_verify.py:804-816):

```python
from scripts.common import md_ast, md_ast_visitor
parts = md_ast_visitor.extract_document(md_ast.parse(src))
assert parts.external_urls, "sanity: AST must expose the URL"
expected = parts.external_urls[0]
data = {"id": "f", "title": "T", "content": f"link {expected}", ...}
assert self._check_ql2(src, data, "md") == []
```

The JSON content is built from `parts.external_urls[0]` — whatever the
AST currently returns. If `md_ast_visitor` regresses and returns
`https://example.com/foo(bar` (truncated at `)`), the test still
passes because the truncated string is placed into JSON and found. The
test verifies self-consistency, not spec conformance. The spec-derived
oracle is the source-literal `https://example.com/foo(bar)`; the test
must pin that literal, not the AST output.

**Proposed fix**: replace `expected = parts.external_urls[0]` with the
source literal `https://example.com/foo(bar)` and put that literal in
JSON. Add a paired FAIL test where JSON contains a truncated form
(`.../foo(bar`) — spec requires 完全一致, so this must FAIL.

---

### F2. Substitution-body URL exclusion — no explicit AST-attribute check

Spec §3-2:
> RST の `.. |sub| raw:: html` substitution body 内 URL も `raw` node として AST に現れるため、対象から除外する場合は AST ノードの属性で判定する

`_source_urls` (verify.py:399-402):

```python
for ref in doctree.findall(nodes.reference):
    refuri = ref.get("refuri", "")
    if refuri.startswith(("http://", "https://")):
        urls.append(refuri)
```

Exclusion happens only *incidentally*: `raw:: html` nodes contain HTML
as an opaque string, so docutils does not parse their `<a href="...">`
into `reference` nodes, and `findall(nodes.reference)` therefore never
sees them. There is no explicit property/ancestor check as spec
prescribes (「AST ノードの属性で判定」).

The hidden failure mode: a substitution definition that produces
reference nodes — e.g. `.. |x| replace:: see \`text <https://url>\`_` —
is parsed by docutils into a `substitution_definition` subtree
containing a real `reference` node with `refuri`. `findall` is recursive
and walks into `substitution_definition`, so that URL IS collected.
If the substitution is never referenced (`|x|` unused), the URL does
not appear in JSON content, producing a spurious QL2 FAIL.

Existing test `test_pass_rst_substitution_only_url_skipped` covers only
the `raw:: html` case, not the `replace::` + embedded `<url>` case.

**Proposed fix**: either (a) add an explicit ancestor-check that skips
any `reference` under a `substitution_definition` that is not referenced
in the rendered content, matching the spec wording; or (b) document in
verify.py that the `raw:: html` case is handled by docutils tree shape
and add a test for the `replace::`+embedded-URL case to pin that the
current behaviour is known and acceptable. Option (a) is closer to the
spec.

---

### F3. CommonMark autolink — PASS counterpart missing

Spec §3-2:
> Markdown: `link_open` トークンの `href` 属性、および CommonMark autolink (`<http://…>`) の `refuri`

Only `test_fail_md_autolink_url_missing` exists. There is no matching
PASS test where the autolinked URL is present in JSON. A regression
where autolinks are silently dropped from `external_urls` would make
the FAIL case still FAIL (vacuous pass) but would also not be caught
in a hypothetical "should detect" scenario. Symmetric PASS+FAIL is
required to prove the check is bi-directional.

**Proposed fix**: add `test_pass_md_autolink_url_present` where JSON
content contains the autolinked URL → expect no QL2 issue.

---

### F4. RST URL-with-parens coverage gap (Javadoc anchor)

verify.py:478 comments:
> URL may contain one level of balanced parens (common in Javadoc anchors like `#findAll(java.lang.Class)`).

This comment lives on `_norm` (QC path), but the concern applies to
QL2 too — RST commonly embeds Javadoc URLs like
`https://…/Class.html#method(java.lang.String)`. No QL2 test covers
a bare RST URL with parens in the path or an RST `text <url>`_
reference whose URL contains parens. The only parens test is MD, and
F1 shows it is circular.

**Proposed fix**: add an RST QL2 test using
`` `Javadoc <https://example.com/Class.html#m(java.lang.String)>`_ ``,
pinning the source-literal URL in JSON for PASS and a truncated form
for FAIL.

---

### F5. http vs https test ensures mismatch — but no "extra char" FAIL

`test_fail_md_http_vs_https_distinguished` pins scheme mismatch.
Missing: a test where JSON contains the URL with a trailing character
appended (`https://example.com/a.`) and source has the bare URL —
the implementation's `url in json_text` substring check would still
PASS this (correct behaviour, since substring containment is what
spec §3-2 mandates), but the symmetric case — JSON has `https://…/` and source
has `https://…` (trailing slash mismatch) — is a real regression
vector for the AST extractor leaking trailing slashes or stripping
them. No test pins this direction.

**Proposed fix**: add `test_fail_md_trailing_slash_distinguished`
where source has `https://example.com/a` and JSON has
`https://example.com/a/` → must FAIL (exact string not contained).

---

## Observations

- **JSON-side substring search**: `url in json_text` — correct per
  spec ("完全一致で含まれているか"). No regex, no boundary issue. Good.
- **`_all_text` join**: parts joined with `\n`, which is URL-unsafe
  (cannot appear inside a URL), so false positives via cross-field
  concatenation are impossible. Good.
- **Duplicate dedup**: `seen` set prevents repeated reports for the
  same URL. Covered by `test_pass_duplicate_url_reported_once`.
- **`xlsx` / no_knowledge early-exit**: both covered
  (`test_pass_xlsx_skipped`, `test_pass_no_knowledge_content_skipped`).
- **Target definition URL exclusion** (`.. _Name: https://…`):
  covered by `test_pass_rst_target_def_url_excluded`, relies on
  converter dropping the URL. Acceptable as long as QC1 catches
  content drift elsewhere.
- **Scheme filter**: `mailto:` / `tel:` / `javascript:` / `#anchor`
  correctly excluded in `md_ast_visitor` (line 413). Not tested at
  QL2 level but exclusion is structural.

---

## Summary

5 findings. F1 (circular parens test) and F2 (substitution exclusion
not implemented per spec wording) are the two highest-signal gaps.
F3–F5 are symmetry / coverage gaps that ゼロトレランス requires closed.
