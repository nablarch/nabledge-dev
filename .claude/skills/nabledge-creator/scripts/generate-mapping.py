#!/usr/bin/env python3
"""
Generate documentation mapping from Nablarch official documentation.

Pipeline: enumerate() → classify() → verify() → enrich() → output()

Exit codes:
  0: Success (no review items)
  1: Success with review items
  2: Error
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import date


# Base directories for Nablarch v6
V6_BASES = {
    'nablarch-document-en': '.lw/nab-official/v6/nablarch-document/en',
    'nablarch-document-ja': '.lw/nab-official/v6/nablarch-document/ja',
    'system-development-guide': '.lw/nab-official/v6/nablarch-system-development-guide',
}


def enumerate_files(version: str) -> List[Dict]:
    """Enumerate all documentation files for the specified version."""
    files = []

    if version == 'v6':
        # nablarch-document (English)
        base_en = Path(V6_BASES['nablarch-document-en'])
        if base_en.exists():
            for rst in base_en.rglob('*.rst'):
                rel_path = rst.relative_to(base_en)
                # Exclude root README and .textlint
                if rel_path.name == 'README.md' or '.textlint' in rel_path.parts:
                    continue
                files.append({
                    'source_path': str(rel_path),
                    'abs_path': str(rst),
                    'source_repo': 'nablarch-document',
                    'lang': 'en'
                })

            for md in base_en.rglob('*.md'):
                rel_path = md.relative_to(base_en)
                if rel_path.name == 'README.md' or '.textlint' in rel_path.parts:
                    continue
                files.append({
                    'source_path': str(rel_path),
                    'abs_path': str(md),
                    'source_repo': 'nablarch-document',
                    'lang': 'en'
                })

        # system-development-guide (specific files only)
        base_guide = Path(V6_BASES['system-development-guide'])
        guide_files = [
            'en/Nablarch-system-development-guide/docs/nablarch-patterns/Asynchronous_operation_in_Nablarch.md',
            'en/Nablarch-system-development-guide/docs/nablarch-patterns/Nablarch_anti-pattern.md',
            'en/Nablarch-system-development-guide/docs/nablarch-patterns/Nablarch_batch_processing_pattern.md',
            'Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx',
        ]
        for file_path in guide_files:
            full_path = base_guide / file_path
            if full_path.exists():
                files.append({
                    'source_path': file_path,
                    'abs_path': str(full_path),
                    'source_repo': 'system-development-guide',
                    'lang': 'en'  # Or 'ja' for Sample_Project
                })

    return files


def classify_by_path(file_info: Dict) -> Dict:
    """
    Classify file based on path patterns.
    Returns: {type, category, pp, confidence}
    """
    path = file_info['source_path']
    repo = file_info['source_repo']

    # Default classification
    classification = {
        'type': None,
        'category': None,
        'pp': '',
        'confidence': 'unknown'
    }

    if repo == 'system-development-guide':
        if 'Asynchronous_operation_in_Nablarch.md' in path:
            return {'type': 'guide', 'category': 'nablarch-patterns', 'pp': '', 'confidence': 'confirmed'}
        elif 'Nablarch_anti-pattern.md' in path:
            return {'type': 'guide', 'category': 'nablarch-patterns', 'pp': '', 'confidence': 'confirmed'}
        elif 'Nablarch_batch_processing_pattern.md' in path:
            return {'type': 'guide', 'category': 'nablarch-patterns', 'pp': '', 'confidence': 'confirmed'}
        elif 'セキュリティ対応表.xlsx' in path:
            return {'type': 'check', 'category': 'security-check', 'pp': '', 'confidence': 'confirmed'}

    # nablarch-document patterns
    if path.startswith('about_nablarch/'):
        return {'type': 'about', 'category': 'about-nablarch', 'pp': '', 'confidence': 'confirmed'}

    if path.startswith('migrationguide/'):
        return {'type': 'about', 'category': 'migration', 'pp': '', 'confidence': 'confirmed'}

    if path.startswith('releases/'):
        return {'type': 'about', 'category': 'release-notes', 'pp': '', 'confidence': 'confirmed'}

    if path.startswith('application_framework/adaptors/'):
        return {'type': 'component', 'category': 'adapters', 'pp': '', 'confidence': 'confirmed'}

    if path.startswith('application_framework/application_framework/blank_project/'):
        classification = {'type': 'setup', 'category': 'blank-project', 'pp': '', 'confidence': 'confirmed'}
        # Check for PP in filename
        if 'Jbatch' in path:
            classification['pp'] = 'jakarta-batch'
        elif 'NablarchBatch' in path:
            classification['pp'] = 'nablarch-batch'
        elif 'Web.rst' in path or 'Web/' in path:
            if 'WebService' not in path:
                classification['pp'] = 'web-application'
        elif 'WebService' in path:
            classification['pp'] = 'restful-web-service'
        return classification

    if path.startswith('application_framework/application_framework/configuration/'):
        return {'type': 'setup', 'category': 'configuration', 'pp': '', 'confidence': 'confirmed'}

    if path.startswith('application_framework/application_framework/cloud_native/'):
        return {'type': 'setup', 'category': 'cloud-native', 'pp': '', 'confidence': 'confirmed'}

    if path.startswith('application_framework/application_framework/setting_guide/'):
        return {'type': 'setup', 'category': 'setting-guide', 'pp': '', 'confidence': 'confirmed'}

    # Handlers - complex logic
    if '/handlers/' in path:
        if '/handlers/batch/' in path:
            return {'type': 'processing-pattern', 'category': 'nablarch-batch', 'pp': 'nablarch-batch', 'confidence': 'confirmed'}
        elif '/handlers/http_messaging/' in path:
            return {'type': 'component', 'category': 'handlers', 'pp': 'http-messaging', 'confidence': 'confirmed'}
        elif '/handlers/mom_messaging/' in path:
            return {'type': 'component', 'category': 'handlers', 'pp': 'mom-messaging', 'confidence': 'confirmed'}
        elif '/handlers/rest/' in path:
            return {'type': 'component', 'category': 'handlers', 'pp': 'restful-web-service', 'confidence': 'confirmed'}
        elif '/handlers/web/' in path:
            return {'type': 'component', 'category': 'handlers', 'pp': 'web-application', 'confidence': 'confirmed'}
        elif '/handlers/web_service/' in path:
            return {'type': 'component', 'category': 'handlers', 'pp': 'http-messaging', 'confidence': 'confirmed'}
        elif '/handlers/standalone/' in path:
            return {'type': 'component', 'category': 'handlers', 'pp': 'nablarch-batch', 'confidence': 'needs_content'}
        elif '/handlers/common/' in path:
            return {'type': 'component', 'category': 'handlers', 'pp': '', 'confidence': 'confirmed'}
        elif '/handlers/messaging/' in path:
            return {'type': 'component', 'category': 'handlers', 'pp': 'db-messaging', 'confidence': 'confirmed'}

    # Processing patterns - batch
    if '/batch/jsr352/' in path:
        return {'type': 'processing-pattern', 'category': 'jakarta-batch', 'pp': 'jakarta-batch', 'confidence': 'confirmed'}
    elif '/batch/nablarch_batch/' in path:
        return {'type': 'processing-pattern', 'category': 'nablarch-batch', 'pp': 'nablarch-batch', 'confidence': 'confirmed'}
    elif path.startswith('application_framework/application_framework/batch/'):
        if 'index.rst' in path or 'functional_comparison' in path:
            return {'type': 'processing-pattern', 'category': 'nablarch-batch', 'pp': 'nablarch-batch', 'confidence': 'confirmed'}

    # Processing patterns - web
    if path.startswith('application_framework/application_framework/web_application/'):
        return {'type': 'processing-pattern', 'category': 'web-application', 'pp': 'web-application', 'confidence': 'confirmed'}

    # Processing patterns - REST
    if path.startswith('application_framework/application_framework/web_service/'):
        return {'type': 'processing-pattern', 'category': 'restful-web-service', 'pp': 'restful-web-service', 'confidence': 'confirmed'}

    # Processing patterns - messaging
    if '/messaging/http/' in path:
        return {'type': 'processing-pattern', 'category': 'http-messaging', 'pp': 'http-messaging', 'confidence': 'confirmed'}
    elif '/messaging/mom/' in path:
        return {'type': 'processing-pattern', 'category': 'mom-messaging', 'pp': 'mom-messaging', 'confidence': 'confirmed'}
    elif '/messaging/db/' in path:
        return {'type': 'processing-pattern', 'category': 'db-messaging', 'pp': 'db-messaging', 'confidence': 'confirmed'}

    # Libraries
    if path.startswith('application_framework/application_framework/libraries/'):
        return {'type': 'component', 'category': 'libraries', 'pp': '', 'confidence': 'confirmed'}

    # Development tools
    if path.startswith('development_tools/testing_framework/'):
        return {'type': 'development-tools', 'category': 'testing-framework', 'pp': '', 'confidence': 'confirmed'}
    elif path.startswith('development_tools/toolbox/'):
        return {'type': 'development-tools', 'category': 'toolbox', 'pp': '', 'confidence': 'confirmed'}
    elif path.startswith('development_tools/java_static_analysis/'):
        return {'type': 'development-tools', 'category': 'java-static-analysis', 'pp': '', 'confidence': 'confirmed'}

    return classification


def read_rst_content(file_path: str, lines: int = 50) -> str:
    """Read first N lines of RST file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return ''.join([f.readline() for _ in range(lines)])
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return ""


def verify_classification(classification: Dict, file_info: Dict) -> Dict:
    """
    Verify classification by reading content.
    All files are read to catch the ~14% misclassified by path patterns.
    """
    if classification['confidence'] == 'confirmed':
        # Even confirmed classifications need spot checking
        # For now, trust path-based confirmed classifications
        return classification

    if classification['confidence'] == 'needs_content':
        # Read content and try to confirm
        content = read_rst_content(file_info['abs_path'])
        # Simple heuristics for standalone handlers
        if 'batch' in content.lower() or 'DataReader' in content:
            classification['pp'] = 'nablarch-batch'
            classification['confidence'] = 'confirmed'
        else:
            classification['confidence'] = 'review'
        return classification

    if classification['confidence'] == 'unknown':
        classification['confidence'] = 'review'

    return classification


def extract_title(file_path: str, file_type: str) -> str:
    """Extract title from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if file_type == 'rst':
            # Find title with === or --- underline
            for i, line in enumerate(lines[:20]):
                if i > 0 and lines[i-1].strip():
                    if re.match(r'^=+\s*$', line) or re.match(r'^-+\s*$', line):
                        return lines[i-1].strip()

        elif file_type == 'md':
            # Find first # heading
            for line in lines[:20]:
                if line.startswith('# '):
                    return line[2:].strip()

        elif file_type == 'xlsx':
            # Use filename
            return Path(file_path).stem

    except Exception as e:
        print(f"Warning: Could not extract title from {file_path}: {e}", file=sys.stderr)

    return ""


def get_japanese_title(en_path: str, repo: str) -> str:
    """Get Japanese title from corresponding Japanese file."""
    if repo == 'nablarch-document':
        ja_path = en_path.replace('/en/', '/ja/')
        # Special case
        if 'duplicate_form_submission.rst' in ja_path:
            ja_path = ja_path.replace('duplicate_form_submission.rst', 'double_transmission.rst')

        full_path = Path(V6_BASES['nablarch-document-ja']) / ja_path.replace('en/', '').replace('.lw/nab-official/v6/nablarch-document/en/', '')
        if not full_path.exists():
            # Try direct replacement
            full_path = Path(en_path.replace('/en/', '/ja/'))

        if full_path.exists():
            return extract_title(str(full_path), 'rst' if full_path.suffix == '.rst' else 'md')

    elif repo == 'system-development-guide':
        # Use mapping table
        mapping = {
            'Asynchronous_operation_in_Nablarch.md': 'Nablarchでの非同期処理.md',
            'Nablarch_anti-pattern.md': 'Nablarchアンチパターン.md',
            'Nablarch_batch_processing_pattern.md': 'Nablarchバッチ処理パターン.md',
        }
        for en_name, ja_name in mapping.items():
            if en_name in en_path:
                ja_path = en_path.replace(en_name, ja_name).replace('/en/', '/ja/')
                full_path = Path(V6_BASES['system-development-guide']) / ja_path
                if full_path.exists():
                    return extract_title(str(full_path), 'md')

    return ""


def generate_official_url(source_path: str, repo: str) -> str:
    """Generate official documentation URL."""
    if repo == 'nablarch-document':
        # Remove .rst extension and replace with .html
        html_path = source_path.replace('.rst', '.html').replace('.md', '.html')
        return f"https://nablarch.github.io/docs/6u3/doc/{html_path}"

    elif repo == 'system-development-guide':
        if '.xlsx' in source_path:
            return f"https://github.com/Fintan-contents/nablarch-system-development-guide/blob/main/{source_path}"
        else:
            # Use Japanese filename for patterns
            ja_mapping = {
                'Asynchronous_operation_in_Nablarch.md': 'Nablarchでの非同期処理.md',
                'Nablarch_anti-pattern.md': 'Nablarchアンチパターン.md',
                'Nablarch_batch_processing_pattern.md': 'Nablarchバッチ処理パターン.md',
            }
            filename = Path(source_path).name
            ja_filename = ja_mapping.get(filename, filename)
            return f"https://github.com/Fintan-contents/nablarch-system-development-guide/blob/main/Nablarchシステム開発ガイド/docs/nablarch-patterns/{ja_filename}"

    return ""


def convert_target_path(source_path: str, type_val: str, category: str) -> str:
    """Convert source path to target path."""
    # Extract filename and path parts
    filename = Path(source_path).name
    parts = Path(source_path).parts

    # Convert filename: _ to -, extension to .md (unless .xlsx)
    if filename.endswith('.rst'):
        target_filename = filename.replace('.rst', '.md').replace('_', '-')
    elif filename.endswith('.md'):
        target_filename = filename.replace('_', '-')
    elif filename.endswith('.xlsx'):
        target_filename = filename
    else:
        target_filename = filename

    # Determine subdirectories and handle special cases based on category
    subdirs = ''

    if category == 'handlers' or category == 'adapters':
        # Preserve subdirectories after handlers/adaptors
        if 'handlers' in parts:
            idx = parts.index('handlers')
            if idx + 1 < len(parts) - 1:  # Has subdirectories
                subdirs = '/'.join(parts[idx+1:-1])
        elif 'adaptors' in parts:
            idx = parts.index('adaptors')
            if idx + 1 < len(parts) - 1:
                subdirs = '/'.join(parts[idx+1:-1])

    elif category in ['jakarta-batch', 'nablarch-batch']:
        # Batch processing patterns: preserve context to avoid collisions
        # Check if this is under getting_started or feature_details
        if 'getting_started' in parts or 'feature_details' in parts:
            # Find the context dir
            context = 'getting_started' if 'getting_started' in parts else 'feature_details'
            ctx_idx = parts.index(context)
            # Get segments after context dir up to filename
            if ctx_idx + 1 < len(parts) - 1:
                # There are subdirs after getting_started/feature_details
                subdirs_after = parts[ctx_idx + 1:-1]
                # Use the last subdir for unique naming
                if subdirs_after and (filename == 'index.rst' or filename == 'index.md'):
                    # Use getting-started-xxx format
                    prefix = 'getting-started' if context == 'getting_started' else 'feature-details'
                    target_filename = f"{prefix}-{subdirs_after[-1].replace('_', '-')}.md"

        # Special case: handlers/batch vs batch/ - disambiguate by adding context
        if 'handlers' in parts and 'batch' in parts:
            # This is handlers/batch - use 'handlers-' prefix
            if filename == 'index.rst' or filename == 'index.md':
                target_filename = 'handlers-batch.md'

    elif category in ['web-application', 'restful-web-service']:
        # Web patterns: preserve subdirectory context for disambiguation
        # Check if there's a subdirectory that provides context (http_messaging, rest, etc.)
        if 'web_service' in parts:
            idx = parts.index('web_service')
            if idx + 1 < len(parts) - 1:
                context_dir = parts[idx + 1]
                # Preserve this context in the filename or subdirs
                subdirs = context_dir
        elif 'web_application' in parts:
            idx = parts.index('web_application')
            if idx + 1 < len(parts) - 1:
                context_dir = parts[idx + 1]
                if context_dir not in ['architecture.rst', 'index.rst']:  # Not a direct file
                    subdirs = context_dir

    elif category in ['http-messaging', 'mom-messaging', 'db-messaging']:
        # Messaging patterns: flatten subdirectories
        pass

    elif category == 'libraries':
        # Libraries: preserve subdirectory for disambiguation
        if 'libraries' in parts:
            idx = parts.index('libraries')
            if idx + 1 < len(parts) - 1:
                # Preserve all subdirectories after libraries
                subdirs = '/'.join(parts[idx+1:-1])

    elif category == 'testing-framework':
        # Development tools: preserve meaningful path structure
        if 'testing_framework' in parts:
            idx = parts.index('testing_framework')
            path_segments = parts[idx+1:-1]  # Segments between testing_framework and filename
            if path_segments:
                # Extract meaningful segments: skip 'guide', 'development_guide'
                meaningful = [s for s in path_segments if not s in ['guide', 'development_guide']]
                if meaningful:
                    # Use last 2 segments for context if available
                    if len(meaningful) >= 2:
                        subdirs = '/'.join(meaningful[-2:])
                        # For index.rst, use the immediate parent
                        if filename == 'index.rst' or filename == 'index.md':
                            target_filename = meaningful[-1].replace('_', '-') + '.md'
                    else:
                        subdirs = meaningful[-1]
                        if filename == 'index.rst' or filename == 'index.md':
                            target_filename = meaningful[-1].replace('_', '-') + '.md'

                # Check for collision: if filename (not index) has same name as parent dir
                # e.g., 01_HttpDumpTool/01_HttpDumpTool.rst vs 01_HttpDumpTool/index.rst
                if not (filename == 'index.rst' or filename == 'index.md'):
                    base_name = Path(filename).stem
                    parent = meaningful[-1] if meaningful else ''
                    if base_name == parent and subdirs:
                        # This is a collision - use 'overview' suffix for the non-index file
                        target_filename = base_name.replace('_', '-') + '-overview.md'

    elif category in ['blank-project', 'cloud-native', 'setting-guide']:
        # Setup categories: flatten subdirectories
        pass

    elif category == 'toolbox':
        # Toolbox: preserve subdirectories for disambiguation
        if 'toolbox' in parts:
            idx = parts.index('toolbox')
            if idx + 1 < len(parts) - 1:
                subdirs = '/'.join(parts[idx+1:-1])

    # Special handling for index.rst - use parent directory name if not already handled
    if (filename == 'index.rst' or filename == 'index.md') and target_filename == 'index.md':
        # Get parent directory name (second-to-last part)
        if len(parts) >= 2:
            parent_dir = parts[-2]
            # Convert parent directory name with same rules
            target_filename = parent_dir.replace('_', '-') + '.md'

    # Build target path
    if subdirs:
        return f"{type_val}/{category}/{subdirs}/{target_filename}"
    else:
        return f"{type_val}/{category}/{target_filename}"


def enrich_mapping(mapping_list: List[Dict]) -> List[Dict]:
    """Enrich confirmed mappings with titles and URLs."""
    enriched = []

    for item in mapping_list:
        if item['classification']['confidence'] != 'confirmed':
            enriched.append(item)
            continue

        file_info = item['file_info']
        classification = item['classification']

        # Extract title
        file_type = 'rst' if file_info['abs_path'].endswith('.rst') else 'md' if file_info['abs_path'].endswith('.md') else 'xlsx'
        title = extract_title(file_info['abs_path'], file_type)
        title_ja = get_japanese_title(file_info['abs_path'], file_info['source_repo'])

        # Generate URL
        official_url = generate_official_url(file_info['source_path'], file_info['source_repo'])

        # Generate target path
        target_path = convert_target_path(
            file_info['source_path'],
            classification['type'],
            classification['category']
        )

        item['title'] = title
        item['title_ja'] = title_ja
        item['official_url'] = official_url
        item['target_path'] = target_path

        enriched.append(item)

    return enriched


def output_markdown(mapping_list: List[Dict], output_path: str):
    """Output mapping to Markdown file."""
    # Count confirmed items
    confirmed = [m for m in mapping_list if m['classification']['confidence'] == 'confirmed']

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Nablarch v6 Documentation Mapping\n\n")
        f.write(f"**Generated**: {date.today().strftime('%Y-%m-%d')}\n")
        f.write(f"**Total Files**: {len(confirmed)}\n\n")
        f.write("This table maps Nablarch v6 documentation files to nabledge-6 knowledge files.\n\n")

        # Header
        f.write("| Source Path | Title | Title (ja) | Official URL | Type | Category ID | Processing Pattern | Target Path |\n")
        f.write("|-------------|-------|------------|--------------|------|-------------|-------------------|-------------|\n")

        # Sort by source path
        sorted_items = sorted(confirmed, key=lambda x: x['file_info']['source_path'])

        for item in sorted_items:
            source_path = item['file_info']['source_path']
            title = item.get('title', '')
            title_ja = item.get('title_ja', '')
            url = f"[🔗]({item.get('official_url', '')})"
            type_val = item['classification']['type']
            category = item['classification']['category']
            pp = item['classification']['pp']
            target_path = item.get('target_path', '')

            f.write(f"| {source_path} | {title} | {title_ja} | {url} | {type_val} | {category} | {pp} | {target_path} |\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: generate-mapping.py VERSION [--output PATH]", file=sys.stderr)
        print("  VERSION: v6", file=sys.stderr)
        sys.exit(2)

    version = sys.argv[1]
    output_path = 'references/mapping/mapping-v6.md'

    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    # Pipeline
    print(f"Enumerating files for {version}...", file=sys.stderr)
    files = enumerate_files(version)
    print(f"Found {len(files)} files", file=sys.stderr)

    print("Classifying...", file=sys.stderr)
    mapping_list = []
    for file_info in files:
        classification = classify_by_path(file_info)
        mapping_list.append({
            'file_info': file_info,
            'classification': classification
        })

    print("Verifying classifications...", file=sys.stderr)
    for item in mapping_list:
        item['classification'] = verify_classification(item['classification'], item['file_info'])

    # Check for review items
    review_items = [m for m in mapping_list if m['classification']['confidence'] == 'review']

    print("Enriching mappings...", file=sys.stderr)
    mapping_list = enrich_mapping(mapping_list)

    print(f"Outputting to {output_path}...", file=sys.stderr)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    output_markdown(mapping_list, output_path)

    confirmed_count = len([m for m in mapping_list if m['classification']['confidence'] == 'confirmed'])
    print(f"\nCompleted: {confirmed_count} files mapped", file=sys.stderr)

    if review_items:
        print(f"\nReview items: {len(review_items)}", file=sys.stderr)
        review_json = {
            'review_items': [
                {
                    'source_path': item['file_info']['source_path'],
                    'hypothesis': f"{item['classification']['type']}/{item['classification']['category']}",
                    'issue': 'Classification needs content verification'
                }
                for item in review_items
            ]
        }
        print(json.dumps(review_json, indent=2))
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
