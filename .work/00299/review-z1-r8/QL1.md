# QL1 r8 Bias-Avoidance Review

Reviewed: `check_source_links` in `tools/rbkc/scripts/verify/verify.py`
(lines 1100–1287) against `rbkc-verify-quality-design.md` §3-2, and the
associated tests in `tools/rbkc/tests/ut/test_verify.py` (`TestCheckSourceLinks`).

Focus per reviewer brief: r7 fixes — substitution-body exclusion via
`_under_substitution` and RST image/figure dedup via
`seen_rst_images` / `seen_rst_figures`.

## Findings

### QL1-F1 (Medium) — substitution-body skip test does not actually pin the skip

- Description: `test_pass_rst_substitution_image_body_skipped` constructs
  a source where the substitution body carries `:alt: アイコン` and sets
  JSON `content` to `"ここに ![アイコン](images/icon.png) を挿入します。"`.
  Because `アイコン` is present in JSON, the QL1 image branch would emit
  no FAIL regardless of whether `_under_substitution` skips the
  substitution-body image or not. The assertion
  `not any("QL1" in i and "アイコン" in i for i in issues)` therefore
  passes under both behaviours and does not pin the skip.
- Spec clause (§3-2 line 268): 「RST の `.. |sub| raw:: html`
  substitution body 内 URL も `raw` node として AST に現れるため、対象
  から除外する場合は AST ノードの属性で判定する」 — and the rbkc.md
  decision "QL1 substitution-body image — include or exclude? →
  Exclude" require the substitution-body occurrence to be excluded by
  AST attribute, not by coincidental JSON containment.
- Proposed fix: make the test reproducibly RED without the
  `_under_substitution` guard. For example, have JSON omit `アイコン`
  entirely, then assert exactly zero QL1 issues mentioning the
  substitution-body image (including any filename fallback), so that
  removing `_under_substitution` would cause a FAIL to fire from the
  substitution-body image and break the test. Ruling out the
  paragraph-rendered occurrence requires the paragraph-rendered image
  not to trigger QL1 independently; use a source where the
  substitution is referenced but the rendered substitution_reference
  carries its own alt handled elsewhere, and assert absence of any QL1
  referencing the substituted image.

### QL1-F2 (Low) — `seen_rst_figures` is implemented but not pinned by a test

- Description: the symmetric dedup `seen_rst_figures` (verify.py:1216,
  1229, 1231) is only exercised indirectly. There is an explicit test
  for `seen_rst_images` dedup
  (`test_pass_rst_image_dedup_same_alt_not_reported_twice`) but no
  equivalent test that two `.. figure::` blocks with the same caption
  (or same filename fallback) and a JSON that omits that caption
  produce exactly one QL1 issue.
- Spec clause: §3-2 line 254 (figure row) defines the same
  "extracted text / filename fallback" contract as the image row.
  ゼロトレランス §2-1 requires each check to be test-pinned, and
  review-feedback.md's horizontal-check rule requires symmetry between
  sibling branches to be enforced by tests, not just by implementation.
- Proposed fix: add a TDD test mirroring
  `test_pass_rst_image_dedup_same_alt_not_reported_twice` for the
  figure branch — two `.. figure::` blocks sharing the same caption
  text, JSON omits that caption, assert `len([i for i in issues if
  "QL1" in i and "<caption>" in i]) == 1`.

## Observations

- `_under_substitution` correctly walks `node.parent` up to
  `substitution_definition`, matching §3-2 line 268's "AST ノードの
  属性で判定する" requirement; regex-based source scanning is
  correctly avoided (§3-2 line 239).
- `seen_rst_images` (verify.py:1238, 1247, 1249) mirrors the MD
  branch's `seen_images` (1278, 1283), satisfying cross-format
  symmetry required by §3-2 rows 5–6.
- Figure → image fallback preserves `_has_visible_text` gating so
  inline-only captions correctly fall back to filename (§3-2 line 260);
  this is pinned by `test_fail_rst_figure_inline_only_caption_fallback_to_filename`.
- External links (`refuri`) continue to be routed to QL2 (verify.py:1144),
  respecting the QL1/QL2 split.
- QL1 substitution-body handling is consistent with QL2's
  substitution-body handling (verify.py:538–551), i.e. the spec §3-2
  line 268 rule is applied symmetrically on both link axes.
