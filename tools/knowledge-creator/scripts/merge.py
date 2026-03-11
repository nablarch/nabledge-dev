"""Phase M-1: Merge split knowledge files."""
import os
import shutil
from common import load_json, write_json
from logger import get_logger


class MergeSplitFiles:
    """Merge split knowledge files into single files.

    Files with split_info.is_split=true are parts of a larger file.
    Group by original_id, merge, save as {original_id}.json to knowledge_dir.
    Part files in knowledge_cache_dir are preserved (not deleted).
    """

    def __init__(self, ctx):
        self.ctx = ctx
        self.logger = get_logger()

    def run(self):
        """Execute merge operation.

        Reads split parts from knowledge_cache_dir, merges them, and writes
        merged files to knowledge_dir. Non-split files are copied from
        knowledge_cache_dir to knowledge_dir.

        Returns:
            Merged catalog dict (split entries replaced by merged entries)
            if any merges were performed, None otherwise.
        """
        classified = load_json(self.ctx.classified_list_path)

        split_groups = {}
        for fi in classified["files"]:
            if "split_info" in fi and fi["split_info"].get("is_split"):
                oid = fi["split_info"]["original_id"]
                split_groups.setdefault(oid, []).append(fi)

        self.logger.info(f"\n--- Merging Split Files ---")
        merged_groups = {}

        for original_id, parts in split_groups.items():
            parts.sort(key=lambda p: p["split_info"]["part"])

            part_paths = []
            all_exist = True
            for part in parts:
                pp = f"{self.ctx.knowledge_cache_dir}/{part['output_path']}"
                if os.path.exists(pp):
                    part_paths.append(pp)
                else:
                    all_exist = False
                    break

            if not all_exist:
                self.logger.info(f"  [SKIP] {original_id}: not all parts generated")
                continue

            self.logger.info(f"   🔗 [MERGE] {original_id}: {len(parts)} parts")
            part_jsons = [load_json(pp) for pp in part_paths]

            merged = {
                "id": original_id,
                "title": part_jsons[0].get("title", ""),
            }

            # Merge official_doc_urls (deduplicate, preserve order)
            seen_urls = set()
            urls = []
            for pj in part_jsons:
                for url in pj.get("official_doc_urls", []):
                    if url not in seen_urls:
                        seen_urls.add(url)
                        urls.append(url)
            merged["official_doc_urls"] = urls

            # Merge index: part-sequential order, dedup by id, merge hints
            merged_index = []
            seen_ids = {}  # id -> position in merged_index
            for pj in part_jsons:
                for entry in pj.get("index", []):
                    sid = entry["id"]
                    if sid not in seen_ids:
                        new_entry = {
                            "id": sid, "title": entry["title"],
                            "hints": list(entry.get("hints", []))
                        }
                        seen_ids[sid] = len(merged_index)
                        merged_index.append(new_entry)
                    else:
                        existing_entry = merged_index[seen_ids[sid]]
                        existing_hints = set(existing_entry["hints"])
                        for h in entry.get("hints", []):
                            if h not in existing_hints:
                                existing_entry["hints"].append(h)
                                existing_hints.add(h)
            merged["index"] = merged_index

            # Merge sections
            merged["sections"] = {}
            for i, pj in enumerate(part_jsons):
                part_id = parts[i]["id"]
                for sid, content in pj.get("sections", {}).items():
                    content = content.replace(f"assets/{part_id}/", f"assets/{original_id}/")
                    if sid not in merged["sections"]:
                        merged["sections"][sid] = content
                    else:
                        merged["sections"][sid] += "\n\n" + content

            type_ = parts[0]["type"]
            category = parts[0]["category"]
            merged_path = f"{self.ctx.knowledge_dir}/{type_}/{category}/{original_id}.json"

            try:
                write_json(merged_path, merged)

                # Validate merged index-section consistency
                merged_idx_ids = set(e["id"] for e in merged["index"])
                merged_sec_ids = set(merged["sections"].keys())
                idx_only = merged_idx_ids - merged_sec_ids
                sec_only = merged_sec_ids - merged_idx_ids
                if idx_only or sec_only:
                    warn_parts = []
                    if idx_only:
                        warn_parts.append(f"index only: {sorted(idx_only)}")
                    if sec_only:
                        warn_parts.append(f"sections only: {sorted(sec_only)}")
                    self.logger.warning(
                        f"    ⚠️ {original_id}: index-section mismatch after merge: "
                        + ", ".join(warn_parts)
                    )

                # Consolidate assets: copy from cache to knowledge_dir (preserve cache)
                merged_assets = f"{self.ctx.knowledge_dir}/{type_}/{category}/assets/{original_id}/"
                for part in parts:
                    part_assets = f"{self.ctx.knowledge_cache_dir}/{part['assets_dir']}"
                    if os.path.exists(part_assets):
                        os.makedirs(merged_assets, exist_ok=True)
                        for af in os.listdir(part_assets):
                            src = os.path.join(part_assets, af)
                            dst = os.path.join(merged_assets, af)
                            if os.path.isfile(src) and not os.path.exists(dst):
                                shutil.copy2(src, dst)

                merged_groups[original_id] = parts
            except Exception as e:
                self.logger.error(f"    ERROR: {original_id}: {e}")

        # Copy non-split files from knowledge_cache_dir to knowledge_dir
        for fi in classified["files"]:
            if "split_info" in fi and fi["split_info"].get("is_split"):
                continue
            src = f"{self.ctx.knowledge_cache_dir}/{fi['output_path']}"
            dst = f"{self.ctx.knowledge_dir}/{fi['output_path']}"
            if os.path.exists(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                src_assets = f"{self.ctx.knowledge_cache_dir}/{fi['assets_dir']}"
                if os.path.isdir(src_assets):
                    dst_assets = f"{self.ctx.knowledge_dir}/{fi['assets_dir']}"
                    if os.path.exists(dst_assets):
                        shutil.rmtree(dst_assets)
                    shutil.copytree(src_assets, dst_assets)

        # Build and return merged catalog dict if any merges happened
        if not merged_groups:
            return None

        part_ids = set()
        for parts in merged_groups.values():
            for p in parts:
                part_ids.add(p["id"])

        # Also exclude non-split entries whose ID collides with a merged entry ID
        merged_oids = set(merged_groups.keys())
        new_files = [fi for fi in classified["files"] if fi["id"] not in part_ids and fi["id"] not in merged_oids]
        for oid, parts in merged_groups.items():
            base = parts[0].copy()
            base["id"] = oid
            base["output_path"] = f"{base['type']}/{base['category']}/{oid}.json"
            base["assets_dir"] = f"{base['type']}/{base['category']}/assets/{oid}/"
            base.pop("split_info", None)
            base.pop("section_range", None)
            base.pop("base_name", None)
            new_files.append(base)

        new_files.sort(key=lambda f: (f["type"], f["category"], f["id"]))
        merged_catalog = dict(classified)
        merged_catalog["files"] = new_files
        return merged_catalog
