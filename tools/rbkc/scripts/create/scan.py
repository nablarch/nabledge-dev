"""Source file scanner for RBKC.

Scans source documentation directories to find RST, MD, and XLSX files
that should be converted to knowledge JSON files.

Public API:
    scan_sources(version: str, repo_root: Path, files: list[str] | None = None)
        -> list[SourceFile]
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scripts.common.file_id import (
    load_mappings as _load_mappings,
    rel_for_classify as _rel_for_classify,
)


@dataclass(frozen=True)
class SourceFile:
    path: Path      # absolute path
    format: str     # 'rst', 'md', 'xlsx'
    filename: str   # basename


def _all_releasenote_root(version: str, repo_root: Path) -> Path | None:
    """Return the all-releasenote directory for the given version, or None if absent."""
    # version "5" → "nablarch-5-all-releasenote", "1.4" → "nablarch-1.4-all-releasenote"
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
    # Add all-releasenote root for all versions (v5, v1.x)
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
                # Check if any RST pattern appears in the relative path
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
