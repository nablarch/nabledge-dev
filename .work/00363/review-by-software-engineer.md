# Expert Review: Software Engineer

**Date**: 2026-06-04
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: tools/rbkc/scripts/common/javadoc_fqcn.py, tools/rbkc/scripts/create/javadoc.py, tools/rbkc/scripts/verify/verify.py, tools/rbkc/scripts/common/rst_ast_visitor.py, tools/rbkc/scripts/common/linkfmt.py, tools/rbkc/scripts/create/docs.py

## Summary

1 Finding — not shippable

## Findings

### Finding 1: `rst_ast_visitor.py` imports from `scripts.create.javadoc` instead of `scripts.common.javadoc_fqcn`

- **Violated clause**: `.claude/rules/rbkc.md` line 8: "verify must never import from or depend on RBKC implementation modules (converters, resolver, run, etc.)"
- **Description**: `scripts/common/rst_ast_visitor.py` line 801 contains `from scripts.create.javadoc import _class_fqcn, fqcn_to_file_id`. `rst_ast_visitor.py` is used by the verify pipeline (via `rst_normaliser.py`), so verify transitively imports a create-side module. Additionally, `fqcn_to_file_id` is imported but never used — dead import. `javadoc_fqcn.py` exists precisely to be the single source of truth for FQCN normalisation.
- **Fix**: Replace line 801 with `from scripts.common.javadoc_fqcn import class_fqcn as _class_fqcn`. Remove the `fqcn_to_file_id` import entirely (dead code).

## Observations

- **Cache skip asymmetry**: `javadoc_generate`'s cache-hit path skips `_write_docs_md`. If `docs/javadoc/` is cleaned without cleaning `knowledge/javadoc/`, docs MD files would be missing. Not a spec violation, but a comment documenting this trade-off would help future readers.
- **`_extract_fqcns` vs AST parser**: The FQCN collection pass uses a simple regex while `rst_ast_visitor` uses the docutils AST. Explicitly documented as intentional; tests confirm correctness.
- **`_bom_version` hardcoded mapping** (v6→"6u3", v5→"5u26"): Needs updating as Nablarch releases new BOM versions. A comment noting this would reduce future maintenance risk.
- **`_parse_javadoc_md` handles only `##`/`###` headings**: If Nablarch Javadoc ever uses `####`, parsing would skip it. Not a current issue, but no guard or comment explains this assumption.

## Positive Aspects

- Create/verify symmetry is well-enforced via `javadoc_fqcn.py` as the single source of truth.
- `docs/javadoc/` README exclusion is correctly implemented using `p.is_relative_to(javadoc_dir)`.
- QL1 extdoc quadrant check correctly implements the five-quadrant spec with explicit spec citations.
- `javadoc_fqcn.py` is thoroughly tested across all normalisation steps.
- All 394 unit tests pass.

## Files Reviewed

- tools/rbkc/scripts/common/javadoc_fqcn.py (source code)
- tools/rbkc/scripts/create/javadoc.py (source code)
- tools/rbkc/scripts/verify/verify.py (source code)
- tools/rbkc/scripts/common/rst_ast_visitor.py (source code)
- tools/rbkc/scripts/common/linkfmt.py (source code)
- tools/rbkc/scripts/create/docs.py (source code)
