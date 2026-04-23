# Expert Review: QA Engineer — QL1 (内部リンク)

**Date**: 2026-04-23
**Reviewer**: Independent QA Engineer (bias-avoidance stance)
**Scope**: QL1 internal link verification, per `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2 (row-by-row table, lines 251-258)
**Spec authority**: AST-only extraction. Node types required: RST `reference` (refid/refname, no refuri), RST `figure`, RST `image`, RST `literal_block` (`.. literalinclude::`, covered by QC1), MD `link_open` (non-external href), MD inline `image`. Regex-based source scanning explicitly forbidden (§3-2 lines 239, 245).

## Overall Assessment

**Rating**: 3.5 / 5
**Summary**: All six spec-mandated AST node types are handled and the AST-only principle is upheld (no regex scanning of source for links). Unit tests cover the main pass/fail shapes for each node type and include filename fallback. However, a **High-priority gap** exists in the RST named-reference path: the only test that exercises it synthesises the AST by hand and monkey-patches `rst_ast.parse`, so the real docutils-produced shape for `.. _label:` + `` `Text`_ `` is never exercised. Additionally, the MD "internal link" classification treats any non-`http(s)` href as internal — including empty/anchor-only/`mailto:` hrefs — which may produce false negatives or noise depending on JSON content.

## Key Issues

### High Priority

1. **RST native named-reference test is end-to-end-circumvented**
   - Description: `test_fail_rst_named_reference_target_title_missing` (`tests/ut/test_verify.py:1321-1340`) and `test_pass_rst_named_reference_unknown_label_skipped` (`:1342-1357`) both build the `nodes.document` tree by hand and monkey-patch `scripts.common.rst_ast.parse` to return that synthetic tree. This proves the walk-and-compare logic in `verify.py:1065-1080` runs, but does NOT verify that real docutils (when parsing `.. _usage-section:\n\n\`Usage\`_` / `.. _usage-section:\n\nlink: Usage_`) actually emits the `reference` node shape with `refname` populated that the code expects. If docutils produces a `pending_xref` / different attribute naming / resolves the ref before we see it, QL1 silently passes for every named reference in v6 — which is exactly the type of gap a QA review must catch.
   - Proposed fix: Add two paired tests driven through `rst_ast.parse(source_text)` (no monkey-patch):
     - `test_fail_rst_named_reference_via_real_parser_target_missing` — source text `` ".. _usage-section:\n\nタイトル\n====\n\n本文\n\nSee `Usage`_ for details.\n" `` (or the standalone target form) with `label_map={"usage-section": "利用ガイド"}`; assert a `QL1 ... named reference` FAIL with `'利用ガイド'` when JSON content lacks it.
     - `test_pass_rst_named_reference_via_real_parser_title_in_json` — same source, JSON containing `利用ガイド`; assert no QL1 issues.
     If the real parser does not populate `refname` on these reference forms, the code path at `verify.py:1069-1080` is dead code and the check must be rewritten to match docutils' actual output (e.g., walking `nodes.target` + resolving locally, or `refid` path).

2. **MD internal-link filter is "not external", not "internal" — `mailto:` / empty / bare-fragment hrefs included**
   - Description: `md_ast_visitor.py:410-413` classifies any href not starting with `http://`/`https://` as internal: `self.internal_links.append((text, href))`. That means `[foo](mailto:x@y)`, `[foo](#section)`, `[foo]()`, `[foo](tel:...)`, `[foo](javascript:...)` all feed QL1. For a `mailto:` the "link text" is typically the display name ("問い合わせ窓口"), which may legitimately be absent from JSON content → spurious QL1 FAIL. Conversely, the spec table row 5 defines "internal link" as a non-external link (implicitly a page/section reference), so the current behaviour arguably matches the letter of the spec — but there is no unit test pinning the boundary, so whichever behaviour is adopted is incidental rather than decided.
   - Proposed fix: Decide and document the classification, then add tests. Recommended decision: exclude `mailto:`, `tel:`, `javascript:`, pure-fragment (`#...`) and empty hrefs from `internal_links`; pure-fragment links only make sense within a single page and JSON does not carry anchors (§3-2 note "JSON はリンク構造を保持せずプレーンテキストのみを保持する"). Add:
     - `test_pass_md_mailto_link_skipped` — `[問い合わせ](mailto:a@b.example)` with unrelated JSON → no QL1 FAIL.
     - `test_pass_md_fragment_only_link_skipped` — `[上へ](#top)` with unrelated JSON → no QL1 FAIL.
     - `test_fail_md_relative_path_link` already covered by `test_fail_md_internal_link_text_missing`.

### Medium Priority

3. **No test for RST `figure` whose `:alt:` option is used (image child's alt) — only caption and filename paths covered**
   - Description: `.. figure::` supports an inline `:alt:` option on the contained image, but `verify.py:1113-1130` only inspects `nodes.caption` children and then falls back to the URI filename. If a real v6 source uses `.. figure:: foo.png\n   :alt: 概要図\n\n   (no caption)`, the alt text — which is the reader-visible text — is ignored entirely. Spec table row 2 explicitly says "child `caption` の inline テキスト、無ければ child `image` の URI ファイル名" which technically omits alt, so this may be spec-conformant — but the absence of a test means the decision is not pinned. Filename fallback for `.. figure::` with alt-only may produce a check against `foo.png` when a human reader would see `概要図`.
   - Proposed fix: Add `test_rst_figure_uses_caption_then_filename_ignoring_alt` to pin the spec-literal behaviour (alt is intentionally ignored), OR extend `verify.py:1113-1130` to use `image.get("alt")` as a middle fallback before filename and add a matching test. Either way, the behaviour must be decided + tested, not left incidental.

4. **No coverage of figure/image nested inside admonitions, sidebars, or substitution definitions**
   - Description: `doctree.findall(nodes.figure)` / `findall(nodes.image)` recursively walks, which is correct, but there is no unit test asserting that a `.. figure::` inside `.. note::` / `.. admonition::` / `.. |sub| image:: x.png` is reached. Sphinx substitution definitions produce `substitution_definition > image` which is a very different tree location — if substitution-body images should be excluded (analogous to QL2's substitution-URL exclusion at `§3-2 line 268`), the current code captures them and may produce spurious FAILs. If they should be included, there is no test confirming the walk reaches them.
   - Proposed fix: Add two tests: (a) `test_rst_figure_inside_admonition_detected` — figure nested in `.. note::` emits QL1 when caption missing from JSON; (b) `test_rst_substitution_image_exclusion_policy` — `.. |logo| image:: logo.png\n:alt: 会社ロゴ` followed by `|logo|` usage. Decide whether the alt should be checked (reader sees it) and pin the decision. Currently the walker captures these silently.

5. **MD image test does not cover the `title` attribute**
   - Description: Spec table row 6 says "`alt` / `title` / `src` のファイル名". Implementation at `verify.py:1167-1174` and extractor at `md_ast_visitor.py:387-391` only capture `(alt, src)` — `title` is never read. If a MD author writes `![](./x.png "説明")` (empty alt, title attribute carrying the reader-visible caption), the check falls back to `x.png` and misses the real reader-visible string.
   - Proposed fix: Extend `md_ast_visitor.py:387-391` to capture title (`c.attrGet("title")`), update `images` tuple to `(alt, title, src)` (or add a parallel list), update `verify.py:1167-1174` fallback chain to `alt or title or filename`, and add `test_fail_md_image_title_fallback` + `test_pass_md_image_title_in_json`.

### Low Priority

6. **`literal_block` / `literalinclude` coverage is delegated to QC1/QC2 without a cross-reference assertion**
   - Description: `verify.py:1144-1145` comment states "literal_block content is covered by QC1/QC2". This is the correct design decision (spec row 4 explicitly says "QC1 handles"), but there is no QL1 test that exercises the "literalinclude present + code in JSON" happy path to document the hand-off. A future refactor that moves QC1/QC2 logic could leave literalinclude unchecked without failing any QL1 test.
   - Proposed fix: Add one `test_pass_rst_literalinclude_delegated_to_qc` (source with `.. literalinclude::`, JSON containing the code body, assert `check_source_links` returns `[]`) with a docstring pointing to QC1/QC2 as the authoritative check. Purely a documentation-via-test.

7. **Unknown-label skip is not distinguishable from PASS in the test**
   - Description: `test_pass_rst_ref_unknown_label_skipped` (`test_verify.py:1218-1222`) asserts `== []`, which is what a PASS and a skip both produce. A tester skimming cannot tell whether the code took the "skip unknown label" branch or the "resolved and matched" branch. Minor but a spec-trace gap.
   - Proposed fix: Use a sentinel — e.g., pass a label_map that, if the code fell through to resolution, would FAIL (because `"internal 別タイトル"` is not in JSON). If the skip branch is taken, no FAIL. Example: `label_map={"other-label": "Some Title"}` + JSON without "Some Title", source `:ref:\`cross-file-label\``: expect `[]` because the ref's label is not in the map (skip path).

## Positive Aspects

- **Spec AST-only principle upheld for QL1**: `check_source_links` (`verify.py:1024-1176`) drives RST via `rst_ast.parse` + `doctree.findall(nodes.reference/figure/image/inline)` and MD via `md_ast_visitor.extract_document`. No regex scans the source for links.
- **All six spec-mandated node types accounted for** in implementation: RST `reference` refname (`:1065-1080`), RST `:ref:` role-inline both display and bare-label forms (`:1082-1111`), RST `figure` with caption→filename fallback (`:1113-1130`), RST `image` outside figure (`:1132-1142`), RST `literal_block` explicitly delegated to QC1/QC2 (`:1144-1145`), MD `link_open` non-external (`:1156-1163`), MD inline `image` with alt→filename fallback (`:1165-1174`).
- **Inline-only caption fallback is correctly implemented and tested**: `_has_visible_text` (`:1179-1195`) strips RST inline constructs (`` `foo`_ ``, `:role:\`x\``, `[1]_`) before deciding fallback, covered by `test_fail_rst_figure_inline_only_caption_fallback_to_filename`.
- **Deduplication via `seen_link_texts` / `seen_images` / `seen_labels`** prevents noisy duplicate FAILs when the same link/image appears multiple times.
- **External-link exclusion is at the MD extractor level** (`md_ast_visitor.py:410-411`), which is structurally cleaner than filtering at QL1: the QL2 vs QL1 split is enforced by the extractor contract, not by QL1 string matching.
- **`no_knowledge_content` skip** (`verify.py:1036`) correctly avoids false positives on TOC / no-content pages.
- **19 `TestCheckSourceLinks` tests pass**; `pytest tests/ut/test_verify.py::TestCheckSourceLinks -q` → 19 passed.
- **v6 runtime verify PASS** (`bash rbkc.sh verify 6` → `All files verified OK`).

## Recommendations

- **Address High-priority gap #1 before claiming QL1 ✅**: the synthetic-tree test is textbook circular (test drives the AST shape the code expects rather than letting the parser produce it). Without a real-parser test, the claim that `refname` path works is unverified for v6's 516 RST files that use `:ref:`. Per bias-avoidance: v6 PASS is insufficient evidence.
- **Address High-priority gap #2** by explicitly defining the internal-link classification (exclude `mailto:` / fragment-only / empty / `tel:` / `javascript:`) and pinning it with tests. Currently the boundary is incidental.
- **Consider adding a "walk-reaches-nested" test** (Medium #4) — `findall` is recursive but there is no test confirming figures/images inside admonitions are reached. Cheap insurance.
- **Consider adding `title` to MD image fallback chain** (Medium #5) — spec row 6 explicitly lists it; currently dead in both extractor and checker.
- **Document the QL1↔QC1/QC2 hand-off** with a test (Low #6) to prevent silent regressions if QC1/QC2 logic is refactored.

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source code) — QL1 core at lines 1021-1195
- `tools/rbkc/scripts/common/md_ast_visitor.py` (source code) — `images`/`internal_links` collection at 387-413
- `tools/rbkc/scripts/common/rst_ast.py` (source code) — parser wrapper
- `tools/rbkc/scripts/common/labels.py` (source code) — `build_label_map` (spec line 261)
- `tools/rbkc/tests/ut/test_verify.py` (tests) — `TestCheckSourceLinks` at 1177-1357
- `tools/rbkc/docs/rbkc-verify-quality-design.md` (spec) — §3-2 lines 228-268

## Runtime Evidence

- `pytest tests/ut/test_verify.py::TestCheckSourceLinks -q` → 19 passed (0.23s)
- `bash rbkc.sh verify 6` → `All files verified OK`
- v6 source exercises QL1 node types at scale: 516 RST files use `:ref:`; figure/image in `.lw/nab-official/v6/.../SqlExecutor.rst`, `.../ja/index.rst`, `.../biz_samples/01/index.rst`.

## Bias-Avoidance Notes

- Spec §3-2 treated as authoritative; v6 PASS explicitly discounted as weak evidence. The synthetic-tree test (High #1) is a textbook example of why v6 PASS can be misleading: if the check is walking a dead branch, every v6 file "passes" regardless of whether the check works.
- Circular test flagged above (High #1) — asserting hand-built AST against code that walks the same hand-built AST shape proves the walk logic, not the parser contract.
- No `pytest.mark.skip` or `importorskip` on internal modules found in QL1 tests.
- No code modifications made (review-only, per instructions).
