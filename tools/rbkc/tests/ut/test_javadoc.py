"""Unit tests for scripts.create.javadoc — javadoc_generate helpers.

TDD: write tests first (RED), then implement (GREEN).
"""
from __future__ import annotations

import json
import textwrap

import pytest


# ---------------------------------------------------------------------------
# _extract_fqcns
# ---------------------------------------------------------------------------

class TestExtractFqcns:
    """Extract nablarch.* FQCNs from RST text containing :java:extdoc: roles."""

    def _extract(self, rst_text):
        from scripts.create.javadoc import _extract_fqcns
        return _extract_fqcns(rst_text)

    def test_basic_nablarch_fqcn(self):
        rst = ":java:extdoc:`UniversalDao <nablarch.common.dao.UniversalDao>`\n"
        result = self._extract(rst)
        assert "nablarch.common.dao.UniversalDao" in result

    def test_java_std_excluded(self):
        rst = ":java:extdoc:`String <java.lang.String>`\n"
        result = self._extract(rst)
        assert "java.lang.String" not in result

    def test_jakarta_excluded(self):
        rst = ":java:extdoc:`HttpServletRequest <jakarta.servlet.http.HttpServletRequest>`\n"
        result = self._extract(rst)
        assert not any(f.startswith("jakarta.") for f in result)

    def test_method_suffix_stripped(self):
        """FQCN with method suffix — return class FQCN only."""
        rst = ":java:extdoc:`UniversalDao#findById <nablarch.common.dao.UniversalDao#findById>`\n"
        result = self._extract(rst)
        assert "nablarch.common.dao.UniversalDao" in result
        assert any("#" in f for f in result) is False

    def test_constructor_suffix_stripped(self):
        """Constructor FQCN (.<init>(args)) — return class FQCN only."""
        rst = ":java:extdoc:`MessageSenderSettings<nablarch.fw.messaging.MessageSenderSettings.<init>(java.lang.String)>`\n"
        result = self._extract(rst)
        assert "nablarch.fw.messaging.MessageSenderSettings" in result
        assert any("<init>" in f for f in result) is False

    def test_dedup(self):
        """Same FQCN appearing multiple times → returned once (set)."""
        rst = (
            ":java:extdoc:`A <nablarch.common.dao.UniversalDao>`\n"
            ":java:extdoc:`B <nablarch.common.dao.UniversalDao>`\n"
        )
        result = self._extract(rst)
        # result is a set — element appears exactly once
        assert sum(1 for f in result if f == "nablarch.common.dao.UniversalDao") == 1

    def test_multiple_fqcns(self):
        rst = (
            ":java:extdoc:`A <nablarch.common.dao.UniversalDao>`\n"
            ":java:extdoc:`B <nablarch.core.beans.BeanUtil>`\n"
        )
        result = self._extract(rst)
        assert "nablarch.common.dao.UniversalDao" in result
        assert "nablarch.core.beans.BeanUtil" in result


# ---------------------------------------------------------------------------
# fqcn_to_file_id
# ---------------------------------------------------------------------------

class TestFqcnToFileId:
    def _convert(self, fqcn):
        from scripts.create.javadoc import fqcn_to_file_id
        return fqcn_to_file_id(fqcn)

    def test_basic(self):
        assert self._convert("nablarch.common.dao.UniversalDao") == \
            "javadoc-nablarch-common-dao-UniversalDao"

    def test_deep_package(self):
        assert self._convert("nablarch.fw.messaging.MessageSenderSettings") == \
            "javadoc-nablarch-fw-messaging-MessageSenderSettings"


# ---------------------------------------------------------------------------
# _class_fqcn (helper)
# ---------------------------------------------------------------------------

class TestClassFqcn:
    def _convert(self, fqcn):
        from scripts.create.javadoc import _class_fqcn
        return _class_fqcn(fqcn)

    def test_plain_class(self):
        assert self._convert("nablarch.common.dao.UniversalDao") == \
            "nablarch.common.dao.UniversalDao"

    def test_hash_method_suffix(self):
        assert self._convert("nablarch.common.dao.UniversalDao#findById") == \
            "nablarch.common.dao.UniversalDao"

    def test_init_constructor_suffix(self):
        assert self._convert(
            "nablarch.fw.messaging.MessageSenderSettings.<init>(java.lang.String)"
        ) == "nablarch.fw.messaging.MessageSenderSettings"


# ---------------------------------------------------------------------------
# _parse_javadoc_md
# ---------------------------------------------------------------------------

SAMPLE_MD = textwrap.dedent("""\
    # class UniversalDao

    **パッケージ:** nablarch.common.dao

    ---

    ```java
    public class UniversalDao
    ```

    ユニバーサルDAOクラス。

    ## メソッドの詳細

    ### findById

    ```java
    public static <T> T findById(Class<T> entityClass, Object id)
    ```

    IDを指定してエンティティを検索する。
""")


class TestParseJavadocMd:
    def _parse(self, md_text, file_id="javadoc-nablarch-common-dao-UniversalDao"):
        from scripts.create.javadoc import _parse_javadoc_md
        return _parse_javadoc_md(md_text, file_id)

    def test_title(self):
        result = self._parse(SAMPLE_MD)
        assert result["title"] == "class UniversalDao"

    def test_id(self):
        result = self._parse(SAMPLE_MD)
        assert result["id"] == "javadoc-nablarch-common-dao-UniversalDao"

    def test_content_contains_description(self):
        result = self._parse(SAMPLE_MD)
        assert "ユニバーサルDAOクラス。" in result["content"]

    def test_sections_h2(self):
        result = self._parse(SAMPLE_MD)
        h2_titles = [s["title"] for s in result["sections"] if s["level"] == 2]
        assert "メソッドの詳細" in h2_titles

    def test_sections_h3(self):
        result = self._parse(SAMPLE_MD)
        h3_titles = [s["title"] for s in result["sections"] if s["level"] == 3]
        assert "findById" in h3_titles

    def test_h3_content_has_code(self):
        result = self._parse(SAMPLE_MD)
        findbyid = next(s for s in result["sections"] if s["title"] == "findById")
        assert "findById" in findbyid["content"]

    def test_sections_have_ids(self):
        result = self._parse(SAMPLE_MD)
        for i, s in enumerate(result["sections"], start=1):
            assert s["id"] == f"s{i}"

    def test_no_knowledge_content_false(self):
        result = self._parse(SAMPLE_MD)
        assert result.get("no_knowledge_content") is False
