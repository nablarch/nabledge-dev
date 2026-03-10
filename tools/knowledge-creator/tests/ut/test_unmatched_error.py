"""Tests: Step2 raises SystemExit on unmatched RST files."""
import os
import shutil
import pytest
from run import Context
from step1_list_sources import Step1ListSources
from step2_classify import Step2Classify

REAL_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def _copy_mappings(repo):
    shutil.copytree(
        os.path.join(REAL_REPO, "tools/knowledge-creator/mappings"),
        os.path.join(str(repo), "tools/knowledge-creator/mappings"),
    )


@pytest.fixture
def ctx_with_unmatched(tmp_path):
    repo = tmp_path / "repo"
    _copy_mappings(repo)
    rst_base = repo / ".lw/nab-official/v6/nablarch-document/ja"
    # Unmatched file
    d = rst_base / "unknown_new_feature"
    d.mkdir(parents=True, exist_ok=True)
    (d / "guide.rst").write_text("New Feature\n=====\n\nContent")
    # Matched file (for contrast)
    d2 = rst_base / "about_nablarch"
    d2.mkdir(parents=True, exist_ok=True)
    (d2 / "concept.rst").write_text("Concept\n=====\n\nContent")
    ctx = Context(version="6", repo=str(repo), concurrency=1)
    os.makedirs(ctx.log_dir, exist_ok=True)
    return ctx


class TestUnmatchedError:
    def test_unmatched_raises_system_exit(self, ctx_with_unmatched):
        sources = Step1ListSources(ctx_with_unmatched, dry_run=True).run()
        with pytest.raises(SystemExit) as exc_info:
            Step2Classify(ctx_with_unmatched, dry_run=True, sources_data=sources).run()
        assert exc_info.value.code == 1

    def test_all_matched_succeeds(self, tmp_path):
        repo = tmp_path / "repo"
        _copy_mappings(repo)
        rst_base = repo / ".lw/nab-official/v6/nablarch-document/ja/about_nablarch"
        rst_base.mkdir(parents=True, exist_ok=True)
        (rst_base / "concept.rst").write_text("Concept\n=====\n\nContent")
        ctx = Context(version="6", repo=str(repo), concurrency=1)
        os.makedirs(ctx.log_dir, exist_ok=True)
        sources = Step1ListSources(ctx, dry_run=True).run()
        result = Step2Classify(ctx, dry_run=True, sources_data=sources).run()
        assert len(result["files"]) == 1
