"""Phase B: Generate Knowledge Files

Generate JSON knowledge files from source documentation using claude -p.
"""

import os
import re
import json
import shutil
import subprocess
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from .common import load_json, write_json, read_file, run_claude as _default_run_claude


class PhaseBGenerate:
    def __init__(self, ctx, dry_run=False, run_claude_fn=None):
        self.ctx = ctx
        self.dry_run = dry_run
        self.run_claude = run_claude_fn or _default_run_claude
        self.prompt_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/generate.md"
        )
        self.json_schema = self._extract_json_schema()

    def _extract_json_schema(self) -> dict:
        """Extract JSON Schema from the first ```json block in the prompt."""
        match = re.search(
            r'```json\s*\n(\{[^`]+\})\s*\n```',
            self.prompt_template, re.DOTALL
        )
        if not match:
            raise ValueError("JSON Schema not found in prompt template")
        schema = json.loads(match.group(1))
        schema.pop("$schema", None)
        return schema

    def _extract_assets(self, source_path, source_content, source_format,
                        assets_dir_abs, assets_dir_rel):
        """Extract images and attachments from source file."""
        assets = []
        source_dir = os.path.dirname(f"{self.ctx.repo}/{source_path}")

        if source_format == "rst":
            for ref in re.findall(r'\.\.\s+(?:image|figure)::\s+(.+)', source_content):
                ref = ref.strip()
                src = os.path.join(source_dir, ref)
                if os.path.exists(src):
                    if not self.dry_run:
                        os.makedirs(assets_dir_abs, exist_ok=True)
                        shutil.copy2(src, os.path.join(assets_dir_abs, os.path.basename(ref)))
                    assets.append({
                        "original": ref,
                        "assets_path": f"{assets_dir_rel}{os.path.basename(ref)}"
                    })

            for ref in re.findall(r':download:`[^<]*<([^>]+)>`', source_content):
                ref = ref.strip()
                src = os.path.join(source_dir, ref)
                if os.path.exists(src):
                    if not self.dry_run:
                        os.makedirs(assets_dir_abs, exist_ok=True)
                        shutil.copy2(src, os.path.join(assets_dir_abs, os.path.basename(ref)))
                    assets.append({
                        "original": ref,
                        "assets_path": f"{assets_dir_rel}{os.path.basename(ref)}"
                    })

        return assets

    def _compute_official_url(self, file_info):
        if file_info["format"] == "rst":
            path = file_info["source_path"]
            marker = "nablarch-document/ja/"
            idx = path.find(marker)
            if idx >= 0:
                relative = path[idx + len(marker):].replace(".rst", ".html")
                return f"https://nablarch.github.io/docs/LATEST/doc/{relative}"
        elif file_info["format"] in ("md", "xlsx"):
            return "https://fintan.jp/page/252/"
        return ""

    def _extract_rst_labels(self, source_content):
        return re.compile(r'^\.\.\s+_([a-z0-9_-]+):', re.MULTILINE).findall(source_content)

    def _build_prompt(self, file_info, source_content, assets):
        prompt = self.prompt_template
        prompt = prompt.replace("{FILE_ID}", file_info["id"])
        prompt = prompt.replace("{FORMAT}", file_info["format"])
        prompt = prompt.replace("{TYPE}", file_info["type"])
        prompt = prompt.replace("{CATEGORY}", file_info["category"])
        prompt = prompt.replace("{OUTPUT_PATH}", file_info["output_path"])
        prompt = prompt.replace("{SOURCE_PATH}", file_info["source_path"])
        prompt = prompt.replace("{ASSETS_DIR}", file_info["assets_dir"])
        prompt = prompt.replace("{OFFICIAL_DOC_BASE_URL}", self._compute_official_url(file_info))
        prompt = prompt.replace("{SOURCE_CONTENT}", source_content)

        if file_info["format"] == "rst":
            labels = self._extract_rst_labels(source_content)
            prompt = prompt.replace("{INTERNAL_LABELS}", json.dumps(labels, ensure_ascii=False))
        else:
            prompt = prompt.replace("{INTERNAL_LABELS}", "[]")

        if assets:
            section = "\n## 画像・添付ファイル一覧\n\n"
            section += "| ソース内パス | assetsパス |\n|---|---|\n"
            for a in assets:
                section += f"| {a['original']} | {a['assets_path']} |\n"
            prompt = prompt.replace("{ASSETS_SECTION}", section)
        else:
            prompt = prompt.replace("{ASSETS_SECTION}", "")

        return prompt

    def _extract_json(self, output):
        """Extract knowledge and trace from output. Returns (knowledge, trace)."""
        parsed = json.loads(output.strip())
        knowledge = parsed.get("knowledge")
        trace = parsed.get("trace")
        if not knowledge:
            raise ValueError("No 'knowledge' field in output")
        return knowledge, trace

    def _extract_section_range(self, content, section_range):
        lines = content.splitlines()
        return '\n'.join(lines[section_range['start_line']:section_range['end_line']])

    def generate_one(self, file_info):
        file_id = file_info["id"]
        source_path = f"{self.ctx.repo}/{file_info['source_path']}"
        output_path = f"{self.ctx.knowledge_dir}/{file_info['output_path']}"
        log_path = f"{self.ctx.log_dir}/generate/{file_id}.json"

        if os.path.exists(output_path):
            print(f"  [SKIP] {file_id}")
            return {"status": "skip", "id": file_id}

        print(f"  [GEN] {file_id}")
        source_content = read_file(source_path)

        if 'section_range' in file_info:
            source_content = self._extract_section_range(source_content, file_info['section_range'])

        assets_dir_rel_full = file_info['assets_dir']
        assets_dir_abs = f"{self.ctx.knowledge_dir}/{assets_dir_rel_full}"
        json_dir = os.path.dirname(file_info['output_path'])
        assets_dir_rel = os.path.relpath(assets_dir_rel_full, json_dir) + "/"

        assets = self._extract_assets(
            file_info['source_path'], source_content,
            file_info['format'], assets_dir_abs, assets_dir_rel
        )
        prompt = self._build_prompt(file_info, source_content, assets)
        started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        try:
            result = self.run_claude(prompt, timeout=1200, json_schema=self.json_schema)
        except subprocess.TimeoutExpired:
            if not self.dry_run:
                write_json(log_path, {"file_id": file_id, "status": "error", "error": "timeout"})
            return {"status": "error", "id": file_id, "error": "timeout"}

        if result.returncode != 0:
            if not self.dry_run:
                write_json(log_path, {"file_id": file_id, "status": "error", "error": result.stderr})
            return {"status": "error", "id": file_id, "error": result.stderr}

        try:
            knowledge_json, trace_json = self._extract_json(result.stdout)
        except (json.JSONDecodeError, ValueError) as e:
            if not self.dry_run:
                write_json(log_path, {"file_id": file_id, "status": "error", "error": str(e)})
            return {"status": "error", "id": file_id, "error": str(e)}

        if not self.dry_run:
            write_json(output_path, knowledge_json)

            if trace_json and trace_json.get("sections"):
                write_json(f"{self.ctx.trace_dir}/{file_id}.json", {
                    "file_id": file_id,
                    "generated_at": started_at,
                    "sections": trace_json["sections"]
                })

        finished_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        duration = (datetime.fromisoformat(finished_at.rstrip("Z"))
                    - datetime.fromisoformat(started_at.rstrip("Z"))).seconds

        if not self.dry_run:
            write_json(log_path, {
                "file_id": file_id, "status": "ok",
                "started_at": started_at, "finished_at": finished_at,
                "duration_sec": duration
            })

        return {"status": "ok", "id": file_id}

    def _merge_split_files(self):
        """Merge split knowledge files into single files.

        Files with split_info.is_split=true are parts of a larger file.
        Group by original_id, merge, save as {original_id}.json,
        delete part files, update classified_list.json.
        """
        classified = load_json(self.ctx.classified_list_path)

        split_groups = {}
        for fi in classified["files"]:
            if "split_info" in fi and fi["split_info"].get("is_split"):
                oid = fi["split_info"]["original_id"]
                split_groups.setdefault(oid, []).append(fi)

        if not split_groups:
            return

        print(f"\n--- Merging Split Files ---")
        merged_groups = {}

        for original_id, parts in split_groups.items():
            parts.sort(key=lambda p: p["split_info"]["part"])

            part_paths = []
            all_exist = True
            for part in parts:
                pp = f"{self.ctx.knowledge_dir}/{part['output_path']}"
                if os.path.exists(pp):
                    part_paths.append(pp)
                else:
                    all_exist = False
                    break

            if not all_exist:
                print(f"  [SKIP] {original_id}: not all parts generated")
                continue

            print(f"  [MERGE] {original_id}: {len(parts)} parts")
            part_jsons = [load_json(pp) for pp in part_paths]

            merged = {
                "id": original_id,
                "title": part_jsons[0].get("title", ""),
            }

            # Merge official_doc_urls (deduplicate, preserve order)
            seen_urls = set()
            urls = []
            for pj in part_jsons:
                for url in pj.get("official_doc_urls", []):
                    if url not in seen_urls:
                        seen_urls.add(url)
                        urls.append(url)
            merged["official_doc_urls"] = urls

            # Merge index
            index_map = {}
            for pj in part_jsons:
                for entry in pj.get("index", []):
                    sid = entry["id"]
                    if sid not in index_map:
                        index_map[sid] = {
                            "id": sid, "title": entry["title"],
                            "hints": list(entry.get("hints", []))
                        }
                    else:
                        existing = set(index_map[sid]["hints"])
                        for h in entry.get("hints", []):
                            if h not in existing:
                                index_map[sid]["hints"].append(h)
                                existing.add(h)
            merged["index"] = list(index_map.values())

            # Merge sections
            merged["sections"] = {}
            for i, pj in enumerate(part_jsons):
                part_id = parts[i]["id"]
                for sid, content in pj.get("sections", {}).items():
                    content = content.replace(f"assets/{part_id}/", f"assets/{original_id}/")
                    if sid not in merged["sections"]:
                        merged["sections"][sid] = content
                    else:
                        merged["sections"][sid] += "\n\n" + content

            type_ = parts[0]["type"]
            category = parts[0]["category"]
            merged_path = f"{self.ctx.knowledge_dir}/{type_}/{category}/{original_id}.json"

            try:
                write_json(merged_path, merged)

                # Consolidate assets
                merged_assets = f"{self.ctx.knowledge_dir}/{type_}/{category}/assets/{original_id}/"
                for part in parts:
                    part_assets = f"{self.ctx.knowledge_dir}/{part['assets_dir']}"
                    if os.path.exists(part_assets):
                        os.makedirs(merged_assets, exist_ok=True)
                        for af in os.listdir(part_assets):
                            src = os.path.join(part_assets, af)
                            dst = os.path.join(merged_assets, af)
                            if os.path.isfile(src) and not os.path.exists(dst):
                                shutil.move(src, dst)
                        try:
                            os.rmdir(part_assets)
                        except OSError:
                            pass

                for pp in part_paths:
                    os.remove(pp)

                merged_groups[original_id] = parts
            except Exception as e:
                print(f"    ERROR: {original_id}: {e}")

        # Update classified_list
        if merged_groups:
            part_ids = set()
            for parts in merged_groups.values():
                for p in parts:
                    part_ids.add(p["id"])

            new_files = [fi for fi in classified["files"] if fi["id"] not in part_ids]
            for oid, parts in merged_groups.items():
                base = parts[0].copy()
                base["id"] = oid
                base["output_path"] = f"{base['type']}/{base['category']}/{oid}.json"
                base["assets_dir"] = f"{base['type']}/{base['category']}/assets/{oid}/"
                base.pop("split_info", None)
                base.pop("section_range", None)
                new_files.append(base)

            new_files.sort(key=lambda f: (f["type"], f["category"], f["id"]))
            classified["files"] = new_files
            write_json(self.ctx.classified_list_path, classified)

    def run(self):
        classified = load_json(self.ctx.classified_list_path)

        if self.dry_run:
            print(f"Would generate {len(classified['files'])} knowledge files")
            return

        with ThreadPoolExecutor(max_workers=self.ctx.concurrency) as executor:
            futures = [executor.submit(self.generate_one, fi) for fi in classified["files"]]
            results = {"ok": 0, "error": 0, "skip": 0}
            for future in as_completed(futures):
                r = future.result()
                results[r["status"]] += 1
                if r["status"] == "error":
                    print(f"    ERROR: {r['id']}: {r.get('error', '')}")

        print(f"\nGeneration: OK={results['ok']}, Skip={results['skip']}, Error={results['error']}")

        if not self.dry_run:
            self._merge_split_files()
