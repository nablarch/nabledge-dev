"""Phase C: Structure Check

Validate generated knowledge files with structural checks (S1-S15).
Pure Python, no AI needed.
"""

import os
import re
import json
from common import load_json, write_json, read_file
from logger import get_logger

KEBAB_CASE_PATTERN = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
VALID_PROCESSING_PATTERNS = {
    "nablarch-batch", "jakarta-batch", "restful-web-service",
    "http-messaging", "web-application", "mom-messaging", "db-messaging"
}


class PhaseCStructureCheck:
    def __init__(self, ctx):
        self.ctx = ctx
        self.logger = get_logger()

    def count_source_headings(self, content, fmt):
        if fmt == "rst":
            return len(re.findall(r'\n[^\n]+\n-{3,}\n', content))
        elif fmt == "md":
            return len(re.findall(r'^## (?!#)', content, re.MULTILINE))
        elif fmt == "xlsx":
            return 1
        return 0

    def validate_structure(self, json_path, source_path, source_format, file_info=None):
        """Perform structural validation checks (S1-S15). Returns list of error strings.

        Args:
            json_path: Path to knowledge JSON file
            source_path: Path to source file
            source_format: Format of source (rst/md)
            file_info: Optional file info dict with section_range for split files
        """
        errors = []

        # S1: JSON parse
        try:
            knowledge = load_json(json_path)
        except json.JSONDecodeError as e:
            return [f"S1: JSON parse error: {e}"]

        # S2: Required fields
        for field in ["id", "title", "no_knowledge_content", "official_doc_urls", "index", "sections"]:
            if field not in knowledge:
                errors.append(f"S2: Missing required field: {field}")

        if "index" not in knowledge or "sections" not in knowledge:
            return errors

        # S16: no_knowledge_content validation
        if knowledge.get("no_knowledge_content") is True:
            if knowledge.get("index"):
                errors.append("S16: no_knowledge_content=true but index is not empty")
            if knowledge.get("sections"):
                errors.append("S16: no_knowledge_content=true but sections is not empty")
            return errors

        # S17: Empty knowledge guard
        if not knowledge.get("index") and not knowledge.get("sections"):
            errors.append("S17: no_knowledge_content=false but index and sections are both empty")
            return errors

        index_ids = [entry["id"] for entry in knowledge.get("index", [])]
        index_id_set = set(index_ids)
        section_keys = set(knowledge.get("sections", {}).keys())

        # S3, S4: index <-> sections consistency
        for iid in index_id_set - section_keys:
            errors.append(f"S3: index[].id '{iid}' has no corresponding section")
        for sk in section_keys - index_id_set:
            errors.append(f"S4: sections key '{sk}' has no corresponding index entry")

        # S5: Kebab-case
        for entry in knowledge.get("index", []):
            if not KEBAB_CASE_PATTERN.match(entry["id"]):
                errors.append(f"S5: Section ID '{entry['id']}' is not kebab-case")

        # S6: Non-empty hints
        for entry in knowledge.get("index", []):
            if not entry.get("hints"):
                errors.append(f"S6: Section '{entry['id']}' has empty hints")

        # S7: Non-empty sections
        for sid, content in knowledge.get("sections", {}).items():
            if not content.strip():
                errors.append(f"S7: Section '{sid}' has empty content")

        # S8: Filename match
        expected_id = os.path.basename(json_path).replace(".json", "")
        if knowledge.get("id") != expected_id:
            errors.append(f"S8: id '{knowledge.get('id')}' != filename '{expected_id}'")

        # S9: Section count
        if file_info and "section_range" in file_info:
            # For split files, use section_range as expected count
            expected = len(file_info["section_range"]["sections"])
        elif os.path.exists(source_path):
            # For non-split files, count headings in source
            source_content = read_file(source_path)
            expected = self.count_source_headings(source_content, source_format)
        else:
            expected = 0

        actual = len(knowledge.get("sections", {}))
        if expected > 0 and actual < expected:
            errors.append(f"S9: Section count {actual} < source headings {expected}")

        # S11: URL format
        for url in knowledge.get("official_doc_urls", []):
            if not url.startswith("https://"):
                errors.append(f"S11: URL not https: {url}")

        # S13: Minimum section length
        for sid, content in knowledge.get("sections", {}).items():
            stripped = content.strip()
            if len(stripped) < 20 and stripped not in ["なし。", "なし"]:
                errors.append(f"S13: Section '{sid}' too short ({len(stripped)} chars)")

        # S14: Internal reference validation
        internal_ref = re.compile(r'\]\(#([a-z0-9_-]+)\)')
        section_ids = set(knowledge.get("sections", {}).keys())
        for sid, content in knowledge.get("sections", {}).items():
            for m in internal_ref.finditer(content):
                if m.group(1) not in section_ids:
                    errors.append(f"S14: Section '{sid}' refs '#{m.group(1)}' not found")

        # S15: Assets path validation
        json_dir = os.path.dirname(json_path)
        asset_ref = re.compile(r'[!\[]\[?[^\]]*\]\(assets/([^)]+)\)')
        for sid, content in knowledge.get("sections", {}).items():
            for m in asset_ref.finditer(content):
                asset_abs = os.path.join(json_dir, f"assets/{m.group(1)}")
                if not os.path.exists(asset_abs):
                    errors.append(f"S15: Section '{sid}' refs 'assets/{m.group(1)}' not found")

        return errors

    def run(self, target_ids=None) -> dict:
        classified = load_json(self.ctx.classified_list_path)
        files = classified["files"]

        if target_ids is not None:
            target_set = set(target_ids)
            files = [fi for fi in files if fi["id"] in target_set]

        results = {
            "total": 0, "pass": 0, "error": 0,
            "error_count": 0, "errors": {}, "pass_ids": []
        }

        for fi in files:
            json_path = f"{self.ctx.knowledge_cache_dir}/{fi['output_path']}"
            source_path = f"{self.ctx.repo}/{fi['source_path']}"

            if not os.path.exists(json_path):
                continue

            results["total"] += 1
            errs = self.validate_structure(json_path, source_path, fi["format"], fi)

            if errs:
                results["error"] += 1
                results["error_count"] += len(errs)
                results["errors"][fi["id"]] = errs
                self.logger.warning(f"  [FAIL] {fi['id']}: {len(errs)} errors")
            else:
                results["pass"] += 1
                results["pass_ids"].append(fi["id"])

        write_json(self.ctx.structure_check_path, results)

        pass_icon = "✅" if results['pass'] == results['total'] else "⚠️"
        self.logger.info(f"\n   {pass_icon} Structure Check: {results['pass']}/{results['total']} pass, "
                         f"{results['error']} fail ({results['error_count']} errors)")
        return results
