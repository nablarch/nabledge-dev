#!/usr/bin/env python3
"""Migrate merged knowledge cache to split state.

For each split group in catalog.json, reads the merged knowledge file and
creates per-split-entry JSON files in the knowledge_cache_dir.

Non-split entries are already in place. Only split entries are processed.

Strategy:
  1. Load merged knowledge file for each split group.
  2. For single-part groups, copy the merged file as the part file.
  3. For multi-part groups, skip (Phase B will regenerate from source).
  4. Copy assets to part-specific directories.

For groups with no merged file, skip (Phase B will regenerate).
"""
import json
import os
import shutil
import sys

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Wrote: {path}")


def migrate_split_group(original_id, parts, knowledge_cache_dir, merged_knowledge):
    """Migrate a single split group from merged to split state.

    For single-part groups: copy the merged file as the part file.
    For multi-part groups: not supported without trace data; caller should skip.
    """
    if len(parts) == 1:
        # Single-part group: just copy the merged file as the part file
        part = parts[0]
        part_path = os.path.join(knowledge_cache_dir, part["output_path"])
        part_knowledge = dict(merged_knowledge)
        part_knowledge["id"] = part["id"]
        write_json(part_path, part_knowledge)

        # Copy assets if any
        merged_assets_dir = os.path.join(
            knowledge_cache_dir,
            parts[0]["type"], parts[0]["category"], "assets", original_id
        )
        if os.path.isdir(merged_assets_dir):
            part_assets_dir = os.path.join(knowledge_cache_dir, part["assets_dir"])
            if not os.path.exists(part_assets_dir):
                shutil.copytree(merged_assets_dir, part_assets_dir)
        return

    # Multi-part group: cannot split without trace data.
    # Phase B will regenerate these from source.
    raise ValueError(f"Multi-part split groups require Phase B regeneration (traces abolished)")


def main():
    repo = os.path.abspath(os.path.join(TOOL_DIR, "..", ".."))
    catalog_path = os.path.join(repo, "tools/knowledge-creator/.cache/v6/catalog.json")
    knowledge_cache_dir = os.path.join(repo, "tools/knowledge-creator/.cache/v6/knowledge")

    catalog = load_json(catalog_path)

    # Group split entries by original_id
    split_groups = {}
    for e in catalog["files"]:
        if "split_info" in e and e["split_info"].get("is_split"):
            oid = e["split_info"]["original_id"]
            split_groups.setdefault(oid, []).append(e)

    print(f"Found {len(split_groups)} split groups to migrate")

    skipped = 0
    migrated = 0
    errors = 0

    for original_id, parts in sorted(split_groups.items()):
        parts.sort(key=lambda p: p["split_info"]["part"])
        t = parts[0]["type"]
        c = parts[0]["category"]

        merged_path = os.path.join(knowledge_cache_dir, t, c, f"{original_id}.json")

        # Check all part files already exist
        all_parts_exist = all(
            os.path.exists(os.path.join(knowledge_cache_dir, p["output_path"]))
            for p in parts
        )
        if all_parts_exist:
            print(f"[SKIP] {original_id}: all parts already exist")
            skipped += 1
            continue

        if not os.path.exists(merged_path):
            print(f"[SKIP] {original_id}: no merged knowledge file, will regenerate in Phase B")
            skipped += 1
            continue

        if len(parts) > 1:
            print(f"[SKIP] {original_id}: multi-part group requires Phase B regeneration")
            skipped += 1
            continue

        merged_knowledge = load_json(merged_path)

        print(f"[MIGRATE] {original_id}: {len(parts)} parts")
        try:
            migrate_split_group(
                original_id, parts,
                knowledge_cache_dir,
                merged_knowledge,
            )
            migrated += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            errors += 1

    print(f"\nDone: {migrated} migrated, {skipped} skipped, {errors} errors")


if __name__ == "__main__":
    main()
