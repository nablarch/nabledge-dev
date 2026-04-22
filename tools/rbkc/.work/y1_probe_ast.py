#!/usr/bin/env python3
"""Phase 21-Y / Y-1: probe docutils AST behavior on all RST files.

For each version's RST tree, run `publish_doctree` and collect:
  - parse success / warning / error counts
  - presence of Sphinx-only roles/directives as system_messages
  - rowspan (`morerows`) attributes on grid-table entries
  - substitution_reference resolution vs. definition
  - include / literalinclude / raw:: html occurrences
  - cross-reference node types (:ref: / :doc: / :file:)
  - footnote / transition / field_list / admonition (docutils built-in) node counts
  - top-level node types encountered

Sphinx-specific roles and directives are registered as generic/pass-through
so docutils does not emit ERROR system_messages that mask real problems.

Output:
  - .work/00299/phase21y/ast-probe.json (machine-readable)
  - .work/00299/phase21y/ast-probe.md   (human-readable summary)
"""

from __future__ import annotations

import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from docutils import nodes
from docutils.core import publish_doctree
from docutils.parsers.rst import Directive, directives, roles
from docutils.parsers.rst.directives import admonitions

REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCES_ROOT = REPO_ROOT / ".lw" / "nab-official"
OUT_DIR = REPO_ROOT / ".work" / "00299" / "phase21y"
VERSIONS = ["v6", "v5", "v1.4", "v1.3", "v1.2"]


def _register_sphinx_shims() -> None:
    """Register minimal shims for Sphinx roles/directives so docutils parses
    the source without emitting ERROR system_messages for unknown roles.

    These shims do not aim to behave like Sphinx — they just produce a
    recognisable node so we can measure usage and decide how the real Visitor
    will translate them.
    """

    # --- Generic roles that wrap the text in a literal-ish node ---
    def _role_noop(name, rawtext, text, lineno, inliner, options=None, content=None):
        node = nodes.inline(rawtext, text, classes=[f"role-{name}"])
        return [node], []

    for role_name in [
        "ref",
        "doc",
        "download",
        "file",
        "guilabel",
        "menuselection",
        "kbd",
        "command",
        "samp",
        "envvar",
        "abbr",
        "term",
        "numref",
        "javadoc_url",
        "strong",
    ]:
        roles.register_local_role(role_name, _role_noop)

    # Sphinx domain roles use colons (java:extdoc, java:ref, ...)
    for role_name in [
        "java:extdoc",
        "java:ref",
        "java:type",
        "java:method",
        "java:field",
        "c:func",
    ]:
        roles.register_local_role(role_name, _role_noop)

    # --- Directive shims ---
    # Sphinx-specific directives split in two groups:
    #  - literal: body is not RST (code-block, literalinclude, raw, include)
    #  - container: body is RST, we nested_parse it so probe sees inner structure
    class _LiteralDirective(Directive):
        has_content = True
        required_arguments = 0
        optional_arguments = 100
        final_argument_whitespace = True
        option_spec: dict[str, Any] = defaultdict(lambda: directives.unchanged)

        def run(self):
            text = "\n".join(self.content) if self.content else ""
            node = nodes.literal_block(text, text, classes=[f"directive-{self.name}"])
            node["directive_name"] = self.name
            return [node]

    class _ContainerDirective(Directive):
        has_content = True
        required_arguments = 0
        optional_arguments = 100
        final_argument_whitespace = True
        option_spec: dict[str, Any] = defaultdict(lambda: directives.unchanged)

        def run(self):
            node = nodes.container(classes=[f"directive-{self.name}"])
            node["directive_name"] = self.name
            if self.content:
                self.state.nested_parse(self.content, self.content_offset, node)
            return [node]

    # NOTE: `raw` and `include` are built-in docutils directives — do not shim
    # them, or substitution_definition via `.. |x| raw:: html ...` breaks.
    # `include` is instead suppressed via settings_overrides=file_insertion_enabled=False.
    literal_directives = [
        "code-block",
        "literalinclude",
        "csv-table",
    ]
    # NOTE: admonition/attention/warning/note/hint/important/tip/image/figure/
    # table/list-table/rubric/contents/topic are **built-in** docutils
    # directives — we leave them alone so probe counts real node types.
    # Only non-docutils (Sphinx or v1.x custom) container directives need
    # shimming:
    container_directives = [
        "toctree",
        "function",  # v1.x custom
        "class",  # v1.x custom (python domain in Sphinx, custom here)
        "java:method",
        "java:type",
        "java:field",
    ]
    for directive_name in literal_directives:
        directives.register_directive(directive_name, _LiteralDirective)
    for directive_name in container_directives:
        directives.register_directive(directive_name, _ContainerDirective)


def _iter_rst_files(version: str) -> list[Path]:
    version_dir = SOURCES_ROOT / version
    if not version_dir.is_dir():
        return []
    return sorted(version_dir.rglob("*.rst"))


class _Probe:
    def __init__(self) -> None:
        self.files_total = 0
        self.files_ok = 0
        self.files_warn = 0
        self.files_err = 0
        self.node_counts: Counter[str] = Counter()
        self.system_message_types: Counter[str] = Counter()
        self.morerows_seen = 0
        self.morecols_seen = 0
        self.table_count = 0
        self.grid_table_entries = 0
        self.substitution_def = 0
        # `substitution_reference` nodes are normally replaced by their target
        # content (raw / Text) by docutils' Substitutions transform before we
        # see the tree. So we count `substitution_definition` only; presence of
        # those is sufficient evidence that docutils handles |x| expansion.
        self.substitution_ref = 0
        self.include_directive = 0  # counted via container classes (directive-include)
        self.raw_directive = 0
        self.reference_classes: Counter[str] = Counter()
        self.problem_files: list[dict[str, Any]] = []

    def scan_file(self, path: Path) -> None:
        self.files_total += 1
        try:
            source = path.read_text(encoding="utf-8")
        except Exception as exc:  # pragma: no cover
            self.files_err += 1
            self.problem_files.append({"path": str(path), "kind": "read_error", "msg": str(exc)})
            return

        warning_stream = io.StringIO()
        try:
            doctree = publish_doctree(
                source,
                settings_overrides={
                    "report_level": 2,  # INFO and above
                    "halt_level": 5,  # never halt
                    "warning_stream": warning_stream,
                    "input_encoding": "utf-8",
                    "file_insertion_enabled": False,  # don't follow .. include::
                    "raw_enabled": True,
                },
            )
        except Exception as exc:
            self.files_err += 1
            self.problem_files.append(
                {"path": str(path), "kind": "parse_exception", "msg": str(exc)[:200]}
            )
            return

        has_error = False
        has_warning = False
        for sm in doctree.traverse(nodes.system_message):
            level = sm.get("level", 0)
            self.system_message_types[f"level={level}:type={sm.get('type','')}"] += 1
            if level >= 2:
                has_warning = True
            if level >= 3:
                has_error = True

        if has_error:
            self.files_err += 1
            self.problem_files.append(
                {
                    "path": str(path),
                    "kind": "parse_error",
                    "warnings": warning_stream.getvalue()[:400],
                }
            )
        elif has_warning:
            self.files_warn += 1
        else:
            self.files_ok += 1

        for node in doctree.traverse():
            name = type(node).__name__
            self.node_counts[name] += 1

            if isinstance(node, nodes.table):
                self.table_count += 1
            if isinstance(node, nodes.entry):
                if node.get("morerows"):
                    self.morerows_seen += 1
                if node.get("morecols"):
                    self.morecols_seen += 1
                self.grid_table_entries += 1
            if isinstance(node, nodes.substitution_definition):
                self.substitution_def += 1
            if isinstance(node, nodes.substitution_reference):
                self.substitution_ref += 1
            if isinstance(node, nodes.container):
                dname = node.get("directive_name") or ""
                if dname == "include" or dname == "literalinclude":
                    self.include_directive += 1
                elif dname == "raw":
                    self.raw_directive += 1
            if isinstance(node, nodes.reference):
                if node.get("refuri"):
                    self.reference_classes["refuri"] += 1
                if node.get("refname"):
                    self.reference_classes["refname"] += 1
                if node.get("anonymous"):
                    self.reference_classes["anonymous"] += 1
                if node.get("refid"):
                    self.reference_classes["refid"] += 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "files_total": self.files_total,
            "files_ok": self.files_ok,
            "files_warn": self.files_warn,
            "files_err": self.files_err,
            "node_counts": dict(self.node_counts.most_common()),
            "system_message_types": dict(self.system_message_types.most_common()),
            "tables": {
                "table_count": self.table_count,
                "entries": self.grid_table_entries,
                "morerows_seen": self.morerows_seen,
                "morecols_seen": self.morecols_seen,
            },
            "substitutions": {
                "definitions": self.substitution_def,
                "references": self.substitution_ref,
            },
            "directives_seen_via_container": {
                "include+literalinclude": self.include_directive,
                "raw": self.raw_directive,
            },
            "reference_attrs": dict(self.reference_classes),
            "problem_files": self.problem_files[:30],
            "problem_files_total": len(self.problem_files),
        }


def main() -> int:
    _register_sphinx_shims()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_results: dict[str, Any] = {}
    for version in VERSIONS:
        probe = _Probe()
        files = _iter_rst_files(version)
        for i, p in enumerate(files, 1):
            probe.scan_file(p)
            if i % 100 == 0:
                print(f"  {version}: {i}/{len(files)}", file=sys.stderr)
        all_results[version] = probe.to_dict()
        summary = all_results[version]
        print(
            f"{version}: total={summary['files_total']} "
            f"ok={summary['files_ok']} warn={summary['files_warn']} err={summary['files_err']} "
            f"morerows={summary['tables']['morerows_seen']} "
            f"subref={summary['substitutions']['references']}"
        )

    (OUT_DIR / "ast-probe.json").write_text(
        json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines: list[str] = ["# Phase 21-Y / Y-1: docutils AST probe", ""]
    lines.append("## Parse health")
    lines.append("")
    lines.append("| Version | Total | OK | Warn | Error |")
    lines.append("|---|---:|---:|---:|---:|")
    for v in VERSIONS:
        r = all_results[v]
        lines.append(
            f"| {v} | {r['files_total']} | {r['files_ok']} | {r['files_warn']} | {r['files_err']} |"
        )
    lines.append("")

    lines.append("## Table rowspan / colspan")
    lines.append("")
    lines.append("| Version | tables | entries | morerows | morecols |")
    lines.append("|---|---:|---:|---:|---:|")
    for v in VERSIONS:
        t = all_results[v]["tables"]
        lines.append(
            f"| {v} | {t['table_count']} | {t['entries']} | {t['morerows_seen']} | {t['morecols_seen']} |"
        )
    lines.append("")

    lines.append("## Substitution")
    lines.append("")
    lines.append("| Version | Definitions | References |")
    lines.append("|---|---:|---:|")
    for v in VERSIONS:
        s = all_results[v]["substitutions"]
        lines.append(f"| {v} | {s['definitions']} | {s['references']} |")
    lines.append("")

    lines.append("## System messages by (level,type)")
    lines.append("")
    for v in VERSIONS:
        sm = all_results[v]["system_message_types"]
        if not sm:
            continue
        lines.append(f"### {v}")
        lines.append("")
        lines.append("| (level,type) | count |")
        lines.append("|---|---:|")
        for k, n in list(sm.items())[:30]:
            lines.append(f"| `{k}` | {n} |")
        lines.append("")

    lines.append("## Top node types")
    lines.append("")
    for v in VERSIONS:
        nc = all_results[v]["node_counts"]
        lines.append(f"### {v}")
        lines.append("")
        lines.append("| Node | Count |")
        lines.append("|---|---:|")
        for name, n in list(nc.items())[:30]:
            lines.append(f"| `{name}` | {n} |")
        lines.append("")

    lines.append("## Problem files (first 30 per version)")
    lines.append("")
    for v in VERSIONS:
        pf = all_results[v]["problem_files"]
        total = all_results[v]["problem_files_total"]
        lines.append(f"### {v} (problem files total: {total})")
        lines.append("")
        if not pf:
            lines.append("_none_")
            lines.append("")
            continue
        for entry in pf:
            lines.append(f"- `{entry['path']}` — {entry['kind']}")
            msg = entry.get("warnings") or entry.get("msg")
            if msg:
                lines.append(f"  - `{msg.splitlines()[0] if msg else ''}`")
        lines.append("")

    (OUT_DIR / "ast-probe.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_DIR/'ast-probe.json'}")
    print(f"wrote {OUT_DIR/'ast-probe.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
