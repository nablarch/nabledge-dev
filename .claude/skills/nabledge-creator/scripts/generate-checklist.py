#!/usr/bin/env python3
"""
Generate verification checklist from RST source and JSON knowledge file.

Extracts structured elements from RST (classes, properties, annotations, directives,
exceptions, h2 headings) and from JSON (hints, sections, properties, errors).
Generates cross-reference checklist for verification session.

Exit codes:
  0: Success
  1: Error
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import date


def extract_from_rst(rst_path: Path) -> Dict:
    """Extract structured elements from RST file."""
    if not rst_path.exists():
        return {}

    with open(rst_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    elements = {
        'classes': [],
        'properties': [],
        'annotations': [],
        'directives': [],
        'exceptions': [],
        'h2_headings': []
    }

    for i, line in enumerate(lines, 1):
        # Class names: `ClassName` (starts with uppercase)
        for match in re.finditer(r'`([A-Z][a-zA-Z0-9_]*)`', line):
            class_name = match.group(1)
            elements['classes'].append({'name': class_name, 'line': i})

        # Properties: name="propertyName"
        for match in re.finditer(r'name="([a-zA-Z][a-zA-Z0-9_]*)"', line):
            prop_name = match.group(1)
            elements['properties'].append({'name': prop_name, 'line': i})

        # Annotations: @AnnotationName
        for match in re.finditer(r'@([A-Z][a-zA-Z0-9_]*)', line):
            anno_name = match.group(1)
            elements['annotations'].append({'name': anno_name, 'line': i})

        # Directives: .. directive::
        if line.strip().startswith('.. ') and '::' in line:
            directive_type = line.strip().split('::')[0].replace('.. ', '')
            # Get content (next non-empty line)
            content = ""
            for j in range(i, min(i+5, len(lines))):
                next_line = lines[j].strip()
                if next_line and not next_line.startswith('..'):
                    content = next_line[:80]
                    break
            elements['directives'].append({
                'type': directive_type,
                'line': i,
                'content': content
            })

        # Exception classes: ends with "Exception"
        for match in re.finditer(r'([A-Z][a-zA-Z0-9_]*Exception)', line):
            exc_name = match.group(1)
            elements['exceptions'].append({'name': exc_name, 'line': i})

        # h2 headings: next line is --- or ===
        if i < len(lines):
            next_line = lines[i] if i < len(lines) else ''
            if re.match(r'^[-=]{3,}$', next_line.strip()):
                heading = line.strip()
                if heading and not heading.startswith('..'):
                    elements['h2_headings'].append({'text': heading, 'line': i})

    # Deduplicate
    for key in elements:
        if key in ['classes', 'properties', 'annotations', 'exceptions']:
            seen = set()
            unique = []
            for item in elements[key]:
                if item['name'] not in seen:
                    seen.add(item['name'])
                    unique.append(item)
            elements[key] = unique

    return elements


def extract_from_json(json_path: Path) -> Dict:
    """Extract hints, sections, properties, errors from JSON."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    extracted = {
        'hints': {},  # {section_id: [hints]}
        'section_ids': [],
        'properties': [],
        'exceptions': []
    }

    # Extract hints by section
    for item in data.get('index', []):
        section_id = item.get('id')
        hints = item.get('hints', [])
        extracted['hints'][section_id] = hints

    # Extract section IDs
    extracted['section_ids'] = list(data.get('sections', {}).keys())

    # Extract properties from setup/configuration sections
    sections = data.get('sections', {})
    for section_id, section_content in sections.items():
        # Check for setup/configuration arrays
        if isinstance(section_content, list):
            for item in section_content:
                if isinstance(item, dict) and 'name' in item:
                    extracted['properties'].append(item['name'])
        elif isinstance(section_content, dict):
            # Check for setup key
            if 'setup' in section_content:
                setup = section_content['setup']
                if isinstance(setup, list):
                    for item in setup:
                        if isinstance(item, dict) and 'name' in item:
                            extracted['properties'].append(item['name'])

    # Extract exceptions from errors sections
    for section_id, section_content in sections.items():
        if isinstance(section_content, dict) and 'errors' in section_content:
            errors = section_content['errors']
            if isinstance(errors, dict) and 'list' in errors:
                for err in errors['list']:
                    if 'exception' in err:
                        extracted['exceptions'].append(err['exception'])
        # Also check if section itself is errors
        if section_id == 'errors' and isinstance(section_content, dict):
            if 'list' in section_content:
                for err in section_content['list']:
                    if 'exception' in err:
                        extracted['exceptions'].append(err['exception'])

    return extracted


def generate_hints_checklist(rst_elements: Dict, json_elements: Dict) -> List[str]:
    """Generate hints candidate checklist."""
    lines = []
    lines.append("## ヒント候補\n")
    lines.append("rstから抽出されたヒント候補。JSONのhintsに含まれているか確認せよ。\n")
    lines.append("| # | 候補 | 種別 | rst行番号 | JSON hints内 | 判定 |")
    lines.append("|---|---|---|---|---|---|")

    # Collect all candidates
    candidates = []

    # Classes
    for item in rst_elements.get('classes', []):
        candidates.append({
            'name': item['name'],
            'type': 'クラス名',
            'line': item['line']
        })

    # Properties
    for item in rst_elements.get('properties', []):
        candidates.append({
            'name': item['name'],
            'type': 'プロパティ',
            'line': item['line']
        })

    # Annotations
    for item in rst_elements.get('annotations', []):
        candidates.append({
            'name': '@' + item['name'],
            'type': 'アノテーション',
            'line': item['line']
        })

    # Check each candidate against JSON hints
    all_hints = json_elements.get('hints', {})

    for i, candidate in enumerate(candidates, 1):
        name = candidate['name']
        ctype = candidate['type']
        line = candidate['line']

        # Find in which section(s) this hint appears
        found_in = []
        for section_id, hints in all_hints.items():
            if name in hints:
                found_in.append(section_id)

        if found_in:
            status = ', '.join([f"{s}:✓" for s in found_in])
        else:
            status = "なし"

        lines.append(f"| {i} | `{name}` | {ctype} | L{line} | {status} | |")

    lines.append("\n「JSON hints内」が「なし」の項目を重点的に確認せよ。\n")

    return lines


def generate_spec_checklist(rst_elements: Dict, json_elements: Dict) -> List[str]:
    """Generate specification items checklist."""
    lines = []
    lines.append("## 仕様項目\n")

    # Properties
    lines.append("### プロパティ\n")
    lines.append("| # | プロパティ名 | rst行番号 | JSON setup内 | 判定 |")
    lines.append("|---|---|---|---|---|")

    rst_props = rst_elements.get('properties', [])
    json_props = json_elements.get('properties', [])

    for i, prop in enumerate(rst_props, 1):
        name = prop['name']
        line = prop['line']
        in_json = '✓' if name in json_props else 'なし'
        lines.append(f"| {i} | `{name}` | L{line} | {in_json} | |")

    lines.append("")

    # Directives
    lines.append("### ディレクティブ\n")
    lines.append("| # | 種別 | rst行番号 | 内容（先頭80文字） | 判定 |")
    lines.append("|---|---|---|---|---|")

    directives = rst_elements.get('directives', [])
    for i, directive in enumerate(directives, 1):
        dtype = directive['type']
        line = directive['line']
        content = directive['content']
        lines.append(f"| {i} | {dtype} | L{line} | {content} | |")

    lines.append("\n各ディレクティブについて：rstの該当行を読み、JSONのいずれかのセクションに内容が反映されているか確認せよ。\n")

    # Exceptions
    lines.append("### 例外クラス\n")
    lines.append("| # | 例外クラス名 | rst行番号 | JSON errors内 | 判定 |")
    lines.append("|---|---|---|---|---|")

    rst_excs = rst_elements.get('exceptions', [])
    json_excs = json_elements.get('exceptions', [])

    for i, exc in enumerate(rst_excs, 1):
        name = exc['name']
        line = exc['line']
        in_json = '✓' if name in json_excs else 'なし'
        lines.append(f"| {i} | `{name}` | L{line} | {in_json} | |")

    lines.append("")

    return lines


def generate_questions(json_path: Path, json_data: Dict) -> List[str]:
    """Generate test questions based on title and hints."""
    lines = []
    lines.append("## 想定質問\n")
    lines.append("以下の質問で検索シミュレーションを行え。\n")

    title = json_data.get('title', '')
    index = json_data.get('index', [])

    # Generate 3-5 questions based on title and hints
    questions = []

    # Q1: Based on title
    if title:
        questions.append(f"{title}の使い方を知りたい")

    # Q2-Q3: Based on section hints
    for item in index[:2]:
        hints = item.get('hints', [])
        if hints:
            # Pick a Japanese hint if available
            ja_hints = [h for h in hints if any(ord(c) > 127 for c in h)]
            if ja_hints:
                questions.append(f"{ja_hints[0]}について教えて")

    # Q4: Error-related
    if any('error' in s.lower() for s in json_data.get('sections', {}).keys()):
        questions.append("エラーが発生した時の対処法は？")

    for i, q in enumerate(questions, 1):
        lines.append(f"{i}. 「{q}」")

    lines.append("")

    return lines


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate-checklist.py JSON_PATH --source RST_PATH [--output PATH]")
        print()
        print("Generate verification checklist from RST and JSON.")
        print()
        print("Options:")
        print("  --source RST_PATH  Source RST file (can specify multiple times)")
        print("  --output PATH      Output checklist file (default: JSON_PATH.checklist.md)")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    rst_paths = []
    output_path = None

    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--source':
            if i + 1 < len(sys.argv):
                rst_paths.append(Path(sys.argv[i + 1]))
                i += 2
            else:
                print("ERROR: --source requires a path")
                sys.exit(1)
        elif sys.argv[i] == '--output':
            if i + 1 < len(sys.argv):
                output_path = Path(sys.argv[i + 1])
                i += 2
            else:
                print("ERROR: --output requires a path")
                sys.exit(1)
        else:
            i += 1

    if not output_path:
        output_path = json_path.with_suffix(json_path.suffix + '.checklist.md')

    if not json_path.exists():
        print(f"ERROR: JSON file not found: {json_path}")
        sys.exit(1)

    if not rst_paths:
        print("ERROR: At least one --source RST_PATH is required")
        sys.exit(1)

    # Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # Extract from RST files (merge if multiple)
    all_rst_elements = {
        'classes': [],
        'properties': [],
        'annotations': [],
        'directives': [],
        'exceptions': [],
        'h2_headings': []
    }

    for rst_path in rst_paths:
        print(f"Extracting from RST: {rst_path}")
        rst_elements = extract_from_rst(rst_path)
        for key in all_rst_elements:
            all_rst_elements[key].extend(rst_elements.get(key, []))

    # Extract from JSON
    print(f"Extracting from JSON: {json_path}")
    json_elements = extract_from_json(json_path)

    # Generate checklist
    print(f"Generating checklist: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        # Header
        f.write(f"# チェックリスト: {json_path.name}\n\n")
        f.write(f"**ソース**: {', '.join([str(p) for p in rst_paths])}\n")
        f.write(f"**生成日**: {date.today()}\n\n")
        f.write("---\n\n")

        # Hints checklist
        lines = generate_hints_checklist(all_rst_elements, json_elements)
        f.write('\n'.join(lines))
        f.write("\n---\n\n")

        # Spec checklist
        lines = generate_spec_checklist(all_rst_elements, json_elements)
        f.write('\n'.join(lines))
        f.write("\n---\n\n")

        # Questions
        lines = generate_questions(json_path, json_data)
        f.write('\n'.join(lines))

    print(f"Checklist generated: {output_path}")
    sys.exit(0)


if __name__ == '__main__':
    main()
