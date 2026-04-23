# SE Design Review: Phase 22-B-16b-main

**Date**: 2026-04-23
**Reviewer**: AI Agent as Software Engineer
**Scope**: Labels extension + ref/doc/numref MD-link emission + QL1 two-sided verify

## Q1. Label map plumbing — **version/repo_root threaded, single call**

Change `run.py` to call `build_label_doc_map(version, repo_root)` **once**. Rationale:

- `LabelTarget` requires `derive_file_id(source, fmt, version, repo_root, mappings=...)`. The mapping is a per-version artifact — passing `(version, repo_root)` once is cheaper and cleaner than threading them through three call sites and three merge loops.
- Internally the function should load mappings once and walk `_source_roots(version, repo_root)` — identical to current loop, but encapsulated. This keeps the per-root walk as an implementation detail of labels.py, where it belongs (it already owns the rglob).
- Replaces 3 duplicated loops in `create` / `create_changed` / `verify` (run.py L196–200, L237–240, L333–336) with one call each.

## Q2. RST visitor contract — **`dict[str, LabelTarget]` only; UNRESOLVED becomes a LabelTarget**

Redefine `UNRESOLVED` as `LabelTarget(title="", file_id="", section_title="", category="")` sentinel (singleton, compared by identity: `is UNRESOLVED`). Rationale:

- Union types propagate: every consumer (rst_ast_visitor, verify `_resolve_title_inline`, verify QL1) is forced to `isinstance`-branch forever. Current code already leaks this via `r if isinstance(r, str) else getattr(r, "title", str(r))` — that is a code smell, not a design.
- A singleton `LabelTarget` sentinel gives one shape. Detection is `target is UNRESOLVED` (identity, O(1), no string compare, no attribute probe).
- Preserves the 22-B-16a horizontal-class fix: orphans are still stamped explicitly, not dropped. Spec §3-2-2 compliance unchanged.

String-typed `UNRESOLVED` stays exported for one release as `UNRESOLVED_TITLE = ""` if any external caller depended on it — grep confirms none do.

## Q3. doc_map resolution — **visitor takes `source_path`; resolve at visit time**

Add `source_path: Path` to `_MDVisitor.__init__`. For `:doc:\`x/y\``, resolve via `(source_path.parent / target).resolve().relative_to(version_source_root)` → doc_map key. Rationale:

- Pre-processing AST rewrite means a second pass over every doctree, duplicating walk cost and losing source context across the boundary.
- The visitor already owns `source_path` semantically (`render_text(text, source_path=...)` in existing signature at L757). Passing it to `__init__` is the minimal change.
- doc_map key = rst-relpath **relative to the matched source root** (not repo_root) — avoids v1.x marker ambiguity since `derive_file_id` already normalises.

## Q4. MD relative link — **same mechanism as Q3**

md_ast_visitor gets the same `source_path` parameter. `link_open` handler: if `href` is relative and not `http(s)/mailto/tel/#`, resolve `(source_path.parent / href).resolve()` against the MD source root, then look up the **combined** doc_map (RST entries keyed by `.rst` relpath, MD entries keyed by `.md` relpath — same map, extensions differentiate).

## Q5. Verify AST walk — **new independent pass, not folded into normalize**

Add `check_source_links_two_sided(source_text, fmt, json_data, docs_md_text, label_map, doc_map, source_path)` as a **new** top-level check in verify.py. Rationale:

- Rule `.claude/rules/rbkc.md`: verify is independent of RBKC internals. Folding into `_normalize_rst_source` couples detection to the normalisation pipeline (which exists to serve content-diff, not link validation).
- Two-sided QL1 has distinct failure modes (link missing in JSON / link missing in docs MD / target file missing / anchor slug mismatch). Each wants its own assertion site with a precise message. A separate pass gives that.
- Independent pass also lets verify tests target it in isolation (TDD per `.claude/rules/rbkc.md`).

## Q6. Scope split — **four commits, atomic per commit, chained on one branch**

ゼロトレランス requires no regression; atomic rollback requires small blast radius:

1. `feat(rbkc): labels.py — LabelTarget + build_label_doc_map` (labels + tests, no call sites touched; UNRESOLVED becomes LabelTarget sentinel).
2. `feat(rbkc): rst_ast_visitor — emit MD links for :ref:/:doc:/:numref:` (consumes new label_map shape; docs_md output changes — verify QO2 must still pass).
3. `feat(rbkc): md_ast_visitor — resolve relative links via doc_map`.
4. `feat(rbkc): verify QL1 two-sided source-link check` (new pass + tests).

Each commit must keep **v6 verify FAIL = 0** before proceeding. If commit 2 regresses v6, commits 3/4 are blocked until fixed — the chain prevents partial landings from sitting on main.

Single atomic commit rejected: ~5 files, >500 LOC change, new semantics in 3 layers. Bisect cost and review cost both drop with the split. CHANGELOG entry (user-facing: "cross-document links now navigable in docs") lands with commit 4.

## Positive Aspects

- Prep refactor (`c99d9992b`) correctly isolated `derive_file_id` in common, making this feature a non-breaking addition rather than a cross-cutting rewrite.
- UNRESOLVED sentinel from 22-B-16a is the right foundation; promoting it to a LabelTarget singleton is a type cleanup, not a semantic change.
- Existing defensive `getattr(r, "title", ...)` in rst_ast_visitor already anticipates LabelTarget — migration surface is smaller than it looks.
