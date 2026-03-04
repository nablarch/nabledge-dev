"""Tests for --target filter across phases."""
import json
import os
import subprocess
import pytest
from steps.common import write_json, load_json


def _make_classified_2files(ctx):
    """Helper: create classified.json with 2 source files."""
    for name in ["file-a", "file-b"]:
        src = f"{ctx.repo}/src/{name}.rst"
        os.makedirs(os.path.dirname(src), exist_ok=True)
        with open(src, "w") as f:
            f.write(f"{name}\n====\n\nContent for {name}\n")

    classified = {
        "version": "6", "generated_at": "2026-01-01T00:00:00Z",
        "files": [
            {
                "id": name, "source_path": f"src/{name}.rst", "format": "rst",
                "filename": f"{name}.rst", "type": "component", "category": "test",
                "output_path": f"component/test/{name}.json",
                "assets_dir": f"component/test/assets/{name}/"
            }
            for name in ["file-a", "file-b"]
        ]
    }
    write_json(ctx.classified_list_path, classified)
    return classified


class TestPhaseBTargetFilter:

    def test_target_generates_only_specified_file(self, ctx, mock_claude):
        from steps.phase_b_generate import PhaseBGenerate

        _make_classified_2files(ctx)
        PhaseBGenerate(ctx, run_claude_fn=mock_claude).run(target_ids=["file-a"])

        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/file-a.json")
        assert not os.path.exists(f"{ctx.knowledge_dir}/component/test/file-b.json")

    def test_no_target_generates_all(self, ctx, mock_claude):
        from steps.phase_b_generate import PhaseBGenerate

        _make_classified_2files(ctx)
        PhaseBGenerate(ctx, run_claude_fn=mock_claude).run(target_ids=None)

        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/file-a.json")
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/file-b.json")

    def test_existing_run_calls_still_work(self, ctx, mock_claude):
        """Backward compat: run() without args still processes all files."""
        from steps.phase_b_generate import PhaseBGenerate

        _make_classified_2files(ctx)
        PhaseBGenerate(ctx, run_claude_fn=mock_claude).run()

        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/file-a.json")
        assert os.path.exists(f"{ctx.knowledge_dir}/component/test/file-b.json")
