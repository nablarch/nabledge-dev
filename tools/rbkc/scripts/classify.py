"""Source file classifier for RBKC.

Classifies scanned source files into type/category/file_id/output_path
using the KC mapping files.

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
                 matched_pattern: str, version: str, xlsx_exact: bool = False) -> str:
    """Generate a knowledge file ID from filename and category."""
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
    if category:
        return f"{category}-{base}"
    return base


def classify_sources(
    sources: list[SourceFile],
    version: str,
    repo_root: Path,
) -> list[FileInfo]:
    """Classify source files using KC mapping files.

    Args:
        sources: List of source files from :func:`scan.scan_sources`.
        version: Nablarch version string.
        repo_root: Repository root directory.

    Returns:
        List of :class:`FileInfo` objects. Unclassified files are silently skipped.
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

    result: list[FileInfo] = []

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

        result.append(FileInfo(
            source_path=src.path,
            format=src.format,
            file_id=file_id,
            type=type_,
            category=category,
            output_path=output_path,
        ))

    return result
