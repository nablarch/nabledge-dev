#!/usr/bin/env python3
"""X-2-d: Enumerate MD source patterns (not RST).

Scans every MD source file collected by RBKC mapping (v6 only has MD today:
nablarch-system-development-guide/...md and the three top-level guides).

Reports:
  - HTML tags in use (e.g., <br>, <details>, <summary>)
  - Image syntaxes (![...](...)  and <img>)
  - Fenced code block languages
  - Link syntaxes
  - Inline code `...`
  - Heading levels

Output: .work/00299/phase21x/md-patterns.json
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
OUT = Path(__file__).parent / "md-patterns.json"
SAMPLE_LIMIT = 5

P_HTML_TAG = re.compile(r"<(/?[A-Za-z][A-Za-z0-9]*)(?:\s[^>]*)?>")
P_MD_LINK = re.compile(r"(?<!\!)\[([^\]\n]+?)\]\(([^)\n]+?)\)")
P_MD_IMAGE = re.compile(r"!\[([^\]\n]*)\]\(([^)\n]+?)\)")
P_FENCE = re.compile(r"^\s*```([A-Za-z0-9_+-]*)\s*$", re.MULTILINE)
P_INLINE_CODE = re.compile(r"(?<![`])`([^`\n]+?)`(?![`])")
P_HEADING = re.compile(r"^(#{1,6})\s+", re.MULTILINE)
P_REF_STYLE_LINK = re.compile(r"^\s*\[([^\]]+)\]:\s+(\S+)", re.MULTILINE)


def _sink() -> dict:
    return {
        "html_tags": Counter(),
        "fence_langs": Counter(),
        "heading_levels": Counter(),
        "md_link_count": 0,
        "md_image_count": 0,
        "inline_code_count": 0,
        "ref_link_count": 0,
        "samples": {
            "html_tags": [],
            "fence_langs": [],
            "md_link": [],
            "md_image": [],
            "inline_code": [],
            "ref_link": [],
        },
    }


def scan_file(text: str, rel: str, sink: dict) -> None:
    for m in P_HTML_TAG.finditer(text):
        sink["html_tags"][m.group(1).lower()] += 1
        if len(sink["samples"]["html_tags"]) < SAMPLE_LIMIT * 2:
            sink["samples"]["html_tags"].append(f"{rel}: {m.group(0)!r}")
    for m in P_MD_LINK.finditer(text):
        sink["md_link_count"] += 1
        if len(sink["samples"]["md_link"]) < SAMPLE_LIMIT:
            sink["samples"]["md_link"].append(f"{rel}: {m.group(0)!r}")
    for m in P_MD_IMAGE.finditer(text):
        sink["md_image_count"] += 1
        if len(sink["samples"]["md_image"]) < SAMPLE_LIMIT:
            sink["samples"]["md_image"].append(f"{rel}: {m.group(0)!r}")
    for m in P_FENCE.finditer(text):
        lang = m.group(1) or "(none)"
        sink["fence_langs"][lang] += 1
    for m in P_INLINE_CODE.finditer(text):
        sink["inline_code_count"] += 1
        if len(sink["samples"]["inline_code"]) < SAMPLE_LIMIT:
            sink["samples"]["inline_code"].append(f"{rel}: {m.group(0)!r}")
    for m in P_HEADING.finditer(text):
        sink["heading_levels"][len(m.group(1))] += 1
    for m in P_REF_STYLE_LINK.finditer(text):
        sink["ref_link_count"] += 1
        if len(sink["samples"]["ref_link"]) < SAMPLE_LIMIT:
            sink["samples"]["ref_link"].append(f"{rel}: {m.group(0)!r}")


def scan_version(version: str) -> tuple[dict, int]:
    sources = scan_sources(version, REPO_ROOT)
    md = [s for s in sources if s.format == "md"]
    sink = _sink()
    for sf in md:
        rel = str(sf.path.relative_to(REPO_ROOT))
        try:
            text = sf.path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scan_file(text, rel, sink)
    return sink, len(md)


def _summarize(sink: dict) -> dict:
    return {
        "html_tags": dict(sink["html_tags"].most_common(40)),
        "html_tags_unique": len(sink["html_tags"]),
        "fence_langs": dict(sink["fence_langs"].most_common(20)),
        "fence_langs_unique": len(sink["fence_langs"]),
        "heading_levels": dict(sink["heading_levels"]),
        "md_link_count": sink["md_link_count"],
        "md_image_count": sink["md_image_count"],
        "inline_code_count": sink["inline_code_count"],
        "ref_link_count": sink["ref_link_count"],
        "samples": sink["samples"],
    }


def main() -> int:
    report = {"versions": {}}
    for v in VERSIONS:
        sink, n = scan_version(v)
        report["versions"][v] = {"md_file_count": n, **_summarize(sink)}
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    for v, info in report["versions"].items():
        print(f"\n=== v{v} ({info['md_file_count']} MD files) ===", file=sys.stderr)
        if info["md_file_count"] == 0:
            continue
        print(f"  html tags unique: {info['html_tags_unique']}", file=sys.stderr)
        for tag, cnt in list(info["html_tags"].items())[:10]:
            print(f"    {tag:12s} {cnt}", file=sys.stderr)
        print(f"  fence langs: {info['fence_langs']}", file=sys.stderr)
        print(f"  heading levels: {info['heading_levels']}", file=sys.stderr)
        print(f"  md_link={info['md_link_count']} img={info['md_image_count']} inline_code={info['inline_code_count']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
