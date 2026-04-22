"""Facet filter for the nabledge-6 faceted search flow.

Reads `index.toon`, applies an AND filter over the `type` and `category`
axes emitted by Stage 1, and returns the matching rows.

Design points:
- The filter is set-OR within each axis, AND across axes
  (`type ∈ want_type AND category ∈ want_category`).
- `processing_patterns` column in index.toon is ignored (it is redundant
  with `type=processing-pattern ∧ category=<pattern>` — see
  Stage 1 Round 2 / 3 logs for simulation).
- If either axis is empty on the Stage 1 side, that axis is a wildcard
  (no constraint) — this is how `out_of_scope` gets handled without
  special-casing.
- If both axes are empty, callers should short-circuit before invoking
  the filter (Stage 2 driver responsibility).
- Fallback ladder: if the AND result is empty, the driver may relax
  (drop type → drop category → empty). The filter itself is a pure
  function; fallback is orchestrated by the caller.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class IndexRow:
    title: str
    type: str
    category: str
    path: str  # relative to knowledge/ root


def _parse_row(line: str) -> IndexRow | None:
    """Parse a single `  title, type, category, processing_patterns, path` row.

    Titles may contain commas inside parentheses; split on comma but
    trust that the *last* four comma-separated fields are the axes +
    path. The format is stable enough that `rsplit(",", 4)` is reliable.
    """
    s = line.strip()
    if not s or s.startswith("#") or s.startswith("files["):
        return None
    # Rightmost 4 commas separate type, category, pp, path from title.
    head, type_, category, _pp, path = [p.strip() for p in s.rsplit(",", 4)]
    return IndexRow(title=head, type=type_, category=category, path=path)


def load_index(index_path: Path) -> list[IndexRow]:
    rows: list[IndexRow] = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        row = _parse_row(line)
        if row is not None:
            rows.append(row)
    return rows


def filter_rows(
    rows: list[IndexRow],
    want_type: list[str],
    want_category: list[str],
) -> list[IndexRow]:
    """Return rows where `row.type ∈ want_type` AND `row.category ∈ want_category`.

    Empty `want_*` means "no constraint on that axis" (wildcard).
    """
    t_set = set(want_type)
    c_set = set(want_category)

    def ok(row: IndexRow) -> bool:
        if t_set and row.type not in t_set:
            return False
        if c_set and row.category not in c_set:
            return False
        return True

    return [r for r in rows if ok(r)]


@dataclass
class FilterOutcome:
    rows: list[IndexRow]
    fallback_used: str  # "none", "drop-category", "drop-type", "all", "empty"


def filter_with_fallback(
    rows: list[IndexRow],
    want_type: list[str],
    want_category: list[str],
    min_rows: int = 1,
) -> FilterOutcome:
    """AND filter with fallback ladder.

    Ladder (first hit wins):
      1. AND(type, category)        → "none" if len >= min_rows
      2. type only (drop category)  → "drop-category"
      3. category only (drop type)  → "drop-type"
      4. all rows                   → "all"
      5. [] (no rows in index)      → "empty"

    When both want_type and want_category are empty, the first step
    returns all rows (no constraint), which maps to "none".
    """
    primary = filter_rows(rows, want_type, want_category)
    if len(primary) >= min_rows:
        return FilterOutcome(rows=primary, fallback_used="none")

    if want_type:
        type_only = filter_rows(rows, want_type, [])
        if len(type_only) >= min_rows:
            return FilterOutcome(rows=type_only, fallback_used="drop-category")

    if want_category:
        cat_only = filter_rows(rows, [], want_category)
        if len(cat_only) >= min_rows:
            return FilterOutcome(rows=cat_only, fallback_used="drop-type")

    if rows:
        return FilterOutcome(rows=rows, fallback_used="all")
    return FilterOutcome(rows=[], fallback_used="empty")
