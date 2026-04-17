"""RBKC verify — stub placeholder.

The old verify implementation (Check A/B/C/D/E/F/H design) has been removed.
New implementation following QC1–QC6 / QL1–QL2 / QO1–QO5 design will be
added in Phase V3.

See: tools/rbkc/docs/rbkc-verify-quality-design.md
"""
# Stub exports used by run.py until new implementation is complete.
# run.verify() is also temporarily stubbed (returns True unconditionally).

from pathlib import Path


def verify_file(source_path, json_path, fmt, knowledge_dir=None):
    """Stub — not yet implemented."""
    return []


def verify_docs_md(source_path, docs_md_path, fmt):
    """Stub — not yet implemented."""
    return []


def check_index_coverage(knowledge_dir, index_path):
    """Stub — not yet implemented."""
    return []


def check_docs_coverage(knowledge_dir, docs_dir):
    """Stub — not yet implemented."""
    return []


def build_label_map(source_dir):
    """Stub — not yet implemented."""
    return {}


def check_source_links(source_text, fmt, data, label_map, source_path=None):
    """Stub — not yet implemented."""
    return []


def check_json_docs_md_consistency(data, docs_md_text):
    """Stub — not yet implemented."""
    return []
