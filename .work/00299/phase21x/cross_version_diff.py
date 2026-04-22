#!/usr/bin/env python3
"""X-2-f: Compare inline/block pattern sets across versions.

Reads inline-patterns.json and block-patterns.json, reports per-version
counts for each pattern and flags any pattern that appears in only a
subset of versions. The goal: confirm the tokenizer's pattern set needs
no version-specific cases beyond what v6 already exhibits.

Output: .work/00299/phase21x/cross-version-diff.md
"""
from __future__ import annotations

import json
from pathlib import Path

BASE = Path(__file__).parent
INLINE = json.loads((BASE / "inline-patterns.json").read_text(encoding="utf-8"))
BLOCK = json.loads((BASE / "block-patterns.json").read_text(encoding="utf-8"))
OUT = BASE / "cross-version-diff.md"

VERSIONS = ["6", "5", "1.4", "1.3", "1.2"]


def main() -> int:
    lines = ["# Cross-version pattern comparison", ""]

    # ---- Inline ----
    lines.append("## Inline patterns (count per version)")
    lines.append("")
    header = "| Pattern | " + " | ".join(f"v{v}" for v in VERSIONS) + " |"
    sep = "|---|" + "---:|" * len(VERSIONS)
    lines.append(header)
    lines.append(sep)
    pattern_names = list(INLINE["totals"].keys())
    for name in pattern_names:
        row = [name]
        for v in VERSIONS:
            c = INLINE["versions"][v]["patterns"][name]["count"]
            row.append(str(c))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # ---- Role names (role_target + role_simple) ----
    lines.append("## Role names in use (per version)")
    lines.append("")
    for name in ["role_target", "role_simple"]:
        lines.append(f"### {name}")
        lines.append("")
        # Collect unique role names across versions
        all_names: dict[str, dict[str, int]] = {}
        for v in VERSIONS:
            vars_ = INLINE["versions"][v]["patterns"][name]["variations_top_20"]
            for rname, cnt in vars_:
                all_names.setdefault(rname, {v2: 0 for v2 in VERSIONS})[v] = cnt
        lines.append("| Role | " + " | ".join(f"v{v}" for v in VERSIONS) + " |")
        lines.append(sep)
        for rname, counts in sorted(all_names.items()):
            row = [rname] + [str(counts[v]) for v in VERSIONS]
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    # ---- Directives ----
    lines.append("## Directive names (per version)")
    lines.append("")
    all_dirs: dict[str, dict[str, int]] = {}
    for v in VERSIONS:
        vdirs = dict(BLOCK["versions"][v]["directives_top_50"])
        for dname, cnt in vdirs.items():
            all_dirs.setdefault(dname, {v2: 0 for v2 in VERSIONS})[v] = cnt
    lines.append("| Directive | " + " | ".join(f"v{v}" for v in VERSIONS) + " |")
    lines.append(sep)
    for dname in sorted(all_dirs.keys()):
        row = [dname] + [str(all_dirs[dname][v]) for v in VERSIONS]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # ---- Version-exclusive ----
    lines.append("## Patterns exclusive to a subset of versions")
    lines.append("")
    lines.append("### Directives appearing in < 5 versions")
    lines.append("")
    for dname in sorted(all_dirs.keys()):
        active = [v for v in VERSIONS if all_dirs[dname][v] > 0]
        if len(active) < len(VERSIONS):
            lines.append(f"- **{dname}**: present in {active}, absent elsewhere")
    lines.append("")

    lines.append("### Roles appearing in < 5 versions")
    lines.append("")
    for role_kind in ["role_target", "role_simple"]:
        all_role_names: dict[str, dict[str, int]] = {}
        for v in VERSIONS:
            for rname, cnt in INLINE["versions"][v]["patterns"][role_kind]["variations_top_20"]:
                all_role_names.setdefault(rname, {v2: 0 for v2 in VERSIONS})[v] = cnt
        for rname in sorted(all_role_names.keys()):
            active = [v for v in VERSIONS if all_role_names[rname][v] > 0]
            if len(active) < len(VERSIONS):
                lines.append(f"- **{role_kind}::{rname}**: {active}")
    lines.append("")

    # ---- Tables / line blocks ----
    lines.append("## Block metrics per version")
    lines.append("")
    metrics = ["simple_table_count", "grid_table_sep_count", "grid_table_head_count", "line_block_count"]
    lines.append("| Metric | " + " | ".join(f"v{v}" for v in VERSIONS) + " |")
    lines.append(sep)
    for m in metrics:
        row = [m] + [str(BLOCK["versions"][v][m]) for v in VERSIONS]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # Section underlines per version
    lines.append("## Section underline characters per version")
    lines.append("")
    lines.append("| v | Underline chars |")
    lines.append("|---|---|")
    for v in VERSIONS:
        u = BLOCK["versions"][v]["section_underlines"]
        lines.append(f"| v{v} | {u} |")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
