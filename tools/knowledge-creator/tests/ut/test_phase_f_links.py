"""Tests for Phase F: RST link resolution integrated into Phase F."""
import os
import pytest
from common import write_json, load_json


def _make_catalog(files):
    return {
        "version": "6",
        "generated_at": "2026-01-01T00:00:00Z",
        "files": files,
    }


def _file_entry(id_, type_="component", category="handlers", source_path=None,
                section_map=None, split_info=None):
    entry = {
        "id": id_,
        "source_path": source_path or f"test/{id_}.rst",
        "format": "rst",
        "filename": f"{id_}.rst",
        "type": type_,
        "category": category,
        "output_path": f"{type_}/{category}/{id_}.json",
        "assets_dir": f"{type_}/{category}/assets/{id_}/",
    }
    if section_map is not None:
        entry["section_map"] = section_map
    if split_info is not None:
        entry["split_info"] = split_info
    return entry


def _write_knowledge(ctx, type_, category, id_, index, sections,
                     official_doc_urls=None):
    path = f"{ctx.knowledge_dir}/{type_}/{category}/{id_}.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = {
        "id": id_,
        "title": id_.replace("-", " ").title(),
        "official_doc_urls": official_doc_urls or [],
        "index": index,
        "sections": sections,
    }
    write_json(path, data)
    return path


class TestBuildLinkMaps:
    """_build_link_maps: label/doc/type-category maps built correctly."""

    def test_label_map_from_section_map(self, ctx):
        """Labels in section_map are indexed to (file_id, section_id)."""
        from phase_f_finalize import PhaseFFinalize

        # Knowledge file with matching heading
        _write_knowledge(ctx, "component", "handlers", "file-a",
                         index=[{"id": "s1", "title": "Overview", "hints": []}],
                         sections={"s1": "content"})

        catalog = _make_catalog([
            _file_entry("file-a", section_map=[
                {"section_id": "s1", "heading": "Overview", "rst_labels": ["file_a_overview"]}
            ])
        ])
        pf = PhaseFFinalize(ctx, dry_run=True, catalog_for_links=catalog)
        pf._build_link_maps()

        assert "file_a_overview" in pf.label_map
        file_id, section_id = pf.label_map["file_a_overview"]
        assert file_id == "file-a"
        assert section_id == "s1"

    def test_label_map_underscore_hyphen_variants(self, ctx):
        """Both underscore and hyphen variants of labels are indexed."""
        from phase_f_finalize import PhaseFFinalize

        _write_knowledge(ctx, "component", "handlers", "file-b",
                         index=[{"id": "s1", "title": "Section", "hints": []}],
                         sections={"s1": "content"})

        catalog = _make_catalog([
            _file_entry("file-b", section_map=[
                {"section_id": "s1", "heading": "Section", "rst_labels": ["file_b_label"]}
            ])
        ])
        pf = PhaseFFinalize(ctx, dry_run=True, catalog_for_links=catalog)
        pf._build_link_maps()

        # Both underscore and hyphen variants should be registered
        assert "file_b_label" in pf.label_map
        assert "file-b-label" in pf.label_map

    def test_label_map_no_matching_heading_uses_none(self, ctx):
        """When heading doesn't match index title, section_id is None."""
        from phase_f_finalize import PhaseFFinalize

        _write_knowledge(ctx, "component", "handlers", "file-c",
                         index=[{"id": "s1", "title": "Actual Title", "hints": []}],
                         sections={"s1": "content"})

        catalog = _make_catalog([
            _file_entry("file-c", section_map=[
                {"section_id": "s1", "heading": "Non-Matching Heading",
                 "rst_labels": ["file_c_label"]}
            ])
        ])
        pf = PhaseFFinalize(ctx, dry_run=True, catalog_for_links=catalog)
        pf._build_link_maps()

        assert "file_c_label" in pf.label_map
        _, section_id = pf.label_map["file_c_label"]
        assert section_id is None

    def test_doc_map_from_source_path(self, ctx):
        """source_path is indexed to file_id."""
        from phase_f_finalize import PhaseFFinalize

        catalog = _make_catalog([
            _file_entry("file-d", source_path="application_framework/config/database.rst")
        ])
        pf = PhaseFFinalize(ctx, dry_run=True, catalog_for_links=catalog)
        pf._build_link_maps()

        assert "application_framework/config/database" in pf.doc_map
        assert pf.doc_map["application_framework/config/database"] == "file-d"
        # Partial path
        assert "config/database" in pf.doc_map
        assert "database" in pf.doc_map

    def test_file_type_category_populated(self, ctx):
        """file_type_category maps file_id to (type, category)."""
        from phase_f_finalize import PhaseFFinalize

        catalog = _make_catalog([
            _file_entry("file-e", type_="component", category="handlers")
        ])
        pf = PhaseFFinalize(ctx, dry_run=True, catalog_for_links=catalog)
        pf._build_link_maps()

        assert pf.file_type_category["file-e"] == ("component", "handlers")

    def test_split_entries_use_original_id(self, ctx):
        """Split catalog entries are indexed under original_id."""
        from phase_f_finalize import PhaseFFinalize

        _write_knowledge(ctx, "component", "handlers", "multi",
                         index=[{"id": "s1", "title": "Part A", "hints": []}],
                         sections={"s1": "content"})

        catalog = _make_catalog([
            _file_entry("multi--s1", section_map=[
                {"section_id": "s1", "heading": "Part A", "rst_labels": ["multi_label"]}
            ], split_info={"is_split": True, "original_id": "multi", "part": 1, "total_parts": 1})
        ])
        pf = PhaseFFinalize(ctx, dry_run=True, catalog_for_links=catalog)
        pf._build_link_maps()

        assert "multi_label" in pf.label_map
        file_id, _ = pf.label_map["multi_label"]
        assert file_id == "multi"


class TestResolveRstLinks:
    """_resolve_rst_links: correct output for each RST link type."""

    def _make_pf(self, ctx):
        from phase_f_finalize import PhaseFFinalize
        pf = PhaseFFinalize(ctx, dry_run=True)
        pf.label_map = {
            "internal_label": ("current-file", "s1"),
            "external_label": ("other-file", "s2"),
            "external_no_section": ("other-file", None),
            "external_label-hyphen": ("other-file", "s2"),
        }
        pf.doc_map = {
            "path/to/other": "other-file",
        }
        pf.file_type_category = {
            "current-file": ("component", "handlers"),
            "other-file": ("component", "adapters"),
        }
        return pf

    def test_ref_internal_same_file_skill_json(self, ctx):
        """:ref: to same file → #section_id."""
        pf = self._make_pf(ctx)
        result = pf._resolve_rst_links(":ref:`internal_label`", "current-file", "skill_json")
        assert result == "[internal_label](#s1)"

    def test_ref_internal_with_display_text(self, ctx):
        """:ref:`display <label>` uses custom display text."""
        pf = self._make_pf(ctx)
        result = pf._resolve_rst_links(":ref:`概要 <internal_label>`", "current-file", "skill_json")
        assert result == "[概要](#s1)"

    def test_ref_external_skill_json(self, ctx):
        """:ref: to different file → file_id.json#section_id."""
        pf = self._make_pf(ctx)
        result = pf._resolve_rst_links(":ref:`external_label`", "current-file", "skill_json")
        assert result == "[external_label](../adapters/other-file.json#s2)"

    def test_ref_external_skill_json_no_section(self, ctx):
        """:ref: to different file with no section → file_id.json."""
        pf = self._make_pf(ctx)
        result = pf._resolve_rst_links(":ref:`external_no_section`", "current-file", "skill_json")
        assert result == "[external_no_section](../adapters/other-file.json)"

    def test_ref_external_docs_md(self, ctx):
        """:ref: to different file in docs_md → relative MD path."""
        pf = self._make_pf(ctx)
        result = pf._resolve_rst_links(":ref:`external_label`", "current-file", "docs_md")
        # From docs/component/handlers to docs/component/adapters/other-file.md
        assert "other-file.md#s2" in result
        assert result.startswith("[external_label](")

    def test_ref_unresolved_kept_as_is(self, ctx):
        """Unresolvable :ref: is kept as-is."""
        pf = self._make_pf(ctx)
        result = pf._resolve_rst_links(":ref:`unknown_label`", "current-file", "skill_json")
        assert result == ":ref:`unknown_label`"

    def test_doc_link_skill_json(self, ctx):
        """:doc: resolves to file_id.json."""
        pf = self._make_pf(ctx)
        result = pf._resolve_rst_links(":doc:`path/to/other`", "current-file", "skill_json")
        assert result == "[path/to/other](../adapters/other-file.json)"

    def test_doc_link_with_display_text(self, ctx):
        """:doc:`display <path>` uses custom display text."""
        pf = self._make_pf(ctx)
        result = pf._resolve_rst_links(":doc:`Other Doc <path/to/other>`", "current-file", "skill_json")
        assert result == "[Other Doc](../adapters/other-file.json)"

    def test_doc_link_unresolved(self, ctx):
        """Unresolvable :doc: is kept as-is."""
        pf = self._make_pf(ctx)
        result = pf._resolve_rst_links(":doc:`unknown/path`", "current-file", "skill_json")
        assert result == ":doc:`unknown/path`"

    def test_download_link_skill_json(self, ctx):
        """:download: resolves to assets path in skill_json."""
        pf = self._make_pf(ctx)
        result = pf._resolve_rst_links(":download:`schema <files/schema.xsd>`", "current-file", "skill_json")
        assert result == "[schema](assets/current-file/schema.xsd)"

    def test_download_link_docs_md(self, ctx):
        """:download: resolves to ../../../knowledge/.../assets/ in docs_md."""
        pf = self._make_pf(ctx)
        result = pf._resolve_rst_links(":download:`schema <files/schema.xsd>`", "current-file", "docs_md")
        assert "schema.xsd" in result
        assert "../../../knowledge/component/handlers/assets/current-file/schema.xsd" in result

    def test_download_unsafe_path_kept(self, ctx):
        """:download: with path traversal is kept as-is."""
        pf = self._make_pf(ctx)
        result = pf._resolve_rst_links(":download:`file <../etc/passwd>`", "current-file", "skill_json")
        assert ":download:" in result

    def test_java_extdoc_simple(self, ctx):
        """:java:extdoc: resolves to inline code with class name."""
        pf = self._make_pf(ctx)
        result = pf._resolve_rst_links(
            ":java:extdoc:`SampleHandler <nablarch.fw.SampleHandler>`",
            "current-file", "skill_json"
        )
        assert result == "`SampleHandler`"

    def test_java_extdoc_plain(self, ctx):
        """:java:extdoc:`class` → inline code with simple class name."""
        pf = self._make_pf(ctx)
        result = pf._resolve_rst_links(
            ":java:extdoc:`nablarch.fw.SampleHandler`",
            "current-file", "skill_json"
        )
        assert result == "`SampleHandler`"


class TestAssetPathBugFix:
    """_convert_asset_paths: uses ../../../knowledge/ (3 levels up, not 2)."""

    def test_image_path_uses_three_levels(self, ctx):
        """Asset image path uses ../../../knowledge/."""
        from phase_f_finalize import PhaseFFinalize
        pf = PhaseFFinalize(ctx, dry_run=True)
        fi = {"id": "my-handler", "type": "component", "category": "handlers"}
        content = "![diagram](assets/my-handler/diagram.png)"
        result = pf._convert_asset_paths(content, fi)
        assert "../../../knowledge/component/handlers/assets/my-handler/diagram.png" in result
        # Should be 3 levels (../../../), not 2 levels (../../)
        assert result.count("../") == 3

    def test_link_path_uses_three_levels(self, ctx):
        """Asset download link path uses ../../../knowledge/."""
        from phase_f_finalize import PhaseFFinalize
        pf = PhaseFFinalize(ctx, dry_run=True)
        fi = {"id": "my-handler", "type": "component", "category": "handlers"}
        content = "[download](assets/my-handler/schema.xsd)"
        result = pf._convert_asset_paths(content, fi)
        assert "../../../knowledge/component/handlers/assets/my-handler/schema.xsd" in result
        assert result.count("../") == 3


class TestGenerateSkillJson:
    """_generate_skill_json: skill JSON files are generated with resolved links."""

    def test_skill_json_links_resolved(self, ctx, mock_claude):
        """Skill JSON sections have RST links resolved."""
        from phase_f_finalize import PhaseFFinalize

        # Set up knowledge file with RST links
        _write_knowledge(ctx, "component", "handlers", "handler-a",
                         index=[{"id": "s1", "title": "Overview", "hints": []}],
                         sections={"s1": ":java:extdoc:`nablarch.fw.Handler` is used here."})

        catalog = _make_catalog([_file_entry("handler-a")])
        write_json(ctx.classified_list_path, catalog)

        pf = PhaseFFinalize(ctx, dry_run=False, catalog_for_links=catalog)
        pf._build_link_maps()
        pf._generate_skill_json()

        result = load_json(f"{ctx.knowledge_dir}/component/handlers/handler-a.json")
        assert ":java:extdoc:" not in result["sections"]["s1"]
        assert "`Handler`" in result["sections"]["s1"]


class TestIndexToonFromCatalog:
    """_build_index_toon: processing_patterns read from catalog, not knowledge JSON."""

    def test_catalog_pp_used_not_knowledge_pp(self, ctx):
        """index.toon uses processing_patterns from catalog entry."""
        from phase_f_finalize import PhaseFFinalize

        _write_knowledge(ctx, "component", "handlers", "handler-b",
                         index=[{"id": "s1", "title": "Handler B", "hints": []}],
                         sections={"s1": "content"})

        # Catalog has processing_patterns, knowledge JSON does NOT
        catalog = _make_catalog([{
            **_file_entry("handler-b"),
            "processing_patterns": ["restful-web-service"],
        }])
        write_json(ctx.classified_list_path, catalog)

        pf = PhaseFFinalize(ctx, dry_run=False, catalog_for_links=catalog)
        pf._build_link_maps()
        pf._build_index_toon()

        toon = open(ctx.index_path).read()
        assert "restful-web-service" in toon

    def test_processing_pattern_type_uses_category(self, ctx):
        """For type=processing-pattern, category value is used as patterns."""
        from phase_f_finalize import PhaseFFinalize

        _write_knowledge(ctx, "processing-pattern", "nablarch-batch", "nablarch-batch",
                         index=[{"id": "s1", "title": "Batch", "hints": []}],
                         sections={"s1": "batch content"})

        catalog = _make_catalog([_file_entry("nablarch-batch", type_="processing-pattern",
                                              category="nablarch-batch")])
        write_json(ctx.classified_list_path, catalog)

        pf = PhaseFFinalize(ctx, dry_run=False, catalog_for_links=catalog)
        pf._build_link_maps()
        pf._build_index_toon()

        toon = open(ctx.index_path).read()
        assert "nablarch-batch" in toon
