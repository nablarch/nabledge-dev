#!/bin/bash
# Phase 7.5: Generate Excel Files
# Converts mapping JSON files to Excel format for review

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR"

echo "=== Phase 7.5: Generate Excel Files ==="
echo ""

if [ ! -f "$WORK_DIR/mapping-v6.json" ] || [ ! -f "$WORK_DIR/mapping-v5.json" ]; then
    echo "❌ Error: mapping-v6.json or mapping-v5.json not found"
    exit 1
fi

# Function to convert JSON to Excel
convert_to_excel() {
    local json_file=$1
    local excel_file=$2
    local version=$3

    echo "Converting $version to Excel..."

    python3 - "$json_file" "$excel_file" "$version" << 'PYTHON_SCRIPT'
import sys
import json

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
except ImportError:
    print("❌ Error: openpyxl not installed. Install with: pip3 install openpyxl")
    sys.exit(1)

json_file = sys.argv[1]
excel_file = sys.argv[2]
version = sys.argv[3]

# Read JSON
with open(json_file, 'r') as f:
    data = json.load(f)

# Sort mappings by source_file (ascending)
mappings = sorted(data['mappings'], key=lambda x: x['source_file'])

# Create workbook
wb = Workbook()
ws = wb.active
ws.title = f"Mapping v{version}"

# Header style
header_font = Font(bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
header_alignment = Alignment(horizontal="center", vertical="center")

# Define columns
columns = [
    ("ID", 15),
    ("Source File", 60),
    ("Title", 40),
    ("Categories", 40),
    ("Target Files", 60),
    ("Alternatives", 60)
]

# Write header
for col_idx, (col_name, col_width) in enumerate(columns, start=1):
    cell = ws.cell(row=1, column=col_idx, value=col_name)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = header_alignment
    ws.column_dimensions[get_column_letter(col_idx)].width = col_width

# Write data
for row_idx, mapping in enumerate(mappings, start=2):
    ws.cell(row=row_idx, column=1, value=mapping.get('id', ''))
    ws.cell(row=row_idx, column=2, value=mapping.get('source_file', ''))
    ws.cell(row=row_idx, column=3, value=mapping.get('title', ''))

    # Categories (comma-separated)
    categories = ', '.join(mapping.get('categories', []))
    ws.cell(row=row_idx, column=4, value=categories)

    # Target files (comma-separated)
    target_files = ', '.join(mapping.get('target_files', []))
    ws.cell(row=row_idx, column=5, value=target_files)

    # Alternatives (comma-separated)
    alternatives = ', '.join(mapping.get('source_file_alternatives', []))
    ws.cell(row=row_idx, column=6, value=alternatives)

# Freeze header row
ws.freeze_panes = "A2"

# Save
wb.save(excel_file)
print(f"  ✅ Generated {excel_file} ({len(mappings)} entries)")
PYTHON_SCRIPT
}

# Convert v6
convert_to_excel "$WORK_DIR/mapping-v6.json" \
                 "$WORK_DIR/mapping-v6.xlsx" \
                 "6"

# Convert v5
convert_to_excel "$WORK_DIR/mapping-v5.json" \
                 "$WORK_DIR/mapping-v5.xlsx" \
                 "5"

echo ""
echo "=== Phase 7.5 Complete ==="
echo ""
echo "Output:"
echo "  - $WORK_DIR/mapping-v6.xlsx"
echo "  - $WORK_DIR/mapping-v5.xlsx"
echo ""
echo "Next step: Phase 8 - Clean up intermediate files"
