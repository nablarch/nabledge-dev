"""Step 2: Type/Category Classification

Classify source files into Type/Category based on path patterns.
Split large files into multiple entries if necessary.
"""

import os
import json
import re
from datetime import datetime
from .common import load_json, write_json, read_file


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
    """Filter file list for test mode using predefined test file set

    Includes split files if the original_id matches a test file ID.
    """
    result = []
    for f in classified:
        # Check direct match
        if f['id'] in test_file_ids:
            result.append(f)
        # Check if this is a split file with original_id in test set
        elif 'split_info' in f and f['split_info']['original_id'] in test_file_ids:
            result.append(f)
    return result


class Step2Classify:
    # Thresholds for file splitting
    FILE_LINE_THRESHOLD = 1000     # Split if file exceeds this
    SECTION_LINE_THRESHOLD = 1000  # Split if any section exceeds this

    def __init__(self, ctx, dry_run=False, sources_data=None):
        self.ctx = ctx
        self.dry_run = dry_run
        self.sources_data = sources_data

    def generate_id(self, filename: str, format: str, category: str = None) -> str:
        """Generate knowledge file ID from filename and category

        Args:
            filename: Source filename
            format: File format (rst/md/xlsx)
            category: Category from classification (optional)

        Returns:
            Unique file ID (category-filename format for rst/md)
        """
        base_name = None
        if format == "rst":
            base_name = filename.replace(".rst", "")
        elif format == "md":
            base_name = filename.replace(".md", "")
        elif format == "xlsx":
            return "security-check"
        else:
            base_name = filename

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
            return None, None

        rel_path = path[idx + len(marker):]

        # Try to match against RST_MAPPING
        for pattern, type_, category in RST_MAPPING:
            if pattern in rel_path:
                return type_, category

        return None, None

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
        """Check if file should be split based on file size or section sizes

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

        # Analyze sections
        sections = self.analyze_rst_sections(content)

        # Check if file exceeds FILE_LINE_THRESHOLD
        file_exceeds = total_lines > self.FILE_LINE_THRESHOLD

        # Check if any section exceeds SECTION_LINE_THRESHOLD
        has_large_section = any(s['line_count'] > self.SECTION_LINE_THRESHOLD for s in sections)

        # Split if either condition is true
        should_split = file_exceeds or has_large_section

        return should_split, sections, total_lines

    def split_file_entry(self, base_entry: dict, sections: list, content: str) -> list:
        """Split a file entry into multiple entries based on sections

        Args:
            base_entry: Original classified entry
            sections: List of h2 section info from analyze_rst_sections
            content: Full source file content

        Returns:
            List of split entries with section_range field
        """
        result = []
        base_id = base_entry['id']
        type_ = base_entry['type']
        category = base_entry['category']

        # Expand h2 sections into h3 subsections if they're too large
        expanded_sections = []
        for section in sections:
            if section['line_count'] > self.SECTION_LINE_THRESHOLD:
                # Try to split at h3 level
                h3_subsections = self.analyze_rst_h3_subsections(
                    content, section['start_line'], section['end_line']
                )

                if h3_subsections:
                    # Use h3 subsections
                    expanded_sections.extend(h3_subsections)
                    print(f"    Expanded h2 '{section['title']}' into {len(h3_subsections)} h3 subsections")
                else:
                    # No h3 subsections found, keep the large h2 section as-is
                    expanded_sections.append(section)
                    print(f"    WARNING: h2 '{section['title']}' has {section['line_count']} lines but no h3 subsections")
            else:
                expanded_sections.append(section)

        # Group sections to keep each part under threshold
        current_group = []
        current_lines = 0
        part_num = 1

        for section in expanded_sections:
            section_lines = section['line_count']

            # If adding this section would exceed threshold, start new part
            if current_group and (current_lines + section_lines > self.SECTION_LINE_THRESHOLD):
                # Save current group as a part
                split_id = f"{base_id}-{part_num}"
                result.append({
                    **base_entry,
                    'id': split_id,
                    'output_path': f"{type_}/{category}/{split_id}.json",
                    'assets_dir': f"{type_}/{category}/assets/{split_id}/",
                    'section_range': {
                        'start_line': current_group[0]['start_line'],
                        'end_line': current_group[-1]['end_line'],
                        'sections': [s['title'] for s in current_group]
                    },
                    'split_info': {
                        'is_split': True,
                        'part': part_num,
                        'original_id': base_id
                    }
                })

                # Start new group
                current_group = [section]
                current_lines = section_lines
                part_num += 1
            else:
                current_group.append(section)
                current_lines += section_lines

        # Add remaining sections as last part
        if current_group:
            split_id = f"{base_id}-{part_num}"
            result.append({
                **base_entry,
                'id': split_id,
                'output_path': f"{type_}/{category}/{split_id}.json",
                'assets_dir': f"{type_}/{category}/assets/{split_id}/",
                'section_range': {
                    'start_line': current_group[0]['start_line'],
                    'end_line': current_group[-1]['end_line'],
                    'sections': [s['title'] for s in current_group]
                },
                'split_info': {
                    'is_split': True,
                    'part': part_num,
                    'original_id': base_id
                }
            })

        return result

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
            if format == "rst":
                type_, category = self.classify_rst(path)
            elif format == "md":
                if filename in MD_MAPPING:
                    type_, category = MD_MAPPING[filename]
            elif format == "xlsx":
                if filename in XLSX_MAPPING:
                    type_, category = XLSX_MAPPING[filename]

            if type_ is None or category is None:
                unmatched.append({
                    "path": path,
                    "filename": filename,
                    "format": format
                })
                continue

            # Generate unique ID using category to avoid collisions
            file_id = self.generate_id(filename, format, category)

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
                print(f"   ✂️Split {entry['id']}: {total_lines} lines → {len(split_entries)} parts")
            else:
                final_classified.append(entry)

        if split_count > 0:
            print(f"\n   ✂️Split {split_count} large files into {len(final_classified) - len(classified) + split_count} total entries")

        classified = final_classified

        # Apply test mode filter if enabled
        if self.ctx.test_file:
            test_file_ids = load_test_file_ids(self.ctx.repo, self.ctx.test_file)
            original_count = len(classified)
            classified = filter_for_test(classified, test_file_ids)
            print(f"\n   🧪Test mode ({self.ctx.test_file}): Filtered {original_count} files → {len(classified)} test files")

            # Show missing test files (files in test set but not found in classified)
            # Include both direct IDs and original_ids from split files
            found_ids = {f['id'] for f in classified}
            found_ids.update({f['split_info']['original_id'] for f in classified if 'split_info' in f})
            missing = test_file_ids - found_ids
            if missing:
                print(f"   ⚠️WARNING: {len(missing)} test files not found:")
                for mid in sorted(missing):
                    print(f"      - {mid}")

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

        print(f"\n   📑Classified {len(classified)} files")

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
            print(f"      {type_emoji[type_name]}{type_name}: {count}")

            if count > 0:
                # Count by category
                category_counts = {}
                for f in type_files:
                    cat = f.get('category', 'unknown')
                    category_counts[cat] = category_counts.get(cat, 0) + 1

                # Sort categories by count (descending) then by name
                for cat in sorted(category_counts.keys(), key=lambda x: (-category_counts[x], x)):
                    emoji = category_emoji.get(cat, "📄")
                    print(f"         {emoji}{cat}: {category_counts[cat]}")

        if unmatched:
            print(f"\n   ⚠️WARNING: {len(unmatched)} files could not be classified:")
            for item in unmatched[:10]:  # Show first 10
                print(f"      {item['path']}")
            if len(unmatched) > 10:
                print(f"      ... and {len(unmatched) - 10} more")

        if not self.dry_run:
            write_json(self.ctx.classified_list_path, output)
            rel_path = os.path.relpath(self.ctx.classified_list_path, self.ctx.repo)
            print(f"\n   💾Saved: {rel_path}")

        return output
