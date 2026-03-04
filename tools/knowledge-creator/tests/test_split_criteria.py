"""Tests for split criteria (Task 7: prevent context overflow)."""
import os
import pytest
from steps.step2_classify import Step2Classify


class TestSplitCriteria:
    """Test split criteria based on line count and section count."""

    def test_file_under_threshold_not_split(self, ctx):
        """File with 500 lines and 5 sections should NOT be split."""
        classifier = Step2Classify(ctx, dry_run=True)

        # Create RST content with 5 h2 sections, ~100 lines each
        content_parts = [
            "Main Title\n==========\n\nPreamble content here.\n"
        ]
        for i in range(1, 6):
            section_content = "\n".join([f"Line {j} of section {i}" for j in range(1, 96)])
            content_parts.append(f"Section {i}\n----------\n{section_content}\n")

        content = "\n".join(content_parts)
        lines = content.splitlines()
        total_lines = len(lines)

        # Verify we're under threshold
        assert total_lines < 800, f"Test setup error: {total_lines} lines (should be < 800)"

        # Write to test file
        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w", encoding="utf-8") as f:
            f.write(content)

        # Should not split
        should_split, sections, _ = classifier.should_split_file("test/test.rst", "rst")
        assert not should_split
        assert len(sections) == 5, f"Expected 5 sections, got {len(sections)}"

    def test_file_over_line_threshold_split(self, ctx):
        """File with >800 lines should be split."""
        classifier = Step2Classify(ctx, dry_run=True)

        # Create RST content with 10 h2 sections, ~90 lines each = ~900 lines total
        content_parts = [
            "Main Title\n==========\n\nPreamble.\n"
        ]
        for i in range(1, 11):
            section_content = "\n".join([f"Line {j} of section {i}" for j in range(1, 86)])
            content_parts.append(f"Section {i}\n----------\n{section_content}\n")

        content = "\n".join(content_parts)
        lines = content.splitlines()
        total_lines = len(lines)

        # Verify we're over threshold
        assert total_lines > 800, f"Test setup error: {total_lines} lines (should be > 800)"

        # Write to test file
        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w", encoding="utf-8") as f:
            f.write(content)

        # Should split
        should_split, _, _ = classifier.should_split_file("test/test.rst", "rst")
        assert should_split

    def test_file_with_many_sections_split(self, ctx):
        """File with 20 sections (line count under threshold) should be split."""
        classifier = Step2Classify(ctx, dry_run=True)

        # Create RST content with 20 h2 sections, ~30 lines each = ~600 lines total
        content_parts = [
            "Main Title\n==========\n\nPreamble.\n"
        ]
        for i in range(1, 21):
            section_content = "\n".join([f"Line {j} of section {i}" for j in range(1, 26)])
            content_parts.append(f"Section {i}\n----------\n{section_content}\n")

        content = "\n".join(content_parts)
        lines = content.splitlines()
        total_lines = len(lines)

        # Verify assumptions
        assert total_lines < 800, f"Test setup error: {total_lines} lines (should be < 800)"

        # Write to test file
        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w", encoding="utf-8") as f:
            f.write(content)

        # Should split due to section count
        should_split, sections, _ = classifier.should_split_file("test/test.rst", "rst")
        assert len(sections) == 20, f"Expected 20 sections, got {len(sections)}"
        assert should_split

    def test_grouping_respects_line_limit(self, ctx):
        """Grouping should respect 800-line limit per part."""
        classifier = Step2Classify(ctx, dry_run=True)

        # Create RST content with 10 h2 sections, ~150 lines each = ~1500 lines total
        content_parts = [
            "Main Title\n==========\n\nPreamble.\n"
        ]
        for i in range(1, 11):
            section_content = "\n".join([f"Line {j} of section {i}" for j in range(1, 146)])
            content_parts.append(f"Section {i}\n----------\n{section_content}\n")

        content = "\n".join(content_parts)
        sections = classifier.analyze_rst_sections(content)

        base_entry = {
            'id': 'test-file',
            'type': 'component',
            'category': 'test',
            'source_path': 'test/test.rst',
            'format': 'rst',
            'filename': 'test.rst'
        }

        # Split the file
        split_entries = classifier.split_file_entry(base_entry, sections, content)

        # Verify each part is under 800 lines
        for entry in split_entries:
            section_range = entry['section_range']
            part_lines = section_range['end_line'] - section_range['start_line']
            assert part_lines <= 800, f"Part has {part_lines} lines (should be <= 800)"

    def test_grouping_respects_section_count_limit(self, ctx):
        """Grouping should respect 15-section limit per part."""
        classifier = Step2Classify(ctx, dry_run=True)

        # Create RST content with 20 h2 sections, ~30 lines each = ~600 lines total
        content_parts = [
            "Main Title\n==========\n\nPreamble.\n"
        ]
        for i in range(1, 21):
            section_content = "\n".join([f"Line {j} of section {i}" for j in range(1, 26)])
            content_parts.append(f"Section {i}\n----------\n{section_content}\n")

        content = "\n".join(content_parts)
        sections = classifier.analyze_rst_sections(content)

        base_entry = {
            'id': 'test-file',
            'type': 'component',
            'category': 'test',
            'source_path': 'test/test.rst',
            'format': 'rst',
            'filename': 'test.rst'
        }

        # Split the file
        split_entries = classifier.split_file_entry(base_entry, sections, content)

        # Verify each part has <= 15 sections
        for entry in split_entries:
            section_count = len(entry['section_range']['sections'])
            assert section_count <= 15, f"Part has {section_count} sections (should be <= 15)"

    def test_grouping_splits_on_whichever_limit_hit_first(self, ctx):
        """Grouping should split when either line or section limit is hit."""
        classifier = Step2Classify(ctx, dry_run=True)

        # Create RST content with 12 h2 sections, ~100 lines each = ~1200 lines total
        content_parts = [
            "Main Title\n==========\n\nPreamble.\n"
        ]
        for i in range(1, 13):
            section_content = "\n".join([f"Line {j} of section {i}" for j in range(1, 96)])
            content_parts.append(f"Section {i}\n----------\n{section_content}\n")

        content = "\n".join(content_parts)
        sections = classifier.analyze_rst_sections(content)

        base_entry = {
            'id': 'test-file',
            'type': 'component',
            'category': 'test',
            'source_path': 'test/test.rst',
            'format': 'rst',
            'filename': 'test.rst'
        }

        # Split the file
        split_entries = classifier.split_file_entry(base_entry, sections, content)

        # Verify both constraints are satisfied
        for entry in split_entries:
            section_range = entry['section_range']
            part_lines = section_range['end_line'] - section_range['start_line']
            section_count = len(section_range['sections'])

            assert part_lines <= 800, f"Part has {part_lines} lines (should be <= 800)"
            assert section_count <= 15, f"Part has {section_count} sections (should be <= 15)"

    def test_large_section_expanded_to_h3(self, ctx):
        """Large h2 section (>800 lines) should be expanded to h3 subsections."""
        classifier = Step2Classify(ctx, dry_run=True)

        # Create RST content with 1 large h2 section containing h3 subsections
        content_parts = [
            "Main Title\n==========\n\nPreamble.\n",
            "Large Section\n-------------\n",
            "Introduction to large section.\n"
        ]

        # Add 10 h3 subsections, ~100 lines each = ~1000 lines for the h2 section
        for i in range(1, 11):
            subsection_content = "\n".join([f"Line {j} of subsection {i}" for j in range(1, 96)])
            content_parts.append(f"Subsection {i}\n^^^^^^^^^^^^^\n{subsection_content}\n")

        content = "\n".join(content_parts)
        sections = classifier.analyze_rst_sections(content)

        # Verify h2 section is large
        assert len(sections) == 1, f"Expected 1 h2 section, got {len(sections)}"
        assert sections[0]['line_count'] > 800, f"Test setup error: h2 has {sections[0]['line_count']} lines"

        base_entry = {
            'id': 'test-file',
            'type': 'component',
            'category': 'test',
            'source_path': 'test/test.rst',
            'format': 'rst',
            'filename': 'test.rst'
        }

        # Split the file
        split_entries = classifier.split_file_entry(base_entry, sections, content)

        # Should have multiple parts (h3 subsections)
        assert len(split_entries) > 1, f"Expected multiple parts from h3 expansion, got {len(split_entries)}"

    def test_single_oversized_h2_without_h3_stays_as_one_part(self, ctx, capsys):
        """Oversized h2 section without h3 subsections should stay as one part with warning."""
        classifier = Step2Classify(ctx, dry_run=True)

        # Create RST content with 1 large h2 section WITHOUT h3 subsections
        content_parts = [
            "Main Title\n==========\n\nPreamble.\n",
            "Large Section\n-------------\n"
        ]

        # Add 1000 lines of content without h3 subsections
        content_parts.append("\n".join([f"Line {i} of large section" for i in range(1, 1001)]))

        content = "\n".join(content_parts)
        sections = classifier.analyze_rst_sections(content)

        # Verify h2 section is large
        assert len(sections) == 1, f"Expected 1 h2 section, got {len(sections)}"
        assert sections[0]['line_count'] > 800, f"Test setup error: h2 has {sections[0]['line_count']} lines"

        base_entry = {
            'id': 'test-file',
            'type': 'component',
            'category': 'test',
            'source_path': 'test/test.rst',
            'format': 'rst',
            'filename': 'test.rst'
        }

        # Split the file
        split_entries = classifier.split_file_entry(base_entry, sections, content)

        # Should have exactly 1 part (cannot split)
        assert len(split_entries) == 1, f"Expected 1 part for unsplittable section, got {len(split_entries)}"

        # Verify warning was printed
        captured = capsys.readouterr()
        assert "WARNING" in captured.out, "Expected warning for oversized section without h3"
        assert "Large Section" in captured.out, "Warning should mention section title"
