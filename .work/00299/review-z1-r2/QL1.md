# QL1 Review — Internal Link Accuracy

**Reviewer**: QA Engineer (independent, Z1-R2)
**Date**: 2026-04-23
**Target**: QL1 per `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2
**Scope**: `check_source_links` + `TestCheckSourceLinks` + v6 runtime

## Overall Assessment

**Rating**: 3 / 5 — Acceptable with notable gaps

The implementation covers the common AST node shapes (`:ref:` role, `figure`, `image`, MD `link_open`, MD inline `image`) and the unit tests exercise the expected PASS/FAIL pairs plus filename fallback. The `literal_block` exclusion is clearly documented and matches the spec. However, the implementation misses a node class the spec table explicitly names — `reference` with `refid` / `refname` and no `refuri` (RST named references like `Usage_`) — and the test suite therefore has no coverage for that shape. There are also edge cases in MD link classification (non-HTTP schemes such as `mailto:` / `ftp:` / fragment-only `#sec`) that are not evaluated.

## Condition 1 — Implementation

File: `tools/rbkc/scripts/verify/verify.py` lines 973–1116.

**Covered node types**

| Spec row | Impl location | Status |
|---|---|---|
| RST `:ref:` display-text form | `verify.py:1003–1024` | Covered |
| RST `:ref:` bare-label form (label_map lookup) | `verify.py:1025–1032` | Covered |
| RST `figure` caption with filename fallback | `verify.py:1034–1051` | Covered (uses `_has_visible_text` for inline-only captions) |
| RST `image` alt with filename fallback | `verify.py:1053–1063` | Covered |
| RST `literal_block` (literalinclude) | `verify.py:1065–1066` (deferred to QC1/QC2) | Documented exclusion consistent with spec note |
| MD `link_open` non-external | `verify.py:1077–1084` (via `md_ast_visitor.internal_links`) | Partially covered (see gap below) |
| MD inline `image` alt/filename | `verify.py:1087–1095` | Covered |

**AST-only principle**: The function operates strictly on AST nodes from `rst_ast.parse` and `md_ast.parse`. The only regex use is inside `_has_visible_text` (`verify.py:1110–1116`) and it runs on the *extracted caption text* (an AST `astext()` result), not on the raw source — this is consistent with the §3-2 prohibition on "line-based regex of the source".

**`_has_visible_text` correctness**: Spot-checked with `[注意事項]` (ordinary bracketed text, no trailing `_`) — retained as visible. `Sample [1]_ caption` reduces to `Samplecaption`, still visible. `[1]_` alone reduces to empty — filename fallback kicks in as expected. The helper is implemented correctly for the documented cases.

**Gap — RST `reference` node with `refid` / `refname` (no `refuri`)**

Spec table §3-2 first row explicitly lists `reference` (`refid` / `refname`, refuri なし) as an extraction target, distinct from `:ref:`. The implementation only iterates `nodes.inline` with `role-ref` class (`verify.py:1005–1011`); it does not iterate `nodes.reference` and filter by `refuri is None`.

Empirical confirmation: an RST snippet `See Usage_ for details.` with an internal target `.. _usage:` produces `reference(refid='usage', refname=None, refuri=None)`. The current impl ignores these nodes entirely, so a named reference whose resolved title is absent from JSON will not be flagged by QL1.

**Gap — MD link classification edge cases**

`md_ast_visitor.py:410` classifies only `http://` / `https://` as external; anything else (including empty href, `#anchor`, `mailto:`, `ftp:`, `javascript:`) is pushed into `internal_links`. For `mailto:foo@bar` the "link text" may be the email itself, which trivially appears or not in JSON — this is noise rather than a real QL1 signal. Not a correctness hole for the current v6 corpus, but worth noting since the spec's "non-external href" wording is ambiguous and the current filter conflates "internal" with "non-http(s)".

## Condition 2 — Unit Tests

File: `tools/rbkc/tests/ut/test_verify.py` lines 1109–1247, `TestCheckSourceLinks`.

**Coverage matrix vs. spec rows**

| Spec row | FAIL test | PASS/fallback test |
|---|---|---|
| RST `:ref:` display text | `test_fail_rst_ref_display_text_missing` (L1128) | `test_pass_rst_ref_display_text_in_json` (L1123) |
| RST `:ref:` bare label via label_map | `test_fail_rst_ref_plain_label_title_missing` (L1140) | `test_pass_rst_ref_plain_label_resolved` (L1134) |
| RST `reference` (refid/refname) | **Missing** | **Missing** |
| RST `figure` caption | `test_fail_rst_figure_caption_missing` (L1178) | `test_pass_rst_figure_caption_in_json` (L1189) |
| RST `figure` inline-only caption → filename | `test_fail_rst_figure_inline_only_caption_fallback_to_filename` (L1199) | — |
| RST `image` alt | `test_fail_rst_image_alt_missing` (L1212) | — |
| RST `image` without alt → filename | `test_fail_rst_image_without_alt_falls_back_to_filename` (L1222) | — |
| RST `literal_block` (literalinclude) | Not tested (spec defers to QC1/QC2) | — |
| MD internal link text | `test_fail_md_internal_link_text_missing` (L1159) | `test_pass_md_internal_link_text_in_json` (L1154), external skipped `test_pass_md_external_link_skipped` (L1165) |
| MD image alt | `test_fail_md_image_alt_missing` (L1231) | `test_pass_md_image_alt_in_json` (L1243) |
| MD image without alt → filename | `test_fail_md_image_without_alt_falls_back_to_filename` (L1237) | — |

**Cross-document :ref: via label_map**: `test_pass_rst_ref_plain_label_resolved` and `test_fail_rst_ref_plain_label_title_missing` both inject a `label_map` from outside the parsed source, which is exactly the cross-document scenario. `test_pass_rst_ref_unknown_label_skipped` documents the "label unknown → skip" behaviour.

**literal_block acknowledgement**: Both code (`verify.py:1065–1066`) and spec (`§3-2` table row: "NOTE: literal_block content is covered by QC1/QC2") align. No test in `TestCheckSourceLinks` for literal_block, which is consistent with the documented exclusion. The QC1/QC2 coverage should be reviewed separately — it is out of scope for this QL1 review.

**Circular-test check**: The tests construct RST/MD source strings manually, parse them through the normal AST pipeline, and assert the expected QL1 message. `json_full` is built from a small `_data(...)` dict with a known `content` string. There is no dependence on RBKC's actual output (converters/resolver are not invoked). Assertions use literal Japanese strings (`"使い方"`, `"サンプル画像の説明"`, `"badge.png"`, `"diagram.png"`, `"会社ロゴ"`) that derive from the input fixtures, not from verify's internal representation. **No circular tests detected.**

**Gap — no test for `nodes.reference` (refid/refname) path**

Because the implementation does not handle named references, the test suite correspondingly lacks any fixture for them. Two tests should exist at minimum:

- FAIL: RST source with `.. _usage:` target + `Usage_` reference in body, JSON missing the resolved title → expect QL1 issue mentioning the resolved title
- PASS: same source with JSON containing the resolved title → expect no QL1 issue

**Gap — no test for display-text form with cross-document label**

The display-text branch (`display and display not in json_full`) checks the display string directly and does not consult `label_map`. A targeted PASS/FAIL pair using `:ref:\`link text <cross_doc_label>\`` where `cross_doc_label` is in `label_map` would confirm that the display text — not the resolved title — is what must appear in JSON. Spec §3-2 is compatible with this, but the test is missing.

**Low-priority gap — MD image title attribute**

Spec row for MD inline image lists "alt / title / src のファイル名". The impl uses alt → filename; `title` is not consulted. `md_ast_visitor` also does not appear to record `title`. If a future MD source uses `![](path "title")` with meaningful title, QL1 silently skips it. Minor, but it is in the spec table.

## Condition 3 — v6 Runtime

- `cd tools/rbkc && python -m pytest -q` → **190 passed** in 3.36 s
- `./rbkc.sh verify 6` → **All files verified OK**
- `pytest tests/ut/test_verify.py::TestCheckSourceLinks -q` → **17 passed** in 0.15 s

Runtime is clean. v6 pass is weak evidence only — the gaps above would not be exercised by the current v6 corpus if it happens not to use `nodes.reference` named refs.

## Key Issues

### High

**H1. RST `reference` (refid/refname, no refuri) not implemented**
- Description: Spec §3-2 table row 1 explicitly names this node shape. `check_source_links` only iterates `nodes.inline` with `role-ref` class; it never reads `nodes.reference` with `refuri is None`. Empirically reproduced on a minimal source with `.. _usage:` + `Usage_` — node is present with `refid='usage'` and the function emits no QL1 issue regardless of JSON content.
- Proposed fix: After the `:ref:` loop, iterate `doctree.findall(nodes.reference)`; skip nodes with `refuri` (those are QL2); for nodes with `refid` or `refname`, look up the resolved title via `label_map` (refname) or by walking the doctree for a target with matching id (refid); emit QL1 when the expected text/title is absent from JSON. Add the corresponding PASS/FAIL tests.

### Medium

**M1. No test for cross-document `:ref:` display-text form**
- Description: The display-text branch is not exercised with `label_map` populated. A future refactor could accidentally start using `label_map` for display-text form (changing which string is compared) and no test would catch it.
- Proposed fix: Add `test_pass_rst_ref_cross_doc_display_text` and `test_fail_rst_ref_cross_doc_display_text_missing` using `:ref:\`使い方 <cross_doc_label>\`` with `label_map={"cross_doc_label": "Other Title"}`, asserting that the display text "使い方" — not "Other Title" — is what QL1 checks.

### Low

**L1. MD `link_open` non-http(s) classification is coarse**
- Description: `md_ast_visitor.py:410` sends all non-`http(s)` hrefs to `internal_links`, including `mailto:`, `ftp:`, `#anchor`, empty href. QL1 then checks the link text against JSON, which may produce spurious failures for link patterns that aren't really "internal links to documents".
- Proposed fix: Tighten the classifier to treat only relative paths and site-local absolute paths as internal, or document explicitly that QL1 treats all non-external anchors the same.

**L2. MD inline image `title` attribute not considered**
- Description: Spec row lists "alt / title / src ファイル名". `title` is dropped by the visitor.
- Proposed fix: Extend `md_ast_visitor.images` to return `(alt, src, title)` and have QL1 fall through alt → title → filename.

**L3. `literal_block` deferral not mirrored in test comment**
- Description: Code comment (`verify.py:1065–1066`) is good. Adding a one-line test comment in `TestCheckSourceLinks` ("literal_block is covered by QC1/QC2 — see §3-2") would make the deliberate absence discoverable by future maintainers.

## Positive Aspects

- Clean AST-only extraction; no regex scan of raw source for link discovery.
- `_has_visible_text` correctly distinguishes RST inline-only captions from ordinary prose in brackets; filename fallback path is exercised by a dedicated test.
- `literal_block` exclusion is documented in both spec and code.
- `no_knowledge_content` short-circuit (`verify.py:985–986`) has a PASS test (`test_pass_no_knowledge_content_skipped`).
- External link skip in MD has an explicit PASS test (`test_pass_md_external_link_skipped`).
- Unit tests are non-circular: fixtures are hand-crafted sources and hand-crafted JSON content; RBKC converters are not involved.

## Recommendations

1. Close the `nodes.reference` (refid/refname) gap — this is the most concrete spec-to-impl deviation and the only one that could let a real QL1 defect ship undetected.
2. Add the two cross-document display-text tests described in M1.
3. Consider whether the MD visitor's link classification should become more precise; if not, add a comment in the spec or in `md_ast_visitor.py:410` pinning the current behaviour so it's not treated as a bug later.

## Files Reviewed

- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` (spec §3-2)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py` (check_source_links, _has_visible_text)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/common/md_ast_visitor.py` (internal/external link classification)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/common/rst_ast.py` (:ref: role registration, lines 28–81)
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py` (TestCheckSourceLinks, lines 1105–1247)
