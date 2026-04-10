"""Phase D: Content Check

Compare knowledge files against source files to identify issues.
Does NOT fix anything - only reports findings.
"""

import os
import json
import re
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from common import load_json, write_json, read_file, run_claude as _default_run_claude, aggregate_cc_metrics, count_source_headings
from logger import get_logger

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
    def __init__(self, ctx, run_claude_fn=None):
        self.ctx = ctx
        self.run_claude = run_claude_fn or _default_run_claude
        self.logger = get_logger()
        self.round_num = 1  # default; overridden by run()
        self.prompt_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/content_check.md"
        )

    def _compute_content_warnings(self, knowledge, source_content, source_format, file_info):
        """Run S6/S7/S9/S13 content quality checks. Returns list of warning strings."""
        warnings = []

        # S6: Non-empty hints
        for entry in knowledge.get("index", []):
            if not entry.get("hints"):
                warnings.append(f"S6: Section '{entry['id']}' has empty hints")

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

    def _compute_section_hash(self, section_text):
        """Compute hash of section text for change detection."""
        return hashlib.sha256(section_text.encode()).hexdigest()

    @staticmethod
    def _normalize_finding_location(location):
        """Extract section ID from location string for consistent key matching."""
        if isinstance(location, str):
            match = re.search(r'\bs(\d+)\b', location, re.IGNORECASE)
            if match:
                return f"s{match.group(1)}"
            return location.lower()
        return location

    def _load_prior_findings(self, file_id):
        """Load findings from previous round if available."""
        if self.round_num <= 1:
            return None
        prior_path = f"{self.ctx.findings_dir}/{file_id}_r{self.round_num - 1}.json"
        if os.path.exists(prior_path):
            return load_json(prior_path)
        return None

    def _lock_severity(self, findings, file_id, knowledge):
        """Lock severity for findings when knowledge content unchanged since prior round.

        For each finding, if the section was unchanged (hash matches), keep severity
        from prior round. If section was modified (Phase E changed it), accept new severity.
        """
        prior = self._load_prior_findings(file_id)
        if not prior or self.round_num <= 1:
            for finding in findings:
                location = finding.get("location", "")
                section_id = self._normalize_finding_location(location)
                section_text = knowledge.get("sections", {}).get(section_id, "")
                finding["_section_hash"] = self._compute_section_hash(section_text)
            return findings

        # Build map of (norm_location, category) -> prior_severity
        prior_findings = prior.get("findings", [])
        prior_map = {}
        for pf in prior_findings:
            norm_loc = self._normalize_finding_location(pf.get("location", ""))
            key = (norm_loc, pf.get("category", ""))
            prior_map[key] = pf.get("severity", "")

        # Check if sections changed and lock severity if unchanged
        for finding in findings:
            location = finding.get("location", "")
            norm_loc = self._normalize_finding_location(location)
            category = finding.get("category", "")
            key = (norm_loc, category)

            # Only apply lock to non-structural findings
            structural = {"section_issue", "no_knowledge_content_invalid"}
            if category in structural:
                continue

            section_id = norm_loc

            if key in prior_map:
                # Get section from knowledge
                section_text = knowledge.get("sections", {}).get(section_id, "")
                current_hash = self._compute_section_hash(section_text)

                # Try to find prior hash from prior findings
                prior_hash = next(
                    (pf.get("_section_hash", "") for pf in prior_findings
                     if self._normalize_finding_location(pf.get("location", "")) == norm_loc
                     and pf.get("category", "") == category),
                    None
                )

                # If hashes match (unchanged), lock severity
                if prior_hash is not None and prior_hash and current_hash == prior_hash:
                    old_severity = finding.get("severity", "")
                    new_severity = prior_map[key]
                    if old_severity != new_severity:
                        self.logger.warning(
                            f"[SEVERITY LOCK] {file_id} {location}/{category}: "
                            f"locked {old_severity} -> {new_severity} (content unchanged)"
                        )
                        finding["severity"] = new_severity

            # Always set _section_hash for next round comparison
            section_id = norm_loc
            section_text = knowledge.get("sections", {}).get(section_id, "")
            finding["_section_hash"] = self._compute_section_hash(section_text)

        return findings

    def _build_prompt(self, file_info, knowledge, source_content, warnings=None, prior_findings=None):
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

        # Add prior findings section if available
        if prior_findings and self.round_num > 1:
            prior_text = "### Prior Round Findings (For reference, do NOT re-report unless still applicable)\n\n"
            for finding in prior_findings:
                prior_text += f"- {finding.get('category', '')}: {finding.get('location', '')} — {finding.get('description', '')}\n"
            prompt = prompt.replace("{PRIOR_FINDINGS}",
                                    prior_text)
        else:
            prompt = prompt.replace("{PRIOR_FINDINGS}", "(none)")
        return prompt

    def check_one(self, file_info) -> dict:
        file_id = file_info["id"]
        findings_path = f"{self.ctx.findings_dir}/{file_id}_r{self.round_num}.json"

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

        # Load prior findings for context (if round > 1)
        prior = self._load_prior_findings(file_id)
        prior_findings = prior.get("findings", []) if prior else None

        prompt = self._build_prompt(file_info, knowledge, source, warnings=warnings, prior_findings=prior_findings)

        try:
            result = self.run_claude(
                prompt=prompt,
                json_schema=FINDINGS_SCHEMA,
                log_dir=self.ctx.phase_d_executions_dir,
                file_id=file_id,
            )
            if result.returncode == 0:
                findings = json.loads(result.stdout)

                # Apply severity lock for findings when knowledge unchanged
                findings_list = findings.get("findings", [])
                findings_list = self._lock_severity(findings_list, file_id, knowledge)
                findings["findings"] = findings_list

                write_json(findings_path, findings)
                return findings
        except Exception:
            pass

        return {"file_id": file_id, "status": "error", "findings": []}

    def run(self, target_ids=None, round_num=1) -> dict:
        classified = load_json(self.ctx.classified_list_path)
        files = classified["files"]

        if target_ids is not None:
            target_set = set(target_ids)
            files = [f for f in files if f["id"] in target_set]

        self.round_num = round_num
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
