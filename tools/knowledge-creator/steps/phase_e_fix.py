"""Phase E: Fix

Apply fixes to knowledge files based on validation findings.
"""

import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from .common import load_json, write_json, read_file, run_claude as _default_run_claude

KNOWLEDGE_SCHEMA = {
    "type": "object",
    "required": ["id", "title", "official_doc_urls", "index", "sections"],
    "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "official_doc_urls": {"type": "array", "items": {"type": "string"}},
        "index": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "title", "hints"],
                "properties": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "hints": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "sections": {"type": "object", "additionalProperties": {"type": "string"}}
    }
}


class PhaseEFix:
    def __init__(self, ctx, dry_run=False, run_claude_fn=None):
        self.ctx = ctx
        self.dry_run = dry_run
        self.run_claude = run_claude_fn or _default_run_claude
        self.prompt_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/fix.md"
        )

    def _build_prompt(self, findings, knowledge, source_content, fmt):
        prompt = self.prompt_template
        prompt = prompt.replace("{FINDINGS_JSON}",
                                json.dumps(findings, ensure_ascii=False, indent=2))
        prompt = prompt.replace("{KNOWLEDGE_JSON}",
                                json.dumps(knowledge, ensure_ascii=False, indent=2))
        prompt = prompt.replace("{SOURCE_CONTENT}", source_content)
        prompt = prompt.replace("{FORMAT}", fmt)
        return prompt

    def fix_one(self, file_info) -> dict:
        file_id = file_info["id"]
        findings_path = f"{self.ctx.findings_dir}/{file_id}.json"

        if not os.path.exists(findings_path):
            return {"status": "skip", "id": file_id}

        findings = load_json(findings_path)
        knowledge = load_json(f"{self.ctx.knowledge_dir}/{file_info['output_path']}")
        source = read_file(f"{self.ctx.repo}/{file_info['source_path']}")

        prompt = self._build_prompt(findings, knowledge, source, file_info["format"])

        try:
            result = self.run_claude(prompt, timeout=1200, json_schema=KNOWLEDGE_SCHEMA)
            if result.returncode == 0:
                fixed = json.loads(result.stdout)
                if not self.dry_run:
                    write_json(
                        f"{self.ctx.knowledge_dir}/{file_info['output_path']}", fixed
                    )
                    os.remove(findings_path)
                return {"status": "fixed", "id": file_id}
        except Exception as e:
            return {"status": "error", "id": file_id, "error": str(e)}

        return {"status": "error", "id": file_id}

    def run(self, target_ids) -> dict:
        classified = load_json(self.ctx.classified_list_path)
        target_set = set(target_ids)
        targets = [f for f in classified["files"] if f["id"] in target_set]

        print(f"Fixing {len(targets)} files...")

        with ThreadPoolExecutor(max_workers=self.ctx.concurrency) as executor:
            futures = [executor.submit(self.fix_one, fi) for fi in targets]
            fixed = 0
            for future in as_completed(futures):
                r = future.result()
                if r["status"] == "fixed":
                    fixed += 1
                    print(f"  [FIXED] {r['id']}")
                elif r["status"] == "error":
                    print(f"  [ERROR] {r['id']}: {r.get('error','')}")

        print(f"\n修正完了: {fixed}/{len(targets)}")
        return {"fixed": fixed, "total": len(targets)}
