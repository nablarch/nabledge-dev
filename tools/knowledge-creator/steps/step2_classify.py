"""Step 2: Type/Category Classification

Classify source files into Type/Category based on path patterns.
"""

import os
import json
from datetime import datetime
from .common import load_json, write_json


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


def load_test_file_ids(repo_path: str) -> set:
    """Load test file IDs from test-files.json"""
    test_file_path = os.path.join(repo_path, "tools/knowledge-creator/test-files.json")

    if not os.path.exists(test_file_path):
        raise FileNotFoundError(f"Test file set not found: {test_file_path}")

    with open(test_file_path) as f:
        test_data = json.load(f)

    # Extract file IDs from the files array
    file_ids = set(test_data["files"])
    return file_ids


def filter_for_test(classified: list, test_file_ids: set) -> list:
    """Filter file list for test mode using predefined test file set"""
    return [f for f in classified if f['id'] in test_file_ids]


class Step2Classify:
    def __init__(self, ctx, dry_run=False, sources_data=None):
        self.ctx = ctx
        self.dry_run = dry_run
        self.sources_data = sources_data

    def generate_id(self, filename: str, format: str) -> str:
        """Generate knowledge file ID from filename"""
        if format == "rst":
            return filename.replace(".rst", "")
        elif format == "md":
            return filename.replace(".md", "")
        elif format == "xlsx":
            return "security-check"
        return filename

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
            file_id = self.generate_id(filename, format)

            # Classify based on format
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

        # Apply test mode filter if enabled
        if self.ctx.test_mode:
            test_file_ids = load_test_file_ids(self.ctx.repo)
            original_count = len(classified)
            classified = filter_for_test(classified, test_file_ids)
            print(f"\nTest mode: Filtered {original_count} files to {len(classified)} test files")

            # Show missing test files (files in test set but not found in classified)
            found_ids = {f['id'] for f in classified}
            missing = test_file_ids - found_ids
            if missing:
                print(f"WARNING: {len(missing)} test files not found in classified list:")
                for mid in sorted(missing):
                    print(f"  - {mid}")

        # Generate output
        output = {
            "version": self.ctx.version,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "files": classified
        }

        print(f"\nClassified {len(classified)} files")
        print(f"  processing-pattern: {sum(1 for f in classified if f['type'] == 'processing-pattern')}")
        print(f"  component: {sum(1 for f in classified if f['type'] == 'component')}")
        print(f"  development-tools: {sum(1 for f in classified if f['type'] == 'development-tools')}")
        print(f"  setup: {sum(1 for f in classified if f['type'] == 'setup')}")
        print(f"  about: {sum(1 for f in classified if f['type'] == 'about')}")
        print(f"  guide: {sum(1 for f in classified if f['type'] == 'guide')}")
        print(f"  check: {sum(1 for f in classified if f['type'] == 'check')}")

        if unmatched:
            print(f"\nWARNING: {len(unmatched)} files could not be classified:")
            for item in unmatched[:10]:  # Show first 10
                print(f"  {item['path']}")
            if len(unmatched) > 10:
                print(f"  ... and {len(unmatched) - 10} more")

        if not self.dry_run:
            write_json(self.ctx.classified_list_path, output)
            print(f"\nWrote: {self.ctx.classified_list_path}")

        return output
