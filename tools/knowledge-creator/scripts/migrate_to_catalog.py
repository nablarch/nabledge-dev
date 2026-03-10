#!/usr/bin/env python3
"""Migrate existing v6 data to .cache/v6/catalog.json."""
import os
import sys
import json
import glob
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))


def find_latest_run(version):
    """Find the latest run_id by sorting directories."""
    logs_dir = os.path.join(REPO_ROOT, f"tools/knowledge-creator/.logs/v{version}")
    if not os.path.isdir(logs_dir):
        return None
    runs = [d for d in os.listdir(logs_dir)
            if os.path.isdir(os.path.join(logs_dir, d)) and d[0].isdigit()]
    return sorted(runs)[-1] if runs else None


def migrate(version):
    run_id = find_latest_run(version)
    if not run_id:
        print(f"v{version}: No runs found, skipping")
        return

    run_dir = f"{REPO_ROOT}/tools/knowledge-creator/.logs/v{version}/{run_id}"
    cache_dir = f"{REPO_ROOT}/tools/knowledge-creator/.cache/v{version}"
    os.makedirs(cache_dir, exist_ok=True)

    # 1. Load sources
    kc_path = f"{REPO_ROOT}/.claude/skills/nabledge-{version}/plugin/knowledge-creator.json"
    sources = []
    generated_at = ""
    if os.path.exists(kc_path):
        with open(kc_path) as f:
            kc = json.load(f)
        sources = kc.get("sources", [])
        generated_at = kc.get("generated_at", "")

    # 2. Load classified files
    classified_path = f"{run_dir}/phase-a/classified.json"
    files = []
    file_version = version
    if os.path.exists(classified_path):
        with open(classified_path) as f:
            classified = json.load(f)
        files = classified.get("files", [])
        file_version = classified.get("version", version)

    # 3. Load patterns
    patterns_dir = f"{run_dir}/phase-f/patterns"
    patterns_map = {}
    for p in glob.glob(f"{patterns_dir}/*.json"):
        with open(p) as f:
            d = json.load(f)
        pp = d.get("patterns", "")
        patterns_map[d["file_id"]] = pp.split() if pp else []

    for fi in files:
        fi["processing_patterns"] = patterns_map.get(fi["id"], [])

    # 4. Write catalog.json
    catalog = {
        "generated_at": generated_at,
        "sources": sources,
        "version": file_version,
        "files": files,
    }
    catalog_path = f"{cache_dir}/catalog.json"
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    # 5. Copy traces
    src_traces = f"{run_dir}/phase-b/traces"
    dst_traces = f"{cache_dir}/traces"
    if os.path.isdir(src_traces):
        shutil.copytree(src_traces, dst_traces, dirs_exist_ok=True)
        print(f"  Traces: {len(os.listdir(dst_traces))} files copied")

    pp_count = sum(1 for f in files if f.get("processing_patterns"))
    print(f"v{version}: Migrated {len(files)} files ({pp_count} with patterns) -> {catalog_path}")


if __name__ == "__main__":
    migrate("6")
    # migrate("5")  # uncomment when v5 data exists
