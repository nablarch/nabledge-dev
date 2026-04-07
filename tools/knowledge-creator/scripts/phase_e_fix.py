"""Phase E: Fix

Apply fixes to knowledge files based on validation findings.
Per-section fix strategy: only pass target section to LLM, avoid mutations to other sections.
"""

import os
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from common import load_json, write_json, read_file, run_claude as _default_run_claude, aggregate_cc_metrics
from logger import get_logger

KNOWLEDGE_SCHEMA = {
    "type": "object",
    "required": ["id", "title", "no_knowledge_content", "official_doc_urls", "index", "sections"],
    "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "no_knowledge_content": {"type": "boolean"},
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

SECTION_FIX_SCHEMA = {
    "type": "object",
    "required": ["section_text"],
    "properties": {
        "section_text": {"type": "string"}
    }
}

HINTS_FIX_SCHEMA = {
    "type": "object",
    "required": ["hints"],
    "properties": {
        "hints": {"type": "array", "items": {"type": "string"}}
    }
}


def _normalize_location(location):
    """Normalize section location: uppercase and dotted prefixes to lowercase."""
    if isinstance(location, str):
        # Remove 'sections.' prefix if present
        if location.lower().startswith("sections."):
            location = location[9:]
        return location.lower()
    return location


def _group_findings_by_section(findings):
    """Group findings by section ID.

    Returns:
        (section_groups, structural_findings)
        - section_groups: dict of section_id -> list of findings
        - structural_findings: list of findings that affect entire file
    """
    section_groups = {}
    structural_findings = []

    structural_categories = {"section_issue", "no_knowledge_content_invalid"}

    for finding in findings:
        category = finding.get("category", "")
        location = finding.get("location", "")

        if category in structural_categories:
            structural_findings.append(finding)
        else:
            section_id = _normalize_location(location)
            if section_id not in section_groups:
                section_groups[section_id] = []
            section_groups[section_id].append(finding)

    return section_groups, structural_findings


class PhaseEFix:
    def __init__(self, ctx, run_claude_fn=None):
        self.ctx = ctx
        self.run_claude = run_claude_fn or _default_run_claude
        self.logger = get_logger()
        self.round_num = 1  # default; overridden by run()
        # Load prompt templates
        self.full_fix_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/fix.md"
        )
        self.section_fix_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/section_fix.md"
        )
        self.hints_fix_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/hints_fix.md"
        )

    def _build_full_prompt(self, findings, knowledge, source_content, fmt):
        """Build full knowledge fix prompt (for structural findings)."""
        prompt = self.full_fix_template
        prompt = prompt.replace("{FINDINGS_JSON}",
                                json.dumps(findings, ensure_ascii=False, indent=2))
        prompt = prompt.replace("{KNOWLEDGE_JSON}",
                                json.dumps(knowledge, ensure_ascii=False, indent=2))
        prompt = prompt.replace("{SOURCE_CONTENT}", source_content)
        prompt = prompt.replace("{FORMAT}", fmt)
        return prompt

    def _build_section_fix_prompt(self, findings, section_text, source_content, fmt):
        """Build per-section fix prompt for omission/fabrication findings."""
        prompt = self.section_fix_template
        prompt = prompt.replace("{FINDINGS_JSON}",
                                json.dumps(findings, ensure_ascii=False, indent=2))
        prompt = prompt.replace("{SECTION_TEXT}", section_text)
        prompt = prompt.replace("{SOURCE_CONTENT}", source_content)
        prompt = prompt.replace("{FORMAT}", fmt)
        return prompt

    def _build_hints_fix_prompt(self, findings, section_text, hints):
        """Build hints fix prompt for hints_missing findings."""
        prompt = self.hints_fix_template
        prompt = prompt.replace("{FINDINGS_JSON}",
                                json.dumps(findings, ensure_ascii=False, indent=2))
        prompt = prompt.replace("{SECTION_TEXT}", section_text)
        prompt = prompt.replace("{CURRENT_HINTS}",
                                json.dumps(hints, ensure_ascii=False, indent=2))
        return prompt

    def fix_one(self, file_info) -> dict:
        file_id = file_info["id"]
        findings_path = f"{self.ctx.findings_dir}/{file_id}_r{self.round_num}.json"

        self.logger = get_logger()
        if not os.path.exists(findings_path):
            return {"status": "skip", "id": file_id}

        findings_data = load_json(findings_path)
        findings = findings_data.get("findings", [])
        knowledge = load_json(f"{self.ctx.knowledge_cache_dir}/{file_info['output_path']}")
        source = read_file(f"{self.ctx.repo}/{file_info['source_path']}")

        # For split files, extract only the section range
        if "section_range" in file_info:
            lines = source.splitlines()
            sr = file_info["section_range"]
            source = "\n".join(lines[sr["start_line"]:sr["end_line"]])

        # Group findings by section
        section_groups, structural_findings = _group_findings_by_section(findings)

        # If there are structural findings, use full knowledge fix (existing behavior)
        if structural_findings:
            prompt = self._build_full_prompt(findings, knowledge, source, file_info["format"])
            try:
                result = self.run_claude(
                    prompt=prompt,
                    json_schema=KNOWLEDGE_SCHEMA,
                    log_dir=self.ctx.phase_e_executions_dir,
                    file_id=file_id,
                )
                if result.returncode == 0:
                    fixed = json.loads(result.stdout)

                    # Guard: output must not shrink drastically
                    input_sec_chars = sum(len(v) for v in knowledge.get("sections", {}).values())
                    output_sec_chars = sum(len(v) for v in fixed.get("sections", {}).values())
                    if input_sec_chars > 0 and output_sec_chars < input_sec_chars * 0.5:
                        self.logger.warning(f"    WARNING: {file_id}: output shrunk to {output_sec_chars/input_sec_chars:.0%} "
                              f"({output_sec_chars:,} / {input_sec_chars:,} chars) - rejecting fix")
                        return {"status": "error", "id": file_id,
                                "error": f"Output too small: {output_sec_chars}/{input_sec_chars} chars"}

                    write_json(
                        f"{self.ctx.knowledge_cache_dir}/{file_info['output_path']}", fixed
                    )
                    return {"status": "fixed", "id": file_id}
            except Exception as e:
                return {"status": "error", "id": file_id, "error": str(e)}

            return {"status": "error", "id": file_id}

        # Per-section fix: process each section independently
        try:
            for section_id, section_findings in section_groups.items():
                section_text = knowledge["sections"].get(section_id, "")
                if not section_text:
                    continue

                # Separate hints_missing from other findings
                hints_findings = [f for f in section_findings if f.get("category") == "hints_missing"]
                content_findings = [f for f in section_findings if f.get("category") != "hints_missing"]

                # Fix content (omission/fabrication)
                if content_findings:
                    prompt = self._build_section_fix_prompt(
                        content_findings, section_text, source, file_info["format"]
                    )
                    result = self.run_claude(
                        prompt=prompt,
                        json_schema=SECTION_FIX_SCHEMA,
                        log_dir=self.ctx.phase_e_executions_dir,
                        file_id=f"{file_id}_s{section_id}",
                    )
                    if result.returncode == 0:
                        fixed_section = json.loads(result.stdout)
                        knowledge["sections"][section_id] = fixed_section.get("section_text", section_text)
                    else:
                        return {"status": "error", "id": file_id,
                                "error": f"Failed to fix section {section_id}"}

                # Fix hints
                if hints_findings:
                    # Find index entry for this section
                    index_entry = next((e for e in knowledge["index"] if e["id"] == section_id), None)
                    if index_entry:
                        current_hints = index_entry.get("hints", [])
                        prompt = self._build_hints_fix_prompt(
                            hints_findings, section_text, current_hints
                        )
                        result = self.run_claude(
                            prompt=prompt,
                            json_schema=HINTS_FIX_SCHEMA,
                            log_dir=self.ctx.phase_e_executions_dir,
                            file_id=f"{file_id}_hints_{section_id}",
                        )
                        if result.returncode == 0:
                            fixed_hints = json.loads(result.stdout)
                            index_entry["hints"] = fixed_hints.get("hints", current_hints)
                        else:
                            return {"status": "error", "id": file_id,
                                    "error": f"Failed to fix hints for section {section_id}"}

            # Save fixed knowledge
            write_json(
                f"{self.ctx.knowledge_cache_dir}/{file_info['output_path']}", knowledge
            )
            return {"status": "fixed", "id": file_id}

        except Exception as e:
            return {"status": "error", "id": file_id, "error": str(e)}

    def run(self, target_ids, round_num=1) -> dict:
        classified = load_json(self.ctx.classified_list_path)
        target_set = set(target_ids)
        targets = [f for f in classified["files"] if f["id"] in target_set]

        self.round_num = round_num
        self.logger.info(f"Fixing {len(targets)} files...")

        with ThreadPoolExecutor(max_workers=self.ctx.concurrency) as executor:
            futures = [executor.submit(self.fix_one, fi) for fi in targets]
            fixed = 0
            for future in as_completed(futures):
                r = future.result()
                if r["status"] == "fixed":
                    fixed += 1
                    self.logger.info(f"  [FIXED] {r['id']}")
                elif r["status"] == "error":
                    self.logger.error(f"  [ERROR] {r['id']}: {r.get('error','')}")

        self.logger.info(f"\n   ✅ 修正完了: {fixed}/{len(targets)}")
        metrics = aggregate_cc_metrics(self.ctx.phase_e_executions_dir)
        self.logger.info(f"   📊 Metrics: cost=${metrics['cost_usd']:.3f}")
        return {
            "fixed":   fixed,
            "error":   len(targets) - fixed,
            "total":   len(targets),
            "metrics": metrics,
        }
