"""Phase 4: Cross-reference resolution and asset copying.

Provides:
- collect_asset_refs: find image/figure/download assets referenced in an RST file
- copy_assets: copy collected assets to the output directory

Phase 22-B-12 ws3: switched from regex to docutils AST walk so that
assets referenced inside `.. include::` files are followed transitively.
Regex-only detection missed 118 v1.3 / 116 v1.2 image assets referenced
via the common `.. include:: ../api/link.rst` pattern (link.rst contains
`.. image::` directives that the includer inherits at parse time).
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from docutils import nodes

from scripts.common import rst_ast


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

@dataclass
class AssetRef:
    """Reference to an asset file used in an RST document."""

    source_path: Path   # Absolute path to the source file
    dest_rel: str       # Relative output path, e.g. "assets/{file_id}/filename"


# ---------------------------------------------------------------------------
# Asset collection
# ---------------------------------------------------------------------------


def _ancestor_source(node: nodes.Node, default: Path) -> Path:
    """Walk up parent chain to find the RST file that sourced this node.

    docutils sets ``node.source`` on nodes created from an included file
    (``.. include::`` / ``.. literalinclude::``).  A node directly
    authored in the top-level document has ``source=None``; we fall back
    to *default* (the document root path passed to the parser).
    """
    cur: nodes.Node | None = node
    while cur is not None:
        src = cur.source
        if src:
            return Path(src)
        cur = cur.parent
    return default


def _parse_download_target(raw: str) -> str:
    """Extract the path target from ``:download:`text <path>``` / ``:download:`path```.

    Mirrors the semantics of ``rst_ast_visitor`` role='download' handling.
    """
    raw = raw.strip()
    if "<" in raw and raw.endswith(">"):
        _text, _, target = raw.rpartition("<")
        return target.rstrip(">").strip()
    return raw


def collect_asset_refs(rst_path: Path, file_id: str) -> list[AssetRef]:
    """Find all image, figure, and download assets referenced in *rst_path*.

    Uses docutils AST walk so that assets referenced inside
    ``.. include::`` files are discovered and resolved relative to the
    included file's own directory (not the includer's).

    Paths that do not exist on disk are silently skipped — matching the
    prior regex-based behaviour.

    Args:
        rst_path: Path to the RST source file.
        file_id:  Knowledge file id used to build the ``assets/{file_id}/…`` dest path.

    Returns:
        Deduplicated list of :class:`AssetRef` objects.
    """
    text = rst_path.read_text(encoding="utf-8", errors="replace")
    doctree, _warn = rst_ast.parse(text, source_path=rst_path)

    seen: set[Path] = set()
    refs: list[AssetRef] = []

    def _add(rel: str, origin: Path) -> None:
        if not rel:
            return
        # Resolve relative to the source file that contained the reference.
        # ``origin`` is the RST file (includer or includee); its parent is
        # the directory against which the asset path is relative.
        abs_src = (origin.parent / rel).resolve()
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

    # Images (covers `.. image::` and the image child inside `.. figure::`).
    for node in doctree.findall(nodes.image):
        uri = node.get("uri")
        if not uri:
            continue
        origin = _ancestor_source(node, rst_path)
        _add(uri, origin)

    # :download:`…` role is emitted by the Sphinx shim as
    # ``<inline classes="role-download">raw</inline>``.
    for node in doctree.findall(nodes.inline):
        classes = node.get("classes") or []
        if "role-download" not in classes:
            continue
        target = _parse_download_target(node.astext())
        origin = _ancestor_source(node, rst_path)
        _add(target, origin)

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
