#!/usr/bin/env python3
"""Enumerate all field-list options used in figure/image/list-table directives.

For each occurrence of `.. figure::`, `.. image::`, `.. list-table::`,
collect the `:name:` field list options that follow and their values.
Also check v6 JSON snapshot: does the value appear in JSON content?
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
OUT = Path(__file__).parent / "figure-image-opts.json"

TARGET_DIRECTIVES = ["figure", "image", "list-table", "table", "csv-table", "code-block", "literalinclude", "include"]

P_DIRECTIVE = re.compile(r"^(\s*)\.\.\s+([A-Za-z][A-Za-z0-9_:-]*)\s*::\s*(.*)$")
P_FIELD = re.compile(r"^(\s*):([^:\n]+):\s*(.*)$")


def _extract_directive_options(src: str, rel: str, sink: dict) -> None:
    lines = src.split("\n")
    i = 0
    while i < len(lines):
        m = P_DIRECTIVE.match(lines[i])
        if not m:
            i += 1
            continue
        dname = m.group(2)
        if dname not in TARGET_DIRECTIVES:
            i += 1
            continue
        head_indent = len(m.group(1))
        arg = m.group(3).strip()
        opts = {}
        caption_lines = []
        body_lines = []
        i += 1
        # Collect indented body
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                if not body_lines:  # still in options area separator
                    continue
                body_lines.append(line)
                continue
            lstrip = len(line) - len(line.lstrip())
            if lstrip <= head_indent:
                break
            # field list line?
            mf = P_FIELD.match(line)
            if mf and not body_lines:
                opts[mf.group(2).strip()] = mf.group(3).strip()
            else:
                # For figure, non-field lines after options are caption
                body_lines.append(line)
            i += 1
        sink[dname]["count"] += 1
        sink[dname]["arg_samples"].append((rel, arg[:80]))
        for k, v in opts.items():
            sink[dname]["options"][k] += 1
            if len(sink[dname]["option_samples"][k]) < 3:
                sink[dname]["option_samples"][k].append(
                    {"path": rel, "value": v[:80], "arg": arg[:40]}
                )
        # For figure, also record caption presence
        caption = "\n".join(l for l in body_lines if l.strip())
        if caption.strip():
            sink[dname]["caption_samples"].append({
                "path": rel,
                "arg": arg[:40],
                "caption_head": caption.strip()[:120],
            })


def _sink_for_directives() -> dict:
    return {
        d: {
            "count": 0,
            "arg_samples": [],
            "options": Counter(),
            "option_samples": defaultdict(list),
            "caption_samples": [],
        }
        for d in TARGET_DIRECTIVES
    }


def scan_version(version: str) -> dict:
    sources = scan_sources(version, REPO_ROOT)
    rst = [s for s in sources if s.format == "rst"]
    sink = _sink_for_directives()
    for sf in rst:
        rel = str(sf.path.relative_to(REPO_ROOT))
        try:
            text = sf.path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        _extract_directive_options(text, rel, sink)
    return sink


def check_option_in_json(sink: dict) -> dict:
    """For v6, check whether each option value appears in JSON content."""
    SNAPSHOT = REPO_ROOT / ".state/6/snapshot.json"
    KNOWLEDGE_DIR = REPO_ROOT / ".claude/skills/nabledge-6/knowledge"
    if not SNAPSHOT.exists():
        return {}
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    src_to_out = {k: v["output_path"] for k, v in snap["files"].items() if v.get("output_path")}
    # Map path → JSON content
    path_to_content: dict[str, str] = {}

    def _get_content(rel_path: str) -> str:
        if rel_path in path_to_content:
            return path_to_content[rel_path]
        out_rel = src_to_out.get(rel_path)
        if not out_rel:
            path_to_content[rel_path] = ""
            return ""
        p = KNOWLEDGE_DIR / out_rel
        if not p.exists():
            path_to_content[rel_path] = ""
            return ""
        data = json.loads(p.read_text(encoding="utf-8"))
        parts = [data.get("title", ""), data.get("content", "")]
        for sec in data.get("sections", []):
            parts.append(sec.get("title", ""))
            parts.append(sec.get("content", ""))
        text = "\n".join(parts)
        path_to_content[rel_path] = text
        return text

    result: dict = defaultdict(lambda: defaultdict(lambda: {"in_json": 0, "not_in_json": 0, "samples_in": [], "samples_not": []}))
    for d, info in sink.items():
        for opt, samples in info["option_samples"].items():
            for s in samples:
                content = _get_content(s["path"])
                v = s["value"]
                if not v or v.isdigit() or v in ("100%", "50%"):
                    continue
                if v and v in content:
                    result[d][opt]["in_json"] += 1
                    if len(result[d][opt]["samples_in"]) < 2:
                        result[d][opt]["samples_in"].append(s)
                else:
                    result[d][opt]["not_in_json"] += 1
                    if len(result[d][opt]["samples_not"]) < 2:
                        result[d][opt]["samples_not"].append(s)
    # caption for figure
    for d, info in sink.items():
        for c in info["caption_samples"][:100]:
            content = _get_content(c["path"])
            head = c["caption_head"]
            if head and head[:40] in content:
                result[d]["_caption"]["in_json"] += 1
            else:
                result[d]["_caption"]["not_in_json"] += 1
    return result


def main() -> int:
    report: dict = {"versions": {}, "v6_json_check": {}}
    for v in VERSIONS:
        sink = scan_version(v)
        report["versions"][v] = {
            d: {
                "count": info["count"],
                "options": dict(info["options"].most_common(30)),
                "option_samples": {k: v for k, v in info["option_samples"].items()},
                "caption_count": len(info["caption_samples"]),
                "caption_samples": info["caption_samples"][:3],
            }
            for d, info in sink.items()
        }
        if v == "6":
            report["v6_json_check"] = {
                d: {opt: dict(v) for opt, v in opts.items()}
                for d, opts in check_option_in_json(sink).items()
            }

    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=list), encoding="utf-8")
    print(f"Wrote {OUT}")

    # Summary for humans
    print("\n=== Directive options summary (v6) ===", file=sys.stderr)
    for d, info in report["versions"]["6"].items():
        print(f"\n{d} (count={info['count']}):", file=sys.stderr)
        for opt, cnt in info["options"].items():
            j = report["v6_json_check"].get(d, {}).get(opt, {})
            in_j = j.get("in_json", 0)
            not_j = j.get("not_in_json", 0)
            print(f"    :{opt}: ={cnt}  JSON[in={in_j} out={not_j}]", file=sys.stderr)
        if info["caption_count"]:
            jcap = report["v6_json_check"].get(d, {}).get("_caption", {})
            print(f"    captions: {info['caption_count']}  JSON[in={jcap.get('in_json',0)} out={jcap.get('not_in_json',0)}]", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
