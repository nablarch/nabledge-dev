#!/usr/bin/env python3
"""X-2-e: Pilot residue analysis.

Applies a prototype pattern-based reducer to every RST source (v6 snapshot),
then checks what remains after removing:
  - RST directives (entire blocks including body)
  - inline roles (text part kept, markup stripped)
  - double-backtick literals (content kept)
  - external links (text kept)
  - substitutions (known expansions applied; others kept as-is)
  - headings (text kept, underline dropped)
  - comments, blank lines, trailing whitespace
  - simple-table / grid-table separators
  - bullet / enum list markers
  - field list markers

The reduced source is then searched for tokens against the corresponding
JSON content. Whatever source tokens still fail to appear in JSON is the
"residue" we need to either (a) handle in the tokenizer or (b) add to
the allowed-syntax list.

Output:
  .work/00299/phase21x/residue-triage.md   (human-readable)
  .work/00299/phase21x/residue-triage.json (machine-readable)

This is a prototype, not the final implementation — the goal is to
dimension the remaining work, not to pass verify.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools/rbkc"))

VERSION = "6"
OUT_MD = Path(__file__).parent / "residue-triage.md"
OUT_JSON = Path(__file__).parent / "residue-triage.json"
SAMPLE_LIMIT = 50
SNAPSHOT_PATH = REPO_ROOT / ".state" / VERSION / "snapshot.json"
KNOWLEDGE_DIR = REPO_ROOT / f".claude/skills/nabledge-{VERSION}/knowledge"


# ---------- pattern set (derived from scan_inline / scan_block) ----------

def normalise_rst(src: str) -> str:
    """Return a reduced form of RST source that drops markup, keeps text.

    This is a *pilot*, not the production tokenizer. It uses sequential
    regex substitutions which is known to be fragile; the point is to
    measure how much actual text remains.
    """
    lines = src.split("\n")

    # Step 1: drop directive blocks (directive line + indented body).
    out_lines: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(\s*)\.\.\s+([A-Za-z][A-Za-z0-9_:-]*)\s*::\s*(.*)$", line)
        if m:
            indent = len(m.group(1))
            dname = m.group(2)
            # Skip header line
            i += 1
            # Skip indented body
            while i < len(lines):
                bl = lines[i]
                if not bl.strip():
                    i += 1
                    continue
                bindent = len(bl) - len(bl.lstrip())
                if bindent > indent:
                    i += 1
                else:
                    break
            # For certain directives we want to KEEP the body text because
            # the converter inlines it into content. These are admonition-
            # family directives whose body is regular paragraph text.
            # But for simplicity in the pilot we drop everything; we'll
            # handle this properly in the real tokenizer (X-4).
            continue
        # Drop comment lines (. .   non-directive)
        if re.match(r"^\s*\.\.\s+(?![A-Za-z][A-Za-z0-9_:-]*::)", line) or re.match(r"^\s*\.\.\s*$", line):
            # Skip continuation lines that are indented
            i += 1
            while i < len(lines):
                bl = lines[i]
                if not bl.strip():
                    i += 1
                    continue
                bindent = len(bl) - len(bl.lstrip())
                if bindent > 0:
                    i += 1
                else:
                    break
            continue
        out_lines.append(line)
        i += 1

    text = "\n".join(out_lines)

    # Step 2: drop section underlines (line with only underline punctuation)
    text = re.sub(r"^([=\-`~'\"*^+#<>:._])\1{2,}\s*$", "", text, flags=re.MULTILINE)

    # Step 3: drop table separators
    text = re.sub(r"^\s*=+(?: +=+)+\s*$", "", text, flags=re.MULTILINE)  # simple
    text = re.sub(r"^\s*\+-+(?:\+-+)+\+\s*$", "", text, flags=re.MULTILINE)  # grid sep
    text = re.sub(r"^\s*\+=+(?:\+=+)+\+\s*$", "", text, flags=re.MULTILINE)  # grid head

    # Step 4: drop bullet/enumerated list markers at line start
    text = re.sub(r"^(\s*)[*+\-]\s+", r"\1", text, flags=re.MULTILINE)
    text = re.sub(r"^(\s*)\(?[0-9a-zA-Z]+[\.\)]\s+", r"\1", text, flags=re.MULTILINE)

    # Step 5: drop field list markers but keep value text (":maxdepth: 2" → " 2")
    text = re.sub(r"^(\s*):[A-Za-z][A-Za-z0-9_ -]*:\s*", r"\1", text, flags=re.MULTILINE)

    # Step 6: inline transforms
    # Role with target → keep text part only
    text = re.sub(r":[A-Za-z][A-Za-z0-9_.:+-]*:`([^`<>]*)<[^`<>]+>`", r"\1", text)
    # Role simple → keep text
    text = re.sub(r":[A-Za-z][A-Za-z0-9_.:+-]*:`([^`]+)`", r"\1", text)
    # Ext link named `text <url>`_ → "text url"
    text = re.sub(r"`([^`<]+?)\s*<([^`<>]+)>`_(?!_)", r"\1 \2", text)
    text = re.sub(r"`([^`<]+?)\s*<([^`<>]+)>`__", r"\1 \2", text)
    # Named ref `text`_ → keep text
    text = re.sub(r"(?<![`:])`([^`<>\n]+?)`_(?!_)", r"\1", text)
    # Double backtick → keep inner
    text = re.sub(r"``([^`]+?)``", r"\1", text)
    # Interpreted text → keep inner (fallback, after role patterns)
    text = re.sub(r"(?<![`:_\w])`([^`<>\n]+?)`(?![_`])", r"\1", text)
    # Strong → keep inner
    text = re.sub(r"(?<![*])\*\*([^*\n]+?)\*\*(?![*])", r"\1", text)
    # Emphasis → keep inner
    text = re.sub(r"(?<![*\w])\*([^*\s][^*\n]*?)\*(?![*\w])", r"\1", text)
    # Substitutions → leave |name| as-is (would need substitution table)
    # Footnote ref [x]_ → leave as-is

    # Step 7: collapse whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def normalise_md(md: str) -> str:
    """Light normalization of JSON content for comparison."""
    # Strip MD fences
    md = re.sub(r"^```.*$", "", md, flags=re.MULTILINE)
    # Drop leading list markers
    md = re.sub(r"^(\s*)[*+\-]\s+", r"\1", md, flags=re.MULTILINE)
    md = re.sub(r"^(\s*)\d+\.\s+", r"\1", md, flags=re.MULTILINE)
    # MD link [text](url) → "text url"
    md = re.sub(r"\[([^\]\n]+?)\]\(([^)\n]+?)\)", r"\1 \2", md)
    # Inline code `x` → x
    md = re.sub(r"`([^`\n]+?)`", r"\1", md)
    # Strong / emphasis
    md = re.sub(r"\*\*([^*\n]+?)\*\*", r"\1", md)
    md = re.sub(r"(?<![*\w])\*([^*\s][^*\n]*?)\*(?![*\w])", r"\1", md)
    # Headings — drop leading #
    md = re.sub(r"^#{1,6}\s+", "", md, flags=re.MULTILINE)
    # Blockquote markers
    md = re.sub(r"^>\s?", "", md, flags=re.MULTILINE)
    # Table pipes
    md = re.sub(r"\|", " ", md)
    md = re.sub(r"[ \t]+", " ", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def _load_snapshot() -> dict:
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


def _iter_pairs():
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


def _collect_content(data: dict) -> str:
    parts = [data.get("title", ""), data.get("content", "")]
    for sec in data.get("sections", []):
        parts.append(sec.get("title", ""))
        parts.append(sec.get("content", ""))
    return "\n".join(parts)


def main() -> int:
    # Sample a few files, compute reduced source / reduced MD, dump which
    # source lines are still not contained in the reduced MD.
    per_file_stats = []
    aggregate = Counter()
    residue_lines: dict[str, list[str]] = defaultdict(list)

    for rst_path, data in _iter_pairs():
        rel = str(rst_path.relative_to(REPO_ROOT))
        src = rst_path.read_text(encoding="utf-8", errors="replace")
        if data.get("no_knowledge_content"):
            continue
        red_src = normalise_rst(src)
        red_md = normalise_md(_collect_content(data))

        # tokenise by lines (non-empty)
        src_lines = [l.strip() for l in red_src.split("\n") if l.strip()]
        missing = []
        for line in src_lines:
            # ignore super-short lines
            if len(line) < 8:
                continue
            # drop spaces for comparison (converter may collapse differently)
            key = re.sub(r"\s+", " ", line).strip()
            if key in red_md:
                aggregate["match"] += 1
            elif re.sub(r"\s+", "", key) in re.sub(r"\s+", "", red_md):
                aggregate["space_only_diff"] += 1
            else:
                aggregate["miss"] += 1
                missing.append(key)
                if len(residue_lines[rel]) < 50:
                    residue_lines[rel].append(key)
        per_file_stats.append({
            "path": rel,
            "src_lines": len(src_lines),
            "missing": len(missing),
        })

    # Aggregate miss classification
    all_miss_samples = []
    for rel, misses in residue_lines.items():
        for m in misses[:3]:
            all_miss_samples.append((rel, m))
            if len(all_miss_samples) >= SAMPLE_LIMIT:
                break
        if len(all_miss_samples) >= SAMPLE_LIMIT:
            break

    # File-level stats
    per_file_stats.sort(key=lambda x: -x["missing"])
    top_missing = per_file_stats[:30]

    report = {
        "aggregate": dict(aggregate),
        "top_missing_files": top_missing,
        "residue_samples": [
            {"path": p, "line": m} for p, m in all_miss_samples
        ],
    }
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# Residue Triage (v6 pilot)", ""]
    md.append("## Aggregate")
    md.append("")
    md.append(f"- match (exact): {aggregate['match']}")
    md.append(f"- match (space-normalised): {aggregate['space_only_diff']}")
    md.append(f"- miss: {aggregate['miss']}")
    total = sum(aggregate.values())
    if total:
        md.append(f"- coverage (match + space): {(aggregate['match'] + aggregate['space_only_diff'])*100/total:.1f}%")
    md.append("")
    md.append("## Top files by unmatched-line count (after pilot reduction)")
    md.append("")
    md.append("| File | Source lines | Missing |")
    md.append("|---|---:|---:|")
    for f in top_missing:
        md.append(f"| {f['path']} | {f['src_lines']} | {f['missing']} |")
    md.append("")
    md.append("## Residue samples (up to 50)")
    md.append("")
    for p, m in all_miss_samples:
        md.append(f"- **{p}**")
        md.append(f"    - `{m[:180]}`")

    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")

    print("\n=== PILOT AGGREGATE ===", file=sys.stderr)
    for k, v in aggregate.items():
        print(f"  {k:20s} {v}", file=sys.stderr)
    if total:
        print(f"  coverage: {(aggregate['match'] + aggregate['space_only_diff'])*100/total:.1f}%", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
