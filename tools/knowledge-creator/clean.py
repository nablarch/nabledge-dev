#!/usr/bin/env python3
"""Clean generated files from knowledge creator

Usage:
    python3 tools/knowledge-creator/clean.py --version 6
    python3 tools/knowledge-creator/clean.py --version 6 --logs  # Also clean logs
"""

import os
import shutil
import argparse


def clean_knowledge_files(version: int, repo: str):
    """Clean generated knowledge files and docs"""
    if version == 6:
        knowledge_dir = f"{repo}/.claude/skills/nabledge-6/knowledge"
        docs_dir = f"{repo}/.claude/skills/nabledge-6/docs"
    elif version == 5:
        knowledge_dir = f"{repo}/.claude/skills/nabledge-5/knowledge"
        docs_dir = f"{repo}/.claude/skills/nabledge-5/docs"
    else:
        print(f"Unknown version: {version}")
        return

    # Clean knowledge files
    if os.path.exists(knowledge_dir):
        for item in os.listdir(knowledge_dir):
            item_path = os.path.join(knowledge_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Removed directory: {item_path}")
            elif os.path.isfile(item_path):
                os.remove(item_path)
                print(f"Removed file: {item_path}")
    else:
        print(f"Knowledge directory not found: {knowledge_dir}")

    # Clean docs
    if os.path.exists(docs_dir):
        for item in os.listdir(docs_dir):
            item_path = os.path.join(docs_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Removed directory: {item_path}")
            elif os.path.isfile(item_path):
                os.remove(item_path)
                print(f"Removed file: {item_path}")
    else:
        print(f"Docs directory not found: {docs_dir}")


def clean_logs(version: int, repo: str):
    """Clean log files"""
    log_dir = f"{repo}/tools/knowledge-creator/logs/v{version}"

    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
        print(f"Removed log directory: {log_dir}")
    else:
        print(f"Log directory not found: {log_dir}")


def clean_cache(repo: str):
    """Clean Python cache files"""
    cache_dirs = [
        f"{repo}/tools/knowledge-creator/__pycache__",
        f"{repo}/tools/knowledge-creator/steps/__pycache__"
    ]

    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"Removed cache directory: {cache_dir}")
        else:
            print(f"Cache directory not found: {cache_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Clean generated files from knowledge creator"
    )
    parser.add_argument(
        "--version",
        type=int,
        choices=[6, 5],
        required=True,
        help="Version to clean (6 or 5)"
    )
    parser.add_argument(
        "--logs",
        action="store_true",
        help="Also clean log files"
    )
    parser.add_argument(
        "--repo",
        default=os.getcwd(),
        help="Repository root path (default: current directory)"
    )

    args = parser.parse_args()

    print(f"Cleaning generated files for version {args.version}...")
    print(f"Repository: {args.repo}\n")

    # Always clean knowledge files, docs, and cache
    clean_knowledge_files(args.version, args.repo)
    clean_cache(args.repo)

    # Optionally clean logs
    if args.logs:
        print("\nCleaning logs...")
        clean_logs(args.version, args.repo)

    print("\n✓ Cleanup complete")


if __name__ == "__main__":
    main()
