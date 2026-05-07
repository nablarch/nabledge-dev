"""Source file scanner for RBKC.

Backward-compat shim: all symbols now live in ``scripts.common.sources``.
This module re-exports them so existing callers do not break.
"""
from __future__ import annotations

from scripts.common.sources import (  # noqa: F401
    SourceFile,
    scan_sources,
    _all_releasenote_root,
    _source_roots,
)
from scripts.common.file_id import (  # noqa: F401
    load_mappings as _load_mappings,
    rel_for_classify as _rel_for_classify,
)
