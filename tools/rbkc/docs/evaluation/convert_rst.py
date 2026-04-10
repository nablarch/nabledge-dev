#!/usr/bin/env python3
"""Minimal RST → knowledge JSON converter for search impact evaluation.

Usage:
    python convert_rst.py <source.rst> <output.json> --id <file_id>

This is a measurement tool, not the production RBKC converter.
It converts RST to knowledge JSON with enough fidelity to measure
search impact (content size, full-text search accuracy/speed).
"""

import argparse
import json
import os
import re
import sys


def detect_heading_chars(lines):
    """Detect heading underline characters in order of first appearance."""
    chars = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Overline style
        if (i + 2 < len(lines)
                and is_underline(line)
                and lines[i + 1].strip()
                and not is_underline(lines[i + 1])
                and is_underline(lines[i + 2])
                and line.strip()[0] == lines[i + 2].strip()[0]):
            char = line.strip()[0]
            if char not in chars:
                chars.append(char)
            i += 3
            continue
        # Underline style
        if (i + 1 < len(lines)
                and line.strip()
                and not is_underline(line)
                and is_underline(lines[i + 1])):
            char = lines[i + 1].strip()[0]
            if char not in chars:
                chars.append(char)
            i += 2
            continue
        i += 1
    return chars


def is_underline(line):
    stripped = line.strip()
    if len(stripped) < 3:
        return False
    char = stripped[0]
    if char not in "=-~^+#*_.`:!\"'":
        return False
    return all(c == char for c in stripped)


def parse_rst(source):
    """Parse RST source into title and sections."""
    lines = source.splitlines()
    heading_chars = detect_heading_chars(lines)

    if not heading_chars:
        return None, [("content", lines)]

    h1_char = heading_chars[0]
    h2_char = heading_chars[1] if len(heading_chars) > 1 else None

    title = None
    sections = []
    preamble = []
    current_section = None
    current_lines = []

    i = 0
    while i < len(lines):
        # Overline heading
        if (i + 2 < len(lines)
                and is_underline(lines[i])
                and lines[i + 1].strip()
                and is_underline(lines[i + 2])
                and lines[i].strip()[0] == lines[i + 2].strip()[0]):
            char = lines[i].strip()[0]
            level = heading_chars.index(char) if char in heading_chars else -1
            text = lines[i + 1].strip()
            if level == 0 and title is None:
                title = text
                i += 3
                continue
            elif level == 1:
                if current_section is not None:
                    sections.append((current_section, current_lines))
                elif current_lines:
                    preamble = current_lines
                current_section = text
                current_lines = []
                i += 3
                continue
            else:
                md_level = "#" * (level + 1)
                current_lines.append(f"{md_level} {text}")
                i += 3
                continue

        # Underline heading
        if (i + 1 < len(lines)
                and lines[i].strip()
                and not is_underline(lines[i])
                and is_underline(lines[i + 1])
                and not (i > 0 and is_underline(lines[i - 1])
                         and lines[i - 1].strip()[0] == lines[i + 1].strip()[0])):
            char = lines[i + 1].strip()[0]
            if char in heading_chars:
                level = heading_chars.index(char)
                text = lines[i].strip()
                if level == 0 and title is None:
                    title = text
                    i += 2
                    continue
                elif level == 1:
                    if current_section is not None:
                        sections.append((current_section, current_lines))
                    elif current_lines:
                        preamble = current_lines
                    current_section = text
                    current_lines = []
                    i += 2
                    continue
                else:
                    md_level = "#" * (level + 1)
                    current_lines.append(f"{md_level} {text}")
                    i += 2
                    continue

        if current_section is not None or title is not None:
            current_lines.append(lines[i])
        i += 1

    if current_section is not None:
        sections.append((current_section, current_lines))
    elif not sections and current_lines:
        preamble = current_lines

    # Prepend preamble to first section
    if preamble and sections:
        first_title, first_lines = sections[0]
        sections[0] = (first_title, preamble + first_lines)
    elif preamble and not sections:
        sections = [("content", preamble)]

    return title, sections


def convert_content(lines):
    """Convert RST content lines to Markdown. Minimal conversion for measurement."""
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip RST labels
        if re.match(r'\.\.\s+_[a-zA-Z0-9_-]+:', stripped):
            i += 1
            continue

        # code-block
        m = re.match(r'\.\.\s+code-block::\s*(\w*)', stripped)
        if m:
            lang = m.group(1) or ""
            output.append(f"```{lang}")
            i += 1
            # Skip blank lines
            while i < len(lines) and not lines[i].strip():
                i += 1
            # Read indented block
            while i < len(lines) and (lines[i].startswith("   ") or not lines[i].strip()):
                if lines[i].strip():
                    output.append(lines[i][3:] if len(lines[i]) > 3 else lines[i].strip())
                else:
                    output.append("")
                i += 1
            output.append("```")
            continue

        # Admonition directives
        m = re.match(r'\.\.\s+(note|warning|important|tip|caution|attention|danger|error|hint|seealso|deprecated|versionadded|versionchanged)::(.*)', stripped)
        if m:
            adm_type = m.group(1).capitalize()
            inline = m.group(2).strip()
            body_parts = [inline] if inline else []
            i += 1
            while i < len(lines) and (lines[i].startswith("   ") or not lines[i].strip()):
                if lines[i].strip():
                    body_parts.append(lines[i].strip())
                i += 1
            body = " ".join(body_parts)
            output.append(f"> **{adm_type}:** {body}")
            continue

        # list-table (simplified: just output raw content)
        if re.match(r'\.\.\s+list-table::', stripped):
            i += 1
            rows = []
            current_row = []
            current_cell = []
            header_rows = 0
            # Parse options
            while i < len(lines) and (lines[i].strip().startswith(":") or not lines[i].strip()):
                m2 = re.match(r'\s+:header-rows:\s+(\d+)', lines[i])
                if m2:
                    header_rows = int(m2.group(1))
                if not lines[i].strip():
                    i += 1
                    break
                i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            # Parse rows
            while i < len(lines):
                line2 = lines[i]
                if not line2.strip():
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines) and re.match(r'\s+[\*-]\s+-?\s*', lines[j]):
                        i = j
                        continue
                    if current_cell:
                        current_row.append(" ".join(current_cell).strip())
                    if current_row:
                        rows.append(current_row)
                    i = j
                    break
                m_row = re.match(r'\s+\*\s+-\s+(.*)', line2)
                if m_row:
                    if current_cell:
                        current_row.append(" ".join(current_cell).strip())
                    if current_row:
                        rows.append(current_row)
                    current_row = []
                    current_cell = [m_row.group(1).strip()]
                    i += 1
                    continue
                m_cell = re.match(r'\s+-\s+(.*)', line2)
                if m_cell:
                    if current_cell:
                        current_row.append(" ".join(current_cell).strip())
                    current_cell = [m_cell.group(1).strip()]
                    i += 1
                    continue
                if line2.startswith("     ") or line2.startswith("\t"):
                    current_cell.append(line2.strip())
                    i += 1
                    continue
                if current_cell:
                    current_row.append(" ".join(current_cell).strip())
                if current_row:
                    rows.append(current_row)
                break
            else:
                if current_cell:
                    current_row.append(" ".join(current_cell).strip())
                if current_row:
                    rows.append(current_row)
            if rows:
                max_cols = max(len(r) for r in rows)
                rows = [r + [""] * (max_cols - len(r)) for r in rows]
                output.append("| " + " | ".join(rows[0]) + " |")
                output.append("| " + " | ".join(["---"] * max_cols) + " |")
                for row in rows[1:]:
                    output.append("| " + " | ".join(row) + " |")
            continue

        # Strip toctree and contents directives
        if re.match(r'\.\.\s+(toctree|contents)::', stripped):
            i += 1
            while i < len(lines) and (lines[i].startswith("   ") or not lines[i].strip()):
                i += 1
            continue

        # image
        m = re.match(r'\.\.\s+image::\s+(.+)', stripped)
        if m:
            filename = m.group(1).strip().split("/")[-1]
            output.append(f"![](images/{filename})")
            i += 1
            while i < len(lines) and (lines[i].startswith("   ") or not lines[i].strip()):
                i += 1
            continue

        # figure
        m = re.match(r'\.\.\s+figure::\s+(.+)', stripped)
        if m:
            filename = m.group(1).strip().split("/")[-1]
            i += 1
            caption_parts = []
            while i < len(lines) and (lines[i].startswith("   ") or not lines[i].strip()):
                if lines[i].strip() and not lines[i].strip().startswith(":"):
                    caption_parts.append(lines[i].strip())
                i += 1
            caption = " ".join(caption_parts)
            output.append(f"![{caption}](images/{filename})")
            continue

        # Regular line
        output.append(line)
        i += 1

    text = "\n".join(output)

    # Inline markup
    text = re.sub(r':java:extdoc:`([^<>`]+?)\s*<([^>`]+)>`', r'`\1`', text)
    text = re.sub(r':java:extdoc:`([^`>]+)`',
                  lambda m: f"`{m.group(1).split('.')[-1].split('#')[0]}`", text)
    text = re.sub(r'`([^<>`]+?)\s*<(https?://[^>`]+)>`_', r'[\1](\2)', text)
    text = re.sub(r'``([^`]+)``', r'`\1`', text)

    # Clean up excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def is_no_knowledge_content(sections):
    """Check if file is navigation-only."""
    for _, sec_lines in sections:
        for line in sec_lines:
            stripped = line.strip()
            if not stripped:
                continue
            if re.match(r'\.\.\s+_[a-zA-Z0-9_-]+:', stripped):
                continue
            if re.match(r'\.\.\s+(toctree|contents)::', stripped):
                continue
            if stripped.startswith(":") or stripped.startswith(".."):
                continue
            return False
    return True


def extract_hints(content, raw_lines):
    """Extract hints from content."""
    hints = set()
    raw_text = "\n".join(raw_lines)

    for m in re.finditer(r':java:extdoc:`([^<>`]+?)\s*<([^>`]+)>`', raw_text):
        hints.add(m.group(1).strip())
        hints.add(m.group(2).strip())
    for m in re.finditer(r':java:extdoc:`([^`>]+)`', raw_text):
        fqcn = m.group(1).strip()
        hints.add(fqcn)
        hints.add(fqcn.split(".")[-1].split("#")[0])

    for m in re.finditer(r'\b([A-Z][a-zA-Z0-9]*(?:[A-Z][a-zA-Z0-9]*)+)\b', content):
        hints.add(m.group(1))
    for m in re.finditer(r'\b([a-z][a-z0-9]*(?:\.[a-z][a-z0-9]*){2,}(?:\.[A-Z][a-zA-Z0-9]*)?)\b', content):
        hints.add(m.group(1))
    for m in re.finditer(r'(@[A-Z][a-zA-Z0-9]+)', content):
        hints.add(m.group(1))
    for m in re.finditer(r'<(?:groupId|artifactId)>([^<]+)</(?:groupId|artifactId)>', content):
        hints.add(m.group(1))

    return sorted(h for h in hints if len(h) > 1)


def convert_file(source_path, file_id):
    """Convert a single RST file to knowledge JSON."""
    with open(source_path, "r", encoding="utf-8") as f:
        source = f.read()

    title, sections_raw = parse_rst(source)

    if is_no_knowledge_content(sections_raw):
        return {
            "id": file_id,
            "title": title or file_id,
            "official_doc_urls": [],
            "no_knowledge_content": True,
            "index": [],
            "sections": {},
        }

    index = []
    sections = {}
    for i, (sec_title, sec_lines) in enumerate(sections_raw):
        sid = f"s{i + 1}"
        content = convert_content(sec_lines)
        hints = extract_hints(content, sec_lines)
        index.append({"id": sid, "title": sec_title, "hints": hints})
        sections[sid] = content

    return {
        "id": file_id,
        "title": title or file_id,
        "official_doc_urls": [],
        "index": index,
        "sections": sections,
    }


def main():
    parser = argparse.ArgumentParser(description="Convert RST to knowledge JSON for evaluation")
    parser.add_argument("source", help="RST source file path")
    parser.add_argument("output", help="Output JSON path")
    parser.add_argument("--id", required=True, help="Knowledge file ID")
    args = parser.parse_args()

    result = convert_file(args.source, args.id)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Report
    content_lines = sum(len(v.splitlines()) for v in result.get("sections", {}).values())
    print(f"  {args.id}: {len(result.get('index', []))} sections, {content_lines} content lines")


if __name__ == "__main__":
    main()
