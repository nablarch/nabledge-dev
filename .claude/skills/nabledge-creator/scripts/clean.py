#!/usr/bin/env python3
"""
Clean generated files for specified Nablarch version.

Deletes:
- Knowledge files (*.json)
- Docs files (*.md)
- Output files (mapping-v{version}.*)

Retains:
- index.toon
"""

import argparse
import sys
from pathlib import Path


def clean_version(version: str, repo_root: Path) -> dict:
    """Clean generated files for specified version.

    Args:
        version: Nablarch version (e.g., '6', '5')
        repo_root: Repository root path

    Returns:
        Dictionary with deletion counts
    """
    results = {
        'json_count': 0,
        'md_count': 0,
        'output_count': 0,
        'errors': []
    }

    # 1. Delete knowledge JSON files (keep index.toon)
    knowledge_dir = repo_root / f'.claude/skills/nabledge-{version}/knowledge'
    if knowledge_dir.exists():
        for json_file in knowledge_dir.rglob('*.json'):
            try:
                json_file.unlink()
                results['json_count'] += 1
            except Exception as e:
                results['errors'].append(f"Failed to delete {json_file}: {e}")

        # Remove empty directories
        for dirpath in sorted(knowledge_dir.rglob('*'), reverse=True):
            if dirpath.is_dir() and not any(dirpath.iterdir()):
                try:
                    dirpath.rmdir()
                except Exception as e:
                    results['errors'].append(f"Failed to remove directory {dirpath}: {e}")

    # 2. Delete all docs MD files
    docs_dir = repo_root / f'.claude/skills/nabledge-{version}/docs'
    if docs_dir.exists():
        for md_file in docs_dir.rglob('*.md'):
            try:
                md_file.unlink()
                results['md_count'] += 1
            except Exception as e:
                results['errors'].append(f"Failed to delete {md_file}: {e}")

        # Remove empty directories
        for dirpath in sorted(docs_dir.rglob('*'), reverse=True):
            if dirpath.is_dir() and not any(dirpath.iterdir()):
                try:
                    dirpath.rmdir()
                except Exception as e:
                    results['errors'].append(f"Failed to remove directory {dirpath}: {e}")

    # 3. Delete output files
    output_dir = repo_root / '.claude/skills/nabledge-creator/output'
    if output_dir.exists():
        output_patterns = [
            f'mapping-v{version}.md',
            f'mapping-v{version}.checklist.md',
            f'mapping-v{version}.xlsx'
        ]
        for pattern in output_patterns:
            output_file = output_dir / pattern
            if output_file.exists():
                try:
                    output_file.unlink()
                    results['output_count'] += 1
                except Exception as e:
                    results['errors'].append(f"Failed to delete {output_file}: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(description='Clean generated files for nabledge')
    parser.add_argument('version', type=str, help='Nablarch version (e.g., 6, 5)')

    args = parser.parse_args()

    # Validate version
    if args.version not in ['6', '5']:
        print(f"Error: Invalid version '{args.version}'. Must be 6 or 5.", file=sys.stderr)
        sys.exit(1)

    # Determine repository root (4 levels up from scripts/)
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent

    # Execute cleanup
    results = clean_version(args.version, repo_root)

    # Report results
    print(f"\nnabledge-{args.version} クリーン完了:")
    print(f"- 知識ファイル: {results['json_count']}個のJSONファイル削除")
    print(f"- ドキュメントファイル: {results['md_count']}個のMDファイル削除")
    print(f"- 出力ファイル: {results['output_count']}個のファイル削除")
    print(f"- 空ディレクトリ削除完了")
    print(f"- 保持: index.toon のみ")

    # Report errors if any
    if results['errors']:
        print(f"\n警告: {len(results['errors'])}個のエラーが発生しました:")
        for error in results['errors']:
            print(f"  - {error}")
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
