"""Shared constants used by both create-side and verify-side modules.

This module must remain dependency-free so verify can import it without
violating the verify-independence rule (`.claude/rules/rbkc.md`).
"""
from __future__ import annotations


# Sentinel title used in hints files to mark the file-level hint entry
# (Phase 21-D schema design §3-4).  Used by xlsx sources whose JSON
# top-level ``title`` is ``""``.  At the create/verify boundary, a
# hints-file head entry with this title maps to the JSON top-level
# ``hints`` field regardless of the JSON title value.
FILE_SENTINEL = "__file__"
