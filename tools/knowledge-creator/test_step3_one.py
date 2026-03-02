#!/usr/bin/env python3
"""Test Step 3 with a single small file."""

import json
import sys
import os

# Add repo root to path to import as package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from dataclasses import dataclass
from tools.knowledge_creator.steps.step3_generate import generate_one


@dataclass
class TestContext:
    """Test context object."""
    repo: str = "/home/tie303177/work/nabledge/work3"
    version: str = "6"
    concurrency: int = 1
    dry_run: bool = False
    knowledge_dir: str = "/home/tie303177/work/nabledge/work3/.claude/skills/nabledge-6/knowledge"
    log_dir: str = "/home/tie303177/work/nabledge/work3/tools/knowledge-creator/logs/v6"


def main():
    """Test with application_design.rst."""
    ctx = TestContext()

    # Single file info
    file_info = {
        "source_path": ".lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/messaging/db/application_design.rst",
        "format": "rst",
        "filename": "application_design.rst",
        "type": "processing-pattern",
        "category": "db-messaging",
        "id": "application_design",
        "output_path": "processing-pattern/db-messaging/application_design.json",
        "assets_dir": "processing-pattern/db-messaging/assets/application_design/"
    }

    print("Testing Step 3 with single file: application_design.rst")
    print(f"Output will be: {os.path.join(ctx.knowledge_dir, file_info['output_path'])}")
    print()

    result = generate_one(ctx, file_info)

    print()
    print(f"Result: {result}")

    if result["status"] == "ok":
        print("\n✅ SUCCESS!")
        output_path = os.path.join(ctx.knowledge_dir, file_info['output_path'])
        with open(output_path) as f:
            knowledge = json.load(f)
        print(f"\nGenerated knowledge file:")
        print(f"  - ID: {knowledge.get('id')}")
        print(f"  - Title: {knowledge.get('title')}")
        print(f"  - Sections: {len(knowledge.get('sections', {}))}")
        print(f"  - Index entries: {len(knowledge.get('index', []))}")
    else:
        print("\n❌ FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
