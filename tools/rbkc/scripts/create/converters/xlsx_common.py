"""Shared Excel parsing utilities for RBKC converters.

Implements Phase 22-B sheet-level file split: each worksheet produces one
:class:`RSTResult` (→ 1 JSON + 1 docs MD).  Release-note and security-table
converters share this logic; they differ only in the mapping entries that
select them.

Design reference: ``tools/rbkc/docs/rbkc-converter-design.md`` §8.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scripts.create.converters.rst import RSTResult, Section


# ---------------------------------------------------------------------------
# Raw sheet extraction (format-agnostic)
# ---------------------------------------------------------------------------

@dataclass
class RawSheet:
    """Sheet contents normalised to a 2-D list of stripped strings.

    Empty cells become ``""``.  Row lengths are uniform (padded with "").
    """
    name: str
    rows: list[list[str]]  # rows[r][c] -- all strings, "" when empty

    @property
    def nrows(self) -> int:
        return len(self.rows)

    @property
    def ncols(self) -> int:
        return len(self.rows[0]) if self.rows else 0


def list_sheet_names(path: Path) -> list[str]:
    """Return worksheet names in file order."""
    ext = path.suffix.lower()
    if ext == ".xls":
        import xlrd
        wb = xlrd.open_workbook(str(path))
        return [s.name for s in wb.sheets()]
    import openpyxl
    wb = openpyxl.load_workbook(str(path), data_only=True, read_only=True)
    return list(wb.sheetnames)


def read_sheet(path: Path, sheet_name: str) -> RawSheet:
    """Read one worksheet into :class:`RawSheet` (stripped strings, "" for empty)."""
    ext = path.suffix.lower()
    if ext == ".xls":
        import xlrd
        wb = xlrd.open_workbook(str(path))
        sheet = wb.sheet_by_name(sheet_name)
        rows: list[list[str]] = []
        for rx in range(sheet.nrows):
            row = []
            for cx in range(sheet.ncols):
                v = sheet.cell_value(rx, cx)
                row.append(str(v).strip() if v is not None else "")
            rows.append(row)
    else:
        import openpyxl
        wb = openpyxl.load_workbook(str(path), data_only=True)
        ws = wb[sheet_name]
        rows = []
        for row in ws.iter_rows(values_only=True):
            rows.append([
                str(v).strip() if v is not None else ""
                for v in row
            ])
    # Trim trailing fully-empty rows (common in xlsx).  Keep leading empties —
    # they preserve row numbering for reference.
    while rows and all(c == "" for c in rows[-1]):
        rows.pop()
    # Normalise row widths (openpyxl already does this; xlrd may vary).
    width = max((len(r) for r in rows), default=0)
    for r in rows:
        if len(r) < width:
            r.extend([""] * (width - len(r)))
    # Trim trailing all-empty columns.
    while width > 0 and all(r[width - 1] == "" for r in rows):
        for r in rows:
            r.pop()
        width -= 1
    return RawSheet(name=sheet_name, rows=rows)


# ---------------------------------------------------------------------------
# Title / preamble extraction
# ---------------------------------------------------------------------------

def _extract_title_and_preamble(sheet: RawSheet) -> tuple[str, str, int]:
    """Return (title, preamble, body_start_row_idx).

    * title  : row-1 ``■...`` text if present, else sheet name.
    * preamble: contiguous paragraph-like rows (single non-empty cell, first
                column) following the title, joined by newline.
    * body_start_row_idx: row index where the body (tables / data) begins.
    """
    rows = sheet.rows
    title = sheet.name
    i = 0
    if rows:
        first_non_empty = next(
            (v for v in rows[0] if v),
            "",
        )
        if first_non_empty.startswith("■"):
            # Keep `■` prefix verbatim so verify's 1:1 source-cell match
            # succeeds (spec §8-4: "title = row 1 の `■...`").
            title = first_non_empty
            i = 1

    preamble_lines: list[str] = []
    while i < len(rows):
        row = rows[i]
        non_empty = [c for c in row if c]
        if not non_empty:
            i += 1
            continue
        # A preamble row is a single text cell (paragraph).  Two or more
        # non-empty cells start the body (usually a header row).
        if len(non_empty) == 1:
            preamble_lines.append(non_empty[0])
            i += 1
            continue
        break
    return title, "\n".join(preamble_lines), i


# ---------------------------------------------------------------------------
# Header detection (P1 candidate)
# ---------------------------------------------------------------------------

def _run_length(row: list[str]) -> int:
    """Longest run of contiguous non-empty cells in *row*."""
    best = cur = 0
    for v in row:
        if v:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def _detect_header(sheet: RawSheet, body_start: int) -> tuple[int, list[str]] | None:
    """Find a header row at ``body_start`` onwards.

    A header is a row whose longest contiguous run of non-empty cells is
    ≥ 3 and which is followed by at least 2 data rows.  If row ``h+1`` is a
    sub-header (strictly narrower than ``h`` and every non-empty cell has
    a parent-to-the-left in ``h``), merge via ``メイン/副``.

    Returns ``(data_start, column_names)`` or ``None`` if no header found.
    """
    rows = sheet.rows
    n = len(rows)
    for h in range(body_start, min(body_start + 20, n)):
        row_h = rows[h]
        if _run_length(row_h) < 3:
            continue
        merged: list[str] = list(row_h)
        data_start = h + 1
        if h + 1 < n:
            row_h1 = rows[h + 1]
            if _looks_like_sub_header(row_h, row_h1):
                # Merge: for every sub-col, attach to the nearest non-empty
                # parent header at cx' <= cx.  Sub-cell with no parent on its
                # left keeps its own label.
                for cx, sub in enumerate(row_h1):
                    if not sub:
                        continue
                    parent_cx = cx
                    while parent_cx >= 0 and not row_h[parent_cx]:
                        parent_cx -= 1
                    if parent_cx >= 0 and row_h[parent_cx]:
                        merged[cx] = f"{row_h[parent_cx]}/{sub}"
                    else:
                        merged[cx] = sub
                data_start = h + 2
        # Need ≥ 2 data rows
        data_rows_available = 0
        for r in rows[data_start:]:
            if any(v for v in r):
                data_rows_available += 1
                if data_rows_available >= 2:
                    break
        if data_rows_available < 2:
            continue
        # Normalise column names: flatten whitespace (Excel cells often
        # contain embedded newlines for wrapping).
        columns = [_flatten_ws(c) for c in merged]
        return data_start, columns
    return None


def _looks_like_sub_header(row_h: list[str], row_h1: list[str]) -> bool:
    """True when ``row_h1`` is a sub-header attached to ``row_h``.

    Conditions (all must hold):

    * ``row_h1`` is non-empty and has strictly fewer non-empty cells than
      ``row_h`` (a sub-header is *narrower* than the parent; this rules
      out data rows which typically match or exceed the header width).
    * Every non-empty cell of ``row_h1`` has a non-empty parent in
      ``row_h`` at the same column or to its left (the parent "span").
    """
    h_non_empty = sum(1 for v in row_h if v)
    h1_non_empty_cols = [cx for cx, v in enumerate(row_h1) if v]
    if not h1_non_empty_cols:
        return False
    if len(h1_non_empty_cols) >= h_non_empty:
        return False
    for cx in h1_non_empty_cols:
        # Find nearest non-empty parent at cx' <= cx.
        px = cx
        while px >= 0 and not row_h[px]:
            px -= 1
        if px < 0 or not row_h[px]:
            return False
    return True


def _flatten_ws(s: str) -> str:
    """Collapse embedded whitespace/newlines to single spaces."""
    return " ".join(s.split())


# ---------------------------------------------------------------------------
# Sheet → RSTResult conversion
# ---------------------------------------------------------------------------

def sheet_to_result(sheet: RawSheet) -> tuple[RSTResult, dict]:
    """Convert one :class:`RawSheet` to an :class:`RSTResult`.

    Returns ``(result, meta)`` where ``meta`` carries the ``sheet_type``
    ("P1" | "P2") and, for P1, the table body (``columns`` + ``data_rows``)
    needed by docs.py to restore a MD table.  ``meta`` is serialised onto
    the output JSON verbatim via ``run._convert_and_write``.
    """
    title, preamble, body_start = _extract_title_and_preamble(sheet)

    # Column-count ≤ 2 is forced P2 per spec §8-2.
    useful_width = _useful_width(sheet, body_start)
    if useful_width > 2:
        header = _detect_header(sheet, body_start)
    else:
        header = None

    if header is not None:
        data_start, columns = header
        sections, data_rows = _build_p1_sections(sheet, data_start, columns)
        result = RSTResult(
            title=title,
            no_knowledge_content=False,
            content=preamble,
            sections=sections,
        )
        meta = {
            "sheet_type": "P1",
            "columns": columns,
            "data_rows": data_rows,
        }
        return result, meta

    # P2: single section-less content body.
    content = _build_p2_content(sheet, body_start, preamble)
    result = RSTResult(
        title=title,
        no_knowledge_content=False,
        content=content,
        sections=[],
    )
    meta = {"sheet_type": "P2"}
    return result, meta


def _useful_width(sheet: RawSheet, body_start: int) -> int:
    """Columns that actually contain data in the body."""
    width = sheet.ncols
    used = [False] * width
    for r in sheet.rows[body_start:]:
        for cx in range(min(width, len(r))):
            if r[cx]:
                used[cx] = True
    return sum(1 for u in used if u)


def _build_p1_sections(
    sheet: RawSheet,
    data_start: int,
    columns: list[str],
) -> tuple[list[Section], list[list[str]]]:
    """Emit one section per data row; return also the raw row matrix."""
    sections: list[Section] = []
    data_rows: list[list[str]] = []
    # Identify the "title column" — either a column named "タイトル", or
    # the first column that is not "No" / "No." / "№" / empty.
    title_col = _pick_title_col(columns)

    width = len(columns)
    for r in sheet.rows[data_start:]:
        cells = [c for c in r[:width]] + [""] * max(0, width - len(r))
        if not any(cells):
            continue
        # Forward-fill row-spanning cells: in merged-cell sheets, only the
        # top-left holds the value.  We currently do NOT forward-fill
        # (`openpyxl` already returns None for merged slaves), so each row
        # reflects what a reader sees.  This keeps verify's cell-tokens
        # model (tokens appear only in the top-left row) consistent.
        data_rows.append(cells)
        # Section title = value at title_col, with fallback.
        raw_title = cells[title_col] if 0 <= title_col < width else ""
        section_title = _flatten_ws(raw_title) or _first_non_empty(cells)
        # Section content = {col}: {val} vertical list (all non-empty cells).
        content_lines = []
        for cx, col in enumerate(columns):
            if cx >= len(cells):
                continue
            val = cells[cx]
            if not val:
                continue
            content_lines.append(f"{col}: {val}")
        sections.append(Section(
            title=section_title,
            content="\n".join(content_lines),
        ))
    return sections, data_rows


def _pick_title_col(columns: list[str]) -> int:
    """Choose the column index whose value we use as section title."""
    for cx, name in enumerate(columns):
        if name == "タイトル":
            return cx
    # Fallback: first column that is not a row-number column.
    for cx, name in enumerate(columns):
        if not name:
            continue
        if name in ("No", "No.", "№", "#"):
            continue
        return cx
    return 0


def _first_non_empty(cells: list[str]) -> str:
    return next((c for c in cells if c), "")


def _build_p2_content(sheet: RawSheet, body_start: int, preamble: str) -> str:
    """Flatten all body rows to text.  Preamble is prepended (blank-line sep)."""
    lines: list[str] = []
    if preamble:
        lines.append(preamble)
    for r in sheet.rows[body_start:]:
        non_empty = [c for c in r if c]
        if not non_empty:
            continue
        lines.append("  ".join(non_empty))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Convenience: per-file convert (used by run.py when sheet_name is given)
# ---------------------------------------------------------------------------

def convert_sheet(path: Path, sheet_name: str) -> tuple[RSTResult, dict]:
    sheet = read_sheet(path, sheet_name)
    return sheet_to_result(sheet)
