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
# Phase 22-B-16a: JSON `sections[].level` records the intended heading depth
# (h2=2, h3=3, h4=4).  Docs MD emits `#` repeated `level` times.  QO1 level
# check matches JSON level with the docs MD heading that bears the same
# title.
_HEADING_RE = re.compile(r'^(#{2,6})\s+(.+)$', re.MULTILINE)
# Legacy names kept for existing QO1 title-order / top-region bounding
# logic.  `_H2_ONLY_RE` still bounds the top-content region (top-level
# content ends at the first `##`); `_H2_OR_H3_RE` is kept as the
# "accepts either level" form for backward compatibility.
_H2_ONLY_RE = re.compile(r'^##\s+(.+)$', re.MULTILINE)
_H2_OR_H3_RE = re.compile(r'^#{2,4}\s+(.+)$', re.MULTILINE)
_H2_RE = _H2_OR_H3_RE

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
    docs_title = m.group(1).strip() if m else ""
    if docs_title != json_title:
        issues.append(f"[QO1] {file_id}: title mismatch: JSON={json_title!r} docs={docs_title!r}")

    # QO1 Excel P1 例外 (spec §3-3): P1 docs MD is a restored MD table
    # (§8-5) — row-level sections are table rows, not `##` headings.
    # Section-title ordering for P1 is verified by §3-4 QP instead.
    # Skip the ##-based section-title loop for P1 only; `#` title above
    # is already checked.
    if data.get("sheet_type") != "P1":
        # QO1: section title order and presence.
        # Phase 22-B-16a: docs MD may emit `##`/`###`/`####` depending on
        # `sections[].level`. Collect every heading and its level so we can
        # check both title order and level alignment.
        docs_headings: list[tuple[int, str]] = []
        for m in _HEADING_RE.finditer(docs_scan):
            hashes, title = m.group(1), m.group(2).strip()
            docs_headings.append((len(hashes), title))
        docs_h2_only_titles = [t for lvl, t in docs_headings if lvl == 2]
        # The "missing" check still accepts any heading level ≥ 2.
        docs_all_titles = [t for _, t in docs_headings]
        json_sec_titles = [s.get("title", "") for s in sections if s.get("title")]

        if not sections and docs_h2_only_titles:
            issues.append(f"[QO1] {file_id}: docs MD has section headings but JSON has no sections")
        else:
            missing = [t for t in json_sec_titles if t not in docs_all_titles]
            extra = [t for t in docs_h2_only_titles if t not in json_sec_titles]
            filtered = [t for t in docs_all_titles if t in json_sec_titles]
            if missing:
                for t in missing:
                    issues.append(f"[QO1] {file_id}: section title missing in docs MD: {t!r}")
            if extra:
                for t in extra:
                    issues.append(f"[QO1] {file_id}: docs MD has extra section title not in JSON: {t!r}")
            if not missing and not extra and filtered != json_sec_titles:
                issues.append(
                    f"[QO1] {file_id}: section title order differs: JSON={json_sec_titles!r} docs={filtered!r}"
                )

            # Phase 22-B-16a QO1 level check: every JSON section must
            # declare `level` and docs MD's heading for that title must
            # have `#` count equal to `level`.
            docs_title_to_levels: dict[str, list[int]] = {}
            for lvl, t in docs_headings:
                docs_title_to_levels.setdefault(t, []).append(lvl)
            used_idx: dict[str, int] = {}
            for s in sections:
                title = s.get("title", "")
                if not title:
                    continue
                if "level" not in s:
                    issues.append(
                        f"[QO1] {file_id}: section {title!r} missing required 'level' field"
                    )
                    continue
                declared = s.get("level")
                levels_for_title = docs_title_to_levels.get(title, [])
                idx = used_idx.get(title, 0)
                if idx >= len(levels_for_title):
                    # Already reported as "missing in docs MD" above;
                    # no extra level message needed.
                    continue
                actual = levels_for_title[idx]
                used_idx[title] = idx + 1
                if declared != actual:
                    issues.append(
                        f"[QO1] {file_id}: section {title!r} level mismatch — "
                        f"JSON level={declared}, docs MD heading has {actual} `#`"
                    )

    # QO2 Excel P1 例外 (spec §3-3): per-sheet Excel JSON whose
    # sheet_type == "P1" cannot be checked verbatim because docs MD renders
    # the row as an MD table — the column headers and `|---|` separators
    # are only in the MD side. Enforce one-way containment instead: every
    # non-empty value token from each `{列名}: {値}` line in JSON must
    # appear in docs MD. The column-name side is naturally in the MD
    # header row. No asset-link rewrite (Excel has no RST asset refs).
    if data.get("sheet_type") == "P1":
        if top_content:
            # P1 top content is plain preamble text (design §8-4);
            # verbatim containment is still the right check.
            if top_content not in docs_md_text:
                issues.append(
                    f"[QO2] {file_id}: top-level content not found in docs MD"
                )
        for s in sections:
            content = s.get("content", "")
            title = s.get("title", "")
            for line in content.split("\n"):
                line = line.strip()
                if not line:
                    continue
                # Split once on ":" so values containing ":" are preserved.
                if ":" in line:
                    _key, _, value = line.partition(":")
                    value = value.strip()
                else:
                    value = line
                if not value:
                    continue
                if value not in docs_md_text:
                    issues.append(
                        f"[QO2] {file_id}: section {title!r} value {value!r} not found in docs MD"
                    )
        return issues

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
    if not readme.exists():
        issues.append(f"[QO3] README.md missing: {readme}")
        return issues

    # Per-file existence check — JSON → MD direction.
    for json_path in sorted(kdir.rglob("*.json")):
        rel = json_path.relative_to(kdir).with_suffix(".md")
        docs_md_path = ddir / rel
        if not docs_md_path.exists():
            issues.append(
                f"[QO3] docs MD missing for JSON: expected {rel} (from {json_path.relative_to(kdir)})"
            )

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

def _parse_toon_index(text: str) -> list[str]:
    """Parse the files[] table from an index.toon.

    RBKC's create side (`scripts/create/index.py`) emits a single fixed
    schema `files[N,]{title,type,category,processing_patterns,path}:`
    with 2-space indented rows, path as the last comma-separated field.
    This parser targets that shape; structural drift would surface as
    a create-side bug (verify does not own adversarial-input parsing).
    """
    paths: list[str] = []
    in_table = False
    for line in text.splitlines():
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
        # Normalise path separator on parse so a Windows writer would
        # still round-trip against forward-slash JSON relpaths.
        paths.append(stripped[last_comma + 1:].strip().replace("\\", "/"))
    return paths


def check_index_coverage(knowledge_dir, index_path) -> list[str]:
    """QO4: index.toon must list exactly the content JSON files on disk.

    Per rbkc-verify-quality-design.md §3-3:
    - index.toon missing: every content JSON is reported as FAIL.
    - JSON on disk not in index.toon: FAIL (not searchable).
    - Path in index.toon without a matching JSON on disk: FAIL (dangling).
    - JSON parse failures: FAIL (no silent skip).
    """
    issues: list[str] = []
    kdir = Path(knowledge_dir)
    idx = Path(index_path)

    # Track JSON files separately by state so we can give accurate
    # messages (Z-1 r7 QO4 F1/F2): content, no_knowledge, broken.
    content_jsons: dict[str, Path] = {}
    no_knowledge_jsons: set[str] = set()
    broken_jsons: set[str] = set()
    for jf in sorted(kdir.rglob("*.json")):
        rel = str(jf.relative_to(kdir)).replace("\\", "/")
        try:
            d = json.loads(jf.read_text(encoding="utf-8"))
        except Exception as exc:
            issues.append(f"[QO4] {rel}: JSON parse failed: {exc}")
            broken_jsons.add(rel)
            continue
        if d.get("no_knowledge_content"):
            no_knowledge_jsons.add(rel)
            continue
        content_jsons[rel] = jf

    if not idx.exists():
        if not content_jsons:
            return issues
        issues.append(f"[QO4] index.toon missing: {idx}")
        for rel in sorted(content_jsons):
            issues.append(f"[QO4] {rel}: JSON not registered in index.toon (index.toon absent)")
        return issues

    indexed_set = set(_parse_toon_index(idx.read_text(encoding="utf-8")))

    # Forward: every content JSON must appear in the index.
    for rel in sorted(content_jsons):
        if rel not in indexed_set:
            issues.append(f"[QO4] {Path(rel).name}: JSON not registered in index.toon: {rel}")

    # Reverse: every path in the index must correspond to a real content JSON.
    # Distinct messages for each orthogonal failure mode so operators don't
    # chase a phantom "missing file" when the file exists but is broken or
    # no_knowledge (F1/F2).
    for rel in sorted(indexed_set):
        if rel in content_jsons:
            continue
        if rel in broken_jsons:
            # Already reported as parse failure above; do not re-flag as
            # missing (F2: avoid double FAIL with misleading second message).
            continue
        if rel in no_knowledge_jsons:
            issues.append(f"[QO4] index.toon lists no_knowledge JSON: {rel}")
            continue
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

    # NULL bytes (\x00) are never valid in any Markdown output.  A NULL
    # in JSON content makes docs MD binary and unrenderable on GitHub
    # Web / other viewers.  Flag any occurrence as QC5 regardless of fmt.
    def _scan_null(text: str, where: str) -> None:
        if text and "\x00" in text:
            issues.append(
                f"[QC5] {file_id}/{where}: NULL byte (\\x00) in content"
            )

    _scan_null(title, "title")
    _scan_null(top_content, "content")
    for s in data.get("sections", []):
        _scan_null(s.get("title", ""), f"section '{s.get('title', '')}'/title")
        _scan_null(s.get("content", ""), f"section '{s.get('title', '')}'/content")

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

def _normalize_rst_source(
    text: str,
    label_map: dict | None = None,
    doc_map: dict | None = None,
    source_path=None,
    file_id: str = "",
) -> str:
    """Normalize RST markup to plain text for comparison with JSON content.

    Delegates to :func:`scripts.common.rst_normaliser.normalise_rst`, which
    implements the docutils-AST normalisation specified in
    `rbkc-verify-quality-design.md` §3-1 手順 0.
    """
    from scripts.common.rst_normaliser import normalise_rst
    warnings: list[str] = []
    out = normalise_rst(
        text,
        label_map=label_map or {},
        doc_map=doc_map,
        source_path=source_path,
        strict_unknown=True,
        warnings_out=warnings,
        file_id=file_id,
    )
    # Phase 22-B-16b step 2b F1: emit dangling-link WARNINGs to stderr.
    # Spec §3-2-2 "WARNING ログ + display text fallback" is silent-skip
    # only if the WARNING is ever dropped.
    if warnings:
        import sys
        tag = f"{source_path}: " if source_path else ""
        for w in warnings:
            print(f"WARN {tag}{w}", file=sys.stderr)
    return out


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


def check_content_completeness(
    source_text: str,
    data: dict,
    fmt: str,
    label_map: dict | None = None,
    doc_map: dict | None = None,
    source_path=None,
    file_id: str = "",
) -> list[str]:
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
        return _check_rst_content_completeness(
            source_text, data, issues, label_map, doc_map, source_path, file_id
        )
    elif fmt == "md":
        return _check_md_content_completeness(
            source_text, data, issues, doc_map=doc_map, source_path=source_path
        )
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
    source_text: str,
    data: dict,
    issues: list[str],
    label_map: dict | None = None,
    doc_map: dict | None = None,
    source_path=None,
    file_id: str = "",
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
        norm_source_raw = _normalize_rst_source(
            source_text, label_map, doc_map=doc_map, source_path=source_path,
            file_id=file_id,
        )
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
    source_text: str,
    data: dict,
    issues: list[str],
    doc_map: dict | None = None,
    source_path=None,
) -> list[str]:
    """QC1-QC4 for MD sources using AST-normalised comparison.

    Per rbkc-verify-quality-design.md §3-1: the source is parsed by the
    shared md_ast Visitor (same code create uses) to produce a normalised
    MD string, then JSON search units are sequential-deleted from it.
    Any non-whitespace residue is a QC1 FAIL (no tolerance list).
    """
    from scripts.common.md_normaliser import UnknownSyntaxError, normalise_md

    warnings: list[str] = []
    try:
        norm_source = normalise_md(
            source_text,
            strict_unknown=True,
            doc_map=doc_map,
            source_path=source_path,
            warnings_out=warnings,
        )
    except UnknownSyntaxError as exc:
        issues.append(f"[QC1] markdown parse/visitor error: {exc}")
        return issues
    if warnings:
        import sys
        tag = f"{source_path}: " if source_path else ""
        for w in warnings:
            print(f"WARN {tag}{w}", file=sys.stderr)

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
    # Spec §3-1 Excel 節 explicitly names `---` as an allowed residue.
    # Match 3+ hyphens as a standalone token (GFM table separator or
    # horizontal rule residue that lost its flanking pipes).
    r'|-{3,}'
    r'|\*\*|\*|__(?![\w])|(?<![\w])__'
    r'|^#+\s*'
    r'|^>\s*'
    r'|^\d+\.\s+'
    r'|`'
    # Phase 22-B P1 structural delimiter: §8-4 specifies section.content
    # as `{列名}: {値}` per line.  The ": " separator is a structural
    # artifact of the JSON schema, not derived from any source cell, and
    # must not trigger QC2 residue.  Matches a lone `:` surrounded by
    # whitespace (already the case after token removal — JSON text is
    # split by whitespace further down, so any `:` that survives as its
    # own token here is structural).
    r'|:'
    , re.MULTILINE
)


def _read_sheet_matrix(source_path, sheet_name: str | None) -> list[list[list[str]]]:
    """Load one or all worksheets as a list of row-matrices of stripped strings.

    Returns ``[[row0, row1, ...], ...]`` where each row is a list of cell
    strings.  Used by ``_xlsx_source_tokens`` and the QP / header-detection
    helpers.  Keeps the format-dispatch (.xls vs .xlsx) in one place.
    """
    ext = Path(source_path).suffix.lower()
    sheets_rows: list[list[list[str]]] = []
    if ext == ".xls":
        import xlrd
        wb = xlrd.open_workbook(str(source_path))
        sheets = [wb.sheet_by_name(sheet_name)] if sheet_name is not None else list(wb.sheets())
        for sheet in sheets:
            rows: list[list[str]] = []
            for rx in range(sheet.nrows):
                row = []
                for cx in range(sheet.ncols):
                    v = sheet.cell_value(rx, cx)
                    row.append(str(v).strip() if v is not None else "")
                rows.append(row)
            sheets_rows.append(rows)
    else:
        import openpyxl
        wb = openpyxl.load_workbook(str(source_path), data_only=True)
        sheets = [wb[sheet_name]] if sheet_name is not None else list(wb.worksheets)
        for ws in sheets:
            rows = []
            for row in ws.iter_rows(values_only=True):
                rows.append([
                    str(v).strip() if v is not None else ""
                    for v in row
                ])
            sheets_rows.append(rows)
    return sheets_rows


# ---------------------------------------------------------------------------
# Phase 22-B-5a-r3a: header detection & P1 header token expansion
#
# verify's copy of the header-detection rules.  Per spec §3-1 Excel 節 and
# rbkc-converter-design.md §8-2, verify MUST NOT call into converter code
# — both sides derive from the same spec independently.  Drift between the
# two implementations is naturally caught: if verify picks a different
# header than converter did, QC1 / QC2 residue surfaces the mismatch.
# ---------------------------------------------------------------------------

def _run_length(row: list[str]) -> int:
    best = cur = 0
    for v in row:
        if v:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def _looks_like_sub_header(row_h: list[str], row_h1: list[str]) -> bool:
    """Mirror converter-design §8-3 sub-header rule (independently derived).

    Conditions: row_h1 strictly narrower than row_h AND every non-empty
    sub cell has a non-empty parent at column ≤ its own.
    """
    h_non_empty = sum(1 for v in row_h if v)
    h1_cols = [cx for cx, v in enumerate(row_h1) if v]
    if not h1_cols:
        return False
    if len(h1_cols) >= h_non_empty:
        return False
    for cx in h1_cols:
        px = cx
        while px >= 0 and not row_h[px]:
            px -= 1
        if px < 0 or not row_h[px]:
            return False
    return True


def _merge_header(row_h: list[str], row_h1: list[str]) -> list[str]:
    """Combine main + sub header rows into a single column-name list."""
    merged = list(row_h)
    for cx, sub in enumerate(row_h1):
        if not sub:
            continue
        parent_cx = cx
        while parent_cx >= 0 and not row_h[parent_cx]:
            parent_cx -= 1
        if parent_cx >= 0 and row_h[parent_cx]:
            merged[cx] = f"{row_h[parent_cx]}/{sub}"
        else:
            merged[cx] = sub
    # Normalise embedded whitespace/newlines so column names compare cleanly
    # with their JSON-side form (§8-4 uses flattened names).
    return [" ".join(c.split()) for c in merged]


def _find_body_start(rows: list[list[str]]) -> int:
    """Skip leading title/preamble rows (single non-empty cell) per §8-4."""
    i = 0
    # Skip over ■title row if present.
    if rows:
        first = next((v for v in rows[0] if v), "")
        if first.startswith("■"):
            i = 1
    while i < len(rows):
        row = rows[i]
        non_empty = [c for c in row if c]
        if not non_empty:
            i += 1
            continue
        if len(non_empty) == 1:
            i += 1
            continue
        break
    return i


def _useful_width(rows: list[list[str]], body_start: int) -> int:
    width = max((len(r) for r in rows), default=0)
    used = [False] * width
    for r in rows[body_start:]:
        for cx in range(min(width, len(r))):
            if r[cx]:
                used[cx] = True
    return sum(1 for u in used if u)


def _detect_header_row(rows: list[list[str]]) -> tuple[int, int, list[str]] | None:
    """Locate the (possibly multi-row) header and return its indices + columns.

    Returns ``(header_start, data_start, columns)`` or None if the sheet
    does not qualify as P1.  Also enforces the ≤ 2 column P2 cap (§8-2).
    """
    body_start = _find_body_start(rows)
    if _useful_width(rows, body_start) <= 2:
        return None
    n = len(rows)
    for h in range(body_start, min(body_start + 20, n)):
        row_h = rows[h]
        if _run_length(row_h) < 3:
            continue
        # Sub-header at h+1?
        data_start = h + 1
        columns = list(row_h)
        if h + 1 < n and _looks_like_sub_header(row_h, rows[h + 1]):
            columns = _merge_header(row_h, rows[h + 1])
            data_start = h + 2
        else:
            columns = [" ".join(c.split()) for c in columns]
        # Need at least 2 data rows
        data_rows = [r for r in rows[data_start:] if any(c for c in r)]
        if len(data_rows) < 2:
            continue
        return h, data_start, columns
    return None


def _data_rows(rows: list[list[str]], data_start: int, width: int) -> list[list[str]]:
    out = []
    for r in rows[data_start:]:
        cells = [c for c in r[:width]] + [""] * max(0, width - len(r))
        if any(cells):
            out.append(cells)
    return out


def _pick_title_col_idx(columns: list[str]) -> int:
    """Spec §8-4 title-column rule (derived independently of converter)."""
    for cx, name in enumerate(columns):
        if name == "タイトル":
            return cx
    for cx, name in enumerate(columns):
        if not name:
            continue
        if name in ("No", "No.", "№", "#"):
            continue
        return cx
    return 0


def _trailing_extra_rows(rows: list[list[str]], data_start: int) -> int:
    """Count of rows at ``data_start`` onward that contain data (per
    ``_data_rows``).  Trailing rows past the last non-empty row are ignored
    — they are not §8-4 data rows."""
    # Find the index of the last non-empty row.
    last = data_start
    for i in range(data_start, len(rows)):
        if any(c for c in rows[i]):
            last = i + 1
    return last - data_start


def _xlsx_source_tokens(
    source_path,
    sheet_name: str | None = None,
    sheet_type: str | None = None,
) -> list[str]:
    """Return non-empty cell tokens from *source_path*.

    When ``sheet_name`` is given, only that worksheet is tokenised. This
    supports Phase 22-B sheet-level file split, where each generated JSON
    corresponds to one sheet and must be verified only against its own
    cells. ``sheet_name=None`` preserves the all-sheet behaviour.

    When ``sheet_type == "P1"`` (and ``sheet_name`` is given), header-row
    cell values are duplicated by data-row count per spec §3-1 Excel 節.
    Without ``sheet_type`` the raw 1:1 tokenisation is returned.
    """
    sheets_rows = _read_sheet_matrix(source_path, sheet_name)

    # Spec §8-4 sheet-name fallback for title: when no ``■...`` row is
    # present in row 1, both P1 and P2 converters use ``sheet.name`` as
    # the JSON title.  Sheet name is not a cell value, so verify injects
    # it as a synthetic source token to satisfy QC1/QC2.  Injected only
    # when the sheet actually lacks a ``■...`` row (otherwise it would
    # let unrelated fabrications slip).
    sheet_name_fallback = None
    if sheet_name is not None and sheets_rows and sheets_rows[0]:
        first = next((v for v in sheets_rows[0][0] if v), "")
        if not first.startswith("■"):
            sheet_name_fallback = sheet_name

    if sheet_type == "P1" and sheet_name is not None and sheets_rows:
        rows = sheets_rows[0]
        detected = _detect_header_row(rows)
        if detected is not None:
            header_start, data_start, columns = detected
            width = len(columns)
            data_rows = _data_rows(rows, data_start, width)
            tokens: list[str] = []
            # §8-4 sheet-name title fallback: the JSON title comes first
            # in the concatenated JSON text, so emit it first to match
            # the forward-scan order.
            if sheet_name_fallback:
                tokens.append(sheet_name_fallback)
            # Pre-header rows (title, preamble, blank rows): emit as
            # flattened 1-line form (§8-4).
            for r in rows[:header_start]:
                for v in r:
                    if v:
                        tokens.append(" ".join(v.split()))
            # Emit tokens in JSON appearance order (spec §8-4) so the
            # existing forward-scan sequential-delete stays tight (QC3
            # still catches reordering).  Per §8-4:
            #   section.title = title-col cell value (or first non-No. col)
            #   section.content = lines of {列名}: {値} for non-empty cells
            # Thus for each data row R we emit:
            #   1. title-col cell value (section.title)
            #   2. for each non-empty col C (in column order):
            #        merged column-name + cell value  (= {列名}: {値} line)
            # The title-col cell therefore appears twice — inherent to §8-4,
            # not a converter artifact.
            title_col_idx = _pick_title_col_idx(columns)
            for row in data_rows:
                title_val = row[title_col_idx] if 0 <= title_col_idx < len(row) else ""
                if not title_val:
                    # Fallback: first non-empty cell (mirrors converter
                    # §8-4 section-title fallback)
                    title_val = next((c for c in row if c), "")
                if title_val:
                    # §8-4 line-based format forbids embedded newlines in
                    # values (see ``check_xlsx_p1_pairing``).  Flatten
                    # whitespace so tokens match the JSON form.
                    tokens.append(" ".join(title_val.split()))
                for cx, col in enumerate(columns):
                    if cx >= len(row):
                        continue
                    cell = row[cx]
                    if not col or not cell:
                        continue
                    tokens.append(col)
                    tokens.append(" ".join(cell.split()))
            # Trailing rows after data_rows (usually none; guard anyway).
            trailing_end = data_start + _trailing_extra_rows(rows, data_start)
            for r in rows[trailing_end:]:
                for v in r:
                    if v:
                        tokens.append(v)
            return tokens

    # Raw 1:1 (non-P1 or all-sheet legacy caller).
    tokens: list[str] = []
    if sheet_name_fallback:
        # JSON title (= sheet name fallback) appears first in JSON text;
        # emit it first so forward-scan finds it.
        tokens.append(sheet_name_fallback)
    for rows in sheets_rows:
        for r in rows:
            for v in r:
                if v:
                    tokens.append(v)
    return tokens


# ---------------------------------------------------------------------------
# Phase 22-B-5a-r3b: QP (spec §3-4) — P1 column-value pairing check
# ---------------------------------------------------------------------------


def _parse_section_pairs(content: str) -> list[tuple[str, str]]:
    """Split a P1 section.content into ``(列名, 値)`` pairs.

    Aligns with §8-4 line format and the QO2 P1 check in
    ``check_json_docs_md_consistency``: partition on the FIRST ``:`` so
    values containing ``:`` (URLs) are preserved verbatim.
    """
    pairs: list[tuple[str, str]] = []
    for line in content.split("\n"):
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if not key:
            continue
        pairs.append((key, val))
    return pairs


def check_xlsx_p1_pairing(source_path, data: dict, sheet_name: str) -> list[str]:
    """Spec §3-4 (QP): verify that JSON section N pairs up with Excel row N.

    Returns ``[]`` for non-P1 sheets (QP is P1-only), else one message per
    detected pairing issue.
    """
    if data.get("sheet_type") != "P1":
        return []
    if _no_knowledge(data):
        return []

    file_id = data.get("id", "?")
    sheets_rows = _read_sheet_matrix(source_path, sheet_name)
    if not sheets_rows:
        return [f"[QP] {file_id}: source sheet {sheet_name!r} not found"]
    rows = sheets_rows[0]
    detected = _detect_header_row(rows)
    if detected is None:
        # P1 judged at converter side but verify disagreed — that
        # inconsistency is already caught by QC1/QC2 residue; QP does not
        # report twice.
        return []
    _, data_start, columns = detected
    width = len(columns)
    data_rows = _data_rows(rows, data_start, width)

    issues: list[str] = []
    sections = data.get("sections", [])
    if len(sections) != len(data_rows):
        issues.append(
            f"[QP] {file_id} sheet={sheet_name!r}: section count mismatch — "
            f"JSON has {len(sections)} sections, Excel has {len(data_rows)} data rows"
        )
        # Continue with the overlap so downstream mismatches are also reported.

    # Duplicate column-name guard (zero-tolerance resolution of the spec
    # gap): two source columns sharing the same header name make the
    # {列名}: {値} line format ambiguous — JSON cannot record which column
    # a given value came from.  Under zero-tolerance, treat duplicates
    # as an explicit failure rather than collapsing silently.
    seen_cols: set[str] = set()
    dup_cols: list[str] = []
    for col in columns:
        if not col:
            continue
        if col in seen_cols:
            if col not in dup_cols:
                dup_cols.append(col)
        else:
            seen_cols.add(col)
    for col in dup_cols:
        issues.append(
            f"[QP] {file_id} sheet={sheet_name!r}: duplicate column name "
            f"{col!r} in Excel header — {{列名}}: {{値}} line format is ambiguous"
        )

    for idx, (sec, row) in enumerate(zip(sections, data_rows), start=1):
        expected: dict[str, str] = {}
        for cx, col in enumerate(columns):
            if cx >= len(row):
                continue
            cell = row[cx]
            if not cell:
                continue
            if not col:
                continue
            if col in dup_cols:
                # Ambiguous column already reported at header level; do
                # not re-flag per row.
                continue
            # §8-4 line-based `{列名}: {値}` format cannot preserve
            # embedded newlines/tabs.  Flatten whitespace on both sides
            # for comparison (verify-side derivation from §8-4, not
            # converter mirroring).
            expected[col] = " ".join(cell.split())
        actual = dict(_parse_section_pairs(sec.get("content", "")))
        # pair_missing: expected column absent or value mismatched.
        for col, val in expected.items():
            if col not in actual:
                issues.append(
                    f"[QP] {file_id} sheet={sheet_name!r} section[{idx}]: "
                    f"missing column {col!r} (expected value {val!r})"
                )
            elif actual[col] != val:
                issues.append(
                    f"[QP] {file_id} sheet={sheet_name!r} section[{idx}]: "
                    f"column {col!r} value mismatch — "
                    f"expected {val!r}, got {actual[col]!r}"
                )
        # pair_extra: JSON section has a column name not present in expected.
        # (spec allows omitting empty cells; extras indicate converter leakage.)
        for col in actual:
            if col not in expected:
                issues.append(
                    f"[QP] {file_id} sheet={sheet_name!r} section[{idx}]: "
                    f"unexpected column {col!r} not in Excel header"
                )
    return issues


def _xlsx_json_text(data: dict) -> str:
    parts = [data.get("title", ""), data.get("content", "")]
    for s in data.get("sections", []):
        if s.get("title"):
            parts.append(s["title"])
        if s.get("content"):
            parts.append(s["content"])
    return "\n".join(p for p in parts if p)


def _verify_xlsx(source_path, data: dict, sheet_name: str | None = None) -> list[str]:
    if _no_knowledge(data):
        return []

    tokens = _xlsx_source_tokens(
        source_path,
        sheet_name=sheet_name,
        sheet_type=data.get("sheet_type"),
    )
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
            # Mirror RST/MD's _classify_missed_unit: walk EVERY occurrence
            # rather than only the earliest. Spec §3-1 Excel 節 手順 4
            # requires QC3 when the token "is found at a consumed
            # position" — this is an existence check across all
            # occurrences, not a check on the first one only.
            any_occurrence = False
            any_consumed = False
            scan = 0
            while True:
                pos = json_text.find(token, scan)
                if pos == -1:
                    break
                any_occurrence = True
                if _in_consumed(pos, len(token)):
                    any_consumed = True
                    break
                scan = pos + 1
            if not any_occurrence:
                issues.append(f"[QC1] Excel cell value missing from JSON: {token!r}")
            elif any_consumed:
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

def verify_file(
    source_path,
    json_path,
    fmt,
    knowledge_dir=None,
    label_map=None,
    sheet_name=None,
    doc_map=None,
    file_id: str = "",
) -> list[str]:
    """Per-file JSON checks (QC1-QC5, QL2).

    ``sheet_name`` is used only when ``fmt == 'xlsx'`` to scope the source
    tokens to one worksheet (Phase 22-B sheet-level split).
    """
    if not Path(json_path).exists():
        return []

    data = json.loads(Path(json_path).read_text(encoding="utf-8"))

    if _no_knowledge(data):
        return []

    if fmt == "xlsx":
        issues = _verify_xlsx(source_path, data, sheet_name=sheet_name)
        # QP (spec §3-4): P1 column-value pairing.  Runs only for P1
        # sheets; a valid sheet_name is required for per-row pairing.
        if sheet_name is not None and data.get("sheet_type") == "P1":
            issues.extend(check_xlsx_p1_pairing(source_path, data, sheet_name))
        return issues

    if fmt in ("rst", "md"):
        source_text = Path(source_path).read_text(encoding="utf-8", errors="replace")
        issues: list[str] = []
        issues.extend(check_content_completeness(
            source_text, data, fmt, label_map, doc_map=doc_map, source_path=source_path,
            file_id=file_id,
        ))
        issues.extend(_check_format_purity(data, fmt))
        issues.extend(check_external_urls(source_text, data, fmt))
        # Phase 22-B-16b step 4: two-sided QL1 on cross-document MD links.
        if knowledge_dir is not None:
            docs_md_text = None
            try:
                docs_md_path = (
                    Path(knowledge_dir).parent / "docs" /
                    Path(json_path).relative_to(Path(knowledge_dir))
                ).with_suffix(".md")
                if docs_md_path.exists():
                    docs_md_text = docs_md_path.read_text(encoding="utf-8")
            except (ValueError, OSError):
                pass
            issues.extend(check_ql1_link_targets(
                data, knowledge_dir, docs_md_text=docs_md_text
            ))
        return issues

    return []


# ---------------------------------------------------------------------------
# verify_docs_md: stub (QO1/QO2 handled via check_json_docs_md_consistency)
# ---------------------------------------------------------------------------

def verify_docs_md(source_path, docs_md_path, fmt) -> list[str]:
    """Per-file docs MD checks beyond JSON↔MD consistency. Stub."""
    return []


# ---------------------------------------------------------------------------
# QL1 two-sided: link target existence (Phase 22-B-16b step 4)
# ---------------------------------------------------------------------------

# Matches CommonMark MD links emitted by the converter:
#   [display](../../{type}/{category}/{file_id}.md)          ← :doc:
#   [display](../../{type}/{category}/{file_id}.md#{anchor}) ← :ref: / numref
_CROSSDOC_LINK_RE = re.compile(
    r'\]\(\.\./\.\./(?P<type>[A-Za-z0-9_\-]+)/'
    r'(?P<category>[A-Za-z0-9_\-]+)/'
    r'(?P<file_id>[^)\s#]+)\.md(?:#(?P<anchor>[^)\s]+))?\)'
)

# Matches ``](assets/{file_id}/{basename})`` links (image/figure/download).
_ASSET_LINK_RE = re.compile(
    r'\]\((?P<path>assets/(?P<file_id>[^)\s/]+)/(?P<basename>[^)\s]+))\)'
)


def check_ql1_link_targets(
    data: dict,
    knowledge_dir,
    docs_md_text: str | None = None,
) -> list[str]:
    """Spec §3-2-3 QL1 two-sided: every cross-document MD link that
    appears in JSON content or section content must point at an
    existing target JSON file.

    JSON side (always): extract ``](../../{type}/{cat}/{file_id}.md[#anchor])``
    links from all content strings, then confirm
    ``knowledge_dir/{type}/{cat}/{file_id}.json`` exists.  Dangling
    links → FAIL (``[QL1] JSON link target missing``).

    Docs MD side (when ``docs_md_text`` is supplied): mirror the check
    against ``{knowledge_dir.parent}/docs/{type}/{cat}/{file_id}.md``.

    Skips asset-link validation (``](assets/...)``) — that belongs to
    22-B-16c (QL1 asset existence).
    """
    from pathlib import Path as _Path

    knowledge_root = _Path(knowledge_dir)
    docs_root = knowledge_root.parent / "docs"

    def _collect_links(text: str) -> list[tuple[str, str, str, str]]:
        return [
            (
                m.group("type"),
                m.group("category"),
                m.group("file_id"),
                m.group("anchor") or "",
            )
            for m in _CROSSDOC_LINK_RE.finditer(text or "")
        ]

    def _collect_assets(text: str) -> list[tuple[str, str]]:
        return [
            (m.group("file_id"), m.group("basename"))
            for m in _ASSET_LINK_RE.finditer(text or "")
        ]

    sources: list[str] = []
    sources.append(data.get("content", "") or "")
    for sec in data.get("sections", []) or []:
        sources.append(sec.get("content", "") or "")

    seen: set[tuple[str, str, str]] = set()
    seen_assets: set[tuple[str, str]] = set()
    issues: list[str] = []

    for text in sources:
        for type_, category, file_id, _anchor in _collect_links(text):
            key = (type_, category, file_id)
            if key in seen:
                continue
            seen.add(key)
            target_json = knowledge_root / type_ / category / f"{file_id}.json"
            if not target_json.exists():
                issues.append(
                    f"[QL1] JSON link target missing: "
                    f"../../{type_}/{category}/{file_id}.md → "
                    f"{target_json.relative_to(knowledge_root.parent)} not on disk"
                )
        # Phase 22-B-16c: asset existence check.  `assets/{file_id}/
        # {basename}` must exist under knowledge_dir/assets/...
        for asset_fid, basename in _collect_assets(text):
            key_a = (asset_fid, basename)
            if key_a in seen_assets:
                continue
            seen_assets.add(key_a)
            asset_path = knowledge_root / "assets" / asset_fid / basename
            if not asset_path.exists():
                issues.append(
                    f"[QL1] asset missing: assets/{asset_fid}/{basename} → "
                    f"{asset_path.relative_to(knowledge_root.parent)} not on disk"
                )

    if docs_md_text is not None:
        seen_md: set[tuple[str, str, str]] = set()
        for type_, category, file_id, _anchor in _collect_links(docs_md_text):
            key = (type_, category, file_id)
            if key in seen_md:
                continue
            seen_md.add(key)
            target_md = docs_root / type_ / category / f"{file_id}.md"
            if not target_md.exists():
                issues.append(
                    f"[QL1] docs MD link target missing: "
                    f"../../{type_}/{category}/{file_id}.md → "
                    f"{target_md.relative_to(docs_root.parent)} not on disk"
                )

    return issues


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
    from scripts.common.labels import UNRESOLVED

    def _resolved_text(target, fallback: str, display: str = "") -> str:
        """Convert a label_map value to its rendered form (MD link or plain).

        Mirrors the create-side ``_MDVisitor._render_label_target`` so the
        string we compare against JSON matches byte-for-byte.
        """
        if target is None or target is UNRESOLVED:
            return fallback
        if isinstance(target, str):
            return display or target
        file_id = getattr(target, "file_id", "") or ""
        category = getattr(target, "category", "") or ""
        type_ = getattr(target, "type", "") or ""
        title = getattr(target, "title", "") or ""
        anchor = getattr(target, "anchor", "") or ""
        disp = display or title
        if not file_id or not category or not type_:
            return disp
        if anchor:
            return f"[{disp}](../../{type_}/{category}/{file_id}.md#{anchor})"
        return f"[{disp}](../../{type_}/{category}/{file_id}.md)"

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
                        parts.append(_resolved_text(label_map.get(raw), raw))
                    continue
                # Other roles: render the raw text (converter does the same).
                parts.append(raw)
                continue
        if isinstance(child, nodes.reference):
            refid = (child.get("refid", "") or "").strip()
            target = label_map.get(refid) if refid else None
            if target is not None and target is not UNRESOLVED:
                parts.append(_resolved_text(target, child.astext()))
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
            # Bare label form: the resolved target title must appear.
            # Phase 22-B-16a (spec §3-2-2 zero-exception): a label that
            # neither docutils nor label_map can resolve is a dangling
            # reference — FAIL.  Silent skip is the horizontal-class bug
            # we are fixing.
            if not display and label not in seen_labels:
                seen_labels.add(label)
                target = label_map.get(label)
                from scripts.common.labels import UNRESOLVED
                if target is None or target is UNRESOLVED:
                    issues.append(
                        f"[QL1] :ref:`{label}` unresolved (label not in label_map or orphan label): dangling reference"
                    )
                    continue
                # Support both legacy str (title only) and the upcoming
                # Phase 22-B-16b LabelTarget dataclass.  The dataclass case
                # is a future-proof no-op here — we only read the title.
                title = target if isinstance(target, str) else getattr(target, "title", str(target))
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
