# Expert Review: 22-B-16b-main step 2b (SE + QA)

**Date**: 2026-04-23
**Reviewer**: AI Agent as Software Engineer + QA Engineer
**Commit**: `e47859b6c`
**Files Reviewed**: 7 (3 source, 2 common, 1 run, 1 verify, 2 tests)

## Summary

**2 Findings — not shippable**

## Findings

### F1. `visitor.warnings` (dangling `:ref:` / `:doc:` / named-ref) are collected but never emitted — silent skip

- **Violated clause** — `rbkc-verify-quality-design.md` §3-2-2:
  > 「未解決 `:ref:` label … → **WARNING ログ** + display text fallback」
  > 「verify は QL1 WARNING としてログに列挙する (**silent skip 禁止は維持**)」
- **Description**: `_MDVisitor` appends to `self.warnings` on dangling `:ref:` (visitor.py:644), dangling `:doc:` (:666), and dangling named ref (:787). `extract_document` copies these into `parts.warnings` (:937). But `rst_normaliser.normalise_rst` returns only `parts.to_flat_md()` (rst_normaliser.py:76) — `parts.warnings` is discarded. No converter, `run.py create`, `run.py verify`, or `check_content_completeness` ever reads `visitor.warnings` or `parts.warnings`. Result: every dangling `:ref:` / `:doc:` / cross-doc `refname` is silently degraded to display text with zero user-visible signal. The spec explicitly forbids this ("silent skip 禁止は維持"). v6 has 353 files; any dangling link there is invisible today.
- **Fix**: Surface warnings at both sites:
  1. `normalise_rst` — return `(text, warnings)` or attach to an out-param; `_normalize_rst_source` forwards them; `check_content_completeness` emits each as `WARN[QL1] ...` (non-FAIL, per spec: "FAIL 昇格は … 保留").
  2. Create side — in the converter pipeline that calls `extract_document`, drain `parts.warnings` and emit via the same logger used by `run.py create`, prefixed `WARN[QL1] {source_rel}: …`.
  Add a unit test: a dangling-`:ref:` RST fixture → verify stdout/stderr contains `WARN[QL1]` with the label name.

### F2. `TestSphinxAnchorParity::test_anchor_is_label_name_slug_for_heading_label` asserts RBKC's own output, not empirical sphinx-build output

- **Violated clause** — `.claude/rules/review-feedback.md` → Horizontal check; `rbkc-verify-quality-design.md` §3-2-1:
  > 「create / verify とも本モジュールを経由する。**circular test を避けるため**、verify 側は anchor を独立に slug 再計算した上で、docs MD の実 heading slug と一致するかを検証する」
  and §3-2-2 bullet design-principle:
  > 「判断に迷ったら `/tmp` で小さな RST を書き **Sphinx を走らせて HTML を観測** し、それに合わせる」
- **Description**: The class docstring claims Sphinx parity is "verified empirically via /tmp sphinx-test," but `test_anchor_is_label_name_slug_for_heading_label` only asserts `lt.anchor == "my-usage-label"` — this is what `_anchor_for_label` produces by construction (`github_slug("my-usage-label")`), so the test is circular: any change to `_anchor_for_label` that still returns the same string passes, even if Sphinx's real rule diverges (e.g., if Sphinx were to strip leading digits, or handle multi-underscore differently). Only `test_anchor_for_block_quote_nested_label` happens to match a value (`runtime-platform`) that was independently observed in `/tmp/sphinx-test/_build/index.html` (`id="runtime-platform"`), but the test does not reference that HTML, so the pinning is latent, not enforced.
- **Fix**: Either (a) add a conftest fixture that runs `sphinx-build` on a minimal RST and parses the resulting HTML for `id=` values, then assert `lt.anchor` equals the parsed id — making the oracle independent of `_anchor_for_label`; or (b) add a frozen JSON fixture `tests/ut/fixtures/sphinx_anchor_parity.json` captured from a real sphinx run with a comment recording the sphinx version used, and assert against that fixture. Either path makes the test non-circular.

## Observations

- `_resolve_doc_target` (visitor.py:740) uses `endswith("/" + key)`. Edge case `endswith(key)` only when key equals resolved_str — `resolved_str == key` clause handles that. Suffix-match is safe given `rel_for_classify` keys start at a directory boundary.
- `LabelTarget` gained `anchor` with a default of `""` — older call sites constructing `LabelTarget` without the field keep compiling. Consider dropping the default in a follow-up to force explicit handling (zero-exception posture).
- `_render_label_target` is duplicated byte-for-byte between visitor and `verify._resolve_title_inline`. Extract to a shared helper in `scripts/common/labels.py` (e.g., `render_label_md_link`) so drift becomes a compile error, not a silent divergence.
- Normaliser parameter rename `label_map: dict[str, str]` → `dict` loses type info for readers. Prefer `dict[str, "LabelTarget | str"]`.

## Positive Aspects

- Spec-first approach: §3-2-2 was amended first and the code follows the spec, not the reverse.
- `_render_label_target` is a single function called from all four emission sites (`ref/numref`, `doc`, `refid`, `refname`) — good factoring; F3 below about drift applies only to the verify mirror, not the create side.
- 11 new spec-pinned cases, including the `big_picture.rst` block_quote regression from 22-B-16a.
- md5 change is documented in the commit message with the prior value — excellent traceability.
- `UNRESOLVED` sentinel handling is consistent across all four emission sites (display text + WARNING, never sentinel text leak).

## Files Reviewed

- `tools/rbkc/scripts/common/labels.py` (source)
- `tools/rbkc/scripts/common/rst_ast_visitor.py` (source)
- `tools/rbkc/scripts/common/rst_normaliser.py` (source)
- `tools/rbkc/scripts/run.py` (source)
- `tools/rbkc/scripts/verify/verify.py` (source)
- `tools/rbkc/tests/ut/test_labels_doc_map.py` (tests)
- `tools/rbkc/tests/ut/test_verify.py` (tests)
