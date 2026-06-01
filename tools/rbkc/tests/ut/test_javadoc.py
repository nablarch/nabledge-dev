"""Unit tests for scripts/create/javadoc.py (Issue #363)."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from scripts.create.javadoc import (
    _class_fqcn,
    _extract_fqcns,
    _parse_javadoc_md,
    fqcn_to_file_id,
)


# ---------------------------------------------------------------------------
# _extract_fqcns
# ---------------------------------------------------------------------------

class TestExtractFqcns:
    def test_angle_bracket_form(self):
        rst = ":java:extdoc:`UniversalDao <nablarch.common.dao.UniversalDao>`"
        fqcns = _extract_fqcns(rst)
        assert "nablarch.common.dao.UniversalDao" in fqcns

    def test_no_angle_bracket_form(self):
        rst = ":java:extdoc:`nablarch.common.dao.UniversalDao`"
        fqcns = _extract_fqcns(rst)
        assert "nablarch.common.dao.UniversalDao" in fqcns

    def test_method_suffix_stripped(self):
        rst = ":java:extdoc:`UniversalDao#insert <nablarch.common.dao.UniversalDao.insert(java.lang.Object)>`"
        fqcns = _extract_fqcns(rst)
        # Method suffix in parens stripped
        assert "nablarch.common.dao.UniversalDao.insert" in fqcns
        assert not any("(java.lang.Object)" in f for f in fqcns)

    def test_non_nablarch_excluded(self):
        rst = ":java:extdoc:`String <java.lang.String>`"
        fqcns = _extract_fqcns(rst)
        assert not fqcns

    def test_jakarta_excluded(self):
        rst = ":java:extdoc:`Entity <jakarta.persistence.Entity>`"
        fqcns = _extract_fqcns(rst)
        assert not fqcns

    def test_multiple_fqcns(self):
        rst = textwrap.dedent("""\
            :java:extdoc:`UniversalDao <nablarch.common.dao.UniversalDao>`
            :java:extdoc:`BasicDaoContext <nablarch.common.dao.BasicDaoContext>`
            :java:extdoc:`String <java.lang.String>`
        """)
        fqcns = _extract_fqcns(rst)
        assert "nablarch.common.dao.UniversalDao" in fqcns
        assert "nablarch.common.dao.BasicDaoContext" in fqcns
        assert "java.lang.String" not in fqcns

    def test_space_before_angle_bracket(self):
        rst = ":java:extdoc:`ObjectMapper <nablarch.common.databind.ObjectMapper>`"
        fqcns = _extract_fqcns(rst)
        assert "nablarch.common.databind.ObjectMapper" in fqcns


# ---------------------------------------------------------------------------
# _class_fqcn
# ---------------------------------------------------------------------------

class TestClassFqcn:
    def test_plain_class(self):
        assert _class_fqcn("nablarch.common.dao.UniversalDao") == "nablarch.common.dao.UniversalDao"

    def test_method_dotted(self):
        # nablarch.common.dao.UniversalDao.insert → UniversalDao is the last uppercase-start
        assert _class_fqcn("nablarch.common.dao.UniversalDao.insert") == "nablarch.common.dao.UniversalDao"

    def test_nested_class(self):
        # Inner class: nablarch.fw.web.HttpRequest.Body → HttpRequest is the class
        result = _class_fqcn("nablarch.fw.web.HttpRequest.Body")
        # Both HttpRequest and Body start with uppercase; first uppercase-start wins
        assert result == "nablarch.fw.web.HttpRequest"

    def test_no_uppercase(self):
        # Fallback: return as-is
        result = _class_fqcn("nablarch.common.dao")
        assert result == "nablarch.common.dao"


# ---------------------------------------------------------------------------
# fqcn_to_file_id
# ---------------------------------------------------------------------------

class TestFqcnToFileId:
    def test_basic(self):
        result = fqcn_to_file_id("nablarch.common.dao.UniversalDao")
        assert result == "javadoc-nablarch-common-dao-UniversalDao"

    def test_deep_package(self):
        result = fqcn_to_file_id("nablarch.fw.batch.ee.chunk.BaseDatabaseItemReader")
        assert result == "javadoc-nablarch-fw-batch-ee-chunk-BaseDatabaseItemReader"


# ---------------------------------------------------------------------------
# _parse_javadoc_md
# ---------------------------------------------------------------------------

class TestParseJavadocMd:
    def _sample_md(self):
        return textwrap.dedent("""\
            # class UniversalDao

            **パッケージ:** nablarch.common.dao

            汎用的なDAO機能を提供するクラス。

            ## フィールドの詳細

            ## コンストラクタの詳細

            ## メソッドの詳細

            ### findById

            ```java
            public static <T> T findById(Class<T> entityClass, Object id)
            ```

            主キーを条件にエンティティを取得する。

            ### insert

            ```java
            public static void insert(Object entity)
            ```

            エンティティをINSERTする。
        """)

    def test_title_extracted(self):
        data = _parse_javadoc_md(self._sample_md())
        assert data["title"] == "class UniversalDao"

    def test_top_content(self):
        data = _parse_javadoc_md(self._sample_md())
        assert "汎用的なDAO機能を提供するクラス" in data["content"]

    def test_h2_sections(self):
        data = _parse_javadoc_md(self._sample_md())
        h2_titles = [s["title"] for s in data["sections"] if s["level"] == 2]
        assert "フィールドの詳細" in h2_titles
        assert "コンストラクタの詳細" in h2_titles
        assert "メソッドの詳細" in h2_titles

    def test_h3_method_sections(self):
        data = _parse_javadoc_md(self._sample_md())
        h3_titles = [s["title"] for s in data["sections"] if s["level"] == 3]
        assert "findById" in h3_titles
        assert "insert" in h3_titles

    def test_h3_content_has_code_and_description(self):
        data = _parse_javadoc_md(self._sample_md())
        find_by_id = next(s for s in data["sections"] if s["title"] == "findById")
        assert "findById" in find_by_id["content"]
        assert "主キーを条件にエンティティを取得する" in find_by_id["content"]

    def test_no_knowledge_content_false(self):
        data = _parse_javadoc_md(self._sample_md())
        assert data["no_knowledge_content"] is False

    def test_empty_h2_section(self):
        data = _parse_javadoc_md(self._sample_md())
        fields_section = next(s for s in data["sections"] if s["title"] == "フィールドの詳細")
        # Empty section should have empty content
        assert fields_section["content"] == ""

    def test_preamble_only(self):
        md = textwrap.dedent("""\
            # class SimpleClass

            シンプルなクラス。
        """)
        data = _parse_javadoc_md(md)
        assert data["title"] == "class SimpleClass"
        assert "シンプルなクラス" in data["content"]
        assert data["sections"] == []
