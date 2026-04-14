"""Unit tests for Phase 5: Markdown converter."""
import pytest

from scripts.converters.md import convert


# ---------------------------------------------------------------------------
# Minimal inline fixtures
# ---------------------------------------------------------------------------

SIMPLE_MD = """\
# タイトル

前文テキスト。

## セクション1

セクション1の内容。

## セクション2

セクション2の内容。
"""

MD_WITH_H3 = """\
# タイトル

## 親セクション

親の内容。

### 子セクション

子の内容。
"""

MD_NO_H2 = """\
# タイトル

コンテンツのみ（セクション見出しなし）。
"""

MD_WITH_CODE = """\
# タイトル

## セクション

```java
public class Foo {}
```

インラインコード `foo` も使えます。
"""

MD_WITH_TABLE = """\
# タイトル

## セクション

| A | B |
|---|---|
| 1 | 2 |
"""

MD_WITH_IMAGE = """\
# タイトル

## セクション

![図](./images/diagram.png)

テキスト。
"""

MD_WITH_HTML_COMMENT = """\
# タイトル

## セクション

<!-- textlint-disable -->
内容。
<!-- textlint-enable -->
"""

MD_WITH_LINKS = """\
# タイトル

## セクション

[Nablarch](https://nablarch.github.io/docs/) を参照。
"""

MD_EMPTY_SECTIONS = """\
# タイトル

## セクション1

## セクション2

セクション2の内容。
"""


# ---------------------------------------------------------------------------
# Title extraction
# ---------------------------------------------------------------------------

class TestTitle:
    def test_extracts_h1_as_title(self):
        result = convert(SIMPLE_MD, "test-doc")
        assert result.title == "タイトル"

    def test_title_not_in_sections(self):
        result = convert(SIMPLE_MD, "test-doc")
        titles = [s.title for s in result.sections]
        assert "タイトル" not in titles

    def test_no_h1_uses_empty_title(self):
        md = "## セクション\n\n内容。\n"
        result = convert(md, "test-doc")
        assert result.title == ""


# ---------------------------------------------------------------------------
# Section splitting
# ---------------------------------------------------------------------------

class TestSectionSplitting:
    def test_h2_creates_sections(self):
        result = convert(SIMPLE_MD, "test-doc")
        titles = [s.title for s in result.sections]
        assert "セクション1" in titles
        assert "セクション2" in titles

    def test_h3_creates_sections(self):
        result = convert(MD_WITH_H3, "test-doc")
        titles = [s.title for s in result.sections]
        assert "子セクション" in titles

    def test_content_before_first_h2_becomes_preamble(self):
        result = convert(SIMPLE_MD, "test-doc")
        # First section is the preamble with pre-h2 content
        assert result.sections[0].content.strip() != ""
        assert "前文テキスト" in result.sections[0].content

    def test_no_h2_single_section(self):
        result = convert(MD_NO_H2, "test-doc")
        assert len(result.sections) == 1
        assert "コンテンツのみ" in result.sections[0].content

    def test_section_count(self):
        result = convert(SIMPLE_MD, "test-doc")
        # preamble + 2 h2 sections = 3
        assert len(result.sections) == 3

    def test_empty_section_preserved(self):
        result = convert(MD_EMPTY_SECTIONS, "test-doc")
        titles = [s.title for s in result.sections]
        assert "セクション1" in titles
        assert "セクション2" in titles


# ---------------------------------------------------------------------------
# Content preservation
# ---------------------------------------------------------------------------

class TestContentPreservation:
    def test_code_block_preserved(self):
        result = convert(MD_WITH_CODE, "test-doc")
        content = result.sections[-1].content
        assert "```java" in content
        assert "public class Foo" in content

    def test_inline_code_preserved(self):
        result = convert(MD_WITH_CODE, "test-doc")
        content = result.sections[-1].content
        assert "`foo`" in content

    def test_table_preserved(self):
        result = convert(MD_WITH_TABLE, "test-doc")
        content = result.sections[-1].content
        assert "| A | B |" in content

    def test_links_preserved(self):
        result = convert(MD_WITH_LINKS, "test-doc")
        content = result.sections[-1].content
        assert "[Nablarch]" in content
        assert "https://nablarch.github.io/docs/" in content

    def test_image_preserved(self):
        result = convert(MD_WITH_IMAGE, "test-doc")
        content = result.sections[-1].content
        assert "diagram.png" in content

    def test_html_comments_removed(self):
        result = convert(MD_WITH_HTML_COMMENT, "test-doc")
        content = result.sections[-1].content
        assert "textlint-disable" not in content
        assert "textlint-enable" not in content
        assert "内容。" in content


# ---------------------------------------------------------------------------
# no_knowledge_content flag
# ---------------------------------------------------------------------------

class TestNoKnowledgeContent:
    def test_normal_doc_not_flagged(self):
        result = convert(SIMPLE_MD, "test-doc")
        assert result.no_knowledge_content is False

    def test_readme_flagged(self):
        result = convert(SIMPLE_MD, "README")
        assert result.no_knowledge_content is True

    def test_changelog_flagged(self):
        result = convert(SIMPLE_MD, "CHANGELOG")
        assert result.no_knowledge_content is True
