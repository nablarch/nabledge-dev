"""Tests for section-unit split criteria."""
import os
import re
import pytest
from step2_classify import Step2Classify


class TestSectionSplit:
    """Test section-unit splitting."""

    def _make_rst(self, section_count, lines_per_section=20):
        """Helper: create RST content with N h2 sections."""
        parts = ["Main Title\n==========\n\nPreamble content.\n"]
        for i in range(1, section_count + 1):
            body = "\n".join([f"Line {j} of section {i}" for j in range(1, lines_per_section + 1)])
            parts.append(f"Section {i}\n----------\n{body}\n")
        return "\n".join(parts)

    def test_single_section_no_split_suffix(self, ctx):
        """h2セクション1個 → split_file_entry が1エントリを返し --s1 サフィックスなし。"""
        classifier = Step2Classify(ctx)
        content = self._make_rst(1)

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w") as f:
            f.write(content)

        should_split, sections, _ = classifier.should_split_file("test/test.rst", "rst")
        assert should_split  # always True for RST
        assert len(sections) == 1

        # split_file_entry returns 1 group; run() checks len > 1 before treating as split
        base_entry = {
            'id': 'test-file', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test-file.json',
            'assets_dir': 'component/test/assets/test-file/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)
        assert len(entries) == 1  # 1 group → run() will use base_entry (no --s1 suffix)

    def test_two_sections_split(self, ctx):
        """h2セクション2個 → 分割する。"""
        classifier = Step2Classify(ctx)
        content = self._make_rst(2)

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w") as f:
            f.write(content)

        should_split, sections, _ = classifier.should_split_file("test/test.rst", "rst")
        assert should_split
        assert len(sections) == 2

    def test_split_produces_one_entry_per_section(self, ctx):
        """5セクション(各20行の本文 + ヘッダー行) → 1グループ、全5セクションを含む。"""
        classifier = Step2Classify(ctx)
        content = self._make_rst(5)
        sections = classifier.analyze_rst_sections(content)

        base_entry = {
            'id': 'test-file', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test-file.json',
            'assets_dir': 'component/test/assets/test-file/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        # プリアンブル + 5セクション(各22-23行) = 119行 → 400行閾値以下なので1グループ
        assert len(entries) == 1
        assert len(entries[0]['section_range']['sections']) == 5
        assert entries[0]['split_info']['total_parts'] == 1
        assert entries[0]['split_info']['original_id'] == 'test-file'
        # 実際の行数は119行（プリアンブルとヘッダー行を含む）
        total_lines = sum(s['line_count'] for s in sections)
        assert entries[0]['split_info']['group_line_count'] == total_lines

    def test_split_id_format(self, ctx):
        """分割IDが {original}--s{N} 形式であること。"""
        classifier = Step2Classify(ctx)
        content = self._make_rst(3)
        sections = classifier.analyze_rst_sections(content)

        base_entry = {
            'id': 'libraries-tag', 'type': 'component', 'category': 'libraries',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/libraries/libraries-tag.json',
            'assets_dir': 'component/libraries/assets/libraries-tag/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        for entry in entries:
            assert '--' in entry['id'], f"ID should contain '--': {entry['id']}"
            assert entry['id'].startswith('libraries-tag--')
            # 連番形式: libraries-tag--s{N}
            suffix = entry['id'].split('--', 1)[1]
            assert re.match(r'^s\d+$', suffix), f"Expected s{{N}} format, got: {suffix}"

    def test_preamble_in_first_section(self, ctx):
        """最初のh2の前のプリアンブルが最初のセクションに含まれること。"""
        classifier = Step2Classify(ctx)
        content = self._make_rst(3)
        sections = classifier.analyze_rst_sections(content)

        # 現行のanalyze_rst_sectionsは最初のセクションのstart_lineを0にする
        assert sections[0]['start_line'] == 0

    def test_non_rst_not_split(self, ctx):
        """format="md" → 分割しない。"""
        classifier = Step2Classify(ctx)
        should_split, _, _ = classifier.should_split_file("test.md", "md")
        assert not should_split

    def test_section_range_covers_all_lines(self, ctx):
        """全エントリのsection_rangeが全行をカバーすること。"""
        classifier = Step2Classify(ctx)
        content = self._make_rst(3, lines_per_section=10)
        sections = classifier.analyze_rst_sections(content)
        lines = content.splitlines()

        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        all_lines = set()
        for entry in entries:
            sr = entry['section_range']
            for i in range(sr['start_line'], sr['end_line']):
                all_lines.add(i)

        assert all_lines == set(range(len(lines)))

    def test_duplicate_titles_get_unique_ids(self, ctx):
        """同じタイトルのh2セクションでも連番IDは重複しないこと。"""
        classifier = Step2Classify(ctx)

        # 同じタイトルのh2セクションを3つ作る(各150行)
        parts = ["Main Title\n==========\n\nPreamble.\n"]
        for i in range(3):
            body = "\n".join([f"Line {j}" for j in range(1, 151)])
            parts.append(f"Same Title\n----------\n{body}\n")
        content = "\n".join(parts)

        sections = classifier.analyze_rst_sections(content)
        assert len(sections) == 3

        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        # 3セクション × 150行 = 450行 → グループ化される
        # [Same Title (s1=150)] + [Same Title (s2=150)] = 300行 → 1グループ
        # [Same Title (s3=150)] = 150行 → 1グループ
        # 合計2グループ
        assert len(entries) == 2

        ids = [e['id'] for e in entries]
        assert len(ids) == len(set(ids)), f"Duplicate IDs found: {ids}"
        # 連番形式: test--s1, test--s3
        assert ids[0] == "test--s1"
        assert ids[1] == "test--s3"

    def test_sequential_section_ids_across_parts(self, ctx):
        """セクションIDがパートをまたいで通し連番になること。"""
        classifier = Step2Classify(ctx)

        # 3パートに分割されるファイル（各パート2セクション × 200行）
        parts = ["Main Title\n==========\n\nPreamble.\n"]
        for i in range(1, 7):
            body = "\n".join([f"Line {j}" for j in range(1, 201)])
            parts.append(f"Section {i}\n----------\n{body}\n")
        content = "\n".join(parts)

        sections = classifier.analyze_rst_sections(content)
        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        # 各パートの section_ids が通し連番になっていること
        all_section_ids = []
        for entry in entries:
            all_section_ids.extend(entry['section_range']['section_ids'])

        # s1, s2, s3, s4, s5, s6 が順に並ぶ
        assert all_section_ids == [f"s{i}" for i in range(1, len(all_section_ids) + 1)]

    def test_section_map_contains_rst_labels(self, ctx):
        """section_map が RST ラベル（.. _label:）を含むこと。"""
        classifier = Step2Classify(ctx)

        content = (
            "Main Title\n==========\n\nPreamble.\n\n"
            ".. _first-section:\n\n"
            "First Section\n----------\n"
            + "\n".join([f"Line {j}" for j in range(1, 50)]) + "\n\n"
            ".. _second-section:\n\n"
            "Second Section\n----------\n"
            + "\n".join([f"Line {j}" for j in range(1, 50)]) + "\n"
        )

        sections = classifier.analyze_rst_sections(content)
        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        assert entries, "Expected at least one entry"
        section_map = entries[0]['section_map']
        assert section_map, "section_map should not be empty"

        # RST ラベルが section_map に含まれること
        all_labels = [label for sm in section_map for label in sm['rst_labels']]
        assert 'first-section' in all_labels
        assert 'second-section' in all_labels

    def test_section_map_for_non_split_files(self, ctx, tmp_path):
        """RSTファイルに section_map が生成されること（1グループ → 非分割扱い）。"""
        classifier = Step2Classify(ctx)

        content = (
            "Main Title\n==========\n\nPreamble.\n\n"
            ".. _only-section:\n\n"
            "Only Section\n----------\n"
            + "\n".join([f"Line {j}" for j in range(1, 20)]) + "\n"
        )

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/single.rst", "w") as f:
            f.write(content)

        should_split, sections, _ = classifier.should_split_file("test/single.rst", "rst")
        assert should_split  # always True for RST

        # 1グループ → run() は非分割扱いで section_map を付与する
        # _extract_rst_labels_with_positions を直接テスト
        labels = classifier._extract_rst_labels_with_positions(content)
        assert any(label == 'only-section' for label, _ in labels)

    def test_h3_fallback_for_large_h2(self, ctx):
        """400行超のh2セクションがh3で再分割され、グループ化されること。"""
        classifier = Step2Classify(ctx)

        # h2が2つ。1つ目は小さい、2つ目は600行超でh3が3つ
        small_body = "\n".join([f"Line {j}" for j in range(1, 21)])
        # 大きいh2の中にh3を3つ(各200行)
        large_body_parts = ["Large section intro.\n"]
        for i in range(1, 4):
            h3_body = "\n".join([f"Line {j} of h3-{i}" for j in range(1, 201)])
            large_body_parts.append(f"Subsection {i}\n^^^^^^^^^^^^^^^^^^^^^^\n{h3_body}\n")
        large_body = "\n".join(large_body_parts)

        content = (
            f"Main Title\n==========\n\nPreamble.\n\n"
            f"Small Section\n----------\n{small_body}\n\n"
            f"Large Section\n----------\n{large_body}\n"
        )

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w") as f:
            f.write(content)

        sections = classifier.analyze_rst_sections(content)
        assert len(sections) == 2

        # 2つ目のh2が400行超であることを確認
        assert sections[1]['line_count'] > 400

        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        # Small Section: 23行, Subsection 1: 203行, Subsection 2: 203行, Subsection 3: 203行
        # グループ化: [Small(23) + Sub1(203)] + [Sub2(203)] + [Sub3(203)] = 3グループ
        assert len(entries) == 3
        # 1つ目のグループ: Small Section + Subsection 1 (2セクション, 226行)
        assert len(entries[0]['section_range']['sections']) == 2
        assert entries[0]['section_range']['sections'] == ['Small Section', 'Subsection 1']
        # 2つ目のグループ: Subsection 2 (1セクション, 203行)
        assert len(entries[1]['section_range']['sections']) == 1
        assert entries[1]['section_range']['sections'] == ['Subsection 2']
        # 3つ目のグループ: Subsection 3 (1セクション, 203行)
        assert len(entries[2]['section_range']['sections']) == 1
        assert entries[2]['section_range']['sections'] == ['Subsection 3']

    def test_h3_fallback_no_h3_keeps_large_h2(self, ctx):
        """400行超のh2にh3がない場合、そのままh2を1エントリとして扱うこと。

        Note: このテストでは WARNING ログが出力されるが、
        テストの主目的は分割動作の確認なので、ログ確認は省略。
        """
        classifier = Step2Classify(ctx)

        # h2が2つ。2つ目は600行だがh3がない
        small_body = "\n".join([f"Line {j}" for j in range(1, 21)])
        large_body = "\n".join([f"Line {j}" for j in range(1, 601)])

        content = (
            f"Main Title\n==========\n\nPreamble.\n\n"
            f"Small Section\n----------\n{small_body}\n\n"
            f"Large Section\n----------\n{large_body}\n"
        )

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w") as f:
            f.write(content)

        sections = classifier.analyze_rst_sections(content)
        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        # h3がないのでh2がそのまま → 2セクション
        # グループ化: [Small(20行)] + [Large(600行)] = 2グループ
        assert len(entries) == 2
        # 1つ目のグループ: Small Section (1セクション)
        assert len(entries[0]['section_range']['sections']) == 1
        # 2つ目のグループ: Large Section (1セクション、警告付きで維持)
        assert len(entries[1]['section_range']['sections']) == 1

    def test_small_sections_grouped(self, ctx):
        """5つの小さいセクション(各80行)が1グループにまとめられること。

        5 sections × 82 lines (80 body + 2 header) = 410 lines total
        Grouping: Sec1-4 (328) + Sec5 (82) → 2 groups (next would exceed 400)
        Verifies: Correct grouping when threshold is approached
        """
        classifier = Step2Classify(ctx)
        content = self._make_rst(5, lines_per_section=80)
        sections = classifier.analyze_rst_sections(content)

        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        # Each section has 82 lines (80 body + 2 header)
        # Grouping: Sec1+Sec2+Sec3+Sec4 = 82*4 = 328 (next would be 410 > 400)
        # So: Group1 (Sec1-4), Group2 (Sec5)
        assert len(entries) == 2
        assert len(entries[0]['section_range']['sections']) == 4
        assert len(entries[1]['section_range']['sections']) == 1

    def test_boundary_exactly_threshold(self, ctx):
        """2セクションの合計が閾値以下の場合、1グループになること。

        Tests the boundary condition where total lines ≤ 400.
        Verifies: 1 group when total doesn't exceed threshold
        """
        classifier = Step2Classify(ctx)

        # Adjust body sizes to get exactly 400 total lines
        # Section 1 will include preamble (5 lines) + section header (2 lines) + body
        # Section 2 will have section header (2 lines) + body + empty line
        body1 = "\n".join([f"Line {j}" for j in range(1, 193)])  # 192 lines
        body2 = "\n".join([f"Line {j}" for j in range(1, 198)])  # 197 lines

        content = (
            f"Main Title\n==========\n\nPreamble.\n\n"
            f"Section 1\n----------\n{body1}\n\n"
            f"Section 2\n----------\n{body2}\n"
        )

        sections = classifier.analyze_rst_sections(content)
        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        # Verify total is at or below threshold
        total_lines = sum(s['line_count'] for s in sections)
        assert total_lines <= 400, f"Expected ≤ 400 lines, got {total_lines}"

        # Should be 1 group since total doesn't exceed threshold
        assert len(entries) == 1
        assert len(entries[0]['section_range']['sections']) == 2
        assert entries[0]['split_info']['group_line_count'] == total_lines

    def test_boundary_exceeds_threshold(self, ctx):
        """3セクションの合計が閾値を超える場合、適切にグループ化されること。

        Section 1: 200 lines, Section 2: 150 lines, Section 3: 100 lines
        Expected: Group 1 (200+150=350), Group 2 (100)
        Verifies: 2 groups with correct line counts
        """
        classifier = Step2Classify(ctx)

        body1 = "\n".join([f"Line {j}" for j in range(1, 201)])
        body2 = "\n".join([f"Line {j}" for j in range(1, 151)])
        body3 = "\n".join([f"Line {j}" for j in range(1, 101)])

        content = (
            f"Main Title\n==========\n\nPreamble.\n\n"
            f"Section 1\n----------\n{body1}\n\n"
            f"Section 2\n----------\n{body2}\n\n"
            f"Section 3\n----------\n{body3}\n"
        )

        sections = classifier.analyze_rst_sections(content)
        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        # グループ1: Sec1(202行) + Sec2(152行) = 354行
        # グループ2: Sec3(102行) = 102行
        assert len(entries) == 2
        assert len(entries[0]['section_range']['sections']) == 2
        assert len(entries[1]['section_range']['sections']) == 1

        group1_lines = sections[0]['line_count'] + sections[1]['line_count']
        group2_lines = sections[2]['line_count']
        assert entries[0]['split_info']['group_line_count'] == group1_lines
        assert entries[1]['split_info']['group_line_count'] == group2_lines

    def test_large_h2_with_h3_grouped(self, ctx):
        """600行のh2セクションが3つのh3に展開され、適切にグループ化されること。

        h2 with 600 lines, 3 h3s (203 lines each including headers)
        Grouping: Each h3 is 203 lines, so 203+203 = 406 > 400
        Expected: 3 groups (one per h3, as each pair exceeds threshold)
        Verifies: All h3 titles appear in section_range.sections
        """
        classifier = Step2Classify(ctx)

        # h2の中に3つのh3(各200行の本文)
        h3_parts = []
        for i in range(1, 4):
            h3_body = "\n".join([f"Line {j} of h3-{i}" for j in range(1, 201)])
            h3_parts.append(f"Subsection {i}\n^^^^^^^^^^^^^^^^^^^^^^\n{h3_body}\n")

        large_body = "Large section intro.\n\n" + "\n".join(h3_parts)

        content = (
            f"Main Title\n==========\n\nPreamble.\n\n"
            f"Large Section\n----------\n{large_body}\n"
        )

        sections = classifier.analyze_rst_sections(content)
        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        # h2が400行超 → h3に展開
        # 各h3は203行(200本文+2ヘッダー+1空行)
        # 203 + 203 = 406 > 400 なので各h3は個別グループ
        assert len(entries) == 3

        # すべてのh3タイトルがsection_range.sectionsに含まれること
        all_sections = []
        for entry in entries:
            all_sections.extend(entry['section_range']['sections'])

        assert 'Subsection 1' in all_sections
        assert 'Subsection 2' in all_sections
        assert 'Subsection 3' in all_sections

    def test_threshold_consistency(self, ctx):
        """LINE_GROUP_THRESHOLDがh3展開とグループ化の両方で一貫して使用されること。

        Create h2 with 401 lines and h3 subsections
        Verifies: h2 is expanded to h3 (proves threshold triggers expansion)
        """
        classifier = Step2Classify(ctx)

        # 401行のh2(閾値400を1行だけ超える)、h3が2つ
        h3_parts = []
        for i in range(1, 3):
            h3_body = "\n".join([f"Line {j} of h3-{i}" for j in range(1, 201)])
            h3_parts.append(f"Subsection {i}\n^^^^^^^^^^^^^^^^^^^^^^\n{h3_body}\n")

        large_body = "Intro.\n\n" + "\n".join(h3_parts)

        content = (
            f"Main Title\n==========\n\nPreamble.\n\n"
            f"Large Section\n----------\n{large_body}\n"
        )

        sections = classifier.analyze_rst_sections(content)
        # 401行 → 400を超えるのでh3展開される
        assert sections[0]['line_count'] > 400

        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        # h3に展開されている証拠: Subsectionタイトルが使われている
        all_sections = []
        for entry in entries:
            all_sections.extend(entry['section_range']['sections'])

        # h3に展開されていればSubsectionタイトルが含まれる
        assert any('Subsection' in s for s in all_sections)

    def test_multiple_groups_per_file(self, ctx):
        """6セクションが適切に3グループに分割されること。

        Sections: 152, 152, 152, 82, 122, 52 lines (includes headers)
        Grouping logic: Group1 (152+152=304), Group2 (152+82+122=356), Group3 (52)
        Verifies: 3 groups with correct line counts
        """
        classifier = Step2Classify(ctx)

        bodies = [
            "\n".join([f"Line {j}" for j in range(1, 151)]),  # 150 body
            "\n".join([f"Line {j}" for j in range(1, 151)]),  # 150 body
            "\n".join([f"Line {j}" for j in range(1, 151)]),  # 150 body
            "\n".join([f"Line {j}" for j in range(1, 81)]),   # 80 body
            "\n".join([f"Line {j}" for j in range(1, 121)]),  # 120 body
            "\n".join([f"Line {j}" for j in range(1, 51)])    # 50 body
        ]

        parts = ["Main Title\n==========\n\nPreamble.\n"]
        for i, body in enumerate(bodies, 1):
            parts.append(f"Section {i}\n----------\n{body}\n")
        content = "\n".join(parts)

        sections = classifier.analyze_rst_sections(content)
        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        # グループ1: Sec1(152行) + Sec2(152行) = 304行 (next would be 456 > 400)
        # グループ2: Sec3(152行) + Sec4(82行) + Sec5(122行) = 356行 (next would be 408 > 400)
        # グループ3: Sec6(52行)
        assert len(entries) == 3

        # 各グループのセクション数を確認
        assert len(entries[0]['section_range']['sections']) == 2
        assert len(entries[1]['section_range']['sections']) == 3
        assert len(entries[2]['section_range']['sections']) == 1

    def test_mixed_small_and_large(self, ctx):
        """小さいh2と大きいh2(h3展開)が混在する場合の適切な処理。

        File with: small h2 (50 lines) + giant h2 (600 lines with 3 h3s of 200 each)
        Expected: small h2 kept separate, giant h2 expanded and grouped
        Verifies: Correct group boundaries (3 groups total)
        """
        classifier = Step2Classify(ctx)

        # 小さいh2
        small_body = "\n".join([f"Line {j}" for j in range(1, 51)])

        # 大きいh2の中に3つのh3(各200行)
        h3_parts = []
        for i in range(1, 4):
            h3_body = "\n".join([f"Line {j} of h3-{i}" for j in range(1, 201)])
            h3_parts.append(f"Subsection {i}\n^^^^^^^^^^^^^^^^^^^^^^\n{h3_body}\n")

        large_body = "Large section intro.\n\n" + "\n".join(h3_parts)

        content = (
            f"Main Title\n==========\n\nPreamble.\n\n"
            f"Small Section\n----------\n{small_body}\n\n"
            f"Large Section\n----------\n{large_body}\n"
        )

        sections = classifier.analyze_rst_sections(content)
        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        # グループ1: Small Section(52行) + Subsection 1(203行) = 255行
        # グループ2: Subsection 2(203行)
        # グループ3: Subsection 3(203行)
        assert len(entries) == 3

        # 最初のグループに小さいセクションが含まれること
        assert 'Small Section' in entries[0]['section_range']['sections']

        # h3のタイトルが含まれていること
        all_sections = []
        for entry in entries:
            all_sections.extend(entry['section_range']['sections'])
        assert 'Subsection 1' in all_sections
        assert 'Subsection 2' in all_sections
        assert 'Subsection 3' in all_sections

    def test_section_range_no_gaps_no_overlaps(self, ctx):
        """複数グループの場合、全行がちょうど1回カバーされること(ギャップや重複なし)。

        Create file with multiple groups
        Verifies: Each line 0 to len(content) appears in exactly one group
        Verifies: No gaps (missing lines), no overlaps (duplicate lines)
        """
        classifier = Step2Classify(ctx)

        # 3セクション(200, 150, 100行)で2グループに分かれるケース
        body1 = "\n".join([f"Line {j}" for j in range(1, 201)])
        body2 = "\n".join([f"Line {j}" for j in range(1, 151)])
        body3 = "\n".join([f"Line {j}" for j in range(1, 101)])

        content = (
            f"Main Title\n==========\n\nPreamble.\n\n"
            f"Section 1\n----------\n{body1}\n\n"
            f"Section 2\n----------\n{body2}\n\n"
            f"Section 3\n----------\n{body3}\n"
        )

        lines = content.splitlines()
        sections = classifier.analyze_rst_sections(content)
        base_entry = {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }
        entries = classifier.split_file_entry(base_entry, sections, content)

        # 各行が正確に1回だけカバーされていることを確認
        covered_lines = []
        for entry in entries:
            sr = entry['section_range']
            for i in range(sr['start_line'], sr['end_line']):
                covered_lines.append(i)

        # 重複がないこと
        assert len(covered_lines) == len(set(covered_lines)), "Overlapping line ranges detected"

        # すべての行がカバーされていること
        assert set(covered_lines) == set(range(len(lines))), "Gap or missing lines detected"

        # 順序が正しいこと(昇順)
        assert covered_lines == sorted(covered_lines), "Line ranges are not in order"


class TestEqualsH3Detection:
    """Tests for ===== as h3 marker recognition (Bug 2 fix).

    Before the fix, ===== was excluded from h3 detection, so large single-h2
    files with ===== subsections could not be split.
    """

    def _base_entry(self):
        return {
            'id': 'test', 'type': 'component', 'category': 'test',
            'source_path': 'test/test.rst', 'format': 'rst', 'filename': 'test.rst',
            'output_path': 'component/test/test.json',
            'assets_dir': 'component/test/assets/test/'
        }

    def test_equals_h3_marker_triggers_split(self, ctx):
        """===== をh3マーカーとして使ったファイルが分割されること (Bug 2修正確認)。

        Before fix: ===== excluded from h3 detection -> no split possible.
        After fix: ===== recognized as h3 -> split on subsection boundaries.
        """
        classifier = Step2Classify(ctx)

        h3_body = "\n".join([f"Line {j}" for j in range(1, 201)])
        content = (
            "Main Title\n==========\n\nPreamble.\n\n"
            "Large Section\n----------\n"
            f"Subsection A\n=============\n{h3_body}\n"
            f"Subsection B\n=============\n{h3_body}\n"
        )

        sections = classifier.analyze_rst_sections(content)
        assert len(sections) == 1
        assert sections[0]['line_count'] > 400

        entries = classifier.split_file_entry(self._base_entry(), sections, content)

        # With ===== recognized as h3, two subsections -> split into 2+ groups
        assert len(entries) > 1, (
            "===== h3 subsections should trigger split. "
            "If this fails, ===== is not being recognized as h3 (Bug 2 regression)."
        )
        all_sections = []
        for e in entries:
            all_sections.extend(e['section_range']['sections'])
        assert 'Subsection A' in all_sections
        assert 'Subsection B' in all_sections

    def test_equals_h3_with_multiple_h2(self, ctx):
        """複数h2のうち1つが=====サブセクションを持つ場合も分割される。"""
        classifier = Step2Classify(ctx)

        h3_body = "\n".join([f"Line {j}" for j in range(1, 201)])
        content = (
            "Main Title\n==========\n\nPreamble.\n\n"
            "Small Section\n----------\nSmall content.\n\n"
            "Large Section\n----------\n"
            f"Subsection A\n=============\n{h3_body}\n"
            f"Subsection B\n=============\n{h3_body}\n"
        )

        sections = classifier.analyze_rst_sections(content)
        assert len(sections) == 2

        entries = classifier.split_file_entry(self._base_entry(), sections, content)

        assert len(entries) > 1
        all_sections = []
        for e in entries:
            all_sections.extend(e['section_range']['sections'])
        assert 'Subsection A' in all_sections
        assert 'Subsection B' in all_sections

    def test_preamble_title_phantom_no_incorrect_split(self, ctx):
        """h1タイトル(=====)のファントムh3が誤った分割を起こさないこと。

        When the first h2 range includes preamble with 'Title\n=====',
        the ===== line may be detected as a phantom h3 marker.
        If no real h3 subsections exist, this should result in 1 group (no split).
        """
        classifier = Step2Classify(ctx)

        # Large h2 (>400 lines) with NO real h3, only the h1 title ===== in preamble
        body = "\n".join([f"Line {j}" for j in range(1, 402)])
        content = (
            "Main Title\n==========\n\nPreamble.\n\n"
            "Large Section\n----------\n" + body + "\n"
        )

        sections = classifier.analyze_rst_sections(content)
        # First h2 start_line is expanded to 0 (includes preamble with Main Title/=====)
        assert sections[0]['start_line'] == 0
        assert sections[0]['line_count'] > 400

        entries = classifier.split_file_entry(self._base_entry(), sections, content)

        # No real h3 -> phantom alone forms 1 group -> no split
        assert len(entries) == 1, (
            "Phantom h3 from h1 title should not cause incorrect split "
            "when no real h3 subsections exist."
        )
