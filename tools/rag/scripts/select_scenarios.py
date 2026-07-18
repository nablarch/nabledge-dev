#!/usr/bin/env python3
"""Select v3-eligible benchmark scenarios.

A scenario is v3-eligible if ALL pages it references (must + acceptable sections)
have NO section whose embedded text exceeds 2048 characters.

Embedded text = "<page_title>\\n<section_title>\\n<section_content>" (same as index.py).

Output: tools/rag/v3-eligible-scenarios.json
"""

import argparse
import json
import pathlib
import sys
from typing import Any

_KNOWLEDGE_DIR = pathlib.Path(".claude/skills/nabledge-6/knowledge")
_SCENARIO_FILE = pathlib.Path("tools/benchmark/scenarios/qa.json")
_OUTPUT_FILE = pathlib.Path("tools/rag/v3-eligible-scenarios.json")
# Sections whose text exceeds this length have their embedding truncated by index.py,
# reducing retrieval quality. Scenarios referencing such sections are excluded.
_V3_MAX_CHARS = 2048


def build_text(page_title: str, section_title: str, section_content: str) -> str:
    return f"{page_title}\n{section_title}\n{section_content}"


def find_truncated_pages(knowledge_dir: pathlib.Path) -> dict[str, list[str]]:
    """Return {page_id: [section_ids...]} for pages that have at least one truncated section."""
    truncated: dict[str, list[str]] = {}
    for json_file in knowledge_dir.rglob("*.json"):
        page_id = str(json_file.relative_to(knowledge_dir).with_suffix(""))
        try:
            with open(json_file, encoding="utf-8") as f:
                page: dict[str, Any] = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[WARN] Skipping {json_file}: {e}", file=sys.stderr)
            continue
        page_title: str = page.get("title", "")
        bad_sections: list[str] = []
        for section in page.get("sections", []):
            text = build_text(
                page_title,
                section.get("title", ""),
                section.get("content", ""),
            )
            if len(text) > _V3_MAX_CHARS:
                bad_sections.append(section.get("id", "?"))
        if bad_sections:
            truncated[page_id] = bad_sections
    return truncated


def page_id_from_section_ref(section_ref: str) -> str:
    """Extract page_id from 'path/to/file.json:sN' format."""
    if ":" not in section_ref:
        print(
            f"[WARN] section_ref has no ':' separator, using path as-is: {section_ref!r}",
            file=sys.stderr,
        )
    path_part = section_ref.split(":")[0]
    return str(pathlib.Path(path_part).with_suffix(""))


def select_scenarios(
    scenarios: list[dict[str, Any]],
    truncated: dict[str, list[str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split scenarios into eligible and ineligible lists."""
    eligible: list[dict[str, Any]] = []
    ineligible: list[dict[str, Any]] = []

    for scenario in scenarios:
        then = scenario.get("then", {})
        all_refs: list[str] = []
        for item in then.get("must", []):
            if "section" in item:
                all_refs.append(item["section"])
        for item in then.get("acceptable", []):
            if "section" in item:
                all_refs.append(item["section"])

        referenced_pages = {page_id_from_section_ref(r) for r in all_refs}
        bad_pages = referenced_pages & set(truncated.keys())

        if bad_pages:
            ineligible.append(
                {
                    "id": scenario["id"],
                    "reason": "excluded",
                    "truncated_pages": sorted(bad_pages),
                    "truncated_sections_per_page": {p: truncated[p] for p in sorted(bad_pages)},
                }
            )
        else:
            eligible.append(
                {
                    "id": scenario["id"],
                    "reason": "all referenced pages have sections within 2048 chars",
                    "referenced_pages": sorted(referenced_pages),
                }
            )

    return eligible, ineligible


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--knowledge-dir",
        default=str(_KNOWLEDGE_DIR),
        help="Path to nabledge-6 knowledge directory",
    )
    parser.add_argument(
        "--scenario-file",
        default=str(_SCENARIO_FILE),
        help="Path to qa.json scenario definitions",
    )
    parser.add_argument(
        "--output",
        default=str(_OUTPUT_FILE),
        help="Output JSON path",
    )
    args = parser.parse_args()

    knowledge_dir = pathlib.Path(args.knowledge_dir)
    scenario_file = pathlib.Path(args.scenario_file)
    output_path = pathlib.Path(args.output)

    if not knowledge_dir.exists():
        print(f"ERROR: knowledge_dir not found: {knowledge_dir}", file=sys.stderr)
        sys.exit(1)
    if not scenario_file.exists():
        print(f"ERROR: scenario_file not found: {scenario_file}", file=sys.stderr)
        sys.exit(1)

    print("Scanning knowledge pages for truncated sections...", flush=True)
    truncated = find_truncated_pages(knowledge_dir)
    print(f"  Pages with truncated sections: {len(truncated)}", flush=True)

    with open(scenario_file, encoding="utf-8") as f:
        data = json.load(f)
    scenarios = data.get("scenarios")
    if scenarios is None:
        print(f"ERROR: 'scenarios' key missing in {scenario_file}", file=sys.stderr)
        sys.exit(1)
    print(f"  Total scenarios: {len(scenarios)}", flush=True)

    eligible, ineligible = select_scenarios(scenarios, truncated)
    print(f"  Eligible: {len(eligible)}, Ineligible: {len(ineligible)}", flush=True)

    result = {
        "description": (
            "v3-eligible scenarios: all referenced pages have NO section "
            "whose embedded text exceeds 2048 characters (Cohere embed-multilingual-v3 limit)."
        ),
        "v3_max_chars": _V3_MAX_CHARS,
        "total_scenarios": len(scenarios),
        "eligible_count": len(eligible),
        "ineligible_count": len(ineligible),
        "eligible_scenario_ids": [e["id"] for e in eligible],
        "eligible": eligible,
        "ineligible": ineligible,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Written: {output_path}", flush=True)


if __name__ == "__main__":
    main()
