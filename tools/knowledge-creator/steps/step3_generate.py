"""Step 3: Generate Knowledge Files

Generate JSON knowledge files from source documentation using claude -p.
"""

import os
import re
import json
import shutil
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from .common import load_json, write_json, read_file, run_claude


class Step3Generate:
    def __init__(self, ctx, dry_run=False):
        self.ctx = ctx
        self.dry_run = dry_run
        self.prompt_template = read_file(f"{ctx.repo}/tools/knowledge-creator/prompts/generate.md")
        self.json_schema = self.extract_json_schema()

    def extract_json_schema(self) -> dict:
        """Extract JSON Schema from prompt template"""
        # Extract JSON schema from markdown code block
        match = re.search(r'```json\s*\n(\{[^`]+\})\s*\n```', self.prompt_template, re.DOTALL)
        if not match:
            raise ValueError("JSON Schema not found in prompt template")

        schema_text = match.group(1)
        # Remove $schema field as it's metadata
        schema = json.loads(schema_text)
        if "$schema" in schema:
            del schema["$schema"]
        return schema

    def extract_assets(self, source_path: str, source_content: str, source_format: str,
                      assets_dir_abs: str, assets_dir_rel: str) -> list:
        """Extract images and attachments from source file

        Args:
            source_path: Relative path to source file
            source_content: Content of source file
            source_format: Format (rst/md/xlsx)
            assets_dir_abs: Absolute path to assets directory
            assets_dir_rel: Relative path from knowledge JSON file to assets directory
        """
        assets = []
        source_dir = os.path.dirname(f"{self.ctx.repo}/{source_path}")

        if source_format == "rst":
            # Extract image/figure directive references
            image_refs = re.findall(r'\.\.\s+(?:image|figure)::\s+(.+)', source_content)
            for ref in image_refs:
                ref = ref.strip()
                src = os.path.join(source_dir, ref)
                if os.path.exists(src):
                    if not self.dry_run:
                        os.makedirs(assets_dir_abs, exist_ok=True)
                        dst = os.path.join(assets_dir_abs, os.path.basename(ref))
                        shutil.copy2(src, dst)
                    assets.append({
                        "original": ref,
                        "assets_path": f"{assets_dir_rel}{os.path.basename(ref)}"
                    })

            # Extract download directive references
            download_refs = re.findall(r':download:`[^<]*<([^>]+)>`', source_content)
            for ref in download_refs:
                ref = ref.strip()
                src = os.path.join(source_dir, ref)
                if os.path.exists(src):
                    if not self.dry_run:
                        os.makedirs(assets_dir_abs, exist_ok=True)
                        dst = os.path.join(assets_dir_abs, os.path.basename(ref))
                        shutil.copy2(src, dst)
                    assets.append({
                        "original": ref,
                        "assets_path": f"{assets_dir_rel}{os.path.basename(ref)}"
                    })

        return assets

    def compute_official_url(self, file_info: dict) -> str:
        """Compute official documentation URL from file info"""
        if file_info["format"] == "rst":
            path = file_info["source_path"]
            marker = "nablarch-document/ja/"
            idx = path.find(marker)
            if idx >= 0:
                relative = path[idx + len(marker):]
                relative = relative.replace(".rst", ".html")
                return f"https://nablarch.github.io/docs/LATEST/doc/{relative}"
        elif file_info["format"] in ("md", "xlsx"):
            return "https://fintan.jp/page/252/"
        return ""

    def build_prompt(self, file_info: dict, source_content: str, assets: list) -> str:
        """Build prompt for claude -p"""
        prompt = self.prompt_template

        # Replace placeholders
        prompt = prompt.replace("{FILE_ID}", file_info["id"])
        prompt = prompt.replace("{FORMAT}", file_info["format"])
        prompt = prompt.replace("{TYPE}", file_info["type"])
        prompt = prompt.replace("{CATEGORY}", file_info["category"])
        prompt = prompt.replace("{OUTPUT_PATH}", file_info["output_path"])
        prompt = prompt.replace("{ASSETS_DIR}", file_info["assets_dir"])
        prompt = prompt.replace("{OFFICIAL_DOC_BASE_URL}", self.compute_official_url(file_info))
        prompt = prompt.replace("{SOURCE_CONTENT}", source_content)

        # Add assets section if any
        if assets:
            assets_section = "\n## 画像・添付ファイル一覧\n\n"
            assets_section += "このソースファイルから以下の画像・添付ファイルが抽出済みです。\n"
            assets_section += "テキスト代替が困難な場合のみ、assets_pathを使って参照してください。\n\n"
            assets_section += "| ソース内パス | assetsパス |\n"
            assets_section += "|---|---|\n"
            for asset in assets:
                assets_section += f"| {asset['original']} | {asset['assets_path']} |\n"
            prompt = prompt.replace("{ASSETS_SECTION}", assets_section)
        else:
            prompt = prompt.replace("{ASSETS_SECTION}", "")

        return prompt

    def extract_json(self, output: str) -> dict:
        """Extract JSON from claude -p output

        When using --json-schema, output is already the structured_output JSON.
        """
        return json.loads(output.strip())

    def extract_section_range(self, content: str, section_range: dict) -> str:
        """Extract specific section range from content

        Args:
            content: Full file content
            section_range: Dict with start_line, end_line, sections keys

        Returns:
            Extracted content for the specified range
        """
        lines = content.splitlines()
        start = section_range['start_line']
        end = section_range['end_line']
        return '\n'.join(lines[start:end])

    def generate_one(self, file_info: dict) -> dict:
        """Generate knowledge file for one source file"""
        file_id = file_info["id"]
        source_path = f"{self.ctx.repo}/{file_info['source_path']}"
        output_path = f"{self.ctx.knowledge_dir}/{file_info['output_path']}"
        log_path = f"{self.ctx.log_dir}/generate/{file_id}.json"

        # Skip if already generated
        if os.path.exists(output_path):
            print(f"  [SKIP] {file_id} (already exists)")
            return {"status": "skip", "id": file_id}

        # Show split info if present
        if 'split_info' in file_info:
            split_info = file_info['split_info']
            print(f"  [GEN] {file_id} (part {split_info['part']} of split file)")
        else:
            print(f"  [GEN] {file_id}")

        # Read source content
        source_content = read_file(source_path)

        # Extract section range if this is a split file
        if 'section_range' in file_info:
            section_range = file_info['section_range']
            source_content = self.extract_section_range(source_content, section_range)
            print(f"    Extracted sections: {', '.join(section_range['sections'][:3])}{'...' if len(section_range['sections']) > 3 else ''}")

        # Extract assets
        assets_dir_rel_full = file_info['assets_dir']  # "type/category/assets/file_id/"
        assets_dir_abs = f"{self.ctx.knowledge_dir}/{assets_dir_rel_full}"

        # Compute relative path from knowledge JSON to assets directory
        json_dir = os.path.dirname(file_info['output_path'])  # "type/category"
        assets_dir_rel = os.path.relpath(assets_dir_rel_full, json_dir) + "/"  # "assets/file_id/"

        assets = self.extract_assets(file_info['source_path'], source_content,
                                     file_info['format'], assets_dir_abs, assets_dir_rel)

        # Build prompt
        prompt = self.build_prompt(file_info, source_content, assets)

        started_at = datetime.utcnow().isoformat() + "Z"

        # Run claude -p with JSON schema validation
        try:
            result = run_claude(prompt, timeout=900, json_schema=self.json_schema)
        except subprocess.TimeoutExpired:
            log_entry = {
                "file_id": file_id,
                "status": "error",
                "started_at": started_at,
                "finished_at": datetime.utcnow().isoformat() + "Z",
                "error": "timeout",
                "raw_output": ""
            }
            if not self.dry_run:
                write_json(log_path, log_entry)
            return {"status": "error", "id": file_id, "error": "timeout"}

        if result.returncode != 0:
            log_entry = {
                "file_id": file_id,
                "status": "error",
                "started_at": started_at,
                "finished_at": datetime.utcnow().isoformat() + "Z",
                "error": result.stderr,
                "raw_output": result.stdout
            }
            if not self.dry_run:
                write_json(log_path, log_entry)
            return {"status": "error", "id": file_id, "error": result.stderr}

        # Extract and save JSON
        try:
            knowledge_json = self.extract_json(result.stdout)
        except (json.JSONDecodeError, ValueError) as e:
            log_entry = {
                "file_id": file_id,
                "status": "error",
                "started_at": started_at,
                "finished_at": datetime.utcnow().isoformat() + "Z",
                "error": f"JSON extraction failed: {e}",
                "raw_output": result.stdout
            }
            if not self.dry_run:
                write_json(log_path, log_entry)
            return {"status": "error", "id": file_id, "error": str(e)}

        if not self.dry_run:
            write_json(output_path, knowledge_json)

        finished_at = datetime.utcnow().isoformat() + "Z"
        duration = (datetime.fromisoformat(finished_at.rstrip("Z"))
                   - datetime.fromisoformat(started_at.rstrip("Z"))).seconds

        log_entry = {
            "file_id": file_id,
            "status": "ok",
            "started_at": started_at,
            "finished_at": finished_at,
            "duration_sec": duration
        }
        if not self.dry_run:
            write_json(log_path, log_entry)

        return {"status": "ok", "id": file_id}

    def run(self):
        """Execute Step 3: Generate all knowledge files"""
        classified = load_json(self.ctx.classified_list_path)

        if self.dry_run:
            print(f"Would generate {len(classified['files'])} knowledge files")
            return

        with ThreadPoolExecutor(max_workers=self.ctx.concurrency) as executor:
            futures = []
            for file_info in classified["files"]:
                futures.append(executor.submit(self.generate_one, file_info))

            results = {"ok": 0, "error": 0, "skip": 0}
            for future in as_completed(futures):
                result = future.result()
                results[result["status"]] += 1
                if result["status"] == "error":
                    print(f"    ERROR: {result['id']}: {result.get('error', 'unknown')}")

        print(f"\nGeneration complete:")
        print(f"  OK: {results['ok']}")
        print(f"  Skip: {results['skip']}")
        print(f"  Error: {results['error']}")
