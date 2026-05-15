"""Unit tests for index.py — processing_patterns semantics (Phase 21-K).

processing_patterns is derived from the mapping-assigned type/category:
- type == "processing-pattern" → category (e.g. "nablarch-batch")
- any other type → ""

This matches KC's semantics (phase_f_finalize.py:303).
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


class TestGenerateIndexMd:
    """Tests for generate_index_md() — Markdown format for semantic search Stage1."""

    def _write_json(self, knowledge_dir: Path, output_path: str, data: dict) -> None:
        p = knowledge_dir / output_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def test_produces_markdown_file(self, tmp_path):
        """Output file is Markdown with H1 title."""
        kn = tmp_path / "knowledge"
        self._write_json(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "ユニバーサルDAO",
            "no_knowledge_content": False, "sections": [],
        })
        fi = _FakeFI("lib", "component", "libraries", "component/libraries/lib.json")
        out = tmp_path / "index.md"
        generate_index_md([fi], kn, out)
        text = out.read_text(encoding="utf-8")
        assert text.startswith("# Knowledge Index")

    def test_category_becomes_h2(self, tmp_path):
        """Each unique directory path becomes an H2 heading."""
        kn = tmp_path / "knowledge"
        self._write_json(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "ユニバーサルDAO",
            "no_knowledge_content": False, "sections": [],
        })
        fi = _FakeFI("lib", "component", "libraries", "component/libraries/lib.json")
        out = tmp_path / "index.md"
        generate_index_md([fi], kn, out)
        text = out.read_text(encoding="utf-8")
        assert "## component/libraries" in text

    def test_file_title_becomes_h3_with_path(self, tmp_path):
        """Each file gets H3 with its title, followed by path: line."""
        kn = tmp_path / "knowledge"
        self._write_json(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "ユニバーサルDAO",
            "no_knowledge_content": False, "sections": [],
        })
        fi = _FakeFI("lib", "component", "libraries", "component/libraries/lib.json")
        out = tmp_path / "index.md"
        generate_index_md([fi], kn, out)
        text = out.read_text(encoding="utf-8")
        assert "### ユニバーサルDAO" in text
        assert "path: component/libraries/lib.json" in text

    def test_l2_sections_listed(self, tmp_path):
        """L2 sections (level=2) appear as list items under the file."""
        kn = tmp_path / "knowledge"
        self._write_json(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "ユニバーサルDAO",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "機能概要", "level": 1, "content": ""},
                {"id": "s2", "title": "SQLを書かなくてもCRUDができる", "level": 2, "content": ""},
                {"id": "s3", "title": "使用方法", "level": 2, "content": ""},
            ],
        })
        fi = _FakeFI("lib", "component", "libraries", "component/libraries/lib.json")
        out = tmp_path / "index.md"
        generate_index_md([fi], kn, out)
        text = out.read_text(encoding="utf-8")
        assert "- s2: SQLを書かなくてもCRUDができる" in text
        assert "- s3: 使用方法" in text

    def test_l3_sections_indented(self, tmp_path):
        """L3 sections appear indented under L2."""
        kn = tmp_path / "knowledge"
        self._write_json(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "DAO",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s2", "title": "使用方法", "level": 2, "content": ""},
                {"id": "s3", "title": "設定", "level": 3, "content": ""},
            ],
        })
        fi = _FakeFI("lib", "component", "libraries", "component/libraries/lib.json")
        out = tmp_path / "index.md"
        generate_index_md([fi], kn, out)
        text = out.read_text(encoding="utf-8")
        assert "  - s3: 設定" in text

    def test_l4_and_deeper_omitted(self, tmp_path):
        """Sections deeper than L3 are not listed."""
        kn = tmp_path / "knowledge"
        self._write_json(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "DAO",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s2", "title": "使用方法", "level": 2, "content": ""},
                {"id": "s3", "title": "設定", "level": 3, "content": ""},
                {"id": "s4", "title": "詳細設定", "level": 4, "content": ""},
            ],
        })
        fi = _FakeFI("lib", "component", "libraries", "component/libraries/lib.json")
        out = tmp_path / "index.md"
        generate_index_md([fi], kn, out)
        text = out.read_text(encoding="utf-8")
        assert "s4" not in text
        assert "詳細設定" not in text

    def test_no_knowledge_content_excluded(self, tmp_path):
        """Files with no_knowledge_content: true are excluded."""
        kn = tmp_path / "knowledge"
        self._write_json(kn, "component/libraries/skip.json", {
            "id": "skip", "title": "Skip",
            "no_knowledge_content": True, "sections": [],
        })
        self._write_json(kn, "component/libraries/keep.json", {
            "id": "keep", "title": "Keep",
            "no_knowledge_content": False, "sections": [],
        })
        fis = [
            _FakeFI("skip", "component", "libraries", "component/libraries/skip.json"),
            _FakeFI("keep", "component", "libraries", "component/libraries/keep.json"),
        ]
        out = tmp_path / "index.md"
        generate_index_md(fis, kn, out)
        text = out.read_text(encoding="utf-8")
        assert "Skip" not in text
        assert "Keep" in text

    def test_multiple_categories_as_multiple_h2(self, tmp_path):
        """Different directory paths produce separate H2 sections."""
        kn = tmp_path / "knowledge"
        self._write_json(kn, "component/libraries/lib.json", {
            "id": "lib", "title": "DAO", "no_knowledge_content": False, "sections": [],
        })
        self._write_json(kn, "processing-pattern/nablarch-batch/batch.json", {
            "id": "batch", "title": "バッチ", "no_knowledge_content": False, "sections": [],
        })
        fis = [
            _FakeFI("lib", "component", "libraries", "component/libraries/lib.json"),
            _FakeFI("batch", "processing-pattern", "nablarch-batch",
                    "processing-pattern/nablarch-batch/batch.json"),
        ]
        out = tmp_path / "index.md"
        generate_index_md(fis, kn, out)
        text = out.read_text(encoding="utf-8")
        assert "## component/libraries" in text
        assert "## processing-pattern/nablarch-batch" in text

    def test_omits_skip_titles(self, tmp_path):
        """Sections with skip-listed titles are not included."""
        kn = tmp_path / "knowledge"
        self._write_json(kn, "component/handlers/handler.json", {
            "id": "handler", "title": "Handler",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "モジュール一覧", "level": 2, "content": ""},
                {"id": "s2", "title": "機能概要", "level": 2, "content": ""},
                {"id": "s3", "title": "ハンドラクラス名", "level": 2, "content": ""},
                {"id": "s4", "title": "制約", "level": 2, "content": ""},
            ],
        })
        fi = _FakeFI("handler", "component", "handlers", "component/handlers/handler.json")
        out = tmp_path / "index.md"
        generate_index_md([fi], kn, out)
        text = out.read_text(encoding="utf-8")
        assert "モジュール一覧" not in text
        assert "ハンドラクラス名" not in text
        assert "制約" not in text
        assert "機能概要" in text

    def test_sections_without_level_are_flat(self, tmp_path):
        """Sections without a level field (Excel-derived) appear as flat list items."""
        kn = tmp_path / "knowledge"
        self._write_json(kn, "check/security-check.json", {
            "id": "security-check", "title": "セキュリティチェック",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "XSSチェック", "content": ""},
                {"id": "s2", "title": "CSRFチェック", "content": ""},
            ],
        })
        fi = _FakeFI("security-check", "check", "check", "check/security-check.json")
        out = tmp_path / "index.md"
        generate_index_md([fi], kn, out)
        text = out.read_text(encoding="utf-8")
        assert "- s1: XSSチェック" in text
        assert "- s2: CSRFチェック" in text

    def test_sorted_by_path_within_category(self, tmp_path):
        """Files within a category are sorted by path."""
        kn = tmp_path / "knowledge"
        self._write_json(kn, "component/libraries/zzz.json", {
            "id": "zzz", "title": "Z", "no_knowledge_content": False, "sections": [],
        })
        self._write_json(kn, "component/libraries/aaa.json", {
            "id": "aaa", "title": "A", "no_knowledge_content": False, "sections": [],
        })
        fis = [
            _FakeFI("zzz", "component", "libraries", "component/libraries/zzz.json"),
            _FakeFI("aaa", "component", "libraries", "component/libraries/aaa.json"),
        ]
        out = tmp_path / "index.md"
        generate_index_md(fis, kn, out)
        text = out.read_text(encoding="utf-8")
        assert text.index("### A") < text.index("### Z")

    def test_empty_file_infos(self, tmp_path):
        """Empty input produces header-only output without error."""
        kn = tmp_path / "knowledge"
        kn.mkdir()
        out = tmp_path / "index.md"
        generate_index_md([], kn, out)
        text = out.read_text(encoding="utf-8")
        assert text.startswith("# Knowledge Index")
