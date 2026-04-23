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

    - ``title``: display fallback — the short text used when the reference
      itself has no explicit display text.  For ``:ref:`` this is the
      label's direct neighbour (heading text, definition-list term, or
      the enclosing section's title).  For ``:doc:`` this is the document
      title.
    - ``file_id``: knowledge file_id of the target (empty in single-dir
      mode without version context).
    - ``section_title``: section title of the label's *enclosing* section
      (empty for document-level ``:doc:`` targets).  Retained for legacy
      consumers.
    - ``category``: knowledge category of the target (empty in single-dir
      mode).
    - ``type``: knowledge type of the target (``component`` / ``about``
      / ...).  Needed to build the ``../../{type}/{category}/...``
      cross-type link path.
    - ``anchor``: HTML anchor slug.  For ``:ref:``/``:numref:``, this is
      the label name slug (Sphinx parity — see spec §3-2-2).  For
      ``:doc:`` it is empty (document-level link, no ``#`` fragment).
    """
    title: str
    file_id: str
    section_title: str
    category: str
    type: str = ""
    anchor: str = ""


#: Singleton sentinel for labels declared in RST but not followed by a heading
#: the parser can recognise.  Compared by identity, never by value.
#:
#: Phase 22-B-16a horizontal-class fix: spec
#: ``rbkc-verify-quality-design.md §3-2-2`` —
#: 「labels.py が heading 検出に失敗して label を map から drop →
#:  drop せず、代わりに「解決不能ラベル」として QC1 FAIL」
UNRESOLVED = LabelTarget(
    title="", file_id="", section_title="", category="", type="", anchor=""
)


def _is_heading_underline(line: str) -> bool:
    s = line.strip()
    return len(s) >= 2 and all(c in _RST_HEADING_CHARS for c in s)


def _scan_rst_labels(rst_path: Path) -> tuple[list[tuple[list[str], str]], str]:
    """Scan a single RST file and return:

    - ``labels_per_heading``: ``[(labels, heading_title)]`` for each label
      set, where ``heading_title`` is the resolved section title.
      Resolution order (matches Sphinx default anchor behaviour):

      1. If the label is immediately followed by a heading, that heading
         wins (preserves the tight ``.. _foo:\\n\\nTitle\\n====`` idiom).
      2. Otherwise, the label resolves to the *enclosing section* — the
         nearest preceding section heading in the same file.
      3. When neither applies (label appears before any heading), the
         label is emitted with an empty title and upstream stamps it
         ``UNRESOLVED``.

    - ``doc_title``: the first heading's title (document title), or ``""``
      when the file has no heading at all.
    """
    try:
        text = rst_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [], ""
    lines = text.splitlines()

    # Pass 1: collect heading positions and titles.
    #   headings[i] = (line_index, title)
    # Overline style (underline above + below) and underline-only are both
    # recognised.  Any title line followed by an underline counts; any
    # underline with a non-underline blank-separated line above it counts.
    headings: list[tuple[int, str]] = []
    i = 0
    n = len(lines)
    while i < n:
        stripped = lines[i].strip()
        if stripped and i + 1 < n and _is_heading_underline(lines[i + 1].strip()):
            # underline-only: title (i), underline (i+1)
            headings.append((i, stripped))
            i += 2
            continue
        if _is_heading_underline(stripped):
            # overline style: overline (i), title (i+1 non-blank),
            # underline (i+2).  Tolerate blank lines between overline
            # and title (docutils does too).
            next_idx = next(
                (j for j in range(i + 1, n) if lines[j].strip()), None
            )
            if (
                next_idx is not None
                and not _is_heading_underline(lines[next_idx].strip())
                and next_idx + 1 < n
                and _is_heading_underline(lines[next_idx + 1].strip())
            ):
                headings.append((next_idx, lines[next_idx].strip()))
                i = next_idx + 2
                continue
        i += 1

    doc_title = headings[0][1] if headings else ""

    # Pass 2: walk line by line, accumulating pending labels, and for each
    # label decide its target title.
    found: list[tuple[list[str], str]] = []
    pending: list[tuple[int, str]] = []  # (line_index, label_name)

    def _enclosing_section_title(line_idx: int) -> str:
        """Return the innermost enclosing section's title for a label at
        ``line_idx``, or ``""`` when no preceding heading exists.
        """
        target = ""
        for h_line, h_title in headings:
            if h_line < line_idx:
                target = h_title
            else:
                break
        return target

    def _next_heading_title(line_idx: int) -> str | None:
        """Return the next heading's title iff it is the very next
        meaningful content after ``line_idx`` (i.e. only blank lines
        and other label definitions intervene)."""
        for h_line, h_title in headings:
            if h_line <= line_idx:
                continue
            # Any non-blank non-label line between line_idx and h_line
            # breaks the "immediately followed by heading" rule.
            for k in range(line_idx + 1, h_line):
                raw = lines[k]
                if not raw.strip():
                    continue
                if _RST_LABEL_DEF_RE.match(raw.strip()):
                    continue
                if _is_heading_underline(raw.strip()):
                    # part of the heading block itself — fine.
                    continue
                return None
            return h_title
        return None

    for idx, line in enumerate(lines):
        m = _RST_LABEL_DEF_RE.match(line.strip())
        if m:
            pending.append((idx, m.group(1) or m.group(2)))

    for line_idx, label in pending:
        title = _next_heading_title(line_idx)
        if not title:
            title = _enclosing_section_title(line_idx)
        found.append(([label], title))

    return found, doc_title


def _anchor_for_label(label: str) -> str:
    """Slug the label name the same way Sphinx does for HTML `id` anchors.

    Spec §3-2-2: Sphinx uses the label name itself as the anchor target,
    lower-casing and replacing underscores with hyphens.  We delegate to
    :func:`scripts.common.github_slug.github_slug` so the output matches
    GitHub's auto-anchor rules for slug consistency across create/verify.
    """
    from scripts.common.github_slug import github_slug
    # Sphinx replaces underscores with hyphens in anchors; github_slug also
    # does so for consistency with GitHub's MD auto-anchor rule.
    return github_slug(label.replace("_", "-"))


def build_label_map(source_dir) -> dict[str, LabelTarget]:
    """Build ``{rst_label: LabelTarget}`` for all .rst under ``source_dir``.

    Single-directory mode: ``file_id`` / ``category`` are empty because no
    version context is available.  ``title`` / ``section_title`` are still
    filled from the heading that follows the label; ``anchor`` is the
    slug of the label name (Sphinx parity).  Orphan labels (file has no
    heading at all at that position) are mapped to :data:`UNRESOLVED`
    (singleton), not silently dropped.
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
                            anchor=_anchor_for_label(lbl),
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
    from scripts.common.file_id import rel_for_classify
    from scripts.create.classify import classify_sources
    from scripts.create.scan import scan_sources

    # Use the full classify pipeline — including collision disambiguation
    # — so label_map / doc_map file_ids match what create writes to disk.
    # Calling derive_file_id directly here would miss disambiguation and
    # produce dangling cross-document links when two RST files share a
    # basename (e.g. multiple ``functional_comparison.rst``).
    sources = scan_sources(version, repo_root)
    file_infos = classify_sources(sources, version, repo_root)

    # Build a ``{absolute_source_path_str: FileInfo}`` index for O(1)
    # lookup while scanning labels.
    fi_by_path: dict[str, "object"] = {}
    for fi in file_infos:
        if fi.format == "rst" and fi.sheet_name is None:
            fi_by_path[str(fi.source_path)] = fi

    label_map: dict[str, LabelTarget] = {}
    doc_map: dict[str, LabelTarget] = {}

    for src_path_str, fi in fi_by_path.items():
        rst_file = Path(src_path_str)
        found, doc_title = _scan_rst_labels(rst_file)

        # label_map entries — one LabelTarget per label (anchor is
        # per-label, so we can't share one LabelTarget across stacked
        # labels).
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
                            file_id=fi.file_id,
                            section_title=title,
                            category=fi.category,
                            type=fi.type,
                            anchor=_anchor_for_label(lbl),
                        ),
                    )

        # doc_map entry (keyed by relpath the mapping patterns use).
        relpath = rel_for_classify(rst_file, version)
        doc_map[relpath] = LabelTarget(
            title=doc_title or fi.file_id,
            file_id=fi.file_id,
            section_title="",
            category=fi.category,
            type=fi.type,
            anchor="",
        )

    return label_map, doc_map
