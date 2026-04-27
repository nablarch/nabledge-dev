"""RST admonition directive → MD blockquote label mapping.

Closed set: the 10 admonition directive names per docutils spec. The
`rst_ast_visitor` reads ``ADMONITION_LABELS`` to render each admonition as
a blockquote with the correct bold label.
"""
from __future__ import annotations


ADMONITION_LABELS: dict[str, str] = {
    "note": "Note",
    "tip": "Tip",
    "warning": "Warning",
    "important": "Important",
    "attention": "Attention",
    "hint": "Hint",
    "admonition": "Note",  # default when no title argument
    "caution": "Caution",
    "danger": "Danger",
    "error": "Error",
}
