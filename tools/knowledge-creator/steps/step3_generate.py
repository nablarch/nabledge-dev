"""Step 3: Generate knowledge files using claude -p."""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import (
    load_json, write_json, read_file, write_file, run_claude, extract_json,
    utcnow_iso, log_info, log_skip, log_success, log_fail, log_error
)


def validate_path(path: str, allowed_parent: str) -> Path:
    """Validate that path is within allowed parent directory.

    Args:
        path: Path to validate
        allowed_parent: Allowed parent directory

    Returns:
        Resolved Path object

    Raises:
        ValueError: If path is outside allowed directory
    """
    resolved = Path(path).resolve()
    allowed = Path(allowed_parent).resolve()

    if not resolved.is_relative_to(allowed):
        raise ValueError(f"Path {path} is outside allowed directory {allowed_parent}")

    return resolved


def extract_assets(source_path: str, source_content: str, source_format: str,
                   assets_dir: str, repo: str, version: str) -> list:
    """Extract images and attachments from source and copy to assets directory.

    Args:
        source_path: Relative path to source file
        source_content: Source file content
        source_format: File format (rst/md/xlsx)
        assets_dir: Target assets directory (relative path)
        repo: Repository root path
        version: Nablarch version (6 or 5)

    Returns:
        List of asset info dicts: [{"original": "path", "assets_path": "assets/..."}]
    """
    assets = []
    source_dir = os.path.dirname(os.path.join(repo, source_path))
    assets_full_dir = os.path.join(repo, ".claude/skills", f"nabledge-{version}", "knowledge", assets_dir)

    # Validate source directory is within .lw/nab-official/
    allowed_parent = os.path.join(repo, ".lw/nab-official")
    try:
        validate_path(source_dir, allowed_parent)
    except ValueError as e:
        log_error(f"Asset extraction skipped: {e}")
        return assets

    if source_format == "rst":
        # Extract image/figure directive references
        image_refs = re.findall(r'\.\.\s+(?:image|figure)::\s+(.+)', source_content)
        for ref in image_refs:
            ref = ref.strip()
            src = os.path.join(source_dir, ref)

            # Validate asset path is within allowed parent
            try:
                validate_path(src, allowed_parent)
            except ValueError as e:
                log_error(f"Skipping asset outside allowed directory: {ref}")
                continue

            if os.path.exists(src):
                os.makedirs(assets_full_dir, exist_ok=True)
                dst = os.path.join(assets_full_dir, os.path.basename(ref))
                shutil.copy2(src, dst)
                assets.append({
                    "original": ref,
                    "assets_path": f"assets/{os.path.basename(assets_dir)}{os.path.basename(ref)}"
                })

        # Extract download directive references
        download_refs = re.findall(r':download:`[^<]*<([^>]+)>`', source_content)
        for ref in download_refs:
            ref = ref.strip()
            src = os.path.join(source_dir, ref)

            # Validate asset path is within allowed parent
            try:
                validate_path(src, allowed_parent)
            except ValueError as e:
                log_error(f"Skipping asset outside allowed directory: {ref}")
                continue

            if os.path.exists(src):
                os.makedirs(assets_full_dir, exist_ok=True)
                dst = os.path.join(assets_full_dir, os.path.basename(ref))
                shutil.copy2(src, dst)
                assets.append({
                    "original": ref,
                    "assets_path": f"assets/{os.path.basename(assets_dir)}{os.path.basename(ref)}"
                })

    return assets


def compute_official_url(file_info: dict) -> str:
    """Compute official documentation URL from source file info.

    Args:
        file_info: Classified file info dict

    Returns:
        Official documentation URL
    """
    if file_info["format"] == "rst":
        path = file_info["source_path"]
        marker = "nablarch-document/ja/"
        idx = path.find(marker)
        if idx >= 0:
            relative = path[idx + len(marker):]
            relative = relative.replace(".rst", ".html")
            return f"https://nablarch.github.io/docs/LATEST/doc/{relative}"
    elif file_info["format"] in ("md", "xlsx"):
        return "https://fintan.jp/page/252/"
    return ""


def build_prompt(ctx, file_info: dict, source_content: str, assets: list) -> str:
    """Build prompt for claude -p.

    Args:
        ctx: Context object
        file_info: Classified file info dict
        source_content: Source file content
        assets: List of extracted assets

    Returns:
        Prompt text
    """
    # Load prompt template
    template_path = os.path.join(ctx.repo, "tools/knowledge-creator/prompts/generate.md")
    template = read_file(template_path)

    # Replace placeholders
    official_url = compute_official_url(file_info)

    prompt = template.replace("{FILE_ID}", file_info["id"])
    prompt = prompt.replace("{FORMAT}", file_info["format"])
    prompt = prompt.replace("{TYPE}", file_info["type"])
    prompt = prompt.replace("{CATEGORY}", file_info["category"])
    prompt = prompt.replace("{OUTPUT_PATH}", file_info["output_path"])
    prompt = prompt.replace("{ASSETS_DIR}", file_info["assets_dir"])
    prompt = prompt.replace("{OFFICIAL_DOC_BASE_URL}", official_url)
    prompt = prompt.replace("{SOURCE_CONTENT}", source_content)

    # Add assets section if any
    if assets:
        assets_table = "\n## 画像・添付ファイル一覧\n\n"
        assets_table += "このソースファイルから以下の画像・添付ファイルが抽出済みです。\n"
        assets_table += "テキスト代替が困難な場合のみ、assets_pathを使って参照してください。\n\n"
        assets_table += "| ソース内パス | assetsパス |\n"
        assets_table += "|---|---|\n"
        for asset in assets:
            assets_table += f"| {asset['original']} | {asset['assets_path']} |\n"
        prompt += "\n" + assets_table

    return prompt


def generate_one(ctx, file_info: dict) -> dict:
    """Generate a single knowledge file.

    Args:
        ctx: Context object
        file_info: Classified file info dict

    Returns:
        Result dict with status and error info
    """
    file_id = file_info["id"]
    output_path = os.path.join(ctx.knowledge_dir, file_info["output_path"])
    log_path = os.path.join(ctx.log_dir, "generate", f"{file_id}.json")

    # Skip if already exists
    if os.path.exists(output_path):
        log_skip(file_id)
        return {"status": "skip", "id": file_id}

    # Read source content
    source_path = os.path.join(ctx.repo, file_info["source_path"])
    try:
        source_content = read_file(source_path)
    except Exception as e:
        log_fail(file_id, f"Failed to read source: {e}")
        return {"status": "error", "id": file_id, "error": str(e)}

    # Extract assets
    assets = extract_assets(
        file_info["source_path"],
        source_content,
        file_info["format"],
        file_info["assets_dir"],
        ctx.repo,
        ctx.version
    )

    # Build prompt
    prompt = build_prompt(ctx, file_info, source_content, assets)

    # Execute claude -p
    started_at = utcnow_iso()
    try:
        result = run_claude(prompt, timeout=300)
    except subprocess.TimeoutExpired:
        log_entry = {
            "file_id": file_id,
            "status": "error",
            "started_at": started_at,
            "finished_at": utcnow_iso(),
            "error": "timeout",
            "raw_output": ""
        }
        write_json(log_path, log_entry)
        log_fail(file_id, "timeout")
        return {"status": "error", "id": file_id, "error": "timeout"}

    if result.returncode != 0:
        log_entry = {
            "file_id": file_id,
            "status": "error",
            "started_at": started_at,
            "finished_at": utcnow_iso(),
            "error": result.stderr,
            "raw_output": result.stdout
        }
        write_json(log_path, log_entry)
        log_fail(file_id, result.stderr[:100])
        return {"status": "error", "id": file_id, "error": result.stderr}

    # Extract and save JSON
    try:
        knowledge_json = extract_json(result.stdout)
    except (json.JSONDecodeError, ValueError) as e:
        log_entry = {
            "file_id": file_id,
            "status": "error",
            "started_at": started_at,
            "finished_at": utcnow_iso(),
            "error": f"JSON extraction failed: {e}",
            "raw_output": result.stdout
        }
        write_json(log_path, log_entry)
        log_fail(file_id, f"JSON extraction failed: {e}")
        return {"status": "error", "id": file_id, "error": str(e)}

    write_json(output_path, knowledge_json)

    finished_at = utcnow_iso()
    log_entry = {
        "file_id": file_id,
        "status": "ok",
        "started_at": started_at,
        "finished_at": finished_at
    }
    write_json(log_path, log_entry)

    log_success(file_id)
    return {"status": "ok", "id": file_id}


def run(ctx):
    """Execute Step 3: Generate knowledge files.

    Args:
        ctx: Context object
    """
    log_info(f"Generating knowledge files for version {ctx.version}")

    # Load classified files
    if not os.path.exists(ctx.classified_list_path):
        log_info("Classified list not found. Please run Step 2 first.")
        return

    classified = load_json(ctx.classified_list_path)
    files = classified["files"]

    log_info(f"Processing {len(files)} files with concurrency={ctx.concurrency}")

    if ctx.dry_run:
        log_info("[DRY-RUN] Would generate knowledge files")
        return

    # Process files concurrently
    with ThreadPoolExecutor(max_workers=ctx.concurrency) as executor:
        futures = []
        for file_info in files:
            futures.append(executor.submit(generate_one, ctx, file_info))

        # Collect results
        ok_count = 0
        skip_count = 0
        error_count = 0
        failed_files = []

        for future in as_completed(futures):
            result = future.result()
            if result["status"] == "ok":
                ok_count += 1
            elif result["status"] == "skip":
                skip_count += 1
            else:
                error_count += 1
                # Track failed files with error messages
                file_id = result.get("id", "unknown")
                error_msg = result.get("error", "unknown error")
                # Find original file_info for more context
                file_info = next((f for f in files if f["id"] == file_id), None)
                failed_files.append((file_info or {"id": file_id}, error_msg))

    # Show detailed error summary if there were failures
    if error_count > 0:
        log_error(f"\n{error_count} files failed to generate:")
        for file_info, error_msg in failed_files[:10]:  # Show first 10
            log_error(f"  - {file_info['id']}: {error_msg[:100]}")
        if len(failed_files) > 10:
            log_error(f"  ... and {len(failed_files) - 10} more")
        log_info(f"Review detailed logs in: {ctx.log_dir}/generate/")

        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            log_info("Aborted by user")
            import sys
            sys.exit(1)

    log_info(f"Step 3 completed: {ok_count} generated, {skip_count} skipped, {error_count} errors")
