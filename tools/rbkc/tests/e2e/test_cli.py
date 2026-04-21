"""E2E tests for RBKC CLI verify operation.

Uses a small subset of real v6 source files to keep tests fast.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parents[4]  # repo root

# 3 real source files used as test fixtures
# NOTE: RST fixture must not contain :ref: cross-references or .. figure::/.. image::
# directives pointing to files not present in the repo. This avoids Check C FAIL
# for RBKC bugs that are tracked separately (e.g., :ref: label emission).
# multiple_process.rst: 95 lines, no :ref:, no figure/image/literalinclude.
_TEST_SOURCES = [
    # RST → processing-pattern/db-messaging
    ".lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/messaging/db/feature_details/multiple_process.rst",
    # XLSX release note → releases/releases
    ".lw/nab-official/v6/nablarch-document/ja/releases/nablarch6-releasenote.xlsx",
    # XLSX security → check/security-check
    ".lw/nab-official/v6/nablarch-system-development-guide/Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx",
]


@pytest.fixture()
def workspace(tmp_path):
    """Workspace with output and state directories."""
    return {
        "output": tmp_path / "knowledge",
        "state": tmp_path / "state",
    }


# ---------------------------------------------------------------------------
# verify tests
# ---------------------------------------------------------------------------

class TestVerify:
    @pytest.fixture()
    def after_create(self, workspace):
        from scripts.run import create
        create(
            version="6",
            repo_root=_REPO_ROOT,
            output_dir=workspace["output"],
            state_dir=workspace["state"],
            files=_TEST_SOURCES,
        )
        return workspace

    def test_verify_passes_for_consistent_output(self, after_create):
        """verify returns True when JSON output matches source."""
        from scripts.run import verify
        ok = verify(
            version="6",
            repo_root=_REPO_ROOT,
            output_dir=after_create["output"],
            files=_TEST_SOURCES,
        )
        assert ok is True

    def test_verify_fails_for_corrupted_json_qc2(self, after_create):
        """verify returns False when JSON contains fabricated content not in source (QC2)."""
        from scripts.run import verify
        output = after_create["output"]

        # Corrupt the xlsx release note JSON by injecting fabricated content.
        # xlsx verify uses QC2 (residual check): content in JSON but not in source
        # is flagged as fabricated.
        json_files = list(output.rglob("*nablarch6*releasenote*.json"))
        corrupted_path = json_files[0]
        data = json.loads(corrupted_path.read_text(encoding="utf-8"))
        # Inject a fabricated section to trigger QC2
        data["sections"].append({"title": "FABRICATED_CONTENT_XYZ", "content": "FABRICATED_CONTENT_XYZ"})
        corrupted_path.write_text(json.dumps(data), encoding="utf-8")

        ok = verify(
            version="6",
            repo_root=_REPO_ROOT,
            output_dir=output,
            files=_TEST_SOURCES,
        )
        assert ok is False

    def test_verify_fails_for_corrupted_json_qc1(self, after_create):
        """verify returns False when source content is missing from JSON (QC1)."""
        from scripts.run import verify
        output = after_create["output"]

        # Corrupt the xlsx release note JSON by clearing all section content but
        # keeping a non-empty title so json_text is not blank (which would skip QC1).
        # xlsx verify uses QC1 (completeness check): source tokens absent from JSON
        # are flagged as missing.
        json_files = list(output.rglob("*nablarch6*releasenote*.json"))
        corrupted_path = json_files[0]
        data = json.loads(corrupted_path.read_text(encoding="utf-8"))
        # Replace section content with a placeholder so json_text is non-empty
        # (blank json_text causes early return in verify before QC1 runs).
        # Source tokens are now absent from JSON → QC1 fires.
        data["title"] = "PLACEHOLDER"
        for sec in data["sections"]:
            sec["content"] = "PLACEHOLDER"
            sec["title"] = ""
        corrupted_path.write_text(json.dumps(data), encoding="utf-8")

        ok = verify(
            version="6",
            repo_root=_REPO_ROOT,
            output_dir=output,
            files=_TEST_SOURCES,
        )
        assert ok is False
