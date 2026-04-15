"""Unit tests for Phase 10-6: hints Stage 1 deletion + Step A/B mapping."""
import json
import pytest
from pathlib import Path
from scripts.hints import build_hints_index, lookup_hints


# ---------------------------------------------------------------------------
# Stage 1 deletion
# ---------------------------------------------------------------------------

class TestStage1Deleted:
    def test_extract_hints_removed_from_module(self):
        """extract_hints はモジュールから削除されている。"""
        import scripts.hints as hints_mod
        assert not hasattr(hints_mod, "extract_hints"), (
            "extract_hints should be removed (Stage 1 deleted)"
        )

    def test_merge_hints_removed_from_module(self):
        """merge_hints はモジュールから削除されている。"""
        import scripts.hints as hints_mod
        assert not hasattr(hints_mod, "merge_hints"), (
            "merge_hints should be removed (no longer needed)"
        )

    def test_run_does_not_call_extract_hints(self):
        """run.py パイプラインから extract_hints 呼び出しが除去されている。"""
        import inspect
        import scripts.run as run_module
        src = inspect.getsource(run_module)
        assert "extract_hints(" not in src, (
            "extract_hints() should not be called in run.py pipeline"
        )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def catalog_cache(tmp_path):
    """Fake KC cache + catalog for Step A tests."""
    knowledge_dir = tmp_path / "knowledge" / "guide"
    knowledge_dir.mkdir(parents=True)

    # KC knowledge file: base_name = "fw-guide"
    kc_file = {
        "id": "fw-guide",
        "title": "ガイド",
        "no_knowledge_content": False,
        "official_doc_urls": [],
        "index": [
            {"id": "s1", "title": "概要",  "hints": ["HintA", "HintB"]},
            {"id": "s2", "title": "設定方法詳細", "hints": ["HintC"]},
            {"id": "s3", "title": "使用方法", "hints": ["HintD"]},
        ],
        "sections": {
            "s1": "HintA概要テキスト",
            "s2": "HintC設定内容",
            "s3": "HintD使用テキスト",
        },
    }
    (knowledge_dir / "fw-guide.json").write_text(
        json.dumps(kc_file, ensure_ascii=False)
    )

    # catalog.json with section_range.sections
    catalog = {
        "version": 6,
        "sources": [],
        "files": [
            {
                "source_path": ".lw/nab-official/v6/doc/guide.rst",
                "format": "rst",
                "id": "fw-guide",
                "base_name": "fw-guide",
                "output_path": "guide/fw-guide.json",
                "assets_dir": "guide/assets/fw-guide/",
                "section_range": {
                    "start_line": 0,
                    "end_line": 100,
                    "sections": ["概要", "設定方法", "使用方法"],
                },
            }
        ],
    }
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False))

    return tmp_path, catalog_path


@pytest.fixture
def catalog_cache_no_sections(tmp_path):
    """Fake KC cache + catalog for Step B tests (no section_range.sections)."""
    knowledge_dir = tmp_path / "knowledge" / "guide"
    knowledge_dir.mkdir(parents=True)

    # KC knowledge file: base_name = "handler-guide"
    kc_file = {
        "id": "handler-guide",
        "title": "ハンドラガイド",
        "no_knowledge_content": False,
        "official_doc_urls": [],
        "index": [
            {"id": "s1", "title": "機能説明",  "hints": ["HandlerA"]},
            {"id": "s2", "title": "設定例", "hints": ["ConfigB"]},
        ],
        "sections": {
            "s1": "HandlerA はリクエストを処理します。",
            "s2": "ConfigB の設定例を示します。xml での設定方法。",
        },
    }
    (knowledge_dir / "handler-guide.json").write_text(
        json.dumps(kc_file, ensure_ascii=False)
    )

    # RST source for content overlap
    rst_dir = tmp_path / ".lw" / "nab-official" / "v6" / "doc"
    rst_dir.mkdir(parents=True)
    rst_source = """\
ハンドラガイド
==============

概要
----

HandlerA はリクエストを処理します。

設定
----

ConfigB の設定例を示します。xml での設定方法。

"""
    (rst_dir / "handler-guide.rst").write_text(rst_source, encoding="utf-8")

    # catalog.json WITHOUT section_range.sections
    catalog = {
        "version": 6,
        "sources": [],
        "files": [
            {
                "source_path": ".lw/nab-official/v6/doc/handler-guide.rst",
                "format": "rst",
                "id": "handler-guide",
                "base_name": "handler-guide",
                "output_path": "guide/handler-guide.json",
                "assets_dir": "guide/assets/handler-guide/",
                "section_range": {"start_line": 0, "end_line": 20, "sections": []},
            }
        ],
    }
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False))

    return tmp_path, catalog_path


# ---------------------------------------------------------------------------
# Step A: Expected Sections mapping
# ---------------------------------------------------------------------------

class TestStepA:
    def test_direct_match_uses_rst_heading_as_key(self, catalog_cache):
        """KC title == Expected section → RST heading をキーとして使う。"""
        cache_dir, catalog_path = catalog_cache
        result = build_hints_index(cache_dir, catalog_path)
        assert "概要" in result["fw-guide"]
        assert result["fw-guide"]["概要"] == ["HintA", "HintB"]

    def test_substring_match(self, catalog_cache):
        """Expected が KC title の部分文字列 → Expected をキーとして使う。"""
        cache_dir, catalog_path = catalog_cache
        result = build_hints_index(cache_dir, catalog_path)
        # "設定方法" is substring of "設定方法詳細" → mapped to "設定方法"
        assert "設定方法" in result["fw-guide"]
        assert result["fw-guide"]["設定方法"] == ["HintC"]

    def test_direct_match_advances_pointer(self, catalog_cache):
        """直接一致したとき、次の KC エントリが次の Expected セクションに割り当てられる。"""
        cache_dir, catalog_path = catalog_cache
        result = build_hints_index(cache_dir, catalog_path)
        # s3 "使用方法" matches Expected "使用方法" directly
        assert "使用方法" in result["fw-guide"]
        assert result["fw-guide"]["使用方法"] == ["HintD"]

    def test_overflow_goes_to_last_expected(self, tmp_path):
        """KC セクション数 > Expected 数 → 末尾を超えた分は最後の Expected に割り当て。"""
        knowledge_dir = tmp_path / "knowledge" / "g"
        knowledge_dir.mkdir(parents=True)
        kc = {
            "id": "x-file",
            "title": "X",
            "no_knowledge_content": False,
            "official_doc_urls": [],
            "index": [
                {"id": "s1", "title": "概要",   "hints": ["H1"]},
                {"id": "s2", "title": "詳細",   "hints": ["H2"]},
                {"id": "s3", "title": "追加情報", "hints": ["H3"]},  # overflow
            ],
            "sections": {},
        }
        (knowledge_dir / "x-file.json").write_text(json.dumps(kc, ensure_ascii=False))

        catalog = {
            "version": 6,
            "sources": [],
            "files": [
                {
                    "source_path": "x.rst",
                    "format": "rst",
                    "id": "x-file",
                    "base_name": "x-file",
                    "output_path": "x-file.json",
                    "assets_dir": "",
                    "section_range": {
                        "start_line": 0,
                        "end_line": 50,
                        "sections": ["概要", "詳細"],  # only 2 expected
                    },
                }
            ],
        }
        (tmp_path / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False))

        result = build_hints_index(tmp_path, tmp_path / "catalog.json")
        # Overflow s3 hints should go to last expected "詳細"
        assert "H1" in result["x-file"].get("概要", [])
        assert "H3" in result["x-file"].get("詳細", [])

    def test_without_catalog_uses_kc_title_fallback(self, catalog_cache):
        """catalog_path なし → 旧来の KC タイトルベースのマッピングにフォールバック。"""
        cache_dir, _ = catalog_cache
        result = build_hints_index(cache_dir)  # no catalog
        # Falls back to KC titles as keys
        assert "概要" in result["fw-guide"]
        assert result["fw-guide"]["概要"] == ["HintA", "HintB"]


# ---------------------------------------------------------------------------
# Step B: Content overlap mapping
# ---------------------------------------------------------------------------

class TestStepB:
    def test_content_overlap_maps_kc_hints_to_rst_heading(
        self, catalog_cache_no_sections
    ):
        """Expected Sections なし → コンテンツオーバーラップで RST 見出しにマッピング。"""
        cache_dir, catalog_path = catalog_cache_no_sections
        result = build_hints_index(cache_dir, catalog_path, repo_root=cache_dir)
        # RST has "概要" section with HandlerA content → HandlerA hints go there
        assert "handler-guide" in result
        assert "概要" in result["handler-guide"] or "設定" in result["handler-guide"]
        # At least one mapping should succeed
        all_hints = [h for s in result["handler-guide"].values() for h in s]
        assert "HandlerA" in all_hints or "ConfigB" in all_hints
