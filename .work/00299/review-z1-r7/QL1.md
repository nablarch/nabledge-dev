# QL1 Bias-Avoidance QA Review (Z-1 r7)

**Target**: `tools/rbkc/scripts/verify/verify.py::check_source_links` (+ `_source_urls` context, `_resolve_title_inline`)
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2
**Tests**: `tools/rbkc/tests/ut/test_verify.py::TestCheckSourceLinks`
**Verdict**: **FAIL — spec violation on RST substitution-body images + no test pinning the behaviour**

---

## Findings

### F1. RST substitution-body images are not excluded — spec symmetry with QL2 violated

**Spec clause (§3-2, line 268)**:
> RST の `.. |sub| raw:: html` substitution body 内 URL も `raw` node として AST に現れるため、対象から除外する場合は AST ノードの属性で判定する

**Project rule (`.claude/rules/rbkc.md`)**:
> "QL1 substitution-body image — include or exclude?" → **Exclude, by spec symmetry with QL2's explicit substitution-body URL exclusion.**

**Observed behaviour**: In `check_source_links` RST branch, `doctree.findall(nodes.image)` (verify.py:1035) walks every `image` node in the tree **without checking the parent**. docutils emits the image node twice for a substituted image: once under `substitution_definition`, once under the paragraph where `|icon|` is substituted. Reproduction:

```
Intro.

.. |icon| image:: images/icon.png
   :alt: アイコン

Use |icon| here.
```
→ `check_source_links` currently returns:
```
[QL1] image alt/filename missing from JSON: 'アイコン'
[QL1] image alt/filename missing from JSON: 'アイコン'
```

Two problems in one:
1. Substitution-body images are not excluded (symmetry-with-QL2 violation).
2. The same image is reported twice (dedup missing, see F2).

QL2 gets this right implicitly: `raw:: html` bodies are `raw` nodes, so `findall(nodes.reference)` never sees those URLs. QL1's equivalent must explicitly skip `substitution_definition` children, because `nodes.image` IS emitted inside that node.

**Fix**: In the RST `image` loop, skip when `isinstance(img.parent, nodes.substitution_definition)` — the substituted occurrence (parent = paragraph) still covers the reader-visible case. Same guard should apply to `figure` (defensive — `.. |x| figure::` is legal).

### F2. RST image loop lacks `seen_images` dedup — MD path has it, RST does not

**Spec/rule**: ゼロトレランス + rbkc.md "QC1 residue reporting — RST one-snippet vs MD all-fragments — which is correct? → All fragments." This finding is the opposite direction (over-reporting not under-reporting), but the asymmetry between branches is the issue: MD branch dedups (verify.py:1069–1074), RST branch does not (verify.py:1035–1044).

After F1 is fixed, duplicates from substitution vanish, but the same `alt`-text appearing on two different images (or the same filename reused in two `.. image::` directives in one file) still produces duplicate FAIL lines on RST while MD collapses them.

**Fix**: Add a `seen_rst_images: set[str]` mirror of the MD dedup so the two branches behave identically for identical input. Decide one policy and apply it to both — spec is silent here, so the bias is toward "match MD" since MD's behaviour is already test-pinned (`seen_link_texts`, `seen_images`).

### F3. No test pins the substitution-body exclusion

**Spec/rule**: rbkc.md §"Review findings — default is fix, not triage" plus ゼロトレランス. QL2 has `test_pass_rst_substitution_only_url_skipped` (test_verify.py:767) that pins the symmetric behaviour for URLs. QL1 has **no** equivalent test pinning substitution-body image exclusion. Once F1 is fixed, a regression that re-walks substitution_definition images will ship undetected.

**Fix**: Add RED → GREEN test `test_pass_rst_substitution_image_body_skipped` using the fixture in F1, asserting that when the image `alt` is absent from JSON, QL1 emits zero FAILs (the reader-visible occurrence comes via the substituted paragraph, whose alt is the same string — which the test JSON must contain to isolate the substitution-body question). Mirror the QL2 test's shape.

### F4. No test pins RST image dedup

QL1 MD dedup is implicitly covered (no test explicitly asserts "duplicate image reported once"). RST dedup (after F2 fix) has no test either. Mirror QL2's `test_pass_duplicate_url_reported_once` (test_verify.py:718) for QL1 on both RST and MD paths.

---

## Observations (no fix required)

- **AST-only collection confirmed**. `check_source_links` uses `doctree.findall(nodes.reference|inline|figure|image)` for RST and `md_ast_visitor.extract_document(...).internal_links / images` for MD. No `_RST_FIGURE_RE`, `_RST_IMAGE_RE`, or raw-text regex scans remain. The only `re` usages inside QL1 are `_AUTO_ID_RE` (matching refid strings, not source text) and `_has_visible_text` (matching caption strings already extracted from the AST) — both operate on AST-derived strings, not on source text. Compliant with §3-2 "AST 経由原則".

- **Scheme filter for MD is correct and test-pinned**. `md_ast_visitor.py:411–418` excludes `http(s)://` (→ QL2), `mailto:`, `tel:`, `javascript:`, and `#` anchors from `internal_links`. Pinned by `test_pass_md_mailto_link_not_internal` / `test_pass_md_tel_link_not_internal` / `test_pass_md_anchor_only_link_not_internal` (test_verify.py:1552–1569). Spec §3-2 row 5 is "href が外部 URL でない" — the visitor's filter honours this while additionally carving out non-document URI schemes, which is the correct reading (a `mailto:` href is not a document-to-document internal link).

- **MD image fallback order matches spec**. `check = alt.strip() or title.strip() or (_Path(src).name if src else "")` (verify.py:1071) implements §3-2 row 6 "`alt` / `title` / `src` のファイル名" in exactly that priority. Pinned by `test_fail_md_image_alt_missing` (alt), `test_fail_md_image_title_missing_from_json` (title, test_verify.py:1571), and `test_fail_md_image_without_alt_falls_back_to_filename` (filename).

- **RST figure inline-only caption fallback is correct**. `_has_visible_text` strips RST inline constructs and, if nothing remains, falls back to the image filename. Matches §3-2 "caption / alt が RST inline 構文のみ ... の場合、ファイル名 fallback を採用する". Pinned by `test_fail_rst_figure_inline_only_caption_fallback_to_filename` (test_verify.py:1472).

- **Auto-generated refid skip is correct**. `_AUTO_ID_RE = ^(?:id|section)-\d+$` (verify.py:957) suppresses docutils-synthesised anchors for TOC/contents directives so vanilla sections do not emit spurious QL1. Pinned by `test_pass_rst_plain_sections_without_named_references` (test_verify.py:1580). Spec §3-2 row 1 requires "label 解決後のタイトル" for `refid` references — auto-IDs are not user-defined labels, so skipping them is the correct reading.

- **literalinclude handoff to QC1/QC2 is spec-compliant**. The comment at verify.py:1046 explicitly hands `literal_block` content to QC1/QC2 (sequential-delete). §3-2 row 4 requires "コード本文が JSON content に含まれているか" — QC1/QC2's sequential-delete over full JSON content satisfies "含まれているか" equivalently. No duplicate check needed in QL1.

- **Tests use real docutils / markdown-it-py fixtures**. `grep` for `nodes.`, `Mock`, `MagicMock`, `_make_` in `test_verify.py` within `TestCheckSourceLinks` returns zero matches — all 30+ cases drive real source strings through `check_source_links`. No hand-built AST nodes, no circular tests: the oracle (`data["content"]`) is the reader-visible JSON content that a correct converter must produce, not a copy of the RST source string, so each assertion independently encodes the spec rather than the implementation. Compliant with bias-avoidance principle.

- **`_resolve_title_inline` for nested `:ref:` inside section titles is spec-faithful**. The function re-resolves label display via `label_map` so the string checked against JSON matches what the converter emitted, not the raw `:ref:\`label\`` source. This is necessary because docutils' `astext()` returns the bare label name, not the target title. Pinned by `test_pass_rst_ref_plain_label_resolved` (test_verify.py:1407).

---

## Summary

Three fixes required (F1, F2, F3) + one defensive test add (F4). F1 is a true spec violation (RST substitution-body images counted against JSON, contrary to symmetry with QL2's §3-2 line 268 clause); F2 is an internal-consistency gap that amplifies F1's symptoms and creates RST-vs-MD behavioural divergence; F3 and F4 are the test-pin gaps that would let either regression ship unnoticed. No findings on AST-only collection, scheme filter, MD image fallback order, or literalinclude handoff — all four are spec-compliant and test-pinned.
