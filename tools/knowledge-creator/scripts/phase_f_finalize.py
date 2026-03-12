"""Phase F: Finalize

Build index.toon, generate skill JSON with resolved links, generate browsable docs,
create summary.
"""

import os
import re
import json
from glob import glob
from datetime import datetime, timezone
from common import load_json, write_json, read_file, write_file
from logger import get_logger


class PhaseFFinalize:
    def __init__(self, ctx, dry_run=False, catalog_for_links=None):
        self.ctx = ctx
        self.dry_run = dry_run
        self.logger = get_logger()
        # Catalog used for _build_link_maps (may differ from classified_list_path
        # when Phase M switches to merged catalog temporarily)
        self._catalog_for_links = catalog_for_links
        # Cache compiled regex patterns per file_id (performance optimization)
        self._pattern_cache = {}
        # Link resolution maps (populated by _build_link_maps)
        self.label_map = {}       # label -> (file_id, section_id_or_None)
        self.doc_map = {}         # source_path_partial -> file_id
        self.file_type_category = {}  # file_id -> (type, category)

    def _build_link_maps(self):
        """Build link resolution maps from catalog and knowledge files.

        Scans catalog section_map entries to build:
          self.label_map: {rst_label: (file_id, section_id_or_None)}
          self.doc_map: {source_path_without_ext: file_id}
          self.file_type_category: {file_id: (type, category)}
        """
        if self._catalog_for_links:
            catalog = self._catalog_for_links
        else:
            catalog = load_json(self.ctx.classified_list_path)

        files = catalog.get("files", [])

        # Pass 1: build file_type_category, doc_map, and collect section_maps per effective_id
        effective_id_data = {}  # effective_id -> {type, category, section_maps, source_path}

        for fi in files:
            si = fi.get("split_info", {})
            effective_id = si["original_id"] if si.get("is_split") else fi["id"]

            if effective_id not in effective_id_data:
                effective_id_data[effective_id] = {
                    "type": fi["type"],
                    "category": fi["category"],
                    "section_maps": [],
                    "source_path": fi.get("source_path", ""),
                }

            self.file_type_category[effective_id] = (fi["type"], fi["category"])

            # Build doc_map from source_path (only once per effective_id)
            source_path = fi.get("source_path", "")
            if source_path and not effective_id_data[effective_id]["source_path"].strip():
                effective_id_data[effective_id]["source_path"] = source_path

            rst_path = re.sub(r'\.(rst|md|xlsx?)$', '', source_path) if source_path else ""
            if rst_path:
                self.doc_map.setdefault(rst_path, effective_id)
                parts = rst_path.split("/")
                for i in range(1, len(parts)):
                    partial = "/".join(parts[i:])
                    self.doc_map.setdefault(partial, effective_id)

            section_map = fi.get("section_map", [])
            if section_map:
                effective_id_data[effective_id]["section_maps"].extend(section_map)

        # Pass 2: for each effective_id with section_maps, load knowledge JSON
        # and build label_map via heading/title text matching
        for effective_id, data in effective_id_data.items():
            if not data["section_maps"]:
                continue

            type_ = data["type"]
            cat = data["category"]
            knowledge_path = f"{self.ctx.knowledge_dir}/{type_}/{cat}/{effective_id}.json"

            heading_to_section_id = {}
            if os.path.exists(knowledge_path):
                knowledge = load_json(knowledge_path)
                for entry in knowledge.get("index", []):
                    title = entry.get("title", "").strip()
                    if title:
                        heading_to_section_id[title] = entry["id"]
                        heading_to_section_id[title.lower()] = entry["id"]

            for sm_entry in data["section_maps"]:
                heading = sm_entry.get("heading", "").strip()
                rst_labels = sm_entry.get("rst_labels", [])
                section_id = (
                    heading_to_section_id.get(heading)
                    or heading_to_section_id.get(heading.lower())
                )

                for label in rst_labels:
                    self.label_map.setdefault(label, (effective_id, section_id))
                    label_u = label.replace("-", "_")
                    label_h = label.replace("_", "-")
                    if label_u != label:
                        self.label_map.setdefault(label_u, (effective_id, section_id))
                    if label_h != label:
                        self.label_map.setdefault(label_h, (effective_id, section_id))

    def _resolve_rst_links(self, content, current_file_id, output_type):
        """Resolve RST link syntax in content.

        Args:
            content: Section content with RST links
            current_file_id: ID of the file being processed
            output_type: 'skill_json' | 'docs_md'

        Returns:
            str: Content with RST links converted to Markdown links
        """
        def resolve_ref(m):
            full = m.group(0)
            # Parse :ref:`display <label>` or :ref:`label`
            with_text = re.match(r':ref:`([^<>`]+?)\s*<([^>`]+)>`', full)
            plain = re.match(r':ref:`([^`>]+)`', full)
            if with_text:
                display_text = with_text.group(1).strip()
                label = with_text.group(2).strip()
            elif plain:
                label = plain.group(1).strip()
                display_text = None
            else:
                return full

            if label not in self.label_map:
                return full  # unresolved: keep as-is

            target_file_id, section_id = self.label_map[label]
            text = display_text if display_text else label

            if target_file_id == current_file_id:
                # Same-file reference
                link = f"#{section_id}" if section_id else f"#"
                return f"[{text}]({link})"
            else:
                # Cross-file reference
                link = self._make_cross_file_link(
                    current_file_id, target_file_id, section_id, output_type
                )
                return f"[{text}]({link})"

        def resolve_doc(m):
            full = m.group(0)
            with_text = re.match(r':doc:`([^<>`]+?)\s*<([^>`]+)>`', full)
            plain = re.match(r':doc:`([^`>]+)`', full)
            if with_text:
                display_text = with_text.group(1).strip()
                doc_path = with_text.group(2).strip()
            elif plain:
                doc_path = plain.group(1).strip()
                display_text = None
            else:
                return full

            # Normalize: strip leading ./ and ../
            norm = re.sub(r'^(\.\.?/)+', '', doc_path)
            target_file_id = self.doc_map.get(doc_path) or self.doc_map.get(norm)
            if not target_file_id:
                return full  # unresolved

            text = display_text if display_text else doc_path
            link = self._make_cross_file_link(current_file_id, target_file_id, None, output_type)
            return f"[{text}]({link})"

        def resolve_download(m):
            full = m.group(0)
            dl = re.match(r':download:`([^<>`]+?)\s*<([^>`]+)>`', full)
            if not dl:
                return full
            display_text = dl.group(1).strip()
            file_path = dl.group(2).strip()

            if file_path.startswith('/') or '..' in file_path or '\\' in file_path:
                return full  # suspicious path

            filename = os.path.basename(os.path.normpath(file_path))
            if output_type == 'skill_json':
                return f"[{display_text}](assets/{current_file_id}/{filename})"
            else:
                type_, cat = self.file_type_category.get(current_file_id, ('', ''))
                return f"[{display_text}](../../../knowledge/{type_}/{cat}/assets/{current_file_id}/{filename})"

        def resolve_java_extdoc(m):
            full = m.group(0)
            with_text = re.match(r':java:extdoc:`([^<>`]+?)\s*<([^>`]+)>`', full)
            plain = re.match(r':java:extdoc:`([^`>]+)`', full)
            if with_text:
                display_text = with_text.group(1).strip()
            elif plain:
                class_name = plain.group(1).strip()
                simple = class_name.split(".")[-1].split("#")[0]
                display_text = simple
            else:
                return full
            return f"`{display_text}`"

        content = re.sub(r':ref:`[^`]+`', resolve_ref, content)
        content = re.sub(r':doc:`[^`]+`', resolve_doc, content)
        content = re.sub(r':download:`[^<>`]+<[^>`]+>`', resolve_download, content)
        content = re.sub(r':java:extdoc:`[^`]+`', resolve_java_extdoc, content)
        return content

    def _make_cross_file_link(self, from_file_id, to_file_id, section_id, output_type):
        """Build a link from one file to another."""
        anchor = f"#{section_id}" if section_id else ""
        if output_type == 'skill_json':
            from_type, from_cat = self.file_type_category.get(from_file_id, ('', ''))
            to_type, to_cat = self.file_type_category.get(to_file_id, ('', ''))
            from_dir = f"{self.ctx.knowledge_dir}/{from_type}/{from_cat}"
            to_path = f"{self.ctx.knowledge_dir}/{to_type}/{to_cat}/{to_file_id}.json"
            rel = os.path.relpath(to_path, from_dir)
            return f"{rel}{anchor}"
        else:
            # docs_md: relative path between two MD files
            from_type, from_cat = self.file_type_category.get(from_file_id, ('', ''))
            to_type, to_cat = self.file_type_category.get(to_file_id, ('', ''))
            from_dir = f"{self.ctx.docs_dir}/{from_type}/{from_cat}"
            to_path = f"{self.ctx.docs_dir}/{to_type}/{to_cat}/{to_file_id}.md"
            rel = os.path.relpath(to_path, from_dir)
            return f"{rel}{anchor}"

    def _generate_skill_json(self):
        """Generate skill JSON files with RST links resolved in-place.

        Reads merged knowledge JSON from knowledge_dir, applies link resolution,
        and overwrites the same files. Cache files in knowledge_cache_dir are
        never modified.
        """
        classified = load_json(self.ctx.classified_list_path)
        resolved = 0

        for fi in classified["files"]:
            json_path = f"{self.ctx.knowledge_dir}/{fi['output_path']}"
            if not os.path.exists(json_path):
                continue

            knowledge = load_json(json_path)
            if knowledge.get("no_knowledge_content"):
                continue

            file_id = fi["id"]
            changed = False
            new_sections = {}
            for sid, content in knowledge.get("sections", {}).items():
                resolved_content = self._resolve_rst_links(content, file_id, 'skill_json')
                new_sections[sid] = resolved_content
                if resolved_content != content:
                    changed = True

            if changed:
                knowledge["sections"] = new_sections
                if not self.dry_run:
                    write_json(json_path, knowledge)
                resolved += 1

        self.logger.info(f"  Skill JSON link resolution applied to {resolved} files")

    def _build_index_toon(self):
        classified = load_json(self.ctx.classified_list_path)
        entries = []

        knowledge_dir = self.ctx.knowledge_dir

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
                # Read processing_patterns from catalog entry, not knowledge JSON
                pp = fi.get("processing_patterns", [])
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
            Browsable MD:   ../../../knowledge/component/handlers/assets/handlers-sample-handler/diagram.png

        Directory structure (depth=3 requires ../../../ prefix):
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
        # Result: ../../../knowledge/type/category/assets/file-id/
        relative_prefix = f"../../../knowledge/{type_}/{category}/assets/{file_id}/"

        # Compile patterns on first use per file_id (performance optimization)
        if file_id not in self._pattern_cache:
            # Use .*? for alt text to handle nested brackets like ![text with [no] inside](...)
            self._pattern_cache[file_id] = {
                'image': re.compile(r'!\[(.*?)\]\(assets/' + re.escape(file_id) + r'/([^)]+)\)'),
                'link': re.compile(r'(?<!\!)\[(.*?)\]\(assets/' + re.escape(file_id) + r'/([^)]+)\)')
            }

        # Convert image references: ![text](assets/file-id/filename) -> ![text](../../../knowledge/.../assets/file-id/filename)
        content = self._pattern_cache[file_id]['image'].sub(
            r'![\1](' + relative_prefix + r'\2)',
            content
        )

        # Convert download links: [text](assets/file-id/filename) -> [text](../../../knowledge/.../assets/file-id/filename)
        content = self._pattern_cache[file_id]['link'].sub(
            r'[\1](' + relative_prefix + r'\2)',
            content
        )

        return content

    def _generate_docs(self):
        classified = load_json(self.ctx.classified_list_path)
        generated = 0

        knowledge_dir = self.ctx.knowledge_dir

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

                # Get section content, convert asset paths and resolve RST links
                section_content = knowledge.get("sections", {}).get(sid, "")
                section_content = self._convert_asset_paths(section_content, fi)
                section_content = self._resolve_rst_links(section_content, fi["id"], 'docs_md')
                md_lines.append(section_content)
                md_lines.append("")

                # Add hints as keywords in a collapsible details block
                hints = entry.get("hints", [])
                if hints:
                    md_lines.append("<details>")
                    md_lines.append("<summary>keywords</summary>")
                    md_lines.append("")
                    md_lines.append(f"{', '.join(hints)}")
                    md_lines.append("")
                    md_lines.append("</details>")
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
        self._build_link_maps()

        self.logger.info("  Generating skill JSON with resolved links...")
        self._generate_skill_json()

        self.logger.info("  Building index.toon...")
        self._build_index_toon()

        self.logger.info("  Generating docs...")
        self._generate_docs()

        self.logger.info("  Generating summary...")
        self._generate_summary()
