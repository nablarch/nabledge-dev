#!/usr/bin/env python3
"""
Knowledge Creator - Clean Generated Files

Remove generated knowledge files and logs for specified version(s).
"""

import argparse
import os
import shutil
import sys


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
    """Remove directory if it exists."""
    if os.path.isdir(path):
        print(f"  Removing: {label}")
        shutil.rmtree(path)
        return True
    else:
        print(f"  (not found: {label})")
        return False


def clean_version(repo_root, version):
    """Clean generated files for a specific version."""
    print(f"\n{'='*60}")
    print(f"Cleaning version {version}")
    print(f"{'='*60}\n")

    removed_count = 0

    print("=== Removing Final Outputs ===")
    knowledge_dir = f"{repo_root}/.claude/skills/nabledge-{version}/knowledge"
    docs_dir = f"{repo_root}/.claude/skills/nabledge-{version}/docs"

    if remove_if_exists(knowledge_dir, f"nabledge-{version}/knowledge/"):
        removed_count += 1
    if remove_if_exists(docs_dir, f"nabledge-{version}/docs/"):
        removed_count += 1

    print("\n=== Removing Intermediate Artifacts ===")
    logs_dir = f"{repo_root}/tools/knowledge-creator/.logs/v{version}"

    if remove_if_exists(logs_dir, f".logs/v{version}/"):
        removed_count += 1

    print(f"\n{'='*60}")
    print(f"Version {version}: {removed_count} directories removed")
    print(f"{'='*60}")

    return removed_count


def main():
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

    args = parser.parse_args()

    # Determine repository root
    if args.repo:
        repo_root = args.repo
    else:
        repo_root = detect_repo_root()
        if repo_root is None:
            print("Error: Cannot detect repository root.")
            print("Please run from repository root or tools/knowledge-creator/")
            print("Or specify --repo /path/to/repository")
            sys.exit(1)

    # Validate repository root
    if not os.path.isdir(repo_root):
        print(f"Error: Repository path does not exist: {repo_root}")
        sys.exit(1)

    run_py = os.path.join(repo_root, "tools/knowledge-creator/run.py")
    if not os.path.exists(run_py):
        print(f"Error: Not a valid nabledge repository: {repo_root}")
        print(f"Missing: tools/knowledge-creator/run.py")
        sys.exit(1)

    print("="*60)
    print("Knowledge Creator - Clean Generated Files")
    print("="*60)
    print(f"\nRepository: {repo_root}")
    print(f"Version: {args.version}\n")

    # Determine versions to clean
    versions = ["6", "5"] if args.version == "all" else [args.version]

    total_removed = 0
    for version in versions:
        total_removed += clean_version(repo_root, version)

    print(f"\n{'='*60}")
    print(f"Clean complete. Total: {total_removed} directories removed")
    print("="*60)


if __name__ == "__main__":
    main()
