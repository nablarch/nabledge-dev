"""E2E tests for Phase 7: index.toon and browsable docs generation.

Creates a small temporary knowledge directory with fixture JSON files,
then verifies index.toon and browsable MD output.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _write_knowledge(base: Path, rel_path: str, data: dict) -> Path:
    p = base / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return p


@pytest.fixture()
def knowledge_dir(tmp_path):
    """Small fixture knowledge directory with 3 JSON files (1 excluded by no_knowledge)."""
    kd = tmp_path / "knowledge"

    _write_knowledge(kd, "component/handlers/handlers-error-handler.json", {
        "id": "handlers-error-handler",
        "title": "HTTPエラー制御ハンドラ",
        "no_knowledge_content": False,
        "sections": [
            {
                "id": "s1",
                "title": "概要",
                "content": "エラー制御を行うハンドラです。",
                "hints": ["HttpErrorHandler", "エラー制御"],
            },
            {
                "id": "s2",
                "title": "設定方法",
                "content": "コンポーネント定義ファイルに追加します。",
                "hints": [],
            },
        ],
    })

    _write_knowledge(kd, "component/handlers/handlers-session-handler.json", {
        "id": "handlers-session-handler",
        "title": "セッション変数保存ハンドラ",
        "no_knowledge_content": False,
        "sections": [
            {
                "id": "s1",
                "title": "概要",
                "content": "セッション管理を行います。",
                "hints": ["SessionStoreHandler"],
            },
        ],
    })

    # This file should be excluded from index.toon (no_knowledge_content=True)
    _write_knowledge(kd, "about/about-nablarch/about-nablarch-readme.json", {
        "id": "about-nablarch-readme",
        "title": "README",
        "no_knowledge_content": True,
        "sections": [],
    })

    # File with assets/ links in content — used to test path rewriting in docs MD
    _write_knowledge(kd, "component/handlers/handlers-asset-handler.json", {
        "id": "handlers-asset-handler",
        "title": "アセットリンクテスト",
        "no_knowledge_content": False,
        "sections": [
            {
                "id": "s1",
                "title": "概要",
                "content": (
                    "説明文です。\n"
                    "![図](assets/handlers-asset-handler/diagram.png)\n"
                    "[設定ファイル](assets/handlers-asset-handler/config.xml)"
                ),
                "hints": [],
            },
        ],
    })
    # Create the actual asset files so resolved links can be verified as existing
    asset_dir = kd / "assets" / "handlers-asset-handler"
    asset_dir.mkdir(parents=True, exist_ok=True)
    (asset_dir / "diagram.png").write_bytes(b"")
    (asset_dir / "config.xml").write_bytes(b"")

    return kd


# ---------------------------------------------------------------------------
# index.toon tests
# ---------------------------------------------------------------------------

class TestGenerateIndex:
    @pytest.fixture()
    def index_path(self, knowledge_dir, tmp_path):
        from scripts.create.index import generate_index
        out = tmp_path / "index.toon"
        generate_index(knowledge_dir, version="6", output_path=out)
        return out

    def test_file_created(self, index_path):
        """index.toon is created at the given path."""
        assert index_path.exists()

    def test_header_present(self, index_path):
        """index.toon starts with a # heading."""
        first_line = index_path.read_text(encoding="utf-8").splitlines()[0]
        assert first_line.startswith("#")

    def test_entry_count_in_header(self, index_path):
        """Header line contains entry count (3, not 4 — no_knowledge excluded)."""
        text = index_path.read_text(encoding="utf-8")
        assert "files[3," in text

    def test_no_knowledge_excluded(self, index_path):
        """Files with no_knowledge_content=True are excluded."""
        text = index_path.read_text(encoding="utf-8")
        assert "about-nablarch-readme" not in text
        assert "README" not in text

    def test_entry_has_title(self, index_path):
        """Each entry includes the document title."""
        text = index_path.read_text(encoding="utf-8")
        assert "HTTPエラー制御ハンドラ" in text

    def test_entry_has_type_and_category(self, index_path):
        """Each entry includes type and category derived from path."""
        text = index_path.read_text(encoding="utf-8")
        # type=component, category=handlers
        assert "component" in text
        assert "handlers" in text

    def test_entry_has_path(self, index_path):
        """Each entry includes the relative JSON path."""
        text = index_path.read_text(encoding="utf-8")
        assert "handlers-error-handler.json" in text

    def test_format_fields(self, index_path):
        """Each data line has 5 comma-separated fields."""
        lines = index_path.read_text(encoding="utf-8").splitlines()
        data_lines = [l for l in lines if l.startswith("  ")]
        assert data_lines, "Expected at least one data line"
        for line in data_lines:
            fields = line.strip().split(", ")
            assert len(fields) == 5, f"Expected 5 fields, got {len(fields)}: {line!r}"


# ---------------------------------------------------------------------------
# Browsable docs tests
# ---------------------------------------------------------------------------

class TestGenerateDocs:
    @pytest.fixture()
    def docs_dir(self, knowledge_dir, tmp_path):
        from scripts.create.docs import generate_docs
        out = tmp_path / "docs"
        generate_docs(knowledge_dir, docs_dir=out)
        return out

    def test_md_file_created(self, docs_dir):
        """Browsable MD files are created for each knowledge file."""
        md = docs_dir / "component/handlers/handlers-error-handler.md"
        assert md.exists()

    def test_no_knowledge_md_also_created(self, docs_dir):
        """Files with no_knowledge_content=True also get a minimal MD (for link targets)."""
        md = docs_dir / "about/about-nablarch/about-nablarch-readme.md"
        assert md.exists()

    def test_md_title(self, docs_dir):
        """Browsable MD starts with # title."""
        md = docs_dir / "component/handlers/handlers-error-handler.md"
        text = md.read_text(encoding="utf-8")
        assert text.startswith("# HTTPエラー制御ハンドラ")

    def test_md_section_heading(self, docs_dir):
        """Section titles appear as ## headings."""
        md = docs_dir / "component/handlers/handlers-error-handler.md"
        text = md.read_text(encoding="utf-8")
        assert "## 概要" in text
        assert "## 設定方法" in text

    def test_md_section_content(self, docs_dir):
        """Section content is included in the MD."""
        md = docs_dir / "component/handlers/handlers-error-handler.md"
        text = md.read_text(encoding="utf-8")
        assert "エラー制御を行うハンドラです。" in text

    def test_md_keywords_details(self, docs_dir):
        """Sections with hints get a <details><summary>keywords</summary> block."""
        md = docs_dir / "component/handlers/handlers-error-handler.md"
        text = md.read_text(encoding="utf-8")
        assert "<details>" in text
        assert "<summary>keywords</summary>" in text
        assert "HttpErrorHandler" in text

    def test_md_no_hints_no_details(self, docs_dir):
        """Sections without hints do not get an empty details block."""
        md = docs_dir / "component/handlers/handlers-error-handler.md"
        text = md.read_text(encoding="utf-8")
        # Section s2 has no hints — should not have spurious <details>
        # Count details blocks: only s1 has hints, so expect exactly 1
        assert text.count("<details>") == 1

    def test_no_knowledge_md_minimal(self, docs_dir):
        """no_knowledge_content MD has # title but no section content."""
        md = docs_dir / "about/about-nablarch/about-nablarch-readme.md"
        text = md.read_text(encoding="utf-8")
        assert "# README" in text
        # Should not have section headings
        assert "## " not in text

    def test_asset_links_rewritten_to_resolve_from_docs_md(self, docs_dir, knowledge_dir):
        """assets/ links in docs MD are rewritten so they resolve relative to the docs MD file.

        The docs MD lives at docs/component/handlers/handlers-asset-handler.md.
        The assets live at knowledge/assets/handlers-asset-handler/.
        The rewritten link must point to an existing file when resolved from the docs MD location.
        """
        import re
        md = docs_dir / "component/handlers/handlers-asset-handler.md"
        assert md.exists()
        text = md.read_text(encoding="utf-8")

        # Extract all relative link targets (not https://)
        links = [m.group(1) for m in re.finditer(r'\[.*?\]\(([^)]+)\)', text)
                 if not m.group(1).startswith("http")]
        links += [m.group(1) for m in re.finditer(r'!\[.*?\]\(([^)]+)\)', text)
                  if not m.group(1).startswith("http")]

        assert links, "Expected at least one asset link in docs MD"

        # Every relative link must resolve to an existing file from the docs MD directory
        for link in links:
            target = (md.parent / link).resolve()
            assert target.exists(), (
                f"Asset link {link!r} in docs MD does not resolve to an existing file "
                f"(resolved to {target})"
            )
