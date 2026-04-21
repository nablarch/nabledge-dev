"""Excel release note converter for RBKC.

Converts Nablarch official release note Excel files (xlsx and xls) into a single
flat section containing all non-empty cell values from all sheets in row-major
order.  No AI, no external API calls.

All cell values are preserved verbatim so verify can confirm 100% coverage.

Public API:
    convert(path: Path, file_id: str = "") -> RSTResult
"""
from __future__ import annotations

from pathlib import Path

from scripts.create.converters.rst import RSTResult, Section


def _xlsx_lines(path: Path) -> list[str]:
    """Return non-empty rows as joined cell lines from all sheets of an xlsx file."""
    import openpyxl
    wb = openpyxl.load_workbook(str(path), data_only=True)
    lines = []
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            cells = [str(c).strip() for c in row if c is not None and str(c).strip()]
            if cells:
                lines.append("  ".join(cells))
    return lines


def _xls_lines(path: Path) -> list[str]:
    """Return non-empty rows as joined cell lines from all sheets of a xls file."""
    import xlrd
    wb = xlrd.open_workbook(str(path))
    lines = []
    for ws in (wb.sheet_by_index(i) for i in range(wb.nsheets)):
        for rx in range(ws.nrows):
            cells = [str(v).strip()
                     for cx in range(ws.ncols)
                     if (v := ws.cell_value(rx, cx)) and str(v).strip()]
            if cells:
                lines.append("  ".join(cells))
    return lines


def convert(path: Path, file_id: str = "") -> RSTResult:
    """Convert a release note Excel file at *path* to :class:`RSTResult`.

    Supports both .xlsx (openpyxl) and .xls (xlrd) formats.

    Args:
        path: Path to the ``.xlsx`` or ``.xls`` file.
        file_id: Unused; present for API consistency with other converters.

    Returns:
        :class:`RSTResult` with a single section containing all cell values.
    """
    if path.suffix.lower() == ".xls":
        lines = _xls_lines(path)
    else:
        lines = _xlsx_lines(path)

    return RSTResult(
        title="",
        no_knowledge_content=False,
        content="\n".join(lines),
        sections=[],
    )
