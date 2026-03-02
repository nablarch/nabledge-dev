"""Step 5: Generate browsable documentation from knowledge files."""

import os
from .utils import load_json, write_file, log_info, log_skip, log_success


def convert_to_md(knowledge: dict) -> str:
    """Convert knowledge JSON to markdown.

    Args:
        knowledge: Knowledge JSON dict

    Returns:
        Markdown content string
    """
    lines = [f"# {knowledge['title']}", ""]

    for entry in knowledge["index"]:
        section_id = entry["id"]
        section_title = entry["title"]
        section_content = knowledge["sections"].get(section_id, "")

        lines.append(f"## {section_title}")
        lines.append("")
        lines.append(section_content)
        lines.append("")

    return "\n".join(lines)


def run(ctx):
    """Execute Step 5: Generate browsable docs.

    Args:
        ctx: Context object
    """
    log_info(f"Generating browsable docs for version {ctx.version}")

    # Load classified files
    if not os.path.exists(ctx.classified_list_path):
        log_info("Classified list not found. Please run Step 2 first.")
        return

    classified = load_json(ctx.classified_list_path)
    files = classified["files"]

    log_info(f"Processing {len(files)} files")

    if ctx.dry_run:
        log_info("[DRY-RUN] Would generate docs")
        return

    generated_count = 0
    skipped_count = 0

    for file_info in files:
        json_path = os.path.join(ctx.knowledge_dir, file_info["output_path"])

        if not os.path.exists(json_path):
            log_skip(f"{file_info['id']} (knowledge file not found)")
            skipped_count += 1
            continue

        # Load knowledge file
        knowledge = load_json(json_path)

        # Convert to markdown
        md_content = convert_to_md(knowledge)

        # Write markdown file
        md_path = os.path.join(ctx.docs_dir, file_info["type"], file_info["category"], f"{file_info['id']}.md")
        os.makedirs(os.path.dirname(md_path), exist_ok=True)
        write_file(md_path, md_content)

        log_success(file_info['id'])
        generated_count += 1

    log_info(f"Step 5 completed: {generated_count} docs generated, {skipped_count} skipped")
