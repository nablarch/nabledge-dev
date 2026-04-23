"""RST admonition → MD blockquote conversion rules (common).

Shared pure-logic module used by both the converter (scripts/create/
converters/rst.py) and the tokenizer (scripts/common/rst_normaliser.py).

Rationale
---------
Admonition rendering is a RST-spec convention, not a converter implementation
detail. Putting it in scripts/common/ keeps verify's independence from RBKC
implementation intact (the tokenizer imports common/, not create/).

Closed set: the 10 admonition directive names per docutils spec (no Sphinx-
specific `seealso` / `deprecated` / `versionadded` / `versionchanged` — those
never appear in the Nablarch corpus per Y-1 AST probe).
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


ADMONITION_DIRECTIVES: set[str] = set(ADMONITION_LABELS)


def is_admonition(name: str) -> bool:
    """Return True if *name* is an RST admonition directive."""
    return name in ADMONITION_DIRECTIVES


def render_header(name: str, title: str = "") -> str:
    """Return the MD blockquote header line for the admonition.

    - `.. note::` → `> **Note:**`
    - `.. admonition:: My Title` → `> **My Title**` (custom titled, no colon)
    - `.. admonition::` (no title) → `> **Note:**` (default)

    Raises KeyError for unknown directive names.
    """
    if name not in ADMONITION_LABELS:
        raise KeyError(name)
    if name == "admonition" and title:
        return f"> **{title}**"
    return f"> **{ADMONITION_LABELS[name]}:**"
