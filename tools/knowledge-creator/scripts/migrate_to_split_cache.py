#!/usr/bin/env python3
"""Migrate merged knowledge cache to split state.

For each split group in catalog.json, reads the merged knowledge file and
trace file from the cache, then creates per-split-entry JSON files in the
knowledge_cache_dir.

Non-split entries are already in place. Only split entries are processed.

Strategy for section assignment:
  1. Load merged knowledge file and trace file for each split group.
  2. For each section in the trace, find which part's section_range.sections
     contains the section's source_heading.
  3. Assign unmatched sections (structural headings not in any section_range)
     to Part 1 by default.
  4. Write per-split-entry knowledge JSON files.
  5. Also copy merged trace to per-part traces (needed for Phase C).

For groups with total_parts=1, just copy the merged file as the single part file.
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


def assign_sections_to_parts(parts, trace_sections, merged_sections, original_id):
    """Assign merged section IDs to each split part based on trace source_headings.

    Returns:
        dict: {part_id: [section_id, ...]}
    """
    # Build source_heading -> section_id map from trace
    heading_to_sid = {}
    for ts in trace_sections:
        heading_to_sid[ts["source_heading"]] = ts["section_id"]

    # For each part, find section_ids by matching section_range.sections
    part_section_ids = {}
    assigned_sids = set()

    for part in parts:
        pid = part["id"]
        section_range = part.get("section_range", {})
        range_sections = section_range.get("sections", [])

        sids = []
        for heading in range_sections:
            if heading and heading in heading_to_sid:
                sid = heading_to_sid[heading]
                if sid in merged_sections:
                    sids.append(sid)
                    assigned_sids.add(sid)
        part_section_ids[pid] = sids

    # Assign unmatched sections (not in any section_range) to Part 1
    unmatched = [
        ts["section_id"] for ts in trace_sections
        if ts["section_id"] not in assigned_sids and ts["section_id"] in merged_sections
    ]
    if unmatched:
        first_part_id = parts[0]["id"]
        # Prepend unmatched to Part 1 (they are usually structural/intro sections)
        part_section_ids[first_part_id] = unmatched + part_section_ids[first_part_id]
        print(f"  Assigned {len(unmatched)} unmatched sections to Part 1 ({first_part_id})")

    return part_section_ids


def migrate_split_group(original_id, parts, knowledge_cache_dir, trace_dir, merged_knowledge, trace_data):
    """Migrate a single split group from merged to split state."""
    merged_sections = merged_knowledge.get("sections", {})
    trace_sections = trace_data.get("sections", [])

    if len(parts) == 1:
        # Single-part group: just copy the merged file as the part file
        part = parts[0]
        part_path = os.path.join(knowledge_cache_dir, part["output_path"])
        part_knowledge = dict(merged_knowledge)
        part_knowledge["id"] = part["id"]
        write_json(part_path, part_knowledge)

        # Copy/create trace for the part
        if trace_data:
            part_trace = dict(trace_data)
            part_trace["file_id"] = part["id"]
            part_trace_path = os.path.join(trace_dir, f"{part['id']}.json")
            write_json(part_trace_path, part_trace)

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

    # Multi-part group: distribute sections across parts
    part_section_map = assign_sections_to_parts(parts, trace_sections, merged_sections, original_id)

    for part in parts:
        pid = part["id"]
        sids = part_section_map.get(pid, [])

        # Build knowledge for this part
        part_knowledge = {
            "id": pid,
            "title": merged_knowledge.get("title", ""),
            "official_doc_urls": merged_knowledge.get("official_doc_urls", []),
            "index": [
                entry for entry in merged_knowledge.get("index", [])
                if entry["id"] in sids
            ],
            "sections": {
                sid: content
                for sid, content in merged_sections.items()
                if sid in sids
            },
        }

        # Fix asset paths: replace original_id with part_id
        for sid in list(part_knowledge["sections"].keys()):
            content = part_knowledge["sections"][sid]
            content = content.replace(f"assets/{original_id}/", f"assets/{pid}/")
            part_knowledge["sections"][sid] = content

        part_path = os.path.join(knowledge_cache_dir, part["output_path"])
        write_json(part_path, part_knowledge)

        # Write part trace
        if trace_data and sids:
            part_trace_sections = [
                ts for ts in trace_sections
                if ts["section_id"] in sids
            ]
            part_trace = {
                "file_id": pid,
                "generated_at": trace_data.get("generated_at", ""),
                "internal_labels": trace_data.get("internal_labels", []),
                "sections": part_trace_sections,
            }
            part_trace_path = os.path.join(trace_dir, f"{pid}.json")
            write_json(part_trace_path, part_trace)

        # Copy assets from merged to part
        merged_assets_dir = os.path.join(
            knowledge_cache_dir,
            part["type"], part["category"], "assets", original_id
        )
        if os.path.isdir(merged_assets_dir):
            part_assets_dir = os.path.join(knowledge_cache_dir, part["assets_dir"])
            if not os.path.exists(part_assets_dir):
                shutil.copytree(merged_assets_dir, part_assets_dir)


def main():
    repo = os.path.abspath(os.path.join(TOOL_DIR, "..", ".."))
    catalog_path = os.path.join(repo, "tools/knowledge-creator/.cache/v6/catalog.json")
    knowledge_cache_dir = os.path.join(repo, "tools/knowledge-creator/.cache/v6/knowledge")
    trace_dir = os.path.join(repo, "tools/knowledge-creator/.cache/v6/traces")

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
        trace_path = os.path.join(trace_dir, f"{original_id}.json")

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

        merged_knowledge = load_json(merged_path)
        trace_data = load_json(trace_path) if os.path.exists(trace_path) else {}

        print(f"[MIGRATE] {original_id}: {len(parts)} parts")
        try:
            migrate_split_group(
                original_id, parts,
                knowledge_cache_dir, trace_dir,
                merged_knowledge, trace_data
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
