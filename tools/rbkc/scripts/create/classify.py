"""Source file classifier for RBKC.

Backward-compat shim: all symbols now live in ``scripts.common.sources``.
This module re-exports them so existing callers do not break.

The ``_parent_prefix`` shim is kept for any external caller that patches it.
``_disambiguate`` and ``_sheet_slug`` are internal helpers; they are
re-exported for completeness.
"""
from __future__ import annotations

from pathlib import Path

from scripts.common.sources import (  # noqa: F401
    FileInfo,
    classify_sources,
    _disambiguate,
    _sheet_slug,
)
from scripts.common.file_id import (  # noqa: F401
    _parent_prefix as _common_parent_prefix,
)


# Keep the old symbol for backward-compat with any external caller.
def _parent_prefix(source_path: Path, levels: int) -> str:
    return _common_parent_prefix(source_path, levels)
