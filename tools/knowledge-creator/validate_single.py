#!/usr/bin/env python3
"""
Single File Validation Script for Agent

Validates a single knowledge JSON file against structural checks.
Outputs all errors in human-readable format.

Exit codes:
  0: All checks passed
  1: Validation errors found

Usage:
  python validate_single.py <json_path> <source_path> <source_format>

Example:
  python validate_single.py knowledge.json source.rst rst
"""

import sys
import os
from dataclasses import dataclass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from steps.step6_validate import Step6Validate


@dataclass
class MockContext:
    """Mock context for validation"""
    repo: str


def main():
    if len(sys.argv) != 4:
        print("Usage: python validate_single.py <json_path> <source_path> <source_format>")
        print("  json_path: Path to knowledge JSON file")
        print("  source_path: Path to source file (RST/MD/XLSX)")
        print("  source_format: Format (rst/md/xlsx)")
        sys.exit(2)

    json_path = sys.argv[1]
    source_path = sys.argv[2]
    source_format = sys.argv[3]

    # Validate inputs
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found: {json_path}")
        sys.exit(2)

    if not os.path.exists(source_path):
        print(f"Error: Source file not found: {source_path}")
        sys.exit(2)

    if source_format not in ["rst", "md", "xlsx"]:
        print(f"Error: Invalid format '{source_format}'. Must be rst, md, or xlsx")
        sys.exit(2)

    # Setup mock context
    repo = os.getcwd()
    ctx = MockContext(repo=repo)

    # Run validation
    validator = Step6Validate(ctx, dry_run=True)
    errors = validator.validate_structure(json_path, source_path, source_format)

    # Output results
    if not errors:
        print("✅ All validation checks passed!")
        sys.exit(0)
    else:
        print(f"❌ Found {len(errors)} validation error(s):\n")
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error}")
        print("\nPlease fix these errors and run validation again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
