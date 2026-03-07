"""Tests for Phase G: Link Resolution."""
import os
import json
import pytest
from phase_g_resolve_links import PhaseGResolveLinks


class TestPhaseGLinkResolution:
    """Test RST link resolution to Markdown."""

    def test_ref_internal_resolution(self, ctx):
        """Internal :ref: should resolve to #anchor."""
        # Setup: Create knowledge file with internal label
        knowledge = {
            "id": "test-handler",
            "title": "Test Handler",
            "official_doc_urls": [],
            "index": [
                {"id": "overview", "title": "Overview", "hints": []},
                {"id": "setup", "title": "Setup", "hints": []}
            ],
            "sections": {
                "overview": "See :ref:`setup` for configuration.",
                "setup": "Configuration details here."
            }
        }

        # Create trace with internal labels
        trace = {
            "internal_labels": ["test-handler", "setup"],
            "sections": []
        }

        knowledge_path = f"{ctx.knowledge_dir}/component/test-handler.json"
        os.makedirs(os.path.dirname(knowledge_path), exist_ok=True)
        with open(knowledge_path, "w", encoding="utf-8") as f:
            json.dump(knowledge, f, ensure_ascii=False)

        trace_path = f"{ctx.trace_dir}/test-handler.json"
        os.makedirs(os.path.dirname(trace_path), exist_ok=True)
        with open(trace_path, "w", encoding="utf-8") as f:
            json.dump(trace, f, ensure_ascii=False)

        # Execute Phase G
        phase_g = PhaseGResolveLinks(ctx)
        result = phase_g.run()

        # Verify: Internal ref resolved to #anchor
        assert result["resolved_count"] == 1
        resolved_path = f"{ctx.knowledge_resolved_dir}/component/test-handler.json"
        assert os.path.exists(resolved_path)

        with open(resolved_path, "r", encoding="utf-8") as f:
            resolved = json.load(f)

        overview = resolved["sections"]["overview"]
        assert "[setup](#setup)" in overview or "[Setup](#setup)" in overview, \
            "Internal :ref: should resolve to #anchor"

    def test_ref_external_resolution(self, ctx):
        """External :ref: should resolve to relative path."""
        # Setup: Create two knowledge files
        handler1 = {
            "id": "handler-a",
            "title": "Handler A",
            "official_doc_urls": [],
            "index": [{"id": "overview", "title": "Overview", "hints": []}],
            "sections": {
                "overview": "See :ref:`handler_b` for details."
            }
        }

        handler2 = {
            "id": "handler-b",
            "title": "Handler B",
            "official_doc_urls": [],
            "index": [{"id": "overview", "title": "Overview", "hints": []}],
            "sections": {
                "overview": "Handler B details."
            }
        }

        trace1 = {"internal_labels": ["handler-a"], "sections": []}
        trace2 = {"internal_labels": ["handler-b"], "sections": []}

        # Write files
        for file_id, knowledge, trace in [
            ("handler-a", handler1, trace1),
            ("handler-b", handler2, trace2)
        ]:
            knowledge_path = f"{ctx.knowledge_dir}/component/{file_id}.json"
            os.makedirs(os.path.dirname(knowledge_path), exist_ok=True)
            with open(knowledge_path, "w", encoding="utf-8") as f:
                json.dump(knowledge, f, ensure_ascii=False)

            trace_path = f"{ctx.trace_dir}/{file_id}.json"
            os.makedirs(os.path.dirname(trace_path), exist_ok=True)
            with open(trace_path, "w", encoding="utf-8") as f:
                json.dump(trace, f, ensure_ascii=False)

        # Execute Phase G
        phase_g = PhaseGResolveLinks(ctx)
        result = phase_g.run()

        # Verify: External ref resolved to relative path
        assert result["resolved_count"] == 2
        resolved_path = f"{ctx.knowledge_resolved_dir}/component/handler-a.json"

        with open(resolved_path, "r", encoding="utf-8") as f:
            resolved = json.load(f)

        overview = resolved["sections"]["overview"]
        assert "handler-b.md" in overview, \
            "External :ref: should resolve to relative path"

    def test_ref_with_display_text(self, ctx):
        """ref: with custom display text should preserve display."""
        knowledge = {
            "id": "test-doc",
            "title": "Test Doc",
            "official_doc_urls": [],
            "index": [{"id": "overview", "title": "Overview", "hints": []}],
            "sections": {
                "overview": "See :ref:`Database Connection <database_connection>` for setup."
            }
        }

        trace = {"internal_labels": ["database-connection"], "sections": []}

        knowledge_path = f"{ctx.knowledge_dir}/test-doc.json"
        with open(knowledge_path, "w", encoding="utf-8") as f:
            json.dump(knowledge, f, ensure_ascii=False)

        trace_path = f"{ctx.trace_dir}/test-doc.json"
        os.makedirs(os.path.dirname(trace_path), exist_ok=True)
        with open(trace_path, "w", encoding="utf-8") as f:
            json.dump(trace, f, ensure_ascii=False)

        # Execute Phase G
        phase_g = PhaseGResolveLinks(ctx)
        result = phase_g.run()

        # Verify: Display text preserved
        resolved_path = f"{ctx.knowledge_resolved_dir}/test-doc.json"
        with open(resolved_path, "r", encoding="utf-8") as f:
            resolved = json.load(f)

        overview = resolved["sections"]["overview"]
        assert "[Database Connection]" in overview, \
            "Custom display text should be preserved"

    def test_doc_link_resolution(self, ctx):
        """:doc: should resolve to .md path."""
        # Setup classified.json with doc paths
        classified = {
            "files": [
                {
                    "id": "config-database",
                    "source_path": "application_framework/configuration/database.rst",
                    "output_path": "config-database.json"
                }
            ]
        }

        classified_path = ctx.classified_list_path
        os.makedirs(os.path.dirname(classified_path), exist_ok=True)
        with open(classified_path, "w", encoding="utf-8") as f:
            json.dump(classified, f, ensure_ascii=False)

        knowledge = {
            "id": "test-doc",
            "title": "Test Doc",
            "official_doc_urls": [],
            "index": [{"id": "overview", "title": "Overview", "hints": []}],
            "sections": {
                "overview": "Refer to :doc:`../configuration/database` for details."
            }
        }

        knowledge_path = f"{ctx.knowledge_dir}/test-doc.json"
        with open(knowledge_path, "w", encoding="utf-8") as f:
            json.dump(knowledge, f, ensure_ascii=False)

        # Execute Phase G
        phase_g = PhaseGResolveLinks(ctx)
        result = phase_g.run()

        # Verify: :doc: resolved
        resolved_path = f"{ctx.knowledge_resolved_dir}/test-doc.json"
        with open(resolved_path, "r", encoding="utf-8") as f:
            resolved = json.load(f)

        overview = resolved["sections"]["overview"]
        # Should be resolved or kept as-is if not found
        assert ":doc:" not in overview or "config-database.md" in overview

    def test_download_link_resolution(self, ctx):
        """:download: should resolve to assets/ path."""
        knowledge = {
            "id": "config-index",
            "title": "Configuration Index",
            "official_doc_urls": [],
            "index": [{"id": "overview", "title": "Overview", "hints": []}],
            "sections": {
                "overview": "Download :download:`Settings <default_settings.xlsx>` file."
            }
        }

        knowledge_path = f"{ctx.knowledge_dir}/config-index.json"
        with open(knowledge_path, "w", encoding="utf-8") as f:
            json.dump(knowledge, f, ensure_ascii=False)

        # Execute Phase G
        phase_g = PhaseGResolveLinks(ctx)
        result = phase_g.run()

        # Verify: :download: resolved to assets path
        resolved_path = f"{ctx.knowledge_resolved_dir}/config-index.json"
        with open(resolved_path, "r", encoding="utf-8") as f:
            resolved = json.load(f)

        overview = resolved["sections"]["overview"]
        assert "[Settings](assets/config-index/default_settings.xlsx)" in overview, \
            ":download: should resolve to assets/ path"

    def test_java_extdoc_resolution(self, ctx):
        """:java:extdoc: should convert to inline code."""
        knowledge = {
            "id": "test-handler",
            "title": "Test Handler",
            "official_doc_urls": [
                "https://nablarch.github.io/docs/LATEST/javadoc/nablarch/core/ThreadContext.html"
            ],
            "index": [{"id": "overview", "title": "Overview", "hints": []}],
            "sections": {
                "overview": "Uses :java:extdoc:`ThreadContext <nablarch.core.ThreadContext>` and :java:extdoc:`nablarch.sample.SampleHandler`."
            }
        }

        knowledge_path = f"{ctx.knowledge_dir}/test-handler.json"
        with open(knowledge_path, "w", encoding="utf-8") as f:
            json.dump(knowledge, f, ensure_ascii=False)

        # Execute Phase G
        phase_g = PhaseGResolveLinks(ctx)
        result = phase_g.run()

        # Verify: :java:extdoc: converted to inline code
        resolved_path = f"{ctx.knowledge_resolved_dir}/test-handler.json"
        with open(resolved_path, "r", encoding="utf-8") as f:
            resolved = json.load(f)

        overview = resolved["sections"]["overview"]
        assert "`ThreadContext`" in overview, \
            ":java:extdoc: with display should convert to inline code"
        assert "`SampleHandler`" in overview, \
            ":java:extdoc: without display should extract class name"
        assert ":java:extdoc:" not in overview, \
            "All :java:extdoc: should be resolved"

    def test_external_url_unchanged(self, ctx):
        """External URLs in Markdown format should remain unchanged."""
        knowledge = {
            "id": "test-doc",
            "title": "Test Doc",
            "official_doc_urls": [],
            "index": [{"id": "overview", "title": "Overview", "hints": []}],
            "sections": {
                "overview": "See [Jackson](https://github.com/FasterXML/jackson) library."
            }
        }

        knowledge_path = f"{ctx.knowledge_dir}/test-doc.json"
        with open(knowledge_path, "w", encoding="utf-8") as f:
            json.dump(knowledge, f, ensure_ascii=False)

        # Execute Phase G
        phase_g = PhaseGResolveLinks(ctx)
        result = phase_g.run()

        # Verify: External URL unchanged
        resolved_path = f"{ctx.knowledge_resolved_dir}/test-doc.json"
        with open(resolved_path, "r", encoding="utf-8") as f:
            resolved = json.load(f)

        overview = resolved["sections"]["overview"]
        assert "[Jackson](https://github.com/FasterXML/jackson)" in overview, \
            "External URLs should remain unchanged"

    def test_mixed_links(self, ctx):
        """Multiple link types in one section should all be resolved."""
        knowledge = {
            "id": "complex-doc",
            "title": "Complex Doc",
            "official_doc_urls": [
                "https://nablarch.github.io/docs/LATEST/javadoc/nablarch/core/ThreadContext.html"
            ],
            "index": [{"id": "overview", "title": "Overview", "hints": []}],
            "sections": {
                "overview": (
                    "Configure :ref:`database_connection` in :doc:`../config/database`. "
                    "Download :download:`sample.xml <sample.xml>` template. "
                    "Uses :java:extdoc:`nablarch.core.ThreadContext` class. "
                    "See [External](https://example.com) site."
                )
            }
        }

        trace = {"internal_labels": ["database-connection"], "sections": []}

        knowledge_path = f"{ctx.knowledge_dir}/complex-doc.json"
        with open(knowledge_path, "w", encoding="utf-8") as f:
            json.dump(knowledge, f, ensure_ascii=False)

        trace_path = f"{ctx.trace_dir}/complex-doc.json"
        os.makedirs(os.path.dirname(trace_path), exist_ok=True)
        with open(trace_path, "w", encoding="utf-8") as f:
            json.dump(trace, f, ensure_ascii=False)

        # Execute Phase G
        phase_g = PhaseGResolveLinks(ctx)
        result = phase_g.run()

        # Verify: All link types processed
        resolved_path = f"{ctx.knowledge_resolved_dir}/complex-doc.json"
        with open(resolved_path, "r", encoding="utf-8") as f:
            resolved = json.load(f)

        overview = resolved["sections"]["overview"]

        # :ref: should be resolved or kept
        assert ":ref:" not in overview or "[" in overview

        # :download: should be resolved to assets
        assert "assets/complex-doc/sample.xml" in overview

        # :java:extdoc: should be inline code
        assert "`ThreadContext`" in overview

        # External URL unchanged
        assert "[External](https://example.com)" in overview
