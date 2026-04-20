"""Excel security checklist converter for RBKC.

Converts 'Nablarch機能のセキュリティ対応表' Excel files into section-split form
suitable for knowledge JSON files.  No AI, no external API calls.

**Format**: Each vulnerability group (identified by integer No. in col B)
becomes one Section.  All rows belonging to the group form the section content.

**Sheet**: '2.チェックリスト'

**Column layout**:
  B (1):  No. (integer for first row of each vulnerability group)
  C (2):  脆弱性の種類 (vulnerability name, in first row of group)
  D (3):  sub-category within XSS entry (optional)
  E (4):  対策の性質 (e.g. '根本的解決' / '保険的対策')
  G (6):  チェック (□ marker, optional)
  H (7):  実施項目 (action item description)
  I (8):  番号 e.g. '1-(i)-a'
  J (9):  対応するNablarchの機能
  K (10): Nablarchでの対応状況 (〇/×/△)
  L (11): 解説 (detailed explanation, usually only in first row of group)

Public API:
    convert(path: Path, file_id: str = "") -> RSTResult
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import openpyxl

from scripts.create.converters.rst import RSTResult, Section

_SHEET_NAME = "2.チェックリスト"

# Column indices (0-based)
_COL_NO = 1          # B: vulnerability group No.
_COL_VULN = 2        # C: 脆弱性の種類
_COL_NATURE = 4      # E: 対策の性質
_COL_ACTION = 7      # H: 実施項目
_COL_ACTION_NO = 8   # I: 実施項目番号
_COL_FEATURE = 9     # J: 対応Nablarch機能
_COL_STATUS = 10     # K: 対応状況
_COL_NOTE = 11       # L: 解説


@dataclass
class _MeasureRow:
    nature: str
    action: str
    action_no: str
    feature: str
    status: str


@dataclass
class _VulnGroup:
    no: int
    name: str
    rows: list[_MeasureRow] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _cell(row: tuple, idx: int) -> str:
    """Return cell value at *idx* as string, or empty string."""
    if idx >= len(row):
        return ""
    val = row[idx]
    if val is None:
        return ""
    return str(val).strip()


def _collect_groups(ws) -> list[_VulnGroup]:
    """Parse the チェックリスト sheet into vulnerability groups."""
    groups: list[_VulnGroup] = []
    current: _VulnGroup | None = None

    for row in ws.iter_rows(values_only=True):
        no_val = row[_COL_NO] if len(row) > _COL_NO else None
        vuln_name = _cell(row, _COL_VULN)

        # Detect start of a new vulnerability group
        if isinstance(no_val, int) and vuln_name:
            # Clean up multi-line vulnerability names (e.g. CSRF has newline)
            clean_name = vuln_name.replace("\n", "").strip()
            current = _VulnGroup(no=no_val, name=clean_name)
            groups.append(current)

        if current is None:
            continue

        # Collect 解説 from every row that has one
        note = _cell(row, _COL_NOTE)
        if note and note not in current.notes:
            current.notes.append(note)

        # Add measure row if it has an action item
        action = _cell(row, _COL_ACTION)
        if action:
            nature = _cell(row, _COL_NATURE)
            action_no = _cell(row, _COL_ACTION_NO)
            feature = _cell(row, _COL_FEATURE)
            status = _cell(row, _COL_STATUS)
            current.rows.append(_MeasureRow(
                nature=nature,
                action=action,
                action_no=action_no,
                feature=feature,
                status=status,
            ))

    return groups


def _esc(s: str) -> str:
    """Escape Markdown table cell: replace pipe and normalize newlines."""
    return s.replace("|", "｜").replace("\n", " ")


def _group_to_section(group: _VulnGroup) -> Section:
    """Convert a :class:`_VulnGroup` to a :class:`Section`."""
    title = f"{group.no}. {group.name}"

    parts: list[str] = []

    # Measure table (data rows only; no fixed header — header text not in Excel source)
    if group.rows:
        rows = [
            f"| {_esc(r.nature)} | {_esc(r.action)} | {_esc(r.action_no)}"
            f" | {_esc(r.feature)} | {_esc(r.status)} |"
            for r in group.rows
        ]
        parts.append("\n".join(rows))

    # Explanations collected from all rows in the group
    for note in group.notes:
        parts.append(note)

    return Section(title=title, content="\n\n".join(parts))


def convert(path: Path, file_id: str = "") -> RSTResult:
    """Convert a security checklist Excel file at *path* to :class:`RSTResult`.

    Args:
        path: Path to the ``.xlsx`` file.
        file_id: Unused; present for API consistency with other converters.

    Returns:
        :class:`RSTResult` with one :class:`Section` per vulnerability group.
    """
    wb = openpyxl.load_workbook(str(path), data_only=True)

    if _SHEET_NAME not in wb.sheetnames:
        raise ValueError(f"Sheet '{_SHEET_NAME}' not found in {path}")
    ws = wb[_SHEET_NAME]

    groups = _collect_groups(ws)
    sections = [_group_to_section(g) for g in groups]

    doc_title = path.stem  # e.g. 'Nablarch機能のセキュリティ対応表'

    return RSTResult(
        title=doc_title,
        no_knowledge_content=False,
        sections=sections,
    )
