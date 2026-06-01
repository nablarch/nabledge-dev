"""Single source of truth for the cross-document MD link format.

Spec §3-2-3 defines the canonical link shape as
``[display](../../{type}/{category}/{file_id}.md[#anchor])``.  This
module is the sole place that literal shape lives, so create-side
emission (``rst_ast_visitor`` / ``md_ast_visitor``) and verify-side
parsing (``verify.py`` / ``_resolve_title_inline``) cannot drift.

Drift would silently break QO2 byte-equality between JSON and docs MD,
which F4 of review-22-b-16b-step3-4-16c.md called out under
ゼロトレランス "1% リスクも許容しない".

Public API:
    emit_crossdoc_link(display, type_, category, file_id, anchor="") -> str
    emit_asset_link(display, file_id, basename) -> str
    CROSSDOC_LINK_RE — pinned regex matching ``emit_crossdoc_link`` output
    ASSET_LINK_RE    — pinned regex matching ``emit_asset_link`` output
"""
from __future__ import annotations

import re


def emit_crossdoc_link(
    display: str,
    type_: str,
    category: str,
    file_id: str,
    anchor: str = "",
) -> str:
    """Return the canonical cross-document MD link per spec §3-2-3."""
    if anchor:
        return f"[{display}](../../{type_}/{category}/{file_id}.md#{anchor})"
    return f"[{display}](../../{type_}/{category}/{file_id}.md)"


def emit_asset_link(display: str, file_id: str, basename: str) -> str:
    """Return the canonical asset MD link per spec §3-2-3 rows 5/6/7."""
    return f"[{display}](assets/{file_id}/{basename})"


#: Matches output of :func:`emit_crossdoc_link` — tested via round-trip
#: in tests/ut/test_linkfmt.py so drift between emit and parse is impossible.
CROSSDOC_LINK_RE = re.compile(
    r"\]\(\.\./\.\./(?P<type>[A-Za-z0-9_\-]+)/"
    r"(?P<category>[A-Za-z0-9_\-]+)/"
    r"(?P<file_id>[^)\s#]+)\.md(?:#(?P<anchor>[^)\s]+))?\)"
)

#: Matches ``](assets/{file_id}/{basename})``.
ASSET_LINK_RE = re.compile(
    r"\]\((?P<path>assets/(?P<file_id>[^)\s/]+)/(?P<basename>[^)\s]+))\)"
)


__all__ = [
    "emit_crossdoc_link",
    "emit_asset_link",
    "CROSSDOC_LINK_RE",
    "ASSET_LINK_RE",
]
