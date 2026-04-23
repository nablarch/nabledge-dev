"""RBKC verify — quality gate for RBKC output.

Checks that knowledge JSON files correctly represent their source documents.
See: tools/rbkc/docs/rbkc-verify-quality-design.md

Public API:
    verify_file(source_path, json_path, fmt, knowledge_dir) -> list[str]
    verify_docs_md(source_path, docs_md_path, fmt) -> list[str]
    check_index_coverage(knowledge_dir, index_path) -> list[str]
    check_docs_coverage(knowledge_dir, docs_dir) -> list[str]
    check_source_links(source_text, fmt, data, label_map, source_path) -> list[str]
    check_json_docs_md_consistency(data, docs_md_text) -> list[str]
    check_external_urls(source_text, data, fmt) -> list[str]
    check_content_completeness(source_text, data, fmt) -> list[str]
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.common.labels import build_label_map  # noqa: F401 (used by run.py)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _no_knowledge(data: dict) -> bool:
    return bool(data.get("no_knowledge_content"))


def _all_text(data: dict) -> str:
    """All JSON text fields concatenated for substring search (QL1/QL2)."""
    parts = [data.get("title", ""), data.get("content", "")]
    for s in data.get("sections", []):
        parts.append(s.get("title", ""))
        parts.append(s.get("content", ""))
    return "\n".join(p for p in parts)


# ---------------------------------------------------------------------------
# QO1 + QO2: check_json_docs_md_consistency
# ---------------------------------------------------------------------------

_H1_RE = re.compile(r'^#\s+(.+)$', re.MULTILINE)
# Per spec §3-3 QO1: a JSON section title may appear at `##` or `###`.
# However, docs.py only emits sections at `##`; a `###` in docs MD is a
# subheading inside a section's content (valid CommonMark). The "extra
# direction" check must therefore use `##` only to avoid false-positives.
# The "missing direction" check accepts either level.
_H2_ONLY_RE = re.compile(r'^##\s+(.+)$', re.MULTILINE)
_H2_OR_H3_RE = re.compile(r'^#{2,3}\s+(.+)$', re.MULTILINE)
# Back-compat name (kept for the top-content region-bounding in QO2 which
# already uses `##` first to locate the region boundary).
_H2_RE = _H2_OR_H3_RE

# Per CommonMark §4.2, an ATX heading accepts an optional trailing `#`
# sequence. Strip that closing sequence from the captured title so
# '# Title #' compares equal to 'Title'.
_ATX_CLOSE_RE = re.compile(r'\s+#+\s*$')


def _strip_atx_close(title: str) -> str:
    return _ATX_CLOSE_RE.sub('', title).strip()
# Fenced code blocks (CommonMark: triple-backtick OR triple-tilde). Headings
# inside a fence are content, not section markers — must be stripped before
# scanning H1/H2.
_FENCE_BLOCK_RE = re.compile(r'^(```|~~~).*?^\1', re.MULTILINE | re.DOTALL)


def _strip_fenced_code(md_text: str) -> str:
    """Return *md_text* with all fenced code blocks blanked out, preserving
    byte positions (spaces for content, newlines kept as-is).

    Used when scanning for H1/H2 so `## ...` inside ```markdown``` samples
    or other fenced content is not misread as a section title — and so the
    resulting match offsets are valid against the original text.
    """
    def _mask(m: re.Match) -> str:
        block = m.group(0)
        return "".join("\n" if ch == "\n" else " " for ch in block)
    return _FENCE_BLOCK_RE.sub(_mask, md_text)


_MD_LINK_RE = re.compile(r'(!?\[[^\]]*\])\(([^)]+)\)')


def _apply_asset_link_rewrite(text: str, docs_md_path, knowledge_dir) -> str:
    """Mirror docs.py's asset-link rewrite so QO2 compares like-for-like.

    docs.py rewrites ``assets/...`` links in the JSON content to paths
    relative to ``docs_md_path.parent`` when it emits docs MD. QO2's
    verbatim check therefore must apply the same transformation to the
    JSON side before comparing. This is NOT a tolerance: the verify
    pipeline independently computes the same transform and asserts
    that the result literally appears in docs MD.
    """
    import os
    from pathlib import Path as _Path
    if docs_md_path is None or knowledge_dir is None:
        return text
    assets_dir = _Path(knowledge_dir) / "assets"
    rel_prefix = os.path.relpath(assets_dir, _Path(docs_md_path).parent)

    def _replace(m: re.Match) -> str:
        bracket = m.group(1)
        url = m.group(2)
        if url.startswith("assets/"):
            rest = url[len("assets/"):]
            url = f"{rel_prefix}/{rest}"
        return f"{bracket}({url})"

    return _MD_LINK_RE.sub(_replace, text)


def check_json_docs_md_consistency(
    data: dict,
    docs_md_text: str,
    docs_md_path=None,
    knowledge_dir=None,
) -> list[str]:
    """QO1: structure (title/section titles/order) and QO2: content verbatim.

    ``docs_md_path`` / ``knowledge_dir`` are used only to mirror the
    asset-link rewrite docs.py applies on write. When they are omitted
    (legacy callers / unit tests without real paths), the rewrite is a
    no-op and QO2 is a strict verbatim check.
    """
    if _no_knowledge(data):
        return []

    issues: list[str] = []
    file_id = data.get("id", "?")
    json_title = data.get("title", "")
    sections = data.get("sections", [])
    top_content = data.get("content", "")

    # Strip fenced code blocks: headings inside ``` ... ``` are content
    # samples (often MD-in-MD examples), not section markers.
    docs_scan = _strip_fenced_code(docs_md_text)

    # QO1: title check. Spec §3-3 requires JSON top-level title == docs MD
    # `#` heading. Both sides must exist and match; an empty JSON title is
    # only valid when no_knowledge_content is set (handled earlier).
    m = _H1_RE.search(docs_scan)
    docs_title = _strip_atx_close(m.group(1).strip()) if m else ""
    if docs_title != json_title:
        issues.append(f"[QO1] {file_id}: title mismatch: JSON={json_title!r} docs={docs_title!r}")

    # QO1: section title order and presence.
    # Per spec §3-3 QO1: the `##` level in docs MD is reserved for section
    # titles; `###` is used only for subheadings *inside* a section's
    # content. The "extra" check therefore uses `##` only (a stray `###`
    # in content is valid). The "missing" check accepts either level so
    # that a converter promoting a section to `###` still reconciles.
    docs_h2_only_titles = [
        _strip_atx_close(m.group(1).strip())
        for m in _H2_ONLY_RE.finditer(docs_scan)
    ]
    docs_h2_or_h3_titles = [
        _strip_atx_close(m.group(1).strip())
        for m in _H2_OR_H3_RE.finditer(docs_scan)
    ]
    json_sec_titles = [s.get("title", "") for s in sections if s.get("title")]

    if not sections and docs_h2_only_titles:
        issues.append(f"[QO1] {file_id}: docs MD has section headings but JSON has no sections")
    else:
        if docs_h2_only_titles != json_sec_titles:
            missing = [t for t in json_sec_titles if t not in docs_h2_or_h3_titles]
            extra = [t for t in docs_h2_only_titles if t not in json_sec_titles]
            if missing:
                for t in missing:
                    issues.append(f"[QO1] {file_id}: section title missing in docs MD: {t!r}")
            if extra:
                for t in extra:
                    issues.append(f"[QO1] {file_id}: docs MD has extra section title not in JSON: {t!r}")
            if not missing and not extra:
                # Same entries, different order
                issues.append(
                    f"[QO1] {file_id}: section title order differs: JSON={json_sec_titles!r} docs={docs_h2_only_titles!r}"
                )

    # QO2: top-level content must appear verbatim *between the `#` heading
    # and the first `##` heading* (spec §3-3 "JSON top-level content が
    # docs MD `#` 見出し直下に完全一致で含まれている"). Because fenced code
    # blocks inside the top content can contain `#` / `##` tokens that
    # must not be read as section markers, we blank out fenced ranges
    # (same byte positions, spaces substituted) so the first real `##`
    # offset is accurate against the original text.
    if top_content:
        expected = _apply_asset_link_rewrite(top_content, docs_md_path, knowledge_dir)
        # Replace fence block bytes with spaces (preserve length + newlines).
        def _mask(m: re.Match) -> str:
            block = m.group(0)
            return "".join("\n" if ch == "\n" else " " for ch in block)
        masked = _FENCE_BLOCK_RE.sub(_mask, docs_md_text)
        h1_match = _H1_RE.search(masked)
        # The top-content region ends at the first section title. docs.py
        # emits sections at `##` only; a `###` is a subheading that belongs
        # to the top content (or to a section's body). Bounding at `##` is
        # required — otherwise a top-content `### subheading` truncates the
        # region and the top content appears to be missing.
        h2_match = _H2_ONLY_RE.search(masked)
        start = h1_match.end() if h1_match else 0
        end = h2_match.start() if h2_match else len(docs_md_text)
        top_region = docs_md_text[start:end] if start <= end else ""
        if expected not in top_region:
            issues.append(f"[QO2] {file_id}: top-level content not found verbatim directly below the # heading")

    # QO2: section content verbatim. Per spec §3-3 QO2 "JSON 各セクション
    # の content が docs MD に完全一致で含まれている" — unconditional.
    # Empty content satisfies the containment check trivially; no skip.
    for s in sections:
        content = s.get("content", "")
        title = s.get("title", "")
        expected = _apply_asset_link_rewrite(content, docs_md_path, knowledge_dir)
        if expected not in docs_md_text:
            issues.append(f"[QO2] {file_id}: section '{title}' content not found verbatim in docs MD")

    return issues


# ---------------------------------------------------------------------------
# QO3 + README count: check_docs_coverage
# ---------------------------------------------------------------------------

_README_COUNT_RE = re.compile(r'^(\d+)\s*ページ', re.MULTILINE)


def check_docs_coverage(knowledge_dir, docs_dir) -> list[str]:
    """QO3: every JSON knowledge file has a matching docs MD.

    Per rbkc-verify-quality-design.md §3-3: docs MD is a per-file derived
    artefact of its JSON. We require a 1:1 mapping between JSON relative
    path and docs MD relative path (``.json`` -> ``.md``).

    The README.md page count is still checked so a coverage mismatch is
    surfaced at a glance.
    """
    issues: list[str] = []
    kdir = Path(knowledge_dir)
    ddir = Path(docs_dir)

    readme = ddir / "README.md"
    readme_missing = not readme.exists()
    if readme_missing:
        issues.append(f"[QO3] README.md missing: {readme}")

    # Per-file existence check — JSON → MD direction.
    json_rel_paths: set[Path] = set()
    for json_path in sorted(kdir.rglob("*.json")):
        rel = json_path.relative_to(kdir).with_suffix(".md")
        json_rel_paths.add(rel)
        docs_md_path = ddir / rel
        if not docs_md_path.exists():
            issues.append(
                f"[QO3] docs MD missing for JSON: expected {rel} (from {json_path.relative_to(kdir)})"
            )

    # MD → JSON direction (Z-1 r7 QO3 F1): spec §3-3 requires bidirectional
    # "JSON↔MD 1:1 存在確認". A docs MD without a backing JSON is a dangling
    # artefact (user clicks into it from a search result, no source data).
    for md_path in sorted(ddir.rglob("*.md")):
        if md_path.name == "README.md":
            continue
        rel = md_path.relative_to(ddir)
        if rel not in json_rel_paths:
            issues.append(
                f"[QO3] dangling docs MD without matching JSON: {rel}"
            )

    if readme_missing:
        return issues

    # README page-count coherence check (spec §3-3 QO3 下位チェック).
    actual = len([p for p in ddir.rglob("*.md") if p.name != "README.md"])
    text = readme.read_text(encoding="utf-8")
    m = _README_COUNT_RE.search(text)
    if not m:
        issues.append(f"[QO3] README.md missing 'N ページ' declaration: {readme}")
    else:
        declared = int(m.group(1))
        if declared != actual:
            issues.append(
                f"[QO3] README.md count mismatch: declares {declared} ページ but found {actual} .md files"
            )
    return issues


# ---------------------------------------------------------------------------
# QO4: check_index_coverage
# ---------------------------------------------------------------------------

def check_index_coverage(knowledge_dir, index_path) -> list[str]:
    """QO4: index.toon must list exactly the content JSON files on disk.

    Per rbkc-verify-quality-design.md §3-3:
    - index.toon missing: every content JSON is reported as FAIL.
    - JSON on disk not in index.toon: FAIL (not searchable).
    - Path in index.toon without a matching JSON on disk: FAIL (dangling).
    """
    issues: list[str] = []
    kdir = Path(knowledge_dir)
    idx = Path(index_path)

    # Collect content JSON paths (relative) on disk. Per spec §3-3 point 4,
    # JSON parse failures are themselves QO4 FAIL (no silent skip).
    content_jsons: dict[str, Path] = {}
    for jf in sorted(kdir.rglob("*.json")):
        rel = str(jf.relative_to(kdir)).replace("\\", "/")
        try:
            d = json.loads(jf.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(f"[QO4] {rel}: JSON parse failed: {exc}")
            continue
        if d.get("no_knowledge_content"):
            continue
        content_jsons[rel] = jf

    if not idx.exists():
        # Spec: list every content JSON as FAIL because the search index
        # is missing entirely.
        if not content_jsons:
            return issues
        issues.append(f"[QO4] index.toon missing: {idx}")
        for rel in sorted(content_jsons):
            issues.append(f"[QO4] {rel}: JSON not registered in index.toon (index.toon absent)")
        return issues

    # Parse index paths from index.toon.
    # TOON format: header "files[N,]{cols}:" then indented rows
    # with comma-separated fields; path is the last field.
    lines = idx.read_text(encoding="utf-8").splitlines()
    indexed_paths: set[str] = set()
    in_table = False
    for line in lines:
        stripped = line.strip()
        if not in_table:
            if stripped.startswith("files[") and stripped.endswith(":"):
                in_table = True
            continue
        if not line.startswith("  ") or not stripped:
            continue
        last_comma = stripped.rfind(",")
        if last_comma < 0:
            continue
        indexed_paths.add(stripped[last_comma + 1:].strip())

    # Forward: every content JSON must appear in the index.
    for rel in sorted(content_jsons):
        if rel not in indexed_paths:
            issues.append(f"[QO4] {Path(rel).name}: JSON not registered in index.toon: {rel}")

    # Reverse: every path in the index must correspond to a real file on disk.
    for rel in sorted(indexed_paths):
        if rel not in content_jsons:
            issues.append(f"[QO4] index.toon lists missing JSON: {rel}")

    return issues


# ---------------------------------------------------------------------------
# QC5: 形式純粋性
# ---------------------------------------------------------------------------

# Spec §3-1 QC5: `:role:`text`` — both opening AND closing backticks are
# part of the named pattern (see rbkc.md "Decide from the spec" entry).
_RST_ROLE_RE = re.compile(r':[a-zA-Z][a-zA-Z0-9_.-]*:`[^`\n]+`')
_RST_DIRECTIVE_RE = re.compile(r'^\.\.\s+[A-Za-z][\w:-]*::', re.MULTILINE)
_RST_HEADING_UNDERLINE_RE = re.compile(r'^[=\-~^"\'`#*+<>]{4,}\s*$', re.MULTILINE)
# Spec §3-1 QC5: `.. _label:` is an RST explicit-markup construct; the RST
# spec requires it to start at line begin. Mid-sentence occurrences are not
# label definitions.
_RST_LABEL_RE = re.compile(r'^\.\.\s+_[a-zA-Z0-9_-]+:\s*$', re.MULTILINE)
_MD_RAW_HTML_RE = re.compile(r'<[a-zA-Z][a-zA-Z0-9]*(?:\s[^>]*)?/?>')
_MD_BACKSLASH_ESCAPE_RE = re.compile(r'\\[*_`\[\](){}#+\-.!|]')


def _rst_syntax_issues(text: str, location: str, *, is_title: bool = False) -> list[str]:
    issues = []
    if _RST_ROLE_RE.search(text):
        issues.append(f"[QC5] {location}: RST role syntax detected (e.g. :role:`text`)")
    if _RST_DIRECTIVE_RE.search(text):
        issues.append(f"[QC5] {location}: RST directive syntax detected (e.g. .. directive::)")
    if _RST_LABEL_RE.search(text):
        issues.append(f"[QC5] {location}: RST label definition detected (e.g. .. _label:)")
    if is_title and _RST_HEADING_UNDERLINE_RE.search(text):
        issues.append(f"[QC5] {location}: RST heading underline detected (e.g. ====)")
    return issues


def _md_syntax_issues(text: str, location: str) -> list[str]:
    issues = []
    if _MD_RAW_HTML_RE.search(text):
        issues.append(f"[QC5] {location}: raw HTML tag detected (e.g. <details>, <br>)")
    if _MD_BACKSLASH_ESCAPE_RE.search(text):
        issues.append(f"[QC5] {location}: backslash escape detected (e.g. \\*)")
    return issues


def _check_format_purity(data: dict, fmt: str) -> list[str]:
    if fmt == "xlsx" or _no_knowledge(data):
        return []
    issues = []
    file_id = data.get("id", "?")

    title = data.get("title", "")
    top_content = data.get("content", "")

    if fmt == "rst":
        issues.extend(_rst_syntax_issues(title, f"{file_id}/title", is_title=True))
        if top_content:
            issues.extend(_rst_syntax_issues(top_content, f"{file_id}/content"))
        for s in data.get("sections", []):
            st = s.get("title", "")
            sc = s.get("content", "")
            issues.extend(_rst_syntax_issues(st, f"{file_id}/section '{st}'/title", is_title=True))
            issues.extend(_rst_syntax_issues(sc, f"{file_id}/section '{st}'/content"))
    elif fmt == "md":
        issues.extend(_md_syntax_issues(title, f"{file_id}/title"))
        if top_content:
            issues.extend(_md_syntax_issues(top_content, f"{file_id}/content"))
        for s in data.get("sections", []):
            st = s.get("title", "")
            sc = s.get("content", "")
            issues.extend(_md_syntax_issues(st, f"{file_id}/section '{st}'/title"))
            issues.extend(_md_syntax_issues(sc, f"{file_id}/section '{st}'/content"))
    return issues


# ---------------------------------------------------------------------------
# QL2: 外部URL一致
# ---------------------------------------------------------------------------

def _source_urls(source_text: str, fmt: str) -> list[str]:
    """Extract external URLs actually visible to readers.

    Per §3-2 AST-only principle: URLs come from AST node attributes, never
    from raw-text regex scans. RST uses docutils' `reference.refuri`; MD
    uses markdown-it-py's `link_open[href]` (collected by the Visitor).
    """
    urls: list[str] = []
    if fmt == "rst":
        from docutils import nodes
        from scripts.common import rst_ast

        try:
            doctree, _ = rst_ast.parse(source_text)
        except Exception:
            return urls

        def _in_substitution(node) -> bool:
            """Per spec §3-2 line 268: substitution bodies are excluded
            by AST-attribute check. Walk ancestors and skip references
            whose definition lives under a substitution_definition —
            those URLs are not directly visible to the reader."""
            cur = node.parent
            while cur is not None:
                if isinstance(cur, nodes.substitution_definition):
                    return True
                cur = cur.parent
            return False

        for ref in doctree.findall(nodes.reference):
            if _in_substitution(ref):
                continue
            refuri = ref.get("refuri", "")
            if refuri.startswith(("http://", "https://")):
                urls.append(refuri)
        return urls

    if fmt == "md":
        from scripts.common import md_ast, md_ast_visitor

        try:
            tokens = md_ast.parse(source_text)
            parts = md_ast_visitor.extract_document(tokens)
        except Exception:
            return urls
        return list(parts.external_urls)

    return urls


def check_external_urls(source_text: str, data: dict, fmt: str) -> list[str]:
    """QL2: External URLs in source must appear verbatim in JSON.

    §3-2 AST-only principle: source URLs come from the doctree
    `reference.refuri` attributes (see `_source_urls`). For JSON we do a
    substring presence check — a URL is considered reflected when its
    exact string appears somewhere in JSON content (handles URLs that
    contain parentheses etc. without regex boundary errors).
    """
    if fmt == "xlsx" or _no_knowledge(data):
        return []

    src_urls = _source_urls(source_text, fmt)
    if not src_urls:
        return []

    json_text = _all_text(data)

    issues = []
    seen: set[str] = set()
    for url in src_urls:
        if url in seen:
            continue
        seen.add(url)
        if url not in json_text:
            issues.append(f"[QL2] external URL missing from JSON: {url}")
    return issues


# ---------------------------------------------------------------------------
# QC1-QC4: sequential-delete algorithm (RST/MD)
# ---------------------------------------------------------------------------

def _normalize_rst_source(text: str, label_map: dict | None = None) -> str:
    """Normalize RST markup to plain text for comparison with JSON content.

    Delegates to :func:`scripts.common.rst_normaliser.normalise_rst`, which
    implements the docutils-AST normalisation specified in
    `rbkc-verify-quality-design.md` §3-1 手順 0.
    """
    from scripts.common.rst_normaliser import normalise_rst
    return normalise_rst(text, label_map=label_map or {}, strict_unknown=True)


def _build_rst_search_units(
    data: dict,
) -> list[tuple[str, str, str, bool]]:
    """Build (original_unit, normalized_unit, sid, is_content) for RST content.

    Per the tokenizer-based design (rbkc-verify-quality-design.md §3-1 手順
    0), the normalised source is already in MD-equivalent form, so JSON
    content can be matched against it after only whitespace normalisation.
    """
    units: list[tuple[str, str, str, bool]] = []
    top_title = data.get("title", "")
    top_content = data.get("content", "")

    def _norm(t: str) -> str:
        # Per spec §3-1 "残存判定の基準", the normalised source (Visitor
        # output) and JSON content share the same MD syntax by
        # construction — no post-normalisation is permitted on the verify
        # side. The only transform here is whitespace collapse to match
        # the same collapse applied to the source (see
        # _check_rst_content_completeness).
        return re.sub(r'\s+', ' ', t).strip()

    if top_title:
        units.append((top_title, _norm(top_title), "__top__", False))
    if top_content:
        norm = _norm(top_content)
        if norm:
            units.append((top_content, norm, "__top__", True))

    for sec in data.get("sections", []):
        title = sec.get("title", "")
        content = sec.get("content", "")
        sid = sec.get("id", "?")
        if title:
            units.append((title, _norm(title), sid, False))
        if content:
            norm = _norm(content)
            if norm:
                units.append((content, norm, sid, True))

    return units


def check_content_completeness(source_text: str, data: dict, fmt: str, label_map: dict | None = None) -> list[str]:
    """QC1/QC2/QC3/QC4: sequential-delete algorithm."""
    if _no_knowledge(data):
        return []

    sections = data.get("sections", [])
    top_title = data.get("title", "")
    top_content = data.get("content", "")

    if not sections and not top_title and not top_content:
        return []

    issues: list[str] = []

    if fmt == "rst":
        return _check_rst_content_completeness(source_text, data, issues, label_map)
    elif fmt == "md":
        return _check_md_content_completeness(source_text, data, issues)
    return issues


def _classify_missed_unit(
    norm_source: str,
    norm_unit: str,
    consumed: list[tuple[int, int]],
    in_consumed,
) -> str:
    """Classify a sequential-delete miss as QC2, QC3, or QC4 per spec §3-1.

    Spec decision table (§3-1 判定分岐のまとめ):
      - Unit does not appear anywhere in normalised source → QC2 (fabricated)
      - Unit appears but every earlier occurrence is already consumed
        (先行削除済み) → QC3 (duplicate)
      - Unit appears with at least one unconsumed earlier occurrence
        → QC4 (misplaced; position regression)

    The spec's "先行削除済み" requires *every* earlier occurrence to be
    consumed. A naive `find(unit)` that picks only the earliest
    occurrence misclassifies the case where the earliest is consumed
    but a middle occurrence is still unconsumed (the unit occurs 3+
    times with a mixed consumption pattern).
    """
    if not norm_unit:
        return "QC2"
    start = 0
    any_occurrence = False
    has_unconsumed = False
    while True:
        pos = norm_source.find(norm_unit, start)
        if pos == -1:
            break
        any_occurrence = True
        if not in_consumed(pos, len(norm_unit)):
            has_unconsumed = True
            break
        start = pos + 1
    if not any_occurrence:
        return "QC2"
    if has_unconsumed:
        return "QC4"
    return "QC3"


def _check_rst_content_completeness(
    source_text: str, data: dict, issues: list[str], label_map: dict | None = None
) -> list[str]:
    """QC1-QC4 for RST sources using normalized comparison.

    RST markup (``code``, :ref:, `text <url>`_) is normalized to plain text
    on both sides before comparison, eliminating false positives from
    RST-to-Markdown conversion differences.
    """
    # Collect substitutions once from the full source so per-line normalisation
    # can resolve `|name|` references defined elsewhere in the file.
    # Per rbkc-verify-quality-design.md §3-1b, Visitor-level errors (unknown
    # node / unknown role / unresolved reference / parse error) are QC1 FAIL,
    # not silent fallbacks.
    from scripts.common.rst_normaliser import UnknownSyntaxError
    try:
        norm_source_raw = _normalize_rst_source(source_text, label_map)
    except UnknownSyntaxError as exc:
        issues.append(f"[QC1] RST parse/visitor error: {exc}")
        return issues
    # Per spec §3-1 "残存判定の基準": the shared Visitor already produces
    # MD-equivalent output; no verify-only post-normalisation is permitted.
    # Collapse whitespace only, to match _build_rst_search_units._norm.
    norm_source = re.sub(r'\s+', ' ', norm_source_raw).strip()
    search_units = _build_rst_search_units(data)

    if not search_units:
        return issues

    consumed: list[tuple[int, int]] = []
    current_pos = 0

    def _in_consumed(pos: int, length: int) -> bool:
        end = pos + length
        return any(pos < e and end > s for s, e in consumed)

    for orig_unit, norm_unit, sid, is_content in search_units:
        idx = norm_source.find(norm_unit, current_pos)
        if idx != -1:
            consumed.append((idx, idx + len(norm_unit)))
            current_pos = idx + len(norm_unit)
        else:
            verdict = _classify_missed_unit(norm_source, norm_unit, consumed, _in_consumed)
            label = "title" if not is_content else "content"
            if verdict == "QC2":
                issues.append(f"[QC2] section '{sid}': fabricated {label}: {orig_unit[:50]!r}")
            elif verdict == "QC4":
                issues.append(f"[QC4] section '{sid}': misplaced {label}: {orig_unit[:50]!r}")
            else:  # QC3
                issues.append(f"[QC3] section '{sid}': duplicate {label}: {orig_unit[:50]!r}")

    # QC1: residual check on the normalised source (no tolerance list).
    # Per `.claude/rules/rbkc.md` ("RST one-snippet vs MD all-fragments —
    # All fragments"), RST must report every non-whitespace residue
    # fragment, not a single truncated snippet. Mirror the MD path below.
    if consumed:
        consumed_sorted = sorted(consumed)
        merged: list[list[int]] = []
        for s, e in consumed_sorted:
            if merged and s <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s, e])
        buf: list[str] = []
        prev_end = 0
        for s, e in merged:
            buf.append(norm_source[prev_end:s])
            prev_end = e
        buf.append(norm_source[prev_end:])
        remaining = "".join(buf)
    else:
        remaining = norm_source

    if remaining.strip():
        for frag in remaining.split():
            if frag:
                issues.append(f"[QC1] RST source content not captured: {frag[:50]!r}")

    return issues


def _check_md_content_completeness(
    source_text: str, data: dict, issues: list[str]
) -> list[str]:
    """QC1-QC4 for MD sources using AST-normalised comparison.

    Per rbkc-verify-quality-design.md §3-1: the source is parsed by the
    shared md_ast Visitor (same code create uses) to produce a normalised
    MD string, then JSON search units are sequential-deleted from it.
    Any non-whitespace residue is a QC1 FAIL (no tolerance list).
    """
    from scripts.common.md_normaliser import UnknownSyntaxError, normalise_md

    try:
        norm_source = normalise_md(source_text, strict_unknown=True)
    except UnknownSyntaxError as exc:
        issues.append(f"[QC1] markdown parse/visitor error: {exc}")
        return issues

    # Collapse whitespace to match the same normalisation applied to
    # JSON units; sequential-delete then operates on a single-line view.
    def _squash(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    norm_source = _squash(norm_source)

    top_title = data.get("title", "")
    top_content = data.get("content", "")

    search_units: list[tuple[str, str, bool]] = []
    if top_title:
        search_units.append((_squash(top_title), "__top__", False))
    if top_content:
        search_units.append((_squash(top_content), "__top__", True))

    for sec in data.get("sections", []):
        title = sec.get("title", "")
        content = sec.get("content", "")
        sid = sec.get("id", "?")
        if title:
            search_units.append((_squash(title), sid, False))
        if content:
            search_units.append((_squash(content), sid, True))

    if not search_units:
        return issues

    consumed: list[tuple[int, int]] = []
    current_pos = 0

    def _in_consumed(pos: int, length: int) -> bool:
        end = pos + length
        return any(pos < e and end > s for s, e in consumed)

    for unit, sid, is_content in search_units:
        idx = norm_source.find(unit, current_pos)
        if idx != -1:
            consumed.append((idx, idx + len(unit)))
            current_pos = idx + len(unit)
        else:
            verdict = _classify_missed_unit(norm_source, unit, consumed, _in_consumed)
            label = "title" if not is_content else "content"
            if verdict == "QC2":
                issues.append(f"[QC2] section '{sid}': fabricated {label}: {unit[:50]!r}")
            elif verdict == "QC4":
                issues.append(f"[QC4] section '{sid}': misplaced {label}: {unit[:50]!r}")
            else:  # QC3
                issues.append(f"[QC3] section '{sid}': duplicate {label}: {unit[:50]!r}")

    # QC1: residual check on the normalised source (no tolerance list).
    if consumed:
        consumed.sort()
        merged: list[list[int]] = []
        for s, e in consumed:
            if merged and s <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s, e])
        buf: list[str] = []
        prev = 0
        for s, e in merged:
            buf.append(norm_source[prev:s])
            prev = e
        buf.append(norm_source[prev:])
        remaining = "".join(buf)
    else:
        remaining = norm_source

    # Anything other than whitespace left over is a QC1 FAIL.
    if remaining.strip():
        # Report at most a few residue fragments for readability.
        for frag in remaining.split():
            if frag:
                issues.append(f"[QC1] source content not captured: {frag[:50]!r}")

    return issues


# ---------------------------------------------------------------------------
# Excel QC1/QC2/QC3: verify_file(fmt="xlsx")
# ---------------------------------------------------------------------------

_MD_SYNTAX_RE = re.compile(
    r'\|[-:]+\|(?:[-:]+\|)*'
    r'|\|'
    r'|\*\*|\*|__(?![\w])|(?<![\w])__'
    r'|^#+\s*'
    r'|^>\s*'
    r'|^\d+\.\s+'
    r'|`'
    , re.MULTILINE
)


def _xlsx_source_tokens(source_path) -> list[str]:
    ext = Path(source_path).suffix.lower()
    if ext == ".xls":
        import xlrd
        wb = xlrd.open_workbook(str(source_path))
        tokens = []
        for sheet in wb.sheets():
            for rx in range(sheet.nrows):
                for cx in range(sheet.ncols):
                    val = str(sheet.cell_value(rx, cx)).strip()
                    if val:
                        tokens.append(val)
        return tokens
    else:
        import openpyxl
        wb = openpyxl.load_workbook(str(source_path), data_only=True)
        tokens = []
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                for cell in row:
                    if cell is None:
                        continue
                    val = str(cell).strip()
                    if val:
                        tokens.append(val)
        return tokens


def _xlsx_json_text(data: dict) -> str:
    parts = [data.get("title", ""), data.get("content", "")]
    for s in data.get("sections", []):
        if s.get("title"):
            parts.append(s["title"])
        if s.get("content"):
            parts.append(s["content"])
    return "\n".join(p for p in parts if p)


def _verify_xlsx(source_path, data: dict) -> list[str]:
    if _no_knowledge(data):
        return []

    tokens = _xlsx_source_tokens(source_path)
    if not tokens:
        return []

    json_text = _xlsx_json_text(data)
    if not json_text.strip():
        return []

    issues: list[str] = []
    consumed: list[tuple[int, int]] = []
    search_start = 0

    def _in_consumed(pos: int, length: int) -> bool:
        end = pos + length
        return any(pos < e and end > s for s, e in consumed)

    for token in tokens:
        idx = json_text.find(token, search_start)
        if idx != -1:
            consumed.append((idx, idx + len(token)))
            search_start = idx + len(token)
        else:
            prev_idx = json_text.find(token)
            if prev_idx == -1:
                issues.append(f"[QC1] Excel cell value missing from JSON: {token!r}")
            elif _in_consumed(prev_idx, len(token)):
                issues.append(f"[QC3] Excel cell value duplicated in JSON: {token!r}")
            else:
                issues.append(f"[QC1] Excel cell value missing from JSON: {token!r}")

    # QC2: residual JSON text not from any source cell
    if consumed:
        consumed.sort()
        merged: list[list[int]] = []
        for s, e in consumed:
            if merged and s <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s, e])
        parts: list[str] = []
        prev = 0
        for s, e in merged:
            parts.append(json_text[prev:s])
            prev = e
        parts.append(json_text[prev:])
        residual = "".join(parts)
    else:
        residual = json_text

    # Per spec §3-1 Excel 節 手順 3: anything other than whitespace/empty
    # remaining after deleting source cells is QC2 (捏造). No length
    # tolerance — a 1-char residue is still a fabrication.
    residual_plain = _MD_SYNTAX_RE.sub(" ", residual)
    for token in residual_plain.split():
        t = token.strip()
        if t:
            issues.append(f"[QC2] JSON token not found in Excel source: {token!r}")

    return issues


# ---------------------------------------------------------------------------
# verify_file: dispatch per format
# ---------------------------------------------------------------------------

def verify_file(source_path, json_path, fmt, knowledge_dir=None, label_map=None) -> list[str]:
    """Per-file JSON checks (QC1-QC5, QL2)."""
    if not Path(json_path).exists():
        return []

    data = json.loads(Path(json_path).read_text(encoding="utf-8"))

    if _no_knowledge(data):
        return []

    if fmt == "xlsx":
        return _verify_xlsx(source_path, data)

    if fmt in ("rst", "md"):
        source_text = Path(source_path).read_text(encoding="utf-8", errors="replace")
        issues: list[str] = []
        issues.extend(check_content_completeness(source_text, data, fmt, label_map))
        issues.extend(_check_format_purity(data, fmt))
        issues.extend(check_external_urls(source_text, data, fmt))
        return issues

    return []


# ---------------------------------------------------------------------------
# verify_docs_md: stub (QO1/QO2 handled via check_json_docs_md_consistency)
# ---------------------------------------------------------------------------

def verify_docs_md(source_path, docs_md_path, fmt) -> list[str]:
    """Per-file docs MD checks beyond JSON↔MD consistency. Stub."""
    return []


# ---------------------------------------------------------------------------
# QL1: check_source_links
# ---------------------------------------------------------------------------

def _resolve_title_inline(title_node, label_map: dict) -> str:
    r"""Render an RST section title to plain text, resolving any embedded
    ``:ref:`label``` / `` `Label`_ `` references via label_map.

    docutils stores unresolved inline references inside the title as
    ``inline`` (class role-ref) or ``reference`` nodes. ``astext()``
    returns their raw text form (the bare label name), which does not
    match what the create-side converter emits (the label's target
    title). Walking the title children and swapping those nodes for
    their resolved form makes the verify string match the JSON string.
    """
    from docutils import nodes
    parts: list[str] = []
    for child in title_node.children:
        if isinstance(child, nodes.inline):
            cls = child.get("classes") or []
            if any(c.startswith("role-") for c in cls):
                role = next((c[5:] for c in cls if c.startswith("role-")), "")
                raw = child.astext().strip()
                if role == "ref":
                    if "<" in raw and raw.rstrip().endswith(">"):
                        disp, _, _ = raw.rpartition("<")
                        parts.append(disp.strip())
                    else:
                        parts.append(label_map.get(raw, raw))
                    continue
                # Other roles: render the raw text (converter does the same).
                parts.append(raw)
                continue
        if isinstance(child, nodes.reference):
            refid = (child.get("refid", "") or "").strip()
            if refid and refid in label_map:
                parts.append(label_map[refid])
            else:
                parts.append(child.astext())
            continue
        parts.append(child.astext())
    return "".join(parts)



def check_source_links(
    source_text: str,
    fmt: str,
    data: dict,
    label_map: dict,
    source_path=None,
) -> list[str]:
    """QL1: Internal links in source must be reflected in JSON.

    Per rbkc-verify-quality-design.md §3-2: extract link candidates from the
    docutils AST (no regex-based source scanning).
    """
    if fmt == "xlsx" or _no_knowledge(data):
        return []

    json_full = _all_text(data)
    issues: list[str] = []

    if fmt == "rst":
        from docutils import nodes
        from scripts.common import rst_ast
        from pathlib import Path as _Path

        try:
            doctree, _warn = rst_ast.parse(source_text, source_path=source_path)
        except Exception:
            # docutils failed — QC1 will already have flagged it via the
            # normaliser; avoid a redundant QL1 FAIL.
            return issues

        # Native RST named references: `.. _label:` + `\`Label\`_` produce a
        # reference node whose `refid` points at a target inside the same
        # doctree (docutils resolves the name during parsing). Per spec §3-2
        # row 1, the reader-visible string (the target section's title)
        # must appear in JSON.
        #
        # We look up `doctree.ids[refid]` and read the resolved section
        # title. Auto-generated anchors (docutils synthesises them for TOC /
        # contents directives) are skipped: their refid uses `id-N` /
        # `section-N` patterns and the target is not a user-defined label,
        # so they are navigation artefacts already covered by QC1.
        _AUTO_ID_RE = re.compile(r"^(?:id|section)-\d+$")
        for ref in doctree.findall(nodes.reference):
            refuri = ref.get("refuri", "")
            if refuri:  # external link — handled by QL2
                continue
            refid = (ref.get("refid", "") or "").strip()
            if not refid or _AUTO_ID_RE.match(refid):
                continue
            target = doctree.ids.get(refid)
            if target is None or not isinstance(target, nodes.section):
                continue
            # Resolved title = the target section's first `title` child.
            title_node = next(
                (c for c in target.children if isinstance(c, nodes.title)),
                None,
            )
            if title_node is None:
                continue
            # When the title itself embeds `:ref:\`label\`` / named refs,
            # render it through the create-side label_map so the string we
            # check against JSON matches what the converter emitted.
            resolved = _resolve_title_inline(title_node, label_map).strip()
            if resolved and resolved not in json_full:
                issues.append(
                    f"[QL1] RST named reference '{refid}' target title missing from JSON: {resolved!r}"
                )

        # :ref: role references (Sphinx shim produces inline with class role-ref)
        seen_labels: set[str] = set()
        for n in doctree.findall(nodes.inline):
            cls = n.get("classes") or []
            if not any(c.startswith("role-") for c in cls):
                continue
            role = next(c[5:] for c in cls if c.startswith("role-"))
            if role != "ref":
                continue
            raw = n.astext().strip()
            if "<" in raw and raw.rstrip().endswith(">"):
                text, _, tgt = raw.rpartition("<")
                display = text.strip()
                label = tgt.rstrip(">").strip()
            else:
                display = ""
                label = raw
            # Display-text form: the display string must appear in JSON
            if display and display not in json_full:
                issues.append(
                    f"[QL1] :ref: display text missing from JSON: {display!r}"
                )
            # Bare label form: the resolved target title must appear
            if not display and label not in seen_labels:
                seen_labels.add(label)
                title = label_map.get(label)
                if title and title not in json_full:
                    issues.append(
                        f"[QL1] :ref:`{label}` target title missing from JSON: {title!r}"
                    )

        def _under_substitution(node) -> bool:
            """True if *node* lives under a substitution_definition subtree.

            Per spec §3-2 symmetry with QL2 (line 268) and rbkc.md decision
            ("QL1 substitution-body image — include or exclude? → Exclude"),
            images and figures defined inside a substitution body are not
            QL1 targets; the visible occurrence is covered by the paragraph
            where the substitution reference is rendered.
            """
            cur = node.parent
            while cur is not None:
                if isinstance(cur, nodes.substitution_definition):
                    return True
                cur = cur.parent
            return False

        # figure nodes — dedup matches the MD branch's seen_images.
        seen_rst_figures: set[str] = set()
        for fig in doctree.findall(nodes.figure):
            if _under_substitution(fig):
                continue
            caption_text = ""
            uri = ""
            for ch in fig.children:
                if isinstance(ch, nodes.caption):
                    caption_text = ch.astext().strip()
                elif isinstance(ch, nodes.image):
                    uri = ch.get("uri", "")
            caption_for_check = caption_text if _has_visible_text(caption_text) else ""
            check_text = caption_for_check or (_Path(uri).name if uri else "")
            if not check_text or check_text in seen_rst_figures:
                continue
            seen_rst_figures.add(check_text)
            if check_text not in json_full:
                issues.append(
                    f"[QL1] figure caption/filename missing from JSON: {check_text!r}"
                )

        # image nodes outside figures — dedup to match MD branch behaviour.
        seen_rst_images: set[str] = set()
        for img in doctree.findall(nodes.image):
            if isinstance(img.parent, nodes.figure):
                continue
            if _under_substitution(img):
                continue
            alt = (img.get("alt") or "").strip()
            uri = img.get("uri", "")
            check_text = alt or (_Path(uri).name if uri else "")
            if not check_text or check_text in seen_rst_images:
                continue
            seen_rst_images.add(check_text)
            if check_text not in json_full:
                issues.append(
                    f"[QL1] image alt/filename missing from JSON: {check_text!r}"
                )

        # NOTE: literal_block content is covered by QC1/QC2 (sequential-delete
        # across the full JSON content), so we don't re-check it here.

    elif fmt == "md":
        from scripts.common import md_ast, md_ast_visitor
        from pathlib import Path as _Path

        try:
            tokens = md_ast.parse(source_text)
            parts = md_ast_visitor.extract_document(tokens)
        except Exception:
            return issues
        seen_link_texts: set[str] = set()
        for link_text, _href in parts.internal_links:
            t = link_text.strip()
            if not t or t in seen_link_texts:
                continue
            seen_link_texts.add(t)
            if t not in json_full:
                issues.append(f"[QL1] internal link text missing from JSON: {t!r}")

        # Images: prefer alt text; then title; then filename. Per spec §3-2
        # "Markdown inline image" row: alt / title / src filename.
        seen_images: set[str] = set()
        for alt, src, title in parts.images:
            check = alt.strip() or title.strip() or (_Path(src).name if src else "")
            if not check or check in seen_images:
                continue
            seen_images.add(check)
            if check not in json_full:
                issues.append(f"[QL1] image alt/title/filename missing from JSON: {check!r}")

    return issues


def _has_visible_text(s: str) -> bool:
    """Return True if *s* contains characters that should be content.

    RST inline-only captions like "[1]_" / ":ref:`x`" / "`foo`_" are filtered
    out here: they carry no prose and should not be used as caption text for
    QL1 comparison (filename fallback applies).
    """
    if not s:
        return False
    # Strip RST inline constructs; if anything non-whitespace remains, it's
    # visible.
    import re as _re
    stripped = _re.sub(r"`[^`]*`_{1,2}", "", s)
    stripped = _re.sub(r":[a-zA-Z][\w.:-]*:`[^`]*`", "", stripped)
    stripped = _re.sub(r"\[[^\]]+\]_", "", stripped)
    stripped = _re.sub(r"[\s*`]+", "", stripped)
    return bool(stripped)
