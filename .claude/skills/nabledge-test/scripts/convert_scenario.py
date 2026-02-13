#!/usr/bin/env python3
"""
Convert nabledge scenarios.json format to skill-creator eval format.

Usage:
    python convert_scenario.py <scenarios-file> <scenario-id>

Example:
    python convert_scenario.py scenarios/nabledge-6/scenarios.json handlers-001
"""

import json
import sys
from pathlib import Path


def convert_scenario(scenarios_file, scenario_id):
    """Convert a single scenario to eval format."""

    # Load scenarios
    with open(scenarios_file) as f:
        data = json.load(f)

    # Find target scenario
    scenario = None
    for s in data["scenarios"]:
        if s["id"] == scenario_id:
            scenario = s
            break

    if not scenario:
        print(f"Error: Scenario '{scenario_id}' not found", file=sys.stderr)
        sys.exit(1)

    # Convert to eval format
    eval_data = {
        "prompt": scenario["question"],
        "expectations": []
    }

    # Add keyword expectations
    for keyword in scenario.get("expected_keywords", []):
        eval_data["expectations"].append(
            f"Response includes keyword '{keyword}'"
        )

    # Add section expectations
    sections = scenario.get("expected_sections", [])
    if sections:
        sections_str = "' or '".join(sections)
        eval_data["expectations"].append(
            f"Response mentions '{sections_str}' sections"
        )

    # Add standard efficiency expectations
    eval_data["expectations"].append(
        "Token usage is between 5000 and 15000"
    )
    eval_data["expectations"].append(
        "Tool calls are between 10 and 20"
    )

    # Add metadata for reference
    eval_data["metadata"] = {
        "scenario_id": scenario["id"],
        "category": scenario["category"],
        "source_file": scenario.get("file", ""),
        "relevance": scenario.get("relevance", "high")
    }

    return eval_data


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    scenarios_file = sys.argv[1]
    scenario_id = sys.argv[2]

    eval_data = convert_scenario(scenarios_file, scenario_id)

    # Output as JSON
    print(json.dumps(eval_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
