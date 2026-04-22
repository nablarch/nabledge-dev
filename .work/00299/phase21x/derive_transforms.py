#!/usr/bin/env python3
"""X-2-c: Derive converter transformation rules from source vs JSON output.

Pairs every RST source file with its generated knowledge JSON (from the
current snapshot), extracts each inline/block construct from the RST side,
locates the corresponding text in the JSON content, and records the
transformation rule (raw source → MD output) as a sample.

Output: .work/00299/phase21x/transform-rules.md (human review) and
.work/00299/phase21x/transform-rules.json (machine-readable sample set).

Notes:
- Only v6 is used for this pass (it has the freshest snapshot).
- For each pattern, up to SAMPLE_LIMIT concrete transformation examples
  are recorded; the intent is to be exhaustive about *kinds* of
  transformations, not about every instance.
- When the source token cannot be located in the output, the sample is
  recorded under "source_only" — those are candidates for tokenizer
  removal (not substring-matchable).
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools/rbkc"))

from scripts.create.scan import scan_sources  # noqa: E402

VERSION = "6"
OUT_MD = Path(__file__).parent / "transform-rules.md"
OUT_JSON = Path(__file__).parent / "transform-rules.json"
SAMPLE_LIMIT = 30
SNAPSHOT_PATH = REPO_ROOT / ".state" / VERSION / "snapshot.json"
KNOWLEDGE_DIR = REPO_ROOT / f".claude/skills/nabledge-{VERSION}/knowledge"

# Reuse inline patterns from scan_inline (redefined here to avoid circular import)
P_ROLE_TARGET = re.compile(r":([A-Za-z][A-Za-z0-9_.:+-]*):`([^`<>]*)<([^`<>]+)>`")
P_ROLE_SIMPLE = re.compile(r":([A-Za-z][A-Za-z0-9_.:+-]*):`([^`]+)`")
P_DOUBLE_BACKTICK = re.compile(r"``([^`]+?)``")
P_EXT_LINK_NAMED = re.compile(r"`([^`<]+?)\s*<([^`<>]+)>`_(?!_)")
P_EXT_LINK_ANON = re.compile(r"`([^`<]+?)\s*<([^`<>]+)>`__")
P_REF_NAMED = re.compile(r"(?<![`:])`([^`<>\n]+?)`_(?!_)")
P_SUBSTITUTION = re.compile(r"\|([A-Za-z0-9][A-Za-z0-9_.:+\- ]*[A-Za-z0-9_.:+\-]|[A-Za-z0-9])\|")
P_FOOTNOTE_REF = re.compile(r"\[([^\]\n]+?)\]_")
P_STRONG = re.compile(r"(?<![*])\*\*([^*\n]+?)\*\*(?![*])")
P_EMPHASIS = re.compile(r"(?<![*\w])\*([^*\s][^*\n]*?)\*(?![*\w])")
P_INTERPRETED = re.compile(r"(?<![`:_\w])`([^`<>\n]+?)`(?![_`])")

# Block patterns worth deriving
P_DIRECTIVE = re.compile(r"^(\s*)\.\.\s+([A-Za-z][A-Za-z0-9_:-]*)\s*::(?:\s+(.*))?$", re.MULTILINE)
P_COMMENT = re.compile(r"^\s*\.\.\s+(?![A-Za-z][A-Za-z0-9_:-]*::)(.*)$", re.MULTILINE)


def _load_snapshot() -> dict:
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


def _iter_pairs():
    """Yield (rst_path, json_data) for each converted source file."""
    snap = _load_snapshot()
    for rel, entry in snap["files"].items():
        if not rel.endswith(".rst"):
            continue
        rst_path = REPO_ROOT / rel
        out_rel = entry.get("output_path")
        if not out_rel:
            continue
        json_path = KNOWLEDGE_DIR / out_rel
        if not json_path.exists() or not rst_path.exists():
            continue
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        yield rst_path, data


def _collect_all_content(data: dict) -> str:
    """Flatten title + top-level content + all section content into one string."""
    parts = [data.get("title", ""), data.get("content", "")]
    for sec in data.get("sections", []):
        parts.append(sec.get("title", ""))
        parts.append(sec.get("content", ""))
    return "\n".join(parts)


def _short_context(text: str, offset: int, window: int = 40) -> str:
    lo = max(0, offset - window)
    hi = min(len(text), offset + window)
    return text[lo:hi].replace("\n", "\\n")


def main() -> int:
    samples: dict[str, list[dict]] = defaultdict(list)
    source_only: dict[str, list[dict]] = defaultdict(list)
    misses = defaultdict(int)
    hits = defaultdict(int)

    patterns = [
        ("role_target", P_ROLE_TARGET),
        ("role_simple", P_ROLE_SIMPLE),
        ("double_backtick", P_DOUBLE_BACKTICK),
        ("ext_link_named", P_EXT_LINK_NAMED),
        ("ext_link_anon", P_EXT_LINK_ANON),
        ("ref_named", P_REF_NAMED),
        ("substitution", P_SUBSTITUTION),
        ("footnote_ref", P_FOOTNOTE_REF),
        ("strong", P_STRONG),
        ("emphasis", P_EMPHASIS),
        ("interpreted", P_INTERPRETED),
    ]

    for rst_path, data in _iter_pairs():
        rel = str(rst_path.relative_to(REPO_ROOT))
        try:
            src = rst_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        content = _collect_all_content(data)

        for name, pat in patterns:
            for m in pat.finditer(src):
                raw = m.group(0)
                # Success: raw token appears in JSON content verbatim → no transform needed
                if raw in content:
                    hits[name] += 1
                    if len(samples[name]) < SAMPLE_LIMIT:
                        samples[name].append({
                            "verdict": "verbatim",
                            "source": rel,
                            "raw": raw,
                        })
                    continue
                # Token NOT verbatim → locate by a "contextual anchor" in the source
                # and compute the corresponding slice of JSON content.
                # Heuristic: we grab the source line, locate any stable
                # substring before the match, then try to find it in output.
                line_start = src.rfind("\n", 0, m.start()) + 1
                line_end = src.find("\n", m.end())
                if line_end < 0:
                    line_end = len(src)
                src_line = src[line_start:line_end]
                # Try to find a non-pattern anchor (word before the match
                # in the same line). Fall back to first 8 chars of the
                # inner text group.
                inner = m.group(1) if m.lastindex else raw
                anchors = []
                before = src[line_start:m.start()]
                # Split into words, take last 1-2 tokens > 3 chars
                words = re.findall(r"[^\s`*_|:\[\]<>]+", before)
                for w in reversed(words):
                    if len(w) >= 3:
                        anchors.append(w)
                        break
                # Also try inner text as a fallback anchor
                inner_text = inner.split("<")[0].strip() if "<" in inner else inner
                if len(inner_text) >= 3:
                    anchors.append(inner_text[:16])

                resolved_md = None
                for a in anchors:
                    cidx = content.find(a)
                    if cidx < 0:
                        continue
                    # take a small window around the anchor
                    cl = max(0, cidx - 10)
                    ch = min(len(content), cidx + 120)
                    resolved_md = content[cl:ch]
                    break

                misses[name] += 1
                if resolved_md is not None:
                    if len(samples[name]) < SAMPLE_LIMIT:
                        samples[name].append({
                            "verdict": "transformed",
                            "source": rel,
                            "raw": raw,
                            "md_context": resolved_md.replace("\n", "\\n"),
                        })
                else:
                    if len(source_only[name]) < SAMPLE_LIMIT:
                        source_only[name].append({
                            "source": rel,
                            "raw": raw,
                            "src_line": src_line.strip(),
                        })

    # Block-level: directives and comments
    dir_samples: dict[str, list[dict]] = defaultdict(list)
    for rst_path, data in _iter_pairs():
        rel = str(rst_path.relative_to(REPO_ROOT))
        try:
            src = rst_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        content = _collect_all_content(data)
        for m in P_DIRECTIVE.finditer(src):
            dname = m.group(2)
            if len(dir_samples[dname]) >= 5:
                continue
            # Get the directive block (indented lines after)
            block_start = m.start()
            lines = src[block_start:].split("\n")
            header_indent = len(m.group(1))
            body = [lines[0]]
            for line in lines[1:]:
                if not line.strip():
                    body.append(line)
                    continue
                lstrip = len(line) - len(line.lstrip())
                if lstrip <= header_indent and line.strip():
                    break
                body.append(line)
            # Drop trailing empties
            while body and not body[-1].strip():
                body.pop()
            block = "\n".join(body)
            dir_samples[dname].append({
                "source": rel,
                "block": block[:400],
            })

    # Write JSON
    out = {
        "stats": {
            name: {"verbatim": hits[name], "transformed_or_dropped": misses[name]}
            for name, _ in patterns
        },
        "samples": samples,
        "source_only": source_only,
        "directive_samples": dir_samples,
    }
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # Write markdown summary
    lines = ["# Transform rules (v6) — derived from source/JSON pairs", ""]
    lines.append("Stats per inline pattern:")
    lines.append("")
    lines.append("| Pattern | Verbatim | Transformed/Dropped |")
    lines.append("|---|---:|---:|")
    for name, _ in patterns:
        lines.append(f"| {name} | {hits[name]} | {misses[name]} |")
    lines.append("")
    for name, _ in patterns:
        lines.append(f"## {name}")
        lines.append("")
        if samples.get(name):
            lines.append("### Sample transformations")
            lines.append("")
            for s in samples[name][:10]:
                lines.append(f"- **{s['verdict']}** `{s['raw']}` ({s['source']})")
                if "md_context" in s:
                    lines.append(f"  - MD context: `{s['md_context']}`")
            lines.append("")
        if source_only.get(name):
            lines.append("### Source-only (tokens not found in output, no nearby anchor)")
            lines.append("")
            for s in source_only[name][:10]:
                lines.append(f"- `{s['raw']}` ({s['source']})")
                lines.append(f"  - line: `{s['src_line']}`")
            lines.append("")
    lines.append("## Directives")
    lines.append("")
    lines.append(f"{len(dir_samples)} distinct directive names.")
    for dname, samps in sorted(dir_samples.items()):
        lines.append(f"### .. {dname}:: ({len(samps)} samples)")
        for s in samps[:2]:
            lines.append("")
            lines.append(f"*{s['source']}*")
            lines.append("")
            lines.append("```rst")
            lines.append(s["block"])
            lines.append("```")
        lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")

    print("\n=== Inline transforms (v6) ===", file=sys.stderr)
    for name, _ in patterns:
        print(f"  {name:20s} verbatim={hits[name]:6d}  transformed={misses[name]:6d}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
