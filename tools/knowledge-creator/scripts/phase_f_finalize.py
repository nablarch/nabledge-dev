"""Phase F: Finalize

Build index.toon, generate browsable docs, create summary.
"""

import os
import re
import json
import subprocess
from glob import glob
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from common import load_json, write_json, read_file, write_file, run_claude as _default_run_claude
from logger import get_logger

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
        self.logger = get_logger()
        self.prompt_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/classify_patterns.md"
        )
        # Cache compiled regex patterns per file_id (performance optimization)
        self._pattern_cache = {}
        self._pp_cache = self._load_pp_cache()  # processing_patterns cache

    def _load_pp_cache(self):
        """Load processing_patterns from catalog.json files[]."""
        cache = {}
        catalog_path = self.ctx.classified_list_path
        if os.path.exists(catalog_path):
            catalog = load_json(catalog_path)
            for fi in catalog.get("files", []):
                pp = fi.get("processing_patterns")
                if pp is not None and pp != []:
                    cache[fi["id"]] = " ".join(pp) if isinstance(pp, list) else pp
        return cache

    def _save_pp_to_catalog(self, pp_map):
        """Write processing_patterns back to catalog.json files[]."""
        catalog_path = self.ctx.classified_list_path
        if not os.path.exists(catalog_path):
            return
        catalog = load_json(catalog_path)
        for fi in catalog.get("files", []):
            fid = fi.get("id", "")
            if fid in pp_map:
                pp = pp_map[fid]
                fi["processing_patterns"] = pp.split() if pp else []
        write_json(catalog_path, catalog)

    def _classify_patterns(self, file_info, knowledge) -> str:
        file_id = file_info["id"]

        # Check catalog cache
        cached = self._pp_cache.get(file_id)
        if cached is not None:
            return cached

        prompt = self.prompt_template
        prompt = prompt.replace("{FILE_ID}", file_id)
        prompt = prompt.replace("{TITLE}", knowledge.get("title", ""))
        prompt = prompt.replace("{TYPE}", file_info["type"])
        prompt = prompt.replace("{CATEGORY}", file_info["category"])
        prompt = prompt.replace("{KNOWLEDGE_JSON}",
                                json.dumps(knowledge, ensure_ascii=False, indent=2))

        try:
            result = self.run_claude(
                prompt=prompt,
                json_schema=CLASSIFY_PATTERNS_SCHEMA,
                log_dir=self.ctx.phase_f_executions_dir,
                file_id=file_id
            )
            if result.returncode == 0:
                parsed = json.loads(result.stdout)
                patterns = " ".join(parsed.get("patterns", []))
                return patterns
        except json.JSONDecodeError:
            pass

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
            if knowledge.get("no_knowledge_content") is True:
                continue
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
            self.logger.info(f"  Classifying {len(to_classify)} files...")
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

        # Save patterns back to catalog.json
        pp_map = {}
        for e in entries:
            fi = e.get("_fi")
            if fi and e["processing_patterns"] is not None:
                pp_map[fi["id"]] = e["processing_patterns"]

        if pp_map and not self.dry_run:
            self._save_pp_to_catalog(pp_map)

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
            self.logger.info(f"  Wrote: {self.ctx.index_path} ({len(entries)} entries)")

    def _convert_asset_paths(self, content, file_info):
        """Convert asset paths for browsable docs.

        Knowledge JSON files use relative paths: assets/file-id/filename
        Browsable MD files need correct relative paths from docs directory.

        Example transformation:
            Knowledge JSON: assets/handlers-sample-handler/diagram.png
            Browsable MD:   ../../knowledge/component/handlers/assets/handlers-sample-handler/diagram.png

        Directory structure (depth=3 requires ../../ prefix):
            docs/type/category/file-id.md           <- browsable MD location
            knowledge/type/category/assets/file-id/ <- assets location

        Args:
            content: Section content with asset references
            file_info: File metadata with type, category, id

        Returns:
            str: Content with converted asset paths
        """
        file_id = file_info["id"]
        type_ = file_info["type"]
        category = file_info["category"]

        # Build relative path from docs/type/category/file-id.md to knowledge/type/category/assets/file-id/
        # Result: ../../knowledge/type/category/assets/file-id/
        relative_prefix = f"../../knowledge/{type_}/{category}/assets/{file_id}/"

        # Compile patterns on first use per file_id (performance optimization)
        if file_id not in self._pattern_cache:
            self._pattern_cache[file_id] = {
                'image': re.compile(r'!\[([^\]]*)\]\(assets/' + re.escape(file_id) + r'/([^)]+)\)'),
                'link': re.compile(r'(?<!\!)\[([^\]]*)\]\(assets/' + re.escape(file_id) + r'/([^)]+)\)')
            }

        # Convert image references: ![text](assets/file-id/filename) -> ![text](../../knowledge/.../assets/file-id/filename)
        # Only convert assets for THIS file's ID (assets/handlers-sample-handler/* for handlers-sample-handler.json)
        content = self._pattern_cache[file_id]['image'].sub(
            r'![\1](' + relative_prefix + r'\2)',
            content
        )

        # Convert download links: [text](assets/file-id/filename) -> [text](../../knowledge/.../assets/file-id/filename)
        # Negative lookbehind (?<!\!) ensures we don't match image syntax ![text](...)
        content = self._pattern_cache[file_id]['link'].sub(
            r'[\1](' + relative_prefix + r'\2)',
            content
        )

        return content

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
            if knowledge.get("no_knowledge_content") is True:
                continue
            md_lines = [f"# {knowledge['title']}", ""]
            for entry in knowledge.get("index", []):
                sid = entry["id"]
                md_lines.append(f"## {entry['title']}")
                md_lines.append("")

                # Get section content and convert asset paths for browsable docs
                section_content = knowledge.get("sections", {}).get(sid, "")
                section_content = self._convert_asset_paths(section_content, fi)
                md_lines.append(section_content)
                md_lines.append("")

            md_path = f"{self.ctx.docs_dir}/{fi['type']}/{fi['category']}/{fi['id']}.md"
            if not self.dry_run:
                write_file(md_path, "\n".join(md_lines))
            generated += 1

        self.logger.info(f"  Generated {generated} docs")

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
            self.logger.info(f"  Summary: {log_dir}/summary.json")

    def run(self):
        self.logger.info("  Building index.toon...")
        self._build_index_toon()

        self.logger.info("  Generating docs...")
        self._generate_docs()

        self.logger.info("  Generating summary...")
        self._generate_summary()
