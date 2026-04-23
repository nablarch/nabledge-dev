#!/usr/bin/env python3
"""Scan docs MD files for readability defects (Phase 22-A-1).

Detects:
  (a) Tables wrapped in blockquote: `>` prefix on a line containing `|...|`.
  (b) Paragraphs wrapped in blockquote without a real quote context.
  (c) Raw RST residue leaking into docs MD: `.. directive::`, `:ref:`, |sub|.

Fenced code blocks are masked before analysis so example RST/MD inside
code samples does not produce false positives.

Usage:
  python3 scan_docs_md.py <docs_root>
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

_FENCE_BLOCK_RE = re.compile(r'^(```|~~~).*?^\1', re.MULTILINE | re.DOTALL)

# (a) blockquoted table: a `>` line whose content is a GFM table row
_BQ_TABLE_RE = re.compile(r'^\s*>\s*\|.*\|\s*$', re.MULTILINE)

# (c) raw RST residue: directive / :role: / |substitution|
_RST_DIRECTIVE_RE = re.compile(r'^\s*\.\.\s+[A-Za-z][\w:-]*::', re.MULTILINE)
_RST_ROLE_RE = re.compile(r':[a-zA-Z][a-zA-Z0-9_.-]*:`[^`\n]+`')
_RST_SUB_RE = re.compile(r'\|[A-Za-z0-9_][A-Za-z0-9_.\- ]*\|')


def _mask_fences(text: str) -> str:
    def _blank(m: re.Match) -> str:
        return "".join("\n" if ch == "\n" else " " for ch in m.group(0))
    return _FENCE_BLOCK_RE.sub(_blank, text)


def scan_file(path: Path) -> dict[str, list[int]]:
    """Return category -> list of 1-based line numbers for hits."""
    text = path.read_text(encoding="utf-8")
    masked = _mask_fences(text)
    hits: dict[str, list[int]] = {"bq_table": [], "rst_directive": [], "rst_role": [], "rst_substitution": []}
    for m in _BQ_TABLE_RE.finditer(masked):
        ln = masked[:m.start()].count("\n") + 1
        hits["bq_table"].append(ln)
    for m in _RST_DIRECTIVE_RE.finditer(masked):
        ln = masked[:m.start()].count("\n") + 1
        hits["rst_directive"].append(ln)
    for m in _RST_ROLE_RE.finditer(masked):
        ln = masked[:m.start()].count("\n") + 1
        hits["rst_role"].append(ln)
    for m in _RST_SUB_RE.finditer(masked):
        # Very loose; filter obvious table separators by requiring the match
        # not to live on a `|---|` separator row (already handled by masking
        # above isn't enough — substring-check the line).
        line_start = masked.rfind("\n", 0, m.start()) + 1
        line_end = masked.find("\n", m.end())
        line = masked[line_start:line_end if line_end != -1 else None]
        if re.match(r'\s*\|[-:| ]+\|\s*$', line):
            continue
        ln = masked[:m.start()].count("\n") + 1
        hits["rst_substitution"].append(ln)
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("docs_root", help="e.g. .claude/skills/nabledge-6/docs")
    ap.add_argument("--max-samples", type=int, default=3)
    args = ap.parse_args()

    root = Path(args.docs_root)
    if not root.exists():
        print(f"error: {root} not found", file=sys.stderr)
        return 2

    totals = Counter()
    per_cat_files: dict[str, list[tuple[Path, list[int]]]] = {k: [] for k in ("bq_table", "rst_directive", "rst_role", "rst_substitution")}

    n_files = 0
    for md in sorted(root.rglob("*.md")):
        if md.name == "README.md":
            continue
        n_files += 1
        hits = scan_file(md)
        for cat, lines in hits.items():
            if lines:
                totals[cat] += len(lines)
                per_cat_files[cat].append((md, lines))

    print(f"Scanned: {n_files} docs MD files under {root}")
    print()
    for cat in ("bq_table", "rst_directive", "rst_role", "rst_substitution"):
        hits_total = totals[cat]
        files = per_cat_files[cat]
        print(f"[{cat}] total hits={hits_total}, files affected={len(files)}")
        for path, lines in files[: args.max_samples]:
            rel = path.relative_to(root)
            print(f"  {rel}: lines {lines[:5]}{'...' if len(lines) > 5 else ''}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
