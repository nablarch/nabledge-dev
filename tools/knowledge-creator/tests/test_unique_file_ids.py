"""Tests: Phase A output has no duplicate file IDs across the full v6 source set."""
import os
import pytest
from run import Context
from step1_list_sources import Step1ListSources
from step2_classify import Step2Classify


V6_RST_BASE = os.path.join(
    os.path.dirname(__file__),
    "../../../.lw/nab-official/v6/nablarch-document/ja"
)


@pytest.mark.skipif(
    not os.path.exists(V6_RST_BASE),
    reason="v6 source files not available (.lw/nab-official/v6/)"
)
class TestUniqueFileIds:
    """Verify all source RST files produce unique base IDs in Phase A output."""

    def test_source_count_matches_unique_id_count(self, tmp_path):
        """Count of source RST files must equal count of unique base IDs.

        Each source RST file must produce a unique base ID so that Phase B
        generation does not silently skip files due to output path collisions.
        """
        repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        ctx = Context(version="6", repo=repo, concurrency=1, run_id="test-unique-ids")
        os.makedirs(ctx.log_dir, exist_ok=True)

        sources = Step1ListSources(ctx, dry_run=True).run()
        result = Step2Classify(ctx, dry_run=True, sources_data=sources).run()

        rst_source_count = sum(
            1 for s in sources["sources"] if s["format"] == "rst"
        )

        # For split files, use original_id as the base ID
        rst_base_ids = [
            f.get("split_info", {}).get("original_id") or f["id"]
            for f in result["files"]
            if f["format"] == "rst"
        ]
        unique_rst_base_ids = set(rst_base_ids)

        duplicates = {
            fid: rst_base_ids.count(fid)
            for fid in set(rst_base_ids)
            if rst_base_ids.count(fid) > 1
        }

        assert len(unique_rst_base_ids) == rst_source_count, (
            f"Duplicate file IDs detected: {duplicates}. "
            f"Expected {rst_source_count} unique IDs, got {len(unique_rst_base_ids)}. "
            f"Add path-based disambiguation in Step2Classify._resolve_duplicate_ids()."
        )
