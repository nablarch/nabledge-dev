#!/usr/bin/env python3
"""Add Type column to mapping file table."""

import re
import sys

def extract_type_from_target_path(target_path):
    """Extract type from target path (first directory component)."""
    if not target_path or target_path.strip() == '':
        return ''
    parts = target_path.strip().split('/')
    return parts[0] if parts else ''

def process_table_row(line):
    """Process a table row and add Type column."""
    # Skip separator rows
    if re.match(r'^\|[-:\s|]+\|$', line):
        # Update separator for new column structure
        return '|-------------|------|-------------|---------------------|--------------|'

    # Parse table row
    parts = [p.strip() for p in line.split('|')]
    if len(parts) < 5:  # | + 4 columns + |
        return line

    # parts[0] is empty (before first |)
    # parts[1] is Source Path
    # parts[2] is Category (will become Category ID)
    # parts[3] is Source Path Pattern
    # parts[4] is Target Path
    # parts[5] is empty (after last |)

    source_path = parts[1]
    category = parts[2]
    pattern = parts[3]
    target_path = parts[4]

    # Extract type from target path
    type_value = extract_type_from_target_path(target_path)

    # Rebuild row with Type column inserted after Source Path
    return f'| {source_path} | {type_value} | {category} | {pattern} | {target_path} |'

def main():
    input_file = 'doc/mapping/all-files-mapping-v6.md'
    output_file = 'doc/mapping/all-files-mapping-v6.md.new'

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(output_file, 'w', encoding='utf-8') as f:
        in_table = False
        header_written = False

        for line in lines:
            line = line.rstrip('\n')

            # Detect table header
            if line.startswith('| Source Path | Category |'):
                # Write new header
                f.write('| Source Path | Type | Category ID | Source Path Pattern | Target Path |\n')
                in_table = True
                header_written = True
                continue

            # Process table rows
            if in_table and line.startswith('|'):
                processed = process_table_row(line)
                f.write(processed + '\n')
            else:
                # Not in table or end of table
                if in_table and not line.startswith('|'):
                    in_table = False
                f.write(line + '\n')

    print(f'Processed {input_file} -> {output_file}')
    print('Review the output and replace the original file if correct.')

if __name__ == '__main__':
    main()
