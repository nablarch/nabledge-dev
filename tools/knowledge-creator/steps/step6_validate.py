"""Step 6: Validation

Validate generated knowledge files with structural checks and content validation.
"""

import os
import re
import json
import subprocess
from glob import glob
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from .common import load_json, write_json, read_file, run_claude


# Validation patterns
KEBAB_CASE_PATTERN = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
JAPANESE_PATTERN = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]')
VALID_PROCESSING_PATTERNS = {
    "nablarch-batch", "jakarta-batch", "restful-web-service",
    "http-messaging", "web-application", "mom-messaging", "db-messaging"
}

# Technical term patterns (for S12)
PASCAL_CASE = re.compile(r'^[A-Z][a-zA-Z0-9]*[a-z][a-zA-Z0-9]*$')
PACKAGE_CLASS = re.compile(r'^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)*\.[A-Z][a-zA-Z0-9]+$')
ANNOTATION = re.compile(r'^@[A-Z][a-zA-Z0-9]+$')
EXCEPTION_CLASS = re.compile(r'^[A-Z][a-zA-Z0-9]*Exception$')


class Step6Validate:
    def __init__(self, ctx, dry_run=False):
        self.ctx = ctx
        self.dry_run = dry_run
        self.prompt_template = read_file(f"{ctx.repo}/tools/knowledge-creator/prompts/validate.md")

    def count_source_headings(self, content: str, fmt: str) -> int:
        """Count split-level headings in source"""
        if fmt == "rst":
            # h2: text line followed by --- line
            return len(re.findall(r'\n[^\n]+\n-{3,}\n', content))
        elif fmt == "md":
            # ## but not ###
            return len(re.findall(r'^## (?!#)', content, re.MULTILINE))
        elif fmt == "xlsx":
            return 1
        return 0

    def validate_structure(self, json_path: str, source_path: str, source_format: str) -> list:
        """Perform structural validation checks (S1-S15)"""
        errors = []

        # S1: JSON parse
        try:
            knowledge = load_json(json_path)
        except json.JSONDecodeError as e:
            return [f"S1: JSON parse error: {e}"]

        # S2: Required fields
        for field in ["id", "title", "official_doc_urls", "index", "sections"]:
            if field not in knowledge:
                errors.append(f"S2: Missing required field: {field}")

        # Continue validation even if S2 fails (to collect all errors in one pass)
        if "index" not in knowledge or "sections" not in knowledge:
            # Cannot continue structural validation without these fields
            return errors

        index_ids = [entry["id"] for entry in knowledge.get("index", [])]
        index_id_set = set(index_ids)
        section_keys = set(knowledge.get("sections", {}).keys())

        # S3, S4: index ↔ sections consistency
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
        if knowledge["id"] != expected_id:
            errors.append(f"S8: id '{knowledge['id']}' does not match filename '{expected_id}'")

        # S9: Section count
        if os.path.exists(source_path):
            source_content = read_file(source_path)
            expected_sections = self.count_source_headings(source_content, source_format)
            actual_sections = len(knowledge.get("sections", {}))

            if actual_sections < expected_sections:
                errors.append(
                    f"S9: Section count {actual_sections} < source heading count {expected_sections}"
                )

        # S11: official_doc_urls validation (simplified - check format only)
        for url in knowledge.get("official_doc_urls", []):
            if not url.startswith("https://"):
                errors.append(f"S11: URL does not start with https://: {url}")

        # S13: Minimum section length
        for sid, content in knowledge.get("sections", {}).items():
            stripped = content.strip()
            # Allow very short content if it's just "なし" or similar
            if len(stripped) < 20 and stripped not in ["なし。", "なし"]:
                errors.append(f"S13: Section '{sid}' is too short ({len(stripped)} chars)")

        # S14: Internal reference validation (# prefix)
        section_ids = set(knowledge.get("sections", {}).keys())
        internal_ref_pattern = re.compile(r'\]\(#([a-z0-9_-]+)\)')
        for sid, content in knowledge.get("sections", {}).items():
            for match in internal_ref_pattern.finditer(content):
                ref_id = match.group(1)
                if ref_id not in section_ids:
                    errors.append(
                        f"S14: Section '{sid}' references internal section '#{ref_id}' but not found"
                    )

        # S18: External reference validation (@ prefix) - warning only
        # Note: We don't validate external refs as errors since the referenced files
        # may not be generated yet. This is informational only.

        # S15: Assets path validation
        json_dir = os.path.dirname(json_path)
        asset_pattern = re.compile(r'[!\[]\[?[^\]]*\]\(assets/([^)]+)\)')
        for sid, content in knowledge.get("sections", {}).items():
            for match in asset_pattern.finditer(content):
                asset_rel = f"assets/{match.group(1)}"
                asset_abs = os.path.join(json_dir, asset_rel)
                if not os.path.exists(asset_abs):
                    errors.append(
                        f"S15: Section '{sid}' references '{asset_rel}' but file not found"
                    )

        return errors

    def validate_index_toon(self) -> list:
        """Validate index.toon (S16, S17)"""
        errors = []
        index_path = self.ctx.index_path

        if not os.path.exists(index_path):
            return ["S16: index.toon does not exist"]

        content = read_file(index_path)

        # S16: Count match
        header_match = re.search(r'files\[(\d+),\]', content)
        if not header_match:
            return ["S16: Cannot parse index.toon header"]

        declared_count = int(header_match.group(1))
        data_lines = [
            line for line in content.split('\n')
            if line.startswith('  ') and line.strip() and not line.strip().startswith('#')
        ]
        data_count = len(data_lines)

        json_files = glob(f"{self.ctx.knowledge_dir}/**/*.json", recursive=True)
        # Exclude index.toon if it's accidentally matched
        json_files = [f for f in json_files if not f.endswith("index.toon")]
        json_count = len(json_files)

        if not (declared_count == data_count == json_count):
            errors.append(
                f"S16: Count mismatch: header={declared_count}, "
                f"data_lines={data_count}, json_files={json_count}"
            )

        # S17: processing_patterns values
        for i, line in enumerate(data_lines, 1):
            fields = [f.strip() for f in line.strip().split(', ')]
            if len(fields) >= 4:
                patterns_str = fields[3]
                if patterns_str:
                    for p in patterns_str.split():
                        if p not in VALID_PROCESSING_PATTERNS:
                            errors.append(
                                f"S17: Invalid processing_pattern '{p}' at line {i}"
                            )

        return errors

    def validate_content_with_claude(self, file_info: dict, knowledge: dict, source_content: str) -> dict:
        """Use claude -p for content validation and improvement"""
        file_id = file_info["id"]
        json_path = f"{self.ctx.knowledge_dir}/{file_info['output_path']}"
        log_path = f"{self.ctx.log_dir}/validate/content/{file_id}.json"

        # Check if already validated successfully
        if os.path.exists(log_path):
            cached = load_json(log_path)
            if cached.get("status") == "improved":
                return cached

        prompt = self.prompt_template
        prompt = prompt.replace("{SOURCE_CONTENT}", source_content)
        prompt = prompt.replace("{KNOWLEDGE_JSON}", json.dumps(knowledge, ensure_ascii=False, indent=2))

        try:
            result = run_claude(prompt, timeout=600)
            if result.returncode == 0:
                # Extract improved knowledge JSON from output
                match = re.search(r'```json?\s*\n(.*?)\n```', result.stdout, re.DOTALL)
                if match:
                    improved_knowledge = json.loads(match.group(1))
                else:
                    improved_knowledge = json.loads(result.stdout.strip())

                # Validate that improved knowledge has required structure
                if not all(k in improved_knowledge for k in ["id", "title", "official_doc_urls", "index", "sections"]):
                    error_result = {
                        "file_id": file_id,
                        "status": "error",
                        "reason": "Improved knowledge missing required fields"
                    }
                    if not self.dry_run:
                        write_json(log_path, error_result)
                    return error_result

                # Save improved knowledge file
                if not self.dry_run:
                    write_json(json_path, improved_knowledge)

                # Log success
                success_result = {
                    "file_id": file_id,
                    "status": "improved",
                    "message": "Content validated and improved"
                }
                if not self.dry_run:
                    write_json(log_path, success_result)
                return success_result

        except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            error_result = {
                "file_id": file_id,
                "status": "error",
                "reason": str(e)
            }
            if not self.dry_run:
                write_json(log_path, error_result)
            return error_result

        return {"file_id": file_id, "status": "error", "reason": "Unknown error"}

    def validate_one(self, file_info: dict) -> dict:
        """Validate one knowledge file"""
        file_id = file_info["id"]
        json_path = f"{self.ctx.knowledge_dir}/{file_info['output_path']}"
        source_path = f"{self.ctx.repo}/{file_info['source_path']}"
        struct_log_path = f"{self.ctx.log_dir}/validate/structure/{file_id}.json"

        if not os.path.exists(json_path):
            return {"id": file_id, "status": "skipped", "reason": "knowledge file not found"}

        print(f"  [VAL] {file_id}")

        # Structural validation
        struct_errors = self.validate_structure(json_path, source_path, file_info['format'])
        struct_result = {
            "file_id": file_id,
            "result": "pass" if not struct_errors else "fail",
            "errors": struct_errors
        }

        if not self.dry_run:
            write_json(struct_log_path, struct_result)

        # Content validation (only if structure passed)
        if not struct_errors:
            knowledge = load_json(json_path)
            source_content = read_file(source_path) if os.path.exists(source_path) else ""
            content_result = self.validate_content_with_claude(file_info, knowledge, source_content)
        else:
            content_result = {"status": "skipped", "reason": "structure validation failed"}

        return {
            "id": file_id,
            "status": "validated",
            "structure": struct_result["result"],
            "content": content_result.get("status", "skipped")
        }

    def generate_summary(self):
        """Generate validation summary"""
        log_dir = self.ctx.log_dir

        # Collect generate results
        generate_dir = f"{log_dir}/generate"
        generate_results = []
        if os.path.exists(generate_dir):
            for f in sorted(os.listdir(generate_dir)):
                if f.endswith(".json"):
                    generate_results.append(load_json(os.path.join(generate_dir, f)))

        # Collect validation results
        structure_dir = f"{log_dir}/validate/structure"
        content_dir = f"{log_dir}/validate/content"
        validate_results = []

        if os.path.exists(structure_dir):
            for f in sorted(os.listdir(structure_dir)):
                if f.endswith(".json"):
                    file_id = f.replace(".json", "")
                    s = load_json(os.path.join(structure_dir, f))
                    c_path = os.path.join(content_dir, f)
                    c = load_json(c_path) if os.path.exists(c_path) else None

                    validate_results.append({
                        "id": file_id,
                        "structure": s["result"],
                        "structure_errors": s.get("errors", []),
                        "content": c.get("status", "skipped") if c else "skipped"
                    })

        summary = {
            "version": self.ctx.version,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "generate": {
                "total": len(generate_results),
                "ok": sum(1 for r in generate_results if r.get("status") == "ok"),
                "error": sum(1 for r in generate_results if r.get("status") == "error"),
            },
            "validate": {
                "total": len(validate_results),
                "all_pass": sum(1 for r in validate_results
                              if r["structure"] == "pass" and r["content"] == "improved"),
                "structure_fail": sum(1 for r in validate_results if r["structure"] == "fail"),
                "content_error": sum(1 for r in validate_results if r["content"] == "error"),
            },
            "validate_results": validate_results,
        }

        if not self.dry_run:
            write_json(f"{log_dir}/summary.json", summary)
            print(f"\nSummary written to: {log_dir}/summary.json")

        return summary

    def run(self):
        """Execute Step 6: Validate all knowledge files"""
        classified = load_json(self.ctx.classified_list_path)

        # Validate index.toon first
        print("\nValidating index.toon...")
        index_errors = self.validate_index_toon()
        if index_errors:
            print(f"  index.toon validation FAILED:")
            for error in index_errors:
                print(f"    - {error}")
        else:
            print(f"  index.toon validation PASSED")

        # Validate individual files
        if self.dry_run:
            print(f"\nWould validate {len(classified['files'])} knowledge files")
            return

        print(f"\nValidating {len(classified['files'])} knowledge files...")

        with ThreadPoolExecutor(max_workers=self.ctx.concurrency) as executor:
            futures = []
            for file_info in classified["files"]:
                futures.append(executor.submit(self.validate_one, file_info))

            results = {"validated": 0, "skipped": 0}
            for future in as_completed(futures):
                result = future.result()
                status = result.get("status", "skipped")
                results[status] = results.get(status, 0) + 1

        print(f"\nValidation complete:")
        print(f"  Validated: {results['validated']}")
        print(f"  Skipped: {results['skipped']}")

        # Generate summary
        print("\nGenerating summary...")
        summary = self.generate_summary()

        print(f"\n=== Validation Summary ===")
        print(f"Generation: {summary['generate']['ok']}/{summary['generate']['total']} OK")
        print(f"Validation: {summary['validate']['all_pass']}/{summary['validate']['total']} PASS")
        if summary['validate']['structure_fail'] > 0:
            print(f"  Structure failures: {summary['validate']['structure_fail']}")
        if summary['validate']['content_error'] > 0:
            print(f"  Content errors: {summary['validate']['content_error']}")
