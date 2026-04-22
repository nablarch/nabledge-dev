"""RST include / literalinclude directive expansion.

Spec: rbkc-verify-quality-design.md §3-1 (tokenizer block-level).

Shared between create (converter) and verify (normaliser). Pure RST-spec
logic — no dependency on RBKC implementation layers.

Public API:
    expand_includes(source_path, max_depth=8) -> str
    resolve_literalinclude(path, start_after=None, end_before=None, lines=None) -> str

Exceptions:
    IncludeCycleError — an include chain forms a cycle
    IncludeDepthError — include chain exceeds max_depth
"""
from __future__ import annotations

import re
from pathlib import Path


class IncludeCycleError(Exception):
    """Raised when `.. include::` chain forms a cycle."""


class IncludeDepthError(Exception):
    """Raised when `.. include::` chain exceeds max_depth."""


_INCLUDE_DIRECTIVE_RE = re.compile(r"^\s*\.\.\s+include::\s+(\S.*)$")


def expand_includes(source_path, max_depth: int = 8) -> str:
    """Recursively splice `.. include:: path` directives into source text.

    Paths are resolved relative to the including file. Missing files raise
    FileNotFoundError. Cycles raise IncludeCycleError. Chains deeper than
    ``max_depth`` raise IncludeDepthError.

    Malformed include directives (no path) are left in place so callers
    can flag them through normal unknown-syntax handling.
    """
    src = Path(source_path).resolve()

    def _expand(path: Path, depth: int, visited: frozenset[Path]) -> str:
        if depth > max_depth:
            raise IncludeDepthError(
                f"include chain depth {depth} exceeds max_depth={max_depth} at {path}"
            )
        if path in visited:
            raise IncludeCycleError(f"include cycle via {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        new_visited = visited | {path}
        out_lines: list[str] = []
        for line in text.splitlines(keepends=True):
            m = _INCLUDE_DIRECTIVE_RE.match(line.rstrip("\n"))
            if not m:
                out_lines.append(line)
                continue
            target_rel = m.group(1).strip()
            if not target_rel:
                out_lines.append(line)
                continue
            target = (path.parent / target_rel).resolve()
            if not target.exists():
                raise FileNotFoundError(f"include target not found: {target} (from {path})")
            out_lines.append(_expand(target, depth + 1, new_visited))
        result = "".join(out_lines)
        return result

    return _expand(src, 0, frozenset())


def resolve_literalinclude(
    path,
    start_after: str | None = None,
    end_before: str | None = None,
    lines: str | None = None,
) -> str:
    """Return the text of a literalinclude target, honoring the standard options.

    ``lines`` is a comma-separated list of line ranges (1-based), e.g.
    "2-4" or "1,3-5". ``start_after`` / ``end_before`` slice the file by
    the first occurrence of the given marker strings (marker line itself
    is excluded). Options may be combined; ``lines`` is applied first.
    """
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    file_lines = text.splitlines(keepends=True)

    if lines:
        keep_idx: list[int] = []
        for part in lines.split(","):
            part = part.strip()
            if "-" in part:
                a, b = part.split("-", 1)
                start, end = int(a), int(b)
            else:
                start = end = int(part)
            for n in range(start, end + 1):
                keep_idx.append(n - 1)
        file_lines = [file_lines[i] for i in keep_idx if 0 <= i < len(file_lines)]
        text = "".join(file_lines)

    if start_after is not None:
        body_lines = text.splitlines(keepends=True)
        out: list[str] = []
        seen = False
        for line in body_lines:
            if not seen:
                if start_after in line:
                    seen = True
                continue
            out.append(line)
        text = "".join(out)

    if end_before is not None:
        body_lines = text.splitlines(keepends=True)
        out = []
        for line in body_lines:
            if end_before in line:
                break
            out.append(line)
        text = "".join(out)

    return text
