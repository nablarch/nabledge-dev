"""Unit tests for verify.py — QO2, QC5, QC6, QC1-QC3(Excel), QC1-QC4(RST/MD), QL2, QL1."""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# QO2: docs MD content 完全一致
# ---------------------------------------------------------------------------

class TestCheckJsonDocsMdConsistency:
    """QO2: JSON sections content must appear verbatim in docs MD."""

    def _check(self, data, docs_md_text):
        from scripts.verify.verify import check_json_docs_md_consistency
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
        assert "QO2" in issues[0]
        assert "概要" in issues[0]

    def test_fail_content_partially_missing(self):
        """Only part of content present → FAIL (QO5)."""
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "前半の内容。後半が欠落。", "hints": []},
        ])
        docs_md = "# テストタイトル\n\n## 概要\n\n前半の内容。\n"
        issues = self._check(data, docs_md)
        assert len(issues) == 1
        assert "QO2" in issues[0]

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
        from scripts.verify.verify import check_format_purity
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
        from scripts.verify.verify import check_hints_completeness
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


# ---------------------------------------------------------------------------
# QC1-QC3: RST/MD コンテンツ完全性・正確性・非重複性 (delete algorithm)
# ---------------------------------------------------------------------------

class TestVerifyFileContentRstMd:
    """QC1/QC2/QC3: RST/MD content verified via sequential-delete algorithm.

    Test setups use empty top-level title/content to isolate section-level
    behavior. Top-level field coverage is exercised in
    ``TestCheckContentCompletenessTopLevel``.
    """

    def _check(self, source_text, data, fmt):
        from scripts.verify.verify import check_content_completeness
        return check_content_completeness(source_text, data, fmt)

    def _make_data(self, file_id, sections):
        return {
            "id": file_id,
            "title": "",
            "content": "",
            "no_knowledge_content": False,
            "sections": sections,
        }

    # --- PASS cases ---

    def test_pass_single_section_content_present(self):
        """All section content appears in source → no issues."""
        source = "概要\n====\n\n概要の説明文です。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "概要の説明文です。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_multiple_sections_all_present(self):
        """All sections present in correct order → no issues."""
        source = "概要\n====\n\n概要の内容。\n\n設定方法\n========\n\n設定の内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "概要の内容。", "hints": []},
            {"id": "s2", "title": "設定方法", "content": "設定の内容。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_no_knowledge_content_skipped(self):
        """no_knowledge_content=True → skip check entirely."""
        source = "目次\n====\n\n.. toctree::\n\n   chapter1\n"
        data = {
            "id": "f",
            "title": "目次",
            "no_knowledge_content": True,
            "sections": [],
        }
        assert self._check(source, data, "rst") == []

    def test_pass_empty_sections_list(self):
        """No sections → nothing to verify → no issues."""
        source = "概要\n====\n\n内容。\n"
        data = self._make_data("f", [])
        assert self._check(source, data, "rst") == []

    def test_pass_whitespace_normalization(self):
        """Source with extra blank lines matches normalized JSON content → no issues."""
        source = "概要\n====\n\n行1\n\n行2\n"
        data = self._make_data("f", [
            # JSON content has single blank line normalized
            {"id": "s1", "title": "概要", "content": "行1\n\n行2", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_md_format(self):
        """MD source content present in JSON → no issues."""
        source = "# タイトル\n\n## 概要\n\nMarkdown の説明です。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "Markdown の説明です。", "hints": []},
        ])
        assert self._check(source, data, "md") == []

    def test_pass_syntax_only_remaining(self):
        """After deletion, only RST syntax markers remain → no QC1 issues."""
        source = "概要\n====\n\n内容テキスト。\n\n.. code-block:: java\n\n  code\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "内容テキスト。\n\n```java\n  code\n```", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    # --- QC1 FAIL: content missing from JSON ---

    def test_fail_qc1_content_missing(self):
        """Source has text not in any JSON section → FAIL QC1."""
        source = "概要\n====\n\n重要な説明があります。追加情報も存在します。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "重要な説明があります。", "hints": []},
            # "追加情報も存在します。" is not captured
        ])
        issues = self._check(source, data, "rst")
        assert len(issues) >= 1
        assert any("QC1" in i for i in issues)

    def test_fail_qc1_section_entirely_missing(self):
        """Entire section content absent from JSON → FAIL QC1."""
        source = "概要\n====\n\n概要内容。\n\n詳細\n====\n\n詳細内容が欠落。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "概要内容。", "hints": []},
            # 詳細 section missing entirely
        ])
        issues = self._check(source, data, "rst")
        assert any("QC1" in i for i in issues)

    # --- QC2 FAIL: fabricated content in JSON ---

    def test_fail_qc2_fabricated_content(self):
        """JSON has content not in source → FAIL QC2."""
        source = "概要\n====\n\n実際の内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "実際の内容。\n捏造された追加情報。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        assert any("QC2" in i for i in issues)

    def test_fail_qc2_completely_different_content(self):
        """JSON content entirely absent from source → FAIL QC2."""
        source = "概要\n====\n\n本物の内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "全く別の内容。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        assert any("QC2" in i for i in issues)

    # --- QC3 FAIL: duplicate content in JSON ---

    def test_fail_qc3_duplicate_section_content(self):
        """Same content appears in two JSON sections → second one FAIL QC3."""
        source = "概要\n====\n\n共有テキスト内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "共有テキスト内容。", "hints": []},
            {"id": "s2", "title": "別セクション", "content": "共有テキスト内容。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        assert any("QC3" in i for i in issues)

    # --- Edge cases ---

    def test_pass_title_is_not_checked_as_content(self):
        """Section titles should not be separately counted as missing content."""
        source = "概要\n====\n\n内容テキスト。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "内容テキスト。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_bold_stripped(self):
        """**text** in JSON content is stripped to 'text' before source matching."""
        source = "概要\n====\n\nキーワードが重要です。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "**キーワード**が重要です。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_single_emphasis_stripped(self):
        """*text* in JSON content is stripped to 'text' before source matching."""
        source = "概要\n====\n\nキーワードが重要です。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "*キーワード*が重要です。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_admonition_label_stripped(self):
        """'> **Note:** text' → label stripped; body 'text' searched in source (MD)."""
        source = "# 概要\n\nメモの内容です。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "> **Note:** メモの内容です。", "hints": []},
        ])
        assert self._check(source, data, "md") == []

    def test_pass_toctree_entries_not_qc1(self):
        """Indented toctree child entries in RST source → treated as syntax, not QC1."""
        source = "目次\n====\n\n通常テキスト。\n\n.. toctree::\n\n   chapter1\n   chapter2\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "目次", "content": "通常テキスト。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_substitution_def_not_qc1(self):
        """RST substitution definitions '.. |name| replace:: ...' → syntax, not QC1."""
        source = "概要\n====\n\n内容テキスト。\n\n.. |NB| replace:: Nablarch\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "内容テキスト。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_md_frontmatter_body_not_qc1(self):
        """Frontmatter body lines (between '---') in MD source → syntax, not QC1."""
        source = "---\ntitle: テスト\ndate: 2026-01-01\n---\n\n# 概要\n\n内容テキスト。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "内容テキスト。", "hints": []},
        ])
        assert self._check(source, data, "md") == []

    def test_fail_qc2_fabricated_title(self):
        """JSON section title absent from source → QC2 (fabricated) with title in message."""
        source = "概要\n====\n\n内容テキスト。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "存在しないタイトル", "content": "内容テキスト。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        qc2_issues = [i for i in issues if "QC2" in i]
        assert len(qc2_issues) >= 1
        assert any("存在しないタイトル" in i for i in qc2_issues)

    def test_fail_qc1_multiple_gaps(self):
        """Multiple uncaptured source lines → all reported (no early break)."""
        source = "概要\n====\n\n欠落行1\n欠落行2\n欠落行3\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        qc1_issues = [i for i in issues if "QC1" in i]
        assert len(qc1_issues) >= 2, f"Expected >=2 QC1 issues, got: {qc1_issues}"

    def test_pass_snake_case_not_mangled(self):
        """snake_case identifiers in JSON content are not mangled by underscore stripping."""
        source = "概要\n====\n\ndo_something_else を使用します。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "do_something_else を使用します。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_directive_body_captured_not_swallowed(self):
        """RST directive body content (note:: body) is real content, must be captured."""
        source = "概要\n====\n\n.. note::\n\n   重要な注記内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "重要な注記内容。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_admonition_japanese_label_stripped(self):
        """'> **注意:** text' → Japanese admonition label stripped before source match (MD)."""
        source = "# 概要\n\nメモの内容です。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "> **注意:** メモの内容です。", "hints": []},
        ])
        assert self._check(source, data, "md") == []

    def test_pass_admonition_lowercase_label_stripped(self):
        """'> **note:** text' → lowercase admonition label stripped before source match (MD)."""
        source = "# 概要\n\nメモの内容です。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "> **note:** メモの内容です。", "hints": []},
        ])
        assert self._check(source, data, "md") == []

    def test_pass_md_hr_not_frontmatter(self):
        """MD horizontal rule '---' in body is not mistaken for frontmatter boundary."""
        source = "# 概要\n\n最初の内容。\n\n---\n\n区切り後の内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "最初の内容。\n\n---\n\n区切り後の内容。", "hints": []},
        ])
        assert self._check(source, data, "md") == []

    def test_fail_qc1_md_content_after_hr_not_captured(self):
        """If content after HR is not in JSON, QC1 is reported (HR does not swallow it)."""
        source = "# 概要\n\n最初の内容。\n\n---\n\n欠落した内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "最初の内容。", "hints": []},
        ])
        issues = self._check(source, data, "md")
        assert any("QC1" in i for i in issues)


# ---------------------------------------------------------------------------
# QC4: 配置正確性 (multi-section)
# ---------------------------------------------------------------------------

class TestVerifyFileContentQC4:
    """QC4: Content from source section A must not appear in a different JSON section."""

    def _check(self, source_text, data, fmt):
        from scripts.verify.verify import check_content_completeness
        return check_content_completeness(source_text, data, fmt)

    def _make_data(self, file_id, sections):
        return {
            "id": file_id,
            "title": "",
            "content": "",
            "no_knowledge_content": False,
            "sections": sections,
        }

    # --- PASS cases ---

    def test_pass_two_sections_correct_order(self):
        """Two sections in correct source order → no issues."""
        source = "概要\n====\n\n概要内容。\n\n詳細\n====\n\n詳細内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "概要内容。", "hints": []},
            {"id": "s2", "title": "詳細", "content": "詳細内容。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_three_sections_correct_order(self):
        """Three sections in correct source order → no issues."""
        source = "A\n====\n\nA内容。\n\nB\n====\n\nB内容。\n\nC\n====\n\nC内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "A", "content": "A内容。", "hints": []},
            {"id": "s2", "title": "B", "content": "B内容。", "hints": []},
            {"id": "s3", "title": "C", "content": "C内容。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_md_two_sections_correct_order(self):
        """MD: two sections in correct order → no issues."""
        source = "# タイトル\n\n## 概要\n\n概要内容。\n\n## 詳細\n\n詳細内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "概要内容。", "hints": []},
            {"id": "s2", "title": "詳細", "content": "詳細内容。", "hints": []},
        ])
        assert self._check(source, data, "md") == []

    # --- QC4 FAIL cases ---

    def test_fail_qc4_content_appears_before_previous_section(self):
        """JSON section 2 content found before section 1 in source → FAIL QC4."""
        # Source order: 詳細 → 概要
        # JSON order:   概要 → 詳細  (reversed)
        source = "詳細\n====\n\n詳細内容。\n\n概要\n====\n\n概要内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "概要内容。", "hints": []},
            {"id": "s2", "title": "詳細", "content": "詳細内容。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        assert any("QC4" in i for i in issues)

    def test_fail_qc4_section_title_reversed(self):
        """JSON section title found before previous section title → FAIL QC4."""
        source = "B\n====\n\nB内容。\n\nA\n====\n\nA内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "A", "content": "A内容。", "hints": []},
            {"id": "s2", "title": "B", "content": "B内容。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        assert any("QC4" in i for i in issues)

    def test_fail_qc4_md_content_reversed(self):
        """MD: JSON section order reversed vs source → FAIL QC4."""
        source = "# タイトル\n\n## 詳細\n\n詳細内容。\n\n## 概要\n\n概要内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "概要内容。", "hints": []},
            {"id": "s2", "title": "詳細", "content": "詳細内容。", "hints": []},
        ])
        issues = self._check(source, data, "md")
        assert any("QC4" in i for i in issues)

    def test_fail_qc4_identifies_section_in_message(self):
        """QC4 FAIL message identifies which section (by ID) has misplaced content."""
        source = "詳細\n====\n\n詳細内容。\n\n概要\n====\n\n概要内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "概要内容。", "hints": []},
            {"id": "s2", "title": "詳細", "content": "詳細内容。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        qc4_issues = [i for i in issues if "QC4" in i]
        assert len(qc4_issues) >= 1
        # section ID 's2' must appear in at least one QC4 message (not just unit text)
        assert any("'s2'" in i for i in qc4_issues)

    def test_fail_qc4_title_and_content_both_reported(self):
        """Both the misplaced section title and its content lines each fire QC4."""
        source = "詳細\n====\n\n詳細内容。\n\n概要\n====\n\n概要内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "概要内容。", "hints": []},
            {"id": "s2", "title": "詳細", "content": "詳細内容。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        qc4_issues = [i for i in issues if "QC4" in i]
        assert len(qc4_issues) >= 2

    def test_fail_qc4_three_sections_middle_misplaced(self):
        """Three sections (A, B, C in source), JSON has A, C, B → C and B are QC4."""
        # Source: A → B → C
        # JSON:   A → C → B  (C and B are out of order)
        source = "A\n====\n\nA内容。\n\nB\n====\n\nB内容。\n\nC\n====\n\nC内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "A", "content": "A内容。", "hints": []},
            {"id": "s3", "title": "C", "content": "C内容。", "hints": []},
            {"id": "s2", "title": "B", "content": "B内容。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        qc4_issues = [i for i in issues if "QC4" in i]
        assert len(qc4_issues) >= 1
        # B (section s2) should be reported as misplaced
        assert any("'s2'" in i for i in qc4_issues)

    # --- Distinguish QC3 vs QC4 ---

    def test_qc3_not_qc4_for_duplicate_consumed(self):
        """Content that was already consumed (duplicate) → QC3, not QC4."""
        source = "概要\n====\n\n共有テキスト。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "共有テキスト。", "hints": []},
            {"id": "s2", "title": "別セクション", "content": "共有テキスト。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        assert any("QC3" in i for i in issues)
        assert not any("QC4" in i for i in issues)

    def test_qc4_not_qc3_for_reversed_unique_content(self):
        """Content reversed in source order (not duplicate) → QC4, not QC3."""
        source = "B\n====\n\nBのみの内容。\n\nA\n====\n\nAのみの内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "A", "content": "Aのみの内容。", "hints": []},
            {"id": "s2", "title": "B", "content": "Bのみの内容。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        qc3 = [i for i in issues if "QC3" in i]
        qc4 = [i for i in issues if "QC4" in i]
        assert len(qc4) >= 1
        assert len(qc3) == 0

    def test_qc3_not_qc4_for_substring_in_consumed(self):
        """Content that is a substring of already-consumed text → QC3, not QC4."""
        # Source has "AB内容。"; s1 consumes it; s2 claims "B内容。" (substring)
        # prev_idx of "B内容。" falls inside the consumed range → QC3
        source = "概要\n====\n\nAB内容。\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "AB内容。", "hints": []},
            {"id": "s2", "title": "別セクション", "content": "B内容。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        assert any("QC3" in i for i in issues)
        assert not any("QC4" in i for i in issues)

    def test_pass_title_only_section_no_qc4_when_correct_order(self):
        """Sections with no content (title only): correct order → no QC4."""
        source = "概要\n====\n\n詳細\n====\n\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "", "hints": []},
            {"id": "s2", "title": "詳細", "content": "", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        qc4 = [i for i in issues if "QC4" in i]
        assert len(qc4) == 0

    def test_fail_qc4_title_only_sections_reversed(self):
        """Sections with no content, reversed title order → QC4 on misplaced title."""
        # Source: 詳細 → 概要; JSON: 概要 → 詳細 (reversed)
        source = "詳細\n====\n\n概要\n====\n\n"
        data = self._make_data("f", [
            {"id": "s1", "title": "概要", "content": "", "hints": []},
            {"id": "s2", "title": "詳細", "content": "", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        qc4 = [i for i in issues if "QC4" in i]
        assert len(qc4) >= 1
        assert any("'s2'" in i for i in qc4)


# ---------------------------------------------------------------------------
# QL2: 外部URL一致
# ---------------------------------------------------------------------------

class TestCheckExternalUrls:
    """QL2: External URLs in source must appear in JSON content/title."""

    def _check(self, source_text, data, fmt):
        from scripts.verify.verify import check_external_urls
        return check_external_urls(source_text, data, fmt)

    def _make_data(self, sections, title="テスト"):
        return {
            "id": "test-file",
            "title": title,
            "no_knowledge_content": False,
            "sections": sections,
        }

    # --- PASS cases ---

    def test_pass_rst_url_in_content(self):
        """RST: URL in source appears in JSON content → no issues."""
        source = "概要\n====\n\n詳細は `公式サイト <https://nablarch.github.io/docs/>`_ を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "詳細は [公式サイト](https://nablarch.github.io/docs/) を参照。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_md_url_in_content(self):
        """MD: URL in source appears in JSON content → no issues."""
        source = "## 概要\n\n詳細は [公式サイト](https://nablarch.github.io/docs/) を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "詳細は [公式サイト](https://nablarch.github.io/docs/) を参照。", "hints": []},
        ])
        assert self._check(source, data, "md") == []

    def test_pass_no_urls_in_source(self):
        """Source has no external URLs → no issues."""
        source = "概要\n====\n\n内部の説明文です。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "内部の説明文です。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_no_knowledge_content_skipped(self):
        """no_knowledge_content=True → skip QL2 entirely."""
        source = "https://example.com の情報です。\n"
        data = {
            "id": "test-file",
            "title": "テスト",
            "no_knowledge_content": True,
            "sections": [],
        }
        assert self._check(source, data, "rst") == []

    def test_pass_url_in_rst_hyperlink_target(self):
        """RST: URL from hyperlink target definition appears in JSON → no issues."""
        source = "概要\n====\n\n詳細は ExternalSite_ を参照。\n\n.. _ExternalSite: https://example.com/docs\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "詳細は [ExternalSite](https://example.com/docs) を参照。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_multiple_urls_all_present(self):
        """Multiple URLs in source, all in JSON → no issues."""
        source = (
            "概要\n====\n\n"
            "`サイトA <https://example.com/a>`_ と `サイトB <https://example.com/b>`_ を参照。\n"
        )
        data = self._make_data([
            {
                "id": "s1",
                "title": "概要",
                "content": "[サイトA](https://example.com/a) と [サイトB](https://example.com/b) を参照。",
                "hints": [],
            },
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_url_with_query_and_fragment(self):
        """URL with query params and fragment: all characters preserved in match."""
        source = "概要\n====\n\n`参照 <https://example.com/path?q=1#section>`_ を確認。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "[参照](https://example.com/path?q=1#section) を確認。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    # --- FAIL cases ---

    def test_fail_ql2_url_missing_from_json(self):
        """Source URL not in any JSON field → FAIL QL2."""
        source = "概要\n====\n\n`公式サイト <https://nablarch.github.io/docs/>`_ を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "公式サイトを参照。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        assert len(issues) == 1
        assert "QL2" in issues[0]
        assert "https://nablarch.github.io/docs/" in issues[0]

    def test_fail_ql2_multiple_urls_one_missing(self):
        """One of multiple source URLs missing from JSON → FAIL for that URL only."""
        source = (
            "概要\n====\n\n"
            "`サイトA <https://example.com/a>`_ と `サイトB <https://example.com/b>`_ を参照。\n"
        )
        data = self._make_data([
            {
                "id": "s1",
                "title": "概要",
                "content": "[サイトA](https://example.com/a) とサイトBを参照。",
                "hints": [],
            },
        ])
        issues = self._check(source, data, "rst")
        ql2_issues = [i for i in issues if "QL2" in i]
        assert len(ql2_issues) == 1
        assert "https://example.com/b" in ql2_issues[0]

    def test_fail_ql2_all_urls_missing(self):
        """All source URLs missing from JSON → FAIL for each."""
        source = (
            "概要\n====\n\n"
            "`サイトA <https://example.com/a>`_ と `サイトB <https://example.com/b>`_ を参照。\n"
        )
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "サイトAとサイトBを参照。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        ql2_issues = [i for i in issues if "QL2" in i]
        assert len(ql2_issues) == 2

    def test_fail_ql2_url_truncated_in_json(self):
        """URL in JSON is truncated (not complete match) → FAIL QL2."""
        source = "概要\n====\n\n`参照 <https://example.com/full/path>`_ を確認。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "[参照](https://example.com/full) を確認。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        ql2_issues = [i for i in issues if "QL2" in i]
        assert len(ql2_issues) >= 1
        assert "https://example.com/full/path" in ql2_issues[0]

    def test_fail_ql2_md_url_missing(self):
        """MD source URL missing from JSON → FAIL QL2."""
        source = "## 概要\n\n[公式サイト](https://nablarch.github.io/docs/) を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "公式サイトを参照。", "hints": []},
        ])
        issues = self._check(source, data, "md")
        ql2_issues = [i for i in issues if "QL2" in i]
        assert len(ql2_issues) == 1
        assert "https://nablarch.github.io/docs/" in ql2_issues[0]

    def test_fail_ql2_identifies_url_in_message(self):
        """FAIL message contains the missing URL."""
        source = "概要\n====\n\n`サイト <https://example.com/specific/path>`_ を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "サイトを参照。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        assert any("https://example.com/specific/path" in i for i in issues)

    # --- Edge cases: RST target definition lines ---

    def test_pass_rst_unreferenced_named_target_no_false_positive(self):
        """RST unreferenced named target URL not in JSON → PASS (target def line excluded)."""
        source = "概要\n====\n\n内部の説明文です。\n\n.. _Unused: https://example.com/unreferenced\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "内部の説明文です。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_rst_anonymous_target_no_false_positive(self):
        """RST anonymous target (`__ url`) URL not in JSON → PASS (target def line excluded)."""
        source = "概要\n====\n\n詳細は `こちら`__ を参照。\n\n__ https://example.com/anon\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "詳細はこちらを参照。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    # --- Edge cases: trailing punctuation ---

    def test_pass_url_with_trailing_period_in_source(self):
        """Bare URL followed by sentence period: period must not be part of extracted URL."""
        source = "概要\n====\n\n詳細は https://example.com/path. を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "詳細は https://example.com/path を参照。", "hints": []},
        ])
        assert self._check(source, data, "rst") == []

    def test_pass_url_with_trailing_comma_in_source(self):
        """Bare URL followed by comma: comma must not be part of extracted URL."""
        source = "概要\n====\n\nhttps://example.com/a, https://example.com/b を参照。\n"
        data = self._make_data([
            {
                "id": "s1",
                "title": "概要",
                "content": "https://example.com/a, https://example.com/b を参照。",
                "hints": [],
            },
        ])
        assert self._check(source, data, "rst") == []

    # --- Edge cases: exact URL matching (set comparison) ---

    def test_fail_ql2_url_with_extra_suffix_in_json(self):
        """Source URL is prefix of JSON URL → FAIL QL2 (substring match would pass incorrectly)."""
        source = "概要\n====\n\n`サイト <https://example.com/path>`_ を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "[サイト](https://example.com/path-extended) を参照。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        ql2_issues = [i for i in issues if "QL2" in i]
        assert len(ql2_issues) == 1
        assert "https://example.com/path" in ql2_issues[0]

    # --- Edge cases: deduplication ---

    def test_pass_duplicate_url_in_source_missing_from_json_reported_once(self):
        """Duplicate URLs in source: missing URL reported only once."""
        source = (
            "概要\n====\n\n"
            "`リンク1 <https://example.com/page>`_ と `リンク2 <https://example.com/page>`_ を参照。\n"
        )
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "リンク1とリンク2を参照。", "hints": []},
        ])
        ql2_issues = [i for i in self._check(source, data, "rst") if "QL2" in i]
        assert len(ql2_issues) == 1

    # --- Edge cases: xlsx skip, HTTP URL ---

    def test_xlsx_format_skipped(self):
        """xlsx format: check skipped regardless of URL presence."""
        source = "https://example.com/should-be-ignored\n"
        data = self._make_data([{"id": "s1", "title": "概要", "content": "何もなし。", "hints": []}])
        assert self._check(source, data, "xlsx") == []

    def test_fail_ql2_http_url_missing(self):
        """HTTP (non-HTTPS) URL missing from JSON → FAIL QL2."""
        source = "概要\n====\n\n`旧サイト <http://example.com/old>`_ を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "旧サイトを参照。", "hints": []},
        ])
        issues = self._check(source, data, "rst")
        assert any("QL2" in i and "http://example.com/old" in i for i in issues)


# ---------------------------------------------------------------------------
# QL1: 内部リンクの正確性
# ---------------------------------------------------------------------------

class TestBuildLabelMap:
    """build_label_map: RST label → section title mapping."""

    def _build(self, rst_text: str, filename: str = "test.rst") -> dict:
        from scripts.verify.verify import build_label_map
        import tempfile, os
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(rst_text)
            from pathlib import Path
            return build_label_map(Path(tmpdir))

    def test_single_label_with_heading(self):
        """Label immediately followed by heading → mapped to that title."""
        rst = ".. _my-label:\n\nMy Section\n==========\n"
        result = self._build(rst)
        assert result.get("my-label") == "My Section"

    def test_multiple_labels_same_file(self):
        """Multiple labels in one file are all mapped."""
        rst = (
            ".. _label-a:\n\nSection A\n=========\n\n"
            ".. _label-b:\n\nSection B\n---------\n"
        )
        result = self._build(rst)
        assert result.get("label-a") == "Section A"
        assert result.get("label-b") == "Section B"

    def test_label_without_following_heading_not_mapped(self):
        """Label not followed by a heading is ignored."""
        rst = ".. _orphan-label:\n\nThis is just a paragraph.\n"
        result = self._build(rst)
        assert "orphan-label" not in result

    def test_multiple_rst_files_combined(self):
        """Labels from multiple .rst files are merged into one map."""
        from scripts.verify.verify import build_label_map
        import tempfile, os
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            for name, label, title in [
                ("a.rst", "label-a", "Section A"),
                ("b.rst", "label-b", "Section B"),
            ]:
                with open(os.path.join(tmpdir, name), "w", encoding="utf-8") as f:
                    f.write(f".. _{label}:\n\n{title}\n{'='*len(title)}\n")
            result = build_label_map(Path(tmpdir))
        assert result.get("label-a") == "Section A"
        assert result.get("label-b") == "Section B"

    def test_nonrst_files_ignored(self):
        """Non-.rst files in the directory are ignored."""
        from scripts.verify.verify import build_label_map
        import tempfile, os
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "notes.txt"), "w") as f:
                f.write(".. _should-not-appear:\n\nHeading\n=======\n")
            result = build_label_map(Path(tmpdir))
        assert result == {}

    def test_stacked_labels_all_mapped(self):
        """Two consecutive labels before one heading → both labels mapped to same title."""
        rst = ".. _alias-old:\n.. _alias-new:\n\nShared Section\n==============\n"
        result = self._build(rst)
        assert result.get("alias-old") == "Shared Section"
        assert result.get("alias-new") == "Shared Section"

    def test_nested_subdirectory_labels_included(self):
        """Labels in .rst files inside subdirectories are found recursively."""
        from scripts.verify.verify import build_label_map
        import tempfile, os
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "sub")
            os.makedirs(subdir)
            with open(os.path.join(subdir, "deep.rst"), "w", encoding="utf-8") as f:
                f.write(".. _deep-label:\n\nDeep Section\n============\n")
            result = build_label_map(Path(tmpdir))
        assert result.get("deep-label") == "Deep Section"

    def test_label_directly_adjacent_to_heading_no_blank_line(self):
        """Label immediately before heading with no blank line: heading is still mapped."""
        rst = ".. _no-blank:\nSection Title\n=============\n"
        result = self._build(rst)
        assert result.get("no-blank") == "Section Title"

    def test_overline_style_heading(self):
        """Label before overline-style heading (====\\ntitle\\n====) → mapped to title."""
        rst = ".. _overline-label:\n\n==============\nOverline Title\n==============\n"
        result = self._build(rst)
        assert result.get("overline-label") == "Overline Title"

    def test_stacked_labels_overline_style(self):
        """Two labels before overline-style heading → both mapped to title."""
        rst = ".. _old:\n.. _new:\n\n==============\nOverline Title\n==============\n"
        result = self._build(rst)
        assert result.get("old") == "Overline Title"
        assert result.get("new") == "Overline Title"


class TestCheckSourceLinks:
    """check_source_links: QL1 verification of internal links."""

    def _check(self, source_text: str, fmt: str, data: dict,
               label_map: dict | None = None, source_path=None) -> list[str]:
        from scripts.verify.verify import check_source_links
        return check_source_links(source_text, fmt, data, label_map or {}, source_path)

    def _make_data(self, sections, title="テスト") -> dict:
        return {
            "id": "test-file",
            "title": title,
            "no_knowledge_content": False,
            "sections": sections,
        }

    # --- RST :ref: ---

    def test_pass_rst_ref_label_title_in_json(self):
        """:ref:`label` where label maps to a title that appears in JSON → PASS."""
        source = "概要\n====\n\n詳細は :ref:`my-label` を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "詳細はMy Sectionを参照。", "hints": []},
        ])
        label_map = {"my-label": "My Section"}
        assert self._check(source, "rst", data, label_map) == []

    def test_fail_rst_ref_label_title_missing_from_json(self):
        """:ref:`label` where label title is absent from JSON → FAIL QL1."""
        source = "概要\n====\n\n詳細は :ref:`my-label` を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "詳細を参照。", "hints": []},
        ])
        label_map = {"my-label": "My Section"}
        issues = self._check(source, "rst", data, label_map)
        assert any("QL1" in i and "my-label" in i for i in issues)

    def test_pass_rst_ref_display_text_form(self):
        """:ref:`display text <label>` — display text appears in JSON → PASS."""
        source = "概要\n====\n\n:ref:`こちら <my-label>` を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "こちらを参照。", "hints": []},
        ])
        label_map = {"my-label": "My Section"}
        assert self._check(source, "rst", data, label_map) == []

    def test_fail_rst_ref_display_text_missing_from_json(self):
        """:ref:`display text <label>` — display text absent from JSON → FAIL QL1."""
        source = "概要\n====\n\n:ref:`こちら <my-label>` を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "参照してください。", "hints": []},
        ])
        label_map = {"my-label": "My Section"}
        issues = self._check(source, "rst", data, label_map)
        assert any("QL1" in i for i in issues)

    def test_pass_rst_ref_unknown_label_skipped(self):
        """:ref:`unknown-label` not in label_map → skip (cannot verify)."""
        source = "概要\n====\n\n詳細は :ref:`unknown-label` を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "詳細を参照。", "hints": []},
        ])
        assert self._check(source, "rst", data, {}) == []

    def test_fail_rst_ref_two_refs_on_same_line_one_missing(self):
        """Two :ref: on same line; one title absent from JSON → FAIL QL1 only for missing."""
        source = "概要\n====\n\n:ref:`label-a` と :ref:`label-b` を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "Section A を参照。", "hints": []},
        ])
        label_map = {"label-a": "Section A", "label-b": "Section B"}
        issues = self._check(source, "rst", data, label_map)
        assert any("QL1" in i and "label-b" in i for i in issues)
        assert not any("label-a" in i for i in issues)

    def test_pass_rst_ref_same_label_repeated_reported_once(self):
        """Same :ref:`label` appears twice; reported at most once even if title missing."""
        source = "概要\n====\n\n:ref:`my-label` と :ref:`my-label` を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "他の説明。", "hints": []},
        ])
        label_map = {"my-label": "My Section"}
        issues = [i for i in self._check(source, "rst", data, label_map) if "my-label" in i]
        assert len(issues) == 1

    # --- RST figure ---

    def test_pass_rst_figure_caption_in_json(self):
        """figure directive with caption that appears in JSON → PASS."""
        source = (
            "概要\n====\n\n"
            ".. figure:: _images/diagram.png\n\n"
            "   システム構成図\n"
        )
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "システム構成図", "hints": []},
        ])
        assert self._check(source, "rst", data) == []

    def test_fail_rst_figure_caption_missing_from_json(self):
        """figure directive with caption absent from JSON → FAIL QL1."""
        source = (
            "概要\n====\n\n"
            ".. figure:: _images/diagram.png\n\n"
            "   システム構成図\n"
        )
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "概要説明のみ。", "hints": []},
        ])
        issues = self._check(source, "rst", data)
        assert any("QL1" in i and "figure" in i for i in issues)

    def test_pass_rst_figure_no_caption_filename_in_json(self):
        """figure without caption: filename appears in JSON → PASS."""
        source = (
            "概要\n====\n\n"
            ".. figure:: _images/diagram.png\n\n"
            "   :align: center\n"
        )
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "diagram.png の説明。", "hints": []},
        ])
        assert self._check(source, "rst", data) == []

    def test_fail_rst_figure_no_caption_filename_missing(self):
        """figure without caption and filename not in JSON → FAIL QL1."""
        source = (
            "概要\n====\n\n"
            ".. figure:: _images/diagram.png\n\n"
            "   :align: center\n"
        )
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "図の説明のみ。", "hints": []},
        ])
        issues = self._check(source, "rst", data)
        assert any("QL1" in i and "figure" in i for i in issues)

    def test_fail_rst_figure_options_only_filename_missing(self):
        """figure with only option lines and filename not in JSON → FAIL QL1."""
        source = (
            "概要\n====\n\n"
            ".. figure:: _images/diagram.png\n\n"
            "   :align: center\n"
            "   :width: 100%\n"
        )
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "図の説明のみ。", "hints": []},
        ])
        issues = self._check(source, "rst", data)
        assert any("QL1" in i and "figure" in i for i in issues)

    # --- RST image ---

    def test_pass_rst_image_alt_in_json(self):
        """image directive with alt text that appears in JSON → PASS."""
        source = (
            "概要\n====\n\n"
            ".. image:: _images/logo.png\n"
            "   :alt: ロゴ画像\n"
        )
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "ロゴ画像の説明。", "hints": []},
        ])
        assert self._check(source, "rst", data) == []

    def test_fail_rst_image_alt_missing_from_json(self):
        """image directive with alt text absent from JSON → FAIL QL1."""
        source = (
            "概要\n====\n\n"
            ".. image:: _images/logo.png\n"
            "   :alt: ロゴ画像\n"
        )
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "図の説明のみ。", "hints": []},
        ])
        issues = self._check(source, "rst", data)
        assert any("QL1" in i and "image" in i for i in issues)

    def test_pass_rst_image_no_alt_filename_in_json(self):
        """image without alt: filename appears in JSON → PASS."""
        source = (
            "概要\n====\n\n"
            ".. image:: _images/logo.png\n"
        )
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "logo.png の説明。", "hints": []},
        ])
        assert self._check(source, "rst", data) == []

    def test_fail_rst_image_no_alt_filename_missing_from_json(self):
        """image without alt and filename absent from JSON → FAIL QL1."""
        source = (
            "概要\n====\n\n"
            ".. image:: _images/logo.png\n"
        )
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "図の説明のみ。", "hints": []},
        ])
        issues = self._check(source, "rst", data)
        assert any("QL1" in i and "image" in i for i in issues)

    # --- RST literalinclude ---

    def test_pass_rst_literalinclude_placeholder_in_json(self):
        """literalinclude directive: placeholder text in JSON → PASS."""
        source = (
            "概要\n====\n\n"
            ".. literalinclude:: _code/example.java\n"
            "   :language: java\n"
        )
        data = self._make_data([
            {"id": "s1", "title": "概要",
             "content": "```java\n# (literalinclude: _code/example.java)\n```",
             "hints": []},
        ])
        assert self._check(source, "rst", data) == []

    def test_fail_rst_literalinclude_placeholder_missing_from_json(self):
        """literalinclude placeholder absent from JSON → FAIL QL1."""
        source = (
            "概要\n====\n\n"
            ".. literalinclude:: _code/example.java\n"
            "   :language: java\n"
        )
        data = self._make_data([
            {"id": "s1", "title": "概要", "content": "コードの説明のみ。", "hints": []},
        ])
        issues = self._check(source, "rst", data)
        assert any("QL1" in i and "literalinclude" in i for i in issues)

    # --- MD internal links ---

    def test_pass_md_internal_link_text_in_json(self):
        """MD [text](#anchor) — link text appears in JSON → PASS."""
        source = "# 概要\n\n## セクション\n\n詳細は [こちらを参照](#details) してください。\n"
        data = self._make_data([
            {"id": "s1", "title": "セクション",
             "content": "詳細はこちらを参照してください。", "hints": []},
        ])
        assert self._check(source, "md", data) == []

    def test_fail_md_internal_link_text_missing_from_json(self):
        """MD [text](#anchor) — link text absent from JSON → FAIL QL1."""
        source = "# 概要\n\n## セクション\n\n詳細は [こちらを参照](#details) してください。\n"
        data = self._make_data([
            {"id": "s1", "title": "セクション",
             "content": "詳細を参照。", "hints": []},
        ])
        issues = self._check(source, "md", data)
        assert any("QL1" in i for i in issues)

    def test_pass_md_external_link_not_checked_by_ql1(self):
        """MD [text](https://...) — external link skipped (covered by QL2)."""
        source = "# 概要\n\n## セクション\n\n詳細は [公式サイト](https://example.com) で確認。\n"
        data = self._make_data([
            {"id": "s1", "title": "セクション",
             "content": "詳細は公式サイトで確認。", "hints": []},
        ])
        assert self._check(source, "md", data) == []

    def test_pass_md_relative_path_link_text_in_json(self):
        """MD [text](../other.md) — relative path link text in JSON → PASS."""
        source = "# 概要\n\n## セクション\n\n詳細は [設定ガイド](../config.md) を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "セクション",
             "content": "詳細は設定ガイドを参照。", "hints": []},
        ])
        assert self._check(source, "md", data) == []

    def test_fail_md_relative_path_link_text_missing(self):
        """MD [text](../other.md) — relative path link text absent from JSON → FAIL QL1."""
        source = "# 概要\n\n## セクション\n\n詳細は [設定ガイド](../config.md) を参照。\n"
        data = self._make_data([
            {"id": "s1", "title": "セクション",
             "content": "詳細を参照。", "hints": []},
        ])
        issues = self._check(source, "md", data)
        assert any("QL1" in i for i in issues)

    # --- No-knowledge / xlsx skip ---

    def test_no_knowledge_content_skipped(self):
        """no_knowledge_content=True → skip all checks."""
        source = "概要\n====\n\n.. figure:: _images/x.png\n\n   キャプション\n"
        data = {
            "id": "test-file", "title": "テスト",
            "no_knowledge_content": True, "sections": [],
        }
        assert self._check(source, "rst", data) == []

    def test_xlsx_format_skipped(self):
        """xlsx format → skip all checks."""
        source = "Some text with internal links"
        data = self._make_data([{"id": "s1", "title": "概要", "content": "text", "hints": []}])
        assert self._check(source, "xlsx", data) == []

    # --- Top-level content coverage (Phase 21-I regression fix) ---

    def test_pass_rst_ref_title_in_top_level_content(self):
        """:ref: target title present in top-level content (preamble) → PASS.

        QL1 must search top-level data["content"] in addition to section content,
        because Phase 21-D preamble text (h1..first h2) is stored there.
        """
        source = "概要\n====\n\n詳細は :ref:`my-label` を参照。\n\nサブ\n---\n\n本文。\n"
        data = {
            "id": "test-file",
            "title": "概要",
            "no_knowledge_content": False,
            "content": "詳細はMy Sectionを参照。",
            "sections": [
                {"id": "s1", "title": "サブ", "content": "本文。", "hints": []},
            ],
        }
        label_map = {"my-label": "My Section"}
        assert self._check(source, "rst", data, label_map) == []

    def test_pass_rst_image_alt_in_top_level_content(self):
        """image alt present in top-level content (preamble) → PASS."""
        source = (
            "概要\n====\n\n"
            ".. image:: _images/mail_system.png\n"
            "   :alt: メールシステム構成\n"
            "\n"
            "サブ\n---\n\n本文。\n"
        )
        data = {
            "id": "test-file",
            "title": "概要",
            "no_knowledge_content": False,
            "content": "![メールシステム構成](assets/test/mail_system.png)",
            "sections": [
                {"id": "s1", "title": "サブ", "content": "本文。", "hints": []},
            ],
        }
        assert self._check(source, "rst", data) == []

    def test_pass_rst_image_filename_in_top_level_content(self):
        """image without alt — filename present in top-level content → PASS."""
        source = (
            "概要\n====\n\n"
            ".. image:: _images/framework.png\n"
            "\n"
            "サブ\n---\n\n本文。\n"
        )
        data = {
            "id": "test-file",
            "title": "概要",
            "no_knowledge_content": False,
            "content": "![](assets/test/framework.png)",
            "sections": [
                {"id": "s1", "title": "サブ", "content": "本文。", "hints": []},
            ],
        }
        assert self._check(source, "rst", data) == []

    def test_fail_rst_ref_missing_when_not_in_top_level_or_sections(self):
        """Negative test: ref title absent from BOTH top-level content and sections → FAIL.

        Guards against false negatives — confirms QL1 still fires when content is
        genuinely missing, not just that the fix's new code path silences it.
        """
        source = "概要\n====\n\n詳細は :ref:`my-label` を参照。\n\nサブ\n---\n\n本文。\n"
        data = {
            "id": "test-file",
            "title": "概要",
            "no_knowledge_content": False,
            "content": "関連なし。",
            "sections": [
                {"id": "s1", "title": "サブ", "content": "本文。", "hints": []},
            ],
        }
        label_map = {"my-label": "My Section"}
        issues = self._check(source, "rst", data, label_map)
        assert any("QL1" in i and "my-label" in i for i in issues)

    def test_pass_md_internal_link_text_in_top_level_content(self):
        """MD internal link text present in top-level content → PASS."""
        source = "# 概要\n\n詳しくは[別ページ](../other.md)を参照。\n\n## サブ\n\n本文。\n"
        data = {
            "id": "test-file",
            "title": "概要",
            "no_knowledge_content": False,
            "content": "詳しくは別ページを参照。",
            "sections": [
                {"id": "s1", "title": "サブ", "content": "本文。", "hints": []},
            ],
        }
        assert self._check(source, "md", data) == []


class TestJsonTextHelper:
    """Direct unit tests for _json_text() concat contract.

    Guards against silent regression of the concat logic itself, independent
    of higher-level QL1 code paths.
    """

    def _helper(self, data: dict) -> str:
        from scripts.verify.verify import _json_text
        return _json_text(data)

    def test_includes_title_and_top_level_content_and_sections(self):
        """_json_text() must concatenate title + top-level content + section titles + section content."""
        data = {
            "title": "T_TITLE",
            "content": "T_TOP_CONTENT",
            "sections": [
                {"title": "S1_TITLE", "content": "S1_CONTENT", "hints": []},
                {"title": "S2_TITLE", "content": "S2_CONTENT", "hints": []},
            ],
        }
        text = self._helper(data)
        assert "T_TITLE" in text
        assert "T_TOP_CONTENT" in text
        assert "S1_TITLE" in text
        assert "S1_CONTENT" in text
        assert "S2_TITLE" in text
        assert "S2_CONTENT" in text

    def test_excludes_hints(self):
        """Hints are out of QL1 scope (covered by QC6) — must not be in concat."""
        data = {
            "title": "T",
            "content": "TOP",
            "hints": ["TOP_HINT_SHOULD_NOT_APPEAR"],
            "sections": [
                {"title": "S", "content": "SC", "hints": ["SEC_HINT_SHOULD_NOT_APPEAR"]},
            ],
        }
        text = self._helper(data)
        assert "TOP_HINT_SHOULD_NOT_APPEAR" not in text
        assert "SEC_HINT_SHOULD_NOT_APPEAR" not in text

    def test_missing_top_level_content_key_safe(self):
        """data without "content" key — no KeyError, still includes other parts."""
        data = {
            "title": "T",
            "sections": [{"title": "S", "content": "SC", "hints": []}],
        }
        text = self._helper(data)
        assert "T" in text
        assert "S" in text
        assert "SC" in text

    def test_empty_top_level_content_safe(self):
        """Empty top-level content — still includes other parts, no error."""
        data = {
            "title": "T",
            "content": "",
            "sections": [{"title": "S", "content": "SC", "hints": []}],
        }
        text = self._helper(data)
        assert "T" in text
        assert "S" in text
        assert "SC" in text


# ---------------------------------------------------------------------------
# V2-4: Excel QC1/QC2/QC3 — sequential-delete via verify_file (placeholder)
# ---------------------------------------------------------------------------

class TestVerifyFileExcelQC:
    """verify_file for xlsx: QC1/QC2/QC3 via sequential-delete algorithm."""

    def _make_xlsx(self, tmpdir, rows: list[list]) -> "Path":
        """Create a minimal xlsx file with given rows in sheet1."""
        import openpyxl
        from pathlib import Path
        wb = openpyxl.Workbook()
        ws = wb.active
        for row in rows:
            ws.append(row)
        path = Path(tmpdir) / "test.xlsx"
        wb.save(str(path))
        return path

    def _make_json(self, tmpdir, data: dict) -> "Path":
        """Write JSON data to a temp file."""
        import json
        from pathlib import Path
        path = Path(tmpdir) / "test.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path

    def _check(self, xlsx_path, json_data: dict) -> list[str]:
        import json, tempfile
        from pathlib import Path
        from scripts.verify.verify import verify_file
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "test.json"
            json_path.write_text(json.dumps(json_data, ensure_ascii=False), encoding="utf-8")
            return verify_file(xlsx_path, json_path, "xlsx")

    def _make_data(self, sections, title="ファイルタイトル") -> dict:
        return {
            "id": "test-file",
            "title": title,
            "no_knowledge_content": False,
            "sections": sections,
        }

    # --- PASS cases ---

    def test_pass_all_cells_in_json(self, tmp_path):
        """All source cell values appear in JSON (title + section title + content) → no issues."""
        xlsx_path = self._make_xlsx(tmp_path, [["ファイルタイトル", "セルA", "セルB"], ["セルC", "セルD"]])
        data = self._make_data([
            {"id": "s1", "title": "セルA", "content": "セルB セルC セルD", "hints": []},
        ], title="ファイルタイトル")
        issues = self._check(xlsx_path, data)
        assert [i for i in issues if "QC" in i] == []

    def test_pass_empty_cells_ignored(self, tmp_path):
        """Empty/whitespace-only cells are not required in JSON."""
        xlsx_path = self._make_xlsx(tmp_path, [["値A", None, "  ", "値B"]])
        data = self._make_data([
            {"id": "s1", "title": "値B", "content": "", "hints": []},
        ], title="値A")
        assert [i for i in self._check(xlsx_path, data) if "QC" in i] == []

    def test_pass_no_knowledge_content_skipped(self, tmp_path):
        """no_knowledge_content=True → skip all QC checks."""
        xlsx_path = self._make_xlsx(tmp_path, [["セルA"]])
        data = {
            "id": "test-file", "title": "捏造タイトル",
            "no_knowledge_content": True, "sections": [],
        }
        assert self._check(xlsx_path, data) == []

    # --- FAIL QC1 ---

    def test_fail_qc1_cell_missing_from_json(self, tmp_path):
        """Source cell value absent from JSON → FAIL QC1."""
        xlsx_path = self._make_xlsx(tmp_path, [["存在するセル", "欠落セル"]])
        data = self._make_data([
            {"id": "s1", "title": "存在するセル", "content": "存在するセル", "hints": []},
        ], title="存在するセル")
        issues = self._check(xlsx_path, data)
        assert any("QC1" in i and "欠落セル" in i for i in issues)

    def test_fail_qc1_multiple_missing_cells(self, tmp_path):
        """Multiple missing cells → multiple QC1 issues."""
        xlsx_path = self._make_xlsx(tmp_path, [["A"], ["B"], ["C"]])
        data = self._make_data([
            {"id": "s1", "title": "A", "content": "A", "hints": []},
        ], title="A")
        issues = [i for i in self._check(xlsx_path, data) if "QC1" in i]
        assert len(issues) >= 2

    # --- FAIL QC2 ---

    def test_fail_qc2_token_in_json_not_in_source(self, tmp_path):
        """JSON contains token absent from source → FAIL QC2."""
        xlsx_path = self._make_xlsx(tmp_path, [["本物のセル"]])
        data = self._make_data([
            {"id": "s1", "title": "本物のセル", "content": "本物のセル 捏造トークン", "hints": []},
        ], title="本物のセル")
        issues = self._check(xlsx_path, data)
        assert any("QC2" in i and "捏造トークン" in i for i in issues)

    # --- FAIL QC3 ---

    def test_fail_qc3_duplicate_token_in_json(self, tmp_path):
        """Cell appears once in source but twice in JSON → FAIL QC2 (residual after delete)."""
        xlsx_path = self._make_xlsx(tmp_path, [["唯一のセル"]])
        data = self._make_data([
            {"id": "s1", "title": "唯一のセル", "content": "唯一のセル 唯一のセル", "hints": []},
        ], title="唯一のセル")
        issues = self._check(xlsx_path, data)
        # Source has "唯一のセル" once; JSON has it 3 times (title + section title + content×2).
        # After deleting source tokens from JSON, residual "唯一のセル" occurrences → QC2.
        assert any(("QC2" in i or "QC3" in i) and "唯一のセル" in i for i in issues)

    def test_pass_cell_value_with_spaces(self, tmp_path):
        """Cell value is matched as a whole string, not split by word."""
        xlsx_path = self._make_xlsx(tmp_path, [["テスト"], ["システム開発ガイド"], ["セキュリティ対応表"]])
        data = self._make_data([
            {"id": "s1", "title": "システム開発ガイド", "content": "セキュリティ対応表", "hints": []},
        ], title="テスト")
        issues = self._check(xlsx_path, data)
        assert [i for i in issues if "QC" in i] == []

    def test_fail_qc1_cell_value_partial_not_accepted(self, tmp_path):
        """Cell value must appear in full — partial word match is not enough."""
        xlsx_path = self._make_xlsx(tmp_path, [["システム開発ガイド"]])
        data = self._make_data([
            {"id": "s1", "title": "テスト", "content": "システム開発", "hints": []},
        ], title="テスト")
        issues = self._check(xlsx_path, data)
        assert any("QC1" in i and "システム開発ガイド" in i for i in issues)

    def test_fail_qc3_cell_consumed_by_earlier_token(self, tmp_path):
        """Cell value found only in already-consumed region → QC3."""
        # Source tokens: "AB", "AB" (duplicate cell)
        # JSON text: "AB" (appears once)
        # First "AB" is consumed, second "AB" finds only consumed region → QC3.
        xlsx_path = self._make_xlsx(tmp_path, [["AB", "AB"]])
        data = self._make_data([
            {"id": "s1", "title": "AB", "content": "", "hints": []},
        ], title="テスト")
        issues = self._check(xlsx_path, data)
        assert any("QC3" in i and "AB" in i for i in issues)

    def test_pass_markdown_syntax_in_content_not_qc2(self, tmp_path):
        """Markdown table/bold syntax in JSON content does not trigger QC2."""
        xlsx_path = self._make_xlsx(tmp_path, [["対策", "実施項目", "対応状況"]])
        content = "| 対策 | 実施項目 | 対応状況 |\n|---|---|---|\n| 根本的解決 | 実施する | 〇 |"
        data = self._make_data([
            {"id": "s1", "title": "対策", "content": content, "hints": []},
        ], title="テスト")
        # "根本的解決", "実施する", "〇" are in content but not in source cells.
        # Only markdown structure tokens (|, ---, etc.) should be stripped.
        # This test confirms table delimiters don't cause QC2.
        issues = self._check(xlsx_path, data)
        qc2_table_issues = [i for i in issues if "QC2" in i and ("|" in i or "---" in i)]
        assert qc2_table_issues == []

    def test_pass_empty_xlsx_no_source_tokens(self, tmp_path):
        """xlsx with all empty cells → no source tokens → skip QC checks."""
        xlsx_path = self._make_xlsx(tmp_path, [[None, None], ["", "  "]])
        data = self._make_data([
            {"id": "s1", "title": "何か", "content": "内容", "hints": []},
        ], title="タイトル")
        assert self._check(xlsx_path, data) == []

    def test_pass_fmt_not_xlsx_returns_empty(self, tmp_path):
        """verify_file with fmt != 'xlsx' returns empty list without reading files."""
        import json
        from scripts.verify.verify import verify_file
        json_path = tmp_path / "test.json"
        json_path.write_text(json.dumps({"id": "x", "title": "T", "no_knowledge_content": False, "sections": []}))
        assert verify_file(tmp_path / "test.rst", json_path, "rst") == []
        assert verify_file(tmp_path / "test.md", json_path, "md") == []


# ---------------------------------------------------------------------------
# check_docs_coverage: README.md existence
# ---------------------------------------------------------------------------

class TestCheckDocsCoverage:
    """check_docs_coverage — README.md must exist and count must match .md files."""

    def _check(self, knowledge_dir, docs_dir):
        from scripts.verify.verify import check_docs_coverage
        return check_docs_coverage(knowledge_dir, docs_dir)

    def _make_readme(self, docs_dir, count):
        """Write a minimal README.md with the given page count line."""
        (docs_dir / "README.md").write_text(f"# header\n\n{count} ページ\n")

    def test_pass_readme_exists_and_count_matches(self, tmp_path):
        """README.md present with matching count → no issues."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        sub = docs_dir / "component"
        sub.mkdir()
        (sub / "file1.md").write_text("# f1\n")
        (sub / "file2.md").write_text("# f2\n")
        self._make_readme(docs_dir, 2)
        assert self._check(tmp_path / "knowledge", docs_dir) == []

    def test_fail_readme_missing(self, tmp_path):
        """README.md absent from docs_dir → FAIL."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        issues = self._check(tmp_path / "knowledge", docs_dir)
        assert any("README.md" in i for i in issues)

    def test_fail_docs_dir_missing(self, tmp_path):
        """docs_dir does not exist → FAIL."""
        issues = self._check(tmp_path / "knowledge", tmp_path / "docs")
        assert any("README.md" in i for i in issues)

    def test_fail_count_mismatch(self, tmp_path):
        """README.md count does not match actual .md files → FAIL."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        sub = docs_dir / "component"
        sub.mkdir()
        (sub / "file1.md").write_text("# f1\n")
        (sub / "file2.md").write_text("# f2\n")
        self._make_readme(docs_dir, 5)  # wrong count
        issues = self._check(tmp_path / "knowledge", docs_dir)
        assert any("count" in i.lower() or "ページ" in i or "mismatch" in i.lower() for i in issues)

    def test_pass_readme_no_count_line(self, tmp_path):
        """README.md with no count line → skip count check (no false positive)."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        sub = docs_dir / "component"
        sub.mkdir()
        (sub / "file1.md").write_text("# f1\n")
        (docs_dir / "README.md").write_text("# header\n\n## section\n")
        assert self._check(tmp_path / "knowledge", docs_dir) == []


# ---------------------------------------------------------------------------
# check_hints_file_consistency: hints/vN.json == JSON hints == docs MD hints
# ---------------------------------------------------------------------------

class TestCheckHintsFileConsistency:
    """Three-way hints consistency: hints/vN.json == knowledge JSON == docs MD."""

    def _check(self, output_dir, docs_dir, hints_file):
        from scripts.verify.verify import check_hints_file_consistency
        return check_hints_file_consistency(output_dir, docs_dir, hints_file)

    def _write_json(self, output_dir, file_id, sections):
        """Write a minimal knowledge JSON with hints."""
        import json
        path = output_dir / f"{file_id}.json"
        data = {
            "id": file_id,
            "title": file_id,
            "no_knowledge_content": False,
            "sections": sections,
        }
        path.write_text(json.dumps(data), encoding="utf-8")

    def _write_docs_md(self, docs_dir, file_id, section_hints_map):
        """Write docs MD with keywords blocks for each section."""
        lines = [f"# {file_id}", ""]
        for title, hints in section_hints_map.items():
            lines += [f"## {title}", ""]
            if hints:
                lines += [
                    "<details>",
                    "<summary>keywords</summary>",
                    "",
                    ", ".join(hints),
                    "",
                    "</details>",
                    "",
                ]
        (docs_dir / f"{file_id}.md").write_text("\n".join(lines), encoding="utf-8")

    def _write_hints_file(self, path, hints_dict):
        """Write hints file in array form.

        Accepts either:
        * {file_id: [{"title", "hints"}, ...]}  (array form, used as-is)
        * {file_id: {title: hints}}             (dict form, normalized to array)
        """
        import json
        normalized: dict[str, list[dict]] = {}
        for fid, entries in hints_dict.items():
            if isinstance(entries, dict):
                normalized[fid] = [{"title": t, "hints": h} for t, h in entries.items()]
            else:
                normalized[fid] = entries
        path.write_text(json.dumps({"version": "6", "hints": normalized}), encoding="utf-8")

    def test_pass_all_consistent(self, tmp_path):
        """JSON hints == docs MD hints == hints file → no issues."""
        kd = tmp_path / "knowledge"
        kd.mkdir()
        dd = tmp_path / "docs"
        dd.mkdir()
        hf = tmp_path / "v6.json"
        self._write_json(kd, "file1", [{"id": "s1", "title": "概要", "content": "", "hints": ["h1", "h2"]}])
        self._write_docs_md(dd, "file1", {"概要": ["h1", "h2"]})
        self._write_hints_file(hf, {"file1": {"概要": ["h1", "h2"]}})
        assert self._check(kd, dd, hf) == []

    def test_pass_no_hints_file(self, tmp_path):
        """hints file absent → skip check (no false positive)."""
        kd = tmp_path / "knowledge"
        kd.mkdir()
        dd = tmp_path / "docs"
        dd.mkdir()
        hf = tmp_path / "v6.json"  # not created
        assert self._check(kd, dd, hf) == []

    def test_fail_json_hints_differ_from_hints_file(self, tmp_path):
        """JSON has different hints than hints file → FAIL."""
        kd = tmp_path / "knowledge"
        kd.mkdir()
        dd = tmp_path / "docs"
        dd.mkdir()
        hf = tmp_path / "v6.json"
        self._write_json(kd, "file1", [{"id": "s1", "title": "概要", "content": "", "hints": ["wrong"]}])
        self._write_docs_md(dd, "file1", {"概要": ["h1"]})
        self._write_hints_file(hf, {"file1": {"概要": ["h1"]}})
        issues = self._check(kd, dd, hf)
        assert any("file1" in i for i in issues)

    def test_fail_docs_md_hints_differ_from_hints_file(self, tmp_path):
        """docs MD has different hints than hints file → FAIL."""
        kd = tmp_path / "knowledge"
        kd.mkdir()
        dd = tmp_path / "docs"
        dd.mkdir()
        hf = tmp_path / "v6.json"
        self._write_json(kd, "file1", [{"id": "s1", "title": "概要", "content": "", "hints": ["h1"]}])
        self._write_docs_md(dd, "file1", {"概要": ["wrong"]})
        self._write_hints_file(hf, {"file1": {"概要": ["h1"]}})
        issues = self._check(kd, dd, hf)
        assert any("file1" in i for i in issues)

    def test_pass_empty_hints_all_consistent(self, tmp_path):
        """All hints empty and consistent → no issues."""
        kd = tmp_path / "knowledge"
        kd.mkdir()
        dd = tmp_path / "docs"
        dd.mkdir()
        hf = tmp_path / "v6.json"
        self._write_json(kd, "file1", [{"id": "s1", "title": "概要", "content": "", "hints": []}])
        self._write_docs_md(dd, "file1", {"概要": []})
        self._write_hints_file(hf, {})  # file1 not in hints file → expect empty
        assert self._check(kd, dd, hf) == []

    def test_pass_same_title_twice_positionally_aligned(self, tmp_path):
        """Same title appearing twice in both JSON and hints file → positional align OK."""
        import json as _json
        kd = tmp_path / "knowledge"
        kd.mkdir()
        dd = tmp_path / "docs"
        dd.mkdir()
        hf = tmp_path / "v6.json"
        # JSON with two sections of same title (h2 + h3 case)
        self._write_json(kd, "file1", [
            {"id": "s1", "title": "使用方法", "content": "", "hints": ["first"]},
            {"id": "s2", "title": "使用方法", "content": "", "hints": ["second"]},
        ])
        # docs MD: two blocks with same title
        (dd / "file1.md").write_text(
            "# file1\n\n"
            "## 使用方法\n\n<details>\n<summary>keywords</summary>\n\nfirst\n\n</details>\n\n"
            "## 使用方法\n\n<details>\n<summary>keywords</summary>\n\nsecond\n\n</details>\n",
            encoding="utf-8",
        )
        # hints file in array form
        hf.write_text(_json.dumps({
            "version": "6",
            "hints": {
                "file1": [
                    {"title": "使用方法", "hints": ["first"]},
                    {"title": "使用方法", "hints": ["second"]},
                ],
            },
        }), encoding="utf-8")
        # Check 1 (JSON ↔ hints file positional) must pass.
        issues = self._check(kd, dd, hf)
        # Filter out the docs-MD-side check (parser collapses same-title)
        json_issues = [i for i in issues if "JSON hints differ" in i or "not matched" in i]
        assert json_issues == []


# ---------------------------------------------------------------------------
# Phase 21-D (session 37): top-level hints three-way consistency
# ---------------------------------------------------------------------------


class TestCheckHintsFileConsistencyTopLevelHints:
    """Top-level hints three-way consistency: JSON `hints` ↔ hints file head ↔ docs MD file block."""

    def _check(self, output_dir, docs_dir, hints_file):
        from scripts.verify.verify import check_hints_file_consistency
        return check_hints_file_consistency(output_dir, docs_dir, hints_file)

    def _write_json_with_top_hints(self, output_dir, file_id, top_hints, sections):
        import json
        data = {
            "id": file_id,
            "title": file_id,
            "content": "",
            "hints": top_hints,
            "no_knowledge_content": False,
            "sections": sections,
        }
        (output_dir / f"{file_id}.json").write_text(json.dumps(data), encoding="utf-8")

    def _write_docs_md_with_top_hints(self, docs_dir, file_id, top_hints, section_hints_map):
        lines = [f"# {file_id}", ""]
        if top_hints:
            lines += [
                "<details>",
                "<summary>keywords</summary>",
                "",
                ", ".join(top_hints),
                "",
                "</details>",
                "",
            ]
        for title, hints in section_hints_map.items():
            lines += [f"## {title}", ""]
            if hints:
                lines += [
                    "<details>",
                    "<summary>keywords</summary>",
                    "",
                    ", ".join(hints),
                    "",
                    "</details>",
                    "",
                ]
        (docs_dir / f"{file_id}.md").write_text("\n".join(lines), encoding="utf-8")

    def _write_hints_file(self, path, entries_by_file):
        import json
        path.write_text(
            json.dumps({"version": "6", "hints": entries_by_file}),
            encoding="utf-8",
        )

    def test_pass_all_top_level_consistent(self, tmp_path):
        """JSON top-level hints == docs MD file-level block == hints file head entry."""
        kd = tmp_path / "knowledge"
        kd.mkdir()
        dd = tmp_path / "docs"
        dd.mkdir()
        hf = tmp_path / "v6.json"
        self._write_json_with_top_hints(
            kd, "file1", ["fk1", "fk2"],
            [{"id": "s1", "title": "概要", "content": "", "hints": ["s1k"]}],
        )
        self._write_docs_md_with_top_hints(
            dd, "file1", ["fk1", "fk2"],
            {"概要": ["s1k"]},
        )
        self._write_hints_file(hf, {
            "file1": [
                {"title": "file1", "hints": ["fk1", "fk2"]},
                {"title": "概要", "hints": ["s1k"]},
            ],
        })
        assert self._check(kd, dd, hf) == []

    def test_fail_json_top_hints_differ_from_hints_file(self, tmp_path):
        """JSON top-level hints ≠ hints file head entry → FAIL."""
        kd = tmp_path / "knowledge"
        kd.mkdir()
        dd = tmp_path / "docs"
        dd.mkdir()
        hf = tmp_path / "v6.json"
        # JSON stores wrong top-level hints
        self._write_json_with_top_hints(
            kd, "file1", ["wrong"],
            [{"id": "s1", "title": "概要", "content": "", "hints": ["s1k"]}],
        )
        self._write_docs_md_with_top_hints(
            dd, "file1", ["fk1"],
            {"概要": ["s1k"]},
        )
        self._write_hints_file(hf, {
            "file1": [
                {"title": "file1", "hints": ["fk1"]},
                {"title": "概要", "hints": ["s1k"]},
            ],
        })
        issues = self._check(kd, dd, hf)
        assert any("top-level" in i.lower() or "__file__" in i for i in issues), issues

    def test_fail_docs_md_missing_top_hints_block(self, tmp_path):
        """docs MD lacks the file-level keywords block but hints file expects it → FAIL."""
        kd = tmp_path / "knowledge"
        kd.mkdir()
        dd = tmp_path / "docs"
        dd.mkdir()
        hf = tmp_path / "v6.json"
        self._write_json_with_top_hints(
            kd, "file1", ["fk1"],
            [{"id": "s1", "title": "概要", "content": "", "hints": []}],
        )
        # docs MD without top-level hints block
        self._write_docs_md_with_top_hints(
            dd, "file1", [],
            {"概要": []},
        )
        self._write_hints_file(hf, {
            "file1": [
                {"title": "file1", "hints": ["fk1"]},
            ],
        })
        issues = self._check(kd, dd, hf)
        assert any("top-level" in i.lower() or "__file__" in i for i in issues), issues

    def test_fail_json_missing_top_hints_field(self, tmp_path):
        """JSON output lacks `hints` field altogether → FAIL."""
        import json as _json
        kd = tmp_path / "knowledge"
        kd.mkdir()
        dd = tmp_path / "docs"
        dd.mkdir()
        hf = tmp_path / "v6.json"
        # Legacy JSON with no `hints` field
        (kd / "file1.json").write_text(_json.dumps({
            "id": "file1",
            "title": "file1",
            "content": "",
            "no_knowledge_content": False,
            "sections": [],
        }), encoding="utf-8")
        # hints file expects file-level hints
        self._write_hints_file(hf, {
            "file1": [{"title": "file1", "hints": ["fk1"]}],
        })
        issues = self._check(kd, dd, hf)
        assert any("top-level" in i.lower() or "hints" in i.lower() for i in issues), issues

    def test_pass_when_hints_file_uses_file_sentinel_for_xlsx(self, tmp_path):
        """xlsx: hints file head entry title is "__file__" sentinel; JSON title is "".

        Verify must treat "__file__" as the file-level entry regardless of JSON
        top-level title value (Phase 21-D session 37 / schema design §3-4).
        """
        import json as _json
        kd = tmp_path / "knowledge"
        kd.mkdir()
        dd = tmp_path / "docs"
        dd.mkdir()
        hf = tmp_path / "v6.json"
        # xlsx-style JSON: title is ""
        (kd / "xls.json").write_text(_json.dumps({
            "id": "xls",
            "title": "",
            "content": "rows",
            "hints": ["セキュリティ", "CVE"],
            "no_knowledge_content": False,
            "sections": [],
        }), encoding="utf-8")
        # docs MD: top-level keywords block (no ## sections)
        (dd / "xls.md").write_text(
            "# \n\n<details>\n<summary>keywords</summary>\n\nセキュリティ, CVE\n\n</details>\n\nrows\n",
            encoding="utf-8",
        )
        self._write_hints_file(hf, {
            "xls": [{"title": "__file__", "hints": ["セキュリティ", "CVE"]}],
        })
        assert self._check(kd, dd, hf) == []

    def test_fail_xlsx_json_top_hints_differ_when_sentinel_used(self, tmp_path):
        """xlsx: JSON top-level hints ≠ __file__ sentinel entry's hints → FAIL."""
        import json as _json
        kd = tmp_path / "knowledge"
        kd.mkdir()
        dd = tmp_path / "docs"
        dd.mkdir()
        hf = tmp_path / "v6.json"
        (kd / "xls.json").write_text(_json.dumps({
            "id": "xls",
            "title": "",
            "content": "rows",
            "hints": ["wrong"],
            "no_knowledge_content": False,
            "sections": [],
        }), encoding="utf-8")
        (dd / "xls.md").write_text(
            "# \n\n<details>\n<summary>keywords</summary>\n\nwrong\n\n</details>\n\nrows\n",
            encoding="utf-8",
        )
        self._write_hints_file(hf, {
            "xls": [{"title": "__file__", "hints": ["セキュリティ"]}],
        })
        issues = self._check(kd, dd, hf)
        assert any("top-level" in i.lower() or "__file__" in i for i in issues), issues

    def test_pass_when_hints_file_has_no_file_level_entry(self, tmp_path):
        """hints file head entry title != top-level title → no top-level hints expected."""
        kd = tmp_path / "knowledge"
        kd.mkdir()
        dd = tmp_path / "docs"
        dd.mkdir()
        hf = tmp_path / "v6.json"
        self._write_json_with_top_hints(
            kd, "file1", [],
            [{"id": "s1", "title": "概要", "content": "", "hints": ["s1k"]}],
        )
        self._write_docs_md_with_top_hints(
            dd, "file1", [],
            {"概要": ["s1k"]},
        )
        # hints file head entry is a section title, not the file-level title
        self._write_hints_file(hf, {
            "file1": [
                {"title": "概要", "hints": ["s1k"]},
            ],
        })
        assert self._check(kd, dd, hf) == []

    def test_fail_stray_docs_md_top_hints_without_hints_file_expectation(self, tmp_path):
        """docs MD has a top-level keywords block, but hints file has no file-level entry → FAIL.

        Three-way consistency must catch drift in either direction.  A stray
        top-level block in docs MD — without a corresponding hints file entry
        or JSON top-level hints — is a correctness bug that must surface.
        """
        kd = tmp_path / "knowledge"
        kd.mkdir()
        dd = tmp_path / "docs"
        dd.mkdir()
        hf = tmp_path / "v6.json"
        # JSON has no top-level hints (empty)
        self._write_json_with_top_hints(
            kd, "file1", [],
            [{"id": "s1", "title": "概要", "content": "", "hints": ["s1k"]}],
        )
        # docs MD has a stray top-level keywords block
        self._write_docs_md_with_top_hints(
            dd, "file1", ["stray1", "stray2"],
            {"概要": ["s1k"]},
        )
        # hints file has no file-level entry — head is a section entry
        self._write_hints_file(hf, {
            "file1": [
                {"title": "概要", "hints": ["s1k"]},
            ],
        })
        issues = self._check(kd, dd, hf)
        assert any("top-level" in i.lower() or "stray" in i.lower() or "__file__" in i for i in issues), issues


# ---------------------------------------------------------------------------
# Phase 21-D: top-level content coverage in verify checks
# ---------------------------------------------------------------------------

class TestCheckContentCompletenessTopLevel:
    """QC1–QC4: top-level title and top-level content must be included in the
    sequential-delete algorithm (Phase 21-D schema change).

    Design: extraction order is
      top-level title → top-level content → sections[0].title → sections[0].content → ...
    """

    def _check(self, source_text, data, fmt):
        from scripts.verify.verify import check_content_completeness
        return check_content_completeness(source_text, data, fmt)

    def test_pass_top_level_content_matched_before_sections(self):
        """h1 title and top-level content present in source before first h2 → no FAIL."""
        source = "全体像\n======\n\n前書きの段落です。\n\n詳細\n====\n\n詳細の内容。\n"
        data = {
            "id": "f",
            "title": "全体像",
            "content": "前書きの段落です。",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "詳細", "content": "詳細の内容。", "hints": []},
            ],
        }
        assert self._check(source, data, "rst") == []

    def test_pass_top_level_content_only_no_sections(self):
        """File with only h1 + preamble (no h2/h3) → top-level content captured, sections=[]."""
        source = "全体像\n======\n\n唯一の段落です。\n"
        data = {
            "id": "f",
            "title": "全体像",
            "content": "唯一の段落です。",
            "no_knowledge_content": False,
            "sections": [],
        }
        assert self._check(source, data, "rst") == []

    def test_fail_qc1_top_level_content_missing(self):
        """Source preamble absent from JSON top-level content → QC1."""
        source = "全体像\n======\n\nこの前書きはJSONに入っていない。\n\n詳細\n====\n\n詳細の内容。\n"
        data = {
            "id": "f",
            "title": "全体像",
            "content": "",  # preamble not captured
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "詳細", "content": "詳細の内容。", "hints": []},
            ],
        }
        issues = self._check(source, data, "rst")
        assert any("QC1" in i for i in issues)

    def test_fail_qc2_top_level_content_fabricated(self):
        """JSON top-level content absent from source → QC2."""
        source = "全体像\n======\n\n本当の内容。\n"
        data = {
            "id": "f",
            "title": "全体像",
            "content": "捏造された段落。",  # not in source
            "no_knowledge_content": False,
            "sections": [],
        }
        issues = self._check(source, data, "rst")
        assert any("QC2" in i for i in issues)

    def test_pass_md_top_level_content(self):
        """Markdown: h1 + preamble + sections → all matched."""
        source = "# 全体像\n\n前書きの段落です。\n\n## 詳細\n\n詳細の内容。\n"
        data = {
            "id": "f",
            "title": "全体像",
            "content": "前書きの段落です。",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "詳細", "content": "詳細の内容。", "hints": []},
            ],
        }
        assert self._check(source, data, "md") == []


class TestCheckFormatPurityTopLevel:
    """QC5: top-level content must also be checked for residual source-format syntax."""

    def _check(self, data, fmt):
        from scripts.verify.verify import check_format_purity
        return check_format_purity(data, fmt)

    def test_rst_fail_role_in_top_level_content(self):
        """Top-level content with RST role syntax → QC5 FAIL."""
        data = {
            "id": "f",
            "title": "T",
            "content": "See :ref:`link-target` for details.",
            "no_knowledge_content": False,
            "sections": [],
        }
        issues = self._check(data, "rst")
        assert any("QC5" in i for i in issues)

    def test_md_fail_raw_html_in_top_level_content(self):
        """Top-level content with raw HTML → QC5 FAIL."""
        data = {
            "id": "f",
            "title": "T",
            "content": "Line1<br>Line2",
            "no_knowledge_content": False,
            "sections": [],
        }
        issues = self._check(data, "md")
        assert any("QC5" in i for i in issues)

    def test_rst_pass_clean_top_level_content(self):
        """Top-level content with no format syntax → no issues."""
        data = {
            "id": "f",
            "title": "T",
            "content": "プレーンな段落。",
            "no_knowledge_content": False,
            "sections": [],
        }
        assert self._check(data, "rst") == []


class TestCheckJsonDocsMdConsistencyTopLevel:
    """QO2 (formerly QO5): top-level content must also appear verbatim in docs MD under h1."""

    def _check(self, data, docs_md_text):
        from scripts.verify.verify import check_json_docs_md_consistency
        return check_json_docs_md_consistency(data, docs_md_text)

    def test_pass_top_level_content_present_under_h1(self):
        """Top-level content present verbatim under h1 → no issues."""
        data = {
            "id": "f",
            "title": "T",
            "content": "前書きの段落です。",
            "no_knowledge_content": False,
            "sections": [],
        }
        docs_md = "# T\n\n前書きの段落です。\n"
        assert self._check(data, docs_md) == []

    def test_fail_top_level_content_missing_from_docs_md(self):
        """Top-level content not present in docs MD → QO2 FAIL."""
        data = {
            "id": "f",
            "title": "T",
            "content": "この段落はdocsに無い。",
            "no_knowledge_content": False,
            "sections": [],
        }
        docs_md = "# T\n\n全く別の文章。\n"
        issues = self._check(data, docs_md)
        assert any("QO2" in i or "top-level" in i.lower() or "content" in i.lower() for i in issues)
        assert len(issues) >= 1

    def test_pass_empty_top_level_content_skipped(self):
        """Empty top-level content → nothing to check."""
        data = {
            "id": "f",
            "title": "T",
            "content": "",
            "no_knowledge_content": False,
            "sections": [
                {"id": "s1", "title": "A", "content": "A本文。", "hints": []},
            ],
        }
        docs_md = "# T\n\n## A\n\nA本文。\n"
        assert self._check(data, docs_md) == []

    def test_pass_top_level_content_with_assets_link_skipped(self):
        """Top-level content containing assets/ link is skipped (docs.py rewrites path)."""
        data = {
            "id": "f",
            "title": "T",
            "content": "説明\n![図](assets/my-file/diagram.png)",
            "no_knowledge_content": False,
            "sections": [],
        }
        docs_md = "# T\n\n説明\n![図](../../knowledge/assets/my-file/diagram.png)\n"
        assert self._check(data, docs_md) == []
