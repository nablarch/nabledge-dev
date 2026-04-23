# Expert Review: QA Engineer — QL1 (内部リンク)

**Date**: 2026-04-23
**Reviewer**: Independent QA Engineer (bias-avoidance stance)
**Round**: r4
**Scope**: QL1 internal link verification, per `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2 (lines 232-261), rows: RST `reference` (refid/refname, no refuri), RST `figure`, RST `image`, RST `literal_block` (literalinclude — delegated to QC1/QC2), MD `link_open` (non-external), MD inline `image`.

## Overall Assessment

**Rating**: 3.5 / 5

**Summary**: Implementation covers all six spec-mandated node types via the AST-only path (no regex source scans for links). r3 feedback was partially absorbed — MD scheme filter (`mailto:` / `tel:` / `#anchor`) is now tested (three new passing tests), MD image `title` fallback is implemented and tested, and the named-reference case has two synthetic-AST tests. However, the **r3 High #1 gap is NOT resolved**: empirically verified that real docutils emits `refid` (not `refname`) for v6's named references (0 / 1008 occurrences across 200 v6 files populate `refname`), so the `refname` branch at `verify.py:915-930` is dead code on real input. The synthetic-AST tests still drive only the walk logic, not the parser contract. This is the same circular-test issue r3 flagged, unchanged.

## Key Issues

### High Priority

1. **RST named-reference branch is dead code on real v6 input (r3 High #1 unresolved)**
   - Description: `verify.py:915-930` walks `nodes.reference` filtering on `refname`. Empirical check across 200 v6 RST files via `rst_ast.parse` → `findall(nodes.reference)`: **0 nodes have `refname` set; 1008 have `refid` set**. docutils resolves the `Text_` → target mapping during parsing and emits `refid` (resolved) or `problematic` (unresolved), not `refname`. The two tests at `test_verify.py:1439-1458` and `:1488-1503` hand-build `nodes.reference("", "...", refname="...")` and monkey-patch `rst_ast.parse` to return it — they prove the walker logic works on that hand-built shape but give zero evidence that real RST source reaches the branch. Result: QL1 currently provides **no detection** for RST native named references in v6 — every file silently passes regardless of JSON content.
   - Proposed fix: Replace the two synthesised tests with real-parser tests and align the walker with what docutils actually emits:
     - Add `test_fail_rst_named_reference_via_real_parser_target_missing` — source with `.. _usage:\n\nタイトル\n====\n\n本文 See \`usage\`_.\n`, `label_map={"usage":"利用ガイド"}`, JSON without `利用ガイド` → expect FAIL.
     - Add `test_pass_rst_named_reference_via_real_parser_title_in_json` — same source, JSON containing `利用ガイド` → expect `[]`.
     - Fix `verify.py:915-930` to walk `refid` (resolving via `doctree.ids` / `label_map`) in addition to (or instead of) `refname`. If the refid path yields the target node whose text already appears as a section title handled by QC1, document that overlap with a comment and a PASS test; do not leave the current dead branch.

### Medium Priority

2. **No test for `javascript:` scheme in MD internal-link filter**
   - Description: `md_ast_visitor.py:413` excludes `("mailto:", "tel:", "javascript:", "#")`. Three of those four schemes have tests (`test_pass_md_mailto_link_not_internal`, `test_pass_md_tel_link_not_internal`, `test_pass_md_anchor_only_link_not_internal`). `javascript:` has no test. A future refactor could silently drop `javascript:` from the filter tuple and no test would catch it. Not a content-correctness bug today, but a coverage hole in the filter contract.
   - Proposed fix: Add `test_pass_md_javascript_link_not_internal` — `[クリック](javascript:void(0))` + JSON without "クリック" → expect `[]`. One-liner sibling of the mailto/tel tests.

3. **No test for empty-href MD link (`[text]()`)**
   - Description: `md_ast_visitor.py:413`'s condition `elif href and not href.startswith(...)` excludes empty hrefs (the `href` truthiness check). This is not pinned by any test. An empty-href link is a rare but valid CommonMark construct and the current behaviour (skip) is reasonable, but undocumented. A refactor that rewrites the condition as `elif not href.startswith(...)` (dropping the truthiness guard) would include empty-href links and no test would fail.
   - Proposed fix: Add `test_pass_md_empty_href_link_not_internal` — `[テキスト]()` with JSON lacking "テキスト" → expect `[]`. Pins the current skip policy.

4. **RST `figure` with `:alt:` option but no caption is not tested (r3 Medium #3 carry-over)**
   - Description: Spec §3-2 row 2 defines the fallback as `caption → URI filename`; alt is intentionally not in the chain. `verify.py:964-980` implements exactly this. But no test pins the decision to ignore alt when a figure has `:alt:` set with no caption. If a future change adds alt to the fallback, no test fails; if the current behaviour is actually a spec gap (human reader sees the alt, not the filename), we have no evidence of the trade-off.
   - Proposed fix: Add `test_rst_figure_alt_only_falls_back_to_filename_not_alt` — source `.. figure:: images/diagram.png\n   :alt: 概要図\n` (no caption), JSON with "概要図" but not "diagram.png" → expect FAIL complaining about `diagram.png`. Pins the spec-literal policy. If the user wants alt used as fallback, that becomes a spec amendment + code fix, not incidental drift.

5. **No test confirms `findall` reaches figure/image nested in admonitions / substitution definitions (r3 Medium #4 carry-over)**
   - Description: `doctree.findall(nodes.figure)` is recursive so nested figures are reached in principle, but no test exercises `.. note::` / `.. admonition::` / `.. |sub| image:: ...` containment. For substitution definitions specifically, QL2 excludes substitution-URL raw nodes (spec line 268). If QL1 should apply the same exclusion to substitution-image alt/filename, the current code does NOT — it would FAIL on `.. |logo| image:: logo.png\n   :alt: 会社ロゴ` if neither string is in JSON, regardless of whether the substitution is ever referenced.
   - Proposed fix: Add `test_rst_figure_inside_note_detected` and `test_rst_substitution_image_policy` (either exclude or include with explicit assertion). Decide substitution policy consistently with QL2 line 268.

### Low Priority

6. **No explicit test documenting QL1↔QC1/QC2 hand-off for `literalinclude` (r3 Low #6 carry-over)**
   - Description: `verify.py:994-995` comments "literal_block content is covered by QC1/QC2". No test pins this hand-off. A future refactor that moves QC1/QC2 logic could silently leave literalinclude unchecked.
   - Proposed fix: Add `test_pass_rst_literalinclude_delegated_to_qc` — source containing `.. literalinclude:: foo.py`, JSON containing the code body, assert `check_source_links` returns `[]` with a docstring pointing to QC1/QC2.

7. **Unknown-label skip is indistinguishable from PASS (r3 Low #7 carry-over)**
   - Description: `test_pass_rst_ref_unknown_label_skipped` (`:1336-1340`) asserts `== []`; both "skip unknown" and "resolved and matched" produce `[]`. A reader cannot tell which branch was taken.
   - Proposed fix: Use a sentinel label_map with an unrelated key (e.g., `{"other-label":"Some Title"}`) and JSON without "Some Title"; `[]` then proves the skip branch ran.

## Positive Aspects

- **AST-only principle upheld**: `check_source_links` (`verify.py:874-1026`) drives RST via `rst_ast.parse` + `doctree.findall(nodes.{reference,inline,figure,image})` and MD via `md_ast_visitor.extract_document`. `grep -n "_URL_RE\|_RST_FIGURE_RE\|_RST_REF\|_MD_INTERNAL_LINK_RE"` on `verify.py` returns no hits — no forbidden regex extractors remain.
- **r3 High #2 (MD internal-link filter) addressed**: extractor now excludes `mailto:` / `tel:` / `javascript:` / `#` (`md_ast_visitor.py:413`); three unit tests (`test_pass_md_mailto_link_not_internal`, `test_pass_md_tel_link_not_internal`, `test_pass_md_anchor_only_link_not_internal`) pin mailto / tel / anchor.
- **r3 Medium #5 (MD image title fallback) addressed**: `md_ast_visitor.py:387-391` now captures `(alt, src, title)`; `verify.py:1018-1024` fallback chain is `alt → title → filename`; `test_fail_md_image_title_missing_from_json` exercises the title-only branch.
- **Inline-only caption fallback correctly implemented and tested**: `_has_visible_text` (`:1029-1045`) strips RST inline constructs before fallback; `test_fail_rst_figure_inline_only_caption_fallback_to_filename` pins `[1]_`-only caption → filename fallback.
- **Deduplication** via `seen_link_texts` / `seen_images` / `seen_labels` keeps failure lists clean.
- **External-link exclusion is at the extractor level** (`md_ast_visitor.py:411-412`) — QL1↔QL2 split enforced structurally, not by string matching in the checker.
- **`no_knowledge_content` skip** (`verify.py:886`) avoids false positives on TOC / no-content pages.
- **23 `TestCheckSourceLinks` tests pass** (`pytest tests/ut/test_verify.py::TestCheckSourceLinks -q` → 23 passed, 0.27s).
- **v6 runtime verify**: `bash rbkc.sh verify 6` → `All files verified OK`.

## Recommendations

- **Fix High #1 before claiming QL1 ✅.** v6 PASS is weak evidence here: empirical survey shows `refname` is never populated in real v6 docutils output, so "PASS" means "the dead branch was taken 0 times." This is the r3 concern, still unresolved. Replace synthetic-tree tests with real-parser tests and rewrite the walker to use `refid` resolution (or document and test that QC1's section-title coverage makes the QL1 named-reference check redundant — but that requires explicit test evidence, not silence).
- **Close Medium #2, #3 (javascript / empty href) trivially** — three-line test each — to make the scheme-filter contract testable.
- **Decide Medium #4, #5 (figure alt, substitution-image)** explicitly; either pin the current spec-literal behaviour with tests or amend spec and code. Incidental behaviour is technical debt.
- **Low #6, #7** are documentation-via-test; address when convenient.

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source code) — QL1 at lines 874-1045
- `tools/rbkc/scripts/common/md_ast_visitor.py` (source code) — `internal_links` / `images` collection at 387-418
- `tools/rbkc/scripts/common/rst_ast.py` (source code) — parser wrapper
- `tools/rbkc/scripts/common/labels.py` (source code) — `build_label_map` (spec line 261)
- `tools/rbkc/tests/ut/test_verify.py` (tests) — `TestCheckSourceLinks` at lines 1295-1503
- `tools/rbkc/docs/rbkc-verify-quality-design.md` (spec) — §3-2 lines 228-268

## Runtime Evidence

- `pytest tests/ut/test_verify.py::TestCheckSourceLinks -q` → 23 passed (0.27s)
- `bash rbkc.sh verify 6` → `All files verified OK`
- Empirical docutils survey (200 v6 RST files): 0 `refname`-populated `nodes.reference`, 1008 `refid`-populated — demonstrates the `refname` branch is dead on real input.
- `grep -n "_URL_RE\|_RST_FIGURE_RE\|_RST_REF\|_MD_INTERNAL_LINK_RE" tools/rbkc/scripts/verify/verify.py` → no hits (AST-only principle preserved).

## Bias-Avoidance Notes

- Spec §3-2 treated as authoritative; v6 PASS explicitly discounted as weak evidence.
- r3 High #1 re-tested empirically with real docutils on real v6 files before reporting — confirms dead-code claim is factual, not inferred.
- Circular test pattern flagged (High #1): hand-built AST + monkey-patched parser → walker-only coverage, zero parser-contract coverage. Same pattern r3 called out, unchanged in r4.
- No `pytest.mark.skip` / `importorskip` on internal modules in QL1 tests.
- No code modifications made (review-only, per instructions).
