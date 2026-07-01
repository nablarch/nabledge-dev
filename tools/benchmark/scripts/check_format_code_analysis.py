"""Format checker for code-analysis documentation output.

Checks that a generated documentation string meets the structural requirements:
no unreplaced placeholders, all required section headings present, and both
class and sequence Mermaid diagrams included.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Required top-level section headings in the generated documentation
_REQUIRED_SECTIONS = [
    "# Code Analysis:",
    "## Overview",
    "## Architecture",
    "## Flow",
    "## Components",
    "## Nablarch Framework Usage",
    "## References",
]

_MERMAID_BLOCK_PATTERN = re.compile(r"```mermaid\s*(.*?)```", re.DOTALL)
_PLACEHOLDER_PATTERN = re.compile(r"\{\{[^}]+\}\}")


def check_format(content: str) -> dict:
    """Check a documentation content string for format compliance.

    Returns:
        {
          "passed": bool,
          "checks": {
            "no_unreplaced_placeholders": bool,
            "all_sections_present": bool,
            "has_class_diagram": bool,
            "has_sequence_diagram": bool
          },
          "details": {"<check_name>": "<failure description or 'OK'>"}
        }
    """
    checks: dict[str, bool] = {}
    details: dict[str, str] = {}

    # Check 1: no unreplaced placeholders ({{...}} patterns)
    placeholders_found = _PLACEHOLDER_PATTERN.findall(content)
    if placeholders_found:
        checks["no_unreplaced_placeholders"] = False
        details["no_unreplaced_placeholders"] = (
            f"Unreplaced placeholders found: {', '.join(placeholders_found)}"
        )
    else:
        checks["no_unreplaced_placeholders"] = True
        details["no_unreplaced_placeholders"] = "OK"

    # Check 2: all 7 required section headings present
    missing_sections = [s for s in _REQUIRED_SECTIONS if s not in content]
    if missing_sections:
        checks["all_sections_present"] = False
        details["all_sections_present"] = (
            f"Missing sections: {', '.join(repr(s) for s in missing_sections)}"
        )
    else:
        checks["all_sections_present"] = True
        details["all_sections_present"] = "OK"

    # Check 3 & 4: mermaid diagrams
    mermaid_blocks = _MERMAID_BLOCK_PATTERN.findall(content)

    has_class = any("classDiagram" in block for block in mermaid_blocks)
    if has_class:
        checks["has_class_diagram"] = True
        details["has_class_diagram"] = "OK"
    else:
        checks["has_class_diagram"] = False
        details["has_class_diagram"] = "No classDiagram found inside a ```mermaid block"

    has_sequence = any("sequenceDiagram" in block for block in mermaid_blocks)
    if has_sequence:
        checks["has_sequence_diagram"] = True
        details["has_sequence_diagram"] = "OK"
    else:
        checks["has_sequence_diagram"] = False
        details["has_sequence_diagram"] = "No sequenceDiagram found inside a ```mermaid block"

    passed = all(checks.values())
    return {
        "passed": passed,
        "checks": checks,
        "details": details,
    }


def check_file(path: str) -> dict:
    """Read a file and run check_format on its contents."""
    content = Path(path).read_text(encoding="utf-8")
    return check_format(content)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Check format compliance of a code-analysis documentation output file"
    )
    parser.add_argument("--content-file", required=True, help="Path to the documentation file to check")
    args = parser.parse_args()

    result = check_file(args.content_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
