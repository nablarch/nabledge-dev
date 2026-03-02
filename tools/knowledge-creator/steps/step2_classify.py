"""Step 2: Classify source files by Type and Category."""

import os
from pathlib import Path
from .utils import load_json, write_json, utcnow_iso, log_info, log_error


def validate_path(path: str, allowed_parent: str) -> Path:
    """Validate that path is within allowed parent directory.

    Args:
        path: Path to validate
        allowed_parent: Allowed parent directory

    Returns:
        Resolved Path object

    Raises:
        ValueError: If path is outside allowed directory
    """
    resolved = Path(path).resolve()
    allowed = Path(allowed_parent).resolve()

    if not resolved.is_relative_to(allowed):
        raise ValueError(f"Path {path} is outside allowed directory {allowed_parent}")

    return resolved


# RST path to Type/Category mapping
# Match from top to bottom, first match wins
RST_MAPPING = [
    # processing-pattern
    ("application_framework/application_framework/batch/nablarch_batch", "processing-pattern", "nablarch-batch"),
    ("application_framework/application_framework/batch/jsr352", "processing-pattern", "jakarta-batch"),
    ("application_framework/application_framework/batch/", "processing-pattern", "nablarch-batch"),  # batch files including functional_comparison.rst
    ("application_framework/application_framework/web_service/rest", "processing-pattern", "restful-web-service"),
    ("application_framework/application_framework/web_service/http_messaging", "processing-pattern", "http-messaging"),
    ("application_framework/application_framework/web_service/", "processing-pattern", "restful-web-service"),  # web_service files including functional_comparison.rst
    ("application_framework/application_framework/web/", "processing-pattern", "web-application"),
    ("application_framework/application_framework/messaging/mom_messaging", "processing-pattern", "mom-messaging"),
    ("application_framework/application_framework/messaging/mom/", "processing-pattern", "mom-messaging"),  # MOM messaging subdirectories
    ("application_framework/application_framework/messaging/db_messaging", "processing-pattern", "db-messaging"),
    ("application_framework/application_framework/messaging/db/", "processing-pattern", "db-messaging"),  # DB messaging subdirectories

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
    ("application_framework/application_framework/setting_guide/", "setup", "setting-guide"),
    ("application_framework/setting_guide/", "setup", "setting-guide"),
    ("application_framework/application_framework/cloud_native/", "setup", "cloud-native"),

    # about
    ("about_nablarch/", "about", "about-nablarch"),
    ("application_framework/application_framework/nablarch_architecture/", "about", "about-nablarch"),
    ("application_framework/application_framework/nablarch/", "about", "about-nablarch"),  # nablarch directory
    ("migration/", "about", "migration"),
    ("release_notes/", "about", "release-notes"),

    # guide - biz_samples
    ("biz_samples/", "guide", "biz-samples"),
]

# MD (pattern collection) filename to Type/Category mapping
MD_MAPPING = {
    "Nablarchバッチ処理パターン.md": ("guide", "nablarch-patterns"),
    "Nablarchでの非同期処理.md": ("guide", "nablarch-patterns"),
    "Nablarchアンチパターン.md": ("guide", "nablarch-patterns"),
}

# Excel (security check table) filename to Type/Category mapping
XLSX_MAPPING = {
    "Nablarch機能のセキュリティ対応表.xlsx": ("check", "security-check"),
}


def generate_id(filename: str, format: str) -> str:
    """Generate knowledge file ID from source filename.

    Args:
        filename: Source filename
        format: File format (rst/md/xlsx)

    Returns:
        Knowledge file ID
    """
    if format == "rst":
        return filename.replace(".rst", "")
    elif format == "md":
        return filename.replace(".md", "")
    elif format == "xlsx":
        return "security-check"
    return filename


def classify_rst(source_path: str, repo_root: str) -> tuple:
    """Classify RST file by path.

    Args:
        source_path: Relative path to source file
        repo_root: Repository root directory for path validation

    Returns:
        Tuple of (type, category) or (None, None) if no match
    """
    # Validate path is within .lw/nab-official/
    allowed_parent = os.path.join(repo_root, ".lw/nab-official")
    try:
        validate_path(os.path.join(repo_root, source_path), allowed_parent)
    except ValueError as e:
        log_error(f"Path validation failed: {e}")
        return None, None

    # Extract path after "nablarch-document/ja/"
    marker = "nablarch-document/ja/"
    idx = source_path.find(marker)
    if idx < 0:
        return None, None

    relative = source_path[idx + len(marker):]

    # Match against mapping table
    for path_pattern, type_, category in RST_MAPPING:
        if relative.startswith(path_pattern):
            return type_, category

    return None, None


def classify_source(source: dict, repo_root: str) -> dict:
    """Classify a source file.

    Args:
        source: Source file info dict
        repo_root: Repository root directory for path validation

    Returns:
        Classified file info dict or None if no match
    """
    format_ = source["format"]
    filename = source["filename"]
    source_path = source["path"]

    if format_ == "rst":
        type_, category = classify_rst(source_path, repo_root)
        if not type_:
            return None

    elif format_ == "md":
        if filename not in MD_MAPPING:
            return None
        type_, category = MD_MAPPING[filename]

    elif format_ == "xlsx":
        if filename not in XLSX_MAPPING:
            return None
        type_, category = XLSX_MAPPING[filename]

    else:
        return None

    # Generate knowledge file ID
    file_id = generate_id(filename, format_)

    # Calculate output path
    output_path = f"{type_}/{category}/{file_id}.json"

    # Calculate assets directory
    assets_dir = f"{type_}/{category}/assets/{file_id}/"

    return {
        "source_path": source_path,
        "format": format_,
        "filename": filename,
        "type": type_,
        "category": category,
        "id": file_id,
        "output_path": output_path,
        "assets_dir": assets_dir
    }


def run(ctx):
    """Execute Step 2: Classify source files.

    Args:
        ctx: Context object
    """
    log_info(f"Classifying source files for version {ctx.version}")

    # Load source list
    if not os.path.exists(ctx.source_list_path):
        log_error(f"Source list not found: {ctx.source_list_path}")
        log_error("Please run Step 1 first")
        return

    sources_data = load_json(ctx.source_list_path)
    sources = sources_data["sources"]

    log_info(f"Classifying {len(sources)} source files")

    # Classify each source
    classified_files = []
    unmatched_files = []

    for source in sources:
        classified = classify_source(source, ctx.repo)
        if classified:
            classified_files.append(classified)
        else:
            unmatched_files.append(source)

    # Report unmatched files and ask user
    if unmatched_files:
        log_error(f"\n{len(unmatched_files)} files could not be classified:")
        for source in unmatched_files[:10]:
            log_error(f"  - {source['format']:4s} {source['path']}")
        if len(unmatched_files) > 10:
            log_error(f"  ... and {len(unmatched_files) - 10} more")
        log_error("\nPlease update mapping tables in step2_classify.py")

        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            log_info("Aborted by user")
            import sys
            sys.exit(1)

    # Prepare output
    output = {
        "version": ctx.version,
        "generated_at": utcnow_iso(),
        "files": classified_files
    }

    # Write output
    if not ctx.dry_run:
        write_json(ctx.classified_list_path, output)
        log_info(f"Wrote {len(classified_files)} classified files to {ctx.classified_list_path}")
    else:
        log_info(f"[DRY-RUN] Would write {len(classified_files)} classified files")
        print(f"\nSample classifications (first 5):")
        for file_info in classified_files[:5]:
            print(f"  - {file_info['type']:20s} {file_info['category']:20s} {file_info['id']}")

    log_info(f"Step 2 completed: {len(classified_files)} files classified, {len(unmatched_files)} unmatched")
