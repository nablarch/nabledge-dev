#!/usr/bin/env python3
"""
knowledge-creator: Tool to convert Nablarch official documentation to AI-ready knowledge files.

Usage:
    python run.py --version 6                    # Process all steps for nabledge-6
    python run.py --version 6 --step 3           # Process only step 3
    python run.py --version 6 --concurrency 8    # Use 8 concurrent workers
    python run.py --version all                  # Process both v6 and v5
    python run.py --version 6 --dry-run          # Show what would be processed
"""

import argparse
import sys
from pathlib import Path
from dataclasses import dataclass

# Add steps directory to path
sys.path.insert(0, str(Path(__file__).parent / "steps"))

from steps import (
    step1_list_sources,
    step2_classify,
    step3_generate,
    step4_build_index,
    step5_generate_docs,
    step6_validate,
)


@dataclass
class Context:
    """Context object shared across all steps."""

    version: str          # "6" or "5"
    repo: str             # Repository root path
    concurrency: int      # Number of concurrent workers
    dry_run: bool         # Dry-run mode (no file writes)

    @property
    def source_list_path(self) -> str:
        return f"{self.repo}/tools/knowledge-creator/logs/v{self.version}/sources.json"

    @property
    def classified_list_path(self) -> str:
        return f"{self.repo}/tools/knowledge-creator/logs/v{self.version}/classified.json"

    @property
    def knowledge_dir(self) -> str:
        return f"{self.repo}/.claude/skills/nabledge-{self.version}/knowledge"

    @property
    def docs_dir(self) -> str:
        return f"{self.repo}/.claude/skills/nabledge-{self.version}/docs"

    @property
    def index_path(self) -> str:
        return f"{self.knowledge_dir}/index.toon"

    @property
    def log_dir(self) -> str:
        return f"{self.repo}/tools/knowledge-creator/logs/v{self.version}"


def run_pipeline(ctx: Context, step: int = None):
    """Execute the knowledge creation pipeline."""

    steps = {
        1: ("List source files", step1_list_sources.run),
        2: ("Classify files", step2_classify.run),
        3: ("Generate knowledge files", step3_generate.run),
        4: ("Build index.toon", step4_build_index.run),
        5: ("Generate browsable docs", step5_generate_docs.run),
        6: ("Validate knowledge files", step6_validate.run),
    }

    if step:
        if step not in steps:
            print(f"Error: Invalid step number: {step}")
            sys.exit(1)
        step_name, step_func = steps[step]
        print(f"\n=== Step {step}: {step_name} (v{ctx.version}) ===\n")
        step_func(ctx)
    else:
        # Run all steps
        for step_num, (step_name, step_func) in steps.items():
            print(f"\n=== Step {step_num}: {step_name} (v{ctx.version}) ===\n")
            step_func(ctx)


def main():
    parser = argparse.ArgumentParser(
        description="Convert Nablarch official documentation to AI-ready knowledge files"
    )
    parser.add_argument(
        "--version",
        required=True,
        choices=["6", "5", "all"],
        help="Nablarch version to process (6, 5, or all)"
    )
    parser.add_argument(
        "--step",
        type=int,
        choices=range(1, 7),
        help="Execute specific step only (1-6)"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Number of concurrent workers (default: 4)"
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository root path (default: current directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without writing files"
    )

    args = parser.parse_args()

    # Resolve repository root to absolute path
    repo = str(Path(args.repo).resolve())

    # Determine versions to process
    versions = ["6", "5"] if args.version == "all" else [args.version]

    # Process each version
    for version in versions:
        ctx = Context(
            version=version,
            repo=repo,
            concurrency=args.concurrency,
            dry_run=args.dry_run
        )

        run_pipeline(ctx, args.step)

    print("\n=== All processing completed ===\n")


if __name__ == "__main__":
    main()
