"""Source file classifier for RBKC.

Classifies scanned source files into type/category/file_id/output_path
using the RBKC mapping files.

Public API:
    classify_sources(sources, version, repo_root) -> list[FileInfo]
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from scripts.scan import SourceFile, _load_mappings, _rel_for_classify


@dataclass(frozen=True)
class FileInfo:
    source_path: Path
    format: str      # 'rst', 'md', 'xlsx'
    file_id: str
    type: str
    category: str
    output_path: str  # relative: e.g. component/libraries/libraries-universal_dao.json


def _generate_id(filename: str, fmt: str, category: str, source_path: Path,
                 matched_pattern: str, version: str, xlsx_exact: bool = False,
                 extra_prefix: str = "") -> str:
    """Generate a knowledge file ID from filename and category.

    Args:
        extra_prefix: Additional path-based prefix for disambiguation (e.g. parent dir).
                      Inserted between category and base: ``{category}-{extra_prefix}-{base}``.
    """
    # For xlsx exact-filename matches (not pattern), category is the full ID
    if fmt == "xlsx" and xlsx_exact:
        return category

    # Strip extension
    if fmt == "rst":
        base = filename[:-4]  # remove .rst
    elif fmt == "md":
        base = filename[:-3]  # remove .md
    else:
        base = Path(filename).stem

    # For index.rst, use path context to avoid collisions
    if base == "index" and source_path is not None and matched_pattern:
        rel = _rel_for_classify(source_path, version)
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

    # Combine with category for uniqueness
    base = base.replace("_", "-")
    if extra_prefix:
        extra_prefix = extra_prefix.replace("_", "-")
        if category:
            return f"{category}-{extra_prefix}-{base}"
        return f"{extra_prefix}-{base}"
    if category:
        return f"{category}-{base}"
    return base


def _parent_prefix(source_path: Path, levels: int) -> str:
    """Return a slug built from ``levels`` parent directory names."""
    parts = source_path.parts
    # parts[-1] is the filename; take ``levels`` dirs before it
    dirs = parts[max(0, len(parts) - 1 - levels):len(parts) - 1]
    return "-".join(p.lower().replace("_", "-") for p in dirs)


def _disambiguate(
    items: list[tuple[str, "FileInfo"]],
    version: str,
) -> list["FileInfo"]:
    """Resolve output_path collisions by progressively adding parent dir prefixes.

    Tries 1-level, then 2-level parent prefixes. Raises ValueError if collisions
    remain after 2 levels.
    """
    from collections import defaultdict

    # Build {output_path: [FileInfo]} to find collisions
    def find_collisions(
        entries: list[tuple[str, FileInfo]]
    ) -> dict[str, list[tuple[str, FileInfo]]]:
        by_out: dict[str, list] = defaultdict(list)
        for out, fi in entries:
            by_out[out].append((out, fi))
        return {k: v for k, v in by_out.items() if len(v) > 1}

    # Regenerate IDs with a given number of parent-dir levels
    def regenerate(
        colliding: list[tuple[str, FileInfo]], levels: int
    ) -> list[tuple[str, FileInfo]]:
        result = []
        for _, fi in colliding:
            prefix = _parent_prefix(fi.source_path, levels)
            new_id = _generate_id(
                fi.source_path.name, fi.format, fi.category,
                fi.source_path, "", version,
                xlsx_exact=(fi.format == "xlsx" and fi.file_id == fi.category),
                extra_prefix=prefix,
            )
            new_out = f"{fi.type}/{fi.category}/{new_id}.json"
            result.append((new_out, FileInfo(
                source_path=fi.source_path,
                format=fi.format,
                file_id=new_id,
                type=fi.type,
                category=fi.category,
                output_path=new_out,
            )))
        return result

    # Start with original entries
    current = list(items)
    collisions = find_collisions(current)

    for levels in (1, 2):
        if not collisions:
            break
        # Replace colliding entries with disambiguated versions
        colliding_outs = set(collisions.keys())
        non_colliding = [(out, fi) for out, fi in current if out not in colliding_outs]
        disambiguated = []
        for col_list in collisions.values():
            disambiguated.extend(regenerate(col_list, levels))
        current = non_colliding + disambiguated
        collisions = find_collisions(current)

    if collisions:
        lines = [
            "output_path collision detected — add more specific patterns to the mapping file:"
        ]
        for out_path, entries in sorted(collisions.items()):
            lines.append(f"  {out_path}:")
            for _, fi in entries:
                lines.append(f"    {fi.source_path}")
        raise ValueError("\n".join(lines))

    return [fi for _, fi in current]


def classify_sources(
    sources: list[SourceFile],
    version: str,
    repo_root: Path,
) -> list[FileInfo]:
    """Classify source files using RBKC mapping files.

    Args:
        sources: List of source files from :func:`scan.scan_sources`.
        version: Nablarch version string.
        repo_root: Repository root directory.

    Returns:
        List of :class:`FileInfo` objects. Unclassified files are silently skipped.
        Output path collisions are resolved automatically by adding parent directory
        prefixes (up to 2 levels). Raises ValueError if collisions remain after that.

    Raises:
        ValueError: If collisions cannot be resolved automatically.
    """
    mappings = _load_mappings(version, repo_root)

    # Sort RST patterns longest-first (more specific matches win)
    rst_entries = sorted(
        mappings.get("rst", []),
        key=lambda e: len(e["pattern"]),
        reverse=True,
    )
    md_mapping: dict = mappings.get("md", {})
    xlsx_exact: dict = mappings.get("xlsx", {})
    xlsx_patterns: list = mappings.get("xlsx_patterns", [])

    items: list[tuple[str, FileInfo]] = []

    for src in sources:
        rel = _rel_for_classify(src.path, version)
        type_ = category = matched_pattern = None
        is_xlsx_exact = False

        if src.format == "rst":
            for entry in rst_entries:
                if entry["pattern"] in rel:
                    type_ = entry["type"]
                    category = entry["category"]
                    matched_pattern = entry["pattern"]
                    break
            if type_ is None:
                # top-level index.rst
                if rel == "index.rst":
                    type_, category, matched_pattern = "about", "about-nablarch", ""
                else:
                    continue  # unclassified

        elif src.format == "md":
            if src.filename in md_mapping:
                info = md_mapping[src.filename]
                type_ = info["type"]
                category = info["category"]
                matched_pattern = ""
            else:
                continue

        elif src.format == "xlsx":
            if src.filename in xlsx_exact:
                info = xlsx_exact[src.filename]
                type_ = info["type"]
                category = info["category"]
                matched_pattern = ""
                is_xlsx_exact = True
            else:
                is_xlsx_exact = False
                for pat in xlsx_patterns:
                    if src.filename.endswith(pat["endswith"]):
                        type_ = pat["type"]
                        category = pat["category"]
                        matched_pattern = ""
                        break
                if type_ is None:
                    continue

        if type_ is None or category is None:
            continue

        file_id = _generate_id(
            src.filename, src.format, category,
            src.path, matched_pattern or "", version,
            xlsx_exact=is_xlsx_exact,
        )
        output_path = f"{type_}/{category}/{file_id}.json"

        items.append((output_path, FileInfo(
            source_path=src.path,
            format=src.format,
            file_id=file_id,
            type=type_,
            category=category,
            output_path=output_path,
        )))

    return _disambiguate(items, version)
