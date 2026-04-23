# Expert Review: QA Engineer — QL1 (内部リンク)

**Date**: 2026-04-23
**Reviewer**: Independent QA Engineer (bias-avoidance stance)
**Round**: r6
**Scope**: QL1 internal-link verification per `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2 (lines 228-268). Rows: RST `reference` (refid + `doctree.ids` lookup), RST `:ref:` role, RST `figure`, RST `image`, MD `link_open` (non-external, scheme-filtered), MD inline `image` (alt / title / filename). Literalinclude delegated to QC1/QC2.

## Overall Assessment

**Rating**: 4.5 / 5

**Summary**: No QL1 source/test changes landed between r5 and r6 — the only r6 commit (`d598590ce`) addresses QO1 tilde-fence and QC2 Excel skip cleanup, leaving QL1 at its r5 state. All r5 strengths carry over and have been re-verified empirically: `TestCheckSourceLinks` passes 25/25, real-docutils tests exercise the `refid` + `doctree.ids` walker (no monkeypatching, no hand-built reference nodes, no circular fixtures), `_AUTO_ID_RE` suppresses auto-id false positives, `_resolve_title_inline` renders embedded `:ref:` / named refs via `label_map`, the MD scheme filter excludes `mailto:` / `tel:` / `javascript:` / `#`, MD image fallback is `alt → title → filename`, and `bash rbkc.sh verify 6` reports `All files verified OK`. AST-only principle holds: `grep` for `_URL_RE` / `_RST_FIGURE_RE` / `_RST_REF` / `_MD_INTERNAL_LINK_RE` returns no hits in `verify.py`. Residual items are the r5 Medium/Low coverage gaps, unchanged; they do not affect current output correctness but leave known contract edges unpinned.

## Key Issues

### Medium Priority

1. **`javascript:` scheme still has no pinning test (carry-over from r4 Medium #2 / r5 Medium #1)**
   - Description: `scripts/common/md_ast_visitor.py:413` excludes the tuple `("mailto:", "tel:", "javascript:", "#")`. Three of four entries are pinned by tests (`test_pass_md_mailto_link_not_internal` at `tests/ut/test_verify.py:1552`, `test_pass_md_tel_link_not_internal` at `test_verify.py:1566`, `test_pass_md_anchor_only_link_not_internal` at `test_verify.py:1559`). `javascript:` is unpinned. Empirically re-confirmed in r6 — `check_source_links('[click](javascript:void(0))\n', 'md', data, {})` returns `[]` — but a refactor that silently drops `javascript:` from the exclusion tuple would pass every existing test.
   - Proposed fix: Add a one-liner `test_pass_md_javascript_link_not_internal` sibling to the three existing scheme tests. Zero-cost contract pinning.

2. **Empty-href MD link (`[text]()`) remains unpinned (carry-over from r4 Medium #3 / r5 Medium #2)**
   - Description: `md_ast_visitor.py:413` reads `elif href and not href.startswith(...)` — the leading truthiness guard is what skips empty-href links. Empirically re-confirmed in r6 — `check_source_links('[テキスト]()\n', 'md', data, {})` returns `[]` — but rewriting to `elif not href.startswith(...)` (a plausible simplification) would silently start pushing empty-href links into `internal_links`, and no test would fail.
   - Proposed fix: Add `test_pass_md_empty_href_link_not_internal` pinning the empty-href skip.

3. **RST `figure` with `:alt:` but no caption — spec-literal fallback unpinned (carry-over from r4 Medium #4 / r5 Medium #3)**
   - Description: Spec §3-2 row 2 defines the chain `caption → URI filename` (alt is **not** in the chain for `figure`; `figure` uses caption, only `image` uses alt). `verify.py:1015-1032` implements exactly this. Empirically re-confirmed in r6: `.. figure:: images/diagram.png\n   :alt: 概要図\n` with JSON containing `概要図` but not `diagram.png` returns `"[QL1] figure caption/filename missing from JSON: 'diagram.png'"`. This is correct per spec, but no test locks it — a future maintainer reading the spec quickly might “fix” the code to include alt in the figure fallback chain and all tests would still pass.
   - Proposed fix: Add `test_rst_figure_alt_only_falls_back_to_filename_not_alt` — `:alt:` only, JSON contains the alt but not the filename, assert FAIL mentions the filename (not the alt).

4. **RST substitution image still produces duplicate FAIL + policy undecided (carry-over from r5 Medium #4)**
   - Description: `.. |logo| image:: logo.png\n   :alt: 会社ロゴ\n\n|logo|\n` triggers QL1 **twice** with identical text. Empirically re-confirmed in r6: `check_source_links(...)` returns `["[QL1] image alt/filename missing from JSON: '会社ロゴ'", "[QL1] image alt/filename missing from JSON: '会社ロゴ'"]`. Two concerns: (a) substitution-image policy is undecided vs. QL2's explicit substitution exclusion (spec line 268, `.. |sub| raw:: html` exclusion); (b) the RST `image` loop at `verify.py:1035-1043` has no dedup, while the MD branch does (`seen_images` at `verify.py:1069`, and `seen_labels` at `verify.py:985` for `:ref:`). `doctree.findall(nodes.image)` visits both the substitution_definition's nested image and any resolved copy, so the duplicate message is a dedup-absence bug, independent of the policy question.
   - Proposed fix: (1) Decide substitution-image policy — recommend **exclude** for consistency with QL2's substitution-raw-URL exclusion (spec line 268). (2) Add a `seen_image_keys` set to the RST `image` loop regardless of the policy decision; duplicate identical FAIL messages are noise that erodes signal. (3) Add a test pinning whichever policy is chosen.

### Low Priority

5. **`literalinclude` → QC1/QC2 handoff still not test-pinned (carry-over from r4 Low #6 / r5 Low #5)**
   - Description: `verify.py:1046-1047` has an explanatory comment stating `literal_block` content is covered by QC1/QC2 sequential-delete. No test documents the handoff. If a future QC1/QC2 refactor narrows its scope, `literalinclude` content could silently fall through the cracks between QL1 and QC.
   - Proposed fix: `test_pass_rst_literalinclude_delegated_to_qc` with a fixture containing `.. literalinclude::` + a docstring linking to the QC1/QC2 check. Intent is documentation-via-test.

6. **Unknown-label skip indistinguishable from PASS (carry-over from r4 Low #7 / r5 Low #6)**
   - Description: `test_pass_rst_ref_unknown_label_skipped` at `test_verify.py:1420-1424` uses `label_map={}`. The `[]` result is consistent with both "skip branch taken" and "branch never entered" — the test does not uniquely evidence the skip. If the walker stopped reaching `role-ref` inline nodes entirely, this test would still pass.
   - Proposed fix: Use `label_map={"other-label": "Some Title"}` with JSON not containing "Some Title"; the `[]` result then uniquely evidences that the `:ref:` branch ran and the unknown label was skipped (because a bug that entered the branch with the wrong label would FAIL on "Some Title" leakage, and a bug that didn't enter at all would still PASS). A second assertion that an unrelated label in label_map does not pollute output strengthens the pin.

7. **`findall` recursion through admonitions is empirically correct but unpinned (carry-over from r5 Low #7)**
   - Description: r6 empirical probe confirms `.. note::` → nested `.. figure::` is detected (`doctree.findall(nodes.figure)` is recursive by docutils contract, and the check returned `"[QL1] figure caption/filename missing from JSON: 'ネストされた図'"`). No regression test locks this. A future edit that swaps `findall` for a non-recursive traversal (e.g. iterating `doctree.children`) would miss figures inside admonitions and no test would fail.
   - Proposed fix: `test_rst_figure_inside_note_detected` with a figure nested in `.. note::`.

## Positive Aspects (re-verified in r6)

- **r4 High #1 stays resolved.** Named-reference resolution uses `refid` + `doctree.ids` lookup (`verify.py:957-982`); `refname` is absent from the file (grep verified). Real-parser tests (`test_fail_rst_named_reference_target_title_missing` at `test_verify.py:1523-1537`, `test_pass_rst_named_reference_target_title_in_json` at `test_verify.py:1539-1550`) feed raw RST through `rst_ast.parse` and let docutils resolve — no monkeypatch, no hand-built nodes, no test-setup circularity.
- **Auto-id precision.** `_AUTO_ID_RE = re.compile(r"^(?:id|section)-\d+$")` at `verify.py:957` is pinned by `test_pass_rst_plain_sections_without_named_references` (`test_verify.py:1580`).
- **`_resolve_title_inline` helper** (`verify.py:875-912`) renders titles that embed `:ref:` / named references through `label_map` so the verify string matches the converter's output; covers role-ref display (`Display <target>`), plain label (→ label_map), nested `reference` (refid → label_map).
- **Lane discipline.** `test_pass_rst_named_reference_scheme_mailto_untouched` (`test_verify.py:1588-1596`) verifies refuri-bearing references (QL2 territory) are not swept into QL1. `test_pass_md_external_link_skipped` (`test_verify.py:1438`) does the same for MD.
- **MD scheme filter.** `md_ast_visitor.py:411-418`: external → `external_urls` (QL2 path); `mailto:` / `tel:` / `javascript:` / `#` excluded from `internal_links`; three of four exclusions pinned (see Medium #1 for the fourth).
- **MD image fallback chain is spec-literal.** `alt → title → filename` at `verify.py:1069-1076` and `md_ast_visitor.py:387-391`; `test_fail_md_image_title_missing_from_json` (`test_verify.py:1571-1578`) pins the title step, others pin alt / filename.
- **Caption-is-inline-only fallback.** `_has_visible_text` at `verify.py:1081+` strips RST inline constructs before using caption; `test_fail_rst_figure_inline_only_caption_fallback_to_filename` (`test_verify.py:1472-1483`) pins it.
- **AST-only principle preserved.** `grep -n "_URL_RE\|_RST_FIGURE_RE\|_RST_REF\|_MD_INTERNAL_LINK_RE" scripts/verify/verify.py` → **no hits** in r6. All link candidates come from `doctree.findall(...)` or `md_ast_visitor.extract_document(...)`.
- **Dedup present where implemented.** `seen_link_texts` / `seen_images` on MD (`verify.py:1058`, `verify.py:1069`); `seen_labels` on `:ref:` (`verify.py:985`). Gap: RST `image` loop — see Medium #4.
- **`no_knowledge_content` skip.** `verify.py:928` avoids TOC-style false positives; pinned by `test_pass_no_knowledge_content_skipped` (`test_verify.py:1444`).

## Runtime Evidence (r6)

- `cd tools/rbkc && python -m pytest tests/ut/test_verify.py::TestCheckSourceLinks -q` → **25 passed in 0.22s**.
- `cd tools/rbkc && bash rbkc.sh verify 6` → **All files verified OK**.
- Unpinned-edge empirical probe (r6, real docutils / markdown-it-py):
  - `javascript:void(0)` → `[]` ✔ (Medium #1 unpinned)
  - `[テキスト]()` → `[]` ✔ (Medium #2 unpinned)
  - figure `:alt:` only, no caption → `"[QL1] figure caption/filename missing from JSON: 'diagram.png'"` ✔ (Medium #3: spec-correct, unpinned)
  - `|logo|` substitution image → **duplicate** `"[QL1] image alt/filename missing from JSON: '会社ロゴ'"` ×2 ✗ (Medium #4: bug, real)
  - `.. note::` → nested `.. figure::` → `"[QL1] figure caption/filename missing from JSON: 'ネストされた図'"` ✔ (Low #7: correct, unpinned)
- `grep -n "monkeypatch" tests/ut/test_verify.py` (within `TestCheckSourceLinks`) → none.
- `grep -n "refname" scripts/verify/verify.py` → none (dead branch from r4 already removed).
- `grep -n "_URL_RE\|_RST_FIGURE_RE\|_RST_REF\|_MD_INTERNAL_LINK_RE" scripts/verify/verify.py` → none.

## Bias-Avoidance Notes

- Spec §3-2 (`tools/rbkc/docs/rbkc-verify-quality-design.md:228-268`) treated as authoritative. `bash rbkc.sh verify 6` passing alone explicitly discounted as weak evidence — real source corpus may simply not contain the edge patterns (substitution images, empty hrefs, figure-with-alt-only) that the Medium findings target.
- Each Medium / Low finding was re-checked empirically in r6 via direct `check_source_links(...)` calls with the edge fixtures, not inferred from code reading.
- Named-reference resolution was re-verified to use real docutils: the FAIL and PASS tests share the same RST fixture and only differ in JSON content, so the pass/fail discriminator is the checker's real behaviour, not a test harness shortcut.
- No `pytest.mark.skip` / `pytest.importorskip` in `TestCheckSourceLinks`.
- No code modifications made during this review (review-only).

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source) — QL1 region `870-1078`; `_resolve_title_inline` at `875-912`; named-ref walker at `957-982`; `:ref:` walker at `984-1013`; figure walker at `1015-1032`; image walker at `1034-1043`; MD branch at `1049-1076`
- `tools/rbkc/scripts/common/md_ast_visitor.py` (source) — scheme filter at `411-418`; image capture at `387-391`
- `tools/rbkc/scripts/common/rst_ast.py` (source) — parser wrapper used unchanged
- `tools/rbkc/tests/ut/test_verify.py` (tests) — `TestCheckSourceLinks` at `1382-1596`
- `tools/rbkc/docs/rbkc-verify-quality-design.md` (spec) — §3-2 at `228-268`

## Recommendations

- **Close Medium #1 / #2** with two one-line sibling tests (javascript / empty-href). Zero-cost contract pinning against refactor drift.
- **Close Medium #3** with a figure-alt-only fixture to freeze the spec-literal `caption → filename` chain (alt not in the chain for `figure`).
- **Close Medium #4** — this is the only item with a real defect: (a) decide substitution-image policy (recommend exclude, consistent with QL2 line 268); (b) add `seen_image_keys` dedup to the RST `image` loop regardless; (c) pin with a test. Duplicate identical FAIL messages erode signal and should be fixed even if the policy lands as "include".
- **Low #5 / #6 / #7** are documentation-via-test; address when convenient. Low #7 (figure-in-admonition) is free insurance against a subtle traversal regression.
- After Medium #1-#4 are closed, QL1 can move to ✅ without reservation. All four are additive (three new tests + one dedup-plus-test) and do not require touching the existing implementation's correct-path logic.
