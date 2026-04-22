"""Tests for scripts/verify/verify.py.

Phase 21-V: currently only smoke tests for the public API stubs.
Real checks are added in V-3 onwards (TDD per rbkc-verify-quality-design.md).
"""
from __future__ import annotations

from scripts.verify.verify import (
    check_docs_coverage,
    check_index_coverage,
    check_json_docs_md_consistency,
    check_source_links,
    verify_docs_md,
    verify_file,
)


def test_verify_file_stub_returns_empty():
    assert verify_file("src", "json", "rst") == []


def test_verify_docs_md_stub_returns_empty():
    assert verify_docs_md("src", "docs", "rst") == []


def test_check_index_coverage_stub_returns_empty():
    assert check_index_coverage("knowledge", "index") == []


def test_check_docs_coverage_stub_returns_empty():
    assert check_docs_coverage("knowledge", "docs") == []


def test_check_source_links_stub_returns_empty():
    assert check_source_links("src", "rst", {}, {}) == []


def test_check_json_docs_md_consistency_stub_returns_empty():
    assert check_json_docs_md_consistency({}, "docs") == []
