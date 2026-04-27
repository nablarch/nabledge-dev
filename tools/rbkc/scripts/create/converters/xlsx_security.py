"""Security-table Excel converter (Phase 22-B sheet-level split).

Same dispatch pattern as :mod:`xlsx_releasenote`.  See
``scripts.create.converters.xlsx_common`` for the parsing algorithm.

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
) -> RSTResult:
    if sheet_name is None:
        names = list_sheet_names(path)
        if not names:
            raise ValueError(f"{path}: workbook has no sheets")
        sheet_name = names[0]
    result, meta = convert_sheet(path, sheet_name)
    result.meta = meta
    return result
