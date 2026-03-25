"""Step 2: Type/Category Classification

Classify source files into Type/Category based on path patterns.
Split large files into multiple entries if necessary.
"""

import os
import json
import re
from datetime import datetime
from common import load_json, write_json, read_file
from logger import get_logger


def _rst_doc_roots(version: str) -> list:
    """RST path segments that separate the repo prefix from the doc-relative path."""
    if version == "1.4":
        return ["document/", "workflow/", "biz_sample/", "ui_dev/", "MessagingSimu/"]
    if version == "1.3":
        return ["document/", "biz_sample/"]
    if version == "1.2":
        return ["document/"]
    return ["nablarch-document/ja/"]


def _load_mappings(repo: str, version: str) -> dict:
    """Load RST/MD/XLSX mappings from version-specific JSON file.

    Each version has its own complete mapping file (vN.json).
    Keep in sync with load_mappings() in tests/e2e/generate_expected.py.

    Returns:
        dict with keys: rst, md, xlsx, xlsx_patterns
    """
    mappings_dir = os.path.join(repo, "tools/knowledge-creator/mappings")
    mapping_path = os.path.join(mappings_dir, f"v{version}.json")

    if not os.path.exists(mapping_path):
        raise FileNotFoundError(
            f"Mapping file not found: {mapping_path}\n"
            f"Create tools/knowledge-creator/mappings/v{version}.json to support this version."
        )

    with open(mapping_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "rst": data.get("rst", []),
        "md": data.get("md", {}),
        "xlsx": data.get("xlsx", {}),
        "xlsx_patterns": data.get("xlsx_patterns", []),
    }


def load_test_file_ids(repo_path: str, test_file_name: str) -> set:
    """Load test file IDs from specified test file"""
    test_file_path = os.path.join(repo_path, "tools/knowledge-creator/tests/e2e/mode", test_file_name)

    if not os.path.exists(test_file_path):
        raise FileNotFoundError(f"Test file set not found: {test_file_path}")

    with open(test_file_path) as f:
        test_data = json.load(f)

    # Extract file IDs from the files array
    file_ids = set(test_data["files"])
    return file_ids


def filter_for_test(classified: list, test_file_ids: set) -> list:
    """Filter file list for test mode using source file names (original_id).

    Test files must specify source file names, not split part IDs.
    All split parts of a matching source file are automatically included.
    """
    result = []
    for f in classified:
        # Get the original_id (for split files) or id (for non-split files)
        original_id = f.get('split_info', {}).get('original_id') or f['id']

        if original_id in test_file_ids:
            result.append(f)

    return result


class Step2Classify:
    # Thresholds for section-unit splitting
    LINE_GROUP_THRESHOLD = 400  # セクションをグループ化する行数の閾値（h3展開とグループ化の両方に使用）

    def __init__(self, ctx, sources_data=None):
        self.ctx = ctx
        self.sources_data = sources_data
        self.logger = get_logger()
        mappings = _load_mappings(ctx.repo, ctx.version)
        self._rst_mapping = [(e["pattern"], e["type"], e["category"]) for e in mappings["rst"]]
        self._md_mapping = {k: (v["type"], v["category"]) for k, v in mappings["md"].items()}
        self._xlsx_mapping = {k: (v["type"], v["category"]) for k, v in mappings["xlsx"].items()}
        self._xlsx_patterns = [(e["endswith"], e["type"], e["category"]) for e in mappings["xlsx_patterns"]]

    def generate_id(self, filename: str, format: str, category: str = None,
                    source_path: str = None, matched_pattern: str = None) -> str:
        """Generate knowledge file ID from filename and category

        Args:
            filename: Source filename
            format: File format (rst/md/xlsx)
            category: Category from classification (optional)
            source_path: Source file path for index.rst disambiguation (optional)
            matched_pattern: rst mapping pattern that matched (optional, for index.rst)

        Returns:
            Unique file ID (category-filename format for rst/md)
        """
        # For Excel files with exact filename mapping, use category as ID
        if format == "xlsx" and filename in self._xlsx_mapping:
            return category

        base_name = None
        if format == "rst":
            base_name = filename.replace(".rst", "")
        elif format == "md":
            base_name = filename.replace(".md", "")
        elif format == "xlsx":
            base_name = filename.replace(".xlsx", "")
        else:
            base_name = filename

        # index.rst: use pattern-remainder path to avoid ID collisions.
        # Multiple index.rst files can map to the same category, so filename alone
        # ("index") is insufficient. Use the path after the matched pattern as context.
        #
        # Examples:
        #   handlers/batch/index.rst matched by "handlers/" -> remainder "batch/index.rst" -> "batch"
        #   handlers/index.rst matched by "handlers/" -> remainder "index.rst" -> pattern basename "handlers"
        #   top-level index.rst matched by "" -> "top"
        if base_name == "index" and source_path is not None and matched_pattern is not None:
            rst_rel = None
            for marker in _rst_doc_roots(self.ctx.version):
                marker_idx = source_path.find(marker)
                if marker_idx >= 0:
                    if self.ctx.version == "1.4" or (self.ctx.version.startswith("1.") and marker != "document/"):
                        rst_rel = marker + source_path[marker_idx + len(marker):]
                    else:
                        rst_rel = source_path[marker_idx + len(marker):]
                    break
            if rst_rel is not None:
                pattern_clean = matched_pattern.rstrip("/")
                if not pattern_clean:
                    # Top-level index.rst (matched by "")
                    base_name = "top"
                else:
                    pat_idx = rst_rel.find(pattern_clean)
                    if pat_idx >= 0:
                        remainder = rst_rel[pat_idx + len(pattern_clean):].strip("/")
                        if remainder == "index.rst":
                            base_name = os.path.basename(pattern_clean)
                        else:
                            dir_part = os.path.dirname(remainder)
                            base_name = dir_part.replace("/", "-").replace("_", "-")
                    else:
                        self.logger.warning(
                            f"generate_id: pattern '{pattern_clean}' not found in path '{rst_rel}'"
                            f" — using 'index' as base_name (potential ID collision)"
                        )

        # Include category to ensure uniqueness
        if category:
            return f"{category}-{base_name}"
        return base_name

    def classify_rst(self, path: str) -> tuple:
        """Classify RST file based on path pattern"""
        # Extract path after nablarch-document/ja/ (or version_maintain/ for v1.x)
        rel_path = None
        for marker in _rst_doc_roots(self.ctx.version):
            idx = path.find(marker)
            if idx >= 0:
                # v1.4 has multiple repos (document/, workflow/, biz_sample/, ui_dev/).
                # v1.3 has document/ (patterns strip it) and biz_sample/ (patterns keep it).
                # Keep the marker in rel_path so patterns can distinguish repos.
                if self.ctx.version == "1.4" or (self.ctx.version.startswith("1.") and marker != "document/"):
                    rel_path = marker + path[idx + len(marker):]
                else:
                    rel_path = path[idx + len(marker):]
                break
        if rel_path is None:
            return None, None, None

        # Top-level index.rst: no RST_MAPPING pattern can match "index.rst" alone
        # because "" would match everything. Handle explicitly.
        if rel_path == "index.rst":
            return "about", "about-nablarch", ""

        # Try to match against rst mapping (version-specific entries first)
        for pattern, type_, category in self._rst_mapping:
            if pattern in rel_path:
                return type_, category, pattern

        return None, None, None

    def analyze_rst_sections(self, content: str) -> list:
        """Analyze RST file structure and return section information

        Returns:
            List of dicts with keys: title, start_line, end_line, line_count, level
        """
        lines = content.splitlines()
        sections = []

        # Find h2 sections (line followed by -----)
        for i in range(len(lines) - 1):
            if re.match(r'^-{5,}$', lines[i + 1]):
                title = lines[i].strip()
                sections.append({
                    'title': title,
                    'start_line': i,
                    'level': 'h2'
                })

        # Expand first section to include preamble (content before first h2)
        if sections:
            sections[0]['start_line'] = 0

        # Calculate end_line and line_count for each section
        for i in range(len(sections)):
            start = sections[i]['start_line']
            end = sections[i + 1]['start_line'] if i + 1 < len(sections) else len(lines)
            sections[i]['end_line'] = end
            sections[i]['line_count'] = end - start

        return sections

    def analyze_rst_h3_subsections(self, content: str, h2_start: int, h2_end: int) -> list:
        """Analyze h3 subsections within an h2 section

        Args:
            content: Full file content
            h2_start: Start line of h2 section
            h2_end: End line of h2 section

        Returns:
            List of h3 subsection dicts with keys: title, start_line, end_line, line_count, level
        """
        lines = content.splitlines()
        subsections = []

        # Find h3 sections within the h2 range
        # h3 can be marked with various underlines: ^^^^^ ~~~~~ +++++ ===== etc.
        # Exclude ----- (h2)
        h3_pattern = re.compile(r'^[\^~+*.=]{5,}$')

        for i in range(h2_start, h2_end - 1):
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # Check if next line is an h3 marker (not h2)
                if h3_pattern.match(next_line) and not re.match(r'^-{5,}$', next_line):
                    title = lines[i].strip()
                    subsections.append({
                        'title': title,
                        'start_line': i,
                        'level': 'h3'
                    })

        # Calculate end_line and line_count for each subsection
        for i in range(len(subsections)):
            start = subsections[i]['start_line']
            end = subsections[i + 1]['start_line'] if i + 1 < len(subsections) else h2_end
            subsections[i]['end_line'] = end
            subsections[i]['line_count'] = end - start

        return subsections

    def should_split_file(self, file_path: str, format: str) -> tuple:
        """Check if file should be split into per-section files.

        Returns:
            (should_split: bool, sections: list, total_lines: int)
        """
        if format != "rst":
            return False, [], 0

        full_path = os.path.join(self.ctx.repo, file_path)
        if not os.path.exists(full_path):
            return False, [], 0

        content = read_file(full_path)
        lines = content.splitlines()
        total_lines = len(lines)
        sections = self.analyze_rst_sections(content)

        return True, sections, total_lines

    def split_file_entry(self, base_entry: dict, sections: list, content: str) -> list:
        """Split a file entry into groups of sections based on line count.

        Large h2 sections (> LINE_GROUP_THRESHOLD) are expanded to h3 subsections first.
        Then sections are grouped together until total lines exceed LINE_GROUP_THRESHOLD.

        Args:
            base_entry: Original classified entry
            sections: List of h2 section info from analyze_rst_sections
            content: Full source file content

        Returns:
            List of split entries, one per section group
        """
        # Step 1: h2セクションをh3で展開(必要な場合のみ)
        expanded_sections = self._expand_large_sections(sections, content)

        # Step 2: セクションを行数でグループ化
        groups = self._group_sections_by_lines(expanded_sections)

        # Step 3: 全セクション（展開後）を通しカウントし、各グループの開始番号を計算
        section_counter = 1
        group_start_counters = []
        for group in groups:
            group_start_counters.append(section_counter)
            section_counter += len(group)

        # Step 4: RST ラベルを抽出
        rst_labels = self._extract_rst_labels_with_positions(content)

        # Step 5: 各グループからエントリを生成（section に assigned_id が付与される）
        result = self._generate_entries_from_groups(base_entry, groups, group_start_counters)

        # Step 6: section_map を構築（全グループ横断）
        section_map = []
        for group in groups:
            for section in group:
                labels = [label for label, line in rst_labels
                          if section['start_line'] <= line < section['end_line']]
                section_map.append({
                    "section_id": section['assigned_id'],
                    "heading": section['title'],
                    "rst_labels": labels
                })

        # Step 7: 各エントリに section_map を付与
        for entry in result:
            entry['section_map'] = section_map

        return result

    def _expand_large_sections(self, sections: list, content: str) -> list:
        """Expand large h2 sections to h3 subsections if they exceed LINE_GROUP_THRESHOLD.

        Args:
            sections: List of h2 section info
            content: Full source file content

        Returns:
            List of expanded sections (h2 or h3)
        """
        expanded_sections = []
        for section in sections:
            if section['line_count'] > self.LINE_GROUP_THRESHOLD:
                h3_subs = self.analyze_rst_h3_subsections(
                    content, section['start_line'], section['end_line']
                )
                if h3_subs:
                    # h2セクションのh3より前の部分(プリアンブル)を最初のh3に含める
                    if h3_subs[0]['start_line'] > section['start_line']:
                        h3_subs[0]['start_line'] = section['start_line']
                        h3_subs[0]['line_count'] = h3_subs[0]['end_line'] - h3_subs[0]['start_line']
                    expanded_sections.extend(h3_subs)
                    self.logger.debug(f"    h3 fallback: '{section['title']}' ({section['line_count']} lines) → {len(h3_subs)} h3 subsections")
                else:
                    # h3がない巨大h2 → そのまま(警告付き)
                    expanded_sections.append(section)
                    self.logger.warning(f"    WARNING: '{section['title']}' has {section['line_count']} lines but no h3 subsections")
            else:
                expanded_sections.append(section)
        return expanded_sections

    def _group_sections_by_lines(self, sections: list) -> list:
        """Group sections together until total lines exceed LINE_GROUP_THRESHOLD.

        Uses greedy accumulation: keep adding sections until total > threshold.

        Args:
            sections: List of section info (after h3 expansion)

        Returns:
            List of groups, each containing list of sections
        """
        if not sections:
            return []

        groups = []
        current_group = []
        current_line_count = 0

        for section in sections:
            # Try adding this section to current group
            new_total = current_line_count + section['line_count']

            if current_group and new_total > self.LINE_GROUP_THRESHOLD:
                # Adding this section would exceed threshold, finalize current group
                groups.append(current_group)
                current_group = [section]
                current_line_count = section['line_count']
            else:
                # Add to current group
                current_group.append(section)
                current_line_count = new_total

        # Don't forget the last group
        if current_group:
            groups.append(current_group)

        return groups

    def _generate_entries_from_groups(self, base_entry: dict, groups: list,
                                       group_start_counters: list) -> list:
        """Generate split entries from section groups using sequential section IDs.

        Args:
            base_entry: Original classified entry
            groups: List of section groups
            group_start_counters: Start counter for each group (sequential across parts)

        Returns:
            List of split entries (sections have 'assigned_id' set as side effect)
        """
        result = []
        base_id = base_entry['id']
        type_ = base_entry['type']
        category = base_entry['category']
        total_parts = len(groups)

        for part_num, (group, start_counter) in enumerate(
            zip(groups, group_start_counters), 1
        ):
            counter = start_counter
            section_id_list = []
            for section in group:
                sid = f"s{counter}"
                section['assigned_id'] = sid  # section_map 構築用
                section_id_list.append(sid)
                counter += 1

            # パートIDは最初のセクションIDを使用
            first_sid = section_id_list[0]
            split_id = f"{base_id}--{first_sid}"

            # Calculate group line range
            start_line = group[0]['start_line']
            end_line = group[-1]['end_line']
            group_line_count = sum(s['line_count'] for s in group)

            # Collect all section titles in this group
            section_titles = [s['title'] for s in group]

            result.append({
                **base_entry,
                'id': split_id,
                'base_name': base_id,
                'output_path': f"{type_}/{category}/{split_id}.json",
                'assets_dir': f"{type_}/{category}/assets/{split_id}/",
                'section_range': {
                    'start_line': start_line,
                    'end_line': end_line,
                    'sections': section_titles,
                    'section_ids': section_id_list
                },
                'split_info': {
                    'is_split': True,
                    'part': part_num,
                    'total_parts': total_parts,
                    'original_id': base_id,
                    'group_line_count': group_line_count
                }
            })

        return result

    def _extract_rst_labels_with_positions(self, content: str) -> list:
        """Extract RST label definitions with their line positions.

        Returns:
            List of (label, line_number) tuples
        """
        results = []
        for i, line in enumerate(content.splitlines()):
            m = re.match(r'^\.\.\s+_([a-z0-9_-]+):', line)
            if m:
                results.append((m.group(1), i))
        return results

    def run(self, return_only=False):
        """Execute Step 2: Classify all source files

        Args:
            return_only: If True, return only the classified entries list without writing to disk.
                         Used by _partial_phase_a for targeted catalog updates.
        """
        if self.sources_data:
            sources = self.sources_data
        else:
            sources = load_json(self.ctx.source_list_path)
        classified = []
        unmatched = []

        for source in sources["sources"]:
            format = source["format"]
            filename = source["filename"]
            path = source["path"]

            type_ = None
            category = None

            # Classify based on format (must be done before generating ID)
            matched_pattern = None
            if format == "rst":
                type_, category, matched_pattern = self.classify_rst(path)
            elif format == "md":
                if filename in self._md_mapping:
                    type_, category = self._md_mapping[filename]
            elif format == "xlsx":
                if filename in self._xlsx_mapping:
                    type_, category = self._xlsx_mapping[filename]
                else:
                    for endswith, t, c in self._xlsx_patterns:
                        if filename.endswith(endswith):
                            type_, category = t, c
                            break

            if type_ is None or category is None:
                unmatched.append({
                    "path": path,
                    "filename": filename,
                    "format": format
                })
                continue

            # Generate unique ID using category to avoid collisions
            file_id = self.generate_id(filename, format, category,
                                       source_path=path, matched_pattern=matched_pattern)

            output_path = f"{type_}/{category}/{file_id}.json"
            assets_dir = f"{type_}/{category}/assets/{file_id}/"

            classified.append({
                "source_path": path,
                "format": format,
                "filename": filename,
                "type": type_,
                "category": category,
                "id": file_id,
                "base_name": file_id,
                "output_path": output_path,
                "assets_dir": assets_dir
            })

        # Check for files that need splitting
        final_classified = []
        split_count = 0

        for entry in classified:
            should_split, sections, total_lines = self.should_split_file(entry['source_path'], entry['format'])

            if should_split:
                # Load content for h3 analysis
                full_path = os.path.join(self.ctx.repo, entry['source_path'])
                content = read_file(full_path)

                split_entries = self.split_file_entry(entry, sections, content)
                if len(split_entries) > 1:
                    final_classified.extend(split_entries)
                    split_count += 1
                    self.logger.info(f"   ✂️Split {entry['id']}: {total_lines} lines → {len(split_entries)} parts")
                else:
                    # 0 or 1 group: treat as non-split (no --s1 suffix)
                    rst_labels = self._extract_rst_labels_with_positions(content)
                    counter = 1
                    section_map = []
                    for sec in sections:
                        labels = [label for label, line in rst_labels
                                  if sec['start_line'] <= line < sec['end_line']]
                        section_map.append({
                            "section_id": f"s{counter}",
                            "heading": sec['title'],
                            "rst_labels": labels
                        })
                        counter += 1
                    # h2 がないファイルでもラベルがあれば記録
                    if not sections and rst_labels:
                        section_map.append({
                            "section_id": "s1",
                            "heading": "",
                            "rst_labels": [label for label, _ in rst_labels]
                        })
                    entry['section_map'] = section_map
                    final_classified.append(entry)
            else:
                # Non-RST files: no section_map
                final_classified.append(entry)

        if split_count > 0:
            self.logger.info(f"\n   ✂️Split {split_count} large files into {len(final_classified) - len(classified) + split_count} total entries")

        classified = final_classified

        # Deduplicate IDs by adding ancestor directory names
        from collections import Counter
        id_counts = Counter(e['id'] for e in classified)
        dup_ids = {k for k, v in id_counts.items() if v > 1}

        if dup_ids:
            self.logger.info(f"\n   🔧Deduplicating {len(dup_ids)} duplicate IDs...")
            for dup_id in dup_ids:
                group = [e for e in classified if e['id'] == dup_id]

                # Find minimum depth where ancestor dirs are all unique
                resolved_depth = None
                for depth in range(1, 6):
                    suffixes = []
                    for e in group:
                        d = os.path.dirname(os.path.join(self.ctx.repo, e['source_path']))
                        for _ in range(depth - 1):
                            d = os.path.dirname(d)
                        suffixes.append(os.path.basename(d))
                    if len(set(suffixes)) == len(group):
                        resolved_depth = depth
                        break

                if resolved_depth is None:
                    self.logger.error(f"   ❌ID dedup failed for {dup_id}")
                    raise SystemExit(1)

                for e in group:
                    d = os.path.dirname(os.path.join(self.ctx.repo, e['source_path']))
                    for _ in range(resolved_depth - 1):
                        d = os.path.dirname(d)
                    suffix = os.path.basename(d)
                    old_id = e['id']

                    if '--' in old_id and 'split_info' in e:
                        base, split_sfx = old_id.split('--', 1)
                        new_id = f"{base}-{suffix}--{split_sfx}"
                    else:
                        new_id = f"{old_id}-{suffix}"

                    e['id'] = new_id
                    e['base_name'] = new_id.split('--')[0] if 'split_info' in e else new_id
                    e['output_path'] = e['output_path'].replace(
                        f"{old_id}.json", f"{new_id}.json")
                    e['assets_dir'] = e['assets_dir'].replace(
                        f"assets/{old_id}/", f"assets/{new_id}/")

                    if 'split_info' in e:
                        old_oid = e['split_info']['original_id']
                        e['split_info']['original_id'] = f"{old_oid}-{suffix}"

                    self.logger.info(f"   🔧Dedup: {old_id} -> {new_id}")

            # Verify all duplicates resolved
            id_counts2 = Counter(e['id'] for e in classified)
            still_dup = {k for k, v in id_counts2.items() if v > 1}
            if still_dup:
                self.logger.error(f"   ❌ID dedup failed: {still_dup}")
                raise SystemExit(1)

        # Apply test mode filter if enabled
        if self.ctx.test_file:
            test_file_ids = load_test_file_ids(self.ctx.repo, self.ctx.test_file)
            original_count = len(classified)
            classified = filter_for_test(classified, test_file_ids)
            self.logger.info(f"\n   🧪Test mode ({self.ctx.test_file}): Filtered {original_count} files → {len(classified)} test files")

            # Show missing test files (source files in test set but not found)
            found_ids = set()
            for f in classified:
                original_id = f.get('split_info', {}).get('original_id') or f['id']
                found_ids.add(original_id)
            missing = test_file_ids - found_ids
            if missing:
                self.logger.warning(f"   ⚠️WARNING: {len(missing)} test files not found:")
                for mid in sorted(missing):
                    self.logger.warning(f"      - {mid}")

        # return_only mode: skip disk write, return entries for caller to merge
        if return_only:
            return classified

        # Update only the files field in existing catalog
        if os.path.exists(self.ctx.classified_list_path):
            try:
                output = load_json(self.ctx.classified_list_path)
            except (json.JSONDecodeError, OSError):
                output = {"version": self.ctx.version, "sources": []}
        else:
            output = {"version": self.ctx.version, "sources": []}
        output["files"] = classified

        # Category emoji mapping
        category_emoji = {
            "libraries": "📚",
            "adapters": "🔌",
            "handlers": "🏗️",
            "authentication": "🔐",
            "authorization": "🛡️",
            "validation": "✅",
            "session-store": "💾",
            "messaging": "📨",
            "batch": "⚙️",
            "etl": "🔄",
            "web-service": "🌐",
            "container-adaptor": "📦",
            "data-format": "📋",
            "testing": "🧪",
            "toolbox": "🧰",
            "cloud-native": "☁️",
            "patterns": "🎨",
            "anti-patterns": "⚠️",
            "async-process": "⏱️",
            "getting-started": "🚀",
            "blank-project": "📁",
            "about": "ℹ️",
            "migration": "🔄",
            "development": "💻",
            "testing-guide": "🧪",
            "performance": "⚡",
            "security-check": "🔒"
        }

        self.logger.info(f"\n   📑Classified {len(classified)} files")

        # Group by type, then by category
        type_order = ['processing-pattern', 'component', 'extension', 'development-tools', 'setup', 'about', 'guide', 'check']
        type_emoji = {
            'processing-pattern': '🔄',
            'component': '🧩',
            'extension': '🔩',
            'development-tools': '🛠️',
            'setup': '⚙️',
            'about': 'ℹ️',
            'guide': '📖',
            'check': '✓'
        }

        for type_name in type_order:
            type_files = [f for f in classified if f['type'] == type_name]
            count = len(type_files)
            self.logger.info(f"      {type_emoji[type_name]}{type_name}: {count}")

            if count > 0:
                # Count by category
                category_counts = {}
                for f in type_files:
                    cat = f.get('category', 'unknown')
                    category_counts[cat] = category_counts.get(cat, 0) + 1

                # Sort categories by count (descending) then by name
                for cat in sorted(category_counts.keys(), key=lambda x: (-category_counts[x], x)):
                    emoji = category_emoji.get(cat, "📄")
                    self.logger.info(f"         {emoji}{cat}: {category_counts[cat]}")

        if unmatched:
            self.logger.error(f"\n   ❌ ERROR: {len(unmatched)} RST files have no RST_MAPPING entry.")
            self.logger.error(f"   Add a mapping for each file to:")
            self.logger.error(f"   tools/knowledge-creator/mappings/v{self.ctx.version}.json")
            self.logger.error(f"")
            self.logger.error(f"   Unmapped files:")
            for item in unmatched:
                self.logger.error(f"     {item['path']}")
            self.logger.error(f"")
            self.logger.error(f"   Example: (\"examples/\", \"about\", \"about-nablarch\"),")
            self.logger.error(f"   If no existing type/category fits, add a new one.")
            raise SystemExit(1)

        write_json(self.ctx.classified_list_path, output)
        rel_path = os.path.relpath(self.ctx.classified_list_path, self.ctx.repo)
        self.logger.info(f"\n   💾Saved: {rel_path}")

        return output
