"""Unit tests for classes.py — classes.md generation (Issue #368).

TDD: these tests are written BEFORE implementation. All tests must be RED
until scripts/create/classes.py is created.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.create.classes import generate_classes_md

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_json(knowledge_dir: Path, output_path: str, data: dict) -> None:
    p = knowledge_dir / output_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _jaxrs_page(classes: list[str]) -> dict:
    """Build a component JSON whose content contains Javadoc links for given class names."""
    content = " ".join(
        f"[{cls}](../../javadoc/javadoc-{cls}.json)" for cls in classes
    )
    return {
        "id": "adapters-jaxrs-adaptor",
        "title": "Jakarta RESTful Web Servicesアダプタ",
        "no_knowledge_content": False,
        "content": content,
        "sections": [],
    }


# ---------------------------------------------------------------------------
# TestGenerateClassesMdHeader
# ---------------------------------------------------------------------------

class TestGenerateClassesMdHeader:
    """classes.md starts with # Class Index header."""

    def test_header_written(self, tmp_path):
        """Output file starts with '# Class Index'."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/a.json", _jaxrs_page(["FooConverter"]))
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert text.startswith("# Class Index\n")


# ---------------------------------------------------------------------------
# TestGenerateClassesMdTargetCategories
# ---------------------------------------------------------------------------

class TestGenerateClassesMdTargetCategories:
    """Only component, processing-pattern, development-tools categories are scanned."""

    def test_component_included(self, tmp_path):
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/a.json", _jaxrs_page(["ConverterA"]))
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "ConverterA" in text

    def test_processing_pattern_included(self, tmp_path):
        kn = tmp_path / "knowledge"
        _write_json(kn, "processing-pattern/web/b.json", _jaxrs_page(["ActionB"]))
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "ActionB" in text

    def test_development_tools_included(self, tmp_path):
        kn = tmp_path / "knowledge"
        _write_json(kn, "development-tools/testing/c.json", _jaxrs_page(["ToolC"]))
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "ToolC" in text

    def test_other_category_excluded(self, tmp_path):
        """Categories outside the 3 targets produce no entry."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "getting-started/intro/d.json", _jaxrs_page(["StartupClass"]))
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "StartupClass" not in text

    def test_check_category_excluded(self, tmp_path):
        """check/ category (Excel origin) is not scanned."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "check/security/e.json", _jaxrs_page(["CheckClass"]))
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "CheckClass" not in text


# ---------------------------------------------------------------------------
# TestGenerateClassesMdClassExtraction
# ---------------------------------------------------------------------------

class TestGenerateClassesMdClassExtraction:
    """Class name extraction from Javadoc link patterns."""

    def test_plain_class_name_extracted(self, tmp_path):
        """[ClassName](../../javadoc/javadoc-*.json) → ClassName listed."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/a.json", {
            "id": "a", "title": "T", "no_knowledge_content": False,
            "content": "[Jackson2BodyConverter](../../javadoc/javadoc-Jackson2BodyConverter.json)",
            "sections": [],
        })
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "- Jackson2BodyConverter" in text

    def test_hash_suffix_stripped(self, tmp_path):
        """[ClassName#method](../../javadoc/...) → only ClassName kept."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/a.json", {
            "id": "a", "title": "T", "no_knowledge_content": False,
            "content": "[JaxRsMethodBinderFactory#handlerList](../../javadoc/javadoc-x.json)",
            "sections": [],
        })
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "- JaxRsMethodBinderFactory" in text
        assert "#handlerList" not in text

    def test_classes_in_sections_extracted(self, tmp_path):
        """Javadoc links in sections[].content are also extracted."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/a.json", {
            "id": "a", "title": "T", "no_knowledge_content": False,
            "content": "",
            "sections": [
                {
                    "id": "s1", "title": "Section",
                    "content": "[SectionClass](../../javadoc/javadoc-SectionClass.json)",
                    "level": 2,
                }
            ],
        })
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "- SectionClass" in text

    def test_duplicate_classes_deduped(self, tmp_path):
        """Same class name appearing multiple times in one page listed once."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/a.json", {
            "id": "a", "title": "T", "no_knowledge_content": False,
            "content": (
                "[Dup](../../javadoc/javadoc-Dup.json) "
                "[Dup](../../javadoc/javadoc-Dup.json)"
            ),
            "sections": [],
        })
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert text.count("- Dup") == 1

    def test_occurrence_order_preserved(self, tmp_path):
        """Class names appear in the order they first occur on the page."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/a.json", {
            "id": "a", "title": "T", "no_knowledge_content": False,
            "content": (
                "[Alpha](../../javadoc/javadoc-Alpha.json) "
                "[Beta](../../javadoc/javadoc-Beta.json)"
            ),
            "sections": [],
        })
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert text.index("- Alpha") < text.index("- Beta")

    def test_non_javadoc_link_not_extracted(self, tmp_path):
        """Links not matching ../../javadoc/javadoc-*.json pattern are ignored."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/a.json", {
            "id": "a", "title": "T", "no_knowledge_content": False,
            "content": "[SomeText](../../other/file.json)",
            "sections": [],
        })
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        # No page block should be emitted (zero classes → page skipped)
        assert "### T" not in text


# ---------------------------------------------------------------------------
# TestGenerateClassesMdSkipRules
# ---------------------------------------------------------------------------

class TestGenerateClassesMdSkipRules:
    """Skip rules: no_knowledge_content, zero-class pages, assets/, javadoc/."""

    def test_no_knowledge_content_skipped(self, tmp_path):
        """Pages with no_knowledge_content: true are not listed."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/a.json", {
            "id": "a", "title": "Skip", "no_knowledge_content": True,
            "content": "[SkipClass](../../javadoc/javadoc-SkipClass.json)",
            "sections": [],
        })
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "SkipClass" not in text

    def test_zero_class_page_not_listed(self, tmp_path):
        """Pages with no Javadoc links produce no H3 entry."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/a.json", {
            "id": "a", "title": "NoClasses", "no_knowledge_content": False,
            "content": "Some text without any javadoc links.",
            "sections": [],
        })
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "### NoClasses" not in text

    def test_assets_dir_skipped(self, tmp_path):
        """Files under assets/ are not scanned."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/assets/x.json", _jaxrs_page(["AssetClass"]))
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "AssetClass" not in text

    def test_javadoc_dir_skipped(self, tmp_path):
        """Files under javadoc/ are not scanned."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/javadoc/javadoc-Foo.json", {
            "id": "javadoc-Foo", "title": "class Foo", "no_knowledge_content": False,
            "content": "[Foo](../../javadoc/javadoc-Foo.json)",
            "sections": [],
        })
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "class Foo" not in text


# ---------------------------------------------------------------------------
# TestGenerateClassesMdFormat
# ---------------------------------------------------------------------------

class TestGenerateClassesMdFormat:
    """Output format: H2=category, H3=title, path: line, - ClassName lines."""

    def test_h2_is_first_path_component(self, tmp_path):
        """H2 heading matches the first path component (top-level category)."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/a.json", _jaxrs_page(["C"]))
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "## component" in text

    def test_h3_is_page_title(self, tmp_path):
        """H3 heading is the JSON title field."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/a.json", {
            "id": "a", "title": "Jakarta RESTful Web Servicesアダプタ",
            "no_knowledge_content": False,
            "content": "[C](../../javadoc/javadoc-C.json)",
            "sections": [],
        })
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "### Jakarta RESTful Web Servicesアダプタ" in text

    def test_path_line_format(self, tmp_path):
        """path: line uses relative path from knowledge_dir."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/adapters-jaxrs-adaptor.json", _jaxrs_page(["C"]))
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "path: component/adapters/adapters-jaxrs-adaptor.json" in text

    def test_class_name_list_item_format(self, tmp_path):
        """Each class name is a `- ClassName` list item."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/a.json", _jaxrs_page(["Jackson2BodyConverter", "JaxbBodyConverter"]))
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "- Jackson2BodyConverter" in text
        assert "- JaxbBodyConverter" in text

    def test_full_page_block_structure(self, tmp_path):
        """A complete page block matches the spec example."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/adapters-jaxrs-adaptor.json", {
            "id": "adapters-jaxrs-adaptor",
            "title": "Jakarta RESTful Web Servicesアダプタ",
            "no_knowledge_content": False,
            "content": (
                "[Jackson2BodyConverter](../../javadoc/javadoc-Jackson2BodyConverter.json) "
                "[JaxbBodyConverter](../../javadoc/javadoc-JaxbBodyConverter.json) "
                "[FormUrlEncodedConverter](../../javadoc/javadoc-FormUrlEncodedConverter.json)"
            ),
            "sections": [],
        })
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        expected_block = (
            "## component\n"
            "\n"
            "### Jakarta RESTful Web Servicesアダプタ\n"
            "path: component/adapters/adapters-jaxrs-adaptor.json\n"
            "- Jackson2BodyConverter\n"
            "- JaxbBodyConverter\n"
            "- FormUrlEncodedConverter\n"
        )
        assert expected_block in text


# ---------------------------------------------------------------------------
# TestGenerateClassesMdOrdering
# ---------------------------------------------------------------------------

class TestGenerateClassesMdOrdering:
    """Files within a category are sorted by path (deterministic output)."""

    def test_files_sorted_by_path(self, tmp_path):
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/zzz.json", _jaxrs_page(["ZClass"]))
        _write_json(kn, "component/adapters/aaa.json", _jaxrs_page(["AClass"]))
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert text.index("AClass") < text.index("ZClass")


# ---------------------------------------------------------------------------
# TestGenerateClassesMdNoJavadocVersion
# ---------------------------------------------------------------------------

class TestGenerateClassesMdNoJavadocVersion:
    """Versions with zero Javadoc links emit fixed message only."""

    def test_fixed_message_when_no_classes(self, tmp_path):
        """When no page has any class, the fixed no-javadoc message is written."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/a.json", {
            "id": "a", "title": "NoClassPage", "no_knowledge_content": False,
            "content": "Plain text, no javadoc links.",
            "sections": [],
        })
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "_No class index available for this version (no Javadoc references in knowledge files)._" in text

    def test_no_h2_when_no_classes(self, tmp_path):
        """When no classes found, no H2/H3 category blocks are written."""
        kn = tmp_path / "knowledge"
        _write_json(kn, "component/adapters/a.json", {
            "id": "a", "title": "NoClassPage", "no_knowledge_content": False,
            "content": "Plain text.",
            "sections": [],
        })
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "## component" not in text

    def test_empty_knowledge_dir(self, tmp_path):
        """Empty knowledge dir also emits fixed message."""
        kn = tmp_path / "knowledge"
        kn.mkdir()
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert "# Class Index" in text
        assert "_No class index available for this version (no Javadoc references in knowledge files)._" in text

    def test_header_present_in_no_class_version(self, tmp_path):
        """Even with fixed message, # Class Index header must be present."""
        kn = tmp_path / "knowledge"
        kn.mkdir()
        out = tmp_path / "classes.md"
        generate_classes_md(kn, out)
        text = out.read_text(encoding="utf-8")
        assert text.startswith("# Class Index\n")
