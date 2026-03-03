"""Phase F: Finalize

Build index.toon, generate browsable docs, create summary.
"""

import os
import json
import subprocess
from glob import glob
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from .common import load_json, write_json, read_file, write_file, run_claude as _default_run_claude

CLASSIFY_PATTERNS_SCHEMA = {
    "type": "object",
    "required": ["patterns", "reasoning"],
    "properties": {
        "patterns": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "nablarch-batch", "jakarta-batch", "restful-web-service",
                    "http-messaging", "web-application", "mom-messaging", "db-messaging"
                ]
            }
        },
        "reasoning": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["pattern", "matched", "evidence"],
                "properties": {
                    "pattern": {"type": "string"},
                    "matched": {"type": "boolean"},
                    "evidence": {"type": "string"}
                }
            }
        }
    }
}

VALID_PROCESSING_PATTERNS = {
    "nablarch-batch", "jakarta-batch", "restful-web-service",
    "http-messaging", "web-application", "mom-messaging", "db-messaging"
}


class PhaseFFinalize:
    def __init__(self, ctx, dry_run=False, run_claude_fn=None):
        self.ctx = ctx
        self.dry_run = dry_run
        self.run_claude = run_claude_fn or _default_run_claude
        self.prompt_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/classify_patterns.md"
        )

    def _classify_patterns(self, file_info, knowledge) -> str:
        file_id = file_info["id"]
        log_path = f"{self.ctx.log_dir}/classify-patterns/{file_id}.json"

        if os.path.exists(log_path):
            return load_json(log_path).get("patterns", "")

        prompt = self.prompt_template
        prompt = prompt.replace("{FILE_ID}", file_id)
        prompt = prompt.replace("{TITLE}", knowledge.get("title", ""))
        prompt = prompt.replace("{TYPE}", file_info["type"])
        prompt = prompt.replace("{CATEGORY}", file_info["category"])
        prompt = prompt.replace("{KNOWLEDGE_JSON}",
                                json.dumps(knowledge, ensure_ascii=False, indent=2))

        try:
            result = self.run_claude(prompt, timeout=1200, json_schema=CLASSIFY_PATTERNS_SCHEMA)
            if result.returncode == 0:
                parsed = json.loads(result.stdout)
                patterns = " ".join(parsed.get("patterns", []))
                reasoning = parsed.get("reasoning", [])
                if not self.dry_run:
                    write_json(log_path, {
                        "file_id": file_id, "patterns": patterns, "reasoning": reasoning
                    })
                return patterns
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            pass

        if not self.dry_run:
            write_json(log_path, {"file_id": file_id, "patterns": "", "error": "failed"})
        return ""

    def _build_index_toon(self):
        classified = load_json(self.ctx.classified_list_path)
        entries = []
        to_classify = []

        # Use resolved knowledge directory if Phase G has run
        knowledge_dir = self.ctx.knowledge_resolved_dir if os.path.exists(self.ctx.knowledge_resolved_dir) else self.ctx.knowledge_dir

        for fi in classified["files"]:
            json_path = f"{knowledge_dir}/{fi['output_path']}"
            if not os.path.exists(json_path):
                entries.append({
                    "title": fi["id"], "type": fi["type"], "category": fi["category"],
                    "processing_patterns": "", "path": "not yet created"
                })
                continue

            knowledge = load_json(json_path)
            title = knowledge.get("title", fi["id"])

            if fi["type"] == "processing-pattern":
                patterns = fi["category"]
            else:
                to_classify.append((fi, knowledge))
                patterns = None

            entries.append({
                "title": title, "type": fi["type"], "category": fi["category"],
                "processing_patterns": patterns, "path": fi["output_path"],
                "_fi": fi, "_knowledge": knowledge
            })

        if to_classify and not self.dry_run:
            print(f"  Classifying {len(to_classify)} files...")
            with ThreadPoolExecutor(max_workers=self.ctx.concurrency) as executor:
                futures = {}
                for fi, knowledge in to_classify:
                    future = executor.submit(self._classify_patterns, fi, knowledge)
                    futures[future] = fi["id"]

                for future in as_completed(futures):
                    fid = futures[future]
                    patterns = future.result()
                    for e in entries:
                        if e.get("_fi", {}).get("id") == fid:
                            e["processing_patterns"] = patterns
                            break

        # Clean up temp fields and write
        for e in entries:
            e.pop("_fi", None)
            e.pop("_knowledge", None)
            if e["processing_patterns"] is None:
                e["processing_patterns"] = ""

        lines = [f"# Nabledge-{self.ctx.version} Knowledge Index", ""]
        lines.append(f"files[{len(entries)},]{{title,type,category,processing_patterns,path}}:")
        for e in entries:
            title = e["title"].replace(",", "、")
            fields = [title, e["type"], e["category"], e["processing_patterns"], e["path"]]
            lines.append(f"  {', '.join(fields)}")
        lines.append("")

        if not self.dry_run:
            write_file(self.ctx.index_path, '\n'.join(lines))
            print(f"  Wrote: {self.ctx.index_path} ({len(entries)} entries)")

    def _generate_docs(self):
        classified = load_json(self.ctx.classified_list_path)
        generated = 0

        # Use resolved knowledge directory if Phase G has run
        knowledge_dir = self.ctx.knowledge_resolved_dir if os.path.exists(self.ctx.knowledge_resolved_dir) else self.ctx.knowledge_dir

        for fi in classified["files"]:
            json_path = f"{knowledge_dir}/{fi['output_path']}"
            if not os.path.exists(json_path):
                continue

            knowledge = load_json(json_path)
            md_lines = [f"# {knowledge['title']}", ""]
            for entry in knowledge.get("index", []):
                sid = entry["id"]
                md_lines.append(f"## {entry['title']}")
                md_lines.append("")
                md_lines.append(knowledge.get("sections", {}).get(sid, ""))
                md_lines.append("")

            md_path = f"{self.ctx.docs_dir}/{fi['type']}/{fi['category']}/{fi['id']}.md"
            if not self.dry_run:
                write_file(md_path, "\n".join(md_lines))
            generated += 1

        print(f"  Generated {generated} docs")

    def _generate_summary(self):
        log_dir = self.ctx.log_dir

        gen_dir = f"{log_dir}/generate"
        gen_results = []
        if os.path.exists(gen_dir):
            for f in sorted(os.listdir(gen_dir)):
                fp = os.path.join(gen_dir, f)
                if f.endswith(".json") and os.path.isfile(fp):
                    gen_results.append(load_json(fp))

        findings_dir = self.ctx.findings_dir
        total_findings = 0
        files_with_issues = 0
        if os.path.exists(findings_dir):
            for f in sorted(os.listdir(findings_dir)):
                if f.endswith(".json"):
                    data = load_json(os.path.join(findings_dir, f))
                    n = len(data.get("findings", []))
                    total_findings += n
                    if n > 0:
                        files_with_issues += 1

        summary = {
            "version": self.ctx.version,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "generate": {
                "total": len(gen_results),
                "ok": sum(1 for r in gen_results if r.get("status") == "ok"),
                "error": sum(1 for r in gen_results if r.get("status") == "error"),
            },
            "content_check": {
                "files_with_issues": files_with_issues,
                "total_findings": total_findings,
            },
        }

        if not self.dry_run:
            write_json(f"{log_dir}/summary.json", summary)
            print(f"  Summary: {log_dir}/summary.json")

    def run(self):
        print("  Building index.toon...")
        self._build_index_toon()

        print("  Generating docs...")
        self._generate_docs()

        print("  Generating summary...")
        self._generate_summary()
