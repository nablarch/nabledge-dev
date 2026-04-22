"""RST substitution definitions and reference expansion.

Spec: rbkc-verify-quality-design.md §3-1 (tokenizer block-level).

Used by both create (converter) and verify (normaliser). Must remain
pure RST-spec logic without depending on either implementation.

Public API:
    collect_substitutions(text) -> dict[str, str]
    expand_substitutions(text, subs) -> str

Exceptions:
    UndefinedSubstitutionError — |name| reference with no definition
    SubstitutionCycleError — substitution defines a cycle
"""
from __future__ import annotations

import re


class UndefinedSubstitutionError(Exception):
    """Raised when `|name|` is referenced but no definition exists."""


class SubstitutionCycleError(Exception):
    """Raised when substitution definitions form a cycle."""


# Top-level substitution definition at column 0.
# `.. |name| directive:: arg` then an optionally indented body.
_DEF_HEAD_RE = re.compile(r"^\.\.\s+\|([^|\n]+)\|\s+([a-z_-]+)::(.*)$")

# Reference: |name| where name is an ASCII identifier (letters/digits plus
# -_.:+). Disallows internal whitespace or line breaks (matches docutils
# reference-name grammar and excludes grid-table pipes).
_REF_RE = re.compile(r"\|([A-Za-z0-9][A-Za-z0-9_.:+\-]*)\|")

_BR_TAG_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)


def collect_substitutions(text: str) -> dict[str, str]:
    """Collect top-level ``.. |name| directive:: ...`` definitions.

    Only column-0 definitions are collected (definitions nested inside a
    directive body are not visible at document scope, matching docutils).

    Handles ``replace::`` (body text preserved) and ``raw:: html`` where
    <br> / <br/> maps to "\\n" and other HTML passes through verbatim.
    Unknown directives are collected with an empty expansion (safe default).
    """
    lines = text.splitlines()
    subs: dict[str, str] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        m = _DEF_HEAD_RE.match(line)
        if not m:
            i += 1
            continue
        name = m.group(1).strip()
        directive = m.group(2).lower()
        first_arg = m.group(3).strip()
        # Gather indented body until a non-indented non-blank line.
        body_lines: list[str] = []
        if first_arg and directive == "replace":
            body_lines.append(first_arg)
        # raw:: html uses first_arg as the output format identifier — body
        # sits on following indented lines.
        j = i + 1
        while j < len(lines):
            bl = lines[j]
            if not bl.strip():
                j += 1
                continue
            if bl.startswith(" ") or bl.startswith("\t"):
                body_lines.append(bl.strip())
                j += 1
                continue
            break
        i = j
        if directive == "replace":
            subs[name] = " ".join(body_lines).strip()
        elif directive == "raw":
            body = " ".join(body_lines).strip()
            if _BR_TAG_RE.fullmatch(body):
                subs[name] = "\n"
            elif _BR_TAG_RE.search(body) and not re.sub(_BR_TAG_RE, "", body).strip():
                # Body is only <br> tags (possibly many) — map each to \n.
                subs[name] = _BR_TAG_RE.sub("\n", body)
            else:
                # Extract `<a href="url">text</a>` → `[text](url)` (MD link)
                # to match converter's rendering of HTML anchors.
                m_a = re.match(r'^<a\s+[^>]*href="([^"]+)"[^>]*>([^<]+)</a>\s*$', body)
                if m_a:
                    subs[name] = f"[{m_a.group(2)}]({m_a.group(1)})"
                else:
                    subs[name] = body
        else:
            # Unknown directive — preserve whatever text is there.
            subs[name] = " ".join(body_lines).strip()
    return subs


def expand_substitutions(text: str, subs: dict[str, str], *, strict: bool = True) -> str:
    """Expand `|name|` references in *text* using *subs*.

    Recursive: if an expansion contains further `|name|` references, those
    are expanded too. Cycles raise SubstitutionCycleError.

    In strict mode, an undefined reference raises UndefinedSubstitutionError.
    In non-strict mode, undefined references are left verbatim in the text
    (useful when text contains `|x|`-shaped content that isn't a real
    substitution, e.g., `|127.0.0.1|` inside prose).

    Note: definition blocks themselves (`.. |name| directive:: ...`) contain
    `|name|` in the header line; these are handled as references during
    expansion since the definition block is expected to be stripped
    elsewhere.
    """

    def _sub_once(s: str, stack: tuple[str, ...]) -> str:
        def _replace(m: re.Match) -> str:
            name = m.group(1)
            if name in stack:
                raise SubstitutionCycleError(f"substitution cycle via |{name}|")
            if name not in subs:
                if strict:
                    raise UndefinedSubstitutionError(f"undefined substitution |{name}|")
                return m.group(0)
            value = subs[name]
            if "|" in value:
                value = _sub_once(value, stack + (name,))
            return value

        return _REF_RE.sub(_replace, s)

    return _sub_once(text, ())
