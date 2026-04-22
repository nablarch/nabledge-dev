#!/usr/bin/env python3
"""X-2-b: Enumerate RST block-level syntax occurrences across all versions.

Output: .work/00299/phase21x/block-patterns.json

Categories:
  - directives: name and count (from ^.. <name>::)
  - section_underlines: which punctuation characters appear under headings
  - simple_table_count: lines that look like simple-table separators (=== ===)
  - grid_table_count: lines that look like grid-table separators (+---+)
  - list_table_count: .. list-table:: occurrences (subset of directives)
  - field_list_names: ^:name: occurrences outside directive blocks
  - bullet_markers: first char in ^[*+-] pos-0 list items
  - enumerated_markers: (1) / 1. / a. patterns at start of line
  - line_block_count: leading '|' lines
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools/rbkc"))

from scripts.create.scan import scan_sources  # noqa: E402

VERSIONS = ["6", "5", "1.4", "1.3", "1.2"]
OUT = Path(__file__).parent / "block-patterns.json"
SAMPLE_LIMIT = 5

P_DIRECTIVE = re.compile(r"^(\s*)\.\.\s+([A-Za-z][A-Za-z0-9_:-]*)\s*::(?:\s+(.*))?$")
P_SIMPLE_TABLE_SEP = re.compile(r"^\s*=+( +=+)+\s*$")
P_GRID_TABLE_SEP = re.compile(r"^\s*\+-+(?:\+-+)+\+\s*$")
P_GRID_TABLE_HEAD = re.compile(r"^\s*\+=+(?:\+=+)+\+\s*$")
P_SECTION_UNDERLINE = re.compile(r"^([=\-`~'\"*^+#<>:._])\1{2,}\s*$")
P_FIELD_LIST = re.compile(r"^\s*:([A-Za-z][A-Za-z0-9_ -]*):\s+\S")
P_BULLET = re.compile(r"^(\s*)([*+\-])\s+\S")
P_ENUMERATED = re.compile(r"^(\s*)(\(?[0-9a-zA-Z]+[\.\)])\s+\S")
P_LINE_BLOCK = re.compile(r"^\s*\|\s")
P_COMMENT = re.compile(r"^\s*\.\.\s+$|^\s*\.\.\s+[^A-Za-z]")


def _make_sink() -> dict:
    return {
        "directives": Counter(),
        "directive_samples": {},
        "section_underlines": Counter(),
        "simple_table_count": 0,
        "grid_table_sep_count": 0,
        "grid_table_head_count": 0,
        "field_list": Counter(),
        "bullet_markers": Counter(),
        "enumerated_markers": Counter(),
        "line_block_count": 0,
        "comment_count": 0,
    }


def scan_file(text: str, path_rel: str, sink: dict) -> None:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = P_DIRECTIVE.match(line)
        if m:
            name = m.group(2)
            sink["directives"][name] += 1
            samples = sink["directive_samples"].setdefault(name, [])
            if len(samples) < SAMPLE_LIMIT:
                samples.append(f"{path_rel}:{i+1}: {line.strip()!r}")
            continue
        if P_SIMPLE_TABLE_SEP.match(line):
            sink["simple_table_count"] += 1
        if P_GRID_TABLE_SEP.match(line):
            sink["grid_table_sep_count"] += 1
        if P_GRID_TABLE_HEAD.match(line):
            sink["grid_table_head_count"] += 1
        mu = P_SECTION_UNDERLINE.match(line)
        if mu and i > 0 and lines[i - 1].strip():
            sink["section_underlines"][mu.group(1)] += 1
        mf = P_FIELD_LIST.match(line)
        if mf:
            sink["field_list"][mf.group(1).strip()] += 1
        mb = P_BULLET.match(line)
        if mb:
            sink["bullet_markers"][mb.group(2)] += 1
        me = P_ENUMERATED.match(line)
        if me:
            sink["enumerated_markers"][me.group(2)] += 1
        if P_LINE_BLOCK.match(line):
            sink["line_block_count"] += 1


def scan_version(version: str) -> tuple[dict, int]:
    sources = scan_sources(version, REPO_ROOT)
    rst = [s for s in sources if s.format == "rst"]
    sink = _make_sink()
    for sf in rst:
        rel = str(sf.path.relative_to(REPO_ROOT))
        try:
            text = sf.path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scan_file(text, rel, sink)
    return sink, len(rst)


def _summarize_sink(sink: dict) -> dict:
    return {
        "directives_top_50": sink["directives"].most_common(50),
        "directives_unique": len(sink["directives"]),
        "directive_samples": sink["directive_samples"],
        "section_underlines": dict(sink["section_underlines"]),
        "simple_table_count": sink["simple_table_count"],
        "grid_table_sep_count": sink["grid_table_sep_count"],
        "grid_table_head_count": sink["grid_table_head_count"],
        "field_list_top_30": sink["field_list"].most_common(30),
        "field_list_unique": len(sink["field_list"]),
        "bullet_markers": dict(sink["bullet_markers"]),
        "enumerated_markers": dict(sink["enumerated_markers"].most_common(20)),
        "line_block_count": sink["line_block_count"],
    }


def _merge(global_sink: dict, v_sink: dict) -> None:
    global_sink["directives"].update(v_sink["directives"])
    for name, samples in v_sink["directive_samples"].items():
        tgt = global_sink["directive_samples"].setdefault(name, [])
        for s in samples:
            if len(tgt) < SAMPLE_LIMIT:
                tgt.append(s)
    global_sink["section_underlines"].update(v_sink["section_underlines"])
    global_sink["simple_table_count"] += v_sink["simple_table_count"]
    global_sink["grid_table_sep_count"] += v_sink["grid_table_sep_count"]
    global_sink["grid_table_head_count"] += v_sink["grid_table_head_count"]
    global_sink["field_list"].update(v_sink["field_list"])
    global_sink["bullet_markers"].update(v_sink["bullet_markers"])
    global_sink["enumerated_markers"].update(v_sink["enumerated_markers"])
    global_sink["line_block_count"] += v_sink["line_block_count"]


def main() -> int:
    report: dict = {"versions": {}, "totals": {}}
    global_sink = _make_sink()

    for v in VERSIONS:
        sink, n = scan_version(v)
        report["versions"][v] = {"rst_file_count": n, **_summarize_sink(sink)}
        _merge(global_sink, sink)

    report["totals"] = _summarize_sink(global_sink)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")

    t = report["totals"]
    print(f"\n=== TOTALS ({sum(r['rst_file_count'] for r in report['versions'].values())} RST files) ===", file=sys.stderr)
    print(f"  directives: {t['directives_unique']} unique (top):", file=sys.stderr)
    for name, cnt in t["directives_top_50"][:20]:
        print(f"    {name:25s} {cnt}", file=sys.stderr)
    print(f"  simple-table seps:  {t['simple_table_count']}", file=sys.stderr)
    print(f"  grid-table seps:    {t['grid_table_sep_count']}", file=sys.stderr)
    print(f"  grid-table heads:   {t['grid_table_head_count']}", file=sys.stderr)
    print(f"  field lists: {t['field_list_unique']} unique (top):", file=sys.stderr)
    for name, cnt in t["field_list_top_30"][:10]:
        print(f"    {name:25s} {cnt}", file=sys.stderr)
    print(f"  section underlines: {t['section_underlines']}", file=sys.stderr)
    print(f"  bullet markers:     {t['bullet_markers']}", file=sys.stderr)
    print(f"  enumerated (top):   {t['enumerated_markers']}", file=sys.stderr)
    print(f"  line-block lines:   {t['line_block_count']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
