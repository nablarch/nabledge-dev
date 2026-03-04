#!/usr/bin/env python3
"""
Knowledge Creator - Clean Generated Files

Remove generated knowledge files and logs for specified version(s).
"""

import argparse
import os
import shutil
import sys

# Add steps directory to path for logger import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'steps'))
from logger import get_logger


def detect_repo_root():
    """Detect repository root from current directory."""
    cwd = os.getcwd()

    # Check if running from repository root
    if os.path.exists(os.path.join(cwd, "tools/knowledge-creator/run.py")):
        return cwd

    # Check if running from tools/knowledge-creator directory
    if os.path.exists(os.path.join(cwd, "run.py")):
        return os.path.abspath(os.path.join(cwd, "../.."))

    # Cannot detect
    return None


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
        choices=["6", "5", "all"],
        help="Version to clean (6, 5, or all)"
    )
    parser.add_argument(
        "--repo",
        default=None,
        help="Repository root path (default: auto-detect from current directory)"
    )
    parser.add_argument("--yes", action="store_true",
                        help="Skip confirmation prompt")

    args = parser.parse_args()

    # Determine repository root
    if args.repo:
        repo_root = args.repo
    else:
        repo_root = detect_repo_root()
        if repo_root is None:
            logger.error("Error: Cannot detect repository root.")
            logger.info("Please run from repository root or tools/knowledge-creator/")
            logger.info("Or specify --repo /path/to/repository")
            sys.exit(1)

    # Validate repository root
    if not os.path.isdir(repo_root):
        logger.error(f"Error: Repository path does not exist: {repo_root}")
        sys.exit(1)

    run_py = os.path.join(repo_root, "tools/knowledge-creator/run.py")
    if not os.path.exists(run_py):
        logger.error(f"Error: Not a valid nabledge repository: {repo_root}")
        logger.info(f"Missing: tools/knowledge-creator/run.py")
        sys.exit(1)

    logger.info("="*60)
    logger.info("Knowledge Creator - Clean Generated Files")
    logger.info("="*60)
    logger.info(f"\nRepository: {repo_root}")
    logger.info(f"Version: {args.version}\n")

    # Determine versions to clean
    versions = ["6", "5"] if args.version == "all" else [args.version]

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
