"""Unit tests for run.py — CLI layer only (argument validation, command routing)."""
# No create-side logic tests: verify.py is the quality gate for output correctness.
# See .claude/rules/rbkc.md for the test coverage policy.

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

_REPO_ROOT = Path(__file__).parents[4]  # repo root


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_file_info(fmt: str = "rst") -> MagicMock:
    """Return a FileInfo mock using a real file under repo root so relative_to() works."""
    fi = MagicMock()
    fi.format = fmt
    fi.file_id = "test-file"
    fi.output_path = "subdir/test.json"
    # Use a real file under repo_root to satisfy relative_to() in verify()
    fi.source_path = _REPO_ROOT / "tools/rbkc/tests/ut/test_run.py"
    return fi


def _make_valid_json(output_dir: Path, rel: str) -> Path:
    p = output_dir / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({
        "id": "test-file",
        "title": "Title",
        "no_knowledge_content": False,
        "sections": [{"id": "s1", "title": "概要", "content": "Content.", "hints": []}],
    }), encoding="utf-8")
    return p


def _make_valid_docs_md(docs_dir: Path, rel: str) -> Path:
    p = docs_dir / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("# Title\n\n## 概要\n\nContent.\n", encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# V-skip: verify() FAIL on missing JSON
# ---------------------------------------------------------------------------

class TestVerifyMissingJson:
    """verify() must FAIL (return False) when JSON file is missing, not silently skip."""

    def _run_verify(self, tmp_path, file_infos):
        from scripts.run import verify
        output_dir = tmp_path / "knowledge"
        output_dir.mkdir()
        (output_dir.parent / "docs").mkdir()

        with patch("scripts.run.scan_sources", return_value=[MagicMock()]), \
             patch("scripts.run.classify_sources", return_value=file_infos), \
             patch("scripts.run.build_label_map", return_value={}), \
             patch("scripts.create.scan._source_roots", return_value=[]):
            return verify(
                version="6",
                repo_root=_REPO_ROOT,
                output_dir=output_dir,
                files=["dummy/source.rst"],
            )

    def test_fail_when_json_missing(self, tmp_path):
        """verify returns False when JSON output file does not exist."""
        fi = _make_file_info()
        # Do NOT create the JSON file → should FAIL
        result = self._run_verify(tmp_path, [fi])
        assert result is False

    def test_pass_when_json_present(self, tmp_path):
        """verify returns True (for this check) when JSON and docs MD exist and are valid."""
        fi = _make_file_info()
        output_dir = tmp_path / "knowledge"
        output_dir.mkdir()
        _make_valid_json(output_dir, fi.output_path)
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        _make_valid_docs_md(docs_dir, Path(fi.output_path).with_suffix(".md"))

        from scripts.run import verify
        with patch("scripts.run.scan_sources", return_value=[MagicMock()]), \
             patch("scripts.run.classify_sources", return_value=[fi]), \
             patch("scripts.run.build_label_map", return_value={}), \
             patch("scripts.run.verify_file", return_value=[]), \
             patch("scripts.run.check_source_links", return_value=[]), \
             patch("scripts.run.verify_docs_md", return_value=[]), \
             patch("scripts.run.check_json_docs_md_consistency", return_value=[]), \
             patch("scripts.create.scan._source_roots", return_value=[]):
            result = verify(
                version="6",
                repo_root=_REPO_ROOT,
                output_dir=output_dir,
                files=["dummy/source.rst"],
            )
        assert result is True


# ---------------------------------------------------------------------------
# V-skip: verify() FAIL on missing docs MD
# ---------------------------------------------------------------------------

class TestVerifyMissingDocsMd:
    """verify() must FAIL when docs MD is missing for non-no_knowledge_content files."""

    def _run_verify(self, tmp_path, fi, json_data: dict):
        from scripts.run import verify
        output_dir = tmp_path / "knowledge"
        output_dir.mkdir()
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        # Write JSON file
        json_path = output_dir / fi.output_path
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(json_data), encoding="utf-8")
        # Do NOT create docs MD

        with patch("scripts.run.scan_sources", return_value=[MagicMock()]), \
             patch("scripts.run.classify_sources", return_value=[fi]), \
             patch("scripts.run.build_label_map", return_value={}), \
             patch("scripts.run.verify_file", return_value=[]), \
             patch("scripts.run.check_source_links", return_value=[]), \
             patch("scripts.create.scan._source_roots", return_value=[]):
            return verify(
                version="6",
                repo_root=_REPO_ROOT,
                output_dir=output_dir,
                files=["dummy/source.rst"],
            )

    def test_fail_when_docs_md_missing_for_knowledge_file(self, tmp_path):
        """verify returns False when docs MD is missing for a non-NKC file."""
        fi = _make_file_info()
        json_data = {
            "id": "test-file", "title": "Title", "no_knowledge_content": False,
            "sections": [{"id": "s1", "title": "概要", "content": "Content.", "hints": []}],
        }
        result = self._run_verify(tmp_path, fi, json_data)
        assert result is False

    def test_pass_when_docs_md_missing_for_no_knowledge_content(self, tmp_path):
        """verify returns True when docs MD is absent but no_knowledge_content=True."""
        fi = _make_file_info()
        json_data = {
            "id": "test-file", "title": "Title", "no_knowledge_content": True,
            "sections": [],
        }
        result = self._run_verify(tmp_path, fi, json_data)
        assert result is True


# ---------------------------------------------------------------------------
# Phase 21-D: hints file array-form loading and section lookup
# ---------------------------------------------------------------------------

class TestLoadHintsFileArrayForm:
    """load_hints_file returns dict[file_id, list[entry]] for array-form hints files."""

    def test_returns_array_form_untouched(self, tmp_path):
        from scripts.run import load_hints_file
        hints_dir = tmp_path / "tools/rbkc/hints"
        hints_dir.mkdir(parents=True)
        (hints_dir / "v6.json").write_text(json.dumps({
            "version": "6",
            "hints": {
                "file-a": [
                    {"title": "概要", "hints": ["h1"]},
                    {"title": "使用方法", "hints": ["h2"]},
                ],
            },
        }), encoding="utf-8")
        result = load_hints_file(tmp_path, "6")
        assert result == {
            "file-a": [
                {"title": "概要", "hints": ["h1"]},
                {"title": "使用方法", "hints": ["h2"]},
            ],
        }

    def test_returns_empty_when_file_missing(self, tmp_path):
        from scripts.run import load_hints_file
        assert load_hints_file(tmp_path, "6") == {}


class TestPopHintsForTitle:
    """_pop_hints_for_title consumes hint entries positionally by matching title at head."""

    def test_pops_head_when_title_matches(self):
        from scripts.run import _pop_hints_for_title
        pending = [
            {"title": "概要", "hints": ["h1"]},
            {"title": "使用方法", "hints": ["h2"]},
        ]
        hints = _pop_hints_for_title(pending, "概要")
        assert hints == ["h1"]
        # Remaining entries untouched
        assert pending == [{"title": "使用方法", "hints": ["h2"]}]

    def test_same_title_twice_consumed_in_order(self):
        """Same title appearing twice must pop first then second entry (positional)."""
        from scripts.run import _pop_hints_for_title
        pending = [
            {"title": "使用方法", "hints": ["first"]},
            {"title": "使用方法", "hints": ["second"]},
        ]
        assert _pop_hints_for_title(pending, "使用方法") == ["first"]
        assert _pop_hints_for_title(pending, "使用方法") == ["second"]
        assert pending == []

    def test_returns_empty_when_head_title_mismatch(self):
        """If the head entry title does not match, return [] and leave pending untouched.

        Positional alignment must not be broken by silent skipping; a mismatch
        indicates a source-vs-hints-file drift that should surface as missing hints.
        """
        from scripts.run import _pop_hints_for_title
        pending = [{"title": "概要", "hints": ["h1"]}]
        hints = _pop_hints_for_title(pending, "別タイトル")
        assert hints == []
        assert pending == [{"title": "概要", "hints": ["h1"]}]

    def test_returns_empty_when_pending_empty(self):
        from scripts.run import _pop_hints_for_title
        pending: list = []
        assert _pop_hints_for_title(pending, "any") == []

    def test_file_sentinel_head_does_not_match_section_title(self):
        """A "__file__" head entry must not be consumed as a section by _pop_hints_for_title.

        The sentinel is reserved for top-level matching.  If it appears at the
        head while the current section title differs, it must stay in pending
        so that the subsequent top-level-only flow can surface the drift (or
        a later orphaned entry is reported as "not matched").
        """
        from scripts.run import _pop_hints_for_title
        pending = [
            {"title": "__file__", "hints": ["file-kw"]},
            {"title": "Sec1", "hints": ["s1-k"]},
        ]
        # No consumption — the section iteration must not mistake "__file__" for a section
        assert _pop_hints_for_title(pending, "Sec1") == []
        assert len(pending) == 2


class TestPopTopLevelHints:
    """_pop_top_level_hints pops head when it is the file-level hint entry.

    Head is file-level when its title equals JSON top-level title OR is the
    "__file__" sentinel (xlsx: JSON title is "").  Any other head is left
    untouched so sections[] can positionally consume it.
    """

    def test_returns_empty_when_pending_empty(self):
        from scripts.run import _pop_top_level_hints
        pending: list = []
        assert _pop_top_level_hints(pending, "any") == []

    def test_pops_when_head_title_matches_top_title(self):
        from scripts.run import _pop_top_level_hints
        pending = [{"title": "T", "hints": ["k"]}, {"title": "Sec", "hints": ["sk"]}]
        assert _pop_top_level_hints(pending, "T") == ["k"]
        assert pending == [{"title": "Sec", "hints": ["sk"]}]

    def test_pops_when_head_title_is_file_sentinel_regardless_of_top_title(self):
        from scripts.run import _pop_top_level_hints
        pending = [{"title": "__file__", "hints": ["k"]}, {"title": "Sec", "hints": ["sk"]}]
        # top_title is empty (xlsx) — sentinel still matches
        assert _pop_top_level_hints(pending, "") == ["k"]
        assert pending == [{"title": "Sec", "hints": ["sk"]}]

    def test_pops_when_head_is_sentinel_even_if_top_title_nonempty(self):
        from scripts.run import _pop_top_level_hints
        pending = [{"title": "__file__", "hints": ["k"]}]
        assert _pop_top_level_hints(pending, "SomeTitle") == ["k"]
        assert pending == []

    def test_does_not_pop_when_head_differs_from_top_and_is_not_sentinel(self):
        from scripts.run import _pop_top_level_hints
        pending = [{"title": "Sec", "hints": ["sk"]}]
        assert _pop_top_level_hints(pending, "TopTitle") == []
        assert pending == [{"title": "Sec", "hints": ["sk"]}]


class TestNormalizeKcToArray:
    """_normalize_kc_to_array converts KC-cache dict form to array form."""

    def test_converts_dict_to_array_preserving_title_order(self):
        from scripts.run import _normalize_kc_to_array
        kc = {
            "file-a": {
                "概要": ["h1"],
                "使用方法": ["h2"],
            },
        }
        result = _normalize_kc_to_array(kc)
        assert result == {
            "file-a": [
                {"title": "概要", "hints": ["h1"]},
                {"title": "使用方法", "hints": ["h2"]},
            ],
        }

    def test_empty_input_returns_empty(self):
        from scripts.run import _normalize_kc_to_array
        assert _normalize_kc_to_array({}) == {}


# ---------------------------------------------------------------------------
# Phase 21-D (session 37): top-level hints injection
# ---------------------------------------------------------------------------

class TestConvertAndWriteTopLevelHints:
    """_convert_and_write injects top-level hints from hints-file head entry.

    If the hints array's head entry's title matches the top-level JSON title,
    it is popped and stored as the JSON ``hints`` field.  Otherwise ``hints: []``.
    The remaining array is then consumed positionally by sections[].
    """

    def _make_converter_result(self, title: str, content: str, sections_spec: list[tuple[str, str]]):
        from scripts.create.converters.rst import RSTResult, Section
        return RSTResult(
            title=title,
            no_knowledge_content=False,
            content=content,
            sections=[Section(title=t, content=c) for t, c in sections_spec],
        )

    def _write_source(self, tmp_path: Path) -> Path:
        src = tmp_path / "src.rst"
        src.write_text("dummy", encoding="utf-8")
        return src

    def test_head_title_matches_top_title_pops_into_top_level_hints(self, tmp_path):
        """Head entry's title == top-level title → popped into top-level `hints`."""
        from scripts.run import _convert_and_write

        src = self._write_source(tmp_path)
        fi = MagicMock()
        fi.format = "rst"
        fi.file_id = "file-a"
        fi.output_path = "x.json"
        fi.source_path = src

        result = self._make_converter_result(
            title="File Title",
            content="preamble",
            sections_spec=[("Sec1", "c1"), ("Sec2", "c2")],
        )
        hints_idx = {
            "file-a": [
                {"title": "File Title", "hints": ["file-keyword"]},
                {"title": "Sec1", "hints": ["s1-k"]},
                {"title": "Sec2", "hints": ["s2-k"]},
            ],
        }

        output_dir = tmp_path / "out"
        with patch("scripts.run._converter_for", return_value=lambda *a, **kw: result):
            _convert_and_write(fi, output_dir, hints_idx, existing_hints=None, label_map={})

        data = json.loads((output_dir / "x.json").read_text(encoding="utf-8"))
        assert data["hints"] == ["file-keyword"]
        assert [s["hints"] for s in data["sections"]] == [["s1-k"], ["s2-k"]]

    def test_head_title_differs_from_top_title_leaves_top_hints_empty(self, tmp_path):
        """Head entry's title != top-level title → top-level `hints` is [] and head is preserved for sections."""
        from scripts.run import _convert_and_write

        src = self._write_source(tmp_path)
        fi = MagicMock()
        fi.format = "rst"
        fi.file_id = "file-a"
        fi.output_path = "x.json"
        fi.source_path = src

        result = self._make_converter_result(
            title="File Title",
            content="preamble",
            sections_spec=[("Sec1", "c1")],
        )
        hints_idx = {
            "file-a": [
                {"title": "Sec1", "hints": ["s1-k"]},
            ],
        }

        output_dir = tmp_path / "out"
        with patch("scripts.run._converter_for", return_value=lambda *a, **kw: result):
            _convert_and_write(fi, output_dir, hints_idx, existing_hints=None, label_map={})

        data = json.loads((output_dir / "x.json").read_text(encoding="utf-8"))
        assert data["hints"] == []
        assert data["sections"][0]["hints"] == ["s1-k"]

    def test_no_entries_gives_empty_hints_everywhere(self, tmp_path):
        from scripts.run import _convert_and_write

        src = self._write_source(tmp_path)
        fi = MagicMock()
        fi.format = "rst"
        fi.file_id = "file-a"
        fi.output_path = "x.json"
        fi.source_path = src

        result = self._make_converter_result(
            title="T",
            content="c",
            sections_spec=[("S", "sc")],
        )

        output_dir = tmp_path / "out"
        with patch("scripts.run._converter_for", return_value=lambda *a, **kw: result):
            _convert_and_write(fi, output_dir, {}, existing_hints=None, label_map={})

        data = json.loads((output_dir / "x.json").read_text(encoding="utf-8"))
        assert data["hints"] == []
        assert data["sections"][0]["hints"] == []

    def test_index_has_file_entry_first_when_top_hints_non_empty(self, tmp_path):
        """When top-level hints non-empty, index[0] = {id:"__file__", title, hints}."""
        from scripts.run import _convert_and_write

        src = self._write_source(tmp_path)
        fi = MagicMock()
        fi.format = "rst"
        fi.file_id = "file-a"
        fi.output_path = "x.json"
        fi.source_path = src

        result = self._make_converter_result(
            title="File Title",
            content="preamble",
            sections_spec=[("Sec1", "c1"), ("Sec2", "c2")],
        )
        hints_idx = {
            "file-a": [
                {"title": "File Title", "hints": ["file-kw"]},
                {"title": "Sec1", "hints": ["s1-k"]},
                {"title": "Sec2", "hints": []},
            ],
        }

        output_dir = tmp_path / "out"
        with patch("scripts.run._converter_for", return_value=lambda *a, **kw: result):
            _convert_and_write(fi, output_dir, hints_idx, existing_hints=None, label_map={})

        data = json.loads((output_dir / "x.json").read_text(encoding="utf-8"))
        assert data["index"] == [
            {"id": "__file__", "title": "File Title", "hints": ["file-kw"]},
            {"id": "s1", "title": "Sec1", "hints": ["s1-k"]},
            {"id": "s2", "title": "Sec2", "hints": []},
        ]

    def test_index_has_no_file_entry_when_top_hints_empty(self, tmp_path):
        """When top-level hints empty, index[] contains only section entries (no __file__)."""
        from scripts.run import _convert_and_write

        src = self._write_source(tmp_path)
        fi = MagicMock()
        fi.format = "rst"
        fi.file_id = "file-a"
        fi.output_path = "x.json"
        fi.source_path = src

        result = self._make_converter_result(
            title="File Title",
            content="",
            sections_spec=[("Sec1", "c1")],
        )
        hints_idx = {
            "file-a": [{"title": "Sec1", "hints": ["s1-k"]}],
        }

        output_dir = tmp_path / "out"
        with patch("scripts.run._converter_for", return_value=lambda *a, **kw: result):
            _convert_and_write(fi, output_dir, hints_idx, existing_hints=None, label_map={})

        data = json.loads((output_dir / "x.json").read_text(encoding="utf-8"))
        assert data["index"] == [{"id": "s1", "title": "Sec1", "hints": ["s1-k"]}]

    def test_fallback_hints_used_when_primary_missing(self, tmp_path):
        """Existing-hints fallback also supplies top-level hints when primary is empty."""
        from scripts.run import _convert_and_write

        src = self._write_source(tmp_path)
        fi = MagicMock()
        fi.format = "rst"
        fi.file_id = "file-a"
        fi.output_path = "x.json"
        fi.source_path = src

        result = self._make_converter_result(
            title="T",
            content="c",
            sections_spec=[("S", "sc")],
        )
        existing = {
            "file-a": [
                {"title": "T", "hints": ["carried"]},
                {"title": "S", "hints": ["sec-carried"]},
            ],
        }

        output_dir = tmp_path / "out"
        with patch("scripts.run._converter_for", return_value=lambda *a, **kw: result):
            _convert_and_write(fi, output_dir, hints_idx={}, existing_hints=existing, label_map={})

        data = json.loads((output_dir / "x.json").read_text(encoding="utf-8"))
        assert data["hints"] == ["carried"]
        assert data["sections"][0]["hints"] == ["sec-carried"]

    def test_file_sentinel_head_pops_into_top_level_hints(self, tmp_path):
        """Head entry's title == "__file__" sentinel → popped into top-level `hints`.

        xlsx sources have ``title = ""`` because the source has no h1.  The
        hints file stores file-level xlsx hints under a ``"__file__"`` sentinel
        title (Phase 21-H design §4-4 / schema design §3-4).  The converter
        must recognize this sentinel and treat it as the file-level entry,
        independent of JSON top-level title value.
        """
        from scripts.run import _convert_and_write

        src = self._write_source(tmp_path)
        fi = MagicMock()
        fi.format = "xlsx"
        fi.file_id = "security-check"
        fi.output_path = "security-check.json"
        fi.source_path = src

        result = self._make_converter_result(
            title="",
            content="xlsx rows flattened",
            sections_spec=[],
        )
        hints_idx = {
            "security-check": [
                {"title": "__file__", "hints": ["セキュリティ", "CVE"]},
            ],
        }

        output_dir = tmp_path / "out"
        with patch("scripts.run._converter_for", return_value=lambda *a, **kw: result):
            _convert_and_write(fi, output_dir, hints_idx, existing_hints=None, label_map={})

        data = json.loads((output_dir / "security-check.json").read_text(encoding="utf-8"))
        assert data["hints"] == ["セキュリティ", "CVE"]
        assert data["sections"] == []
        assert data["index"] == [
            {"id": "__file__", "title": "", "hints": ["セキュリティ", "CVE"]},
        ]

    def test_file_sentinel_beats_title_mismatch(self, tmp_path):
        """__file__ sentinel matches regardless of actual JSON title value.

        Even when the JSON top-level title is non-empty, a head entry titled
        "__file__" still represents the file-level hint entry.
        """
        from scripts.run import _convert_and_write

        src = self._write_source(tmp_path)
        fi = MagicMock()
        fi.format = "xlsx"
        fi.file_id = "rn"
        fi.output_path = "rn.json"
        fi.source_path = src

        result = self._make_converter_result(
            title="Some Derived Title",
            content="body",
            sections_spec=[],
        )
        hints_idx = {
            "rn": [
                {"title": "__file__", "hints": ["k1"]},
            ],
        }

        output_dir = tmp_path / "out"
        with patch("scripts.run._converter_for", return_value=lambda *a, **kw: result):
            _convert_and_write(fi, output_dir, hints_idx, existing_hints=None, label_map={})

        data = json.loads((output_dir / "rn.json").read_text(encoding="utf-8"))
        assert data["hints"] == ["k1"]
