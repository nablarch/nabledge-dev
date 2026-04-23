"""Common: RST label-to-section-title mapping.

Used by both create (rst converter) and verify (QL1 check).
"""
from __future__ import annotations

import re
from pathlib import Path


_RST_LABEL_DEF_RE = re.compile(r'^\.\.\s+_(?:`([^`]+)`|([a-zA-Z0-9_-]+)):')
_RST_HEADING_CHARS = set('=-~^"\'`#*+<>')


def _is_heading_underline(line: str) -> bool:
    s = line.strip()
    return len(s) >= 2 and all(c in _RST_HEADING_CHARS for c in s)


def build_label_map(source_dir) -> dict[str, str]:
    """Build a map of {rst_label: section_title} from all .rst files under source_dir.

    Supports stacked labels (multiple consecutive `.. _label:` lines before one heading):
    all labels in the stack are mapped to the same section title.

    Args:
        source_dir: Path to directory containing RST source files (searched recursively).

    Returns:
        Dict mapping RST label names to the section title they point to.
    """
    label_map: dict[str, str] = {}
    for rst_file in Path(source_dir).rglob("*.rst"):
        try:
            text = rst_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = text.splitlines()
        pending_labels: list[str] = []
        for i, line in enumerate(lines):
            m = _RST_LABEL_DEF_RE.match(line.strip())
            if m:
                pending_labels.append(m.group(1) or m.group(2))
                continue
            if pending_labels:
                stripped = line.strip()
                if not stripped:
                    continue
                if _is_heading_underline(stripped):
                    # Overline style: label → overline → title → underline
                    # The title is the next non-blank line after the overline.
                    next_non_blank_idx = next(
                        (j for j in range(i + 1, len(lines)) if lines[j].strip()), None
                    )
                    if next_non_blank_idx is not None and not _is_heading_underline(lines[next_non_blank_idx]):
                        for lbl in pending_labels:
                            label_map[lbl] = lines[next_non_blank_idx].strip()
                else:
                    # Underline-only style: label → title → underline
                    next_non_blank_idx = next(
                        (j for j in range(i + 1, len(lines)) if lines[j].strip()), None
                    )
                    if next_non_blank_idx is not None and _is_heading_underline(lines[next_non_blank_idx]):
                        for lbl in pending_labels:
                            label_map[lbl] = stripped
                pending_labels = []
    return label_map
