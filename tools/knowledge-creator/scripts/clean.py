#!/usr/bin/env python3
"""
Knowledge Creator - Clean Generated Files

Remove generated knowledge files and logs for specified version(s).
"""

import argparse
import json
import os
import shutil
import sys

from logger import get_logger


def detect_repo_root():
    """Detect repository root from this script's location."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


def remove_if_exists(path, label):
    logger = get_logger()
    """Remove directory if it exists."""
    if os.path.isdir(path):
        logger.info(f"  Removing: {label}")
        shutil.rmtree(path)
        return True
    else:
        logger.info(f"  (not found: {label})")
        return False


def _load_catalog_sources(catalog_path, logger):
    """Load sources from catalog.json if it exists and has non-empty sources."""
    if not os.path.exists(catalog_path):
        return None
    try:
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
        sources = catalog.get("sources", [])
        if sources:
            logger.info(f"  Preserving {len(sources)} source(s) from catalog.json")
        return sources or None
    except (json.JSONDecodeError, OSError):
        return None


def _restore_catalog_sources(cache_dir, catalog_path, version, sources, logger):
    """Write a minimal catalog.json containing only the preserved sources."""
    try:
        os.makedirs(cache_dir, exist_ok=True)
        with open(catalog_path, 'w', encoding='utf-8') as f:
            json.dump({"version": version, "sources": sources}, f, ensure_ascii=False, indent=2)
        logger.info(f"  Restored sources to catalog.json")
    except OSError as e:
        logger.warning(f"  Failed to restore sources to catalog.json: {e}")


def clean_version(repo_root, version):
    logger = get_logger()
    """Clean generated files for a specific version."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Cleaning version {version}")
    logger.info(f"{'='*60}\n")

    removed_count = 0

    logger.info("=== Removing Final Outputs ===")
    knowledge_dir = f"{repo_root}/.claude/skills/nabledge-{version}/knowledge"
    docs_dir = f"{repo_root}/.claude/skills/nabledge-{version}/docs"

    if remove_if_exists(knowledge_dir, f"nabledge-{version}/knowledge/"):
        removed_count += 1
    if remove_if_exists(docs_dir, f"nabledge-{version}/docs/"):
        removed_count += 1

    cache_dir = f"{repo_root}/tools/knowledge-creator/.cache/v{version}"
    catalog_path = os.path.join(cache_dir, "catalog.json")
    preserved_sources = _load_catalog_sources(catalog_path, logger)
    if remove_if_exists(cache_dir, f".cache/v{version}/"):
        removed_count += 1
    if preserved_sources:
        _restore_catalog_sources(cache_dir, catalog_path, version, preserved_sources, logger)

    logger.info("\n=== Removing Intermediate Artifacts ===")
    logs_dir = f"{repo_root}/tools/knowledge-creator/.logs/v{version}"

    if remove_if_exists(logs_dir, f".logs/v{version}/"):
        removed_count += 1

    logger.info(f"\n{'='*60}")
    logger.info(f"Version {version}: {removed_count} directories removed")
    logger.info(f"{'='*60}")

    return removed_count


def main():
    logger = get_logger()
    parser = argparse.ArgumentParser(
        description="Clean generated knowledge files and logs"
    )
    parser.add_argument(
        "--version",
        required=True,
        choices=["6", "5", "1.4", "1.3", "1.2", "all"],
        help="Version to clean (6, 5, 1.4, 1.3, 1.2, or all)"
    )
    parser.add_argument("--yes", action="store_true",
                        help="Skip confirmation prompt")

    args = parser.parse_args()

    repo_root = detect_repo_root()

    logger.info("="*60)
    logger.info("Knowledge Creator - Clean Generated Files")
    logger.info("="*60)
    logger.info(f"\nRepository: {repo_root}")
    logger.info(f"Version: {args.version}\n")

    # Determine versions to clean
    versions = ["6", "5", "1.4", "1.3", "1.2"] if args.version == "all" else [args.version]

    if not args.yes:
        answer = input(f"\nVersion {args.version} の全成果物を削除します。続行しますか？ [y/N]: ")
        if answer.lower() != "y":
            print("中止しました")
            sys.exit(0)

    total_removed = 0
    for version in versions:
        total_removed += clean_version(repo_root, version)

    logger.info(f"\n{'='*60}")
    logger.info(f"Clean complete. Total: {total_removed} directories removed")
    logger.info("="*60)


if __name__ == "__main__":
    main()
