#!/usr/bin/env python3
"""Migration: Add processing_patterns to existing knowledge cache files.

Fixes two problems in .cache/v6/knowledge/:
1. Files missing top-level 'processing_patterns' field
2. S3/S4 errors from index/sections inconsistency (specific files)

Usage:
    python migrate_add_processing_patterns.py [--version 6] [--dry-run]
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from common import load_json, write_json
from logger import get_logger

# S3/S4 specific fixes: {file_id: list of fix functions}
# Each fix function takes (knowledge_data) and returns modified data
SPECIFIC_FIXES = {
    "libraries-data_bind--sec-cd48d52b": "fix_data_bind_sec",
    "libraries-data_bind--csv": "fix_data_bind_csv",
    "handlers-jaxrs_access_log_handler--sec-2a8f8aeb": "fix_jaxrs_handler",
}

VALID_PROCESSING_PATTERNS = {
    "nablarch-batch", "jakarta-batch", "restful-web-service",
    "http-messaging", "web-application", "mom-messaging", "db-messaging"
}


def fix_data_bind_sec(knowledge):
    """Fix libraries-data_bind--sec-cd48d52b:
    - S4: sections key 'section-extension' has no corresponding index entry
    - Fix: Rename 'section-extension' -> 'extension' in sections, add index entry
    """
    sections = knowledge.get("sections", {})
    index = knowledge.get("index", [])

    if "section-extension" in sections and "extension" not in sections:
        content = sections.pop("section-extension")
        sections["extension"] = content
        # Add index entry for 'extension'
        index_ids = {e["id"] for e in index}
        if "extension" not in index_ids:
            index.append({
                "id": "extension",
                "title": "拡張",
                "hints": ["ObjectMapper", "ObjectMapperFactory", "ファイル形式追加", "ObjectMapper拡張"]
            })
        knowledge["sections"] = sections
        knowledge["index"] = index
    return knowledge


def fix_data_bind_csv(knowledge):
    """Fix libraries-data_bind--csv:
    - S3: index[].id 'extension' has no corresponding section
    - Fix: Remove orphan 'extension' index entry (content was moved to sec-cd48d52b)
    """
    index = knowledge.get("index", [])
    sections = knowledge.get("sections", {})

    if "extension" in {e["id"] for e in index} and "extension" not in sections:
        knowledge["index"] = [e for e in index if e["id"] != "extension"]
    return knowledge


def fix_jaxrs_handler(knowledge):
    """Fix handlers-jaxrs_access_log_handler--sec-2a8f8aeb:
    - S4: sections key 'processing-patterns' has no corresponding index entry
    - Fix: Remove 'processing-patterns' from sections, use value for processing_patterns
    """
    sections = knowledge.get("sections", {})
    index = knowledge.get("index", [])

    pp_content = sections.pop("processing-patterns", None)

    # Remove from index if present
    knowledge["index"] = [e for e in index if e["id"] != "processing-patterns"]
    knowledge["sections"] = sections

    # Set processing_patterns from sections content if not already set
    if "processing_patterns" not in knowledge and pp_content:
        if isinstance(pp_content, str):
            # Content might be a pattern name like "restful-web-service"
            stripped = pp_content.strip()
            if stripped in VALID_PROCESSING_PATTERNS:
                knowledge["processing_patterns"] = [stripped]
            else:
                # Try to parse multiple patterns
                patterns = [p.strip() for p in stripped.split(",") if p.strip() in VALID_PROCESSING_PATTERNS]
                knowledge["processing_patterns"] = patterns
        elif isinstance(pp_content, list):
            knowledge["processing_patterns"] = [p for p in pp_content if p in VALID_PROCESSING_PATTERNS]
    return knowledge


SPECIFIC_FIX_FUNCTIONS = {
    "libraries-data_bind--sec-cd48d52b": fix_data_bind_sec,
    "libraries-data_bind--csv": fix_data_bind_csv,
    "handlers-jaxrs_access_log_handler--sec-2a8f8aeb": fix_jaxrs_handler,
}


def compute_processing_patterns(file_info):
    """Compute processing_patterns from file_info type/category."""
    if file_info.get("type") == "processing-pattern":
        return [file_info["category"]]
    return []


def run_migration(version="6", repo=None, dry_run=False):
    """Run the migration."""
    logger = get_logger()

    if repo is None:
        repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

    cache_dir = os.path.join(repo, "tools", "knowledge-creator", ".cache", f"v{version}")
    catalog_path = os.path.join(cache_dir, "catalog.json")
    knowledge_cache_dir = os.path.join(cache_dir, "knowledge")

    if not os.path.exists(catalog_path):
        logger.error(f"Catalog not found: {catalog_path}")
        return False

    catalog = load_json(catalog_path)
    files = catalog["files"]

    stats = {"total": 0, "pp_added": 0, "specific_fixed": 0, "errors": 0, "skipped": 0}

    for fi in files:
        file_id = fi["id"]
        cache_path = os.path.join(knowledge_cache_dir, fi["output_path"])

        if not os.path.exists(cache_path):
            stats["skipped"] += 1
            continue

        stats["total"] += 1
        modified = False

        try:
            knowledge = load_json(cache_path)
        except Exception as e:
            logger.error(f"Failed to load {file_id}: {e}")
            stats["errors"] += 1
            continue

        # Apply specific fixes for known S3/S4 errors
        if file_id in SPECIFIC_FIX_FUNCTIONS:
            fix_fn = SPECIFIC_FIX_FUNCTIONS[file_id]
            original = json.dumps(knowledge, sort_keys=True)
            knowledge = fix_fn(knowledge)
            if json.dumps(knowledge, sort_keys=True) != original:
                logger.info(f"  [FIX] {file_id}: applied specific fix")
                modified = True
                stats["specific_fixed"] += 1

        # Add processing_patterns if missing
        if "processing_patterns" not in knowledge:
            knowledge["processing_patterns"] = compute_processing_patterns(fi)
            logger.info(f"  [PP] {file_id}: added processing_patterns={knowledge['processing_patterns']}")
            modified = True
            stats["pp_added"] += 1

        # Write if modified
        if modified and not dry_run:
            write_json(cache_path, knowledge)

    # Update catalog with processing_patterns from cache files
    if not dry_run:
        for fi in files:
            cache_path = os.path.join(knowledge_cache_dir, fi["output_path"])
            if os.path.exists(cache_path):
                try:
                    knowledge = load_json(cache_path)
                    fi["processing_patterns"] = knowledge.get("processing_patterns", [])
                except Exception:
                    pass
        write_json(catalog_path, catalog)
        logger.info(f"\n  Catalog updated with processing_patterns.")

    dry_label = " (DRY RUN)" if dry_run else ""
    logger.info(f"\n  Migration complete{dry_label}:")
    logger.info(f"    Total files:       {stats['total']}")
    logger.info(f"    Specific fixes:    {stats['specific_fixed']}")
    logger.info(f"    PP added:          {stats['pp_added']}")
    logger.info(f"    Errors:            {stats['errors']}")
    logger.info(f"    Skipped (missing): {stats['skipped']}")

    return stats["errors"] == 0


def main():
    parser = argparse.ArgumentParser(description="Migrate knowledge cache files to add processing_patterns")
    parser.add_argument("--version", default="6", help="Version (default: 6)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no file changes)")
    parser.add_argument("--repo", default=None, help="Repository root path")
    args = parser.parse_args()

    success = run_migration(version=args.version, repo=args.repo, dry_run=args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
