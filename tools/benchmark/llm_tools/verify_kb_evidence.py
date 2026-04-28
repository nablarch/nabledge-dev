#!/usr/bin/env python3
"""Verify that a quote exists verbatim (or normalized) in a knowledge section body.

Usage:
    python verify_kb_evidence.py <knowledge_root> <file_rel> <sid> -  <<'QUOTE_END'
    <verbatim quote text>
    QUOTE_END

Pass the quote via stdin (the fourth positional argument must be "-").
Using a single-quoted heredoc (<<'QUOTE_END') prevents the shell from
expanding backticks or $-variables in the quote, which would corrupt it.

Legacy positional-arg form (argv[4] != "-") is still accepted for
compatibility but should not be used when the quote may contain
backticks, dollar-signs, or other shell-special characters.

Prints "match" if the quote is found in the specified section, or
"mismatch: <reason>" otherwise. Designed to be called by the judge LLM
as a Bash tool so it can self-correct SUPPORTED_BY_KB citations before
emitting StructuredOutput.
"""

import json
import re
import sys
from pathlib import Path


_NORM_WS = re.compile(r"\s+")
# Markdown markup patterns: emphasis (**text** / __text__) and ATX headers.
# Applied to the KB body only — not to the quote — because __ in a quote
# typically means a Python dunder name, not emphasis markup.
_NORM_MD = re.compile(r"\*\*|__|^\s*#+\s+.*$", flags=re.M)
# Strip inline-code backtick wrapping (`token` → token).  Applied to BOTH
# body and quote so that a KB body using `code` style matches a quote that
# omits the backticks (review-07 pattern) or vice-versa (impact-01 pattern).
_NORM_BACKTICK = re.compile(r"`([^`\n]*)`")


def _normalize_body(s: str) -> str:
    """Normalize KB section body: strip MD markers + backticks + collapse whitespace."""
    s = _NORM_MD.sub("", s or "")
    s = _NORM_BACKTICK.sub(r"\1", s)
    return _NORM_WS.sub(" ", s).strip()


def _normalize_quote(s: str) -> str:
    """Normalize quote: strip backtick wrapping + collapse whitespace only.

    Deliberately does NOT strip ** / __ emphasis markers from the quote
    because __ in a quote is more likely to be a Python dunder name than
    Markdown emphasis.  Stripping it would produce false matches.
    """
    s = _NORM_BACKTICK.sub(r"\1", s or "")
    return _NORM_WS.sub(" ", s).strip()


def verify(knowledge_root: str, file_rel: str, sid: str, quote: str) -> str:
    if not quote or not quote.strip():
        return "mismatch: empty quote"

    kb_path = Path(knowledge_root) / file_rel
    try:
        data = json.loads(kb_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        return f"mismatch: file unreadable ({e})"

    sections = data.get("sections") or {}
    raw = sections.get(sid)
    if raw is None:
        return f"mismatch: sid '{sid}' not found in {file_rel}"

    body = raw.get("body") if isinstance(raw, dict) else raw
    if not isinstance(body, str) or not body:
        return f"mismatch: sid '{sid}' has empty body"

    norm_body = _normalize_body(body)
    norm_quote = _normalize_quote(quote)
    if quote in body or norm_quote in norm_body:
        return "match"

    return f"mismatch: quote not found in {file_rel}:{sid}"


def main() -> None:
    if len(sys.argv) != 5:
        print(
            "Usage: verify_kb_evidence.py <knowledge_root> <file_rel> <sid> -\n"
            "  (pass quote via stdin; use a single-quoted heredoc to avoid shell expansion)",
            file=sys.stderr,
        )
        sys.exit(1)
    _, knowledge_root, file_rel, sid, quote_arg = sys.argv
    if quote_arg == "-":
        quote = sys.stdin.read().rstrip("\n")
    else:
        quote = quote_arg
    print(verify(knowledge_root, file_rel, sid, quote))


if __name__ == "__main__":
    main()
