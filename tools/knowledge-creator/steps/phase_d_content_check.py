"""Phase D: Content Check

Compare knowledge files against source files to identify issues.
Does NOT fix anything - only reports findings.
"""

import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from .common import load_json, write_json, read_file, run_claude as _default_run_claude

FINDINGS_SCHEMA = {
    "type": "object",
    "required": ["file_id", "status", "findings"],
    "properties": {
        "file_id": {"type": "string"},
        "status": {"type": "string", "enum": ["clean", "has_issues"]},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["category", "severity", "location", "description"],
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["omission", "fabrication", "hints_missing", "section_issue"]
                    },
                    "severity": {"type": "string", "enum": ["critical", "minor"]},
                    "location": {"type": "string"},
                    "description": {"type": "string"},
                    "source_evidence": {"type": "string"}
                }
            }
        }
    }
}


class PhaseDContentCheck:
    def __init__(self, ctx, dry_run=False, run_claude_fn=None):
        self.ctx = ctx
        self.dry_run = dry_run
        self.run_claude = run_claude_fn or _default_run_claude
        self.prompt_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/content_check.md"
        )

    def _build_prompt(self, file_info, knowledge, source_content):
        prompt = self.prompt_template
        prompt = prompt.replace("{SOURCE_PATH}", file_info["source_path"])
        prompt = prompt.replace("{FORMAT}", file_info["format"])
        prompt = prompt.replace("{SOURCE_CONTENT}", source_content)
        prompt = prompt.replace("{FILE_ID}", file_info["id"])
        prompt = prompt.replace("{KNOWLEDGE_JSON}",
                                json.dumps(knowledge, ensure_ascii=False, indent=2))
        return prompt

    def check_one(self, file_info) -> dict:
        file_id = file_info["id"]
        findings_path = f"{self.ctx.findings_dir}/{file_id}.json"

        if os.path.exists(findings_path):
            return load_json(findings_path)

        json_path = f"{self.ctx.knowledge_dir}/{file_info['output_path']}"
        source_path = f"{self.ctx.repo}/{file_info['source_path']}"

        if not os.path.exists(json_path) or not os.path.exists(source_path):
            return {"file_id": file_id, "status": "error", "findings": []}

        knowledge = load_json(json_path)
        source = read_file(source_path)

        # For split files, extract only the section range
        if "section_range" in file_info:
            lines = source.splitlines()
            sr = file_info["section_range"]
            source = "\n".join(lines[sr["start_line"]:sr["end_line"]])

        prompt = self._build_prompt(file_info, knowledge, source)

        try:
            result = self.run_claude(
                prompt=prompt,
                json_schema=FINDINGS_SCHEMA,
                log_dir=self.ctx.phase_d_executions_dir,
                file_id=file_id
            )
            if result.returncode == 0:
                findings = json.loads(result.stdout)
                if not self.dry_run:
                    write_json(findings_path, findings)
                return findings
        except Exception:
            pass

        return {"file_id": file_id, "status": "error", "findings": []}

    def run(self, target_ids=None) -> dict:
        classified = load_json(self.ctx.classified_list_path)
        files = classified["files"]

        if target_ids is not None:
            target_set = set(target_ids)
            files = [f for f in files if f["id"] in target_set]

        if self.dry_run:
            print(f"Would check {len(files)} files")
            return {"issues_count": 0, "issue_file_ids": []}

        os.makedirs(self.ctx.findings_dir, exist_ok=True)

        with ThreadPoolExecutor(max_workers=self.ctx.concurrency) as executor:
            futures = {executor.submit(self.check_one, fi): fi["id"] for fi in files}
            issue_ids = []
            clean = 0
            for future in as_completed(futures):
                r = future.result()
                if r.get("status") == "has_issues":
                    issue_ids.append(r["file_id"])
                    print(f"  [ISSUE] {r['file_id']}: {len(r['findings'])} findings")
                elif r.get("status") == "clean":
                    clean += 1

        status_icon = "✅" if len(issue_ids) == 0 else "⚠️"
        print(f"\n   {status_icon} Content Check: {clean} clean, {len(issue_ids)} with issues")
        return {"issues_count": len(issue_ids), "issue_file_ids": issue_ids}
