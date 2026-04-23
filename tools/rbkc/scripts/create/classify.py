"""Source file classifier for RBKC.

Classifies scanned source files into type/category/file_id/output_path
using the RBKC mapping files.

Public API:
    classify_sources(sources, version, repo_root) -> list[FileInfo]
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scripts.common.file_id import (
    _generate_id,
    derive_file_id,
    load_mappings as _load_mappings,
    rel_for_classify as _rel_for_classify,
)
from scripts.create.scan import SourceFile


@dataclass(frozen=True)
class FileInfo:
    source_path: Path
    format: str      # 'rst', 'md', 'xlsx'
    file_id: str
    type: str
    category: str
    output_path: str  # relative: e.g. component/libraries/libraries-universal_dao.json
    # Phase 22-B: set only for xlsx sheet-level split.  ``None`` for rst/md.
    sheet_name: str | None = None


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
            # Phase 22-B: preserve the sheet suffix on xlsx rows so
            # disambiguation does not collapse per-sheet FileInfos back
            # to the file-level id.
            if fi.sheet_name and fi.file_id.endswith(f"-{_sheet_slug(fi.sheet_name)}"):
                new_id = f"{new_id}-{_sheet_slug(fi.sheet_name)}"
            new_out = f"{fi.type}/{fi.category}/{new_id}.json"
            result.append((new_out, FileInfo(
                source_path=fi.source_path,
                format=fi.format,
                file_id=new_id,
                type=fi.type,
                category=fi.category,
                output_path=new_out,
                sheet_name=fi.sheet_name,
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

    items: list[tuple[str, FileInfo]] = []

    for src in sources:
        fc = derive_file_id(src.path, src.format, version, repo_root, mappings=mappings)
        if fc is None:
            continue

        # Phase 22-B: xlsx files expand into one FileInfo per worksheet.
        # Sheet count = 1 keeps the bare file_id; ≥ 2 appends the sheet
        # name (design §8-1).  Sheet names are Japanese-safe already;
        # `/` is the only filesystem-unsafe char we have to guard.
        if src.format == "xlsx":
            from scripts.create.converters.xlsx_common import list_sheet_names
            sheet_names = list_sheet_names(src.path)
            if not sheet_names:
                continue
            for sheet in sheet_names:
                if len(sheet_names) == 1:
                    file_id = fc.file_id
                else:
                    file_id = f"{fc.file_id}-{_sheet_slug(sheet)}"
                output_path = f"{fc.type}/{fc.category}/{file_id}.json"
                items.append((output_path, FileInfo(
                    source_path=src.path,
                    format=src.format,
                    file_id=file_id,
                    type=fc.type,
                    category=fc.category,
                    output_path=output_path,
                    sheet_name=sheet,
                )))
            continue

        output_path = f"{fc.type}/{fc.category}/{fc.file_id}.json"
        items.append((output_path, FileInfo(
            source_path=src.path,
            format=src.format,
            file_id=fc.file_id,
            type=fc.type,
            category=fc.category,
            output_path=output_path,
        )))

    return _disambiguate(items, version)


def _sheet_slug(name: str) -> str:
    """Make a worksheet name safe for use as a filename component.

    We keep Japanese characters verbatim (design §8-1) and only replace the
    path separator, which is the single character Linux rejects in a
    filename.  Windows-reserved characters (``\\ : * ? " < > |``) are also
    mapped because the repo is checked out on Windows during editing.
    """
    bad = '\\/:*?"<>|'
    return "".join("_" if c in bad else c for c in name).strip() or "sheet"
