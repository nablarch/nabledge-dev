"""Common: RST label / :doc: target resolution.

Used by both create (rst converter — emits MD links) and verify (QL1 two-sided
check). The derivation lives here so that a single spec (RST label syntax +
heading detection + ``mappings/v{N}.json``) is the only source of truth.

Public API
----------
- :class:`LabelTarget` — ``(title, file_id, section_title, category)``.
- :data:`UNRESOLVED` — singleton :class:`LabelTarget` used for labels
  that parse correctly but do not precede a heading.  Compared by identity
  (``x is UNRESOLVED``), never by value.
- :func:`build_label_map` — single-directory scan, backward-compatible API.
  Returns ``dict[label, LabelTarget | UNRESOLVED]``.  ``file_id`` /
  ``category`` stay empty because single-dir mode has no version context.
- :func:`build_label_doc_map` — whole-version scan.  Returns
  ``(label_map, doc_map)`` with ``file_id`` / ``category`` resolved
  per-file via :func:`scripts.common.file_id.derive_file_id`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


_RST_LABEL_DEF_RE = re.compile(r'^\.\.\s+_(?:`([^`]+)`|([a-zA-Z0-9_-]+)):')
_RST_HEADING_CHARS = set('=-~^"\'`#*+<>')


@dataclass(frozen=True)
class LabelTarget:
    """Resolved target for a ``:ref:`` / ``:doc:`` / ``:numref:``.

    - ``title``: target section's title (for ``:ref:``) or document title
      (for ``:doc:``).
    - ``file_id``: knowledge file_id of the target (empty when resolved in
      single-directory mode without version context).
    - ``section_title``: section title used for anchor slug generation.
      Empty for document-level (``:doc:``) targets.
    - ``category``: knowledge category of the target (empty in single-dir
      mode).
    """
    title: str
    file_id: str
    section_title: str
    category: str


#: Singleton sentinel for labels declared in RST but not followed by a heading
#: the parser can recognise.  Compared by identity, never by value.
#:
#: Phase 22-B-16a horizontal-class fix: spec
#: ``rbkc-verify-quality-design.md §3-2-2`` —
#: 「labels.py が heading 検出に失敗して label を map から drop →
#:  drop せず、代わりに「解決不能ラベル」として QC1 FAIL」
UNRESOLVED = LabelTarget(title="", file_id="", section_title="", category="")


def _is_heading_underline(line: str) -> bool:
    s = line.strip()
    return len(s) >= 2 and all(c in _RST_HEADING_CHARS for c in s)


def _scan_rst_labels(rst_path: Path) -> tuple[list[tuple[list[str], str]], str]:
    """Scan a single RST file and return:

    - ``labels_per_heading``: ``[(labels, heading_title)]`` for each heading
      preceded by label definitions, plus ``[(orphan_labels, "")]`` for the
      trailing orphan block.
    - ``doc_title``: the first heading's title (document title), or ``""``
      when none is found.

    Emits the orphan list via the second tuple element with an empty title.
    """
    try:
        text = rst_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [], ""
    lines = text.splitlines()
    pending_labels: list[str] = []
    found: list[tuple[list[str], str]] = []
    doc_title = ""

    def _flush_unresolved() -> None:
        nonlocal pending_labels
        if pending_labels:
            found.append((list(pending_labels), ""))
            pending_labels = []

    i = 0
    while i < len(lines):
        line = lines[i]
        m = _RST_LABEL_DEF_RE.match(line.strip())
        if m:
            pending_labels.append(m.group(1) or m.group(2))
            i += 1
            continue

        stripped = line.strip()
        if _is_heading_underline(stripped):
            # overline style: underline line reached before title — the title
            # is the next non-blank line.
            next_non_blank_idx = next(
                (j for j in range(i + 1, len(lines)) if lines[j].strip()),
                None,
            )
            if (
                next_non_blank_idx is not None
                and not _is_heading_underline(lines[next_non_blank_idx])
            ):
                title = lines[next_non_blank_idx].strip()
                if pending_labels:
                    found.append((list(pending_labels), title))
                    pending_labels = []
                if not doc_title:
                    doc_title = title
            else:
                _flush_unresolved()
            i += 1
            continue

        if stripped and i + 1 < len(lines):
            underline = lines[i + 1].strip()
            if _is_heading_underline(underline):
                # underline-only: title then underline
                title = stripped
                if pending_labels:
                    found.append((list(pending_labels), title))
                    pending_labels = []
                if not doc_title:
                    doc_title = title
                i += 2
                continue

        if pending_labels and not stripped:
            # blank line between label and heading is allowed
            i += 1
            continue

        if pending_labels and stripped:
            # non-heading content between label and heading: labels don't
            # resolve.
            _flush_unresolved()

        i += 1

    _flush_unresolved()
    return found, doc_title


def build_label_map(source_dir) -> dict[str, LabelTarget]:
    """Build ``{rst_label: LabelTarget}`` for all .rst under ``source_dir``.

    Single-directory mode: ``file_id`` / ``category`` are empty because no
    version context is available.  ``title`` / ``section_title`` are still
    filled from the heading that follows the label.  Orphan labels are
    mapped to :data:`UNRESOLVED` (singleton), not silently dropped.
    """
    label_map: dict[str, LabelTarget] = {}
    for rst_file in Path(source_dir).rglob("*.rst"):
        found, _ = _scan_rst_labels(rst_file)
        for labels, title in found:
            if not title:
                for lbl in labels:
                    label_map.setdefault(lbl, UNRESOLVED)
            else:
                for lbl in labels:
                    label_map.setdefault(
                        lbl,
                        LabelTarget(
                            title=title,
                            file_id="",
                            section_title=title,
                            category="",
                        ),
                    )
    return label_map


def build_label_doc_map(
    version: str, repo_root: Path
) -> tuple[dict[str, LabelTarget], dict[str, LabelTarget]]:
    """Whole-version scan: return ``(label_map, doc_map)``.

    - ``label_map``: ``{rst_label: LabelTarget}`` with ``file_id`` /
      ``category`` populated via :func:`scripts.common.file_id.derive_file_id`.
    - ``doc_map``: ``{rst_relpath: LabelTarget}`` keyed by the relpath the
      source-root walker sees (matches :func:`scripts.common.file_id.rel_for_classify`
      output), with ``section_title=""`` (document-level target).

    The walk covers every source root known to the version (see
    :func:`scripts.create.scan._source_roots`).
    """
    # Import locally to avoid a cycle at module load time.
    from scripts.common.file_id import derive_file_id, load_mappings, rel_for_classify
    from scripts.create.scan import _source_roots

    mappings = load_mappings(version, repo_root)

    label_map: dict[str, LabelTarget] = {}
    doc_map: dict[str, LabelTarget] = {}

    for src_root in _source_roots(version, repo_root):
        if not src_root.exists():
            continue
        for rst_file in src_root.rglob("*.rst"):
            fc = derive_file_id(rst_file, "rst", version, repo_root, mappings=mappings)
            # fc can be None for RST files under src_root that don't match
            # any mapping pattern (and aren't top-level index.rst).  We still
            # skip them — they wouldn't produce a knowledge file anyway, so
            # any labels or :doc: targets into them are unresolvable by
            # design (verify will flag them as QC1).
            if fc is None:
                continue

            found, doc_title = _scan_rst_labels(rst_file)

            # label_map entries
            for labels, title in found:
                if not title:
                    for lbl in labels:
                        label_map.setdefault(lbl, UNRESOLVED)
                else:
                    lt = LabelTarget(
                        title=title,
                        file_id=fc.file_id,
                        section_title=title,
                        category=fc.category,
                    )
                    for lbl in labels:
                        label_map.setdefault(lbl, lt)

            # doc_map entry (keyed by relpath the mapping patterns use)
            relpath = rel_for_classify(rst_file, version)
            doc_map[relpath] = LabelTarget(
                title=doc_title or fc.file_id,
                file_id=fc.file_id,
                section_title="",
                category=fc.category,
            )

    return label_map, doc_map
