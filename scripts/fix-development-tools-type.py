#!/usr/bin/env python3
"""Fix development-tools entries to use correct Type and Category ID."""

import re
import sys

def determine_dev_tools_category(source_path):
    """Determine the correct Category ID for development_tools files."""
    if '/testing_framework/' in source_path:
        return 'testing-framework'
    elif '/toolbox/' in source_path:
        return 'toolbox'
    elif '/java_static_analysis/' in source_path:
        return 'java-static-analysis'
    else:
        # Fallback for files directly under development_tools/
        return 'development-tools-general'

def update_target_path(target_path, old_category, new_category):
    """Update target path to reflect new type and category structure."""
    if not target_path or target_path.strip() == '':
        return target_path

    # Replace component/development-tools with development-tools/{new_category}
    if target_path.startswith('component/development-tools/'):
        filename = target_path.replace('component/development-tools/', '')
        return f'development-tools/{new_category}/{filename}'

    return target_path

def process_table_row(line):
    """Process a table row and fix development-tools entries."""
    # Skip separator rows
    if re.match(r'^\|[-:\s|]+\|$', line):
        return line

    # Parse table row
    parts = [p.strip() for p in line.split('|')]
    if len(parts) < 6:  # | + 5 columns + |
        return line

    # parts[0] is empty (before first |)
    # parts[1] is Source Path
    # parts[2] is Type
    # parts[3] is Category ID
    # parts[4] is Source Path Pattern
    # parts[5] is Target Path
    # parts[6] is empty (after last |)

    source_path = parts[1]
    type_value = parts[2]
    category_id = parts[3]
    pattern = parts[4]
    target_path = parts[5]

    # Only process development-tools related entries
    if category_id != 'development-tools' and type_value != 'component':
        return line

    if 'development_tools' not in source_path:
        return line

    # Determine new category based on source path
    new_category = determine_dev_tools_category(source_path)

    # Update type to development-tools
    new_type = 'development-tools'

    # Update target path
    new_target_path = update_target_path(target_path, category_id, new_category)

    # Rebuild row
    return f'| {source_path} | {new_type} | {new_category} | {pattern} | {new_target_path} |'

def main():
    input_file = 'doc/mapping/all-files-mapping-v6.md.new'
    output_file = 'doc/mapping/all-files-mapping-v6.md.fixed'

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(output_file, 'w', encoding='utf-8') as f:
        for line in lines:
            line = line.rstrip('\n')

            # Process table rows
            if line.startswith('|') and 'Source Path' not in line:
                processed = process_table_row(line)
                f.write(processed + '\n')
            else:
                f.write(line + '\n')

    print(f'Processed {input_file} -> {output_file}')
    print('Review the output and replace the original file if correct.')

if __name__ == '__main__':
    main()
