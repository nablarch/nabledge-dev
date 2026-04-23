"""Common: source → (type, category, file_id) derivation.

Phase 22-B-16b-prep: the naming spec (``mappings/v{N}.json`` rules + the
file_id composition rules) is the single source of truth for how a source
path becomes an output file_id.  Both the create side (``create/classify.py``)
and the verify side (upcoming QL1 two-sided check in Phase 22-B-16b-main)
need to resolve sources → file_id identically.

Rather than duplicating the rules in two places (which would drift when
``mappings/`` evolves), the derivation lives here.  ``create/classify.py``
remains the place where xlsx sheet-level expansion and collision
disambiguation happen — those are output-path concerns, not naming concerns.

Public API
----------
- :func:`load_mappings` — read ``mappings/v{N}.json``.
- :func:`rel_for_classify` — extract the path segment used for pattern matching.
- :func:`derive_file_id` — produce a :class:`FileClass` for a single source,
  or ``None`` for unclassified sources.
- :class:`FileClass` — immutable value type carrying ``(source_path, format,
  type, category, file_id, matched_pattern)``.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileClass:
    source_path: Path
    format: str            # 'rst', 'md', 'xlsx'
    type: str
    category: str
    file_id: str
    matched_pattern: str   # "" if pattern not applicable (md, xlsx-exact, top-index)


def load_mappings(version: str, repo_root: Path) -> dict:
    """Load RBKC mapping file for the given version.

    Raises :class:`FileNotFoundError` if ``mappings/v{version}.json`` is absent.
    """
    mapping_path = repo_root / "tools/rbkc/mappings" / f"v{version}.json"
    if not mapping_path.exists():
        raise FileNotFoundError(
            f"Mapping file not found: {mapping_path}\n"
            f"Create tools/rbkc/mappings/v{version}.json to support this version."
        )
    return json.loads(mapping_path.read_text(encoding="utf-8"))


def rel_for_classify(path: Path, version: str) -> str:
    """Extract the path segment used for pattern matching.

    For v5/v6: strip everything up to and including ``nablarch-document/ja/``.
    For v1.x: keep the source root marker (``document/`` / ``workflow/`` / etc.)
    because v1.x mapping patterns are namespaced by that marker.
    """
    markers = {
        "5": "nablarch-document/ja/",
        "6": "nablarch-document/ja/",
        "1.4": ("document/", "workflow/", "biz_sample/", "ui_dev/"),
        "1.3": ("document/", "biz_sample/"),
        "1.2": ("document/",),
    }
    raw = str(path).replace("\\", "/")
    marker_list = markers.get(version, ("nablarch-document/ja/",))
    if isinstance(marker_list, str):
        marker_list = (marker_list,)
    for marker in marker_list:
        idx = raw.find(marker)
        if idx >= 0:
            if version.startswith("1.") and marker != "document/":
                return marker + raw[idx + len(marker):]
            return raw[idx + len(marker):]
    return path.name


def _generate_id(
    filename: str,
    fmt: str,
    category: str,
    source_path: Path,
    matched_pattern: str,
    version: str,
    *,
    xlsx_exact: bool = False,
    extra_prefix: str = "",
) -> str:
    """Compose a file_id from filename/category/pattern context.

    This function is a pure transformation of the mapping spec: it does NOT
    read files, does NOT inspect output directories, and does NOT resolve
    collisions.  Collision disambiguation lives in ``create/classify.py``.
    """
    # xlsx exact-filename matches have the category itself as the file_id
    if fmt == "xlsx" and xlsx_exact:
        return category

    if fmt == "rst":
        base = filename[:-4]
    elif fmt == "md":
        base = filename[:-3]
    else:
        base = Path(filename).stem

    # index.rst special handling: use path context to avoid {category}-index collisions
    if base == "index" and source_path is not None and matched_pattern:
        rel = rel_for_classify(source_path, version)
        pattern_clean = matched_pattern.rstrip("/")
        if not pattern_clean:
            base = "top"
        else:
            idx = rel.find(pattern_clean)
            if idx >= 0:
                remainder = rel[idx + len(pattern_clean):].strip("/")
                if remainder == "index.rst":
                    base = Path(pattern_clean).name
                else:
                    dir_part = str(Path(remainder).parent)
                    if dir_part == ".":
                        base = Path(pattern_clean).name
                    else:
                        base = dir_part.replace("/", "-").replace("_", "-")

    base = base.replace("_", "-")
    if extra_prefix:
        extra_prefix = extra_prefix.replace("_", "-")
        if category:
            return f"{category}-{extra_prefix}-{base}"
        return f"{extra_prefix}-{base}"
    if category:
        return f"{category}-{base}"
    return base


def _match_rst(
    rel: str, mappings: dict
) -> tuple[str | None, str | None, str | None]:
    """Return (type, category, matched_pattern) for an RST rel path."""
    # Longest pattern wins — callers typically pre-sort, but we sort here too
    # so derive_file_id is correct regardless of input order.
    rst_entries = sorted(
        mappings.get("rst", []),
        key=lambda e: len(e["pattern"]),
        reverse=True,
    )
    for entry in rst_entries:
        if entry["pattern"] in rel:
            return entry["type"], entry["category"], entry["pattern"]
    return None, None, None


def derive_file_id(
    source_path: Path,
    format: str,
    version: str,
    repo_root: Path,
    *,
    mappings: dict | None = None,
) -> FileClass | None:
    """Derive ``(type, category, file_id)`` for a single source file.

    Returns ``None`` when the source does not match any mapping entry (and is
    not the top-level ``index.rst`` fallback).

    This function does **not** handle xlsx sheet-level expansion or output
    collision disambiguation — those transforms live in
    ``create/classify.py`` because they only make sense when a whole source
    set is known.
    """
    if mappings is None:
        mappings = load_mappings(version, repo_root)

    rel = rel_for_classify(source_path, version)
    type_: str | None = None
    category: str | None = None
    matched_pattern: str | None = None
    is_xlsx_exact = False

    if format == "rst":
        type_, category, matched_pattern = _match_rst(rel, mappings)
        if type_ is None:
            if rel == "index.rst":
                type_, category, matched_pattern = (
                    "about",
                    "about-nablarch",
                    "",
                )
            else:
                return None

    elif format == "md":
        md_mapping: dict = mappings.get("md", {})
        filename = source_path.name
        if filename in md_mapping:
            info = md_mapping[filename]
            type_ = info["type"]
            category = info["category"]
            matched_pattern = ""
        else:
            return None

    elif format == "xlsx":
        xlsx_exact: dict = mappings.get("xlsx", {})
        xlsx_patterns: list = mappings.get("xlsx_patterns", [])
        filename = source_path.name
        if filename in xlsx_exact:
            info = xlsx_exact[filename]
            type_ = info["type"]
            category = info["category"]
            matched_pattern = ""
            is_xlsx_exact = True
        else:
            for pat in xlsx_patterns:
                if filename.endswith(pat["endswith"]):
                    type_ = pat["type"]
                    category = pat["category"]
                    matched_pattern = ""
                    break
            if type_ is None:
                return None
    else:
        return None

    file_id = _generate_id(
        source_path.name,
        format,
        category or "",
        source_path,
        matched_pattern or "",
        version,
        xlsx_exact=is_xlsx_exact,
    )

    return FileClass(
        source_path=source_path,
        format=format,
        type=type_ or "",
        category=category or "",
        file_id=file_id,
        matched_pattern=matched_pattern or "",
    )
