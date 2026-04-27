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


# ---------------------------------------------------------------------------
# Collision disambiguation (pure — no filesystem reads)
# ---------------------------------------------------------------------------
# Phase 22-B-16b step 4 F1 fix: create-side's ``classify_sources`` used to
# own collision disambiguation, but ``common/labels.py`` needs the same
# disambiguation to build label_map file_ids that match what create will
# eventually write.  Keeping the logic in create/ forced common/ to
# import create/ — a layering violation (spec §2-2).  The pure helpers
# below live in common/ so both sides can consume them without reaching
# into create/.


def _parent_prefix(source_path: Path, levels: int) -> str:
    parts = source_path.parts
    dirs = parts[max(0, len(parts) - 1 - levels):len(parts) - 1]
    return "-".join(p.lower().replace("_", "-") for p in dirs)


def disambiguate_file_classes(
    items: list[tuple[str, FileClass]],
    version: str,
) -> list[tuple[str, FileClass]]:
    """Resolve output-path collisions by adding 1 then 2 parent-dir
    prefixes to the file_id.  Input/output are ``(output_path, FileClass)``
    tuples so callers can build whatever wrapper type they need without
    ``common/`` depending on it.

    Raises :class:`ValueError` when collisions remain after 2 levels.
    """
    from collections import defaultdict

    def _find_collisions(entries):
        by_out: dict[str, list] = defaultdict(list)
        for out, fc in entries:
            by_out[out].append((out, fc))
        return {k: v for k, v in by_out.items() if len(v) > 1}

    def _regenerate(colliding, levels: int):
        result = []
        for _out, fc in colliding:
            prefix = _parent_prefix(fc.source_path, levels)
            new_id = _generate_id(
                fc.source_path.name,
                fc.format,
                fc.category,
                fc.source_path,
                "",
                version,
                xlsx_exact=(fc.format == "xlsx" and fc.file_id == fc.category),
                extra_prefix=prefix,
            )
            new_out = f"{fc.type}/{fc.category}/{new_id}.json"
            result.append(
                (
                    new_out,
                    FileClass(
                        source_path=fc.source_path,
                        format=fc.format,
                        type=fc.type,
                        category=fc.category,
                        file_id=new_id,
                        matched_pattern=fc.matched_pattern,
                    ),
                )
            )
        return result

    current = list(items)
    collisions = _find_collisions(current)
    for levels in (1, 2):
        if not collisions:
            break
        colliding_outs = set(collisions.keys())
        non_colliding = [(o, fc) for o, fc in current if o not in colliding_outs]
        disambiguated = []
        for col_list in collisions.values():
            disambiguated.extend(_regenerate(col_list, levels))
        current = non_colliding + disambiguated
        collisions = _find_collisions(current)

    if collisions:
        lines = [
            "output_path collision detected — add more specific patterns to the mapping file:"
        ]
        for out_path, entries in sorted(collisions.items()):
            lines.append(f"  {out_path}:")
            for _out, fc in entries:
                lines.append(f"    {fc.source_path}")
        raise ValueError("\n".join(lines))

    return current


def _source_roots_for_version(version: str, repo_root: Path) -> list[Path]:
    """Return RST/MD source root directories for *version*.

    Duplicated from ``scripts.create.scan._source_roots`` so
    ``common/`` does not import ``create/`` (spec §2-2 layering).  The
    source-root layout is part of the RBKC input contract, not a
    create-side concern, so it belongs in ``common/``.
    """
    roots: list[Path] = []
    if version in ("5", "6"):
        roots = [
            repo_root / f".lw/nab-official/v{version}/nablarch-document/ja",
            repo_root / f".lw/nab-official/v{version}/nablarch-system-development-guide",
        ]
    else:
        v_dir = repo_root / f".lw/nab-official/v{version}"
        if v_dir.exists():
            roots = sorted(d for d in v_dir.iterdir() if d.is_dir())
    dir_name = f"nablarch-{version}-all-releasenote"
    all_rn = repo_root / ".lw/nab-official/all-releasenote" / dir_name
    if all_rn.exists():
        roots = list(roots) + [all_rn]
    return roots


def iter_rst_paths(version: str, repo_root: Path) -> list[Path]:
    """Yield every .rst file under the version's source roots.  Used by
    ``common/labels.py`` to build label / doc maps without depending on
    ``create/scan.py``.
    """
    out: list[Path] = []
    for root in _source_roots_for_version(version, repo_root):
        if not root.exists():
            continue
        for p in root.rglob("*.rst"):
            if p.is_file():
                out.append(p)
    return out


def classify_rst_and_md(
    sources: list,
    version: str,
    repo_root: Path,
    *,
    mappings: dict | None = None,
) -> list[FileClass]:
    """Pure-common classification for RST + MD sources, with collision
    disambiguation applied.  Xlsx sources are skipped because their
    expansion requires reading the workbook (impure).  Intended for
    ``common/labels.py`` consumers — they only need RST files anyway,
    and the disambiguation result matches what ``create/classify.py``
    writes to disk for RST+MD entries.

    Each element of ``sources`` must expose ``.path`` (Path) and
    ``.format`` ("rst"/"md") attributes — matches the ``SourceFile``
    duck type without importing it.
    """
    if mappings is None:
        mappings = load_mappings(version, repo_root)
    items: list[tuple[str, FileClass]] = []
    for src in sources:
        fmt = getattr(src, "format", "")
        if fmt not in ("rst", "md"):
            continue
        path = getattr(src, "path", None)
        if path is None:
            continue
        fc = derive_file_id(path, fmt, version, repo_root, mappings=mappings)
        if fc is None:
            continue
        output_path = f"{fc.type}/{fc.category}/{fc.file_id}.json"
        items.append((output_path, fc))
    disambiguated = disambiguate_file_classes(items, version)
    return [fc for _out, fc in disambiguated]
