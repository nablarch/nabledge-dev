#!/usr/bin/env python3
"""
Knowledge Creator - Main Entry Point

Converts Nablarch official documentation (RST/MD/Excel) to AI-ready JSON knowledge files.
"""

import argparse
import sys
import os
from dataclasses import dataclass
from datetime import datetime
from glob import glob
import shutil

# Add steps directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'steps'))

from steps.step1_list_sources import Step1ListSources
from steps.step2_classify import Step2Classify
from steps.step3_generate import Step3Generate
from steps.step4_build_index import Step4BuildIndex
from steps.step5_generate_docs import Step5GenerateDocs
from steps.step6_validate import Step6Validate


@dataclass
class Context:
    """Shared context for all steps"""
    version: str          # "6" or "5"
    repo: str             # Repository root path
    concurrency: int      # Concurrency level for parallel processing
    test_mode: bool = False  # Test mode: process curated file set only

    def __post_init__(self):
        """Validate paths after initialization"""
        if not os.path.isdir(self.repo):
            raise ValueError(f"Repository path does not exist: {self.repo}")

        # Check for critical subdirectories
        required_dirs = [
            f"{self.repo}/.lw/nab-official/v{self.version}",
            f"{self.repo}/.claude/skills/nabledge-{self.version}"
        ]

        for dir_path in required_dirs:
            if not os.path.isdir(dir_path):
                raise ValueError(f"Required directory does not exist: {dir_path}")

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


def detect_changes(ctx: Context) -> dict:
    """Detect changes between current source files and existing knowledge files"""
    import json

    # Load current classified list
    if not os.path.exists(ctx.classified_list_path):
        return {"added": set(), "deleted": set(), "updated": set()}

    with open(ctx.classified_list_path) as f:
        current = json.load(f)

    current_ids = {f["id"] for f in current["files"]}

    # Scan existing knowledge files
    existing_ids = set()
    if os.path.exists(ctx.knowledge_dir):
        for json_file in glob(f"{ctx.knowledge_dir}/**/*.json", recursive=True):
            if "index.toon" not in json_file:
                existing_ids.add(os.path.basename(json_file).replace(".json", ""))

    added = current_ids - existing_ids
    deleted = existing_ids - current_ids

    # Detect updates (source mtime > knowledge file mtime)
    updated = set()
    for f in current["files"]:
        if f["id"] not in added:
            source_path = f"{ctx.repo}/{f['source_path']}"
            json_path = f"{ctx.knowledge_dir}/{f['output_path']}"

            if os.path.exists(source_path) and os.path.exists(json_path):
                source_mtime = os.path.getmtime(source_path)
                json_mtime = os.path.getmtime(json_path)
                if source_mtime > json_mtime:
                    updated.add(f["id"])

    return {"added": added, "deleted": deleted, "updated": updated}


def delete_knowledge(ctx: Context, file_id: str, file_info: dict):
    """Delete knowledge file, docs, and assets for a file"""
    json_path = f"{ctx.knowledge_dir}/{file_info['output_path']}"
    md_path = f"{ctx.docs_dir}/{file_info['type']}/{file_info['category']}/{file_id}.md"
    assets_path = f"{ctx.knowledge_dir}/{file_info['assets_dir']}"

    for path in [json_path, md_path]:
        if os.path.exists(path):
            os.remove(path)
            print(f"Deleted: {path}")

    if os.path.exists(assets_path):
        shutil.rmtree(assets_path)
        print(f"Deleted assets: {assets_path}")


def delete_knowledge_json(ctx: Context, file_id: str, file_info: dict):
    """Delete only the knowledge JSON file (for updates)"""
    json_path = f"{ctx.knowledge_dir}/{file_info['output_path']}"
    if os.path.exists(json_path):
        os.remove(json_path)
        print(f"Deleted for update: {json_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Knowledge Creator - Convert Nablarch documentation to AI-ready JSON"
    )
    parser.add_argument(
        "--version",
        required=True,
        choices=["6", "5", "all"],
        help="Version to process (6, 5, or all)"
    )
    parser.add_argument(
        "--step",
        type=int,
        choices=[1, 2, 3, 4, 5, 6],
        help="Run specific step only (1-6)"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Number of parallel claude -p sessions (default: 4)"
    )
    parser.add_argument(
        "--repo",
        default=os.getcwd(),
        help="Repository root path (default: current directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without actual execution"
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Test mode: process curated file set covering all validation scenarios"
    )

    args = parser.parse_args()

    # Resolve versions to process
    versions = ["6", "5"] if args.version == "all" else [args.version]

    for v in versions:
        print(f"\n{'='*60}")
        print(f"Processing version: {v}")
        if args.test_mode:
            print(f"TEST MODE: Processing curated file set only")
        print(f"{'='*60}\n")

        ctx = Context(
            version=v,
            repo=args.repo,
            concurrency=args.concurrency,
            test_mode=args.test_mode
        )

        # Create log directory
        os.makedirs(ctx.log_dir, exist_ok=True)

        # Step 1, 2: Always run (lightweight, overwrite generation)
        if args.step is None or args.step <= 2:
            print("\n--- Step 1: List Source Files ---")
            sources_output = Step1ListSources(ctx, dry_run=args.dry_run).run()

            print("\n--- Step 2: Classify Files ---")
            Step2Classify(ctx, dry_run=args.dry_run, sources_data=sources_output).run()

        # Detect changes (before Step 3+)
        if not args.dry_run and (args.step is None or args.step >= 3):
            changes = detect_changes(ctx)

            if changes["deleted"]:
                print(f"\nDeleted files: {len(changes['deleted'])}")
                import json
                with open(ctx.classified_list_path) as f:
                    classified = json.load(f)
                file_info_map = {f["id"]: f for f in classified["files"]}

                for file_id in changes["deleted"]:
                    if file_id in file_info_map:
                        delete_knowledge(ctx, file_id, file_info_map[file_id])

            if changes["updated"]:
                print(f"\nUpdated files: {len(changes['updated'])}")
                import json
                with open(ctx.classified_list_path) as f:
                    classified = json.load(f)
                file_info_map = {f["id"]: f for f in classified["files"]}

                for file_id in changes["updated"]:
                    if file_id in file_info_map:
                        delete_knowledge_json(ctx, file_id, file_info_map[file_id])

        # Step 3: Generate knowledge files
        if args.step is None or args.step == 3:
            print("\n--- Step 3: Generate Knowledge Files ---")
            Step3Generate(ctx, dry_run=args.dry_run).run()

        # Step 4: Build index.toon
        if args.step is None or args.step == 4:
            print("\n--- Step 4: Build index.toon ---")
            Step4BuildIndex(ctx, dry_run=args.dry_run).run()

        # Step 5: Generate browsable docs
        if args.step is None or args.step == 5:
            print("\n--- Step 5: Generate Browsable Docs ---")
            Step5GenerateDocs(ctx, dry_run=args.dry_run).run()

        # Step 6: Validate
        if args.step is None or args.step == 6:
            print("\n--- Step 6: Validate ---")
            Step6Validate(ctx, dry_run=args.dry_run).run()

        print(f"\n{'='*60}")
        print(f"Completed version: {v}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
