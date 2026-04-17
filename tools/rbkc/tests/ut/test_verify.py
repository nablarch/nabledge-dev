"""Unit tests for verify.py — QO5, QC5, QC6, QC1-QC3(Excel), QC1-QC4(RST/MD), QO3, QL2, QL1."""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# QO5: docs MD content 完全一致
# ---------------------------------------------------------------------------

class TestCheckJsonDocsMdConsistency:
    """QO5: JSON sections content must appear verbatim in docs MD."""

    def _check(self, data, docs_md_text):
        from scripts.verify import check_json_docs_md_consistency
        return check_json_docs_md_consistency(data, docs_md_text)

    def _make_data(self, sections):
        return {
            "id": "test-file",
            "title": "テストタイトル",
            "no_knowledge_content": False,
            "sections": sections,
        }

    # --- PASS cases ---

    def test_pass_content_present_in_docs_md(self):
        """Content verbatim in docs MD → no issues."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "概要の説明文です。", "hints": []},
        ])
        docs_md = "# テストタイトル\n\n## 概要\n\n概要の説明文です。\n"
        assert self._check(data, docs_md) == []

    def test_pass_multiple_sections_all_present(self):
        """All sections present in docs MD → no issues."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "概要の内容。", "hints": []},
            {"id": "s2", "title": "設定方法", "content": "設定の内容。", "hints": []},
        ])
        docs_md = "# テストタイトル\n\n## 概要\n\n概要の内容。\n\n## 設定方法\n\n設定の内容。\n"
        assert self._check(data, docs_md) == []

    def test_pass_empty_content_section(self):
        """Empty content section → no issues (nothing to check)."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "", "hints": []},
        ])
        docs_md = "# テストタイトル\n\n## 概要\n\n"
        assert self._check(data, docs_md) == []

    def test_pass_no_knowledge_content_skipped(self):
        """no_knowledge_content=True files are not checked."""
        data = {
            "id": "test-file",
            "title": "テスト",
            "no_knowledge_content": True,
            "sections": [],
        }
        docs_md = "# テスト\n"
        assert self._check(data, docs_md) == []

    # --- FAIL cases ---

    def test_fail_content_missing_from_docs_md(self):
        """Content not in docs MD → FAIL (QO5)."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "重要な説明が欠落しています。", "hints": []},
        ])
        docs_md = "# テストタイトル\n\n## 概要\n\n全く別の内容。\n"
        issues = self._check(data, docs_md)
        assert len(issues) == 1
        assert "QO5" in issues[0]
        assert "概要" in issues[0]

    def test_fail_content_partially_missing(self):
        """Only part of content present → FAIL (QO5)."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "前半の内容。後半が欠落。", "hints": []},
        ])
        docs_md = "# テストタイトル\n\n## 概要\n\n前半の内容。\n"
        issues = self._check(data, docs_md)
        assert len(issues) == 1
        assert "QO5" in issues[0]

    def test_fail_multiple_sections_one_missing(self):
        """One of multiple sections missing → FAIL for that section only."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "概要の内容。", "hints": []},
            {"id": "s2", "title": "設定方法", "content": "欠落している設定内容。", "hints": []},
        ])
        docs_md = "# テストタイトル\n\n## 概要\n\n概要の内容。\n\n## 設定方法\n\n別の内容。\n"
        issues = self._check(data, docs_md)
        assert len(issues) == 1
        assert "設定方法" in issues[0]

    def test_fail_includes_section_title_in_message(self):
        """FAIL message identifies the section with missing content."""
        data = self._make_data([
            {"id": "s1", "title": "処理概要", "content": "欠落コンテンツ。", "hints": []},
        ])
        docs_md = "# テストタイトル\n\n## 処理概要\n\n\n"
        issues = self._check(data, docs_md)
        assert any("処理概要" in i for i in issues)

    def test_pass_section_with_assets_link_skipped(self):
        """Sections with assets/ links are skipped (docs MD rewrites paths → verbatim match impossible)."""
        data = self._make_data([
            {
                "id": "s1",
                "title": "図解",
                "content": "説明\n![図](assets/my-file/diagram.png)",
                "hints": [],
            },
        ])
        # docs MD would have rewritten link — but we skip this section entirely
        docs_md = "# テストタイトル\n\n## 図解\n\n説明\n![図](../../knowledge/assets/my-file/diagram.png)\n"
        assert self._check(data, docs_md) == []


# ---------------------------------------------------------------------------
# QC5: 形式純粋性
# ---------------------------------------------------------------------------

class TestCheckFormatPurity:
    """QC5: Format-specific syntax must not remain in JSON content/title."""

    def _check(self, data, fmt):
        from scripts.verify import check_format_purity
        return check_format_purity(data, fmt)

    def _make_data(self, sections, title="テスト"):
        return {
            "id": "test",
            "title": title,
            "no_knowledge_content": False,
            "sections": sections,
        }

    # --- RST PASS cases ---

    def test_rst_pass_clean_content(self):
        """RST: no format-specific syntax → no issues."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "クリーンな内容です。", "hints": []},
        ])
        assert self._check(data, "rst") == []

    def test_rst_pass_plain_backtick_code(self):
        """RST: plain backtick inline code (Markdown style) is allowed."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "`MyClass` を使います。", "hints": []},
        ])
        assert self._check(data, "rst") == []

    # --- RST FAIL cases ---

    def test_rst_fail_role_syntax(self):
        """RST: :role:`text` pattern → FAIL (QC5)."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": ":java:class:`MyClass` を使います。", "hints": []},
        ])
        issues = self._check(data, "rst")
        assert len(issues) >= 1
        assert "QC5" in issues[0]

    def test_rst_fail_directive_syntax(self):
        """RST: .. directive:: pattern → FAIL (QC5)."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": ".. code-block:: java\n\nコード", "hints": []},
        ])
        issues = self._check(data, "rst")
        assert len(issues) >= 1
        assert "QC5" in issues[0]

    def test_rst_fail_heading_underline_in_title(self):
        """RST: heading underline in file title → FAIL (QC5)."""
        data = {
            "id": "test",
            "title": "見出し\n======",
            "no_knowledge_content": False,
            "sections": [],
        }
        issues = self._check(data, "rst")
        assert len(issues) >= 1
        assert "QC5" in issues[0]

    def test_rst_fail_heading_underline_in_section_title(self):
        """RST: heading underline in section title → FAIL (QC5)."""
        data = self._make_data([
            {"id": "s1", "title": "見出し\n======", "content": "内容", "hints": []},
        ])
        issues = self._check(data, "rst")
        assert len(issues) >= 1
        assert "QC5" in issues[0]

    def test_rst_pass_heading_underline_in_content(self):
        """RST: heading underline in content (code example) → PASS (not checked in content)."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "コード例:\n\n    ====\n\n内容", "hints": []},
        ])
        # Heading underline check is NOT applied to content fields
        assert self._check(data, "rst") == []

    def test_rst_fail_label_definition(self):
        """RST: _label: label definition → FAIL (QC5)."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": ".. _my-label:\n\n内容", "hints": []},
        ])
        issues = self._check(data, "rst")
        assert len(issues) >= 1
        assert "QC5" in issues[0]

    def test_rst_fail_title_contaminated(self):
        """RST: :role: in title → FAIL (QC5)."""
        data = self._make_data(
            [{"id": "s1", "title": "概要", "content": "内容", "hints": []}],
            title=":java:class:`Title`"
        )
        issues = self._check(data, "rst")
        assert len(issues) >= 1

    # --- MD PASS cases ---

    def test_md_pass_clean_content(self):
        """MD: no format-specific syntax → no issues."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "クリーンな内容。", "hints": []},
        ])
        assert self._check(data, "md") == []

    def test_md_pass_code_fence(self):
        """MD: code fences (```) are allowed in MD content."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "```java\ncode\n```", "hints": []},
        ])
        assert self._check(data, "md") == []

    # --- MD FAIL cases ---

    def test_md_fail_raw_html_tag(self):
        """MD: raw HTML tag → FAIL (QC5)."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "<details>\n<summary>詳細</summary>\n</details>", "hints": []},
        ])
        issues = self._check(data, "md")
        assert len(issues) >= 1
        assert "QC5" in issues[0]

    def test_md_fail_backslash_escape(self):
        """MD: backslash escape \\* → FAIL (QC5)."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "\\*エスケープされたテキスト\\*", "hints": []},
        ])
        issues = self._check(data, "md")
        assert len(issues) >= 1
        assert "QC5" in issues[0]

    def test_md_fail_br_tag(self):
        """MD: <br> HTML tag → FAIL (QC5)."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "行1<br>行2", "hints": []},
        ])
        issues = self._check(data, "md")
        assert len(issues) >= 1
        assert "QC5" in issues[0]

    def test_md_pass_java_generic_type(self):
        """MD: Java generic type like List<String> → PASS (not raw HTML)."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "List<String> と Map<K, V> を使います。", "hints": []},
        ])
        assert self._check(data, "md") == []

    def test_md_pass_java_generic_uppercase_single(self):
        """MD: single uppercase type param like List<T> → PASS (not raw HTML)."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "List<T> を実装します。", "hints": []},
        ])
        assert self._check(data, "md") == []

    # --- Excel: no QC5 check ---

    def test_excel_skipped(self):
        """Excel format: QC5 is not applicable → no issues."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "内容", "hints": []},
        ])
        assert self._check(data, "xlsx") == []


# ---------------------------------------------------------------------------
# QC6: hints 完全性
# ---------------------------------------------------------------------------

class TestCheckHintsCompleteness:
    """QC6: Hints from previous run must all be present in current output."""

    def _check(self, data, prev_hints):
        from scripts.verify import check_hints_completeness
        return check_hints_completeness(data, prev_hints)

    def _make_data(self, file_id, sections):
        return {
            "id": file_id,
            "title": "テスト",
            "no_knowledge_content": False,
            "sections": sections,
        }

    # --- PASS cases ---

    def test_pass_all_hints_present(self):
        """All previous hints present in current output → no issues."""
        data = self._make_data("my-file", [
            {"id": "s1", "title": "概要", "content": "内容", "hints": ["HintA", "HintB"]},
        ])
        prev_hints = {"my-file": {"概要": ["HintA", "HintB"]}}
        assert self._check(data, prev_hints) == []

    def test_pass_additional_hints_allowed(self):
        """Current output has more hints than previous → no issues (additions OK)."""
        data = self._make_data("my-file", [
            {"id": "s1", "title": "概要", "content": "内容", "hints": ["HintA", "HintB", "HintC"]},
        ])
        prev_hints = {"my-file": {"概要": ["HintA", "HintB"]}}
        assert self._check(data, prev_hints) == []

    def test_pass_no_previous_hints_for_file(self):
        """File not in prev_hints → no issues (first run)."""
        data = self._make_data("new-file", [
            {"id": "s1", "title": "概要", "content": "内容", "hints": []},
        ])
        prev_hints = {}
        assert self._check(data, prev_hints) == []

    def test_pass_no_previous_hints_for_section(self):
        """Section not in prev_hints[file_id] → no issues."""
        data = self._make_data("my-file", [
            {"id": "s1", "title": "新セクション", "content": "内容", "hints": []},
        ])
        prev_hints = {"my-file": {}}
        assert self._check(data, prev_hints) == []

    # --- FAIL cases ---

    def test_fail_hint_missing_from_current(self):
        """Previous hint missing from current output → FAIL (QC6)."""
        data = self._make_data("my-file", [
            {"id": "s1", "title": "概要", "content": "内容", "hints": ["HintA"]},
        ])
        prev_hints = {"my-file": {"概要": ["HintA", "HintB"]}}
        issues = self._check(data, prev_hints)
        assert len(issues) == 1
        assert "QC6" in issues[0]
        assert "HintB" in issues[0]

    def test_fail_all_hints_missing(self):
        """All previous hints missing from current section → FAIL for each."""
        data = self._make_data("my-file", [
            {"id": "s1", "title": "概要", "content": "内容", "hints": []},
        ])
        prev_hints = {"my-file": {"概要": ["HintA", "HintB"]}}
        issues = self._check(data, prev_hints)
        assert len(issues) >= 1
        assert all("QC6" in i for i in issues)

    def test_fail_identifies_section_and_hint(self):
        """FAIL message includes section title and missing hint name."""
        data = self._make_data("my-file", [
            {"id": "s1", "title": "処理詳細", "content": "内容", "hints": []},
        ])
        prev_hints = {"my-file": {"処理詳細": ["ImportantHint"]}}
        issues = self._check(data, prev_hints)
        assert any("処理詳細" in i for i in issues)
        assert any("ImportantHint" in i for i in issues)

    def test_fail_multiple_sections_partial_miss(self):
        """Missing hint in one section only → FAIL for that section."""
        data = self._make_data("my-file", [
            {"id": "s1", "title": "概要", "content": "内容", "hints": ["HintA"]},
            {"id": "s2", "title": "詳細", "content": "内容", "hints": []},
        ])
        prev_hints = {"my-file": {"概要": ["HintA"], "詳細": ["HintX"]}}
        issues = self._check(data, prev_hints)
        assert len(issues) == 1
        assert "詳細" in issues[0]
