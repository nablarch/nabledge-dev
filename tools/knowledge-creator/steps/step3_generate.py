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

    def extract_rst_labels(self, source_content: str) -> list:
        """Extract RST label definitions from source content

        Labels are defined as: .. _label_name:
        These indicate internal sections that can be referenced within the same file.
        """
        label_pattern = re.compile(r'^\.\.\s+_([a-z0-9_-]+):', re.MULTILINE)
        return label_pattern.findall(source_content)

    def build_prompt(self, file_info: dict, source_content: str, assets: list) -> str:
        """Build prompt for claude -p"""
        prompt = self.prompt_template

        # Replace placeholders
        prompt = prompt.replace("{FILE_ID}", file_info["id"])
        prompt = prompt.replace("{FORMAT}", file_info["format"])
        prompt = prompt.replace("{TYPE}", file_info["type"])
        prompt = prompt.replace("{CATEGORY}", file_info["category"])
        prompt = prompt.replace("{OUTPUT_PATH}", file_info["output_path"])
        prompt = prompt.replace("{SOURCE_PATH}", file_info["source_path"])
        prompt = prompt.replace("{ASSETS_DIR}", file_info["assets_dir"])
        prompt = prompt.replace("{OFFICIAL_DOC_BASE_URL}", self.compute_official_url(file_info))
        prompt = prompt.replace("{SOURCE_CONTENT}", source_content)

        # Extract internal labels for RST files
        if file_info["format"] == "rst":
            internal_labels = self.extract_rst_labels(source_content)
            labels_json = json.dumps(internal_labels, ensure_ascii=False)
            prompt = prompt.replace("{INTERNAL_LABELS}", labels_json)
        else:
            prompt = prompt.replace("{INTERNAL_LABELS}", "[]")

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
            result = run_claude(prompt, timeout=600, json_schema=self.json_schema)
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

    def merge_split_files(self):
        """Merge split knowledge files into single files

        After generation, files with split_info.is_split=true should be merged
        back into their original_id file.

        Process:
        1. Find all generated files with split_info
        2. Group by original_id
        3. Merge each group into single JSON:
           - metadata: from part 1 (title, type, category, format, etc.)
           - sections: concatenate all parts in order
           - contents: concatenate all parts in order
           - search_hints: merge and deduplicate
           - internal_labels: merge and deduplicate
           - related_topics: merge and deduplicate
           - assets: concatenate all parts
        4. Save merged file as {original_id}.json
        5. Delete individual part files
        """
        classified = load_json(self.ctx.classified_list_path)

        # Group files by original_id
        split_groups = {}
        for file_info in classified["files"]:
            if "split_info" in file_info and file_info["split_info"]["is_split"]:
                original_id = file_info["split_info"]["original_id"]
                if original_id not in split_groups:
                    split_groups[original_id] = []
                split_groups[original_id].append(file_info)

        if not split_groups:
            return

        print(f"\n--- Merging Split Files ---")
        print(f"Found {len(split_groups)} file groups to merge")

        merged_count = 0
        total_parts = 0
        merged_groups = {}  # Track successfully merged groups

        for original_id, parts in split_groups.items():
            # Sort parts by part number
            parts.sort(key=lambda p: p["split_info"]["part"])

            # Check if all parts were generated
            part_files = []
            all_exist = True
            for part in parts:
                part_path = f"{self.ctx.knowledge_dir}/{part['output_path']}"
                if os.path.exists(part_path):
                    part_files.append(part_path)
                else:
                    all_exist = False
                    break

            if not all_exist:
                print(f"  [SKIP] {original_id}: Not all parts generated yet")
                continue

            print(f"  [MERGE] {original_id}: {len(parts)} parts")

            # Load all part JSONs
            part_jsons = []
            for part_path in part_files:
                with open(part_path, 'r', encoding='utf-8') as f:
                    part_jsons.append(json.load(f))

            # Merge data
            merged = {}

            # Metadata from part 1
            first_part = part_jsons[0]
            merged["file_id"] = original_id
            merged["title"] = first_part["title"]
            merged["type"] = first_part["type"]
            merged["category"] = first_part["category"]
            merged["format"] = first_part["format"]
            merged["source_path"] = first_part["source_path"]
            merged["official_doc_base_url"] = first_part["official_doc_base_url"]

            # Concatenate index (sections list)
            merged["index"] = []
            for part_json in part_jsons:
                merged["index"].extend(part_json.get("index", []))

            # Merge sections dict - concatenate contents for each section
            merged["sections"] = {}
            for part_json in part_jsons:
                for section_id, content in part_json.get("sections", {}).items():
                    if section_id not in merged["sections"]:
                        merged["sections"][section_id] = content
                    else:
                        # Concatenate with double newline separator
                        merged["sections"][section_id] += "\n\n" + content

            # Merge and deduplicate search_hints
            all_hints = []
            for part_json in part_jsons:
                all_hints.extend(part_json.get("search_hints", []))
            merged["search_hints"] = sorted(set(all_hints))

            # Merge and deduplicate internal_labels
            all_labels = []
            for part_json in part_jsons:
                all_labels.extend(part_json.get("internal_labels", []))
            merged["internal_labels"] = sorted(set(all_labels))

            # Merge and deduplicate related_topics
            all_topics = []
            for part_json in part_jsons:
                all_topics.extend(part_json.get("related_topics", []))
            merged["related_topics"] = sorted(set(all_topics))

            # Concatenate official_doc_urls
            all_urls = []
            for part_json in part_jsons:
                all_urls.extend(part_json.get("official_doc_urls", []))
            merged["official_doc_urls"] = sorted(set(all_urls))

            # Get type and category from first part
            type_ = parts[0]["type"]
            category = parts[0]["category"]

            # Concatenate assets and update paths to point to merged assets directory
            merged["assets"] = []
            merged_assets_dir = f"{type_}/{category}/assets/{original_id}/"

            for i, part_json in enumerate(part_jsons):
                for asset in part_json.get("assets", []):
                    # Update asset path to point to merged directory
                    # Original path is like "assets/file-id-1/image.png"
                    # Need to change to "assets/file-id/image.png"
                    filename = os.path.basename(asset.get("assets_path", ""))
                    if filename:
                        merged_asset = {
                            "original": asset.get("original", ""),
                            "assets_path": f"{merged_assets_dir}{filename}"
                        }
                        merged["assets"].append(merged_asset)

            # Find output path for merged file
            merged_output_path = f"{type_}/{category}/{original_id}.json"
            merged_file_path = f"{self.ctx.knowledge_dir}/{merged_output_path}"

            # Save merged file
            try:
                write_json(merged_file_path, merged)

                # Consolidate assets directories if they exist
                merged_assets_abs = f"{self.ctx.knowledge_dir}/{merged_assets_dir}"
                for part in parts:
                    part_assets_dir = f"{self.ctx.knowledge_dir}/{part['assets_dir']}"
                    if os.path.exists(part_assets_dir):
                        # Move assets from part directory to merged directory
                        os.makedirs(merged_assets_abs, exist_ok=True)
                        for asset_file in os.listdir(part_assets_dir):
                            src = os.path.join(part_assets_dir, asset_file)
                            dst = os.path.join(merged_assets_abs, asset_file)
                            if os.path.isfile(src):
                                # Only move if destination doesn't exist (avoid overwriting)
                                if not os.path.exists(dst):
                                    shutil.move(src, dst)
                        # Remove empty part assets directory
                        try:
                            os.rmdir(part_assets_dir)
                        except OSError:
                            # Directory not empty, skip
                            pass

                # Delete part files
                for part_path in part_files:
                    os.remove(part_path)

                merged_count += 1
                total_parts += len(parts)
                merged_groups[original_id] = parts  # Track successful merge

            except Exception as e:
                print(f"    ERROR merging {original_id}: {e}")
                continue

        print(f"\nMerge complete: {merged_count} file groups ({total_parts} parts → {merged_count} files)")

        # Update classified_list after successful merges
        if merged_groups:
            self.update_classified_list_after_merge(merged_groups)

    def update_classified_list_after_merge(self, merged_groups: dict):
        """Update classified_list.json after merging split files

        Args:
            merged_groups: Dict mapping original_id to list of part file_info dicts
        """
        classified = load_json(self.ctx.classified_list_path)

        # Create set of part IDs to remove
        part_ids_to_remove = set()
        for original_id, parts in merged_groups.items():
            for part in parts:
                part_ids_to_remove.add(part['id'])

        # Filter out split entries and collect other files
        new_files = []
        for file_info in classified['files']:
            if file_info['id'] in part_ids_to_remove:
                # Skip split entries
                continue
            new_files.append(file_info)

        # Add merged file entries
        for original_id, parts in merged_groups.items():
            # Use part 1 as base (parts are sorted by part number)
            base = parts[0].copy()

            # Update to merged file info
            base['id'] = original_id
            base['output_path'] = f"{base['type']}/{base['category']}/{original_id}.json"
            base['assets_dir'] = f"{base['type']}/{base['category']}/assets/{original_id}/"

            # Remove split-specific fields
            if 'split_info' in base:
                del base['split_info']
            if 'section_range' in base:
                del base['section_range']

            new_files.append(base)

        # Sort by type, category, id for consistent order
        new_files.sort(key=lambda f: (f['type'], f['category'], f['id']))

        # Update classified list
        classified['files'] = new_files

        if not self.dry_run:
            write_json(self.ctx.classified_list_path, classified)
            print(f"  Updated classified_list: removed {len(part_ids_to_remove)} split entries, added {len(merged_groups)} merged entries")

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

        # Merge split files after generation
        if not self.dry_run:
            self.merge_split_files()
