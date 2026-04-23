# Expert Review: QA Engineer — QL1 (内部リンク)

**Date**: 2026-04-23
**Reviewer**: Independent QA Engineer (bias-avoidance stance)
**Round**: r5
**Scope**: QL1 internal-link verification per `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2 (lines 228-268). Rows: RST `reference` (refid/refname), RST `:ref:`, RST `figure`, RST `image`, MD `link_open` (non-external), MD inline `image`. Literalinclude delegated to QC1/QC2.

## Overall Assessment

**Rating**: 4.5 / 5

**Summary**: r4 High #1 (dead-code `refname` branch + circular monkey-patched tests) is **fully resolved** in r5. Implementation now uses `refid` + `doctree.ids` lookup and a new `_resolve_title_inline` helper renders embedded `:ref:` / named references inside the target title via `label_map`. Auto-ids (`section-N` / `id-N`) are skipped. Two real-parser tests drive docutils end-to-end (no monkeypatch, no hand-built reference nodes) with a FAIL case and a PASS case over the same fixture. Empirical check via `rst_ast.parse` confirms `refid='detailed-usage'` and `doctree.ids['detailed-usage']` contain the resolved section — the branch executes on real input, not in isolation. MD scheme filter now excludes `mailto:` / `tel:` / `javascript:` / `#anchor`; MD image fallback is `alt → title → filename`. 25/25 `TestCheckSourceLinks` tests pass; v6 runtime `verify` is clean. Residual issues are all Medium/Low coverage gaps that do not affect current content correctness.

## Key Issues

### Medium Priority

1. **`javascript:` scheme still has no pinning test (r4 Medium #2 carry-over)**
   - Description: `md_ast_visitor.py:413` excludes the tuple `("mailto:", "tel:", "javascript:", "#")`. Three of four entries have tests (`test_pass_md_mailto_link_not_internal`, `test_pass_md_tel_link_not_internal`, `test_pass_md_anchor_only_link_not_internal`). `javascript:` is unpinned. Empirically confirmed — `check_source_links` returns `[]` on `[クリック](javascript:void(0))` — but a refactor that silently drops `javascript:` from the tuple would not be caught by any test.
   - Proposed fix: Add a one-liner `test_pass_md_javascript_link_not_internal` sibling to the existing scheme tests.

2. **Empty-href MD link (`[text]()`) remains unpinned (r4 Medium #3 carry-over)**
   - Description: `md_ast_visitor.py:413` `elif href and not href.startswith(...)` relies on truthiness of `href` to skip empty-href links. Empirically confirmed — `[テキスト]()` yields `[]` — but rewriting the condition to `elif not href.startswith(...)` (dropping the truthiness guard) would silently start including empty-href links as QL1 candidates.
   - Proposed fix: Add `test_pass_md_empty_href_link_not_internal` pinning the skip policy.

3. **RST `figure` with `:alt:` but no caption — spec-literal fallback unpinned (r4 Medium #4 carry-over)**
   - Description: Spec §3-2 row 2 defines the chain `caption → URI filename` (no alt). `verify.py:1015-1031` implements exactly this: empirically, `.. figure:: images/diagram.png\n   :alt: 概要図\n` with no caption FAILs on `diagram.png` even when JSON contains `概要図`. No test fixes this behaviour. A future edit adding alt to the chain would not fail any test, and a reader of the spec might mistakenly "fix" the code to match a perceived user-friendly fallback.
   - Proposed fix: Add `test_rst_figure_alt_only_falls_back_to_filename_not_alt` — fixture with `:alt:` only, JSON containing the alt but not the filename, assert FAIL on filename.

4. **RST substitution image produces duplicate FAIL + no policy decision (r4 Medium #5 carry-over, new observation)**
   - Description: `.. |logo| image:: logo.png\n   :alt: 会社ロゴ\n\n|logo|\n` triggers QL1 twice with the identical message: `[QL1] image alt/filename missing from JSON: '会社ロゴ'` appears twice in the issues list. Two problems: (a) the substitution-image policy is still undecided vs. QL2's explicit substitution exclusion (spec line 268), and (b) the duplicate issue suggests `doctree.findall(nodes.image)` hits both the substitution definition's image and a resolved copy, with no deduplication analogous to `seen_images` on the MD path. Current code has `seen_images` only in the MD branch (`verify.py:1068`); the RST `image` loop (`verify.py:1034-1043`) has no dedup.
   - Proposed fix: (1) Decide substitution-image policy (likely exclude, consistent with QL2 substitution-URL exclusion); (2) add `seen_images` dedup to the RST branch regardless of the policy decision — duplicate failure messages are noise that erodes signal; (3) add a test pinning whichever policy is chosen.

### Low Priority

5. **`literalinclude` → QC1/QC2 handoff still not test-pinned (r4 Low #6 carry-over)**
   - Description: `verify.py:1045-1046` comment states literal_block is covered by QC1/QC2. Still no test documents this boundary. If QC1/QC2 scope changes, literalinclude could silently become unchecked.
   - Proposed fix: `test_pass_rst_literalinclude_delegated_to_qc` with a docstring pointing to the QC1/QC2 check.

6. **Unknown-label skip indistinguishable from PASS (r4 Low #7 carry-over)**
   - Description: `test_pass_rst_ref_unknown_label_skipped` at `test_verify.py:1417-1421` uses `label_map={}`; the `[]` result is consistent with both "branch taken → skipped" and "branch not reached". A sentinel label_map with an unrelated key would prove the skip branch specifically ran.
   - Proposed fix: Change to `label_map={"other-label": "Some Title"}` with JSON not containing "Some Title"; the `[]` then uniquely evidences the skip.

7. **No test confirms `findall` reaches figures nested in admonitions**
   - Description: `doctree.findall` is recursive by contract, but no test exercises `.. note:: :: .. figure::` containment. Low risk, but a simple pinning test protects against a regression that swaps `findall` for `traverse(descend=False)` or similar.
   - Proposed fix: `test_rst_figure_inside_note_detected` with a figure inside `.. note::` block.

## Positive Aspects

- **r4 High #1 fully resolved**: implementation walks `refid` and resolves via `doctree.ids` (verify.py:957-981); real-parser tests (`test_fail_rst_named_reference_target_title_missing`, `test_pass_rst_named_reference_target_title_in_json`) drive actual docutils parsing with standard RST syntax. No monkeypatching, no hand-built `nodes.reference(...)` — the circular pattern is gone.
- **Auto-id skip is precise**: `_AUTO_ID_RE = re.compile(r"^(?:id|section)-\d+$")` at `verify.py:956` + `test_pass_rst_plain_sections_without_named_references` confirms vanilla sections do not trigger false positives.
- **`_resolve_title_inline` helper** (`verify.py:874-911`) correctly handles titles that embed `:ref:` or named references — without it, `astext()` would return the bare label name and never match the converter's output, producing false FAILs. Logic covers role-ref display form (`Display <target>`), plain label form (→ label_map), and nested `nodes.reference` (refid → label_map).
- **Negative sanity-check coverage**: `test_pass_rst_named_reference_scheme_mailto_untouched` verifies that `.. _Contact: mailto:...` (a refuri-bearing reference, QL2 territory) is not swept into QL1.
- **MD scheme filter hardening** (`md_ast_visitor.py:411-418`): external URLs go to `external_urls` (QL2 path); `mailto:` / `tel:` / `javascript:` / `#` are excluded from `internal_links`; three explicit tests pin the contract.
- **MD image fallback chain is spec-literal**: `alt → title → filename` (`verify.py:1069-1075`, `md_ast_visitor.py:387-391`); pinned by `test_fail_md_image_title_missing_from_json`.
- **Caption-is-inline-only fallback**: `_has_visible_text` strips RST inline constructs before using caption, pinned by `test_fail_rst_figure_inline_only_caption_fallback_to_filename`.
- **AST-only principle preserved**: no regex link extraction in `verify.py`; all link candidates come from `doctree.findall(...)` or `md_ast_visitor.extract_document(...)`.
- **Deduplication** present in MD branch via `seen_link_texts` / `seen_images`; also in `:ref:` branch via `seen_labels`.
- **no_knowledge_content skip** (`verify.py:927`) avoids TOC false positives.

## Runtime Evidence

- `pytest tests/ut/test_verify.py::TestCheckSourceLinks -q` → 25 passed in 0.22s.
- `bash rbkc.sh verify 6` → `All files verified OK`.
- Empirical real-parser probe on the r5 fixture:
  - `refuri=None, refid='detailed-usage', refname=None, text='Detailed Usage'`
  - `doctree.ids` contains `'detailed-usage'` → section node → title → resolved text `'Detailed Usage'`
  - FAIL case returns `"[QL1] RST named reference 'detailed-usage' target title missing from JSON: 'Detailed Usage'"`; PASS case returns `[]`. Real end-to-end, no mocks.
- Empirical check of unpinned behaviours (Medium #1-#4): javascript-href → `[]`; empty-href → `[]`; figure alt-only → `'diagram.png'` filename FAIL; substitution-image → duplicate `'会社ロゴ'` FAIL.
- `grep -n "monkeypatch\|refname" tests/ut/test_verify.py` → only legacy `test_pass_rst_ref_unknown_label_skipped` match noise (no monkeypatch in QL1 tests; `refname` string absent from test file).
- `grep -n "_URL_RE\|_RST_FIGURE_RE\|_RST_REF\|_MD_INTERNAL_LINK_RE" scripts/verify/verify.py` → no hits (AST-only principle).

## Bias-Avoidance Notes

- Spec §3-2 treated as authoritative; v6 PASS alone explicitly discounted as weak evidence.
- r4 High #1 re-verified empirically with real docutils on the r5 fixture before upgrading the rating — confirmed the `refid` branch executes, `refname` is never populated, and the walker reaches the correct node.
- Test circularity audit: re-read both new named-reference tests. Input is raw RST string → `check_source_links` → `rst_ast.parse` → `doctree.findall` → real resolution. No layer is mocked. The FAIL and PASS cases share the fixture and differ only in JSON content — the discriminator is the checker's real behaviour, not a test harness shortcut.
- Empirically checked unpinned edge cases (javascript/empty-href/figure alt/substitution) instead of inferring from code — surfaced the duplicate substitution-image FAIL, which is a real defect, not a speculative one.
- No `pytest.mark.skip` / `importorskip` on internal modules in QL1 tests.
- No code modifications (review-only).

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source) — QL1 at 871-1077; `_resolve_title_inline` at 874-911; named-ref walker at 957-981
- `tools/rbkc/scripts/common/md_ast_visitor.py` (source) — scheme filter at 411-418; image capture at 387-391
- `tools/rbkc/scripts/common/rst_ast.py` (source) — parser wrapper used unchanged
- `tools/rbkc/tests/ut/test_verify.py` (tests) — `TestCheckSourceLinks` at 1379-1594
- `tools/rbkc/docs/rbkc-verify-quality-design.md` (spec) — §3-2 at 228-268

## Recommendations

- **Close Medium #1-#2** with one-line sibling tests (javascript / empty-href). Zero-cost contract pinning.
- **Close Medium #3** with a figure-alt fixture to freeze the spec-literal fallback chain against accidental drift.
- **Address Medium #4 explicitly**: decide substitution-image policy (recommend exclude, consistent with QL2 line 268), add `seen_images` dedup to the RST branch, and pin both with tests. The duplicate FAIL is real and should be fixed even if the policy ends up being "include".
- **Low #5-#7** are documentation-via-test; address when convenient.
- After Medium #1-#4 are closed, QL1 can be marked ✅ without reservation.
