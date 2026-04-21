"""Excel security checklist converter for RBKC.

Converts 'Nablarch機能のセキュリティ対応表' Excel files into a single flat
section containing all non-empty cell values from all sheets in row-major order.
No AI, no external API calls.

All cell values are preserved verbatim so verify can confirm 100% coverage.

Public API:
    convert(path: Path, file_id: str = "") -> RSTResult
"""
from __future__ import annotations

from pathlib import Path

import openpyxl

from scripts.create.converters.rst import RSTResult, Section


def convert(path: Path, file_id: str = "") -> RSTResult:
    """Convert a security checklist Excel file at *path* to :class:`RSTResult`.

    Args:
        path: Path to the ``.xlsx`` file.
        file_id: Unused; present for API consistency with other converters.

    Returns:
        :class:`RSTResult` with a single section containing all cell values.
    """
    wb = openpyxl.load_workbook(str(path), data_only=True)

    lines = []
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            cells = [str(c).strip() for c in row if c is not None and str(c).strip()]
            if cells:
                lines.append("  ".join(cells))

    return RSTResult(
        title="",
        no_knowledge_content=False,
        content="\n".join(lines),
        sections=[],
    )
