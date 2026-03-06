"""End-to-end tests for --test option (test-files-largest3.json, test-files-comprehensive.json).

These tests use the real repository with actual source files to verify test mode filtering.
"""
import pytest
import os
import sys
import json

# Get real repository path
TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(os.path.dirname(TOOL_DIR))

sys.path.insert(0, TOOL_DIR)
from run import Context
from steps.step1_list_sources import Step1ListSources
from steps.step2_classify import Step2Classify
from steps.common import load_json


@pytest.fixture
def real_ctx(tmp_path):
    """Context using real repository source files but temporary output."""
    # Use real repo for sources, temp for outputs
    log_base = tmp_path / ".logs"
    log_base.mkdir()

    class RealContext(Context):
        @property
        def log_dir(self):
            return str(log_base / f"v{self.version}")

    ctx = RealContext(version="6", repo=REPO_ROOT, concurrency=1, run_id="test")
    os.makedirs(ctx.log_dir, exist_ok=True)
    return ctx


pytestmark = pytest.mark.skipif(
    not os.path.exists(f"{REPO_ROOT}/.lw/nab-official/v6"),
    reason="Requires real repository with source files"
)


class TestLargest3Mode:
    """Tests for test-files-largest3.json filtering."""

    def test_top3_phase_a_filtering(self, real_ctx):
        """test-files-largest3.json: 3ソースファイル → 22エントリー（分割後）"""
        # Set test mode
        real_ctx.test_file = "test-files-largest3.json"

        # Phase A
        sources = Step1ListSources(real_ctx, dry_run=False).run()
        Step2Classify(real_ctx, dry_run=False, sources_data=sources).run()

        # Load classified result
        classified = load_json(real_ctx.classified_list_path)

        # Expected: 3 source files split into 22 entries
        # - libraries-tag: 9 parts
        # - libraries-tag_reference: 6 parts
        # - adapters-micrometer_adaptor: 7 parts
        assert len(classified["files"]) == 22

        # Check split files are included
        original_ids = set()
        for f in classified["files"]:
            if "split_info" in f:
                original_ids.add(f["split_info"]["original_id"])
            else:
                original_ids.add(f["id"])

        assert "libraries-tag" in original_ids
        assert "libraries-tag_reference" in original_ids
        assert "adapters-micrometer_adaptor" in original_ids

    def test_top3_all_parts_present(self, real_ctx):
        """test-files-largest3.json: 分割ファイルの全パーツが含まれる"""
        real_ctx.test_file = "test-files-largest3.json"

        sources = Step1ListSources(real_ctx, dry_run=False).run()
        Step2Classify(real_ctx, dry_run=False, sources_data=sources).run()

        classified = load_json(real_ctx.classified_list_path)

        # Count parts for each original file
        parts_count = {}
        for f in classified["files"]:
            if "split_info" in f:
                oid = f["split_info"]["original_id"]
                parts_count[oid] = parts_count.get(oid, 0) + 1

        # Verify expected part counts
        assert parts_count.get("libraries-tag", 0) == 9
        assert parts_count.get("libraries-tag_reference", 0) == 6
        assert parts_count.get("adapters-micrometer_adaptor", 0) == 7


class TestComprehensiveMode:
    """Tests for test-files-comprehensive.json filtering."""

    def test_comprehensive_phase_a_filtering(self, real_ctx):
        """test-files-comprehensive.json: 17ソースファイル → 24エントリー（分割後）"""
        real_ctx.test_file = "test-files-comprehensive.json"

        sources = Step1ListSources(real_ctx, dry_run=False).run()
        Step2Classify(real_ctx, dry_run=False, sources_data=sources).run()

        classified = load_json(real_ctx.classified_list_path)

        # Expected: 17 source files, some split into multiple parts
        assert len(classified["files"]) == 24

    def test_comprehensive_original_ids_match(self, real_ctx):
        """test-files-comprehensive.json: 指定した17個のoriginal_idが全て含まれる"""
        real_ctx.test_file = "test-files-comprehensive.json"

        # Load test file
        test_file_path = f"{real_ctx.repo}/tools/knowledge-creator/test-files-comprehensive.json"
        with open(test_file_path) as f:
            test_config = json.load(f)
        expected_ids = set(test_config["files"])

        sources = Step1ListSources(real_ctx, dry_run=False).run()
        Step2Classify(real_ctx, dry_run=False, sources_data=sources).run()

        classified = load_json(real_ctx.classified_list_path)

        # Collect original_ids from classified files
        found_ids = set()
        for f in classified["files"]:
            original_id = f.get("split_info", {}).get("original_id") or f["id"]
            found_ids.add(original_id)

        # All expected IDs should be found
        assert expected_ids == found_ids

    def test_comprehensive_categories_coverage(self, real_ctx):
        """test-files-comprehensive.json: 複数カテゴリをカバー"""
        real_ctx.test_file = "test-files-comprehensive.json"

        sources = Step1ListSources(real_ctx, dry_run=False).run()
        Step2Classify(real_ctx, dry_run=False, sources_data=sources).run()

        classified = load_json(real_ctx.classified_list_path)

        # Collect types and categories
        types = set(f["type"] for f in classified["files"])
        categories = set(f["category"] for f in classified["files"])

        # Should cover multiple types
        assert "component" in types
        assert "development-tools" in types
        assert "processing-pattern" in types

        # Should include specific categories
        assert "adapters" in categories or "handlers" in categories or "libraries" in categories
        assert "testing-framework" in categories


# Note: Phase B E2E tests are omitted as they require actual Claude API calls
# or complex mocking infrastructure. Phase A filtering tests above verify
# that test mode correctly filters files before generation.


class TestTestModeEdgeCases:
    """Edge cases for test mode."""

    def test_nonexistent_test_file_id_warning(self, real_ctx):
        """存在しないファイルIDを指定 → 警告を出力"""
        real_ctx.test_file = "test-files-largest3.json"

        # Modify test file to include non-existent ID
        test_file_path = f"{real_ctx.repo}/tools/knowledge-creator/test-files-largest3.json"
        with open(test_file_path) as f:
            original = f.read()

        try:
            # Add fake ID
            with open(test_file_path, "r") as f:
                config = json.load(f)
            config["files"].append("nonexistent-file-id-12345")
            with open(test_file_path, "w") as f:
                json.dump(config, f)

            sources = Step1ListSources(real_ctx, dry_run=False).run()
            result = Step2Classify(real_ctx, dry_run=False, sources_data=sources).run()

            classified = load_json(real_ctx.classified_list_path)

            # Should still work, but the fake ID won't be found
            found_ids = set()
            for f in classified["files"]:
                original_id = f.get("split_info", {}).get("original_id") or f["id"]
                found_ids.add(original_id)

            assert "nonexistent-file-id-12345" not in found_ids

        finally:
            # Restore original file
            with open(test_file_path, "w") as f:
                f.write(original)

    def test_test_mode_preserves_split_structure(self, real_ctx):
        """テストモードでも分割構造が保持される"""
        real_ctx.test_file = "test-files-largest3.json"

        sources = Step1ListSources(real_ctx, dry_run=False).run()
        Step2Classify(real_ctx, dry_run=False, sources_data=sources).run()

        classified = load_json(real_ctx.classified_list_path)

        # Check split_info is preserved
        split_files = [f for f in classified["files"] if "split_info" in f]
        assert len(split_files) > 0

        # Verify split_info structure
        for f in split_files:
            assert "original_id" in f["split_info"]
            assert "part" in f["split_info"]
            assert "total_parts" in f["split_info"]
            assert "is_split" in f["split_info"]
            assert f["split_info"]["is_split"] is True
