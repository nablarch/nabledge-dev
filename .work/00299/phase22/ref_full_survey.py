"""Survey every :ref: usage against every .. _label: definition across all versions.

For each version (6, 5, 1.4, 1.3, 1.2):
1. Collect all :ref: uses (file, line, label, explicit-text form or bare)
2. Collect all labels defined in corpus (full iter_rst_paths)
3. Collect labels defined in RBKC-input set (classify_rst_and_md filtered)
4. For each :ref:, classify:
   A. label in RBKC set → resolvable
   B. label outside RBKC set but in corpus → input-scope dangling
   C. label nowhere in corpus → true dangling (Sphinx-parity display-text)

Also:
- Collect labels from create-side scanner (scripts.common.labels.build_label_map over ALL rst) and diff against independent regex scanner.

Output: .work/00299/phase22/ref-full-survey.json + .md
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "/home/tie303177/work/nabledge/work2/tools/rbkc")

from scripts.common.file_id import (  # noqa: E402
    classify_rst_and_md,
    iter_rst_paths,
    load_mappings,
)


ROOT = Path("/home/tie303177/work/nabledge/work2")
OUT_JSON = Path("/home/tie303177/work/nabledge/work2/.work/00299/phase22/ref-full-survey.json")
OUT_MD = Path("/home/tie303177/work/nabledge/work2/.work/00299/phase22/ref-full-survey.md")


REF_RE = re.compile(r":ref:`([^<`]+?)(?:\s*<([^>]+)>)?\s*`")
LABEL_DEF_RE = re.compile(r"^\s*\.\.\s+_([A-Za-z0-9_.:\-]+):\s*$", re.MULTILINE)


class _RstSrc:
    __slots__ = ("path", "format")

    def __init__(self, path):
        self.path = path
        self.format = "rst"


def _collect_refs(paths: list[Path]) -> list[dict]:
    refs = []
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in REF_RE.finditer(line):
                label = (m.group(2) or m.group(1)).strip()
                display = m.group(1).strip() if m.group(2) else ""
                refs.append({
                    "file": str(p),
                    "line": lineno,
                    "label": label,
                    "display": display,
                })
    return refs


def _collect_labels(paths: list[Path]) -> dict[str, str]:
    """{label: defining_file}"""
    labels: dict[str, str] = {}
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in LABEL_DEF_RE.finditer(text):
            lbl = m.group(1).strip()
            labels.setdefault(lbl, str(p))
    return labels


def _survey_version(version: str) -> dict:
    all_rst = iter_rst_paths(version, ROOT)
    mappings = load_mappings(version, ROOT)
    srcs = [_RstSrc(p) for p in all_rst]
    classified = classify_rst_and_md(srcs, version, ROOT, mappings=mappings)
    rbkc_paths = {Path(fc.source_path) for fc in classified}

    corpus_refs = _collect_refs(all_rst)
    rbkc_refs = [r for r in corpus_refs if Path(r["file"]) in rbkc_paths]
    corpus_labels = _collect_labels(all_rst)
    rbkc_labels = _collect_labels(list(rbkc_paths))

    # Classify refs that originate from RBKC-input files.
    classes = Counter()
    examples_by_class: dict[str, list] = defaultdict(list)
    for r in rbkc_refs:
        lbl = r["label"]
        if lbl in rbkc_labels:
            k = "A_resolvable"
        elif lbl in corpus_labels:
            k = "B_outside_rbkc"
        else:
            k = "C_true_dangling"
        classes[k] += 1
        if len(examples_by_class[k]) < 5:
            examples_by_class[k].append({
                "label": lbl, "file": Path(r["file"]).name, "line": r["line"], "display": r["display"]
            })

    # Also: labels defined OUTSIDE rbkc that are REFERENCED from rbkc — these
    # are the ones that would become "false positive QL1 FAIL" under the
    # current buggy verify.
    outside_refs = [r for r in rbkc_refs if r["label"] not in rbkc_labels and r["label"] in corpus_labels]

    return {
        "version": version,
        "corpus_rst_files": len(all_rst),
        "rbkc_rst_files": len(rbkc_paths),
        "corpus_refs": len(corpus_refs),
        "rbkc_refs": len(rbkc_refs),
        "corpus_labels": len(corpus_labels),
        "rbkc_labels": len(rbkc_labels),
        "class_counts": dict(classes),
        "class_examples": {k: examples_by_class[k] for k in examples_by_class},
        "outside_refs_sample": outside_refs[:20],
    }


def main() -> None:
    versions = ["6", "5", "1.4", "1.3", "1.2"]
    out = {"versions": {}}
    for v in versions:
        print(f"== v{v} ==")
        try:
            out["versions"][v] = _survey_version(v)
        except Exception as e:
            out["versions"][v] = {"error": repr(e)}
            continue
        print(json.dumps(out["versions"][v]["class_counts"], ensure_ascii=False, indent=2))
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # Markdown summary
    lines = ["# RST :ref: / label full survey", ""]
    for v, data in out["versions"].items():
        lines.append(f"## v{v}")
        if "error" in data:
            lines.append(f"ERROR: {data['error']}")
            continue
        lines.append(f"- corpus rst files: {data['corpus_rst_files']}")
        lines.append(f"- RBKC-input rst files: {data['rbkc_rst_files']}")
        lines.append(f"- corpus refs: {data['corpus_refs']} (labels: {data['corpus_labels']})")
        lines.append(f"- RBKC refs: {data['rbkc_refs']} (labels: {data['rbkc_labels']})")
        lines.append(f"- class counts (RBKC refs):")
        for k, n in data["class_counts"].items():
            lines.append(f"  - {k}: {n}")
        lines.append(f"- examples:")
        for k, exs in data["class_examples"].items():
            lines.append(f"  - {k}:")
            for ex in exs:
                lines.append(f"    - `{ex['label']}` @ {ex['file']}:{ex['line']}")
        lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_JSON} and {OUT_MD}")


if __name__ == "__main__":
    main()
