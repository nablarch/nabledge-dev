# Expert Review: 22-B-16b step 3 + step 4 + 22-B-16c

**Date**: 2026-04-23
**Reviewer**: AI Agent as Software Engineer + QA Engineer (combined)
**Files Reviewed**: 7 source files + 1 test file across commits `5e70d5c83`, `6b828cd01`, `86549073d`
**Context**: MD relative link → cross-doc MD link; cross-type path fix; asset URI rewrite + QL1 asset-exists

## Summary

**4 Findings — not shippable**

---

## Findings

### F1. `scripts/common/labels.py` imports `scripts.create.classify` — §2-2 layering violation

**Violated clause** (`rbkc-verify-quality-design.md` §2-2, lines 45-48):

> **ソースフォーマット仕様由来の共通ロジック**は create と verify の両方から利用してよい (...)
> - `scripts/common/` 配下のモジュール (**RST 仕様由来の純粋ロジック層**)

and §2-2 line 42:

> verify → create 実装 の依存は禁止 (`scripts/create/` 配下の converters / resolver / run 等をインポートしない)

**Description**: commit `6b828cd01` patches `build_label_doc_map` to lazy-import `scripts.create.classify.classify_sources` and `scripts.create.scan.scan_sources`. Even though the import is lazy and verify currently only calls `build_label_map`, `common/labels.py` is now a `common/` module that reaches into `create/`. §2-2 line 47 defines `common/` as **RST-仕様由来の純粋ロジック層**; collision disambiguation is a create-side concern, not RST spec. Any future verify caller of `build_label_doc_map` would transitively import `create/`, breaking §2-2 line 42.

**Fix**: Move collision disambiguation into `common/file_id.py` (or a new `common/classify_pure.py`) as a pure function `classify_for_labels(sources, mappings) -> list[FileInfo]` that uses only `common/` dependencies; `create/classify.py` keeps its create-specific wrapping and delegates to it. `build_label_doc_map` calls the pure helper. This keeps layering intact while preserving the disambiguation fix.

---

### F2. `_CROSSDOC_LINK_RE` / `_ASSET_LINK_RE` regex-scan JSON content — violates the spirit of §3-2 AST 経由原則 and risks code-block false positives

**Violated clause** (`rbkc-verify-quality-design.md` §3-2 line 262):

> **AST 経由原則**: QL1 / QL2 の抽出は、ソースフォーマットの公式パーサーで取得した AST から読み取る。ソースを行単位の regex で直接走査してはならない (...)

and `.claude/rules/rbkc.md` (ゼロトレランス / 1% リスク):

> If there is even a 1% risk, eliminate it

**Description**: `check_ql1_link_targets` iterates `_CROSSDOC_LINK_RE.finditer(text)` and `_ASSET_LINK_RE.finditer(text)` over raw JSON `content` strings. JSON content is CommonMark MD that **contains fenced code blocks** (e.g. snippets from `.. code-block::`). A code sample that happens to contain the literal substring `](../../foo/bar/baz.md)` or `](assets/x/y.png)` — perfectly plausible in Nablarch docs that show config paths or sample Markdown — would be treated as a real link and FAIL if the path doesn't resolve. §3-2 is explicit that QL1 must use AST-based extraction precisely because regex-based extraction misidentifies links inside other syntactic constructs.

The rule targets source scanning, but the **reason** ("formatting context confusion") applies identically to JSON content scanning. Under ゼロトレランス, a 1% false-positive risk is not acceptable when the alternative (parsing the JSON MD with `markdown-it-py` and reading `link_open` tokens) is equally cheap.

**Fix**: Replace both regexes with AST-based extraction: feed `text` into `scripts.common.md_ast.parse(...)` and collect hrefs from `link_open` tokens whose href matches the cross-doc / asset shapes. Code-block content is not exposed as `link_open`, so FPs are structurally impossible.

---

### F3. `_MDVisitor._render_block_group` creates a sub-visitor without `doc_map` / `source_path` — silent skip of link rewriting inside lists / blockquotes

**Violated clause** (`rbkc-verify-quality-design.md` §3-2-2 line 292):

> verify は QL1 WARNING としてログに列挙する (**silent skip 禁止は維持**)。

and `.claude/rules/rbkc.md`:

> Silent skips are forbidden (spec §3-2-2)

**Description**: In `md_ast_visitor.py` line 336:
```python
sub = _MDVisitor()                     # no doc_map, no source_path
sub.external_urls = self.external_urls # link buckets reused
sub.internal_links = self.internal_links
sub.images = self.images
```
`sub.walk(tokens)` will hit `_resolve_md_relative_href` with `self._source_path is None`, which returns `[text](href)` verbatim **with no warning**. Any relative MD link inside a list item, blockquote, or nested block is silently not rewritten and no WARNING is emitted — the exact shape §3-2-2 forbids. `sub.warnings` is also not copied back to the parent.

**Fix**: Propagate the visitor's link-resolution context and warnings list when constructing the sub-visitor:
```python
sub = _MDVisitor(doc_map=self._doc_map, source_path=self._source_path)
...
self.warnings.extend(sub.warnings)
```

---

### F4. Four-way drift risk: `_render_label_target` (rst), `_resolve_md_relative_href` (md), `_resolved_text` (verify), and `_CROSSDOC_LINK_RE` (verify) all encode the `../../{type}/{cat}/{file_id}.md[#anchor]` literal — QO2 byte-equality will break silently if any drifts

**Violated clause** (`.claude/rules/rbkc.md` — "verify is the quality gate / Never weaken verify's detection") in combination with `.claude/rules/rbkc.md` "Tests must be spec-pinned, not implementation-pinned":

> verify must never import from or depend on RBKC implementation modules

**Description**: Spec §3-2-3 Row 1 / 3 / 5 define the link shape `../../{type}/{category}/{file_id}.md[#anchor]` as the canonical form. Today that literal appears in four places:
1. `rst_ast_visitor._MDVisitor._render_label_target` (create-side emission)
2. `md_ast_visitor._MDVisitor._resolve_md_relative_href` (create-side MD emission)
3. `verify._resolve_title_inline._resolved_text` (verify-side source normalisation)
4. `verify._CROSSDOC_LINK_RE` (verify-side extraction regex)

If any one copy drifts (e.g. someone later adds a trailing slash, or changes `..` depth), QC1/QC2/QO2 byte-equality checks would either pass silently (because create and verify both drift together via a copy-paste fix) or FAIL in one place while create & docs stay consistent. Under ゼロトレランス "1% risk も許容しない", four synchronised literal sites is a latent drift mine.

**Fix**: Introduce a single source of truth in `scripts/common/linkfmt.py`:
```python
def emit_crossdoc_link(display: str, type_: str, category: str, file_id: str, anchor: str = "") -> str: ...
CROSSDOC_LINK_RE = re.compile(...)  # pinned to the same shape
```
All four sites consume this module. The regex and the emitter must be proven consistent by a unit test: generate `N` random (display, type, cat, file_id, anchor) tuples, format via `emit_crossdoc_link`, then assert `CROSSDOC_LINK_RE.fullmatch` yields the original components. This is a spec-pinned test, not circular, because it only tests that format / parse round-trip.

---

## Observations

Non-blocking notes, no clause violation.

- **O1** — `copy_assets` in `scripts/create/resolver.py` line 97-98 silently skips missing source files. QL1 asset-exists compensates on the verify side, so no observable gap today, but tightening to `WARNING` (not FAIL, per §3-2-2) would make the handoff to verify explicit. Pre-existing code, not introduced by these commits.
- **O2** — `_rewrite_asset_uri` passes through absolute-path URIs (`/abs/x.png`). Matches Sphinx behaviour so §3-2 Sphinx 追従原則 covers it, but two images with the same basename in different source dirs would collide at `assets/{file_id}/{basename}` under `copy_assets` (last write wins). v6 did not trip this, but it is a silent-collision risk worth a unit test for a future version.
- **O3** — The suffix-match longest-wins logic in `_resolve_md_relative_href` and `_resolve_doc_target` is correct (longest key wins, no shorter-suffix false positive possible given doc_map keys come from real source paths). Explicit test would be useful but not required.
- **O4** — `DocumentParts.warnings` is assigned post-construction in `extract_document` (`parts.warnings = list(v.warnings)`) rather than passed via the dataclass constructor. Works today because `DocumentParts` is mutable; would break if someone later marks it `frozen=True`. Low risk but trivial to harden by passing `warnings=v.warnings` into the constructor.
- **O5** — `TestCheckQL1LinkTargets` covers only `component/libraries` → `component/libraries`. A cross-type test (`about/migration/...` → `component/adapters/...`) would directly pin the fix in commit `6b828cd01`.

## Positive Aspects

- Dangling-link WARNING plumbing is thorough: `warnings_out` threaded through `normalise_rst` / `normalise_md` / `_normalize_rst_source` / `_check_md_content_completeness` → `sys.stderr`, so §3-2-2 "WARNING ログ + display text fallback" is honoured on both RST and MD sides.
- `build_label_doc_map` refactor correctly routes through `classify_sources` to pick up collision disambiguation — the underlying defect diagnosis is sound; only the layering placement is wrong (F1).
- QL1 two-sided check covers both JSON target and docs MD target (when present), matching spec §3-2-3 table columns 4 and 5.
- New tests are clause-pinned (existence of target JSON / MD / asset on disk), not implementation-pinned — avoids the circular-test trap called out in `.claude/rules/rbkc.md`.
- `:download:` handling correctly parses both `text <path>` and bare `path` forms; empty `file_id` degrades to display text rather than emitting a broken link.

## Files Reviewed

- `tools/rbkc/scripts/common/md_ast_visitor.py` (source code, steps 3 + 16c)
- `tools/rbkc/scripts/common/md_normaliser.py` (source code, step 3)
- `tools/rbkc/scripts/common/labels.py` (source code, step 4)
- `tools/rbkc/scripts/common/rst_ast_visitor.py` (source code, steps 4 + 16c)
- `tools/rbkc/scripts/common/rst_normaliser.py` (source code, 16c)
- `tools/rbkc/scripts/create/converters/md.py` (source code, step 3)
- `tools/rbkc/scripts/create/converters/rst.py` (source code, 16c)
- `tools/rbkc/scripts/run.py` (source code, all three commits)
- `tools/rbkc/scripts/verify/verify.py` (source code, all three commits)
- `tools/rbkc/tests/ut/test_verify.py` (tests, steps 4 + 16c)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` (spec, step 4)
