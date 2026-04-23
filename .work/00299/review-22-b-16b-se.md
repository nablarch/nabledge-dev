# Expert Review: Software Engineer — Phase 22-B-16b scope design

**Date**: 2026-04-23
**Reviewer**: AI Agent as Software Engineer (bias-avoidance subagent)
**Target**: 22-B-16b implementation strategy — where does file_id derivation live?

## Summary

Recommendation: **Option A (move file_id derivation to `scripts/common/file_id.py`) + split 22-B-16b into -prep and -main**.

## Rationale

Option B/C force verify to re-derive `file_id` independently → two implementations of the same naming spec → guaranteed drift when mappings evolve. That violates §2-2 in spirit (verify must be derivable from the spec). The spec *is* `mappings/v{version}.json` + naming rules — those rules belong in `scripts/common/`. Both sides legitimately need them.

Option A is the only path with a single authoritative derivation.

## Concrete plan

### New file: `scripts/common/file_id.py`

```python
def load_mappings(version: str, repo_root: Path) -> dict: ...
def rel_for_classify(path: Path, version: str) -> str: ...
def derive_file_id(
    source_path: Path, format: str, version: str, repo_root: Path,
    *, mappings: dict | None = None,
) -> FileClass | None

# FileClass: frozen dataclass(source_path, format, file_id, type, category, matched_pattern)
# Returns None for unclassified sources.
# Does NOT handle xlsx sheet split or collision disambiguation.
```

### Code moves (pure motion, no behaviour change)

- `scan.py:24-32` `_load_mappings` → `common/file_id.py::load_mappings`
- `scan.py:62-81` `_rel_for_classify` → `common/file_id.py::rel_for_classify`
- `classify.py:31-80` `_generate_id` → `common/file_id.py` (module-private)
- `classify.py:170-257` rst/md/xlsx-exact/xlsx-pattern branch logic → `common/file_id.py::derive_file_id`

### Stays in create/classify.py

- Sheet-split loop (L259-283), `_disambiguate`, `_parent_prefix`, `_sheet_slug` (xlsx-specific, output-path-specific)
- `classify_sources` becomes a thin wrapper: iterate sources → `derive_file_id` → sheet-split → disambiguate

### labels.py gains a second entry point (non-breaking)

```python
@dataclass(frozen=True)
class LabelTarget:
    title: str | None
    file_id: str | None
    category: str | None
    section_title: str

def build_label_doc_map(
    version: str, repo_root: Path,
) -> dict[str, LabelTarget]: ...
```

Internally: walk source roots, call `derive_file_id` per RST file, run label/heading scan, join on RST path. Zero dependency on `scripts.create`.

## Tests (TDD, spec-pinned, not implementation-pinned)

- `tests/ut/test_file_id.py`: parametrise over `mappings/v6.json` rst entries; each test asserts `derive_file_id(path)` yields the `{type, category, file_id}` the **mapping rules** prescribe. Oracle hand-computed from mapping, NOT from `classify_sources` output.
- Edge cases: top-level `index.rst`; two `index.rst` under different patterns; xlsx exact; v1.x markers.
- Negative: unmapped path → None.
- `tests/ut/test_labels_doc_map.py`: fixture RST tree with cross-doc `:ref:` target → asserts `LabelTarget.file_id` matches spec-derived id.

## Scope split: yes

- **22-B-16b-prep**: Move derivation to `common/file_id.py`, refactor classify.py + scan.py to re-export, add spec-pinned tests. Zero behavioural change — verify output bit-identical to pre-prep. SE review. Commit.
- **22-B-16b-main**: Add `LabelTarget` + `build_label_doc_map`, wire into RST converter to emit MD links, update verify QL1 two-sided. SE + QA review. Commit.

Prep lands as a clean refactor PR (reviewable on its own, low risk, easy revert). Main PR then becomes a pure feature diff. Bundling them hides the refactor inside a feature review and makes rollback coupled.

## Files Reviewed

- `tools/rbkc/scripts/create/scan.py`
- `tools/rbkc/scripts/create/classify.py`
- `tools/rbkc/scripts/create/run.py`
- `tools/rbkc/scripts/common/labels.py`
- `tools/rbkc/scripts/verify/verify.py`
- `tools/rbkc/mappings/v6.json` (schema)
