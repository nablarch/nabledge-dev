#!/usr/bin/env python3
"""Migrate knowledge JSON section IDs from kebab-case to sequential (s1, s2, ...).

Strategy: Use index array order in each knowledge JSON file.
index[0].id -> s1, index[1].id -> s2, ...

Also:
- Renames split files to match new catalog output_paths (--s1.json, --s2.json, etc.)
- Removes processing_patterns field from all knowledge JSON files

Process:
1. Update content (section IDs) of all existing files
2. Move biz_samples non-split files from old to new path
3. Rename split files to match new catalog naming convention
4. Update biz_samples section IDs
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


def _title_to_section_id_legacy(title):
    """Reproduce the old _title_to_section_id logic for reverse mapping."""
    import hashlib
    ascii_id = re.sub(r'[^a-zA-Z0-9-]', '', title.replace(' ', '-')).lower().strip('-')
    ascii_id = re.sub(r'-+', '-', ascii_id)
    if ascii_id and len(ascii_id) >= 3:
        return ascii_id[:50]
    h = hashlib.md5(title.encode('utf-8')).hexdigest()[:8]
    return f"sec-{h}"


_ORIGINAL_ID_REMAP_REVERSE = {
    "testing-framework-rest-02_RequestUnitTest": "testing-framework-rest",
    "testing-framework-batch-02_RequestUnitTest": "testing-framework-batch",
    "testing-framework-send_sync-02_RequestUnitTest": "testing-framework-send_sync",
    "testing-framework-rest-03_DealUnitTest": "testing-framework-rest",
    "testing-framework-batch-03_DealUnitTest": "testing-framework-batch",
    "testing-framework-send_sync-03_DealUnitTest": "testing-framework-send_sync",
}


def migrate_file_content(data):
    """Update section IDs and remove processing_patterns in a knowledge JSON data dict.

    Modifies data in-place.
    Returns True if content was changed (section IDs migrated or pp removed).
    """
    changed = False

    # processing_patterns を削除
    if "processing_patterns" in data:
        del data["processing_patterns"]
        changed = True

    # no_knowledge_content=true はセクションなし → スキップ
    if data.get("no_knowledge_content"):
        return changed

    index = data.get("index", [])
    if not index:
        return changed

    # index-section不整合を修正（Issue #150 bugs: 3件）
    idx_ids = {e["id"] for e in index}
    sec_keys = set(data.get("sections", {}).keys())
    orphan_sections = sec_keys - idx_ids
    orphan_index = idx_ids - sec_keys
    if orphan_sections or orphan_index:
        for orphan_key in orphan_sections:
            del data["sections"][orphan_key]
            print(f"  Removed orphan section key: {orphan_key} in {data.get('id', '?')}")
        for oid in orphan_index:
            data["index"] = [e for e in data["index"] if e["id"] != oid]
            print(f"  Removed orphan index entry: {oid} in {data.get('id', '?')}")

    # index順で old_id -> new_id マッピングを構築
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

    return True


def rename_non_split_biz_samples(knowledge_cache_dir, catalog_path, stats):
    """Move biz_samples non-split cache files from old to new path."""
    catalog = load_json(catalog_path)
    moved = 0
    for fi in catalog.get("files", []):
        if fi.get("split_info", {}).get("is_split"):
            continue
        if fi["category"] != "biz-samples":
            continue
        new_path = os.path.join(knowledge_cache_dir, fi["output_path"])
        if os.path.exists(new_path):
            continue
        old_id = fi["id"].replace("biz-samples-", "about-nablarch-")
        old_path = os.path.join(knowledge_cache_dir, "about", "about-nablarch", f"{old_id}.json")
        if not os.path.exists(old_path):
            print(f"  WARNING: biz_samples non-split not found: {old_path}")
            continue
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(old_path, new_path)
        data = load_json(new_path)
        data["id"] = fi["id"]
        write_json(new_path, data)
        moved += 1
    stats["biz_samples_nonsplit_moved"] = moved
    print(f"  Moved {moved} biz_samples non-split files")


def rename_split_files(knowledge_cache_dir, catalog_path, stats):
    """Rename split cache files to match new catalog output_paths.

    For each catalog split entry:
    1. Reconstruct old filename: {old_original_id}--{_title_to_section_id_legacy(first_heading)}.json
    2. Handle biz_samples (type/category changed) via reverse mapping
    3. Handle 5 original_id changes via _ORIGINAL_ID_REMAP_REVERSE
    4. Verify old file exists, rename to new output_path, update id field
    """
    catalog = load_json(catalog_path)
    renamed = 0
    skipped = 0
    errors = []

    for fi in catalog.get("files", []):
        si = fi.get("split_info")
        if not si or not si.get("is_split"):
            continue

        new_output_path = fi["output_path"]
        new_path = os.path.join(knowledge_cache_dir, new_output_path)
        if os.path.exists(new_path):
            skipped += 1
            continue

        original_id = si["original_id"]
        type_ = fi["type"]
        category = fi["category"]

        # Reverse-map to old type/category/original_id
        old_type, old_category, old_original_id = type_, category, original_id
        if category == "biz-samples":
            old_type, old_category = "about", "about-nablarch"
            old_original_id = original_id.replace("biz-samples-", "about-nablarch-")
        if original_id in _ORIGINAL_ID_REMAP_REVERSE:
            old_original_id = _ORIGINAL_ID_REMAP_REVERSE[original_id]

        # Reconstruct old suffix
        sections = fi.get("section_range", {}).get("sections", [])
        first_heading = sections[0] if sections else ""
        old_suffix = _title_to_section_id_legacy(first_heading)

        # Try exact match, then dedup suffixes (-2, -3, ...)
        old_dir = os.path.join(knowledge_cache_dir, old_type, old_category)
        old_path = os.path.join(old_dir, f"{old_original_id}--{old_suffix}.json")
        if not os.path.exists(old_path):
            found = False
            for counter in range(2, 10):
                candidate = os.path.join(old_dir, f"{old_original_id}--{old_suffix}-{counter}.json")
                if os.path.exists(candidate):
                    old_path = candidate
                    found = True
                    break
            if not found:
                errors.append(f"{old_original_id}--{old_suffix} (for {new_output_path})")
                continue

        # Execute rename
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(old_path, new_path)

        # Update id field
        data = load_json(new_path)
        new_file_id = os.path.basename(new_path).replace(".json", "")
        data["id"] = new_file_id
        write_json(new_path, data)

        # Rename assets directory
        old_basename = os.path.basename(old_path).replace(".json", "")
        old_assets = os.path.join(os.path.dirname(old_path), "assets", old_basename)
        new_assets = os.path.join(os.path.dirname(new_path), "assets", new_file_id)
        if os.path.isdir(old_assets):
            os.makedirs(os.path.dirname(new_assets), exist_ok=True)
            if os.path.exists(new_assets):
                shutil.rmtree(new_assets)
            shutil.move(old_assets, new_assets)
            for sid in list(data.get("sections", {}).keys()):
                data["sections"][sid] = data["sections"][sid].replace(
                    f"assets/{old_basename}/", f"assets/{new_file_id}/")
            write_json(new_path, data)

        renamed += 1

    stats["renamed"] = renamed
    stats["skipped"] = skipped
    if errors:
        print(f"  WARNING: {len(errors)} files not found:")
        for e in errors[:10]:
            print(f"    {e}")
    print(f"  Renamed {renamed}, skipped {skipped} (already correct)")


def migrate_biz_samples_content(knowledge_cache_dir, catalog_path, stats):
    """Update section IDs in biz_samples JSONs (still in old kebab-case)."""
    catalog = load_json(catalog_path)
    updated = 0
    for fi in catalog.get("files", []):
        if fi["category"] != "biz-samples":
            continue
        path = os.path.join(knowledge_cache_dir, fi["output_path"])
        if not os.path.exists(path):
            continue
        data = load_json(path)
        if data.get("no_knowledge_content"):
            continue
        changed = migrate_file_content(data)
        if changed:
            write_json(path, data)
            updated += 1
    stats["biz_content_updated"] = updated
    print(f"  Updated section IDs in {updated} biz_samples files")


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

    # Phase 0: Update content (section IDs) of all existing files
    all_files = glob.glob(f"{knowledge_cache_dir}/**/*.json", recursive=True)
    knowledge_files = [p for p in all_files if '/assets/' not in p]
    print(f"Found {len(knowledge_files)} knowledge JSON files")

    migrated = 0
    skipped = 0

    if not args.dry_run:
        for path in sorted(knowledge_files):
            data = load_json(path)
            changed = migrate_file_content(data)
            write_json(path, data)
            if changed:
                migrated += 1
            else:
                skipped += 1

    print(f"  Content migrated: {migrated}, skipped: {skipped}")

    stats = {}

    # Phase 1: biz_samples 非splitファイルの移動
    print("Phase 1: Move biz_samples non-split files...")
    rename_non_split_biz_samples(knowledge_cache_dir, catalog_path, stats)

    # Phase 2: 全splitファイルのリネーム（biz_samples split含む）
    print("Phase 2: Rename split files...")
    rename_split_files(knowledge_cache_dir, catalog_path, stats)

    # Phase 3: biz_samples のJSON中身セクションID更新
    print("Phase 3: Update biz_samples section IDs...")
    migrate_biz_samples_content(knowledge_cache_dir, catalog_path, stats)

    print(f"\nMigration complete:")
    print(f"  biz_samples non-split moved:  {stats.get('biz_samples_nonsplit_moved', 0)}")
    print(f"  Split files renamed:          {stats.get('renamed', 0)}")
    print(f"  Split files skipped:          {stats.get('skipped', 0)}")
    print(f"  biz_samples content updated:  {stats.get('biz_content_updated', 0)}")

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
