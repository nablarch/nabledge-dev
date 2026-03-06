"""Step 2: Type/Category Classification

Classify source files into Type/Category based on path patterns.
Split large files into multiple entries if necessary.
"""

import os
import json
import re
from datetime import datetime
from .common import load_json, write_json, read_file
from .logger import get_logger


# RST path-based mapping (evaluated in order, first match wins)
RST_MAPPING = [
    # processing-pattern
    ("application_framework/application_framework/batch/nablarch_batch", "processing-pattern", "nablarch-batch"),
    ("application_framework/application_framework/batch/jsr352", "processing-pattern", "jakarta-batch"),
    ("application_framework/application_framework/batch/", "processing-pattern", "nablarch-batch"),  # Catch-all for batch
    ("application_framework/application_framework/web_service/rest", "processing-pattern", "restful-web-service"),
    ("application_framework/application_framework/web_service/http_messaging", "processing-pattern", "http-messaging"),
    ("application_framework/application_framework/web_service/", "processing-pattern", "restful-web-service"),  # Catch-all for web_service
    ("application_framework/application_framework/web/", "processing-pattern", "web-application"),
    ("application_framework/application_framework/messaging/mom", "processing-pattern", "mom-messaging"),
    ("application_framework/application_framework/messaging/db", "processing-pattern", "db-messaging"),

    # component - handlers
    ("application_framework/application_framework/handlers/", "component", "handlers"),
    ("application_framework/application_framework/batch/jBatchHandler", "component", "handlers"),

    # component - libraries
    ("application_framework/application_framework/libraries/", "component", "libraries"),

    # component - adapters
    ("application_framework/adaptors/", "component", "adapters"),

    # development-tools
    ("development_tools/testing_framework/", "development-tools", "testing-framework"),
    ("development_tools/toolbox/", "development-tools", "toolbox"),
    ("development_tools/java_static_analysis/", "development-tools", "java-static-analysis"),

    # setup
    ("application_framework/application_framework/blank_project/", "setup", "blank-project"),
    ("application_framework/application_framework/configuration/", "setup", "configuration"),
    ("application_framework/setting_guide/", "setup", "setting-guide"),
    ("application_framework/application_framework/cloud_native/", "setup", "cloud-native"),

    # about
    ("about_nablarch/", "about", "about-nablarch"),
    ("application_framework/application_framework/nablarch_architecture/", "about", "about-nablarch"),
    ("application_framework/application_framework/nablarch/", "about", "about-nablarch"),
    ("migration/", "about", "migration"),
    ("release_notes/", "about", "release-notes"),

    # biz_samples - examples and utilities
    ("biz_samples/", "about", "about-nablarch"),

    # messaging intermediate page
    ("application_framework/application_framework/messaging/", "processing-pattern", "db-messaging"),

    # Standalone content pages
    ("examples/", "about", "about-nablarch"),
    ("external_contents/", "about", "about-nablarch"),
    ("inquiry/", "about", "about-nablarch"),
    ("jakarta_ee/", "about", "about-nablarch"),
    ("nablarch_api/", "about", "about-nablarch"),
    ("releases/", "about", "release-notes"),
    ("terms_of_use/", "about", "about-nablarch"),

    # Intermediate toctree pages (will be no_knowledge_content in Phase B)
    ("application_framework/application_framework/", "about", "about-nablarch"),
    ("application_framework/", "about", "about-nablarch"),
    ("development_tools/", "development-tools", "testing-framework"),
]

# MD filename-based mapping
MD_MAPPING = {
    "Nablarchバッチ処理パターン.md": ("guide", "nablarch-patterns"),
    "Nablarchでの非同期処理.md": ("guide", "nablarch-patterns"),
    "Nablarchアンチパターン.md": ("guide", "nablarch-patterns"),
}

# Excel filename-based mapping
XLSX_MAPPING = {
    "Nablarch機能のセキュリティ対応表.xlsx": ("check", "security-check"),
}


def classify_excel_by_pattern(filename: str) -> tuple:
    """Classify Excel file by filename pattern.

    Returns:
        (type, category) tuple or None if no match
    """
    # Release notes: *-releasenote.xlsx (covers both v5 and v6)
    if filename.endswith("-releasenote.xlsx"):
        return ("releases", "releases")

    return None


def load_test_file_ids(repo_path: str, test_file_name: str) -> set:
    """Load test file IDs from specified test file"""
    test_file_path = os.path.join(repo_path, "tools/knowledge-creator", test_file_name)

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
    SPLIT_SECTION_THRESHOLD = 2  # h2セクションがこの数以上あれば分割
    LINE_GROUP_THRESHOLD = 400  # セクションをグループ化する行数の閾値（h3展開とグループ化の両方に使用）

    def __init__(self, ctx, dry_run=False, sources_data=None):
        self.ctx = ctx
        self.dry_run = dry_run
        self.sources_data = sources_data
        self.logger = get_logger()

    def generate_id(self, filename: str, format: str, category: str = None,
                    source_path: str = None, matched_pattern: str = None) -> str:
        """Generate knowledge file ID from filename and category

        Args:
            filename: Source filename
            format: File format (rst/md/xlsx)
            category: Category from classification (optional)
            source_path: Source file path for index.rst disambiguation (optional)
            matched_pattern: RST_MAPPING pattern that matched (optional, for index.rst)

        Returns:
            Unique file ID (category-filename format for rst/md)
        """
        # For Excel files in XLSX_MAPPING, use category as ID (fixed mapping)
        if format == "xlsx" and filename in XLSX_MAPPING:
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
            marker = "nablarch-document/ja/"
            marker_idx = source_path.find(marker)
            if marker_idx >= 0:
                rst_rel = source_path[marker_idx + len(marker):]
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
        # Extract path after nablarch-document/ja/
        marker = "nablarch-document/ja/"
        idx = path.find(marker)
        if idx < 0:
            return None, None, None

        rel_path = path[idx + len(marker):]

        # Top-level index.rst: no RST_MAPPING pattern can match "index.rst" alone
        # because "" would match everything. Handle explicitly.
        if rel_path == "index.rst":
            return "about", "about-nablarch", ""

        # Try to match against RST_MAPPING
        for pattern, type_, category in RST_MAPPING:
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
        # h3 can be marked with various underlines: ^^^^^ ~~~~~ +++++ etc.
        # Exclude ----- (h2) and ===== (h1)
        h3_pattern = re.compile(r'^[\^~+*.]{5,}$')

        for i in range(h2_start, h2_end - 1):
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # Check if next line is an h3 marker (not h1/h2)
                if h3_pattern.match(next_line) and not re.match(r'^[-=]{5,}$', next_line):
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

        # h2セクションが2個以上あれば分割
        should_split = len(sections) >= self.SPLIT_SECTION_THRESHOLD
        return should_split, sections, total_lines

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

        # Step 3: 各グループからエントリを生成
        result = self._generate_entries_from_groups(base_entry, groups)

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

    def _generate_entries_from_groups(self, base_entry: dict, groups: list) -> list:
        """Generate split entries from section groups.

        Args:
            base_entry: Original classified entry
            groups: List of section groups

        Returns:
            List of split entries
        """
        result = []
        base_id = base_entry['id']
        type_ = base_entry['type']
        category = base_entry['category']
        total_parts = len(groups)
        used_ids = set()  # 同一ファイル内のID重複を回避

        for part_num, group in enumerate(groups, 1):
            # Use first section's ID for the group ID
            first_section = group[0]
            section_id = self._title_to_section_id(first_section['title'])

            # 重複回避: 同じsection_idが既出なら連番を付与
            original_section_id = section_id
            counter = 2
            while section_id in used_ids:
                section_id = f"{original_section_id}-{counter}"
                counter += 1
            used_ids.add(section_id)
            split_id = f"{base_id}--{section_id}"

            # Calculate group line range
            start_line = group[0]['start_line']
            end_line = group[-1]['end_line']
            group_line_count = sum(s['line_count'] for s in group)

            # Collect all section titles in this group
            section_titles = [s['title'] for s in group]

            result.append({
                **base_entry,
                'id': split_id,
                'output_path': f"{type_}/{category}/{split_id}.json",
                'assets_dir': f"{type_}/{category}/assets/{split_id}/",
                'section_range': {
                    'start_line': start_line,
                    'end_line': end_line,
                    'sections': section_titles
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

    @staticmethod
    def _title_to_section_id(title: str) -> str:
        """Convert section title to a safe, deterministic ID string.

        ASCII英数字部分を抽出。十分な長さがなければmd5ハッシュを使う。

        Examples:
            "HTMLエスケープ漏れを防げる" -> "html"
            "module-list" -> "module-list"
            "モジュール一覧" -> "sec-xxxxxxxx" (md5ハッシュ)
            "DefaultMeterBinderListProvider" -> "defaultmeterbinderlistprovider"
        """
        import hashlib
        # ASCII英数字とハイフンのみ残す
        ascii_id = re.sub(r'[^a-zA-Z0-9-]', '', title.replace(' ', '-')).lower().strip('-')
        # 連続ハイフンを1つに
        ascii_id = re.sub(r'-+', '-', ascii_id)
        if ascii_id and len(ascii_id) >= 3:
            return ascii_id[:50]
        # 日本語タイトル等: md5ハッシュの先頭8文字
        h = hashlib.md5(title.encode('utf-8')).hexdigest()[:8]
        return f"sec-{h}"

    def run(self):
        """Execute Step 2: Classify all source files"""
        # Use cached data in dry-run mode, otherwise load from file
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
                if filename in MD_MAPPING:
                    type_, category = MD_MAPPING[filename]
            elif format == "xlsx":
                if filename in XLSX_MAPPING:
                    type_, category = XLSX_MAPPING[filename]
                else:
                    result = classify_excel_by_pattern(filename)
                    if result:
                        type_, category = result

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
                final_classified.extend(split_entries)
                split_count += 1
                self.logger.info(f"   ✂️Split {entry['id']}: {total_lines} lines → {len(split_entries)} parts")
            else:
                final_classified.append(entry)

        if split_count > 0:
            self.logger.info(f"\n   ✂️Split {split_count} large files into {len(final_classified) - len(classified) + split_count} total entries")

        classified = final_classified

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

        # Generate output
        output = {
            "version": self.ctx.version,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "files": classified
        }

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
        type_order = ['processing-pattern', 'component', 'development-tools', 'setup', 'about', 'guide', 'check']
        type_emoji = {
            'processing-pattern': '🔄',
            'component': '🧩',
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
            self.logger.error(f"   Add a mapping for each file to RST_MAPPING in:")
            self.logger.error(f"   tools/knowledge-creator/steps/step2_classify.py")
            self.logger.error(f"")
            self.logger.error(f"   Unmapped files:")
            for item in unmatched:
                self.logger.error(f"     {item['path']}")
            self.logger.error(f"")
            self.logger.error(f"   Example: (\"examples/\", \"about\", \"about-nablarch\"),")
            self.logger.error(f"   If no existing type/category fits, add a new one.")
            raise SystemExit(1)

        if not self.dry_run:
            write_json(self.ctx.classified_list_path, output)
            rel_path = os.path.relpath(self.ctx.classified_list_path, self.ctx.repo)
            self.logger.info(f"\n   💾Saved: {rel_path}")

        return output
