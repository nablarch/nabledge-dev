#!/usr/bin/env python3
"""X-2-a: Enumerate RST inline syntax occurrences across all versions.

Scans every RST source file enumerated by RBKC mappings for each supported
version, counts occurrences of each inline RST construct, and records
variations (e.g., distinct role names, directive options).

Output: .work/00299/phase21x/inline-patterns.json

The report contains, per pattern category:
  - total: aggregate count across all versions
  - per_version: count per version
  - variations: unique tokens (role names, substitution names, ...) with counts
  - samples: up to 5 raw example strings per category (repo-relative path + line)

Exit status is always 0; findings are the payload.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools/rbkc"))

from scripts.create.scan import scan_sources  # noqa: E402

VERSIONS = ["6", "5", "1.4", "1.3", "1.2"]
OUT = Path(__file__).parent / "inline-patterns.json"
SAMPLE_LIMIT = 5

# ----- patterns ------------------------------------------------------------
# Order matters for mutual exclusion: we match greedy things first and
# remove them from the line before matching simpler ones.

# 1. Inline role with target: :role:`text <target>`
P_ROLE_TARGET = re.compile(r":([A-Za-z][A-Za-z0-9_.:+-]*):`([^`<>]*)<([^`<>]+)>`")
# 2. Inline role simple: :role:`text`
P_ROLE_SIMPLE = re.compile(r":([A-Za-z][A-Za-z0-9_.:+-]*):`([^`]+)`")
# 3. Double-backtick inline literal: ``code``
P_DOUBLE_BACKTICK = re.compile(r"``([^`]+?)``")
# 4. External link named: `text <url>`_
P_EXT_LINK_NAMED = re.compile(r"`([^`<]+?)\s*<([^`<>]+)>`_(?!_)")
# 5. External link anon: `text <url>`__
P_EXT_LINK_ANON = re.compile(r"`([^`<]+?)\s*<([^`<>]+)>`__")
# 6. Plain reference: `text`_
P_REF_NAMED = re.compile(r"(?<![`:])`([^`<>\n]+?)`_(?!_)")
# 7. Anonymous reference: `text`__
P_REF_ANON = re.compile(r"(?<![`:])`([^`<>\n]+?)`__")
# 8. Substitution reference: |name|
# Per docutils spec, reference names are alphanumerics plus "-_.:+", and
# internal spaces are allowed but are normalised to single-space. Names may
# NOT start or end with whitespace. In practice in this corpus substitution
# names are ASCII identifiers, so we intentionally restrict to ASCII to keep
# grid-table cell contents (which frequently contain Japanese text between
# vertical pipes) from being counted as substitutions.
P_SUBSTITUTION = re.compile(r"\|([A-Za-z0-9][A-Za-z0-9_.:+\- ]*[A-Za-z0-9_.:+\-]|[A-Za-z0-9])\|")
# 9. Footnote/citation reference: [label]_
P_FOOTNOTE_REF = re.compile(r"\[([^\]\n]+?)\]_")
# 10. Strong emphasis: **text**
P_STRONG = re.compile(r"(?<![*])\*\*([^*\n]+?)\*\*(?![*])")
# 11. Emphasis: *text*
P_EMPHASIS = re.compile(r"(?<![*\w])\*([^*\s][^*\n]*?)\*(?![*\w])")
# 12. Interpreted text default: `text` (no role, no trailing underscore)
P_INTERPRETED = re.compile(r"(?<![`:_\w])`([^`<>\n]+?)`(?![_`])")


def _scan_line(line: str, sink: dict, sample_sink: dict, path_rel: str, lineno: int) -> None:
    """Apply patterns to a single line, updating counters and samples."""
    # We consume matches by replacing them to avoid double-counting
    # when a more specific pattern (role_target) overlaps with a generic
    # pattern (role_simple or interpreted).
    working = line

    def _count(name: str, m: re.Match, *, capture_key: str | None = None):
        sink[name]["count"] += 1
        if capture_key is not None:
            sink[name]["variations"][m.group(capture_key)] += 1
        if len(sample_sink[name]) < SAMPLE_LIMIT:
            sample_sink[name].append(f"{path_rel}:{lineno}: {m.group(0)!r}")

    # 1. Role with target (must come before role_simple and ext_link)
    def _role_target(m):
        _count("role_target", m, capture_key=1)
        return " " * (m.end() - m.start())

    working = P_ROLE_TARGET.sub(_role_target, working)

    # 2. Role simple
    def _role_simple(m):
        _count("role_simple", m, capture_key=1)
        return " " * (m.end() - m.start())

    working = P_ROLE_SIMPLE.sub(_role_simple, working)

    # 3. Double-backtick literal
    def _double_backtick(m):
        _count("double_backtick", m)
        return " " * (m.end() - m.start())

    working = P_DOUBLE_BACKTICK.sub(_double_backtick, working)

    # 4-5. External links (named + anon)
    def _ext_named(m):
        _count("ext_link_named", m)
        return " " * (m.end() - m.start())

    working = P_EXT_LINK_NAMED.sub(_ext_named, working)

    def _ext_anon(m):
        _count("ext_link_anon", m)
        return " " * (m.end() - m.start())

    working = P_EXT_LINK_ANON.sub(_ext_anon, working)

    # 6-7. Reference names
    def _ref_named(m):
        _count("ref_named", m)
        return " " * (m.end() - m.start())

    working = P_REF_NAMED.sub(_ref_named, working)

    def _ref_anon(m):
        _count("ref_anon", m)
        return " " * (m.end() - m.start())

    working = P_REF_ANON.sub(_ref_anon, working)

    # 8. Substitution
    def _subst(m):
        _count("substitution", m, capture_key=1)
        return " " * (m.end() - m.start())

    working = P_SUBSTITUTION.sub(_subst, working)

    # 9. Footnote ref
    def _fn(m):
        _count("footnote_ref", m)
        return " " * (m.end() - m.start())

    working = P_FOOTNOTE_REF.sub(_fn, working)

    # 10. Strong
    def _strong(m):
        _count("strong", m)
        return " " * (m.end() - m.start())

    working = P_STRONG.sub(_strong, working)

    # 11. Emphasis
    def _em(m):
        _count("emphasis", m)
        return " " * (m.end() - m.start())

    working = P_EMPHASIS.sub(_em, working)

    # 12. Interpreted text (bare backtick)
    def _interp(m):
        _count("interpreted", m)
        return " " * (m.end() - m.start())

    working = P_INTERPRETED.sub(_interp, working)


def _make_sink() -> dict:
    return {
        name: {"count": 0, "variations": Counter()}
        for name in [
            "role_target", "role_simple", "double_backtick",
            "ext_link_named", "ext_link_anon",
            "ref_named", "ref_anon",
            "substitution", "footnote_ref",
            "strong", "emphasis", "interpreted",
        ]
    }


def scan_version(version: str) -> tuple[dict, dict, int]:
    """Scan one version; return (sink, sample_sink, rst_file_count)."""
    sources = scan_sources(version, REPO_ROOT)
    rst_files = [s for s in sources if s.format == "rst"]
    sink = _make_sink()
    sample_sink: dict = {k: [] for k in sink}
    for sf in rst_files:
        rel = str(sf.path.relative_to(REPO_ROOT))
        try:
            text = sf.path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            _scan_line(line, sink, sample_sink, rel, lineno)
    return sink, sample_sink, len(rst_files)


def main() -> int:
    report = {"versions": {}, "totals": {}}
    global_totals = _make_sink()
    global_samples: dict = {k: [] for k in global_totals}

    for v in VERSIONS:
        sink, samples, n_files = scan_version(v)
        report["versions"][v] = {
            "rst_file_count": n_files,
            "patterns": {
                name: {
                    "count": info["count"],
                    "variations_top_20": info["variations"].most_common(20),
                    "unique_variations": len(info["variations"]),
                    "samples": samples[name],
                }
                for name, info in sink.items()
            },
        }
        # aggregate
        for name, info in sink.items():
            global_totals[name]["count"] += info["count"]
            global_totals[name]["variations"].update(info["variations"])
            for s in samples[name]:
                if len(global_samples[name]) < SAMPLE_LIMIT:
                    global_samples[name].append(s)

    report["totals"] = {
        name: {
            "count": info["count"],
            "unique_variations": len(info["variations"]),
            "variations_top_30": info["variations"].most_common(30),
            "samples": global_samples[name],
        }
        for name, info in global_totals.items()
    }

    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    # Print compact summary to stderr for quick human scan
    print("\n=== TOTALS (all versions) ===", file=sys.stderr)
    for name, info in report["totals"].items():
        print(f"  {name:20s} count={info['count']:6d} uniq={info['unique_variations']:4d}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
