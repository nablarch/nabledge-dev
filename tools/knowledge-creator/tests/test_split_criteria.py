"""Tests for section-unit split criteria."""
import os
import re
import pytest
from steps.step2_classify import Step2Classify


class TestSectionSplit:
    """Test section-unit splitting."""

    def _make_rst(self, section_count, lines_per_section=20):
        """Helper: create RST content with N h2 sections."""
        parts = ["Main Title\n==========\n\nPreamble content.\n"]
        for i in range(1, section_count + 1):
            body = "\n".join([f"Line {j} of section {i}" for j in range(1, lines_per_section + 1)])
            parts.append(f"Section {i}\n----------\n{body}\n")
        return "\n".join(parts)

    def test_single_section_not_split(self, ctx):
        """h2セクション1個 → 分割しない。"""
        classifier = Step2Classify(ctx, dry_run=True)
        content = self._make_rst(1)

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w") as f:
            f.write(content)

        should_split, sections, _ = classifier.should_split_file("test/test.rst", "rst")
        assert not should_split
        assert len(sections) == 1

    def test_two_sections_split(self, ctx):
        """h2セクション2個 → 分割する。"""
        classifier = Step2Classify(ctx, dry_run=True)
        content = self._make_rst(2)

        os.makedirs(f"{ctx.repo}/test", exist_ok=True)
        with open(f"{ctx.repo}/test/test.rst", "w") as f:
            f.write(content)

        should_split, sections, _ = classifier.should_split_file("test/test.rst", "rst")
        assert should_split
        assert len(sections) == 2

    def test_split_produces_one_entry_per_section(self, ctx):
        """5セクション(各20行の本文 + ヘッダー行) → 1グループ、全5セクションを含む。"""
        classifier = Step2Classify(ctx, dry_run=True)
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
        """分割IDが {original}--{section_id} 形式であること。"""
        classifier = Step2Classify(ctx, dry_run=True)
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

    def test_title_to_section_id_ascii(self):
        """英字タイトル → ASCII部分を使用。"""
        result = Step2Classify._title_to_section_id("module-list")
        assert result == "module-list"

    def test_title_to_section_id_mixed(self):
        """英字+日本語タイトル → ASCII部分が3文字以上ならそれを使用。"""
        result = Step2Classify._title_to_section_id("HTMLエスケープ")
        assert result == "html"

    def test_title_to_section_id_japanese_only(self):
        """日本語のみタイトル → ハッシュ。"""
        result = Step2Classify._title_to_section_id("モジュール一覧")
        assert result.startswith("sec-")
        assert len(result) == 12  # "sec-" + 8 hex chars

    def test_title_to_section_id_deterministic(self):
        """同じタイトル → 同じID(決定的)。"""
        id1 = Step2Classify._title_to_section_id("可変条件を持つSQL")
        id2 = Step2Classify._title_to_section_id("可変条件を持つSQL")
        assert id1 == id2

    def test_preamble_in_first_section(self, ctx):
        """最初のh2の前のプリアンブルが最初のセクションに含まれること。"""
        classifier = Step2Classify(ctx, dry_run=True)
        content = self._make_rst(3)
        sections = classifier.analyze_rst_sections(content)

        # 現行のanalyze_rst_sectionsは最初のセクションのstart_lineを0にする
        assert sections[0]['start_line'] == 0

    def test_non_rst_not_split(self, ctx):
        """format="md" → 分割しない。"""
        classifier = Step2Classify(ctx, dry_run=True)
        should_split, _, _ = classifier.should_split_file("test.md", "md")
        assert not should_split

    def test_section_range_covers_all_lines(self, ctx):
        """全エントリのsection_rangeが全行をカバーすること。"""
        classifier = Step2Classify(ctx, dry_run=True)
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
        """同じタイトルのh2セクションが重複しないIDを取得すること。"""
        classifier = Step2Classify(ctx, dry_run=True)

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
        # [Same Title (150)] + [Same Title (150)] = 300行 → 1グループ
        # [Same Title (150)] = 150行 → 1グループ
        # 合計2グループ
        assert len(entries) == 2

        ids = [e['id'] for e in entries]
        assert len(ids) == len(set(ids)), f"Duplicate IDs found: {ids}"
        # 期待: test--same-title, test--same-title-2
        assert ids[0] == "test--same-title"
        assert ids[1] == "test--same-title-2"

    def test_h3_fallback_for_large_h2(self, ctx):
        """400行超のh2セクションがh3で再分割され、グループ化されること。"""
        classifier = Step2Classify(ctx, dry_run=True)

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
        classifier = Step2Classify(ctx, dry_run=True)

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
