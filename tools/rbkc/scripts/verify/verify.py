"""RBKC verify — quality gate for RBKC output.

Checks that knowledge JSON files correctly represent their source documents.
See: tools/rbkc/docs/rbkc-verify-quality-design.md

This module is being rebuilt from scratch (Phase 21-V). All checks are currently
stubs returning []; they will be implemented TDD-style per the design spec.

Public API (preserved for run.py compatibility):
    verify_file(source_path, json_path, fmt, knowledge_dir) -> list[str]
    verify_docs_md(source_path, docs_md_path, fmt) -> list[str]
    check_index_coverage(knowledge_dir, index_path) -> list[str]
    check_docs_coverage(knowledge_dir, docs_dir) -> list[str]
    check_source_links(source_text, fmt, data, label_map, source_path) -> list[str]
    check_json_docs_md_consistency(data, docs_md_text) -> list[str]
"""
from __future__ import annotations


def verify_file(source_path, json_path, fmt, knowledge_dir=None):
    """Per-file JSON checks (QC1-QC5, QL2). Stub."""
    return []


def verify_docs_md(source_path, docs_md_path, fmt):
    """Per-file docs MD checks. Stub."""
    return []


def check_index_coverage(knowledge_dir, index_path):
    """QO4: index.toon coverage. Stub."""
    return []


def check_docs_coverage(knowledge_dir, docs_dir):
    """QO3: docs MD existence. Stub."""
    return []


def check_source_links(source_text, fmt, data, label_map, source_path=None):
    """QL1: internal links. Stub."""
    return []


def check_json_docs_md_consistency(data, docs_md_text):
    """QO1/QO2: JSON ↔ docs MD consistency. Stub."""
    return []
