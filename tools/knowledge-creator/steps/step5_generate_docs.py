"""Step 5: Generate Browsable Markdown Documentation

Convert knowledge JSON files to browsable Markdown format.
"""

import os
from .common import load_json, write_file


class Step5GenerateDocs:
    def __init__(self, ctx, dry_run=False):
        self.ctx = ctx
        self.dry_run = dry_run

    def convert_to_md(self, knowledge: dict) -> str:
        """Convert knowledge JSON to Markdown"""
        lines = [f"# {knowledge['title']}", ""]

        for entry in knowledge.get("index", []):
            section_id = entry["id"]
            section_title = entry["title"]
            section_content = knowledge.get("sections", {}).get(section_id, "")

            lines.append(f"## {section_title}")
            lines.append("")
            lines.append(section_content)
            lines.append("")

        return "\n".join(lines)

    def run(self):
        """Execute Step 5: Generate browsable Markdown docs"""
        classified = load_json(self.ctx.classified_list_path)
        generated = 0

        for file_info in classified["files"]:
            json_path = f"{self.ctx.knowledge_dir}/{file_info['output_path']}"

            if not os.path.exists(json_path):
                continue

            knowledge = load_json(json_path)
            md_content = self.convert_to_md(knowledge)

            md_path = f"{self.ctx.docs_dir}/{file_info['type']}/{file_info['category']}/{file_info['id']}.md"

            if not self.dry_run:
                os.makedirs(os.path.dirname(md_path), exist_ok=True)
                write_file(md_path, md_content)

            generated += 1

        print(f"Generated {generated} Markdown documentation files")
        if not self.dry_run:
            print(f"Output directory: {self.ctx.docs_dir}")
