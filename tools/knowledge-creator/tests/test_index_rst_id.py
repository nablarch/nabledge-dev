"""Tests: index.rst ID generation (pattern-remainder approach)."""
import pytest
from steps.step2_classify import Step2Classify


class TestIndexRstId:
    @pytest.fixture
    def c(self, ctx):
        return Step2Classify(ctx, dry_run=True)

    def test_at_pattern_root(self, c):
        assert c.generate_id(
            "index.rst", "rst", "handlers",
            source_path=".lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/handlers/index.rst",
            matched_pattern="application_framework/application_framework/handlers/"
        ) == "handlers-handlers"

    def test_in_subdirectory(self, c):
        assert c.generate_id(
            "index.rst", "rst", "handlers",
            source_path=".lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/handlers/batch/index.rst",
            matched_pattern="application_framework/application_framework/handlers/"
        ) == "handlers-batch"

    def test_deep_subdirectory(self, c):
        assert c.generate_id(
            "index.rst", "rst", "nablarch-batch",
            source_path=".lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/batch/nablarch_batch/getting_started/nablarch_batch/index.rst",
            matched_pattern="application_framework/application_framework/batch/nablarch_batch"
        ) == "nablarch-batch-getting-started-nablarch-batch"

    def test_same_category_unique(self, c):
        id1 = c.generate_id("index.rst", "rst", "about-nablarch",
            source_path=".lw/nab-official/v6/nablarch-document/ja/about_nablarch/index.rst",
            matched_pattern="about_nablarch/")
        id2 = c.generate_id("index.rst", "rst", "about-nablarch",
            source_path=".lw/nab-official/v6/nablarch-document/ja/biz_samples/index.rst",
            matched_pattern="biz_samples/")
        assert id1 != id2

    def test_top_level(self, c):
        assert c.generate_id(
            "index.rst", "rst", "about-nablarch",
            source_path=".lw/nab-official/v6/nablarch-document/ja/index.rst",
            matched_pattern=""
        ) == "about-nablarch-top"

    def test_non_index_unchanged(self, c):
        assert c.generate_id("tag.rst", "rst", "libraries") == "libraries-tag"

    def test_backward_compat_no_new_params(self, c):
        assert c.generate_id("tag.rst", "rst", "libraries") == "libraries-tag"
