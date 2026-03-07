"""Tests: Step1 lists all RST files including index.rst."""
import os
import pytest
from run import Context
from step1_list_sources import Step1ListSources


@pytest.fixture
def ctx_with_rst(tmp_path):
    repo = tmp_path / "repo"
    rst_base = repo / ".lw/nab-official/v6/nablarch-document/ja"
    for dir_path, files in {
        "application_framework/application_framework/libraries": ["tag.rst", "index.rst"],
        "about_nablarch": ["index.rst", "concept.rst"],
        "examples": ["index.rst"],
        "": ["index.rst"],
        "_static": ["excluded.rst"],
    }.items():
        d = rst_base / dir_path if dir_path else rst_base
        d.mkdir(parents=True, exist_ok=True)
        for f in files:
            (d / f).write_text(f"content of {f}")
    ctx = Context(version="6", repo=str(repo), concurrency=1)
    os.makedirs(ctx.log_dir, exist_ok=True)
    return ctx


class TestAllInclusive:
    def test_index_rst_included(self, ctx_with_rst):
        result = Step1ListSources(ctx_with_rst, dry_run=True).run()
        filenames = [s["filename"] for s in result["sources"]]
        assert filenames.count("index.rst") == 4

    def test_underscore_dirs_excluded(self, ctx_with_rst):
        result = Step1ListSources(ctx_with_rst, dry_run=True).run()
        assert not any("_static" in s["path"] for s in result["sources"])

    def test_total_count(self, ctx_with_rst):
        result = Step1ListSources(ctx_with_rst, dry_run=True).run()
        assert len([s for s in result["sources"] if s["format"] == "rst"]) == 6
