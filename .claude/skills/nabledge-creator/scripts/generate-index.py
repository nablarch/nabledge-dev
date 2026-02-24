#!/usr/bin/env python3
"""
Generate knowledge search index (index.toon) from mapping metadata.

Usage:
    python generate-index.py v6 [--mapping PATH] [--output PATH] [--knowledge-dir DIR]

Exit codes:
  0: Success (no issues)
  1: Success with warnings (some hints may be insufficient)
  2: Error (invalid input, file not found, parsing failed)

Phase 2: Generates metadata-based index from mapping-v6.md
  - Extracts title, category, type from each mapping row
  - Generates basic hints from title keywords + category mapping
  - All entries marked "not yet created" (knowledge files pending)
  - Output: index.toon with 291 entries

Phase 3-4 (Future): Update index from created knowledge files
  - Scan .json files and aggregate hints from index[].hints
  - Update corresponding entries with detailed hints
  - Change path from "not yet created" to actual file path
"""

import argparse
import locale
import re
import sys
from pathlib import Path
from typing import List, Tuple


# Category keyword mapping (L1 keywords)
# Split multi-word keywords to avoid duplicates with title keywords
CATEGORY_KEYWORDS = {
    'adapters': ['アダプタ', '連携', '統合'],
    'handlers': ['ハンドラ', 'アーキテクチャ', '制御'],
    'libraries': ['ライブラリ', '機能', 'ユーティリティ'],
    'tools': ['ツール', 'テスト', '開発支援'],
    'jakarta-batch': ['バッチ', 'JSR352', 'Jakarta', 'Batch'],
    'nablarch-batch': ['バッチ', 'Nablarchバッチ', 'データ処理'],
    'web-application': ['Web', 'ウェブアプリケーション', 'HTTP'],
    'restful-web-service': ['REST', 'WebAPI', 'RESTful'],
    'messaging': ['メッセージング', 'MOM', 'キュー'],
    'blank-project': ['プロジェクト', 'セットアップ', '初期設定'],
    'cloud-native': ['クラウド', 'コンテナ', 'クラウドネイティブ'],
    'configuration': ['設定', '構成', 'コンフィグ'],
    'about-nablarch': ['Nablarch', '概要', 'コンセプト'],
    'nablarch-patterns': ['パターン', '設計', 'ベストプラクティス'],
    'security-check': ['セキュリティ', 'チェック', '対応表'],
}

# Type keyword mapping
TYPE_KEYWORDS = {
    'component': ['コンポーネント', '機能'],
    'processing-pattern': ['処理方式', 'アーキテクチャ'],
    'guide': ['ガイド', '開発'],
    'setup': ['セットアップ', '初期設定'],
    'about': ['概要', '説明'],
    'check': ['チェック', '確認'],
}

# Common Japanese particles to remove
JAPANESE_PARTICLES = ['の', 'を', 'に', 'は', 'で', 'と', 'から', 'まで', 'について', 'する', 'ための', 'による']


def extract_keywords_from_title(title_ja: str) -> List[str]:
    """
    Extract keywords from Japanese title.

    Simple heuristic: Extract 2+ character sequences, remove particles.
    """
    if not title_ja:
        return []

    # Remove parentheses and their content (e.g., "(Lettuce)")
    title_clean = re.sub(r'[（(][^）)]*[）)]', '', title_ja)

    # Split by common separators
    words = re.split(r'[　 、，]', title_clean)

    keywords = []
    for word in words:
        word = word.strip()
        if len(word) >= 2 and word not in JAPANESE_PARTICLES:
            keywords.append(word)

    # Also extract continuous katakana/kanji sequences (3+ chars)
    # This helps capture terms like "データベース", "ハンドラ", etc.
    katakana_sequences = re.findall(r'[ァ-ヶー]{3,}', title_clean)
    kanji_sequences = re.findall(r'[一-龯]{2,}', title_clean)

    keywords.extend(katakana_sequences)
    keywords.extend(kanji_sequences)

    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword not in seen:
            seen.add(keyword)
            unique_keywords.append(keyword)

    return unique_keywords[:5]  # Limit title keywords to 5


def map_category_to_keywords(category_id: str, type_field: str) -> List[str]:
    """
    Map category ID and type to L1 domain keywords.
    """
    keywords = []

    # Add category keywords
    if category_id in CATEGORY_KEYWORDS:
        keywords.extend(CATEGORY_KEYWORDS[category_id])

    # Add type keywords
    if type_field in TYPE_KEYWORDS:
        keywords.extend(TYPE_KEYWORDS[type_field])

    return keywords


def get_fallback_keywords(type_field: str) -> List[str]:
    """
    Get generic fallback keywords based on type.
    """
    fallbacks = {
        'component': ['機能', 'コンポーネント'],
        'processing-pattern': ['処理', 'アーキテクチャ'],
        'guide': ['ガイド', '説明'],
        'setup': ['設定', 'セットアップ'],
        'about': ['概要', 'について'],
        'check': ['チェック', '確認'],
    }
    return fallbacks.get(type_field, ['Nablarch', '機能'])


def add_japanese_hints_for_english_title(title: str, hints: List[str]) -> List[str]:
    """Add Japanese keywords if title is English-only."""
    # Check if title has Japanese characters
    has_japanese = any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9fff' for c in title)

    if not has_japanese:
        # Add Japanese translations for common English patterns
        english_to_japanese = {
            'openapi': ['OpenAPI', 'API仕様', '自動生成'],
            'generator': ['ジェネレータ', 'コード生成', '自動生成'],
            'sql executor': ['SQL実行', 'クエリ実行', 'SQLツール'],
            'test': ['テスト', '試験', '検証'],
            'duplicate form submission': ['二重サブミット', 'フォーム送信', '重複防止'],
            'prevention': ['防止', '対策'],
        }

        title_lower = title.lower()
        for pattern, ja_hints in english_to_japanese.items():
            if pattern in title_lower:
                hints.extend(ja_hints)
                break  # Add only one pattern match

    return hints


def generate_hints_from_metadata(title_ja: str, category_id: str, type_field: str) -> List[str]:
    """
    Generate 3-8 hints from metadata.

    Process:
    1. Extract keywords from Japanese title
    2. Add category and type keywords
    3. Add Japanese hints for English-only titles
    4. Deduplicate case-insensitively and limit to 8
    5. Ensure minimum 3 hints with fallbacks
    """
    hints = []

    # Extract keywords from title
    title_keywords = extract_keywords_from_title(title_ja)
    hints.extend(title_keywords)

    # Map category to keywords
    category_keywords = map_category_to_keywords(category_id, type_field)
    hints.extend(category_keywords)

    # Add Japanese hints for English-only titles
    hints = add_japanese_hints_for_english_title(title_ja, hints)

    # Deduplicate case-insensitively but preserve original case
    seen = set()
    unique_hints = []
    for hint in hints:
        if hint:
            hint_lower = hint.lower()
            if hint_lower not in seen:
                seen.add(hint_lower)
                unique_hints.append(hint)

    # Limit to 8 hints
    unique_hints = unique_hints[:8]

    # Ensure minimum 3 hints
    if len(unique_hints) < 3:
        fallback = get_fallback_keywords(type_field)
        for fb in fallback:
            fb_lower = fb.lower()
            if fb_lower not in seen:
                unique_hints.append(fb)
                seen.add(fb_lower)
                if len(unique_hints) >= 3:
                    break

    return unique_hints


def parse_mapping_file(mapping_path: Path) -> Tuple[List[Tuple[str, str, str]], int]:
    """
    Parse mapping-v6.md file and extract entries.

    Returns:
        Tuple of (entries_list, warning_count)
        entries_list: List of (title_ja, hints_string, path) tuples
        warning_count: Number of entries with insufficient hints
    """
    if not mapping_path.exists():
        print(f"Error: Mapping file not found: {mapping_path}", file=sys.stderr)
        sys.exit(2)

    entries = []
    warning_count = 0
    line_num = 0

    try:
        with open(mapping_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_num += 1

                # Skip header lines (first 7 lines: title, blank, generated, total, blank, headers, separator)
                if line_num <= 8:
                    continue

                # Skip empty lines
                if not line.strip():
                    continue

                # Parse table row
                if not line.startswith('|'):
                    continue

                # Skip separator line (contains dashes)
                if '----' in line:
                    continue

                # Split by | and clean up
                fields = [field.strip() for field in line.split('|')[1:-1]]  # Exclude first/last empty

                if len(fields) < 8:
                    print(f"Warning: Line {line_num} has insufficient fields, skipping", file=sys.stderr)
                    continue

                # Extract fields: [source_path, title, title_ja, official_url, type, category_id, processing_pattern, target_path]
                title_en = fields[1]
                title_ja = fields[2]
                type_field = fields[4]
                category_id = fields[5]

                # Use Japanese title, fallback to English if empty
                if not title_ja:
                    title_ja = title_en
                    if not title_ja:
                        print(f"Warning: Line {line_num} has empty title, skipping", file=sys.stderr)
                        warning_count += 1
                        continue

                # Generate hints
                hints = generate_hints_from_metadata(title_ja, category_id, type_field)

                # Check hint quality
                if len(hints) < 3:
                    print(f"Warning: Line {line_num} ({title_ja}) has only {len(hints)} hints", file=sys.stderr)
                    warning_count += 1

                # Convert hints to space-separated string
                hints_str = ' '.join(hints)

                # Path is always "not yet created" in Phase 2
                path = "not yet created"

                entries.append((title_ja, hints_str, path))

    except Exception as e:
        print(f"Error: Failed to parse mapping file at line {line_num}: {e}", file=sys.stderr)
        sys.exit(2)

    return entries, warning_count


def sort_entries_japanese(entries: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
    """
    Sort entries by title using Japanese lexical order.
    """
    try:
        # Set Japanese locale for sorting
        locale.setlocale(locale.LC_COLLATE, 'ja_JP.UTF-8')
        sorted_entries = sorted(entries, key=lambda x: locale.strxfrm(x[0]))
    except locale.Error:
        # Fallback to default sorting if Japanese locale not available
        print("Warning: Japanese locale not available, using default sorting", file=sys.stderr)
        sorted_entries = sorted(entries, key=lambda x: x[0])

    return sorted_entries


def write_toon_file(output_path: Path, entries: List[Tuple[str, str, str]], version: str):
    """
    Write entries to TOON format file.
    """
    count = len(entries)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# Nabledge-{version} Knowledge Index\n\n")
            f.write(f"files[{count},]{{title,hints,path}}:\n")

            # Write entries
            for title, hints, path in entries:
                f.write(f"  {title}, {hints}, {path}\n")

        print(f"Successfully generated index: {output_path}")
        print(f"Total entries: {count}")

    except Exception as e:
        print(f"Error: Failed to write output file: {e}", file=sys.stderr)
        sys.exit(2)


def main():
    parser = argparse.ArgumentParser(
        description='Generate knowledge search index from mapping metadata'
    )
    parser.add_argument(
        'version',
        choices=['v6', 'v5'],
        help='Version identifier (v6 or v5)'
    )
    parser.add_argument(
        '--mapping',
        type=Path,
        default=Path('.claude/skills/nabledge-creator/output/mapping-v6.md'),
        help='Path to mapping file (default: .claude/skills/nabledge-creator/output/mapping-v6.md)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output file path (default: {knowledge-dir}/index.toon)'
    )
    parser.add_argument(
        '--knowledge-dir',
        type=Path,
        default=Path('.claude/skills/nabledge-6/knowledge/'),
        help='Knowledge files directory (default: .claude/skills/nabledge-6/knowledge/)'
    )

    args = parser.parse_args()

    # Validate version
    if args.version not in ['v6', 'v5']:
        print(f"Error: Invalid version '{args.version}'. Must be 'v6' or 'v5'.", file=sys.stderr)
        sys.exit(2)

    # Set default output path if not specified
    if args.output is None:
        args.output = args.knowledge_dir / 'index.toon'

    # Update mapping path for v5 if needed
    if args.version == 'v5' and args.mapping == Path('.claude/skills/nabledge-creator/output/mapping-v6.md'):
        args.mapping = Path('.claude/skills/nabledge-creator/output/mapping-v5.md')

    print(f"Generating index for version {args.version}...")
    print(f"Mapping file: {args.mapping}")
    print(f"Output file: {args.output}")

    # Parse mapping file
    entries, warning_count = parse_mapping_file(args.mapping)

    if not entries:
        print("Error: No entries found in mapping file", file=sys.stderr)
        sys.exit(2)

    # Check for duplicate titles
    titles = [entry[0] for entry in entries]
    unique_titles = set(titles)
    if len(titles) != len(unique_titles):
        print("Warning: Duplicate titles found in mapping file", file=sys.stderr)
        # Keep only first occurrence
        seen = set()
        deduplicated = []
        for entry in entries:
            if entry[0] not in seen:
                deduplicated.append(entry)
                seen.add(entry[0])
        entries = deduplicated
        warning_count += 1

    # Sort entries by Japanese title
    entries = sort_entries_japanese(entries)

    # Create output directory if needed
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Write TOON file
    write_toon_file(args.output, entries, args.version)

    # Exit with appropriate code
    if warning_count > 0:
        print(f"\nCompleted with {warning_count} warnings")
        print("Some entries may have insufficient hints (< 3 keywords)")
        sys.exit(1)
    else:
        print("\nCompleted successfully with no warnings")
        sys.exit(0)


if __name__ == '__main__':
    main()
