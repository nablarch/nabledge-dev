"""Phase F: Finalize

Build index.toon, generate browsable docs, create summary.
"""

import os
import re
import json
from glob import glob
from datetime import datetime, timezone
from common import load_json, write_json, read_file, write_file
from logger import get_logger

VALID_PROCESSING_PATTERNS = {
    "nablarch-batch", "jakarta-batch", "restful-web-service",
    "http-messaging", "web-application", "mom-messaging", "db-messaging"
}


class PhaseFFinalize:
    def __init__(self, ctx, dry_run=False):
        self.ctx = ctx
        self.dry_run = dry_run
        self.logger = get_logger()
        # Cache compiled regex patterns per file_id (performance optimization)
        self._pattern_cache = {}

    def _build_index_toon(self):
        classified = load_json(self.ctx.classified_list_path)
        entries = []

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
                pp = knowledge.get("processing_patterns", [])
                patterns = " ".join(pp) if isinstance(pp, list) else (pp or "")

            entries.append({
                "title": title, "type": fi["type"], "category": fi["category"],
                "processing_patterns": patterns, "path": fi["output_path"],
            })

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

            # Add official doc URLs
            urls = knowledge.get("official_doc_urls", [])
            if urls:
                if len(urls) == 1:
                    link = f"[{knowledge['title']}]({urls[0]})"
                else:
                    link = " ".join(f"[{i + 1}]({u})" for i, u in enumerate(urls))
                md_lines.append(f"**公式ドキュメント**: {link}")
                md_lines.append("")

            for entry in knowledge.get("index", []):
                sid = entry["id"]
                md_lines.append(f"## {entry['title']}")
                md_lines.append("")

                # Get section content and convert asset paths for browsable docs
                section_content = knowledge.get("sections", {}).get(sid, "")
                section_content = self._convert_asset_paths(section_content, fi)
                md_lines.append(section_content)
                md_lines.append("")

                # Add hints as keywords
                hints = entry.get("hints", [])
                if hints:
                    md_lines.append(f"*キーワード: {', '.join(hints)}*")
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
