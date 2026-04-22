"""Tests for scripts/common/rst_include.py — Phase 21-X.

Spec (rbkc-verify-quality-design.md §3-1):
  - expand_includes(source_path, max_depth=8) — splice `.. include:: path` recursively
  - resolve_literalinclude(path, start_after=None, end_before=None, lines=None) -> str
  - Cycle detection → IncludeCycleError
  - Depth-limit exceeded → IncludeDepthError
"""
from __future__ import annotations

from pathlib import Path

import pytest


class TestExpandIncludes:
    def _expand(self, path, **kw):
        from scripts.common.rst_include import expand_includes
        return expand_includes(path, **kw)

    def test_no_includes(self, tmp_path):
        src = tmp_path / "a.rst"
        src.write_text("title\n=====\nBody\n", encoding="utf-8")
        assert self._expand(src) == "title\n=====\nBody\n"

    def test_single_include_relative(self, tmp_path):
        (tmp_path / "inner.rst").write_text("inner content\n", encoding="utf-8")
        main = tmp_path / "main.rst"
        main.write_text("before\n.. include:: inner.rst\nafter\n", encoding="utf-8")
        result = self._expand(main)
        assert "before" in result
        assert "inner content" in result
        assert "after" in result
        assert ".. include::" not in result

    def test_nested_includes(self, tmp_path):
        (tmp_path / "c.rst").write_text("C-text\n", encoding="utf-8")
        (tmp_path / "b.rst").write_text(".. include:: c.rst\n", encoding="utf-8")
        (tmp_path / "a.rst").write_text("A\n.. include:: b.rst\n", encoding="utf-8")
        assert "C-text" in self._expand(tmp_path / "a.rst")
        assert "A" in self._expand(tmp_path / "a.rst")

    def test_cycle_detection(self, tmp_path):
        from scripts.common.rst_include import IncludeCycleError
        (tmp_path / "a.rst").write_text(".. include:: b.rst\n", encoding="utf-8")
        (tmp_path / "b.rst").write_text(".. include:: a.rst\n", encoding="utf-8")
        with pytest.raises(IncludeCycleError):
            self._expand(tmp_path / "a.rst")

    def test_depth_limit_exceeded(self, tmp_path):
        from scripts.common.rst_include import IncludeDepthError
        # Create a chain of 10 files each including the next
        for i in range(10):
            nxt = f"f{i+1}.rst"
            (tmp_path / f"f{i}.rst").write_text(
                f".. include:: {nxt}\n" if i < 9 else "leaf\n",
                encoding="utf-8",
            )
        with pytest.raises(IncludeDepthError):
            self._expand(tmp_path / "f0.rst", max_depth=3)

    def test_missing_file_raises(self, tmp_path):
        src = tmp_path / "main.rst"
        src.write_text(".. include:: nonexistent.rst\n", encoding="utf-8")
        with pytest.raises(FileNotFoundError):
            self._expand(src)

    def test_relative_path_to_sibling_dir(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "inner.rst").write_text("inner body\n", encoding="utf-8")
        main = tmp_path / "main.rst"
        main.write_text(".. include:: sub/inner.rst\n", encoding="utf-8")
        assert "inner body" in self._expand(main)

    def test_preserves_non_include_directives(self, tmp_path):
        main = tmp_path / "main.rst"
        main.write_text(
            ".. note::\n   a note\n\n.. include::\n   (not a real include — malformed)\n",
            encoding="utf-8",
        )
        # Malformed include with empty path should pass through as-is so the
        # caller (tokenizer) can flag it as unknown syntax.
        result = self._expand(main)
        assert ".. note::" in result


class TestLiteralInclude:
    def test_full_file(self, tmp_path):
        from scripts.common.rst_include import resolve_literalinclude
        target = tmp_path / "sample.java"
        target.write_text("L1\nL2\nL3\nL4\n", encoding="utf-8")
        assert resolve_literalinclude(target) == "L1\nL2\nL3\nL4\n"

    def test_start_after_end_before(self, tmp_path):
        from scripts.common.rst_include import resolve_literalinclude
        target = tmp_path / "s.java"
        target.write_text(
            "// preamble\n// START\nKEEP1\nKEEP2\n// END\n// trailing\n",
            encoding="utf-8",
        )
        out = resolve_literalinclude(target, start_after="// START", end_before="// END")
        assert out.strip() == "KEEP1\nKEEP2"

    def test_lines_range(self, tmp_path):
        from scripts.common.rst_include import resolve_literalinclude
        target = tmp_path / "s.java"
        target.write_text("1\n2\n3\n4\n5\n", encoding="utf-8")
        out = resolve_literalinclude(target, lines="2-4")
        assert out.splitlines() == ["2", "3", "4"]

    def test_lines_single(self, tmp_path):
        from scripts.common.rst_include import resolve_literalinclude
        target = tmp_path / "s.java"
        target.write_text("1\n2\n3\n", encoding="utf-8")
        out = resolve_literalinclude(target, lines="2")
        assert out.splitlines() == ["2"]
