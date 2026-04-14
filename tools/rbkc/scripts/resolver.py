"""Phase 4: Cross-reference resolution and asset copying.

Provides:
- build_label_map: collect all RST ``.. _label:`` definitions
- collect_asset_refs: find image/figure/download assets referenced in an RST file
- copy_assets: copy collected assets to the output directory
"""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

@dataclass
class AssetRef:
    """Reference to an asset file used in an RST document."""

    source_path: Path   # Absolute path to the source file
    dest_rel: str       # Relative output path, e.g. "assets/{file_id}/filename"


# ---------------------------------------------------------------------------
# Label map
# ---------------------------------------------------------------------------

# Matches ``.. _label:`` and ``.. _`label with spaces`:``
_LABEL_RE = re.compile(r"^\.\. _`?([^:`\n]+?)`?\s*:\s*$", re.MULTILINE)


def build_label_map(
    source_dir: Path,
    path_to_id: Callable[[Path], str] = lambda p: p.stem,
) -> dict[str, str]:
    """Scan RST files under *source_dir* and build a label → file_id mapping.

    Args:
        source_dir: Root directory to scan recursively for ``*.rst`` files.
        path_to_id: Callable that converts an RST :class:`Path` to a file_id.
                    Defaults to ``path.stem``.

    Returns:
        ``{label: file_id}`` dict.  If the same label appears in multiple files,
        the last one wins (consistent with Sphinx behaviour).
    """
    result: dict[str, str] = {}
    for rst_path in sorted(source_dir.rglob("*.rst")):
        file_id = path_to_id(rst_path)
        text = rst_path.read_text(encoding="utf-8", errors="replace")
        for m in _LABEL_RE.finditer(text):
            label = m.group(1).strip()
            result[label] = file_id
    return result


# ---------------------------------------------------------------------------
# Asset collection
# ---------------------------------------------------------------------------

# Matches ``.. image:: path`` or ``.. figure:: path`` (optionally indented)
_IMAGE_RE = re.compile(r"^\s*\.\. (?:image|figure)::\s*(\S+)", re.MULTILINE)

# Matches ``:download:`label <path>```
_DOWNLOAD_RE = re.compile(r":download:`[^<`]*<([^>]+)>`")


def collect_asset_refs(rst_path: Path, file_id: str) -> list[AssetRef]:
    """Find all image, figure, and download assets referenced in *rst_path*.

    Paths are resolved relative to ``rst_path.parent``.  Files that do not
    exist on disk are silently skipped.

    Args:
        rst_path: Path to the RST source file.
        file_id:  Knowledge file id used to build the ``assets/{file_id}/…`` dest path.

    Returns:
        Deduplicated list of :class:`AssetRef` objects.
    """
    text = rst_path.read_text(encoding="utf-8", errors="replace")
    rst_dir = rst_path.parent

    seen: set[Path] = set()
    refs: list[AssetRef] = []

    def _add(rel: str) -> None:
        abs_src = (rst_dir / rel).resolve()
        if abs_src in seen:
            return
        if not abs_src.exists():
            return
        seen.add(abs_src)
        filename = abs_src.name
        refs.append(AssetRef(
            source_path=abs_src,
            dest_rel=f"assets/{file_id}/{filename}",
        ))

    for m in _IMAGE_RE.finditer(text):
        _add(m.group(1).strip())

    for m in _DOWNLOAD_RE.finditer(text):
        _add(m.group(1).strip())

    return refs


# ---------------------------------------------------------------------------
# Asset copying
# ---------------------------------------------------------------------------

def copy_assets(refs: list[AssetRef], dest_dir: Path) -> list[Path]:
    """Copy asset files to *dest_dir*.

    Args:
        refs:     Asset references collected by :func:`collect_asset_refs`.
        dest_dir: Root output directory.  Files are placed at
                  ``dest_dir / ref.dest_rel``.

    Returns:
        List of destination :class:`Path` objects for files that were copied.
        Missing source files are silently skipped.
    """
    copied: list[Path] = []
    for ref in refs:
        if not ref.source_path.exists():
            continue
        dest = dest_dir / ref.dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ref.source_path, dest)
        copied.append(dest)
    return copied
