"""Phase D: Content Check

Compare knowledge files against source files to identify issues.
Does NOT fix anything - only reports findings.
"""

import os
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from common import load_json, write_json, read_file, run_claude as _default_run_claude, aggregate_cc_metrics, count_source_headings
from logger import get_logger

_GENERIC_TERMS = frozenset([
    "String", "Object", "List", "Map", "Set", "Integer", "Long", "Boolean",
    "Double", "Float", "Short", "Byte", "Char", "Number", "Class", "Type",
    "Array", "Collection", "Iterator", "Optional", "Stream", "Void",
    "Override", "SuppressWarnings", "Deprecated", "FunctionalInterface",
    "Java", "Excel", "XML", "SQL", "HTTP", "HTTPS",
    "Returns", "Throws", "Since", "Note", "See", "True", "False", "None",
])

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
                        "enum": ["omission", "fabrication", "hints_missing", "section_issue", "no_knowledge_content_invalid"]
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
        self.logger = get_logger()
        self.prompt_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/content_check.md"
        )

    def _extract_important_terms(self, content):
        """Extract PascalCase class names, @Annotations, and XxxException names from section content."""
        content_no_urls = re.sub(r'https?://\S+', '', content)
        terms = set()
        for m in re.finditer(r'@[A-Z][a-zA-Z0-9]+', content_no_urls):
            terms.add(m.group())
        # Require 4+ chars to avoid short acronyms/abbreviations being flagged.
        # Skip if @-prefixed form was already captured (avoids double-listing same concept).
        for m in re.finditer(r'\b[A-Z][a-zA-Z0-9]{3,}\b', content_no_urls):
            name = m.group()
            if name not in _GENERIC_TERMS and f'@{name}' not in terms:
                terms.add(name)
        return terms

    def _compute_content_warnings(self, knowledge, source_content, source_format, file_info):
        """Run S6/S7/S9/S13 content quality checks. Returns list of warning strings."""
        warnings = []

        # S6: Non-empty hints and complete hints
        for entry in knowledge.get("index", []):
            section_id = entry["id"]
            hints = entry.get("hints", [])
            if not hints:
                warnings.append(f"S6: Section '{section_id}' has empty hints")
                continue
            section_content = knowledge.get("sections", {}).get(section_id, "")
            if section_content:
                important_terms = self._extract_important_terms(section_content)
                hint_base_names = {h.lstrip('@') for h in hints}
                missing = sorted(t for t in important_terms if t.lstrip('@') not in hint_base_names)
                if missing:
                    warnings.append(f"S6: Section '{section_id}' hints missing terms: {missing}")

        # S7: Non-empty sections
        for sid, content in knowledge.get("sections", {}).items():
            if not content.strip():
                warnings.append(f"S7: Section '{sid}' has empty content")

        # S9: Section count vs source headings
        if file_info and "section_range" in file_info:
            expected = len(file_info["section_range"]["sections"])
        else:
            expected = count_source_headings(source_content, source_format)

        actual = len(knowledge.get("sections", {}))
        if expected > 0 and actual < expected:
            warnings.append(f"S9: Section count {actual} < source headings {expected}")

        # S13: Minimum section length
        for sid, content in knowledge.get("sections", {}).items():
            stripped = content.strip()
            if len(stripped) < 20 and stripped not in ["なし。", "なし"]:
                warnings.append(f"S13: Section '{sid}' too short ({len(stripped)} chars)")

        return warnings

    def _build_prompt(self, file_info, knowledge, source_content, warnings=None):
        prompt = self.prompt_template
        prompt = prompt.replace("{SOURCE_PATH}", file_info["source_path"])
        prompt = prompt.replace("{FORMAT}", file_info["format"])
        prompt = prompt.replace("{SOURCE_CONTENT}", source_content)
        prompt = prompt.replace("{FILE_ID}", file_info["id"])
        prompt = prompt.replace("{KNOWLEDGE_JSON}",
                                json.dumps(knowledge, ensure_ascii=False, indent=2))
        if warnings:
            prompt = prompt.replace("{CONTENT_WARNINGS}",
                                    "\n".join(f"- {w}" for w in warnings))
        else:
            prompt = prompt.replace("{CONTENT_WARNINGS}", "なし")
        return prompt

    def check_one(self, file_info) -> dict:
        file_id = file_info["id"]
        findings_path = f"{self.ctx.findings_dir}/{file_id}.json"

        self.logger = get_logger()
        if os.path.exists(findings_path):
            return load_json(findings_path)

        json_path = f"{self.ctx.knowledge_cache_dir}/{file_info['output_path']}"
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

        warnings = self._compute_content_warnings(knowledge, source, file_info["format"], file_info)
        prompt = self._build_prompt(file_info, knowledge, source, warnings=warnings)

        try:
            result = self.run_claude(
                prompt=prompt,
                json_schema=FINDINGS_SCHEMA,
                log_dir=self.ctx.phase_d_executions_dir,
                file_id=file_id,
                verbose=self.ctx.verbose
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
            self.logger.info(f"Would check {len(files)} files")
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
                    self.logger.info(f"  [ISSUE] {r['file_id']}: {len(r['findings'])} findings")
                elif r.get("status") == "clean":
                    clean += 1

        status_icon = "✅" if len(issue_ids) == 0 else "⚠️"
        self.logger.info(f"\n   {status_icon} Content Check: {clean} clean, {len(issue_ids)} with issues")
        metrics = aggregate_cc_metrics(self.ctx.phase_d_executions_dir)
        self.logger.info(f"   📊 Metrics: cost=${metrics['cost_usd']:.3f} avg_turns={metrics.get('avg_turns', 'N/A')}")
        return {
            "issues_count":   len(issue_ids),
            "issue_file_ids": issue_ids,
            "clean":          clean,
            "metrics":        metrics,
        }
