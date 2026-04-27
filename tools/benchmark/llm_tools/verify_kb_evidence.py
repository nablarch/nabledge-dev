#!/usr/bin/env python3
"""Verify that a quote exists verbatim (or normalized) in a knowledge section body.

Usage:
    python verify_kb_evidence.py <knowledge_root> <file_rel> <sid> <quote>

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
_NORM_MD = re.compile(r"\*\*|__|^\s*#+\s+.*$", flags=re.M)


def _normalize(s: str) -> str:
    s = _NORM_MD.sub("", s or "")
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

    norm_body = _normalize(body)
    norm_quote = _NORM_WS.sub(" ", quote).strip()
    if quote in body or norm_quote in norm_body:
        return "match"

    return f"mismatch: quote not found in {file_rel}:{sid}"


def main() -> None:
    if len(sys.argv) != 5:
        print("Usage: verify_kb_evidence.py <knowledge_root> <file_rel> <sid> <quote>", file=sys.stderr)
        sys.exit(1)
    _, knowledge_root, file_rel, sid, quote = sys.argv
    print(verify(knowledge_root, file_rel, sid, quote))


if __name__ == "__main__":
    main()
