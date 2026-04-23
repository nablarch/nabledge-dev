# QL2 bias-avoidance QA review — Z-1 r9

Target: `scripts/verify/verify.py::check_external_urls`, `_source_urls`
Spec: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2
Tests: `tests/ut/test_verify.py::TestVerifyFileQL2`

## Findings

(No findings. No spec clause is violated by the reviewed implementation or tests.)

## Observations

### O1. `_all_text` is flat; spec does not require nested-section scanning

Spec §3-2 line 263 requires the URL to appear in "JSON content". Spec §3 line 161
enumerates JSON text fields as "top-level title / top-level content / 各セクション
title / 各セクション content" — a flat, single-level list. `_all_text` mirrors
that contract exactly. This is consistent with spec, not a gap. Noted here only
because a future schema change that introduces nested subsections would silently
bypass QL2 unless `_all_text` is extended in lockstep.

Spec clause (line 161):
> 抽出順序は「top-level title → top-level content → sections[0].title → sections[0].content → sections[1].title → ...」

### O2. Duplicate-URL dedup suppresses repeated reports, not repeated checks

`check_external_urls` dedups via `seen` before the containment test, so a URL
that appears N times in source produces at most one FAIL line. Spec §3-2 says
"URL 文字列が JSON content 内に完全一致で含まれているかを確認する" — a presence
check, not a count check. Dedup is consistent with spec. Noted because the
corresponding behaviour must not be misread as "first-occurrence-only" if spec
ever moves to count-based matching.

Spec clause (line 263):
> URL 文字列が JSON content 内に完全一致で含まれているかを確認する

### O3. RST target-directive URLs (`.. _Name: https://...`) are excluded via node-type selection, not via a substitution check

`_source_urls` iterates `nodes.reference` only. Bare target definitions are
`nodes.target` and never enter the iteration; the `_in_substitution` walk is not
what filters them. `test_pass_rst_target_def_url_excluded` relies on this, and
its docstring ("dropped by converter") does not match the actual mechanism
(docutils emits `target`, not `reference`, for the directive form — the URL is
never in the candidate set to begin with). Mechanism-vs-test-comment drift only;
spec requirement is met.

Spec clause (line 265):
> RST: `reference` node の `refuri` 属性

### O4. CommonMark autolink coverage is indirect — autolinks surface as `link_open`, not as a separate AST node

Spec §3-2 line 266 distinguishes "`link_open` トークンの `href` 属性、および
CommonMark autolink (`<http://…>`) の `refuri`". In markdown-it-py output,
autolinks are emitted as `link_open`/`text`/`link_close` with
`href=https://...`; there is no distinct `refuri` field. `md_ast_visitor`
collects from `link_open[href]` and therefore captures autolinks through the
same branch. The behaviour is spec-conformant; the spec's wording implies two
paths where the parser provides one.

Spec clause (line 266):
> Markdown: `link_open` トークンの `href` 属性、および CommonMark autolink (`<http://…>`) の `refuri`

### O5. `return []` on AST parse exception is a silent fallback

Both the RST and MD branches wrap `parse()` in `try/except Exception: return []`.
Spec §3-2 is silent on error handling for parser failures, and rbkc.md forbids
silent skips. If source fails to parse, no URLs are extracted and QL2 cannot
FAIL — which hides the entire quality observation for that file. Spec does not
explicitly address this case, so recorded as an observation, not a finding.

Relevant project rule (rbkc.md):
> silent skip 禁止。ゼロトレランスに基づき、壊れたファイルは検出対象とする
(context: applied to QO4 in spec §3-3; QL2 has no equivalent explicit clause)

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (lines 552–631)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/common/md_ast_visitor.py` (external_urls collection, lines 395–412)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (TestVerifyFileQL2, lines 1052–1237)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` (§3-2, lines 228–268)
