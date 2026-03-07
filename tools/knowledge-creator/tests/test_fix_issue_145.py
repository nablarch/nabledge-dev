# https://github.com/nablarch/nabledge-dev/issues/145
"""Regression test for issue #145: duplicate file IDs cause silent Phase B skips.

Phase B skips generation when output_path already exists on disk.
If two source files produce the same output_path, the second is silently skipped.
"""
import os
import pytest
from collections import Counter
from unittest.mock import patch, MagicMock

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.abspath(os.path.join(TOOL_DIR, "../.."))
V6_RST_BASE = os.path.join(REPO_ROOT, ".lw/nab-official/v6/nablarch-document/ja")


def _make_args(phase):
    args = MagicMock()
    args.version = "6"
    args.phase = phase
    args.max_rounds = 1
    args.concurrency = 1
    args.dry_run = False
    args.test = None
    args.run_id = "test-issue-145"
    args.yes = True
    args.regen = False
    args.target = None
    args.clean_phase = None
    return args


def _run_phase_a():
    """Run Phase A through main() entry point against real v6 sources."""
    import sys
    sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))

    args = _make_args(phase="A")
    argv = ["run.py", "--version", "6", "--phase", "A"]

    with patch("sys.argv", argv), \
         patch("argparse.ArgumentParser.parse_args", return_value=args):
        import run as run_module
        run_module.main()

    from run import Context
    return Context(version="6", repo=REPO_ROOT, concurrency=1, run_id="test-issue-145")


def test_no_duplicate_output_paths():
    """All classified entries must have unique output_path values.

    A duplicate output_path means Phase B would silently skip the second source
    file, causing a coverage gap with no error or warning.
    """
    from common import load_json

    assert os.path.exists(V6_RST_BASE), (
        f"v6 source files not found: {V6_RST_BASE}\n"
        "Run setup to clone .lw/nab-official/v6/ before executing this test."
    )

    ctx = _run_phase_a()
    result = load_json(ctx.classified_list_path)

    counts = Counter(entry["output_path"] for entry in result["files"])
    duplicates = {path: count for path, count in counts.items() if count > 1}

    assert not duplicates, (
        f"{len(duplicates)} duplicate output_path(s) — Phase B would silently skip these:\n"
        + "\n".join(f"  {path} ({count} sources)" for path, count in sorted(duplicates.items()))
    )
