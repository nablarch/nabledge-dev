"""Phase M-1: Merge split knowledge files."""
import os
import shutil
from steps.common import load_json, write_json


class MergeSplitFiles:
    """Merge split knowledge files into single files.

    Files with split_info.is_split=true are parts of a larger file.
    Group by original_id, merge, save as {original_id}.json,
    delete part files, update classified_list.json.
    """

    def __init__(self, ctx):
        self.ctx = ctx

    def run(self):
        """Execute merge operation."""
        classified = load_json(self.ctx.classified_list_path)

        split_groups = {}
        for fi in classified["files"]:
            if "split_info" in fi and fi["split_info"].get("is_split"):
                oid = fi["split_info"]["original_id"]
                split_groups.setdefault(oid, []).append(fi)

        if not split_groups:
            return

        print(f"\n--- Merging Split Files ---")
        merged_groups = {}

        for original_id, parts in split_groups.items():
            parts.sort(key=lambda p: p["split_info"]["part"])

            part_paths = []
            all_exist = True
            for part in parts:
                pp = f"{self.ctx.knowledge_dir}/{part['output_path']}"
                if os.path.exists(pp):
                    part_paths.append(pp)
                else:
                    all_exist = False
                    break

            if not all_exist:
                print(f"  [SKIP] {original_id}: not all parts generated")
                continue

            print(f"   🔗 [MERGE] {original_id}: {len(parts)} parts")
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

            # Merge index
            index_map = {}
            for pj in part_jsons:
                for entry in pj.get("index", []):
                    sid = entry["id"]
                    if sid not in index_map:
                        index_map[sid] = {
                            "id": sid, "title": entry["title"],
                            "hints": list(entry.get("hints", []))
                        }
                    else:
                        existing = set(index_map[sid]["hints"])
                        for h in entry.get("hints", []):
                            if h not in existing:
                                index_map[sid]["hints"].append(h)
                                existing.add(h)
            merged["index"] = list(index_map.values())

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

                # Consolidate assets
                merged_assets = f"{self.ctx.knowledge_dir}/{type_}/{category}/assets/{original_id}/"
                for part in parts:
                    part_assets = f"{self.ctx.knowledge_dir}/{part['assets_dir']}"
                    if os.path.exists(part_assets):
                        os.makedirs(merged_assets, exist_ok=True)
                        for af in os.listdir(part_assets):
                            src = os.path.join(part_assets, af)
                            dst = os.path.join(merged_assets, af)
                            if os.path.isfile(src) and not os.path.exists(dst):
                                shutil.move(src, dst)
                        try:
                            os.rmdir(part_assets)
                        except OSError:
                            pass

                for pp in part_paths:
                    os.remove(pp)

                merged_groups[original_id] = parts
            except Exception as e:
                print(f"    ERROR: {original_id}: {e}")

        # Update classified_list
        if merged_groups:
            part_ids = set()
            for parts in merged_groups.values():
                for p in parts:
                    part_ids.add(p["id"])

            new_files = [fi for fi in classified["files"] if fi["id"] not in part_ids]
            for oid, parts in merged_groups.items():
                base = parts[0].copy()
                base["id"] = oid
                base["output_path"] = f"{base['type']}/{base['category']}/{oid}.json"
                base["assets_dir"] = f"{base['type']}/{base['category']}/assets/{oid}/"
                base.pop("split_info", None)
                base.pop("section_range", None)
                new_files.append(base)

            new_files.sort(key=lambda f: (f["type"], f["category"], f["id"]))
            classified["files"] = new_files
            write_json(self.ctx.classified_list_path, classified)
