"""Common: source file scanning and classification.

Consolidates ``SourceFile``/``scan_sources`` from ``create/scan.py`` and
``FileInfo``/``classify_sources``/``_sheet_slug`` from ``create/classify.py``
into ``common/`` so verify-side consumers can import them without reaching
into create/ (spec §2-2 layering).

Public API
----------
- :class:`SourceFile`      — immutable source-file descriptor
- :class:`FileInfo`        — classified source file with output path
- :func:`scan_sources`     — discover source files for a version
- :func:`classify_sources` — classify scanned sources into FileInfo objects
- :func:`_sheet_slug`      — make a worksheet name safe for use as filename component
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scripts.common.file_id import (
    _generate_id,
    _parent_prefix as _common_parent_prefix,
    derive_file_id,
    disambiguate_file_classes,
    load_mappings as _load_mappings,
    rel_for_classify as _rel_for_classify,
)


@dataclass(frozen=True)
class SourceFile:
    path: Path      # absolute path
    format: str     # 'rst', 'md', 'xlsx'
    filename: str   # basename


@dataclass(frozen=True)
class FileInfo:
    source_path: Path
    format: str      # 'rst', 'md', 'xlsx'
    file_id: str
    type: str
    category: str
    output_path: str  # relative: e.g. component/libraries/libraries-universal_dao.json
    # set only for xlsx sheet-level split; None for rst/md
    sheet_name: str | None = None


def list_sheet_names(path: Path) -> list[str]:
    """Return worksheet names in file order."""
    ext = path.suffix.lower()
    if ext == ".xls":
        import xlrd
        wb = xlrd.open_workbook(str(path))
        return [s.name for s in wb.sheets()]
    import openpyxl
    wb = openpyxl.load_workbook(str(path), data_only=True, read_only=True)
    return list(wb.sheetnames)


def _all_releasenote_root(version: str, repo_root: Path) -> Path | None:
    """Return the all-releasenote directory for the given version, or None if absent."""
    dir_name = f"nablarch-{version}-all-releasenote"
    root = repo_root / ".lw/nab-official/all-releasenote" / dir_name
    return root if root.exists() else None


def _source_roots(version: str, repo_root: Path) -> list[Path]:
    """Return source directory roots for the given version."""
    roots: list[Path] = []
    if version in ("5", "6"):
        roots = [
            repo_root / f".lw/nab-official/v{version}/nablarch-document/ja",
            repo_root / f".lw/nab-official/v{version}/nablarch-system-development-guide",
        ]
    else:
        # v1.x versions
        v_dir = repo_root / f".lw/nab-official/v{version}"
        roots = sorted(d for d in v_dir.iterdir() if d.is_dir())
    all_rn = _all_releasenote_root(version, repo_root)
    if all_rn is not None:
        roots = list(roots) + [all_rn]
    return roots


def scan_sources(
    version: str,
    repo_root: Path,
    files: list[str] | None = None,
) -> list[SourceFile]:
    """Scan source files for the given version.

    Args:
        version: Nablarch version string (e.g. "6", "5").
        repo_root: Repository root directory.
        files: Optional list of specific source file paths (relative to repo_root).
               If provided, only these files are returned (skipping directory scan).

    Returns:
        List of :class:`SourceFile` objects.
    """
    if files is not None:
        result = []
        for f in files:
            p = repo_root / f if not Path(f).is_absolute() else Path(f)
            suffix = p.suffix.lower()
            if suffix == ".rst":
                fmt = "rst"
            elif suffix == ".md":
                fmt = "md"
            elif suffix in (".xlsx", ".xls"):
                fmt = "xlsx"
            else:
                continue
            result.append(SourceFile(path=p, format=fmt, filename=p.name))
        return result

    mappings = _load_mappings(version, repo_root)
    rst_patterns = {entry["pattern"] for entry in mappings.get("rst", [])}
    md_files = set(mappings.get("md", {}).keys())
    xlsx_exact = set(mappings.get("xlsx", {}).keys())
    xlsx_patterns = mappings.get("xlsx_patterns", [])

    result: list[SourceFile] = []

    for src_root in _source_roots(version, repo_root):
        if not src_root.exists():
            continue
        for path in src_root.rglob("*"):
            if not path.is_file():
                continue
            suffix = path.suffix.lower()
            rel = _rel_for_classify(path, version)

            if suffix == ".rst":
                if any(pat in rel for pat in rst_patterns):
                    result.append(SourceFile(path=path, format="rst", filename=path.name))

            elif suffix == ".md":
                if path.name in md_files:
                    result.append(SourceFile(path=path, format="md", filename=path.name))

            elif suffix in (".xlsx", ".xls"):
                if path.name in xlsx_exact:
                    result.append(SourceFile(path=path, format="xlsx", filename=path.name))
                elif any(path.name.endswith(p["endswith"]) for p in xlsx_patterns):
                    result.append(SourceFile(path=path, format="xlsx", filename=path.name))

    return result


def _sheet_slug(name: str) -> str:
    """Make a worksheet name safe for use as a filename component.

    Japanese characters are kept verbatim (design §8-1); only the path
    separator and Windows-reserved characters are replaced.
    """
    bad = '\\/:*?"<>|'
    return "".join("_" if c in bad else c for c in name).strip() or "sheet"


def _disambiguate(
    items: list[tuple[str, FileInfo]],
    version: str,
) -> list[FileInfo]:
    """Thin wrapper over :func:`common.file_id.disambiguate_file_classes`.

    xlsx sheet-level FileInfos carry extra metadata (``sheet_name``) that the
    common helper would lose, so xlsx disambiguation is handled here and only
    the RST/MD path is delegated.
    """
    from collections import defaultdict
    from scripts.common.file_id import FileClass

    xlsx_items: list[tuple[str, FileInfo]] = [
        (o, fi) for o, fi in items if fi.format == "xlsx"
    ]
    rest_items: list[tuple[str, FileInfo]] = [
        (o, fi) for o, fi in items if fi.format != "xlsx"
    ]

    rest_as_fc: list[tuple[str, FileClass]] = [
        (o, FileClass(
            source_path=fi.source_path,
            format=fi.format,
            type=fi.type,
            category=fi.category,
            file_id=fi.file_id,
            matched_pattern="",
        ))
        for o, fi in rest_items
    ]
    disambiguated = disambiguate_file_classes(rest_as_fc, version)
    rest_out = [
        FileInfo(
            source_path=fc.source_path,
            format=fc.format,
            file_id=fc.file_id,
            type=fc.type,
            category=fc.category,
            output_path=o,
        )
        for o, fc in disambiguated
    ]

    def _find_collisions(entries):
        by_out: dict[str, list] = defaultdict(list)
        for o, fi in entries:
            by_out[o].append((o, fi))
        return {k: v for k, v in by_out.items() if len(v) > 1}

    current = list(xlsx_items)
    collisions = _find_collisions(current)
    for levels in (1, 2):
        if not collisions:
            break
        colliding_outs = set(collisions.keys())
        non_colliding = [(o, fi) for o, fi in current if o not in colliding_outs]
        regen: list[tuple[str, FileInfo]] = []
        for col_list in collisions.values():
            for _o, fi in col_list:
                prefix = _common_parent_prefix(fi.source_path, levels)
                new_id = _generate_id(
                    fi.source_path.name, fi.format, fi.category,
                    fi.source_path, "", version,
                    xlsx_exact=(fi.format == "xlsx" and fi.file_id == fi.category),
                    extra_prefix=prefix,
                )
                if fi.sheet_name and fi.file_id.endswith(f"-{_sheet_slug(fi.sheet_name)}"):
                    new_id = f"{new_id}-{_sheet_slug(fi.sheet_name)}"
                new_out = f"{fi.type}/{fi.category}/{new_id}.json"
                regen.append((new_out, FileInfo(
                    source_path=fi.source_path,
                    format=fi.format,
                    file_id=new_id,
                    type=fi.type,
                    category=fi.category,
                    output_path=new_out,
                    sheet_name=fi.sheet_name,
                )))
        current = non_colliding + regen
        collisions = _find_collisions(current)

    if collisions:
        lines = [
            "output_path collision detected — add more specific patterns to the mapping file:"
        ]
        for out_path, entries in sorted(collisions.items()):
            lines.append(f"  {out_path}:")
            for _o, fi in entries:
                lines.append(f"    {fi.source_path}")
        raise ValueError("\n".join(lines))

    xlsx_out = [fi for _o, fi in current]
    return rest_out + xlsx_out


def classify_sources(
    sources: list[SourceFile],
    version: str,
    repo_root: Path,
) -> list[FileInfo]:
    """Classify source files using RBKC mapping files.

    Args:
        sources: List of source files from :func:`scan_sources`.
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

        if src.format == "xlsx":
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
