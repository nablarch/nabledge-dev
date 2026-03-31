"""Phase E: Fix

Apply fixes to knowledge files based on validation findings.
"""

import os
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from common import load_json, write_json, read_file, run_claude as _default_run_claude, aggregate_cc_metrics
from logger import get_logger


def _extract_allowed_sections(findings):
    """Return (section_ids, is_full_rebuild) from findings list.

    section_ids: set of section IDs (e.g. {'s1', 's3'}) that Phase E is
    allowed to modify.  Derived from the 'location' field of each finding.

    is_full_rebuild: True when a no_knowledge_content_invalid finding is
    present, meaning the entire file may be restructured.
    """
    section_ids = set()
    is_full_rebuild = False

    for f in findings:
        cat = f.get("category", "")
        if cat == "no_knowledge_content_invalid":
            is_full_rebuild = True
            break
        loc = f.get("location", "")
        # Extract sN identifiers from the location string
        for m in re.findall(r'\bs(\d+)\b', loc):
            section_ids.add(f"s{m}")

    return section_ids, is_full_rebuild


def _apply_diff_guard(input_knowledge, output_knowledge, allowed_sections,
                      is_full_rebuild=False):
    """Revert any changes outside the scope of the fix instruction.

    For sections not listed in allowed_sections, the output is overwritten
    with the input value — making collateral damage physically impossible.

    Index hints follow the same rule: only entries whose section ID is in
    allowed_sections may change.

    Top-level metadata (id, title, official_doc_urls, no_knowledge_content)
    is always restored from the input unless is_full_rebuild is True.

    Returns the guarded knowledge object.
    """
    if is_full_rebuild:
        # no_knowledge_content_invalid: allow the LLM to fully restructure
        return output_knowledge

    guarded = dict(output_knowledge)

    # Protect metadata
    for field in ("id", "title", "no_knowledge_content", "official_doc_urls"):
        if field in input_knowledge:
            guarded[field] = input_knowledge[field]

    # Protect sections not in scope
    input_sections = input_knowledge.get("sections", {})
    output_sections = dict(output_knowledge.get("sections", {}))

    # Revert out-of-scope sections to input values
    for sid, content in input_sections.items():
        if sid not in allowed_sections:
            output_sections[sid] = content

    # Remove any new sections added by the LLM that are not in scope
    for sid in list(output_sections.keys()):
        if sid not in input_sections and sid not in allowed_sections:
            del output_sections[sid]

    guarded["sections"] = output_sections

    # Protect index hints for sections not in scope
    input_index = {entry["id"]: entry for entry in input_knowledge.get("index", [])}
    output_index = list(output_knowledge.get("index", []))
    guarded_index = []

    seen = set()
    for entry in output_index:
        sid = entry.get("id")
        seen.add(sid)
        if sid not in allowed_sections and sid in input_index:
            guarded_index.append(dict(input_index[sid]))
        else:
            guarded_index.append(entry)

    # Restore index entries removed by the LLM that are not in scope
    for sid, entry in input_index.items():
        if sid not in allowed_sections and sid not in seen:
            guarded_index.append(dict(entry))

    guarded["index"] = guarded_index
    return guarded

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


class PhaseEFix:
    def __init__(self, ctx, run_claude_fn=None):
        self.ctx = ctx
        self.run_claude = run_claude_fn or _default_run_claude
        self.logger = get_logger()
        self.round_num = 1  # default; overridden by run()
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
        findings_path = f"{self.ctx.findings_dir}/{file_id}_r{self.round_num}.json"

        self.logger = get_logger()
        if not os.path.exists(findings_path):
            return {"status": "skip", "id": file_id}

        findings = load_json(findings_path)
        knowledge = load_json(f"{self.ctx.knowledge_cache_dir}/{file_info['output_path']}")
        source = read_file(f"{self.ctx.repo}/{file_info['source_path']}")

        # For split files, extract only the section range
        if "section_range" in file_info:
            lines = source.splitlines()
            sr = file_info["section_range"]
            source = "\n".join(lines[sr["start_line"]:sr["end_line"]])

        prompt = self._build_prompt(findings, knowledge, source, file_info["format"])

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

                # Diff guard: revert changes outside the scope of findings
                finding_list = findings.get("findings", [])
                allowed_sections, is_full_rebuild = _extract_allowed_sections(finding_list)
                fixed = _apply_diff_guard(knowledge, fixed, allowed_sections,
                                          is_full_rebuild=is_full_rebuild)

                # Reject if no authorized sections actually changed
                if not is_full_rebuild:
                    input_sections = knowledge.get("sections", {})
                    changed = sum(
                        1 for sid in allowed_sections
                        if input_sections.get(sid) != fixed.get("sections", {}).get(sid)
                    )
                    if changed == 0:
                        self.logger.warning(f"    WARNING: {file_id}: diff guard found no changes in allowed sections")
                        return {"status": "error", "id": file_id,
                                "error": "Diff guard: no changes in allowed sections"}

                write_json(
                    f"{self.ctx.knowledge_cache_dir}/{file_info['output_path']}", fixed
                )
                return {"status": "fixed", "id": file_id}
        except Exception as e:
            return {"status": "error", "id": file_id, "error": str(e)}

        return {"status": "error", "id": file_id}

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
