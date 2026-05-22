"""
Prototype script for Task 3: generate expected JSON + docs MD for security-check-2 sheet
with P1-merged grouping applied.

Strategy: load the real RBKC-generated JSON, keep everything (id, title, content, columns,
sheet_type, etc.) and only replace sections/data_rows/index + add sheet_subtype.
This ensures columns and other fields are byte-for-byte identical to RBKC output.

This is a one-off script — not production code.
"""
import json
import openpyxl
from pathlib import Path

EXCEL_PATH = Path(__file__).parents[2] / ".lw/nab-official/v6/nablarch-system-development-guide/Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx"
SHEET_NAME = "2.チェックリスト"
CURRENT_JSON = Path(__file__).parents[2] / ".claude/skills/nabledge-6/knowledge/check/security-check/security-check-2.チェックリスト.json"
TITLE_COL = 3  # column C (1-indexed)
DATA_START_ROW = 9  # row 9 is first data row (rows 7-8 are header)


def get_merged_groups(ws, title_col, data_start_row):
    """Return list of (start_row, end_row) for each vulnerability group, sorted by row."""
    merge_ranges = []
    for m in ws.merged_cells.ranges:
        if m.min_col <= title_col <= m.max_col and m.min_row >= data_start_row:
            merge_ranges.append((m.min_row, m.max_row))

    last_data_row = data_start_row
    for row_idx in range(data_start_row, ws.max_row + 1):
        row_vals = [ws.cell(row=row_idx, column=c).value for c in range(1, ws.max_column + 1)]
        if any(v is not None for v in row_vals):
            last_data_row = row_idx

    merged_rows = set()
    for start, end in merge_ranges:
        for r in range(start, end + 1):
            merged_rows.add(r)

    groups = list(merge_ranges)
    for row_idx in range(data_start_row, last_data_row + 1):
        title_val = ws.cell(row=row_idx, column=title_col).value
        if row_idx not in merged_rows and title_val is not None:
            groups.append((row_idx, row_idx))

    groups.sort(key=lambda x: x[0])
    return groups, last_data_row


def flatten_cell(val):
    """Mirror RBKC's _flatten_ws: collapse all whitespace (incl. \\n, 　) to single spaces."""
    if val is None:
        return ""
    return " ".join(str(val).split())


def build_section_content(ws, start_row, end_row, columns):
    """Build section content string matching RBKC's {col_name}: {value} format."""
    lines = []
    for row_idx in range(start_row, end_row + 1):
        for col_idx, col_name in enumerate(columns):
            if not col_name:
                continue
            val = ws.cell(row=row_idx, column=col_idx + 1).value
            if val is not None:
                flat = flatten_cell(val)
                if flat:
                    lines.append(f"{col_name}: {flat}")
    return "\n".join(lines)


def main():
    # Load existing JSON to reuse fields unchanged by this fix
    with open(CURRENT_JSON, encoding="utf-8") as f:
        base = json.load(f)

    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    ws = wb[SHEET_NAME]
    columns = base["columns"]

    groups, last_data_row = get_merged_groups(ws, TITLE_COL, DATA_START_ROW)
    print(f"Found {len(groups)} vulnerability groups (data rows {DATA_START_ROW}-{last_data_row})")

    # Build sections (1 group = 1 section)
    new_sections = []
    for i, (start_row, end_row) in enumerate(groups, 1):
        title = flatten_cell(ws.cell(row=start_row, column=TITLE_COL).value)
        content = build_section_content(ws, start_row, end_row, columns)
        new_sections.append({"id": f"s{i}", "title": title, "content": content})

    # data_rows: representative row only per group (1-indexed columns → list)
    new_data_rows = []
    for start_row, _ in groups:
        row = [ws.cell(row=start_row, column=c + 1).value or "" for c in range(len(columns))]
        new_data_rows.append(row)

    # index: __file__ + one per section
    new_index = [{"id": "__file__", "title": base["title"]}]
    for s in new_sections:
        new_index.append({"id": s["id"], "title": s["title"]})

    # Assemble output JSON (preserve all other fields from base)
    json_out = dict(base)
    json_out["sections"] = new_sections
    json_out["data_rows"] = new_data_rows
    json_out["sheet_subtype"] = "P1-merged"
    json_out["index"] = new_index

    json_path = Path(__file__).parent / "preview-security-check-2-checklist.json"
    json_path.write_text(json.dumps(json_out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Written JSON to: {json_path}")

    print(f"\n=== JSON sections ({len(new_sections)}) ===")
    for s in new_sections:
        line_count = s["content"].count("\n") + 1
        print(f"  {s['id']}: '{s['title']}' ({line_count} content lines)")

    # Build docs MD (mirror current RBKC docs.py P1 output format)
    # Use the current RBKC docs MD as reference for preamble/table format
    current_docs = Path(__file__).parents[2] / ".claude/skills/nabledge-6/docs/check/security-check/security-check-2.チェックリスト.md"
    current_md = current_docs.read_text(encoding="utf-8")
    # Keep everything up to and including the table (same as now), then replace section headings
    # Find the end of the table block (last `|` line before any `##`)
    md_lines = current_md.splitlines()
    table_end = 0
    for i, line in enumerate(md_lines):
        if line.startswith("|"):
            table_end = i
    # New MD = preamble + table (unchanged) + new section headings
    new_md_lines = md_lines[: table_end + 1]
    new_md_lines.append("")
    for s in new_sections:
        new_md_lines.append(f"## {s['title']}")
        new_md_lines.append("")
        new_md_lines.append(s["content"])
        new_md_lines.append("")

    md_path = Path(__file__).parent / "preview-security-check-2-checklist.md"
    md_path.write_text("\n".join(new_md_lines), encoding="utf-8")
    print(f"Written MD  to: {md_path}")


if __name__ == "__main__":
    main()
