#!/usr/bin/env python3
"""Migrate biz_samples knowledge files from about/about-nablarch to guide/biz-samples.

Changes:
- Catalog: type=about→guide, category=about-nablarch→biz-samples
- Catalog: id prefix about-nablarch-→biz-samples- (for biz_samples files only)
- Catalog: output_path, assets_dir updated accordingly
- Catalog: split_info.original_id updated if applicable
- Cache files: moved to new path, id field updated, asset refs updated
"""
import os
import re
import sys
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


def new_id(old_id):
    """Replace about-nablarch- prefix with biz-samples-."""
    return re.sub(r'^about-nablarch-', 'biz-samples-', old_id)


def migrate_catalog(catalog_path):
    """Update catalog entries for biz_samples files."""
    catalog = load_json(catalog_path)
    files = catalog.get("files", [])

    changed = 0
    new_files = []
    for fi in files:
        if "biz_samples" not in fi.get("source_path", ""):
            new_files.append(fi)
            continue

        fi = dict(fi)
        old_fid = fi["id"]
        new_fid = new_id(old_fid)

        fi["id"] = new_fid
        fi["type"] = "guide"
        fi["category"] = "biz-samples"
        fi["output_path"] = re.sub(
            r'^about/about-nablarch/', 'guide/biz-samples/',
            fi.get("output_path", "")
        )
        fi["output_path"] = fi["output_path"].replace(f"/{old_fid}.json", f"/{new_fid}.json")
        fi["assets_dir"] = re.sub(
            r'^about/about-nablarch/', 'guide/biz-samples/',
            fi.get("assets_dir", "")
        )
        fi["assets_dir"] = fi["assets_dir"].replace(f"/{old_fid}/", f"/{new_fid}/")

        # Update split_info.original_id
        si = fi.get("split_info", {})
        if si.get("is_split") and si.get("original_id", "").startswith("about-nablarch-"):
            fi["split_info"] = dict(si)
            fi["split_info"]["original_id"] = new_id(si["original_id"])

        # Update section_range is not needed (section IDs s1, s2... stay the same)

        new_files.append(fi)
        if old_fid != new_fid:
            changed += 1
            print(f"  Catalog: {old_fid} → {new_fid}")

    catalog["files"] = new_files
    write_json(catalog_path, catalog)
    print(f"  Updated {changed} catalog entries")
    return changed


def migrate_cache_files(knowledge_cache_dir):
    """Move knowledge JSON files to new locations and update their content."""
    moved = 0
    old_dir = os.path.join(knowledge_cache_dir, "about/about-nablarch")
    new_dir = os.path.join(knowledge_cache_dir, "guide/biz-samples")

    if not os.path.isdir(old_dir):
        print(f"  No files to move from {old_dir}")
        return 0

    # Find all biz_samples-related files in old location
    # They are identified by their id field containing the biz_samples content
    # We move any file whose id starts with about-nablarch-{biz_samples_suffix}
    # We detect biz_samples files from the catalog instead
    catalog_path = os.path.join(os.path.dirname(knowledge_cache_dir), "catalog.json")
    catalog = load_json(catalog_path)

    # Build map: new_id → (new_output_path, old_possible_paths)
    for fi in catalog["files"]:
        if "biz_samples" not in fi.get("source_path", ""):
            continue

        new_output_path = fi["output_path"]  # e.g., guide/biz-samples/biz-samples-biz_samples.json
        new_path = os.path.join(knowledge_cache_dir, new_output_path)
        new_fid = fi["id"]

        # The old file would be at about/about-nablarch/{old_id}.json
        old_fid = re.sub(r'^biz-samples-', 'about-nablarch-', new_fid)
        old_output_path = f"about/about-nablarch/{old_fid}.json"
        old_path = os.path.join(knowledge_cache_dir, old_output_path)

        if not os.path.exists(old_path):
            # Try finding it with old sec-hash names (pre-migration files)
            # These won't exist after catalog regen, but check anyway
            continue

        # Load file and update id + asset refs
        data = load_json(old_path)
        data["id"] = new_fid

        # Update asset references: assets/about-nablarch-*/  → assets/biz-samples-*/
        for sid in list(data.get("sections", {}).keys()):
            content = data["sections"][sid]
            content = re.sub(
                r'assets/about-nablarch-([^/]+)/',
                lambda m: f"assets/biz-samples-{m.group(1)}/",
                content
            )
            data["sections"][sid] = content

        # Move assets directory
        old_assets_dir = fi.get("assets_dir", "").replace("guide/biz-samples/", "about/about-nablarch/")
        old_assets_dir = re.sub(r'assets/biz-samples-', 'assets/about-nablarch-', old_assets_dir)
        old_assets_path = os.path.join(knowledge_cache_dir, old_assets_dir)
        new_assets_path = os.path.join(knowledge_cache_dir, fi.get("assets_dir", ""))

        if os.path.isdir(old_assets_path) and old_assets_path != new_assets_path:
            os.makedirs(os.path.dirname(new_assets_path), exist_ok=True)
            shutil.move(old_assets_path, new_assets_path)
            print(f"  Assets: {old_assets_dir} → {fi['assets_dir']}")

        # Write to new path
        write_json(new_path, data)

        # Remove old file
        os.remove(old_path)

        print(f"  Cache: {old_fid} → {new_fid}")
        moved += 1

    print(f"  Moved {moved} cache files")
    return moved


def verify(catalog_path):
    """Verify all biz_samples files are in guide/biz-samples."""
    catalog = load_json(catalog_path)
    errors = []
    biz_count = 0
    for fi in catalog["files"]:
        if "biz_samples" not in fi.get("source_path", ""):
            continue
        biz_count += 1
        if fi["type"] != "guide":
            errors.append(f"  {fi['id']}: type={fi['type']} (expected: guide)")
        if fi["category"] != "biz-samples":
            errors.append(f"  {fi['id']}: category={fi['category']} (expected: biz-samples)")
        if not fi["output_path"].startswith("guide/biz-samples/"):
            errors.append(f"  {fi['id']}: output_path={fi['output_path']}")
        if fi["id"].startswith("about-nablarch-"):
            errors.append(f"  {fi['id']}: id still has about-nablarch- prefix")

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(e)
        return False
    else:
        print(f"OK: {biz_count} biz_samples files in guide/biz-samples")
        return True


def main():
    parser = argparse.ArgumentParser(description="Migrate biz_samples from about/about-nablarch to guide/biz-samples")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--verify-only", action="store_true", help="Only verify, do not migrate")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    kc_root = os.path.dirname(script_dir)
    catalog_path = os.path.join(kc_root, ".cache/v6/catalog.json")
    knowledge_cache_dir = os.path.join(kc_root, ".cache/v6/knowledge")

    if not os.path.exists(catalog_path):
        print(f"ERROR: catalog not found: {catalog_path}")
        sys.exit(1)

    if args.verify_only:
        ok = verify(catalog_path)
        sys.exit(0 if ok else 1)

    if args.dry_run:
        print("DRY RUN - no files written")
        # Just show what would be changed
        catalog = load_json(catalog_path)
        for fi in catalog["files"]:
            if "biz_samples" in fi.get("source_path", ""):
                new_fid = new_id(fi["id"])
                if new_fid != fi["id"]:
                    print(f"  Would rename: {fi['id']} → {new_fid}")
        return

    print("Step 1: Updating catalog...")
    migrate_catalog(catalog_path)

    print("\nStep 2: Moving cache files...")
    migrate_cache_files(knowledge_cache_dir)

    print("\nVerifying...")
    ok = verify(catalog_path)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
