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

from dataclasses import dataclass
from pathlib import Path


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


def _enclosing_section_title_for_node(node: "nodes.Node") -> str:
    """Return the title text of the innermost enclosing ``section`` ancestor,
    or ``""`` when the node is a direct child of the ``document`` root.

    Spec §3-2-3 resolution order (matches Sphinx default anchor behaviour):

    - ``parent=document`` → ``""`` (document-level label, e.g. h1-direct)
    - ``parent=section``  → that section's title text
    - other parent (block_quote, bullet_list, …) → walk up to the nearest
      enclosing section and return its title
    """
    from docutils import nodes as _nodes
    p = node.parent
    while p is not None:
        if isinstance(p, _nodes.section):
            title_node = p[0] if p.children else None
            if title_node and isinstance(title_node, _nodes.title):
                return title_node.astext()
            return ""
        if isinstance(p, _nodes.document):
            return ""
        p = p.parent
    return ""


def _enclosing_section_is_h1(node: "nodes.Node") -> bool:
    """Return True if the innermost enclosing section is an h1
    (its parent is the document root) or if the node is at document level.

    RBKC JSON contract: h1 maps to the top-level JSON ``title`` field;
    only h2 and deeper sections appear in JSON ``sections[]``.  Labels in
    h1 scope must therefore get ``section_title=""`` so verify §3-2-3
    skips the JSON section check.
    """
    from docutils import nodes as _nodes
    p = node.parent
    while p is not None:
        if isinstance(p, _nodes.section):
            return isinstance(p.parent, _nodes.document)
        if isinstance(p, _nodes.document):
            return True
        p = p.parent
    return True


def _parse_rst_without_transforms(text: str, rst_path: Path) -> "nodes.document":
    """Parse RST source without running docutils transforms.

    ``publish_doctree`` runs the full transform pipeline including ``DocTitle``
    which promotes a lone h1 into the document node — merging the h1 label's
    ``ids``/``names`` into the document and replacing the target node with a
    ``refid``-only stub.  That loses parent-node information needed for
    ``_enclosing_section_title_for_node``.

    Parsing without transforms preserves the raw AST where:
    - target nodes keep their ``ids`` / ``names``
    - parent relationships are intact (target.parent == document for h1-direct
      labels, target.parent == section for in-section labels)
    """
    import io
    import docutils.parsers.rst as _rst_parser
    import docutils.frontend as _frontend
    import docutils.utils as _utils
    from scripts.common.rst_ast import register_shims, _substitution_prolog

    register_shims()
    full_source = _substitution_prolog() + text

    warning_stream = io.StringIO()
    settings = _frontend.get_default_settings(_rst_parser.Parser)
    settings.halt_level = 5
    settings.report_level = 5
    settings.warning_stream = warning_stream
    settings.file_insertion_enabled = True
    settings.raw_enabled = True

    document = _utils.new_document(str(rst_path), settings=settings)
    parser = _rst_parser.Parser()
    parser.parse(full_source, document)
    return document


def _next_section_for_node(node: "nodes.Node"):
    """Return the ``section`` node that this target immediately precedes,
    or ``None``.  See :func:`_next_section_title_for_node` for the full rules.
    """
    from docutils import nodes as _nodes

    parent = node.parent
    if parent is None:
        return None
    siblings = list(parent.children)
    try:
        idx = siblings.index(node)
    except ValueError:
        return None

    for sib in siblings[idx + 1:]:
        if isinstance(sib, _nodes.section):
            return sib
        if isinstance(sib, _nodes.target):
            continue
        break

    is_last_meaningful = all(
        isinstance(sib, _nodes.target) for sib in siblings[idx + 1:]
    )
    if is_last_meaningful and isinstance(parent, _nodes.section):
        grandparent = parent.parent
        if grandparent is not None:
            gp_siblings = list(grandparent.children)
            try:
                parent_idx = gp_siblings.index(parent)
            except ValueError:
                return None
            for gp_sib in gp_siblings[parent_idx + 1:]:
                if isinstance(gp_sib, _nodes.section):
                    return gp_sib
                if isinstance(gp_sib, _nodes.target):
                    continue
                break

    return None


def _next_section_title_for_node(node: "nodes.Node") -> str | None:
    """Return the title of the section that this target node directly precedes.

    See :func:`_next_section_for_node` for the full detection rules.
    Returns the section title, or ``None``.
    """
    from docutils import nodes as _nodes
    sec = _next_section_for_node(node)
    if sec is None or not sec.children:
        return None
    t = sec[0]
    return t.astext() if isinstance(t, _nodes.title) else None


def _scan_rst_labels(
    rst_path: Path,
) -> tuple[list[tuple[list[str], str, str]], str]:
    """Scan a single RST file via docutils AST (without transforms) and return:

    - ``entries``: ``[(labels, title, section_title)]`` for each target node.

      - ``title``: the heading text to use as display text.
        Resolution order (matches Sphinx default anchor behaviour):

        1. If the target is immediately followed by a section (only blank
           targets intervene), that section's title wins (the tight
           ``.. _foo:\\n\\nTitle\\n====`` idiom).
        2. Otherwise, the title is the enclosing section's title.
        3. When neither applies (no enclosing section, parent=document),
           the title is the document title (``doc_title``).  An empty
           ``doc_title`` means UNRESOLVED.

      - ``section_title``: the enclosing section title, or ``""`` when the
        label is at document level (parent=document, e.g. h1-direct).
        Callers (verify.py §3-2-3) use this to check whether the
        target's section exists in the JSON.  An empty ``section_title``
        skips that check.

    - ``doc_title``: the document's first section title, or ``""`` when the
      file has no sections.

    Uses raw docutils parse (no transforms) so that:
    - h1-direct labels keep ``parent=document`` (DocTitle transform would
      merge them into the document node, losing parent info).
    - Non-RST text like ``-->`` (JSP comment end) or ``}`` (Java code) is
      not misidentified as a heading underline by the old line-scanner.
    """
    from docutils import nodes as _nodes

    try:
        text = rst_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return [], ""

    doctree = _parse_rst_without_transforms(text, rst_path)

    # Document title = first section's title (no transforms, so h1 stays as section).
    doc_title = ""
    for child in doctree.children:
        if isinstance(child, _nodes.section) and child.children:
            t = child[0]
            if isinstance(t, _nodes.title):
                doc_title = t.astext()
                break

    found: list[tuple[list[str], str, str]] = []
    for node in doctree.findall(_nodes.target):
        ids = node.get("ids", [])
        names = node.get("names", [])
        # Prefer names[0] (original form, e.g. 'universal_dao') over ids[0]
        # (docutils-normalised form, e.g. 'universal-dao'). Downstream callers
        # (verify.py, rst_ast_visitor.py) look up labels by the RST source
        # name, not the normalised id.  ids is kept as fallback for
        # label-only targets where names is empty (rare).
        label = names[0] if names else (ids[0] if ids else None)
        if label is None:
            continue
        enclosing = _enclosing_section_title_for_node(node)
        in_h1_scope = _enclosing_section_is_h1(node)
        next_node = _next_section_for_node(node)
        next_sec_title = (
            _next_section_title_for_node(node) if next_node is not None else None
        )
        # Is the next section an h1 (direct child of document)?
        next_is_h1 = (
            next_node is not None
            and isinstance(next_node.parent, _nodes.document)
        )

        if next_sec_title and not next_is_h1:
            # Label directly before an h2+ heading.
            # Target = that heading.  section_title = heading title.
            title = next_sec_title
            section_title = next_sec_title
        elif next_sec_title and next_is_h1:
            # Label directly before h1 (document-level or h1-scope label).
            # H1 maps to JSON title field, not sections[].
            title = next_sec_title
            section_title = ""
        elif enclosing and not in_h1_scope:
            # Label inside an h2+ section, not directly before a heading.
            title = enclosing
            section_title = enclosing
        elif enclosing and in_h1_scope:
            # Label inside h1 section, not directly before a heading.
            # H1 is not in JSON sections[].
            title = enclosing
            section_title = ""
        else:
            # Label at document level, not before any heading (pre-h1 orphan).
            title = doc_title
            section_title = ""
        found.append(([label], title, section_title))

    return found, doc_title


def _anchor_for_title(title: str) -> str:
    """Slug the heading text to match GitHub's auto-anchor for the heading.

    Spec §3-2-1: GitHub auto-anchors are derived from heading text (lowercased,
    spaces → hyphens, non-word chars stripped).  Using heading text here ensures
    the ``#anchor`` fragment in generated docs MD matches what GitHub renders.
    """
    from scripts.common.github_slug import github_slug
    return github_slug(title)


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
        for labels, title, section_title in found:
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
                            section_title=section_title,
                            category="",
                            anchor=_anchor_for_title(title),
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
    # F1 fix: depend only on ``common/`` so ``labels.py`` does not
    # import ``create/`` (spec §2-2 layering).  ``classify_rst_and_md``
    # applies the same collision disambiguation create uses, so
    # label_map / doc_map file_ids still match what create writes.
    from scripts.common.file_id import (
        classify_rst_and_md,
        iter_rst_paths,
        load_mappings,
        rel_for_classify,
    )

    class _RstSrc:
        __slots__ = ("path", "format")
        def __init__(self, path):
            self.path = path
            self.format = "rst"

    mappings = load_mappings(version, repo_root)
    srcs = [_RstSrc(p) for p in iter_rst_paths(version, repo_root)]
    classified = classify_rst_and_md(srcs, version, repo_root, mappings=mappings)
    by_path: dict[str, "FileClass"] = {
        str(fc.source_path): fc for fc in classified
    }

    label_map: dict[str, LabelTarget] = {}
    doc_map: dict[str, LabelTarget] = {}

    for src_path_str, fc in by_path.items():
        rst_file = Path(src_path_str)
        found, doc_title = _scan_rst_labels(rst_file)

        for labels, title, section_title in found:
            if not title:
                for lbl in labels:
                    label_map.setdefault(lbl, UNRESOLVED)
            else:
                for lbl in labels:
                    label_map.setdefault(
                        lbl,
                        LabelTarget(
                            title=title,
                            file_id=fc.file_id,
                            section_title=section_title,
                            category=fc.category,
                            type=fc.type,
                            anchor=_anchor_for_title(title),
                        ),
                    )

        relpath = rel_for_classify(rst_file, version)
        doc_map[relpath] = LabelTarget(
            title=doc_title or fc.file_id,
            file_id=fc.file_id,
            section_title="",
            category=fc.category,
            type=fc.type,
            anchor="",
        )

    return label_map, doc_map
