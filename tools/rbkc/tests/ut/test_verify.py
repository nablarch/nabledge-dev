"""Tests for scripts/verify/verify.py — rebuilt per rbkc-verify-quality-design.md."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# QO1: docs MD 構造整合性
# ---------------------------------------------------------------------------

class TestCheckJsonDocsMdConsistency_QO1:
    """QO1: docs MD structure (title, section titles, order) must match JSON."""

    def _check(self, data, docs_md_text):
        from scripts.verify.verify import check_json_docs_md_consistency
        return check_json_docs_md_consistency(data, docs_md_text)

    def test_pass_title_and_sections_match(self):
        data = {
            "id": "f", "title": "タイトル", "content": "", "sections": [
                {"id": "s1", "title": "概要", "content": "説明"},
                {"id": "s2", "title": "設定", "content": "設定内容"},
            ]
        }
        docs = "# タイトル\n\n## 概要\n\n説明\n\n## 設定\n\n設定内容\n"
        assert self._check(data, docs) == []

    def test_fail_title_mismatch(self):
        data = {"id": "f", "title": "正しいタイトル", "content": "", "sections": []}
        docs = "# 別のタイトル\n\n"
        issues = self._check(data, docs)
        assert any("QO1" in i and "title" in i for i in issues)

    def test_fail_section_title_missing(self):
        data = {
            "id": "f", "title": "T", "content": "", "sections": [
                {"id": "s1", "title": "存在しないセクション", "content": "c"},
            ]
        }
        docs = "# T\n\n## 別のセクション\n\nc\n"
        issues = self._check(data, docs)
        assert any("QO1" in i for i in issues)

    def test_fail_section_order_reversed(self):
        data = {
            "id": "f", "title": "T", "content": "", "sections": [
                {"id": "s1", "title": "A", "content": "a"},
                {"id": "s2", "title": "B", "content": "b"},
            ]
        }
        # B appears before A in docs MD — order mismatch
        docs = "# T\n\n## B\n\nb\n\n## A\n\na\n"
        issues = self._check(data, docs)
        assert any("QO1" in i for i in issues)

    def test_pass_no_knowledge_content_skipped(self):
        data = {"id": "f", "title": "T", "no_knowledge_content": True, "sections": []}
        assert self._check(data, "# 全然違う\n") == []

    def test_pass_no_sections_no_h2(self):
        """sections=[] means no ## headings expected in docs MD."""
        data = {"id": "f", "title": "T", "content": "本文です。", "sections": []}
        docs = "# T\n\n本文です。\n"
        assert self._check(data, docs) == []

    def test_fail_extra_h2_in_docs_md(self):
        """docs MD has ## heading but JSON has no sections → QO1 FAIL."""
        data = {"id": "f", "title": "T", "content": "本文です。", "sections": []}
        docs = "# T\n\n## 余計なセクション\n\n本文です。\n"
        issues = self._check(data, docs)
        assert any("QO1" in i for i in issues)


# ---------------------------------------------------------------------------
# QO2: docs MD 本文整合性
# ---------------------------------------------------------------------------

class TestCheckJsonDocsMdConsistency_QO2:
    """QO2: JSON content must appear verbatim in docs MD."""

    def _check(self, data, docs_md_text):
        from scripts.verify.verify import check_json_docs_md_consistency
        return check_json_docs_md_consistency(data, docs_md_text)

    def test_pass_top_content_in_docs(self):
        data = {"id": "f", "title": "T", "content": "トップレベル本文。", "sections": []}
        docs = "# T\n\nトップレベル本文。\n"
        assert self._check(data, docs) == []

    def test_fail_top_content_missing(self):
        data = {"id": "f", "title": "T", "content": "重要な本文。", "sections": []}
        docs = "# T\n\n全然違う内容。\n"
        issues = self._check(data, docs)
        assert any("QO2" in i for i in issues)

    def test_pass_section_content_in_docs(self):
        data = {
            "id": "f", "title": "T", "content": "", "sections": [
                {"id": "s1", "title": "概要", "content": "概要の説明。"},
            ]
        }
        docs = "# T\n\n## 概要\n\n概要の説明。\n"
        assert self._check(data, docs) == []

    def test_fail_section_content_missing(self):
        data = {
            "id": "f", "title": "T", "content": "", "sections": [
                {"id": "s1", "title": "概要", "content": "欠落する説明。"},
            ]
        }
        docs = "# T\n\n## 概要\n\n別の説明。\n"
        issues = self._check(data, docs)
        assert any("QO2" in i and "概要" in i for i in issues)

    def test_pass_assets_section_skipped(self):
        """Sections containing assets/ are skipped (docs.py rewrites paths)."""
        data = {
            "id": "f", "title": "T", "content": "", "sections": [
                {"id": "s1", "title": "図", "content": "![図](assets/img.png)"},
            ]
        }
        docs = "# T\n\n## 図\n\n![図](../assets/img.png)\n"
        assert self._check(data, docs) == []


# ---------------------------------------------------------------------------
# QO4: index.toon 網羅性
# ---------------------------------------------------------------------------

class TestCheckIndexCoverage:
    """QO4: every JSON without no_knowledge_content must be in index.toon."""

    def _check(self, knowledge_dir, index_path):
        from scripts.verify.verify import check_index_coverage
        return check_index_coverage(knowledge_dir, index_path)

    def _write_toon(self, idx_path, entries):
        """Write index.toon in real TOON format: comma-separated, indented rows."""
        lines = [
            "# Nabledge-6 Knowledge Index",
            "",
            f"files[{len(entries)},]{{title,type,category,processing_patterns,path}}:",
        ]
        for e in entries:
            lines.append(f"  {', '.join(e)}")
        idx_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_pass_all_files_indexed(self, tmp_path):
        kdir = tmp_path / "knowledge"
        kdir.mkdir()
        (kdir / "a.json").write_text(json.dumps({"id": "a", "title": "A", "no_knowledge_content": False}))
        idx = tmp_path / "index.toon"
        self._write_toon(idx, [["A", "", "", "", "a.json"]])
        assert self._check(kdir, idx) == []

    def test_fail_json_not_in_index(self, tmp_path):
        kdir = tmp_path / "knowledge"
        kdir.mkdir()
        (kdir / "missing.json").write_text(json.dumps({"id": "m", "title": "M", "no_knowledge_content": False}))
        idx = tmp_path / "index.toon"
        self._write_toon(idx, [])
        issues = self._check(kdir, idx)
        assert any("QO4" in i and "missing.json" in i for i in issues)

    def test_pass_no_knowledge_content_excluded(self, tmp_path):
        kdir = tmp_path / "knowledge"
        kdir.mkdir()
        (kdir / "toc.json").write_text(json.dumps({"id": "t", "title": "T", "no_knowledge_content": True}))
        idx = tmp_path / "index.toon"
        self._write_toon(idx, [])
        assert self._check(kdir, idx) == []

    def test_pass_nested_path_indexed(self, tmp_path):
        """Nested JSON with commas in title must parse correctly from TOON."""
        kdir = tmp_path / "knowledge"
        (kdir / "sub").mkdir(parents=True)
        (kdir / "sub" / "b.json").write_text(json.dumps({"id": "b", "title": "B"}))
        idx = tmp_path / "index.toon"
        self._write_toon(idx, [["B", "about", "sub", "", "sub/b.json"]])
        assert self._check(kdir, idx) == []

    def test_fail_missing_index_file(self, tmp_path):
        kdir = tmp_path / "knowledge"
        kdir.mkdir()
        (kdir / "a.json").write_text(json.dumps({"id": "a", "title": "A", "no_knowledge_content": False}))
        issues = self._check(kdir, tmp_path / "nonexistent.toon")
        assert any("QO4" in i for i in issues)


# ---------------------------------------------------------------------------
# QO3: docs MD 存在確認 (via check_docs_coverage)
# ---------------------------------------------------------------------------

class TestCheckDocsCoverage:
    """QO3: README.md count matches .md file count in docs_dir."""

    def _check(self, knowledge_dir, docs_dir):
        from scripts.verify.verify import check_docs_coverage
        return check_docs_coverage(knowledge_dir, docs_dir)

    def test_pass_readme_count_matches(self, tmp_path):
        kdir = tmp_path / "knowledge"
        kdir.mkdir()
        ddir = tmp_path / "docs"
        ddir.mkdir()
        (ddir / "a.md").write_text("content")
        (ddir / "README.md").write_text("1ページ\n")
        assert self._check(kdir, ddir) == []

    def test_fail_readme_count_mismatch(self, tmp_path):
        kdir = tmp_path / "knowledge"
        kdir.mkdir()
        ddir = tmp_path / "docs"
        ddir.mkdir()
        (ddir / "a.md").write_text("content")
        (ddir / "b.md").write_text("content")
        (ddir / "README.md").write_text("1ページ\n")
        issues = self._check(kdir, ddir)
        assert any("QO3" in i or "count mismatch" in i for i in issues)

    def test_fail_readme_missing(self, tmp_path):
        kdir = tmp_path / "knowledge"
        kdir.mkdir()
        ddir = tmp_path / "docs"
        ddir.mkdir()
        issues = self._check(kdir, ddir)
        assert any("README" in i for i in issues)


# ---------------------------------------------------------------------------
# QC5: 形式純粋性
# ---------------------------------------------------------------------------

class TestVerifyFileQC5:
    """QC5: No format-specific syntax remnants in JSON output."""

    def _check(self, data, fmt):
        from scripts.verify.verify import verify_file
        import json, tempfile, os
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{fmt}', delete=False, encoding='utf-8') as sf:
            sf.write("dummy source\n")
            src = sf.name
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as jf:
            json.dump(data, jf, ensure_ascii=False)
            jpath = jf.name
        try:
            from scripts.verify.verify import verify_file
            return verify_file(src, jpath, fmt)
        finally:
            os.unlink(src)
            os.unlink(jpath)

    # RST format
    def test_fail_rst_role_in_content(self):
        data = {"id": "f", "title": "T", "content": "", "sections": [
            {"id": "s1", "title": "概要", "content": ":ref:`something`"}
        ]}
        issues = self._check(data, "rst")
        assert any("QC5" in i and "RST role" in i for i in issues)

    def test_fail_rst_directive_in_content(self):
        data = {"id": "f", "title": "T", "content": "", "sections": [
            {"id": "s1", "title": "概要", "content": ".. note::"}
        ]}
        issues = self._check(data, "rst")
        assert any("QC5" in i and "directive" in i for i in issues)

    def test_fail_rst_label_in_content(self):
        data = {"id": "f", "title": "T", "content": "", "sections": [
            {"id": "s1", "title": "概要", "content": ".. _my-label:"}
        ]}
        issues = self._check(data, "rst")
        assert any("QC5" in i and "label" in i for i in issues)

    def test_fail_rst_heading_underline_in_title(self):
        data = {"id": "f", "title": "====", "content": "", "sections": []}
        issues = self._check(data, "rst")
        assert any("QC5" in i and "underline" in i for i in issues)

    def test_pass_rst_clean_content(self):
        data = {"id": "f", "title": "概要", "content": "普通の本文です。", "sections": [
            {"id": "s1", "title": "詳細", "content": "詳細説明。"}
        ]}
        assert [i for i in self._check(data, "rst") if "QC5" in i] == []

    # MD format
    def test_fail_md_raw_html_in_content(self):
        data = {"id": "f", "title": "T", "content": "", "sections": [
            {"id": "s1", "title": "概要", "content": "<details>内容</details>"}
        ]}
        issues = self._check(data, "md")
        assert any("QC5" in i and "HTML" in i for i in issues)

    def test_fail_md_backslash_escape_in_content(self):
        data = {"id": "f", "title": "T", "content": "", "sections": [
            {"id": "s1", "title": "概要", "content": r"これは\*エスケープ\*です"}
        ]}
        issues = self._check(data, "md")
        assert any("QC5" in i and "backslash" in i for i in issues)

    def test_pass_md_clean_content(self):
        data = {"id": "f", "title": "概要", "content": "普通の説明文。", "sections": [
            {"id": "s1", "title": "詳細", "content": "詳細です。`code` も含む。"}
        ]}
        assert [i for i in self._check(data, "md") if "QC5" in i] == []

    def test_pass_xlsx_no_qc5(self):
        """xlsx format: QC5 is not applicable — _check_format_purity returns []."""
        from scripts.verify.verify import _check_format_purity
        data = {"id": "f", "title": "T", "content": ":ref:`role`", "sections": []}
        assert _check_format_purity(data, "xlsx") == []

    def test_pass_no_knowledge_content_skipped(self):
        data = {"id": "f", "title": "T", "no_knowledge_content": True, "sections": []}
        assert self._check(data, "rst") == []


# ---------------------------------------------------------------------------
# QL2: 外部URL一致
# ---------------------------------------------------------------------------

class TestVerifyFileQL2:
    """QL2: External URLs in source must appear verbatim in JSON."""

    def _check_ql2(self, source_text, data, fmt):
        from scripts.verify.verify import check_external_urls
        return check_external_urls(source_text, data, fmt)

    def test_pass_url_in_json(self):
        src = "詳細は https://example.com を参照。\n"
        data = {"id": "f", "title": "T", "content": "https://example.com を参照。", "sections": []}
        assert self._check_ql2(src, data, "rst") == []

    def test_fail_url_missing_from_json(self):
        src = "詳細は https://example.com を参照。\n"
        data = {"id": "f", "title": "T", "content": "説明。", "sections": []}
        issues = self._check_ql2(src, data, "rst")
        assert any("QL2" in i and "example.com" in i for i in issues)

    def test_pass_duplicate_url_reported_once(self):
        src = "https://example.com と https://example.com が重複。\n"
        data = {"id": "f", "title": "T", "content": "https://example.com を参照。", "sections": []}
        issues = self._check_ql2(src, data, "rst")
        # URL present in JSON → no FAIL even if duplicated in source
        assert all("QL2" not in i for i in issues)

    def test_pass_rst_target_def_url_excluded(self):
        src = ".. _Name: https://only-in-target.com\n通常テキスト\n"
        data = {"id": "f", "title": "T", "content": "通常テキスト", "sections": []}
        # RST target definition URLs are dropped by converter, so no QL2 FAIL
        assert self._check_ql2(src, data, "rst") == []

    def test_pass_no_source_urls(self):
        src = "URLなしのテキスト\n"
        data = {"id": "f", "title": "T", "content": "説明。", "sections": []}
        assert self._check_ql2(src, data, "rst") == []

    def test_pass_xlsx_skipped(self):
        src = "https://should-be-ignored.com\n"
        data = {"id": "f", "title": "T", "content": "説明。", "sections": []}
        assert self._check_ql2(src, data, "xlsx") == []

    def test_pass_no_knowledge_content_skipped(self):
        src = "https://example.com\n"
        data = {"id": "f", "title": "T", "no_knowledge_content": True, "sections": []}
        assert self._check_ql2(src, data, "rst") == []

    def test_fail_url_in_section_content_missing(self):
        src = "詳細は https://example.com を参照。\n"
        data = {"id": "f", "title": "T", "content": "", "sections": [
            {"id": "s1", "title": "参照", "content": "リンクなし"}
        ]}
        issues = self._check_ql2(src, data, "rst")
        assert any("QL2" in i for i in issues)

    def test_pass_url_in_section_content(self):
        src = "詳細は https://example.com を参照。\n"
        data = {"id": "f", "title": "T", "content": "", "sections": [
            {"id": "s1", "title": "参照", "content": "https://example.com を参照。"}
        ]}
        assert self._check_ql2(src, data, "rst") == []

    def test_pass_rst_inline_code_url_trailing_backtick_trimmed(self):
        """RST ``http://...`` must not leak trailing backticks into the URL."""
        src = "起動したら ``http://localhost:9080/`` にアクセス。\n"
        data = {"id": "f", "title": "T", "content": "起動したら `http://localhost:9080/` にアクセス。", "sections": []}
        assert self._check_ql2(src, data, "rst") == []

    def test_pass_rst_substitution_only_url_skipped(self):
        """URLs appearing only inside a substitution directive body are skipped."""
        src = (
            "通常テキスト。\n\n"
            ".. |jsr317| raw:: html\n\n"
            "   <a href=\"https://only-in-subst.example\" target=\"_blank\">Text</a>\n"
        )
        data = {"id": "f", "title": "T", "content": "通常テキスト。", "sections": []}
        assert self._check_ql2(src, data, "rst") == []


# ---------------------------------------------------------------------------
# QC1-QC4: content completeness (RST/MD sequential-delete)
# ---------------------------------------------------------------------------

class TestCheckContentCompleteness:
    """QC1-QC4: sequential-delete algorithm via check_content_completeness."""

    def _check(self, source_text, data, fmt="rst", label_map=None):
        from scripts.verify.verify import check_content_completeness
        return check_content_completeness(source_text, data, fmt, label_map)

    def _data(self, title="", content="", sections=None):
        return {
            "id": "f", "title": title, "content": content,
            "sections": sections or []
        }

    # --- QC2: fabricated content (not in source) ---

    def test_fail_qc2_fabricated_title(self):
        src = "概要\n====\n\n本文。\n"
        data = self._data(sections=[
            {"id": "s1", "title": "存在しないセクション", "content": "本文。"}
        ])
        issues = self._check(src, data)
        assert any("QC2" in i and "fabricated" in i for i in issues)

    def test_fail_qc2_fabricated_content(self):
        src = "概要\n====\n\n本文。\n"
        data = self._data(sections=[
            {"id": "s1", "title": "概要", "content": "捏造されたテキスト。"}
        ])
        issues = self._check(src, data)
        assert any("QC2" in i and "fabricated" in i for i in issues)

    # --- QC3: duplicate content ---

    def test_fail_qc3_duplicate_title(self):
        src = "概要\n====\n\n本文。\n\n詳細\n====\n\n詳細内容。\n"
        data = self._data(sections=[
            {"id": "s1", "title": "概要", "content": "本文。"},
            {"id": "s2", "title": "概要", "content": "詳細内容。"},  # duplicate title
        ])
        issues = self._check(src, data)
        assert any("QC3" in i for i in issues)

    # --- QC4: misplaced content ---

    def test_fail_qc4_misplaced_title(self):
        src = "詳細\n====\n\n詳細内容。\n\n概要\n====\n\n概要内容。\n"
        data = self._data(sections=[
            {"id": "s1", "title": "概要", "content": "概要内容。"},   # appears later in source
            {"id": "s2", "title": "詳細", "content": "詳細内容。"},   # appears earlier in source
        ])
        issues = self._check(src, data)
        assert any("QC4" in i for i in issues)

    # --- QC1: source content not captured ---

    def test_fail_qc1_residual_content(self):
        src = "概要\n====\n\n本文。\n\n追加情報はここにあります。\n"
        data = self._data(sections=[
            {"id": "s1", "title": "概要", "content": "本文。"}
            # "追加情報はここにあります。" not captured
        ])
        issues = self._check(src, data)
        assert any("QC1" in i for i in issues)

    def test_pass_rst_syntax_in_residual_allowed(self):
        # Converter renders `.. note::` as `> **Note:** ...` so JSON content
        # includes the MD admonition header.
        src = "概要\n====\n\n本文。\n\n.. note::\n\n   注記内容。\n"
        data = self._data(sections=[
            {"id": "s1", "title": "概要", "content": "本文。\n\n> **Note:** 注記内容。"}
        ])
        issues = self._check(src, data)
        assert all("QC1" not in i for i in issues)

    def test_pass_md_heading_in_residual_allowed(self):
        src = "# タイトル\n\n## セクション\n\n本文。\n"
        data = self._data(sections=[
            {"id": "s1", "title": "セクション", "content": "本文。"}
        ])
        issues = self._check(src, data, fmt="md")
        assert all("QC1" not in i for i in issues)

    # --- PASS cases ---

    def test_pass_all_content_captured(self):
        src = "概要\n====\n\n本文です。\n"
        data = self._data(sections=[
            {"id": "s1", "title": "概要", "content": "本文です。"}
        ])
        assert self._check(src, data) == []

    def test_pass_no_knowledge_content_skipped(self):
        data = {"id": "f", "title": "T", "no_knowledge_content": True, "sections": []}
        assert self._check("any source", data) == []

    def test_pass_empty_data_no_issues(self):
        data = self._data()
        assert self._check("any source", data) == []

    def test_pass_md_verbatim_match(self):
        """MD source and MD JSON content are same format — verbatim match."""
        src = "## セクション\n\n**重要な**情報があります。\n"
        data = self._data(sections=[
            {"id": "s1", "title": "セクション", "content": "**重要な**情報があります。"}
        ])
        issues = self._check(src, data, fmt="md")
        assert all("QC2" not in i for i in issues)
        assert all("QC1" not in i for i in issues)

    def test_pass_top_level_content_captured(self):
        src = "タイトル\n========\n\nトップレベル本文。\n\nセクション\n==========\n\nセクション本文。\n"
        data = self._data(
            title="タイトル",
            content="トップレベル本文。",
            sections=[{"id": "s1", "title": "セクション", "content": "セクション本文。"}]
        )
        assert self._check(src, data) == []

    # --- RST normalization: false positive prevention ---

    def test_pass_rst_double_backtick_inline_code(self):
        """RST ``code`` is converted to MD `code` — must not trigger QC2."""
        src = "名前空間が ``javax.*`` から ``jakarta.*`` になる。\n"
        data = self._data(content="名前空間が `javax.*` から `jakarta.*` になる。")
        assert self._check(src, data) == []

    def test_pass_rst_ref_label_resolved_text(self):
        """RST :ref:`label` is resolved to display text — must not trigger QC2."""
        src = "詳細は :ref:`doma_dependency` を参照。\n\ndoma_dependency\n===============\n\nDoma 設定。\n"
        # converter resolves :ref:`doma_dependency` to label and also captures the section content
        data = self._data(
            content="詳細は doma_dependency を参照。",
            sections=[{"id": "s1", "title": "doma_dependency", "content": "Doma 設定。"}]
        )
        assert self._check(src, data) == []

    def test_pass_rst_external_link_text(self):
        """RST `text <url>`_ is converted to MD [text](url) — must not trigger QC2."""
        src = "`公式サイト <https://example.com>`_ を参照。\n"
        data = self._data(content="[公式サイト](https://example.com) を参照。")
        assert self._check(src, data) == []

    def test_pass_rst_ref_display_form_resolved(self):
        """RST :ref:`display <label>` resolved to display text — must not trigger QC2."""
        src = "詳細は :ref:`Doma設定 <doma_config>` を参照。\n"
        data = self._data(content="詳細は Doma設定 を参照。")
        assert self._check(src, data) == []

    def test_pass_rst_backtick_underscore_literal_in_code(self):
        """RST ``_`` literal underscore inside inline code must not be stripped as
        named-reference marker. Converter emits `_` in MD; both sides must align."""
        src = "区切り文字に ``_`` を使用する。\n"
        data = self._data(content="区切り文字に `_` を使用する。")
        assert self._check(src, data) == []

    def test_pass_rst_comment_line_is_syntax(self):
        """``.. text-without-colons`` lines are RST comments per spec and must be
        treated as allowed syntax residue for QC1."""
        src = "概要\n====\n\n本文。\n\n.. textlint-disable ja/foo\n"
        data = self._data(sections=[
            {"id": "s1", "title": "概要", "content": "本文。"}
        ])
        assert self._check(src, data) == []

    def test_pass_rst_comment_block_with_indented_body(self):
        """``..`` comment with indented body: entire block is RST syntax per spec."""
        src = (
            "概要\n====\n\n本文。\n\n"
            ".. 実装済み\n"
            ".. * 項目1\n"
            "..   * サブ項目\n"
            ".. * 項目2\n"
        )
        data = self._data(sections=[
            {"id": "s1", "title": "概要", "content": "本文。"}
        ])
        assert self._check(src, data) == []

    def test_pass_rst_field_list_with_inline_value(self):
        """RST field list ``:name: value`` — converter preserves as MD; both sides align."""
        src = "概要\n====\n\n:エスケープ対象文字: ``%`` 、 ``_``\n"
        data = self._data(sections=[
            {"id": "s1", "title": "概要", "content": ":エスケープ対象文字: `%` 、 `_`"}
        ])
        assert self._check(src, data) == []

    def test_pass_rst_field_list_with_separate_value(self):
        """RST field list ``:name:\\n  value`` — value on indented next line."""
        src = (
            "概要\n====\n\n"
            ":Status-Code:\n"
            "  応答電文のステータスコード。\n"
        )
        data = self._data(sections=[
            {"id": "s1", "title": "概要", "content": ":Status-Code:\n応答電文のステータスコード。"}
        ])
        assert self._check(src, data) == []


# ---------------------------------------------------------------------------
# Excel QC1/QC2/QC3: verify_file(fmt="xlsx")
# ---------------------------------------------------------------------------

class TestVerifyFileExcel:
    """Excel sequential-delete: source cells must appear in JSON text."""

    def _check(self, source_path, data):
        from scripts.verify.verify import verify_file
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as jf:
            json.dump(data, jf, ensure_ascii=False)
            jpath = jf.name
        try:
            return verify_file(source_path, jpath, "xlsx")
        finally:
            os.unlink(jpath)

    def test_pass_real_xlsx(self, tmp_path):
        """A real .xlsx with one cell 'Hello' whose value appears in JSON title."""
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not available")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws["A1"] = "Hello"
        xlsx_path = tmp_path / "test.xlsx"
        wb.save(xlsx_path)
        data = {"id": "f", "title": "Hello", "content": "", "sections": []}
        assert self._check(str(xlsx_path), data) == []

    def test_fail_cell_missing_from_json(self, tmp_path):
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not available")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws["A1"] = "必須セル値"
        xlsx_path = tmp_path / "test.xlsx"
        wb.save(xlsx_path)
        data = {"id": "f", "title": "別の内容", "content": "", "sections": []}
        issues = self._check(str(xlsx_path), data)
        assert any("QC1" in i for i in issues)

    def test_pass_no_knowledge_content_skipped(self, tmp_path):
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not available")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws["A1"] = "値"
        xlsx_path = tmp_path / "test.xlsx"
        wb.save(xlsx_path)
        data = {"id": "f", "title": "T", "no_knowledge_content": True, "sections": []}
        assert self._check(str(xlsx_path), data) == []


# ---------------------------------------------------------------------------
# QL1: 内部リンク (check_source_links)
# ---------------------------------------------------------------------------

class TestCheckSourceLinks:
    """QL1: Internal links in source must be reflected in JSON."""

    def _check(self, source_text, fmt, data, label_map=None):
        from scripts.verify.verify import check_source_links
        return check_source_links(source_text, fmt, data, label_map or {})

    def _data(self, content="", sections=None):
        return {
            "id": "f", "title": "T", "content": content,
            "sections": sections or []
        }

    # RST :ref:
    def test_pass_rst_ref_display_text_in_json(self):
        src = "詳細は :ref:`使い方 <usage>` を参照。\n"
        data = self._data(content="詳細は 使い方 を参照。")
        assert self._check(src, "rst", data) == []

    def test_fail_rst_ref_display_text_missing(self):
        src = "詳細は :ref:`使い方 <usage>` を参照。\n"
        data = self._data(content="詳細を参照。")
        issues = self._check(src, "rst", data)
        assert any("QL1" in i and "使い方" in i for i in issues)

    def test_pass_rst_ref_plain_label_resolved(self):
        src = ":ref:`usage`\n"
        data = self._data(content="使い方セクション")
        label_map = {"usage": "使い方セクション"}
        assert self._check(src, "rst", data, label_map) == []

    def test_fail_rst_ref_plain_label_title_missing(self):
        src = ":ref:`usage`\n"
        data = self._data(content="別の内容")
        label_map = {"usage": "使い方セクション"}
        issues = self._check(src, "rst", data, label_map)
        assert any("QL1" in i and "usage" in i for i in issues)

    def test_pass_rst_ref_unknown_label_skipped(self):
        src = ":ref:`cross-file-label`\n"
        data = self._data(content="内容")
        # Unknown label (not in label_map) → cannot verify cross-file ref → PASS
        assert self._check(src, "rst", data, {}) == []

    # MD internal links
    def test_pass_md_internal_link_text_in_json(self):
        src = "[使い方](./usage.md)\n"
        data = self._data(content="使い方")
        assert self._check(src, "md", data) == []

    def test_fail_md_internal_link_text_missing(self):
        src = "[使い方](./usage.md)\n"
        data = self._data(content="別の内容")
        issues = self._check(src, "md", data)
        assert any("QL1" in i and "使い方" in i for i in issues)

    def test_pass_md_external_link_skipped(self):
        """External links (https://) are QL2, not QL1."""
        src = "[外部サイト](https://example.com)\n"
        data = self._data(content="内容")
        assert self._check(src, "md", data) == []

    def test_pass_no_knowledge_content_skipped(self):
        src = ":ref:`something`\n"
        data = {"id": "f", "title": "T", "no_knowledge_content": True, "sections": []}
        assert self._check(src, "rst", data) == []
