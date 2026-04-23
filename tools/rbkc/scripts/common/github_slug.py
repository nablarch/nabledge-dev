"""GitHub Web heading auto-anchor algorithm (independent of RBKC create).

Reproduces the slugify rule used by ``gjtorikian/html-pipeline``
(lib/html/pipeline/toc_filter.rb) — the filter GitHub Web applies to
Markdown heading text when generating ``#anchor`` links.

Used by both create (docs.py / future link-generation) and verify
(QL1 docs-MD anchor resolution) per spec §3-2-1:
  「仕様根拠は GitHub docs: 小文字化、空白を `-` に置換、ASCII 記号除去
   (一部許容)、CJK/非ASCII はそのまま保持、重複時は `-1`/`-2` サフィックス」

The algorithm is spec-derived, not create-derived — this module is the
*single source of truth*, and both sides independently consume it.  Tests
in ``tests/ut/test_verify.py::TestGithubSlug`` pin the algorithm against
the GitHub spec, so a bug in this file would surface without regard to
how docs.py happens to call it (avoiding the circular-test pattern
forbidden by `.claude/rules/rbkc.md`).

Algorithm (applied in order):
    1. ASCII downcase — non-ASCII letters unchanged
    2. Strip every char that is NOT \\p{Word} / `-` / ` `
       (Ruby regex ``/[^\\p{Word}\\- ]/u``).  \\p{Word} covers letters,
       digits, marks, and connector punctuation (`_`).  CJK is kept.
    3. Replace every space with ``-``.  No collapsing, no trimming —
       consecutive / leading / trailing spaces produce consecutive /
       leading / trailing hyphens.
    4. Collision counter — first occurrence = bare slug; Nth (N ≥ 2)
       occurrence = ``slug-{N-1}``.  Handled by the ``seen`` dict param.

Public API:
    github_slug(text: str, seen: dict[str, int] | None = None) -> str
"""
from __future__ import annotations

import re
import unicodedata

# Unicode \p{Word} = letters (L*), digits (N*), marks (M*), connector
# punctuation (P_, i.e. `_`).  Python's re module does not expose \p{},
# so we enumerate by Unicode category per the spec.
_WORD_CATEGORIES = {"L", "N", "M"}


def _is_word_char(ch: str) -> bool:
    """Return True iff *ch* is \\p{Word} per the Ruby Unicode definition."""
    if ch == "_":
        return True  # Pc (connector punctuation) — kept as word
    cat = unicodedata.category(ch)
    return cat[0] in _WORD_CATEGORIES


def _strip_punctuation(text: str) -> str:
    """Strip every char that is NOT \\p{Word}, `-`, or ` `."""
    return "".join(ch for ch in text if _is_word_char(ch) or ch in {"-", " "})


_ASCII_UPPER_RE = re.compile(r"[A-Z]")


def _ascii_downcase(text: str) -> str:
    """Lowercase ASCII letters only; leave non-ASCII letters (e.g. É) intact.

    Unlike ``str.lower()``, this preserves characters whose uppercase
    form differs from their lowercase form outside the ASCII range —
    matching Ruby's ``String#downcase`` default (not the full-Unicode
    ``:fold`` option).
    """
    return _ASCII_UPPER_RE.sub(lambda m: m.group(0).lower(), text)


def github_slug(text: str, seen: dict[str, int] | None = None) -> str:
    """Produce the GitHub Web heading auto-anchor slug for *text*.

    Args:
        text: Heading text as it appears rendered on the page (GitHub's
            TOC filter operates on rendered text — images, code spans,
            inline formatting have already been flattened).
        seen: Optional collision counter.  When provided, each call
            increments ``seen[slug]`` and suffixes duplicates with
            ``-1``/``-2``/...  Pass a fresh dict per document; omit for
            single-heading use.

    Returns:
        The anchor slug (without leading ``#``).
    """
    slug = _ascii_downcase(text)
    slug = _strip_punctuation(slug)
    slug = slug.replace(" ", "-")

    if seen is None:
        return slug

    count = seen.get(slug, 0)
    seen[slug] = count + 1
    if count == 0:
        return slug
    return f"{slug}-{count}"


__all__ = ["github_slug"]
