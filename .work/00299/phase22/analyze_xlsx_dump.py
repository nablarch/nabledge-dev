"""Analyze xlsx-full-dump.json and report:

1. Classification counts (P1 / P2 / loaded-fail)
2. Preamble distribution: how many P1 sheets have preamble, total cells, value patterns
3. Header-row count distribution (how many sheets have 1/2/3+ header rows)
4. Column-composition:
   a. duplicate-after-compose count (0 = composition succeeds universally)
   b. separator collision: how many composed columns contain " / " / ": " / etc.
   c. last-char distribution of composed column names
5. Cell values containing " / " substring in actual data (would collide with separator)
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

SEP = " / "
PATH = Path("/home/tie303177/work/nabledge/work2/.work/00299/phase22/xlsx-full-dump.json")
records = json.loads(PATH.read_text(encoding="utf-8"))

print(f"# Total sheets: {len(records)}")

# 1. classification
klass = Counter()
errors = 0
for r in records:
    if r.get("error"):
        errors += 1
        continue
    klass[r["classification_guess"]] += 1
print(f"\n## Classification (by auto-heuristic)")
print(f"error/load_fail: {errors}")
for k, v in klass.items():
    print(f"{k}: {v}")

# 2. preamble
p1_sheets = [r for r in records if r.get("classification_guess") == "P1"]
p1_with_preamble = [r for r in p1_sheets if r["preamble_cells"]]
print(f"\n## P1 preamble distribution")
print(f"P1 total: {len(p1_sheets)}")
print(f"P1 with non-empty preamble: {len(p1_with_preamble)}")

pre_cell_count = Counter()
for r in p1_with_preamble:
    pre_cell_count[len(r["preamble_cells"])] += 1
print("preamble cell count distribution:")
for k in sorted(pre_cell_count.keys()):
    print(f"  {k} cells: {pre_cell_count[k]} sheets")

# preamble value length
max_len = 0
for r in p1_with_preamble:
    for _, _, v in r["preamble_cells"]:
        max_len = max(max_len, len(v))
print(f"longest preamble cell: {max_len} chars")

# 3. header rows
hr_count = Counter()
for r in p1_sheets:
    hr_count[len(r["header_rows"])] += 1
print(f"\n## Header-row count distribution (P1)")
for k in sorted(hr_count.keys()):
    print(f"  {k} rows: {hr_count[k]} sheets")

# 4. column composition duplicates
dup_sheets = [r for r in p1_sheets if r["duplicate_after_compose"]]
print(f"\n## Duplicate-after-compose (should be 0 for span-compose to work universally)")
print(f"P1 sheets with duplicate composed columns: {len(dup_sheets)}")
for r in dup_sheets:
    non_empty = [c for c in r["columns_composed"] if c]
    print(f"  {r['file']} :: {r['sheet']}")
    print(f"    composed: {non_empty}")

# column separator collision: does any EXISTING column name contain " / "?
sep_in_source = []
for r in p1_sheets:
    for raw_row in r["columns_raw"]:
        for c in raw_row:
            if c and SEP in c:
                sep_in_source.append((r["file"], r["sheet"], c))
print(f"\n## Separator collision (raw column cells containing '{SEP}')")
print(f"count: {len(sep_in_source)}")
for ex in sep_in_source[:10]:
    print(f"  {ex}")

# column-ending patterns (for QP line-format safety)
end_counter = Counter()
for r in p1_sheets:
    for c in r["columns_composed"]:
        if not c:
            continue
        if c.endswith(": "):
            end_counter[": "] += 1
        if c.endswith(":"):
            end_counter[":"] += 1
        if c.endswith("/"):
            end_counter["/"] += 1
        if c.endswith(" / "):
            end_counter[" / "] += 1
print(f"\n## Composed-column trailing patterns")
for k, v in end_counter.items():
    print(f"  ends with {k!r}: {v}")

# 5. does any DATA cell contain " / "? (would collide with separator if we reverse-parse)
# We did NOT record data cells. Check just column_raw and a note.
# verify does forward containment, not reverse-parse, so this is just diagnostic.
print(f"\n## Note: verify does forward containment (JSON line -> cell), not reverse-parse. Separator collision in data cells doesn't break QP.")
