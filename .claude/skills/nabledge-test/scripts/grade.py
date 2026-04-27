#!/usr/bin/env python3
"""Grade a single nabledge-test scenario workspace.

Reads response.md and output/ (for CA scenarios) from a scenario workspace,
applies the detection rules defined in scenarios.json, and writes grading.json.

Design principles (per .claude/rules/rbkc.md quality standard):
- Strict: never relax a rule to hide a miss. For CA "Nablarch Framework Usage
  includes 'X'", require X to appear as a ### or #### heading within the NU
  section — NOT anywhere in the NU body. Text-only fallback is forbidden.
- Deterministic: same inputs always produce same grading.json.
- Spec-anchored: each rule documents the SKILL.md detection logic it implements.

Usage:
    python grade.py --workspace <workspace_dir> --scenario-id <id> \
                    --scenarios <scenarios.json>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


# Section heading regexes. Each applies to text prefixed with "\n" to make the
# same pattern work whether the section is at the start of the text or not.
# stop_pattern is "next heading at the same-or-shallower level", i.e. "\n## X"
# for a ## section, "\n#{1,3} X" for a ### section, etc.

def _extract_section(
    text: str,
    heading_patterns: list[str],
    stop_pattern: str = r"\n#{1,6}[^#]",
) -> str:
    """Extract the body of a section matched by any of heading_patterns.

    Both heading_patterns and stop_pattern expect the text to begin with "\n".
    We prepend one unconditionally so the leading heading (first line of file)
    still matches.

    Returns "" if no heading matched.
    """
    t = "\n" + text
    for hp in heading_patterns:
        m = re.search(hp, t)
        if m:
            start = m.end()
            stop_m = re.search(stop_pattern, t[start:])
            return t[start : start + stop_m.start()] if stop_m else t[start:]
    return ""


def _mermaid_blocks(text: str, kind: str) -> str:
    """Concatenate all ```mermaid fenced blocks whose body contains `kind`
    (e.g. "classDiagram" or "sequenceDiagram").
    """
    blocks = re.findall(r"```mermaid\s*\n(.*?)```", text, re.DOTALL)
    return "\n".join(b for b in blocks if kind in b)


def _headings(nu_text: str) -> list[str]:
    """Return all ### / #### heading titles in nu_text."""
    return re.findall(r"^#{3,4}\s+(.+?)\s*$", nu_text, re.MULTILINE)


def _load_ca_text(workspace: Path, scenario_id: str, response: str) -> str:
    """For CA scenarios, prefer concatenated output/*.md over response.md."""
    out_dir = workspace / scenario_id / "output"
    if out_dir.is_dir():
        pieces = []
        for f in sorted(out_dir.glob("*.md")):
            pieces.append(f.read_text())
        if pieces:
            return "\n".join(pieces)
    return response


def _evidence(found: bool, where: str) -> str:
    return f"Found in {where}" if found else f"Not found in {where}"


def grade_qa(scenario: dict, response: str) -> dict:
    """QA grading: check each expectation item against response body.

    An expectation item is either:
    - a string → must appear literally (case-sensitive substring)
    - a list of strings → OR: any one must appear
    """
    items: list[dict] = []
    for aspect, bucket in scenario["expectations"].items():
        for entry in bucket:
            if isinstance(entry, list):
                detected = any(k in response for k in entry)
                text = "Response includes one of: " + ", ".join(repr(k) for k in entry)
                where = "response (OR match)"
            else:
                detected = entry in response
                text = f"Response includes {entry!r}"
                where = "response"
            items.append(
                {"text": text, "detected": detected, "evidence": _evidence(detected, where)}
            )
    return _finalize(scenario["id"], items)


def grade_ca(scenario: dict, response: str, workspace: Path) -> dict:
    """CA grading: detection rules are section-qualified.

    Rules (strict; spec-anchored to SKILL.md Step 6):
    - Overview includes 'X'         → X in `## Overview` section text
    - Class diagram includes class 'X'         → X in any ```mermaid classDiagram``` fence
    - Class diagram includes relationship 'X'  → X in any ```mermaid classDiagram``` fence
    - Component Summary includes 'X'           → X in `### Component Summary` section text
    - Processing Flow includes 'X'             → X in `### Processing Flow` section text
    - Sequence diagram includes object/message → X in any ```mermaid sequenceDiagram``` fence
    - Nablarch Framework Usage includes 'X'    → X appears in a ### or #### heading
                                                  within the `## Nablarch Framework Usage` section
    - Output includes 'X'                      → X anywhere in output text or response
    """
    items: list[dict] = []
    exp = scenario["expectations"]
    text = _load_ca_text(workspace, scenario["id"], response)

    overview = _extract_section(text, [r"\n##\s+Overview\s*\n", r"\n##\s+概要\s*\n"])
    for kw in exp.get("overview", []):
        d = kw in overview
        items.append({"text": f"Overview includes {kw!r}", "detected": d,
                      "evidence": _evidence(d, "## Overview section")})

    cd = _mermaid_blocks(text, "classDiagram")
    for cls in exp.get("class_diagram", {}).get("classes", []):
        d = cls in cd
        items.append({"text": f"Class diagram includes class {cls!r}", "detected": d,
                      "evidence": _evidence(d, "```mermaid classDiagram```")})
    for rel in exp.get("class_diagram", {}).get("relationships", []):
        d = rel in cd
        items.append({"text": f"Class diagram includes relationship {rel!r}", "detected": d,
                      "evidence": _evidence(d, "```mermaid classDiagram```")})

    cs = _extract_section(text, [r"\n###\s+Component Summary\s*\n"])
    for kw in exp.get("component_summary", []):
        d = kw in cs
        items.append({"text": f"Component Summary includes {kw!r}", "detected": d,
                      "evidence": _evidence(d, "### Component Summary section")})

    pf = _extract_section(text, [r"\n###\s+Processing Flow\s*\n", r"\n###\s+処理フロー\s*\n"])
    for kw in exp.get("processing_flow", []):
        d = kw in pf
        items.append({"text": f"Processing Flow includes {kw!r}", "detected": d,
                      "evidence": _evidence(d, "### Processing Flow section")})

    sd = _mermaid_blocks(text, "sequenceDiagram")
    for obj in exp.get("sequence_diagram", {}).get("objects", []):
        d = obj in sd
        items.append({"text": f"Sequence diagram includes object {obj!r}", "detected": d,
                      "evidence": _evidence(d, "```mermaid sequenceDiagram```")})
    for msg in exp.get("sequence_diagram", {}).get("messages", []):
        d = msg in sd
        items.append({"text": f"Sequence diagram includes message {msg!r}", "detected": d,
                      "evidence": _evidence(d, "```mermaid sequenceDiagram```")})

    # Nablarch Framework Usage — STRICT: the keyword must appear in a ###/####
    # heading within the ## Nablarch Framework Usage section, NOT just anywhere
    # in the body. "Heading" is interpreted as substring of the heading text
    # (so "### SessionUtil (セッションストア)" counts for "SessionUtil").
    nu = _extract_section(
        text,
        [r"\n##\s+Nablarch Framework Usage\s*\n"],
        stop_pattern=r"\n##[^#]",
    )
    nu_headings = _headings(nu)
    for kw in exp.get("nablarch_usage", []):
        d = any(kw in h for h in nu_headings)
        items.append({
            "text": f"Nablarch Framework Usage includes {kw!r}",
            "detected": d,
            "evidence": (
                f"Matched heading in ## Nablarch Framework Usage section"
                if d
                else f"Not found as heading (headings: {nu_headings})"
            ),
        })

    full = text + "\n" + response
    for kw in exp.get("output", []):
        d = kw in full
        items.append({"text": f"Output includes {kw!r}", "detected": d,
                      "evidence": _evidence(d, "output files or response")})

    return _finalize(scenario["id"], items)


def _finalize(scenario_id: str, items: list[dict]) -> dict:
    detected = sum(1 for i in items if i["detected"])
    total = len(items)
    return {
        "scenario_id": scenario_id,
        "detection_items": items,
        "summary": {
            "detected": detected,
            "not_detected": total - detected,
            "total": total,
            "detection_rate": round(detected / total, 4) if total else 0.0,
        },
    }


def grade_scenario(scenario: dict, workspace: Path) -> dict:
    sc_dir = workspace / scenario["id"]
    response = (sc_dir / "response.md").read_text()
    if scenario.get("type") == "code-analysis":
        return grade_ca(scenario, response, workspace)
    return grade_qa(scenario, response)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", required=True, type=Path,
                   help="workspace dir (e.g. .tmp/nabledge-test/run-YYYYMMDD-HHMMSS/)")
    p.add_argument("--scenario-id", required=True,
                   help="scenario id (e.g. qa-001)")
    p.add_argument("--scenarios", required=True, type=Path,
                   help="scenarios.json path")
    p.add_argument("--trial", type=int, default=None,
                   help="trial number for benchmark scenarios (writes to trials/N/)")
    args = p.parse_args()

    data = json.loads(args.scenarios.read_text())
    scenario = next((s for s in data["scenarios"] if s["id"] == args.scenario_id), None)
    if scenario is None:
        print(f"scenario {args.scenario_id!r} not found in {args.scenarios}", file=sys.stderr)
        return 1

    # Trial-specific workspace: override sc_dir by pointing to trials/N/
    if args.trial is not None:
        # Create a view where response.md sits in trials/N/ and output/ in trials/N/output/
        class TrialWorkspace:
            def __init__(self, base, sid, trial):
                self._trial = base / sid / "trials" / str(trial)
                self._base = base
                self._sid = sid
            def __truediv__(self, name):
                if name == args.scenario_id:
                    return self._trial.parent.parent  # fake: grade_ca does workspace/sid/output
                return self._base / name
        # Simpler: just rebase response.md lookup. Use a shim.
        trial_dir = args.workspace / args.scenario_id / "trials" / str(args.trial)
        response = (trial_dir / "response.md").read_text()
        if scenario.get("type") == "code-analysis":
            # rewrite grade_ca to look at trial_dir
            out_dir = trial_dir / "output"
            if out_dir.is_dir():
                pieces = [f.read_text() for f in sorted(out_dir.glob("*.md"))]
                ca_text = "\n".join(pieces) if pieces else response
            else:
                ca_text = response
            # call internal with pre-loaded text by duck-typing: use grade_ca via fake workspace
            fake_workspace = args.workspace
            # Temporarily copy response so grade_ca finds it — but we want to avoid filesystem mutation.
            # Instead inline-adapt:
            grading = _grade_ca_with_text(scenario, ca_text, response)
        else:
            grading = grade_qa(scenario, response)
        out_path = trial_dir / "grading.json"
    else:
        grading = grade_scenario(scenario, args.workspace)
        out_path = args.workspace / args.scenario_id / "grading.json"

    out_path.write_text(json.dumps(grading, ensure_ascii=False, indent=2) + "\n")
    s = grading["summary"]
    print(f"{args.scenario_id}"
          + (f" trial {args.trial}" if args.trial is not None else "")
          + f": {s['detected']}/{s['total']} ({s['detection_rate'] * 100:.1f}%) → {out_path}")
    return 0


def _grade_ca_with_text(scenario: dict, ca_text: str, response: str) -> dict:
    """Trial variant of grade_ca that takes pre-loaded ca_text (avoids filesystem lookup)."""
    items: list[dict] = []
    exp = scenario["expectations"]

    overview = _extract_section(ca_text, [r"\n##\s+Overview\s*\n", r"\n##\s+概要\s*\n"])
    for kw in exp.get("overview", []):
        d = kw in overview
        items.append({"text": f"Overview includes {kw!r}", "detected": d,
                      "evidence": _evidence(d, "## Overview section")})

    cd = _mermaid_blocks(ca_text, "classDiagram")
    for cls in exp.get("class_diagram", {}).get("classes", []):
        d = cls in cd
        items.append({"text": f"Class diagram includes class {cls!r}", "detected": d,
                      "evidence": _evidence(d, "```mermaid classDiagram```")})
    for rel in exp.get("class_diagram", {}).get("relationships", []):
        d = rel in cd
        items.append({"text": f"Class diagram includes relationship {rel!r}", "detected": d,
                      "evidence": _evidence(d, "```mermaid classDiagram```")})

    cs = _extract_section(ca_text, [r"\n###\s+Component Summary\s*\n"])
    for kw in exp.get("component_summary", []):
        d = kw in cs
        items.append({"text": f"Component Summary includes {kw!r}", "detected": d,
                      "evidence": _evidence(d, "### Component Summary section")})

    pf = _extract_section(ca_text, [r"\n###\s+Processing Flow\s*\n", r"\n###\s+処理フロー\s*\n"])
    for kw in exp.get("processing_flow", []):
        d = kw in pf
        items.append({"text": f"Processing Flow includes {kw!r}", "detected": d,
                      "evidence": _evidence(d, "### Processing Flow section")})

    sd = _mermaid_blocks(ca_text, "sequenceDiagram")
    for obj in exp.get("sequence_diagram", {}).get("objects", []):
        d = obj in sd
        items.append({"text": f"Sequence diagram includes object {obj!r}", "detected": d,
                      "evidence": _evidence(d, "```mermaid sequenceDiagram```")})
    for msg in exp.get("sequence_diagram", {}).get("messages", []):
        d = msg in sd
        items.append({"text": f"Sequence diagram includes message {msg!r}", "detected": d,
                      "evidence": _evidence(d, "```mermaid sequenceDiagram```")})

    nu = _extract_section(ca_text,
                          [r"\n##\s+Nablarch Framework Usage\s*\n"],
                          stop_pattern=r"\n##[^#]")
    nu_headings = _headings(nu)
    for kw in exp.get("nablarch_usage", []):
        d = any(kw in h for h in nu_headings)
        items.append({
            "text": f"Nablarch Framework Usage includes {kw!r}",
            "detected": d,
            "evidence": (
                f"Matched heading in ## Nablarch Framework Usage section"
                if d
                else f"Not found as heading (headings: {nu_headings})"
            ),
        })

    full = ca_text + "\n" + response
    for kw in exp.get("output", []):
        d = kw in full
        items.append({"text": f"Output includes {kw!r}", "detected": d,
                      "evidence": _evidence(d, "output files or response")})

    return _finalize(scenario["id"], items)


if __name__ == "__main__":
    sys.exit(main())
