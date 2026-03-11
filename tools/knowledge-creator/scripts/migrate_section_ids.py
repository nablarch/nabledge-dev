#!/usr/bin/env python3
"""Migrate knowledge JSON section IDs from kebab-case to sequential (s1, s2, ...).

Strategy: Use index array order in each knowledge JSON file.
index[0].id -> s1, index[1].id -> s2, ...

Also:
- Renames split files to match new catalog output_paths (--s1.json, --s2.json, etc.)
- Removes processing_patterns field from all knowledge JSON files

Process:
1. Update content (section IDs) of all existing files
2. Rename split files to match new catalog naming convention
"""
import os
import re
import sys
import glob
import json
import shutil
import argparse


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def migrate_file_content(path, stats):
    """Update section IDs and remove processing_patterns in a knowledge JSON file."""
    data = load_json(path)

    # processing_patterns を削除
    if "processing_patterns" in data:
        del data["processing_patterns"]
        stats["pp_removed"] += 1

    # no_knowledge_content=true はセクションなし → スキップ
    if data.get("no_knowledge_content"):
        write_json(path, data)
        stats["skipped"] += 1
        return

    index = data.get("index", [])
    if not index:
        write_json(path, data)
        stats["skipped"] += 1
        return

    # index順で old_id -> new_id マッピングを構築
    mapping = {}
    for i, entry in enumerate(index, start=1):
        old_id = entry["id"]
        new_id = f"s{i}"
        mapping[old_id] = new_id

    # index-section不整合を修正（Issue #150 bugs: 3件）
    idx_ids = set(mapping.keys())
    sec_keys = set(data.get("sections", {}).keys())
    orphan_sections = sec_keys - idx_ids
    orphan_index = idx_ids - sec_keys
    if orphan_sections or orphan_index:
        stats["inconsistency_fixed"] += 1
        for orphan_key in orphan_sections:
            del data["sections"][orphan_key]
            print(f"  Removed orphan section key: {orphan_key} in {os.path.basename(path)}")
        for oid in orphan_index:
            del mapping[oid]
            data["index"] = [e for e in data["index"] if e["id"] != oid]
            print(f"  Removed orphan index entry: {oid} in {os.path.basename(path)}")
        # mapping を再構築
        mapping = {}
        for i, entry in enumerate(data["index"], start=1):
            mapping[entry["id"]] = f"s{i}"

    # index[].id をリネーム
    for entry in data["index"]:
        entry["id"] = mapping[entry["id"]]

    # sections のキーをリネーム + 内部参照を更新
    new_sections = {}
    for old_key, content in data.get("sections", {}).items():
        new_key = mapping.get(old_key, old_key)
        for old_id, new_id in mapping.items():
            content = re.sub(
                r'\(#' + re.escape(old_id) + r'\)',
                f'(#{new_id})',
                content
            )
        new_sections[new_key] = content
    data["sections"] = new_sections

    write_json(path, data)
    stats["migrated"] += 1


def rename_split_files(knowledge_cache_dir, catalog_path, stats):
    """Rename split files in cache to match new catalog output_paths.

    The catalog was regenerated with new sequential IDs (--s1, --s2, etc.).
    Existing files use old kebab-case IDs (--sec-cd48d52b, etc.).
    This function renames files to match the catalog.
    """
    catalog = load_json(catalog_path)
    files = catalog.get("files", [])

    # Build a map: (original_id, part) -> new_output_path
    split_entries = {}
    for fi in files:
        si = fi.get("split_info")
        if si and si.get("is_split"):
            key = (si["original_id"], si["part"])
            split_entries[key] = fi["output_path"]

    if not split_entries:
        return

    # Find all split files in cache
    all_cache_files = glob.glob(f"{knowledge_cache_dir}/**/*.json", recursive=True)
    renamed = 0
    for path in all_cache_files:
        if '/assets/' in path:
            continue
        try:
            data = load_json(path)
        except Exception:
            continue
        si = data.get("split_info")
        if not si or not si.get("is_split"):
            continue
        key = (si.get("original_id"), si.get("part"))
        new_output_path = split_entries.get(key)
        if not new_output_path:
            continue

        new_path = os.path.join(knowledge_cache_dir, new_output_path)
        if os.path.abspath(path) != os.path.abspath(new_path):
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            shutil.move(path, new_path)

            # Also update "id" field inside the file
            file_id = os.path.basename(new_path).replace(".json", "")
            if data.get("id") != file_id:
                data["id"] = file_id
                write_json(new_path, data)

            renamed += 1

    stats["renamed"] = renamed
    print(f"  Renamed {renamed} split files to match new catalog naming")


def verify(knowledge_cache_dir):
    """Verify all section IDs are in s{N} format and no processing_patterns remain."""
    errors = []
    pattern = re.compile(r'^s\d+$')
    for p in glob.glob(f'{knowledge_cache_dir}/**/*.json', recursive=True):
        if '/assets/' in p:
            continue
        data = load_json(p)
        if data.get('no_knowledge_content'):
            continue
        # Check section IDs
        for entry in data.get('index', []):
            if not pattern.match(entry['id']):
                errors.append(f"{p}: index id '{entry['id']}' not sequential")
        for sid in data.get('sections', {}).keys():
            if not pattern.match(sid):
                errors.append(f"{p}: section key '{sid}' not sequential")
        # Check no processing_patterns
        if 'processing_patterns' in data:
            errors.append(f"{p}: processing_patterns still present")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Migrate knowledge JSON section IDs to sequential format")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--verify-only", action="store_true", help="Only verify, do not migrate")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    kc_root = os.path.dirname(script_dir)
    knowledge_cache_dir = os.path.join(kc_root, ".cache/v6/knowledge")
    catalog_path = os.path.join(kc_root, ".cache/v6/catalog.json")

    if not os.path.isdir(knowledge_cache_dir):
        print(f"ERROR: knowledge cache directory not found: {knowledge_cache_dir}")
        sys.exit(1)

    if args.verify_only:
        errors = verify(knowledge_cache_dir)
        if errors:
            print(f"ERRORS ({len(errors)}):")
            for e in errors:
                print(f"  {e}")
            sys.exit(1)
        else:
            print("OK: All section IDs are sequential, no processing_patterns")
        return

    # Phase 1: Update content of all files
    all_files = glob.glob(f"{knowledge_cache_dir}/**/*.json", recursive=True)
    knowledge_files = [p for p in all_files if '/assets/' not in p]
    print(f"Found {len(knowledge_files)} knowledge JSON files")

    stats = {"migrated": 0, "skipped": 0, "pp_removed": 0, "inconsistency_fixed": 0, "renamed": 0}

    if not args.dry_run:
        for path in sorted(knowledge_files):
            migrate_file_content(path, stats)

    # Phase 2: Rename split files to match new catalog
    if not args.dry_run and os.path.exists(catalog_path):
        print("Renaming split files to match catalog...")
        rename_split_files(knowledge_cache_dir, catalog_path, stats)

    print(f"\nMigration complete:")
    print(f"  Content migrated:          {stats['migrated']}")
    print(f"  Skipped:                   {stats['skipped']}")
    print(f"  processing_patterns removed: {stats['pp_removed']}")
    print(f"  Inconsistencies fixed:     {stats['inconsistency_fixed']}")
    print(f"  Split files renamed:       {stats['renamed']}")

    # Verify
    print("\nVerifying...")
    errors = verify(knowledge_cache_dir)
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors[:20]:
            print(f"  {e}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more")
        sys.exit(1)
    else:
        print("OK: All section IDs are sequential, no processing_patterns")


if __name__ == "__main__":
    main()
