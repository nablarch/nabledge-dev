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
from common import load_json, write_json, read_file, run_claude as _default_run_claude, aggregate_cc_metrics
from logger import get_logger


class PhaseBGenerate:
    def __init__(self, ctx, dry_run=False, run_claude_fn=None):
        self.ctx = ctx
        self.dry_run = dry_run
        self.run_claude = run_claude_fn or _default_run_claude
        self.logger = get_logger()
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
        self.logger = get_logger()
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
        prompt = prompt.replace("{OFFICIAL_DOC_BASE_URL}", self._compute_official_url(file_info))
        prompt = prompt.replace("{SOURCE_CONTENT}", source_content)

        if file_info["format"] == "rst":
            labels = self._extract_rst_labels(source_content)
            prompt = prompt.replace("{INTERNAL_LABELS}", json.dumps(labels, ensure_ascii=False))
        else:
            prompt = prompt.replace("{INTERNAL_LABELS}", "[]")

        # Pass detected section list to prevent Claude from missing sections (especially for large split files)
        if "section_range" in file_info and "sections" in file_info["section_range"]:
            sections_list = file_info["section_range"]["sections"]
            if isinstance(sections_list, list) and sections_list:
                if len(sections_list) > 10:
                    self.logger.debug(f"    Passing {len(sections_list)} detected sections to Claude")
                sections_md = "\n".join(f"- {s}" for s in sections_list)
                prompt = prompt.replace("{EXPECTED_SECTIONS}", sections_md)
            else:
                prompt = prompt.replace("{EXPECTED_SECTIONS}", "(empty - scan the source yourself)")
        else:
            prompt = prompt.replace("{EXPECTED_SECTIONS}", "(empty - scan the source yourself)")

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
        output_path = f"{self.ctx.knowledge_cache_dir}/{file_info['output_path']}"
        log_path = f"{self.ctx.log_dir}/generate/{file_id}.json"

        if os.path.exists(output_path):
            self.logger.info(f"  [SKIP] {file_id}")
            return {"status": "skip", "id": file_id}

        self.logger.info(f"   🤖[GEN] {file_id}")
        source_content = read_file(source_path)

        if 'section_range' in file_info:
            source_content = self._extract_section_range(source_content, file_info['section_range'])

        assets_dir_rel_full = file_info['assets_dir']
        assets_dir_abs = f"{self.ctx.knowledge_cache_dir}/{assets_dir_rel_full}"
        json_dir = os.path.dirname(file_info['output_path'])
        assets_dir_rel = os.path.relpath(assets_dir_rel_full, json_dir) + "/"

        assets = self._extract_assets(
            file_info['source_path'], source_content,
            file_info['format'], assets_dir_abs, assets_dir_rel
        )
        prompt = self._build_prompt(file_info, source_content, assets)
        started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        result = self.run_claude(
            prompt=prompt,
            json_schema=self.json_schema,
            log_dir=self.ctx.phase_b_executions_dir,
            file_id=file_id,
            verbose=self.ctx.verbose
        )

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

    def run(self, target_ids=None):
        classified = load_json(self.ctx.classified_list_path)
        files = classified["files"]

        if target_ids is not None:
            target_set = set(target_ids)
            files = [f for f in files if f["id"] in target_set]

        if self.dry_run:
            self.logger.info(f"Would generate {len(files)} knowledge files")
            return

        with ThreadPoolExecutor(max_workers=self.ctx.concurrency) as executor:
            futures = [executor.submit(self.generate_one, fi) for fi in files]
            results = {"ok": 0, "error": 0, "skip": 0}
            for future in as_completed(futures):
                r = future.result()
                results[r["status"]] += 1
                if r["status"] == "error":
                    self.logger.error(f"    ERROR: {r['id']}: {r.get('error', '')}")

        ok_icon = "✅" if results['error'] == 0 else "⚠️"
        self.logger.info(f"\n   {ok_icon} Generation: OK={results['ok']}, Skip={results['skip']}, Error={results['error']}")
        metrics = aggregate_cc_metrics(self.ctx.phase_b_executions_dir)
        self.logger.info(
            f"   📊 Metrics: cost=${metrics['cost_usd']:.3f} "
            f"avg_turns={metrics.get('avg_turns', 'N/A')} "
            f"avg={metrics.get('avg_duration_sec', 'N/A')}s "
            f"p95={metrics.get('p95_duration_sec', 'N/A')}s"
        )
        results["metrics"] = metrics
        return results
