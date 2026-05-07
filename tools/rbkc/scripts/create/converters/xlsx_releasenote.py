"""Release-note Excel converter (Phase 22-B sheet-level split).

Entry point delegated by ``scripts.run._converter_for`` when the filename
matches a release-note pattern.  The actual parsing lives in
``scripts.create.converters.xlsx_common``; release-note and security-table
share the same algorithm and differ only in the mapping entries that route
a file here.

Public API:
    convert(path: Path, file_id: str = "", sheet_name: str | None = None)
        -> RSTResult
"""
from __future__ import annotations

from pathlib import Path

from scripts.create.converters.rst import RSTResult
from scripts.create.converters.xlsx_common import convert_sheet, list_sheet_names


def convert(
    path: Path,
    file_id: str = "",
    sheet_name: str | None = None,
    sheet_subtype: str | None = None,
) -> RSTResult:
    """Convert one worksheet of *path* to :class:`RSTResult`.

    Phase 22-B contract: the caller (``run._convert_and_write``) invokes this
    once per worksheet with ``sheet_name`` set.  A missing ``sheet_name``
    falls back to the first worksheet to preserve ad-hoc unit-test callers.
    """
    if sheet_name is None:
        names = list_sheet_names(path)
        if not names:
            raise ValueError(f"{path}: workbook has no sheets")
        sheet_name = names[0]
    result, meta = convert_sheet(path, sheet_name, sheet_subtype=sheet_subtype)
    result.meta = meta
    return result
