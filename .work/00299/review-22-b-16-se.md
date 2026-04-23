# Expert Review: Software Engineer — Phase 22-B-16

**Date**: 2026-04-23
**Reviewer**: AI Agent as Software Engineer (bias-avoidance subagent)
**Target**: Phase 22-B-16 link handling rewrite design

## Summary

Direction is sound (unify 7 link kinds through CommonMark, add `level`, strengthen QL1 on docs MD), but the initial "diverge JSON / docs MD strings" path violates `rbkc-verify-quality-design.md` §3-3 QO2 ("JSON 各セクションの `content` が docs MD に完全一致で含まれている"). That clause is the only load-bearing invariant that catches content drift between the two outputs — it must be preserved.

## Findings

### F1. Divergent link strings break QO2 verbatim containment
- **Violated clause**: `rbkc-verify-quality-design.md` §3-3 QO2: *"JSON 各セクションの `content` が docs MD に完全一致で含まれている"*.
- **Description**: Diverging strings forces relaxing QO2, which `.claude/rules/rbkc.md` forbids: *"Never weaken verify's detection to make RBKC output pass"*.
- **Fix**: Emit **identical** link strings in JSON content and docs MD. Use the docs MD form (`../other/file_id.md#anchor`) in both. AI consumers read JSON content as text — they do not path-dereference. QO2 stays strict.

### F2. `#s1/s2/s3` anchor is not verifiable against GitHub Web
- **Violated clause**: §2-2 verify independence: verify derives anchors from source-format spec, not from RBKC output.
- **Description**: GitHub Web auto-generates heading anchors by slugifying heading text; it does not honor `id="s3"`. A `#s3` link is dead on GitHub Web.
- **Fix**: Anchor = GitHub slug of the section title. Implement slug algorithm in `scripts/common/github_slug.py`. verify QO1 independently recomputes the slug; QL1 asserts the emitted `#anchor` equals the slug of the resolved target title in the target file.

### F3. Current `label_map` is insufficient for `:ref:` resolution
- **Violated clause**: `rbkc-converter-design.md` rule "未解決 reference → FAIL" (zero-exception).
- **Description**: Current `labels.py` returns only `label → title`. To emit `[title](../xxx/file_id.md#anchor)` the resolver needs `label → (title, file_id, section_title_for_anchor)`.
- **Fix**: Extend `build_label_map` to return `dict[str, LabelTarget]` where `LabelTarget = (title, file_id, section_title)`. Belongs in `scripts/common/labels.py` per §2-2.

### F4. `:doc:` has no `doc_map` today
- **Violated clause**: zero-exception rule. `rst_ast_visitor.inline_inline` currently drops `:doc:` to just the basename, losing the resolvable target (237 occurrences in v6 are active latent defects).
- **Fix**: Add `build_doc_map(source_dir) → dict[rst_relpath → (title, file_id)]` in `scripts/common/labels.py`.

### F5. Image path rewriting is pattern-matched, not structural
- **Violated clause**: `rbkc-converter-design.md` zero-exception / `.claude/rules/review-feedback.md` horizontal check.
- **Description**: `docs.py:_rewrite_asset_links` only rewrites when URL literally starts with `assets/`. RST-relative paths (`../images/foo.png`) silently pass through → 404. Silent fallback — forbidden.
- **Fix**: Converter (not docs writer) resolves `.. image::` / `.. figure::` URIs at AST time against source file directory, copies asset to `knowledge/assets/{file_id}/{basename}`, emits `assets/{file_id}/{basename}` into JSON content. docs.py then rewrites the single canonical `assets/` prefix.

### F6. `numref` declared KNOWN but not resolved
- **Violated clause**: zero-exception. `_KNOWN_ROLES` includes `numref`, but `inline_inline` handles it identically to `:doc:` (basename fallback) — silent text degradation.
- **Fix**: Route `:numref:` through the same label→target resolver.

## Recommendation per design question

1. **Correctness / anchor choice**: Anchor must be the **GitHub slug of the target section title**, not `#s3`. Implement slug in `scripts/common/github_slug.py`. verify independently recomputes the slug from `section.title` + target file's section list — no circular check.

2. **JSON vs docs MD divergence — pick identical-string option**: Emit **identical strings in both**, using docs MD form (`[title](../xxx/file_id.md#anchor)` and `![alt](../../knowledge/assets/{file_id}/foo.png)`). For assets, emit `assets/{file_id}/{name}` in both and let docs.py rewrite to `../../knowledge/assets/...`. QO2 does the identical rewrite on the JSON string before containment check — deterministic source-independent transform, permitted under §2-2 "出力間整合の参照".

3. **Scope — split into 3 PRs**:
   - **22-B-16a**: `Section.level` + docs.py heading emission + QO1 level check. No link changes.
   - **22-B-16b**: `anchors.py` slug + `labels.py` extended + `doc_map` + create-side `:ref:` / `:doc:` / `:numref:` emit as MD link. QL1 docs-side check. Bulk of ~6,500 transforms.
   - **22-B-16c**: image / figure asset resolution + docs.py path rewrite unification. 606 transforms.
   Each slice has an independent verify gate (QO1, QL1, QL1-asset).

4. **Verify design impact**: slug, label_map, doc_map all live in `scripts/common/` per §2-2. verify **must not** consume create-built label_map; verify rebuilds from source via the same pure `common/` function.

5. **Horizontal class — "converter discards link structure that cannot be reconstructed"**:
   - `inline_inline` roles: `:doc:` (basename fallback, 237), `:numref:` (basename fallback, 0 v6 / unknown v5), `:download:` (raw text, 53), `:file:` / `:command:` / `:samp:` / `:envvar:` / `:kbd:` / `:guilabel:` / `:menuselection:` / `:term:` / `:abbr:` / `java:extdoc` / `javadoc_url` (all return `raw`)
   - `inline_reference` with `refid` only: returns plain text — same bug as `:ref:`
   - `visit_image` / `visit_figure`: URI pass-through without asset copy
   - `literalinclude` via `visit_literal_block`: source path lost; filename should be kept as `// file: path` comment on fence

6. **Production risk**, ranked by blast radius:
   - Wrong anchor slug algorithm for Japanese → 5,582 dead `:ref:` links on GitHub Web
   - Asset not copied to `knowledge/assets/{file_id}/` because resolver missed a relative form → 404 image
   - `doc_map` collision when two RST files have same relpath stem → silent wrong-target
   - `:ref:` unresolved in v5/v1.x corpora that v6-based slug algorithm never saw → runtime FAIL

## Positive aspects

- Adding `Section.level` is overdue — the current flat `##` emission is a latent QO1 bug the spec already implies
- Strengthening QL1 to check docs MD is strictly within §3-2 QL1 intent (spec already lists "docs MD での期待形式" columns)
- "Hierarchy must be fixed before anchors" insight is correct: unstable slug dedup (`slug-1/-2`) would otherwise fluctuate with h2/h3 collapse

## Files to change (absolute paths)

- `tools/rbkc/scripts/common/rst_ast_visitor.py` (Section.level, inline_inline for :doc:/:numref:/:download:, visit_image/figure URI resolution, inline_reference refid path, _walk_section level tracking)
- `tools/rbkc/scripts/common/md_ast_visitor.py` (parallel level + link handling)
- `tools/rbkc/scripts/common/labels.py` (LabelTarget, doc_map)
- `tools/rbkc/scripts/common/github_slug.py` (new, GitHub slug)
- `tools/rbkc/scripts/create/docs.py` (emit ## / ### / ####, single canonical asset prefix rewrite)
- `tools/rbkc/scripts/create/converters/rst.py` (image/figure asset copy)
- `tools/rbkc/scripts/verify/verify.py` (QO1 level match, QL1 docs-side dangling-link + anchor-exists, QO2 asset-prefix rewrite before containment)
- `tools/rbkc/docs/rbkc-json-schema-design.md` (add `sections[].level`)
- `tools/rbkc/docs/rbkc-converter-design.md` (link / level mapping table)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` (QO1/QL1 expanded; confirm asset-prefix rewrite is deterministic pre-check)
