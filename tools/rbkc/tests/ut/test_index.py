"""Unit tests for index.py — processing_patterns semantics (Phase 21-K) and
index.md generation (Phase 22-B-2).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from scripts.create.index import generate_index, generate_index_md


@dataclass
class _FakeFI:
    """Minimal FileInfo stand-in for index tests."""
    file_id: str
    type: str
    category: str
    output_path: str
    source_path: Path = Path(".")
    format: str = "rst"


def _write_json(knowledge_dir: Path, output_path: str, data: dict) -> None:
    p = knowledge_dir / output_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _read_entries(index_path: Path) -> list[list[str]]:
    """Parse TOON data lines into list of fields per entry."""
    lines = index_path.read_text(encoding="utf-8").splitlines()
    entries: list[list[str]] = []
    for line in lines:
        if line.startswith("  "):
            fields = [f.strip() for f in line[2:].split(",")]
            entries.append(fields)
    return entries


class TestProcessingPatternsSemantics:
    """processing_patterns column reflects mapping-assigned type/category."""

    def test_processing_pattern_type_uses_category_as_pp(self, tmp_path):
        """type == 'processing-pattern' → processing_patterns == category."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "processing-pattern/nablarch-batch/nablarch-batch-intro.json", {
            "id": "nablarch-batch-intro",
            "title": "Nablarch Batch 概要",
            "no_knowledge_content": False,
            "sections": [],
        })
        fi = _FakeFI(
            file_id="nablarch-batch-intro",
            type="processing-pattern",
            category="nablarch-batch",
            output_path="processing-pattern/nablarch-batch/nablarch-batch-intro.json",
        )
        idx = tmp_path / "index.toon"
        n = generate_index([fi], kn, "6", idx)
        assert n == 1
        entries = _read_entries(idx)
        assert len(entries) == 1
        title, type_, category, pp, path = entries[0]
        assert type_ == "processing-pattern"
        assert category == "nablarch-batch"
        assert pp == "nablarch-batch"  # pp == category

    def test_non_processing_pattern_type_has_empty_pp(self, tmp_path):
        """Any non-processing-pattern type → processing_patterns == ''."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/handlers/handlers-error.json", {
            "id": "handlers-error",
            "title": "Error Handler",
            "no_knowledge_content": False,
            "sections": [],
        })
        fi = _FakeFI(
            file_id="handlers-error",
            type="component",
            category="handlers",
            output_path="component/handlers/handlers-error.json",
        )
        idx = tmp_path / "index.toon"
        generate_index([fi], kn, "6", idx)
        entries = _read_entries(idx)
        assert entries[0][1] == "component"
        assert entries[0][2] == "handlers"
        assert entries[0][3] == ""  # pp empty

    def test_about_type_has_empty_pp(self, tmp_path):
        kn = tmp_path / "knowledge"
        _write_json(kn, "about/release-notes/rn.json", {
            "id": "rn", "title": "RN",
            "no_knowledge_content": False, "sections": [],
        })
        fi = _FakeFI(
            file_id="rn", type="about", category="release-notes",
            output_path="about/release-notes/rn.json",
        )
        idx = tmp_path / "index.toon"
        generate_index([fi], kn, "6", idx)
        entries = _read_entries(idx)
        assert entries[0][1] == "about"
        assert entries[0][2] == "release-notes"
        assert entries[0][3] == ""

    def test_no_hints_field_injected_into_pp(self, tmp_path):
        """Even if JSON contains a stray 'hints' field, it must NOT leak into pp.

        Regression guard for the pre-Phase-21-K bug where _collect_hints(data)
        aggregated JSON hints into processing_patterns.
        """
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "Lib",
            "hints": ["stray-top-keyword"],
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "S", "content": "c", "hints": ["stray-sec-keyword"]},
            ],
        })
        fi = _FakeFI(
            file_id="lib", type="component", category="libraries",
            output_path="component/libraries/lib.json",
        )
        idx = tmp_path / "index.toon"
        generate_index([fi], kn, "6", idx)
        entries = _read_entries(idx)
        # All mapping-derived columns must stay clean — not just pp
        assert entries[0][1] == "component"
        assert entries[0][2] == "libraries"
        assert entries[0][3] == ""
        assert "stray-top-keyword" not in idx.read_text(encoding="utf-8")
        assert "stray-sec-keyword" not in idx.read_text(encoding="utf-8")


class TestGenerateIndexEdgeCases:
    def test_empty_file_infos_yields_header_only(self, tmp_path):
        """Empty file_infos → header with 0-count, no data rows."""
        kn = tmp_path / "knowledge"
        kn.mkdir()
        idx = tmp_path / "index.toon"
        n = generate_index([], kn, "6", idx)
        assert n == 0
        text = idx.read_text(encoding="utf-8")
        assert "files[0,]" in text
        assert _read_entries(idx) == []

    def test_entries_sorted_by_path(self, tmp_path):
        """Input order is not significant — output is sorted by path for determinism."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "z/z/last.json", {
            "id": "last", "title": "Last",
            "no_knowledge_content": False, "sections": [],
        })
        _write_json(kn, "a/a/first.json", {
            "id": "first", "title": "First",
            "no_knowledge_content": False, "sections": [],
        })
        # Pass in reverse alphabetical order
        fis = [
            _FakeFI("last", "z", "z", "z/z/last.json"),
            _FakeFI("first", "a", "a", "a/a/first.json"),
        ]
        idx = tmp_path / "index.toon"
        generate_index(fis, kn, "6", idx)
        entries = _read_entries(idx)
        paths = [e[-1] for e in entries]
        assert paths == ["a/a/first.json", "z/z/last.json"]


class TestNoKnowledgeContentExcluded:
    def test_no_knowledge_content_file_omitted(self, tmp_path):
        kn = tmp_path / "knowledge"
        _write_json(kn, "a/b/keep.json", {
            "id": "keep", "title": "Keep",
            "no_knowledge_content": False, "sections": [],
        })
        _write_json(kn, "a/b/skip.json", {
            "id": "skip", "title": "Skip",
            "no_knowledge_content": True, "sections": [],
        })
        keep = _FakeFI("keep", "a", "b", "a/b/keep.json")
        skip = _FakeFI("skip", "a", "b", "a/b/skip.json")
        idx = tmp_path / "index.toon"
        n = generate_index([keep, skip], kn, "6", idx)
        assert n == 1
        entries = _read_entries(idx)
        assert len(entries) == 1
        assert entries[0][0] == "Keep"


class TestMissingJsonSkipped:
    def test_file_info_without_json_is_skipped(self, tmp_path):
        """FileInfo whose JSON was not written (e.g. failed conversion) is skipped, not crashed."""
        kn = tmp_path / "knowledge"
        fi = _FakeFI("nonexistent", "component", "handlers", "component/handlers/nonexistent.json")
        idx = tmp_path / "index.toon"
        n = generate_index([fi], kn, "6", idx)
        assert n == 0


class TestTitleCommaEscape:
    def test_comma_in_title_replaced_with_japanese_comma(self, tmp_path):
        """TOON field separator is ASCII comma — commas in title would break the format."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "a/b/comma.json", {
            "id": "comma", "title": "Title, with, commas",
            "no_knowledge_content": False, "sections": [],
        })
        fi = _FakeFI("comma", "a", "b", "a/b/comma.json")
        idx = tmp_path / "index.toon"
        generate_index([fi], kn, "6", idx)
        text = idx.read_text(encoding="utf-8")
        assert "Title、 with、 commas" in text
        # Confirm no ASCII commas bleed into the title field
        assert "Title, with" not in text


# ---------------------------------------------------------------------------
# Tests for generate_index_md (Phase 22-B-2)
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
