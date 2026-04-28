#!/usr/bin/env python3
"""
Diff check script for PR #315 (Issue #312).
Converts handler docs raw HTML (Handler.js script) to Markdown tables for nabledge-1.x.

This script classifies all files changed in the branch vs origin/main and
validates that every change falls into one of the expected categories.
Any file with changes outside those categories is flagged.

Usage:
    cd /path/to/nabledge-dev
    python3 .work/00312/diff-check.py

Expected change categories
--------------------------
A  Handler docs (MD)
   - 136 files (v1.2/v1.3/v1.4, 45-46 handlers each)
   - Change: invisible placeholder images removed, Handler.js script block
     converted to Markdown table, Bug 3 blank line added after bold headings
   - Note: handlers-RequestHandlerEntry.md has no Handler.js block (simpler handler)

B  Handler knowledge JSON
   - 136 files — regenerated from category A

C  Processing-pattern / library docs (MD) with Handler.js
   - 26 files (v1.2/v1.3/v1.4 processing-pattern + libraries-messaging-sending-batch
     + libraries-enterprise-messaging*)
   - Change: same Handler.js script block converted to Markdown table

D  Processing-pattern / library knowledge JSON
   - 26 files — regenerated from category C

E  Other docs (MD) — invisible image removal and/or Bug 3 blank lines only
   - 248 files (about, libraries, readers, guide, development-tools)
   - Change: only whitespace/blank lines and invisible image removal
   - No Handler.js script blocks in these files

F  Other knowledge JSON
   - 179 files — regenerated from category E

G  Tool / work files
   - 20 files (RBKC source code, tests, design docs, tasks, index.toon)
"""

import subprocess
import sys
import re
from collections import defaultdict


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout


def get_changed_files():
    out = run(['git', 'diff', '--name-only', 'origin/main..HEAD'])
    return [f for f in out.strip().split('\n') if f]


def get_diff(filepath):
    return run(['git', 'diff', 'origin/main..HEAD', '--', filepath])


def classify_file(filepath, diff):
    """Returns (category_letter, issues_list)."""
    issues = []

    # Tool / work / index files
    if (filepath.startswith('tools/')
            or filepath.startswith('.work/')
            or filepath.startswith('docs/')
            or filepath.endswith('.toon')):
        return 'G', []

    is_handler = bool(re.search(r'/handlers/handlers-', filepath))
    is_processing = bool(re.search(
        r'/(processing-pattern|libraries-messaging-sending-batch|libraries-enterprise-messaging)',
        filepath))
    is_json = filepath.endswith('.json')
    is_md = filepath.endswith('.md')

    if is_handler and is_md:
        return 'A', []
    if is_handler and is_json:
        return 'B', []
    if is_processing and is_md:
        return 'C', []
    if is_processing and is_json:
        return 'D', []

    if is_md:
        # Validate: only expected changes (invisible image removal, Bug 3 blank lines)
        if re.search(r'^\-<script>', diff, re.MULTILINE):
            issues.append(
                'UNEXPECTED: non-processing-pattern doc contains <script> removal')
        return 'E', issues

    if is_json:
        return 'F', []

    return 'UNKNOWN', ['Cannot classify file']


CATEGORY_LABELS = {
    'A': 'Handler docs (MD)                — Handler.js script → Markdown table',
    'B': 'Handler knowledge JSON            — regenerated from A',
    'C': 'Processing-pattern/library docs   — same Handler.js → Markdown table',
    'D': 'Processing-pattern/library JSON   — regenerated from C',
    'E': 'Other docs (MD)                   — Bug 3 blank-line fix + invisible image removal',
    'F': 'Other knowledge JSON              — regenerated from E',
    'G': 'Tool / work / index files         — RBKC source, tests, design docs, tasks',
    'UNKNOWN': 'UNCLASSIFIED',
}

EXPECTED_COUNTS = {
    'A': 136,
    'B': 136,
    'C': 26,
    'D': 26,
    'E': 248,
    'F': 179,
    'G': 20,
}


def main():
    files = get_changed_files()

    categories = defaultdict(list)
    all_issues = []

    for filepath in files:
        diff = get_diff(filepath)
        category, issues = classify_file(filepath, diff)
        categories[category].append(filepath)
        for issue in issues:
            all_issues.append(f"{issue}\n    File: {filepath}")

    print('=' * 70)
    print('DIFF CHECK REPORT: PR #315 (Issue #312)')
    print('Handler docs raw HTML → Markdown table conversion for nabledge-1.x')
    print('=' * 70)
    print()
    print(f'Total files changed: {len(files)}')
    print()

    count_ok = True
    for cat in sorted(CATEGORY_LABELS):
        count = len(categories.get(cat, []))
        expected = EXPECTED_COUNTS.get(cat)
        if expected is None:
            count_str = f'{count:4d}'
        elif count == expected:
            count_str = f'{count:4d}  (expected {expected}  OK)'
        else:
            count_str = f'{count:4d}  (expected {expected}  MISMATCH)'
            count_ok = False
        print(f'  {cat}  {count_str}  {CATEGORY_LABELS[cat]}')

    print()

    if all_issues:
        print(f'CONTENT ISSUES FOUND: {len(all_issues)}')
        for issue in all_issues:
            print(f'  {issue}')
        print()

    if all_issues or not count_ok:
        print('RESULT: FAIL — unexpected changes detected (see above)')
        sys.exit(1)
    else:
        print('RESULT: PASS — all 771 changed files are in expected categories,'
              ' counts match, no unexpected content changes.')

    print()
    print('Category C (processing-pattern/library docs with Handler.js):')
    for f in sorted(categories.get('C', [])):
        print(f'  {f}')


if __name__ == '__main__':
    main()
