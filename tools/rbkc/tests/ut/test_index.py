"""Unit tests for index.py — index.md generation."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.create.index import generate_index_md


# ---------------------------------------------------------------------------
# Tests for generate_index_md
# ---------------------------------------------------------------------------

def _write_json_with_sections(
    knowledge_dir: Path,
    output_path: str,
    data: dict,
) -> None:
    p = knowledge_dir / output_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


class TestGenerateIndexMdBasic:
    """Basic structure of the generated index.md."""

    def test_header_and_category_h2(self, tmp_path):
        """index.md starts with H1 then H2 per category."""
        kn = tmp_path / "knowledge"
        _write_json_with_sections(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "Universal DAO",
            "no_knowledge_content": False,
            "sections": [],
        })
        out = tmp_path / "index.md"
        generate_index_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "# Knowledge Index" in text
        assert "## component/libraries" in text

    def test_file_entry_h3_and_path(self, tmp_path):
        """Each file produces H3 title + path: line."""
        kn = tmp_path / "knowledge"
        _write_json_with_sections(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "Universal DAO",
            "no_knowledge_content": False,
            "sections": [],
        })
        out = tmp_path / "index.md"
        generate_index_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "### Universal DAO" in text
        assert "path: component/libraries/lib.json" in text

    def test_l2_section_as_list_item(self, tmp_path):
        """L2 sections appear as `- sN: title` list items."""
        kn = tmp_path / "knowledge"
        _write_json_with_sections(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "Universal DAO",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s2", "title": "使用方法", "content": "", "level": 2},
            ],
        })
        out = tmp_path / "index.md"
        generate_index_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "- s2: 使用方法" in text

    def test_l3_section_indented_under_l2(self, tmp_path):
        """L3 sections appear as `  - sN: title` (indented under L2)."""
        kn = tmp_path / "knowledge"
        _write_json_with_sections(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "Universal DAO",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s5", "title": "使用方法", "content": "", "level": 2},
                {"id": "s6", "title": "設定", "content": "", "level": 3},
            ],
        })
        out = tmp_path / "index.md"
        generate_index_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "- s5: 使用方法" in text
        assert "  - s6: 設定" in text

    def test_l4_section_omitted(self, tmp_path):
        """L4+ sections are omitted."""
        kn = tmp_path / "knowledge"
        _write_json_with_sections(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "Universal DAO",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "概要", "content": "", "level": 2},
                {"id": "s2", "title": "詳細", "content": "", "level": 4},
            ],
        })
        out = tmp_path / "index.md"
        generate_index_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "s2" not in text
        assert "詳細" not in text


class TestGenerateIndexMdSkipRules:
    """Skip rules for boilerplate section titles."""

    SKIP_TITLES = ["モジュール一覧", "アプリケーションフレームワーク", "制約", "ハンドラクラス名"]

    def test_skip_boilerplate_titles(self, tmp_path):
        """Sections with boilerplate titles are omitted from the index."""
        kn = tmp_path / "knowledge"
        for title in self.SKIP_TITLES:
            _write_json_with_sections(kn, f"component/handlers/{title}.json", {
                "id": "h1", "title": title,
                "no_knowledge_content": False,
                "sections": [
                    {"id": "s1", "title": title, "content": "", "level": 2},
                ],
            })
            out = tmp_path / f"index_{title}.md"
            generate_index_md(kn, out)
            text = out.read_text(encoding="utf-8")
            assert f"- s1: {title}" not in text, f"Should skip section title '{title}'"


class TestGenerateIndexMdExcelFlat:
    """Excel-derived files (no level field) → flat list."""

    def test_excel_sections_flat_list(self, tmp_path):
        """Sections without level field are listed as flat items (no nesting)."""
        kn = tmp_path / "knowledge"
        _write_json_with_sections(kn, "check/security/sec.json", {
            "id": "sec", "title": "Security Check",
            "no_knowledge_content": False,
            "sections": [
                {"id": "c1", "title": "入力値チェック", "content": ""},
                {"id": "c2", "title": "認証チェック", "content": ""},
            ],
        })
        out = tmp_path / "index.md"
        generate_index_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "- c1: 入力値チェック" in text
        assert "- c2: 認証チェック" in text


class TestGenerateIndexMdOrdering:
    """Files within a category are sorted by path (deterministic output)."""

    def test_files_sorted_by_path(self, tmp_path):
        """Files in the same category appear sorted by filename."""
        kn = tmp_path / "knowledge"
        _write_json_with_sections(kn, "component/libraries/zzz.json", {
            "id": "z", "title": "ZZZ", "no_knowledge_content": False, "sections": [],
        })
        _write_json_with_sections(kn, "component/libraries/aaa.json", {
            "id": "a", "title": "AAA", "no_knowledge_content": False, "sections": [],
        })
        out = tmp_path / "index.md"
        generate_index_md(kn, out)
        text = out.read_text(encoding="utf-8")
        pos_aaa = text.index("### AAA")
        pos_zzz = text.index("### ZZZ")
        assert pos_aaa < pos_zzz


class TestGenerateIndexMdNoKnowledgeContent:
    """Files with no_knowledge_content: true are excluded."""

    def test_no_knowledge_content_excluded(self, tmp_path):
        kn = tmp_path / "knowledge"
        _write_json_with_sections(kn, "component/libraries/skip.json", {
            "id": "skip", "title": "Skip Me",
            "no_knowledge_content": True,
            "sections": [{"id": "s1", "title": "Foo", "content": "", "level": 2}],
        })
        _write_json_with_sections(kn, "component/libraries/keep.json", {
            "id": "keep", "title": "Keep Me",
            "no_knowledge_content": False,
            "sections": [],
        })
        out = tmp_path / "index.md"
        generate_index_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "Skip Me" not in text
        assert "Keep Me" in text


class TestGenerateIndexMdIndexFileSkipped:
    """index.md and index.toon files in knowledge dir are not listed."""

    def test_index_files_are_skipped(self, tmp_path):
        kn = tmp_path / "knowledge"
        # Write a real knowledge file
        _write_json_with_sections(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "Lib", "no_knowledge_content": False, "sections": [],
        })
        # Write an index file that must not appear in output
        _write_json_with_sections(kn, "index.json", {
            "id": "idx", "title": "Index", "no_knowledge_content": False, "sections": [],
        })
        out = tmp_path / "index.md"
        generate_index_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "### Index" not in text
        assert "### Lib" in text

    def test_assets_json_is_excluded(self, tmp_path):
        """JSON files under assets/ are literalinclude source copies — not content."""
        kn = tmp_path / "knowledge"
        _write_json_with_sections(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "Lib", "no_knowledge_content": False, "sections": [],
        })
        # A JSON under assets/ that must be excluded
        _write_json_with_sections(kn, "assets/etl-etl/file_output.json", {
            "id": "file_output", "title": "file_output", "no_knowledge_content": False, "sections": [],
        })
        out = tmp_path / "index.md"
        generate_index_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "file_output" not in text
        assert "### Lib" in text

    def test_javadoc_json_is_excluded(self, tmp_path):
        """JSON files under javadoc/ are generated by javadoc_generate() — not content index."""
        kn = tmp_path / "knowledge"
        _write_json_with_sections(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "Lib", "no_knowledge_content": False, "sections": [],
        })
        _write_json_with_sections(kn, "javadoc/javadoc-nablarch-common-dao-UniversalDao.json", {
            "id": "javadoc-nablarch-common-dao-UniversalDao",
            "title": "class UniversalDao",
            "no_knowledge_content": False,
            "sections": [],
        })
        out = tmp_path / "index.md"
        generate_index_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "UniversalDao" not in text
        assert "### Lib" in text
