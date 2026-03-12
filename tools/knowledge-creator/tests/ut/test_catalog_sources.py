"""Test that step2_classify preserves catalog.json fields other than files."""
import os
import json
import pytest
import sys

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))

from common import load_json, write_json


class TestStep2PreservesCatalogFields:
    """step2 must only update 'files', preserving all other fields."""

    def test_sources_preserved_after_step2(self, ctx):
        """sources field is not overwritten by step2."""
        from step1_list_sources import Step1ListSources
        from step2_classify import Step2Classify

        os.makedirs(os.path.dirname(ctx.classified_list_path), exist_ok=True)
        write_json(ctx.classified_list_path, {
            "version": ctx.version,
            "generated_at": "2026-03-08T01:00:00+09:00",
            "sources": [
                {"repo": "https://github.com/nablarch/nablarch-document",
                 "branch": "main", "commit": "abc123"},
                {"repo": "https://github.com/Fintan-contents/nablarch-system-development-guide",
                 "branch": "main", "commit": "def456"},
            ],
            "files": []
        })

        sources = Step1ListSources(ctx, dry_run=False).run()
        Step2Classify(ctx, dry_run=False, sources_data=sources).run()

        catalog = load_json(ctx.classified_list_path)
        assert len(catalog["sources"]) == 2
        assert catalog["sources"][0]["repo"] == "https://github.com/nablarch/nablarch-document"
        assert catalog["sources"][0]["commit"] == "abc123"
        assert catalog["sources"][1]["repo"] == "https://github.com/Fintan-contents/nablarch-system-development-guide"

    def test_generated_at_preserved_after_step2(self, ctx):
        """generated_at is not overwritten by step2."""
        from step1_list_sources import Step1ListSources
        from step2_classify import Step2Classify

        os.makedirs(os.path.dirname(ctx.classified_list_path), exist_ok=True)
        write_json(ctx.classified_list_path, {
            "version": ctx.version,
            "generated_at": "2026-01-01T00:00:00Z",
            "sources": [],
            "files": []
        })

        sources = Step1ListSources(ctx, dry_run=False).run()
        Step2Classify(ctx, dry_run=False, sources_data=sources).run()

        catalog = load_json(ctx.classified_list_path)
        assert catalog["generated_at"] == "2026-01-01T00:00:00Z"

    def test_files_updated_after_step2(self, ctx):
        """files field is updated with new classification results."""
        from step1_list_sources import Step1ListSources
        from step2_classify import Step2Classify

        os.makedirs(os.path.dirname(ctx.classified_list_path), exist_ok=True)
        write_json(ctx.classified_list_path, {
            "version": ctx.version,
            "generated_at": "2026-01-01T00:00:00Z",
            "sources": [{"repo": "test", "branch": "main", "commit": "x"}],
            "files": [{"id": "old-file"}]
        })

        sources = Step1ListSources(ctx, dry_run=False).run()
        Step2Classify(ctx, dry_run=False, sources_data=sources).run()

        catalog = load_json(ctx.classified_list_path)
        file_ids = [f["id"] for f in catalog["files"]]
        assert "old-file" not in file_ids
        assert len(catalog["sources"]) == 1
        assert catalog["sources"][0]["repo"] == "test"

    def test_first_run_without_existing_catalog(self, ctx):
        """First run creates catalog.json with empty sources and correct files."""
        from step1_list_sources import Step1ListSources
        from step2_classify import Step2Classify

        if os.path.exists(ctx.classified_list_path):
            os.remove(ctx.classified_list_path)

        sources = Step1ListSources(ctx, dry_run=False).run()
        Step2Classify(ctx, dry_run=False, sources_data=sources).run()

        assert os.path.exists(ctx.classified_list_path)
        catalog = load_json(ctx.classified_list_path)
        assert "files" in catalog
        assert "version" in catalog
        assert "sources" in catalog
