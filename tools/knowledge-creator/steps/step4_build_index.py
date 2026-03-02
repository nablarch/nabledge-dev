"""Step 4: Build index.toon

Build knowledge index file with processing patterns classification.
"""

import os
import json
import subprocess
from glob import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from .common import load_json, write_json, read_file, write_file, run_claude


class Step4BuildIndex:
    def __init__(self, ctx, dry_run=False):
        self.ctx = ctx
        self.dry_run = dry_run
        self.prompt_template = read_file(f"{ctx.repo}/tools/knowledge-creator/prompts/classify_patterns.md")

    def classify_patterns_with_claude(self, file_info: dict, knowledge: dict) -> str:
        """Use claude -p to classify processing patterns for a knowledge file"""
        file_id = file_info["id"]
        log_path = f"{self.ctx.log_dir}/classify-patterns/{file_id}.json"

        # Check if already classified
        if os.path.exists(log_path):
            cached = load_json(log_path)
            return cached.get("patterns", "")

        prompt = self.prompt_template
        prompt = prompt.replace("{FILE_ID}", file_id)
        prompt = prompt.replace("{TITLE}", knowledge.get("title", ""))
        prompt = prompt.replace("{TYPE}", file_info["type"])
        prompt = prompt.replace("{CATEGORY}", file_info["category"])
        prompt = prompt.replace("{KNOWLEDGE_JSON}", json.dumps(knowledge, ensure_ascii=False, indent=2))

        try:
            result = run_claude(prompt, timeout=120)
            if result.returncode == 0:
                patterns = result.stdout.strip()
                if not self.dry_run:
                    write_json(log_path, {"file_id": file_id, "patterns": patterns})
                return patterns
        except subprocess.TimeoutExpired:
            if not self.dry_run:
                write_json(log_path, {"file_id": file_id, "patterns": "", "error": "timeout"})

        return ""

    def write_toon(self, index_path: str, entries: list, version: str):
        """Write index.toon in TOON format"""
        lines = [f"# Nabledge-{version} Knowledge Index", ""]
        lines.append(f"files[{len(entries)},]{{title,type,category,processing_patterns,path}}:")

        for entry in entries:
            # Replace comma with full-width comma in title to avoid field separator collision
            title = entry["title"].replace(",", "、")
            fields = [
                title,
                entry["type"],
                entry["category"],
                entry["processing_patterns"],
                entry["path"],
            ]
            lines.append(f"  {', '.join(fields)}")

        lines.append("")  # Final newline
        content = '\n'.join(lines)

        if not self.dry_run:
            write_file(index_path, content)

    def run(self):
        """Execute Step 4: Build index.toon"""
        classified = load_json(self.ctx.classified_list_path)
        entries = []

        # Collect knowledge files that need pattern classification
        to_classify = []

        for file_info in classified["files"]:
            json_path = f"{self.ctx.knowledge_dir}/{file_info['output_path']}"

            if not os.path.exists(json_path):
                # Not yet generated
                entries.append({
                    "title": file_info["id"],
                    "type": file_info["type"],
                    "category": file_info["category"],
                    "processing_patterns": "",
                    "path": "not yet created"
                })
                continue

            knowledge = load_json(json_path)
            title = knowledge.get("title", file_info["id"])

            # Determine processing patterns
            if file_info["type"] == "processing-pattern":
                patterns = file_info["category"]
            else:
                to_classify.append((file_info, knowledge))
                patterns = None  # Will be filled in later

            entries.append({
                "title": title,
                "type": file_info["type"],
                "category": file_info["category"],
                "processing_patterns": patterns,
                "path": file_info["output_path"],
                "file_info": file_info,
                "knowledge": knowledge
            })

        # Classify processing patterns in parallel
        if to_classify and not self.dry_run:
            print(f"Classifying processing patterns for {len(to_classify)} files...")

            with ThreadPoolExecutor(max_workers=self.ctx.concurrency) as executor:
                futures = {}
                for file_info, knowledge in to_classify:
                    future = executor.submit(self.classify_patterns_with_claude, file_info, knowledge)
                    futures[future] = file_info["id"]

                for future in as_completed(futures):
                    file_id = futures[future]
                    patterns = future.result()
                    # Update entry
                    for entry in entries:
                        if entry.get("file_info", {}).get("id") == file_id:
                            entry["processing_patterns"] = patterns
                            break

        # Clean up temporary fields
        for entry in entries:
            if "file_info" in entry:
                del entry["file_info"]
            if "knowledge" in entry:
                del entry["knowledge"]
            if entry["processing_patterns"] is None:
                entry["processing_patterns"] = ""

        # Write index.toon
        print(f"Writing index.toon with {len(entries)} entries")

        if not self.dry_run:
            self.write_toon(self.ctx.index_path, entries, self.ctx.version)
            print(f"Wrote: {self.ctx.index_path}")
        else:
            print(f"Would write: {self.ctx.index_path}")
