"""Step 4: Build index.toon with processing pattern classification."""

import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import (
    load_json, write_file, read_file, run_claude,
    utcnow_iso, log_info, log_skip, log_success, log_fail
)


def classify_patterns_with_claude(ctx, file_info: dict, knowledge: dict) -> str:
    """Classify processing patterns using claude -p.

    Args:
        ctx: Context object
        file_info: Classified file info dict
        knowledge: Knowledge JSON dict

    Returns:
        Space-separated processing pattern values
    """
    file_id = file_info["id"]
    log_path = os.path.join(ctx.log_dir, "classify-patterns", f"{file_id}.json")

    # Skip if already classified
    if os.path.exists(log_path):
        try:
            log_entry = load_json(log_path)
            if log_entry.get("status") == "ok":
                return log_entry.get("patterns", "")
        except:
            pass

    # Load prompt template
    template_path = os.path.join(ctx.repo, "tools/knowledge-creator/prompts/classify_patterns.md")
    template = read_file(template_path)

    # Replace placeholders
    prompt = template.replace("{FILE_ID}", file_info["id"])
    prompt = prompt.replace("{TITLE}", knowledge.get("title", ""))
    prompt = prompt.replace("{TYPE}", file_info["type"])
    prompt = prompt.replace("{CATEGORY}", file_info["category"])
    prompt = prompt.replace("{KNOWLEDGE_JSON}", json.dumps(knowledge, indent=2, ensure_ascii=False))

    # Execute claude -p
    started_at = utcnow_iso()
    try:
        result = run_claude(prompt, timeout=120)
    except subprocess.TimeoutExpired:
        log_entry = {
            "file_id": file_id,
            "status": "error",
            "started_at": started_at,
            "finished_at": utcnow_iso(),
            "error": "timeout",
            "patterns": ""
        }
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "w") as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)
        log_fail(file_id, "pattern classification timeout")
        return ""

    if result.returncode != 0:
        log_entry = {
            "file_id": file_id,
            "status": "error",
            "started_at": started_at,
            "finished_at": utcnow_iso(),
            "error": result.stderr,
            "patterns": ""
        }
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "w") as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)
        log_fail(file_id, "pattern classification failed")
        return ""

    # Extract patterns from output
    patterns = result.stdout.strip()

    log_entry = {
        "file_id": file_id,
        "status": "ok",
        "started_at": started_at,
        "finished_at": utcnow_iso(),
        "patterns": patterns
    }
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w") as f:
        json.dump(log_entry, f, indent=2, ensure_ascii=False)

    return patterns


def write_toon(index_path: str, entries: list, version: str):
    """Write index.toon in TOON format.

    Args:
        index_path: Output path for index.toon
        entries: List of index entry dicts
        version: Nablarch version
    """
    lines = [f"# Nabledge-{version} Knowledge Index", ""]
    lines.append(f"files[{len(entries)},]{{title,type,category,processing_patterns,path}}:")

    for entry in entries:
        # Escape commas in title by replacing with full-width comma
        title = entry["title"].replace(",", "、")
        fields = [
            title,
            entry["type"],
            entry["category"],
            entry["processing_patterns"],
            entry["path"],
        ]
        lines.append(f"  {', '.join(fields)}")

    lines.append("")  # Trailing newline
    write_file(index_path, '\n'.join(lines))


def run(ctx):
    """Execute Step 4: Build index.toon.

    Args:
        ctx: Context object
    """
    log_info(f"Building index.toon for version {ctx.version}")

    # Load classified files
    if not os.path.exists(ctx.classified_list_path):
        log_info("Classified list not found. Please run Step 2 first.")
        return

    classified = load_json(ctx.classified_list_path)
    files = classified["files"]

    log_info(f"Processing {len(files)} files")

    if ctx.dry_run:
        log_info("[DRY-RUN] Would build index.toon")
        return

    entries = []

    # Process each file
    for file_info in files:
        json_path = os.path.join(ctx.knowledge_dir, file_info["output_path"])

        if not os.path.exists(json_path):
            # Knowledge file not yet generated
            entries.append({
                "title": file_info["id"],
                "type": file_info["type"],
                "category": file_info["category"],
                "processing_patterns": "",
                "path": "not yet created"
            })
            log_skip(f"{file_info['id']} (not yet generated)")
            continue

        # Load knowledge file
        knowledge = load_json(json_path)
        title = knowledge.get("title", file_info["id"])

        # Determine processing patterns
        if file_info["type"] == "processing-pattern":
            # For processing-pattern type, use category as pattern
            patterns = file_info["category"]
        else:
            # For other types, classify with claude -p
            patterns = classify_patterns_with_claude(ctx, file_info, knowledge)

        entries.append({
            "title": title,
            "type": file_info["type"],
            "category": file_info["category"],
            "processing_patterns": patterns,
            "path": file_info["output_path"]
        })

        log_success(f"{file_info['id']} → {patterns if patterns else '(none)'}")

    # Write index.toon
    index_path = os.path.join(ctx.knowledge_dir, "index.toon")
    write_toon(index_path, entries, ctx.version)

    log_info(f"Step 4 completed: index.toon written with {len(entries)} entries")
