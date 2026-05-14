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

    Multi-level climb: when the target is the last meaningful item in its
    parent section, climb to the parent's parent and look for the next
    sibling section there.  Repeat until a sibling section is found or the
    document root is reached.  This handles deeply-nested end-of-section
    labels like::

        section ``要求`` (h2)
          section ``未検討`` (h3)
            ...
            .. _Log_LoggerProcess:   ← last in 未検討, 2 levels above
        section ``ログ出力要求受付処理`` (h2)  ← correct target
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

    # First check: direct siblings after the target node.
    # Skip over other target nodes, transition nodes (horizontal rules like
    # +++ in RST), and line_block nodes (bare ``|`` lines).  Sphinx
    # PropagateTargets moves a label's id past a transition because transition
    # cannot hold an HTML id — so the label effectively points to the section
    # that follows the transition.  line_block (``|``) is a visual spacer
    # with no semantic content and should be treated similarly.
    def _is_skippable(n) -> bool:
        return isinstance(n, (_nodes.target, _nodes.transition, _nodes.line_block))

    for sib in siblings[idx + 1:]:
        if isinstance(sib, _nodes.section):
            return sib
        if _is_skippable(sib):
            continue
        break

    # Multi-level climb: if the target is the last meaningful item in its
    # section (only target/transition/line_block nodes follow), walk up through
    # ancestor sections looking for the next sibling section at each level.
    is_last_meaningful = all(
        _is_skippable(sib) for sib in siblings[idx + 1:]
    )
    if not is_last_meaningful:
        return None

    current = parent
    while isinstance(current, _nodes.section):
        ancestor = current.parent
        if ancestor is None:
            break
        anc_siblings = list(ancestor.children)
        try:
            current_idx = anc_siblings.index(current)
        except ValueError:
            break
        # Check siblings after current in ancestor
        tail = anc_siblings[current_idx + 1:]
        for sib in tail:
            if isinstance(sib, _nodes.section):
                return sib
            if _is_skippable(sib):
                continue
            break
        # No next section found — keep climbing unless ancestor is document
        # (document root has no further parent to climb to)
        if isinstance(ancestor, _nodes.document):
            break
        # tail contained no section — keep climbing only if current is
        # the last meaningful item in ancestor
        if not all(_is_skippable(s) for s in tail):
            break
        current = ancestor

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


def _paragraph_anchor_title(node: "nodes.Node") -> str | None:
    """Return a title derived from a paragraph that immediately follows a target.

    Resolution rules:
    - bold-only (``**text**``): single ``strong`` child → its text
    - italic-only (``*text*``): single ``emphasis`` child → its text
    - bold-start (``**text** rest``): first child is ``strong`` → its text only
    - letter/digit + ``)`` + space (Issue #320): ``nodes.Text`` child matching
      ``^[a-zA-Z0-9]\\) `` (Nablarch 1.x ``\\e)`` / ``\\1)`` subsection convention —
      backslash stripped by docutils → plain paragraph) → full paragraph text
    - anything else (unmarked plain text, line_block, image, etc.) → ``None``
      (caller falls back to enclosing section)

    Called from :func:`_scan_rst_labels` after exhausting heading-based resolution.
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

    # Find the first non-skippable sibling after the target
    for sib in siblings[idx + 1:]:
        if isinstance(sib, (_nodes.target, _nodes.transition, _nodes.line_block)):
            continue
        if not isinstance(sib, _nodes.paragraph):
            return None
        # sib is a paragraph — extract title from its inline content
        children = list(sib.children)
        if not children:
            return None
        first = children[0]
        if isinstance(first, _nodes.strong) and len(children) == 1:
            # bold-only: **text**
            return first.astext()
        if isinstance(first, _nodes.emphasis) and len(children) == 1:
            # italic-only: *text*
            return first.astext()
        if isinstance(first, _nodes.strong):
            # bold-start: **text** (optional trailing text)
            return first.astext()
        if isinstance(first, _nodes.Text):
            import re as _re
            # letter/digit + ")" + space: Nablarch 1.x subsection list convention
            # (e.g. RST source ``\e) SQL文のロードクラス`` → plain paragraph ``e) SQL…``).
            # This structural pattern signals intentional heading use.
            if _re.match(r'^[a-zA-Z0-9]\) ', first.astext()):
                return sib.astext()
        return None
    return None


def _entry_parent_xparen_title(node: "nodes.Node") -> str | None:
    """Return an X) paragraph anchor title for a label whose parent is a table entry.

    Handles Rule 7 (§3-2-2): when a label lives inside a table cell (entry),
    the normal ``isinstance(node.parent, nodes.section)`` guard in
    ``_scan_rst_labels`` prevents ``_paragraph_anchor_title`` from running.

    Walk up from the label to the direct child of the enclosing section
    (``block_quote`` or ``table``), then look at the sibling immediately before
    it.  If that sibling is an X) paragraph (letter/digit + `)` + space), AND
    the sibling before that paragraph is a ``target`` node (meaning
    ``_walk_section`` will generate a synthetic section for this X) paragraph),
    return the paragraph text.  Otherwise return ``None`` so that the caller
    falls back to the enclosing section title.

    The ``target`` pre-condition mirrors ``_walk_section``'s synthetic-section
    boundary detection: only ``target + X) paragraph`` pairs produce a synthetic
    section in the knowledge JSON.  X) paragraphs with no preceding target are
    not turned into synthetic sections and therefore cannot serve as valid anchor
    targets.

    Applies only to v1.x sources (v5/v6 do not have this structure).
    """
    from docutils import nodes as _nodes
    import re as _re

    # Only handles entry-parent labels
    if not isinstance(node.parent, _nodes.entry):
        return None

    # Walk up to find the enclosing section
    p = node.parent
    while p is not None and not isinstance(p, _nodes.section):
        p = p.parent
    if p is None:
        return None
    enclosing_section = p

    # Find the direct child of the section that contains the label
    p2 = node.parent
    while p2 is not None and p2.parent is not enclosing_section:
        p2 = p2.parent
    if p2 is None:
        return None

    # Look at the sibling immediately before p2 (should be the X) paragraph)
    section_children = list(enclosing_section.children)
    try:
        idx = section_children.index(p2)
    except ValueError:
        return None
    if idx < 2:
        return None

    prev_sib = section_children[idx - 1]
    if not isinstance(prev_sib, _nodes.paragraph):
        return None
    children = list(prev_sib.children)
    if not children:
        return None
    first = children[0]
    if not (isinstance(first, _nodes.Text) and _re.match(r'^[a-zA-Z0-9]\) ', first.astext())):
        return None

    # Verify that the X) paragraph is preceded by a target node.
    # Only target + X) paragraph pairs cause _walk_section to generate a
    # synthetic section; X) paragraphs without a preceding target are plain
    # body text and must not be treated as anchor titles.
    prev_prev_sib = section_children[idx - 2]
    if not isinstance(prev_prev_sib, _nodes.target):
        return None

    return prev_sib.astext()


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
        # Skip external hyperlink definitions (`.. _Label: URL`).
        # These have a `refuri` attribute and are not section anchors.
        # Sphinx does not create an HTML anchor for them, so they must not
        # be registered in label_map (spec §3-2-2: label_map covers section
        # labels only).  Including them caused same-named section labels in
        # other files to be blocked by setdefault (v1.4 Bug 1: link.rst
        # `.. _ResponseMessage: ../../javadoc/...` blocked 01_Utility.rst).
        if node.get("refuri"):
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

        # Only attempt paragraph-anchor resolution when:
        # 1. no next section found (otherwise heading takes priority)
        # 2. parent is a section node (not block_quote, list, etc.)
        #    — OR — parent is entry (Rule 7: table-cell label, see below)
        # 3. NOT in h1 scope — h1-scoped files have DocTitle-promoted structure
        #    where _walk_section is never called, so no synthetic section is
        #    generated and the anchor would not exist in docs MD.
        if next_node is None and not in_h1_scope:
            if isinstance(node.parent, _nodes.section):
                para_title = _paragraph_anchor_title(node)
            elif isinstance(node.parent, _nodes.entry):
                # Rule 7: label inside table cell — look for X) paragraph
                # before the enclosing block_quote/table in the parent section.
                para_title = _entry_parent_xparen_title(node)
            else:
                para_title = None
        else:
            para_title = None

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
        elif para_title:
            # Label directly before a bold/italic paragraph (non-heading),
            # inside an h2+ section.  para_title is None for h1-scoped labels
            # (h1 DocTitle-promoted structure has no _walk_section call, so no
            # synthetic section would be generated).
            title = para_title
            section_title = para_title
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
