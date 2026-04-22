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

from scripts.common.labels import build_label_map, _RST_LABEL_DEF_RE  # noqa: F401 (re-exported)


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
_H2_RE = re.compile(r'^#{2,}\s+(.+)$', re.MULTILINE)


def check_json_docs_md_consistency(data: dict, docs_md_text: str) -> list[str]:
    """QO1: structure (title/section titles/order) and QO2: content verbatim."""
    if _no_knowledge(data):
        return []

    issues: list[str] = []
    file_id = data.get("id", "?")
    json_title = data.get("title", "")
    sections = data.get("sections", [])
    top_content = data.get("content", "")

    # QO1: title check
    m = _H1_RE.search(docs_md_text)
    docs_title = m.group(1).strip() if m else ""
    if json_title and docs_title != json_title:
        issues.append(f"[QO1] {file_id}: title mismatch: JSON={json_title!r} docs={docs_title!r}")

    # QO1: section title order and presence
    docs_h2_titles = [m.group(1).strip() for m in _H2_RE.finditer(docs_md_text)]
    json_sec_titles = [s.get("title", "") for s in sections if s.get("title")]

    if not sections and docs_h2_titles:
        issues.append(f"[QO1] {file_id}: docs MD has section headings but JSON has no sections")
    else:
        # Check all JSON section titles appear in docs MD in order
        pos = 0
        for title in json_sec_titles:
            found = False
            for i in range(pos, len(docs_h2_titles)):
                if docs_h2_titles[i] == title:
                    pos = i + 1
                    found = True
                    break
            if not found:
                issues.append(f"[QO1] {file_id}: section title missing or out of order in docs MD: {title!r}")

    # QO2: top-level content verbatim
    if top_content and "assets/" not in top_content:
        if top_content not in docs_md_text:
            issues.append(f"[QO2] {file_id}: top-level content not found verbatim in docs MD")

    # QO2: section content verbatim
    for s in sections:
        content = s.get("content", "")
        title = s.get("title", "")
        if not content or "assets/" in content:
            continue
        if content not in docs_md_text:
            issues.append(f"[QO2] {file_id}: section '{title}' content not found verbatim in docs MD")

    return issues


# ---------------------------------------------------------------------------
# QO3 + README count: check_docs_coverage
# ---------------------------------------------------------------------------

_README_COUNT_RE = re.compile(r'^(\d+)\s*ページ', re.MULTILINE)


def check_docs_coverage(knowledge_dir, docs_dir) -> list[str]:
    """QO3: README.md exists with correct file count."""
    issues = []
    readme = Path(docs_dir) / "README.md"
    if not readme.exists():
        issues.append(f"[QO3] README.md missing: {readme}")
        return issues

    actual = len([p for p in Path(docs_dir).rglob("*.md") if p.name != "README.md"])
    text = readme.read_text(encoding="utf-8")
    m = _README_COUNT_RE.search(text)
    if m:
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
    """QO4: every JSON (without no_knowledge_content) must be in index.toon."""
    issues = []
    kdir = Path(knowledge_dir)
    idx = Path(index_path)

    if not idx.exists():
        # Collect all JSON files that need indexing
        json_files = list(kdir.rglob("*.json"))
        content_files = []
        for jf in json_files:
            try:
                d = json.loads(jf.read_text(encoding="utf-8"))
                if not d.get("no_knowledge_content"):
                    content_files.append(jf)
            except Exception:
                pass
        if content_files:
            issues.append(f"[QO4] index.toon missing: {idx}")
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
        # Path is the last comma-separated field on the row
        last_comma = stripped.rfind(",")
        if last_comma < 0:
            continue
        indexed_paths.add(stripped[last_comma + 1:].strip())

    for jf in sorted(kdir.rglob("*.json")):
        try:
            d = json.loads(jf.read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("no_knowledge_content"):
            continue
        rel = str(jf.relative_to(kdir)).replace("\\", "/")
        if rel not in indexed_paths:
            issues.append(f"[QO4] {jf.name}: JSON not registered in index.toon: {rel}")

    return issues


# ---------------------------------------------------------------------------
# QC5: 形式純粋性
# ---------------------------------------------------------------------------

_RST_ROLE_RE = re.compile(r':[a-zA-Z][a-zA-Z0-9_.-]*:`')
_RST_DIRECTIVE_RE = re.compile(r'\.\.\s+\S+.*::')
_RST_HEADING_UNDERLINE_RE = re.compile(r'^[=\-~^"\'`#*+<>]{4,}\s*$', re.MULTILINE)
_RST_LABEL_RE = re.compile(r'\.\.\s+_[a-zA-Z0-9_-]+:')
_MD_RAW_HTML_RE = re.compile(r'(?<![a-zA-Z])<[a-zA-Z][a-zA-Z0-9]*[\s>]')
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

_URL_RE = re.compile(r'https?://[^\s\'"<>)\]`]+')
_URL_TRAILING_PUNCT_RE = re.compile(r'[.,;:`]+$')
_RST_TARGET_LINE_RE = re.compile(r'^(?:\.\.?\s+_|__\s+https?://)')
_RST_SUBSTITUTION_RE = re.compile(r'^\s*\.\.\s+\|[^|]+\|\s+[a-z_-]+::')


def _clean_url(url: str) -> str:
    return _URL_TRAILING_PUNCT_RE.sub('', url)


def _source_urls(source_text: str, fmt: str) -> list[str]:
    """Extract external URLs actually visible to readers.

    Excludes RST link-target definitions and RST substitution definitions
    (the bodies of ``.. |name| raw:: html`` blocks). Substitution blocks
    are dedented bodies that start after the directive header and run until
    a blank line immediately followed by a non-indented line, so we track
    block context.
    """
    urls = []
    lines = source_text.splitlines()
    in_subst_block = False
    subst_indent = 0
    for line in lines:
        stripped = line.strip()
        if fmt == "rst":
            if _RST_SUBSTITUTION_RE.match(stripped):
                in_subst_block = True
                subst_indent = len(line) - len(line.lstrip())
                continue
            if in_subst_block:
                if not stripped:
                    continue
                cur_indent = len(line) - len(line.lstrip())
                if cur_indent > subst_indent:
                    # still inside the substitution body — skip
                    continue
                in_subst_block = False
            if _RST_TARGET_LINE_RE.match(stripped):
                continue
        for url in _URL_RE.findall(line):
            u = _clean_url(url)
            if u:
                urls.append(u)
    return urls


def check_external_urls(source_text: str, data: dict, fmt: str) -> list[str]:
    """QL2: External URLs in source must appear verbatim in JSON."""
    if fmt == "xlsx" or _no_knowledge(data):
        return []

    src_urls = _source_urls(source_text, fmt)
    if not src_urls:
        return []

    json_text = _all_text(data)
    json_urls: set[str] = set()
    for url in _URL_RE.findall(json_text):
        json_urls.add(_clean_url(url))

    issues = []
    seen: set[str] = set()
    for url in src_urls:
        if url in seen:
            continue
        seen.add(url)
        if url not in json_urls:
            issues.append(f"[QL2] external URL missing from JSON: {url}")
    return issues


# ---------------------------------------------------------------------------
# QC1-QC4: sequential-delete algorithm (RST/MD)
# ---------------------------------------------------------------------------

def _collect_rst_substitutions(text: str) -> dict[str, str]:
    """Extract visible-text resolutions for RST substitution definitions.

    For ``.. |name| raw:: html`` with an ``<a ...>text</a>`` body we emit the
    anchor text so the normalised source matches the converter's output.
    """
    subs: dict[str, str] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^\s*\.\.\s+\|([^|]+)\|\s+([a-z_-]+)::(.*)", lines[i])
        if not m:
            i += 1
            continue
        name = m.group(1).strip()
        directive = m.group(2).lower()
        arg = m.group(3).strip()
        # Read indented body
        body_lines: list[str] = []
        j = i + 1
        while j < len(lines):
            bl = lines[j]
            if not bl.strip():
                body_lines.append("")
                j += 1
                continue
            if bl.startswith(" ") or bl.startswith("\t"):
                body_lines.append(bl.strip())
                j += 1
                continue
            break
        i = j
        # For ``raw::`` the directive arg is the output format, not body text.
        if directive == "raw":
            body = " ".join(b for b in body_lines if b).strip()
        else:
            body = " ".join([arg] + [b for b in body_lines if b]).strip()
        if directive == "replace":
            subs[name] = body
        elif directive == "raw":
            m_a = re.search(r"<a[^>]*>([^<]+)</a>", body)
            if m_a:
                subs[name] = m_a.group(1).strip()
            else:
                subs[name] = ""
        else:
            subs[name] = body
    return subs


def _normalize_rst_source(text: str, label_map: dict | None = None, substitutions: dict | None = None) -> str:
    """Normalize RST markup to plain text for comparison with JSON content.

    Applies the inverse of common RST-to-Markdown conversions so that
    JSON units (already in MD form) can be found in the normalized source.
    Uses ``[^\\S\\n]`` (non-newline whitespace) to avoid swallowing newlines before
    the final whitespace collapse step.
    """
    # Drop substitution definition blocks (header + indented body) before
    # expanding `|name|` references — otherwise the header line itself loses
    # its `|name|` token after expansion and the block-stripper can no longer
    # recognise it, leaving raw bodies like ``<br />`` in the output.
    def _strip_subst_blocks(src: str) -> str:
        lines = src.split('\n')
        out_lines: list[str] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            m = re.match(r'^\s*\.\.\s+\|[^|]+\|\s+[a-z_-]+::', line)
            if not m:
                out_lines.append(line)
                i += 1
                continue
            header_indent = len(line) - len(line.lstrip())
            i += 1
            while i < len(lines):
                bl = lines[i]
                if not bl.strip():
                    i += 1
                    continue
                cur_indent = len(bl) - len(bl.lstrip())
                if cur_indent > header_indent:
                    i += 1
                    continue
                break
        return '\n'.join(out_lines)

    text = _strip_subst_blocks(text)

    # Drop directive blocks whose raw body content is NOT expected to appear
    # in JSON (converter either skips them or rewrites them into an
    # unrecognisable form for direct substring comparison). Directives that
    # carry real content (list-table, code-block, literalinclude, etc.) must
    # NOT be stripped — their bodies reach JSON content.
    _STRIP_BLOCK_DIRECTIVES = re.compile(
        r'^\s*\.\.\s+(toctree|include|raw|class|only|ifconfig'
        r'|contents|sectnum|header|footer|meta)\s*::'
    )

    def _strip_directive_blocks(src: str) -> str:
        lines = src.split('\n')
        out_lines: list[str] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if _STRIP_BLOCK_DIRECTIVES.match(line):
                header_indent = len(line) - len(line.lstrip())
                i += 1
                while i < len(lines):
                    bl = lines[i]
                    if not bl.strip():
                        i += 1
                        continue
                    cur_indent = len(bl) - len(bl.lstrip())
                    if cur_indent > header_indent:
                        i += 1
                        continue
                    break
                continue
            out_lines.append(line)
            i += 1
        return '\n'.join(out_lines)

    text = _strip_directive_blocks(text)

    # Drop RST comment blocks. Per RST spec, a line that begins with ``..``
    # followed by text that does NOT form a directive/label/footnote/
    # substitution reference is a comment; indented content underneath is the
    # comment body. Comments are not rendered and their content must not
    # appear in JSON.
    def _strip_comment_blocks(src: str) -> str:
        lines = src.split('\n')
        out_lines: list[str] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            s = line.lstrip()
            # Identify a comment marker: `..` or `.. <text without "::">`
            # that is NOT a directive/label/footnote/substitution.
            is_comment = False
            if s.startswith('..'):
                rest = s[2:]
                # Bare `..` on its own line is a comment.
                if not rest.strip():
                    is_comment = True
                elif rest.startswith(' ') or rest.startswith('\t'):
                    body = rest.lstrip()
                    # Exclusions: directive (`name::`), label (`_name:`),
                    # footnote/citation (`[tag]`), substitution (`|name|`).
                    if (
                        '::' not in body.split('\n', 1)[0]
                        and not body.startswith('_')
                        and not body.startswith('[')
                        and not body.startswith('|')
                    ):
                        is_comment = True
            if is_comment:
                header_indent = len(line) - len(line.lstrip())
                i += 1
                # Consume indented body (deeper than header).
                while i < len(lines):
                    bl = lines[i]
                    if not bl.strip():
                        i += 1
                        continue
                    cur_indent = len(bl) - len(bl.lstrip())
                    if cur_indent > header_indent:
                        i += 1
                        continue
                    break
                continue
            out_lines.append(line)
            i += 1
        return '\n'.join(out_lines)

    text = _strip_comment_blocks(text)

    # Expand substitution references using definitions supplied or collected.
    # Only substitute when the name between `|...|` is actually in the map —
    # other bars in prose (e.g. ``Prometheus | HTTP API | OTLP Receiver``)
    # must survive as plain text.
    subs = substitutions if substitutions is not None else _collect_rst_substitutions(text)
    if subs:
        def _resolve_sub(m: re.Match) -> str:
            name = m.group(1).strip()
            if name in subs:
                return subs[name]
            return m.group(0)
        text = re.sub(r'\|([^|\n]+)\|_?', _resolve_sub, text)
    # ``inline code`` -> inline code
    text = re.sub(r'``([^`]+)``', r'\1', text)
    # :ref:`display text <label>` -> display text
    text = re.sub(r':ref:`([^<`]+?)[^\S\n]*<[^>]+>`', r'\1', text)
    # :ref:`label` -> resolved title (if known), else label
    if label_map:
        def _resolve_ref(m: re.Match) -> str:
            label = m.group(1).strip()
            return label_map.get(label, label)
        text = re.sub(r':ref:`([^`]+)`', _resolve_ref, text)
    else:
        text = re.sub(r':ref:`([^`]+)`', r'\1', text)
    # :java:extdoc:`ClassName <fqcn>` -> ClassName (converter drops the fqcn)
    text = re.sub(r':java:extdoc:`([^<`]+?)[^\S\n]*<[^>]+>`', r'\1', text)
    # :doc:`display text <path>` -> display text  (converter drops the path)
    text = re.sub(r':doc:`([^<`]+?)[^\S\n]*<[^>]+>`', r'\1', text)
    # :doc:`path` -> path
    text = re.sub(r':doc:`([^`]+)`', r'\1', text)
    # Generic domain role with target: :role:`text <target>` -> text
    # (must run before the `text <url>`_ external-hyperlink pattern below, so
    # roles like :javadoc_url: don't leak their leading ``:role:`` marker).
    text = re.sub(r':[a-zA-Z][a-zA-Z0-9_.:-]*:`([^<`]+?)[^\S\n]*<[^>]+>`', r'\1', text)
    # `link text <url>`_ -> link text  (RST external hyperlink, inline form).
    # Accept both absolute URLs and relative refs (e.g. ``<./file.zip>``).
    text = re.sub(r'`([^`<]+?)[^\S\n]*<[^>]+>`_?', r'\1', text)
    # `text`_  -> text (named-reference form; resolved URL is separate target def)
    text = re.sub(r'`([^`<]+?)`_+', r'\1', text)
    # General RST role :role:`text` -> text
    text = re.sub(r':[a-zA-Z][a-zA-Z0-9_.:-]*:`([^`]*)`', r'\1', text)
    # `single-backtick interpreted text` — RST treats this as an interpreted
    # text role; the converter passes it through as a single-backtick MD code
    # span, but ``_normalize_md_unit`` strips those backticks, so match here.
    # Must run AFTER all role-based regexes so it only fires on bare backticks.
    text = re.sub(r'(?<![`])`([^`\n]+)`(?![`])', r'\1', text)
    # RST footnote/citation target: `.. [tag] body` -> keep body only.
    # Must run *before* the catch-all directive strip below, otherwise the
    # footnote body text (which the converter inlines into the section
    # content) is dropped from the source side.
    text = re.sub(r'^[^\S\n]*\.\.\s+\[[^\]]+\][^\S\n]*', '', text, flags=re.MULTILINE)
    # RST directive lines: .. directive:: args -> remove line (keep body content)
    text = re.sub(r'^[^\S\n]*\.\.[^\S\n]+\S[^\n]*\n', '', text, flags=re.MULTILINE)
    # RST option lines inside directives: :option: value -> remove line.
    # Restricted to ASCII option names (directive options never use CJK);
    # CJK field-list entries like ``:システム設定値: value`` are handled
    # separately below so the value portion survives.
    text = re.sub(r'^[^\S\n]*:[a-zA-Z][a-zA-Z0-9_-]*:[^\n]*\n', '', text, flags=re.MULTILINE)
    # RST field-list entries (e.g. ``:name: value`` at line start) — keep the
    # value, drop the marker so source and JSON-side unit normalisation agree.
    text = re.sub(r'^[^\S\n]*:([^:`\n]+):[^\S\n]+', '', text, flags=re.MULTILINE)
    # RST list-table item markers: `* - ` or `  - ` — the trailing hyphen
    # must be followed by at least one space and a non-hyphen character,
    # otherwise multi-hyphen tokens like `---` (code-block content or YAML
    # separator) are mistakenly eaten.
    text = re.sub(r'^[^\S\n]{0,6}\*?[^\S\n]*-[^\S\n]+(?=[^-])', '', text, flags=re.MULTILINE)
    # Empty list-table cell marker: ``*`` followed by ``-`` on its own line.
    # The cell has no content so the marker must be dropped entirely —
    # otherwise a bare ``-`` residue appears on source side but not in JSON.
    text = re.sub(r'^[^\S\n]*\*?[^\S\n]*-[^\S\n]*$', '', text, flags=re.MULTILINE)
    # Bullet markers: "* ", "- ", "+ " at line start. The marker must be a
    # single char followed by whitespace and a non-marker char — this
    # prevents `---` from being rewritten to `--`.
    text = re.sub(r'^[^\S\n]*[*+\-][^\S\n]+(?=[^*+\-])', '', text, flags=re.MULTILINE)
    # Enumerated list markers (RST): "#." or "1." / "2." etc. at line start
    text = re.sub(r'^[^\S\n]*(?:\d+|#)\.[^\S\n]+', '', text, flags=re.MULTILINE)
    # Grid-table content prefix "| " at start of line -> drop the pipe.
    text = re.sub(r'^[^\S\n]*\|[^\S\n]*', '', text, flags=re.MULTILINE)
    # Any remaining bare pipe within a line is also stripped so source and
    # JSON (where ``_normalize_md_unit`` turns `|` into a space) stay aligned.
    text = re.sub(r'\|', ' ', text)
    # Trailing hyperlink-reference underscore: "text_" or "text__". Allow
    # a closing backtick to terminate too, so ``code_``-style spans also match.
    # Preceding char must be word-ending (alnum/]/)) — never a backtick, which
    # would wrongly strip the ``_`` inside ``` `_` ``` inline code literals.
    text = re.sub(r'([\w\]\)])_+(?=[\s`]|$)', r'\1', text, flags=re.MULTILINE)
    # Remove leading indentation from directive bodies (1-8 non-newline spaces)
    text = re.sub(r'^[^\S\n]{1,8}', '', text, flags=re.MULTILINE)
    # RST heading underlines: ====, ----, ~~~~, etc. Require 4+ of the SAME
    # character (so mixed strings like ``#----`` in shell-comment dividers
    # don't accidentally match and consume legitimate content).
    text = re.sub(
        r'^(?:={4,}|-{4,}|~{4,}|\^{4,}|"{4,}|\'{4,}|`{4,}|\#{4,}|\*{4,}|\+{4,}|<{4,}|>{4,})[^\S\n]*$',
        '',
        text,
        flags=re.MULTILINE,
    )
    # Simple-table separator row (e.g. "=== === ====") and grid-table border
    text = re.sub(r'^[^\S\n]*[=\-]+(?:[^\S\n]+[=\-]+)+[^\S\n]*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[^\S\n]*\+[-=+]+[^\S\n]*$', '', text, flags=re.MULTILINE)
    # Collapse all whitespace (including newlines) for multi-line comparison
    text = re.sub(r'\s+', ' ', text)
    # Drop stray bullet markers that sit between words (e.g. residue of a
    # nested bullet list collapsed onto one line).
    text = re.sub(r'(?:(?<=^)|(?<=\s))[*+\-](?=[^\S\n]+[^*+\-\s])', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _normalize_md_unit(text: str) -> str:
    """Normalize MD content (JSON field) to plain text for RST source comparison.

    Strips code fences, headings, inline code markers, links, table syntax, and
    blockquote/admonition prefixes, then collapses whitespace so multi-line content
    can be found in the normalized RST source.
    """
    # Strip RST footnote/citation/label remnants that converter passes through.
    # (Source-side normalisation drops them, so we strip here for symmetry.)
    text = re.sub(r'(?m)^\s*\.\.\s+\[[^\]]+\][^\n]*', '', text)
    text = re.sub(r'(?m)^\s*\.\.\s+_[^:]+:[^\n]*', '', text)

    # Split into fenced-code and non-code regions so MD syntax strips (HTML
    # tags, headings, list markers, etc.) only apply to non-code text. Inside
    # fenced code blocks, verbatim content must be preserved — otherwise HTML
    # tags that originate from the source (e.g. ``<br/>`` inside Java
    # Javadoc comments) get stripped on the MD side while the source side
    # keeps them, causing a spurious QC2 fabricated-content error.
    out: list[str] = []
    in_fence = False
    for line in text.split("\n"):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue  # drop the fence marker itself
        if in_fence:
            # Inside fenced code: preserve content verbatim except for a
            # few tokens that source-side normalisation removes as well,
            # keeping both sides aligned:
            # - ``|`` → space (e.g. ASCII directory trees)
            # - leading bullet markers `` * ``, `` - ``, `` + `` (Javadoc-style
            #   line prefixes are source-side bullet markers)
            inner = line.replace("|", " ")
            inner = re.sub(r'^[^\S\n]*[*+\-][^\S\n]+(?=[^*+\-])', '', inner)
            out.append(inner)
            continue
        l = line
        # Grid-table HTML scaffolding the converter emits: strip
        # <table>/<tbody>/<tr>/<td>/<th>/<thead>/<br>/<br /> tags and their
        # closers so the cell text aligns with source-side rst normalisation.
        l = re.sub(r'</?(?:table|thead|tbody|tr|td|th|br)(?:\s[^>]*)?/?>', ' ', l, flags=re.IGNORECASE)
        # Unresolved RST field-list entries the converter passes through as-is
        # (``:name: value`` or ``:name:`` on its own line with the value
        # continued below). Drop the ``:name:`` marker so the value aligns
        # with the source-normalised form (which collapses these away).
        l = re.sub(r'^\s*:([^:`\n]+):(?:\s+|$)', '', l)
        # Footnote/citation reference trailing underscore: "[1]_" -> "[1]"
        # (and ``name_`` → ``name``). Preceding char must be a word-ending
        # marker (alnum, closing bracket/paren) — a backtick must NOT be
        # allowed because that would incorrectly strip the ``_`` inside
        # ``` `_` ``` inline code.
        l = re.sub(r'([\w\]\)])_+(?=[\s`]|$)', r'\1', l)
        # MD headings: #### Heading -> Heading
        l = re.sub(r'^#{1,6}[^\S\n]+', '', l)
        # Bullet list markers (MD): "* "/"- "/"+ ". Require the next char after
        # the marker's whitespace to NOT be another marker so we don't eat
        # multi-hyphen tokens (table separators, YAML `---`).
        l = re.sub(r'^[^\S\n]*[*+\-][^\S\n]+(?=[^*+\-])', '', l)
        # Enumerated list markers (MD): "1." / "2." / "#." at line start
        l = re.sub(r'^[^\S\n]*(?:\d+|#)\.[^\S\n]+', '', l)
        # `inline code` -> inline code
        l = re.sub(r'`([^`]+)`', r'\1', l)
        # Image: ![alt](path) -> "" (image is covered by QL1)
        # URL may include one level of balanced parens (common in Javadoc
        # anchors like ``#apiKey()``).
        l = re.sub(r'!\[[^\]]*\]\((?:[^()]|\([^)]*\))+\)', '', l)
        # [link text](url) -> link text
        l = re.sub(r'\[([^\]]+)\]\((?:[^()]|\([^)]*\))+\)', r'\1', l)
        # Admonition header line: > **Type:** ... -> content only
        l = re.sub(r'>[^\S\n]*\*\*[^*]+\*\*:?[^\S\n]*', '', l)
        # Remaining blockquote prefix: > text -> text
        l = re.sub(r'^>[^\S\n]*', '', l)
        # MD table separator rows: |---|---| -> remove line
        l = re.sub(r'^\|[-:| ]+\|[^\S\n]*$', '', l)
        # MD table cell borders: | -> space. Before collapsing, strip bullet
        # markers that sit inside a cell (e.g. `| * javax.json * javax.json.spi |`):
        # they originate from a nested bullet list in an RST list-table cell
        # but the source side normalises them away.
        l = re.sub(r'\|[^\S\n]*[*+\-][^\S\n]+(?=[^*+\-])', '| ', l)
        # Drop ``\|`` MD-cell escape sequences entirely — the source-side
        # never has the leading backslash so a bare backslash residue would
        # cause a mismatch.
        l = l.replace("\\|", " ")
        l = re.sub(r'\|', ' ', l)
        out.append(l)
    text = "\n".join(out)
    # Collapse whitespace (handles multi-line content merged into one line)
    text = re.sub(r'\s+', ' ', text)
    # After collapsing, remove any isolated " * "/" - "/" + " bullet markers
    # that survived from nested bullet lists inside list-table cells.
    text = re.sub(r'(?:(?<=^)|(?<=\s))[*+\-](?=[^\S\n]+[^*+\-\s])', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _strip_md_to_plain_lines(text: str) -> list[str]:
    """Strip Markdown syntax from JSON content; return non-empty searchable lines.

    Used only for MD sources (verbatim content comparison).
    """
    result = []
    in_fence = False
    for line in text.split('\n'):
        if re.match(r'^\s*```', line):
            in_fence = not in_fence
            continue
        if in_fence:
            if line.strip():
                result.append(line)
            continue
        l = re.sub(r'^#+\s*', '', line)
        l = re.sub(r'^>\s?', '', l)
        l = re.sub(r'^\*\*[^\*]+[：:]\*\*\s*', '', l)
        l = re.sub(r'\*\*(.+?)\*\*', r'\1', l)
        l = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\1', l)
        l = re.sub(r'(?<![a-zA-Z0-9_])__(.+?)__(?![a-zA-Z0-9_])', r'\1', l)
        l = re.sub(r'(?<![a-zA-Z0-9_])_([^_\s][^_]*)_(?![a-zA-Z0-9_])', r'\1', l)
        if l.strip():
            result.append(l)
    return result


def _is_rst_syntax_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if re.match(r"^[=\-~^\"'`#*+<>]{4,}\s*$", s):
        return True
    # Simple-table separator row, e.g. `=== === ====` (chars + spaces only)
    if re.match(r'^[=\-]+(\s+[=\-]+)+\s*$', s):
        return True
    # Grid-table border: `+---+---+` / `+===+===+`
    if re.match(r'^\+[-=+]+\+?\s*$', s):
        return True
    # Line continuation marker (RST leading backslash) `\` on its own
    if s == '\\':
        return True
    if re.match(r'^\.\.\s*(\S.*::|$)', s):
        return True
    # Label definition: `.. _label:` / `.. _label: url` — RST permits arbitrary
    # text in the label; accept anything up to the terminating colon (the
    # URL/target that may follow is validated separately).
    if re.match(r'^\.\.\s+_[^:]+:', s):
        return True
    # Substitution definition (any form): `.. |name| ...`
    if re.match(r'^\.\.\s+\|', s):
        return True
    # Footnote / citation target: `.. [#name]` / `.. [1]` etc.
    if re.match(r'^\.\.\s+\[[^\]]+\]', s):
        return True
    # Anonymous hyperlink target: `__ https://...`
    if re.match(r'^__\s+https?://', s):
        return True
    # RST comment: `.. <arbitrary text without "::">`. Per spec, any `..`
    # line that is not a directive / label / footnote / substitution is a
    # comment. This must come AFTER the directive/label/footnote/substitution
    # matchers above so those structural lines aren't mis-classified.
    if re.match(r'^\.\.(?:\s|$)', s):
        return True
    if re.match(r'^:[a-zA-Z][a-zA-Z0-9_.-]*:`', s):
        return True
    if re.match(r'^\s+:[a-zA-Z]', line):
        return True
    # Bare field-list marker line ``:name:`` (no inline value). The value is
    # on subsequent indented lines and will be captured as content there.
    if re.match(r'^:[^:`\n]+:$', s):
        return True
    return False


def _is_md_syntax_line(line: str, in_frontmatter: bool = False) -> bool:
    s = line.strip()
    if not s:
        return True
    if re.match(r'^---+\s*$', s):
        return True
    if in_frontmatter:
        return True
    if re.match(r'^```', s):
        return True
    if re.match(r'^<!--', s):
        return True
    if re.match(r'^#+\s*', s):
        return True
    return False


_RST_STRUCTURAL_DIRECTIVES = re.compile(
    r'^\.\.\s+(toctree|include|image|figure|raw|csv-table|list-table'
    r'|class|only|ifconfig|replace|unicode|date|contents|sectnum'
    r'|header|footer|rubric|meta|compound|container|math'
    r'|code-block|code|sourcecode|highlight|parsed-literal'
    r'|literalinclude|testsetup|testcleanup|doctest)\s*::'
)


def _build_rst_search_units(
    data: dict,
) -> list[tuple[str, str, str, bool]]:
    """Build (original_unit, normalized_unit, sid, is_content) for RST content.

    For RST sources: JSON content is in MD form (converter output).
    We normalize each JSON field to plain text so it can be found in a
    normalized RST source.  Titles are searched verbatim (already plain text).
    """
    units: list[tuple[str, str, str, bool]] = []
    top_title = data.get("title", "")
    top_content = data.get("content", "")

    def _norm_title(t: str) -> str:
        # Titles are plain text but may contain double spaces / tabs that
        # source normalisation collapses. Apply the same whitespace collapse.
        return re.sub(r'\s+', ' ', t).strip()

    if top_title:
        units.append((top_title, _norm_title(top_title), "__top__", False))
    if top_content:
        norm = _normalize_md_unit(top_content)
        if norm:
            units.append((top_content, norm, "__top__", True))

    for sec in data.get("sections", []):
        title = sec.get("title", "")
        content = sec.get("content", "")
        sid = sec.get("id", "?")
        if title:
            units.append((title, _norm_title(title), sid, False))
        if content:
            norm = _normalize_md_unit(content)
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
    rst_substitutions = _collect_rst_substitutions(source_text)
    norm_source = _normalize_rst_source(source_text, label_map, rst_substitutions)
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
            prev_idx = norm_source.find(norm_unit)
            if not is_content:
                if prev_idx == -1:
                    issues.append(f"[QC2] section '{sid}': fabricated title: {orig_unit[:50]!r}")
                elif _in_consumed(prev_idx, len(norm_unit)):
                    issues.append(f"[QC3] section '{sid}': duplicate title: {orig_unit[:50]!r}")
                else:
                    issues.append(f"[QC4] section '{sid}': misplaced title: {orig_unit[:50]!r}")
            elif prev_idx == -1:
                issues.append(f"[QC2] section '{sid}': fabricated content: {orig_unit[:50]!r}")
            elif _in_consumed(prev_idx, len(norm_unit)):
                issues.append(f"[QC3] section '{sid}': duplicate content: {orig_unit[:50]!r}")
            else:
                issues.append(f"[QC4] section '{sid}': misplaced content: {orig_unit[:50]!r}")

    # QC1: each non-syntax RST source line must appear (normalized) in some JSON field
    all_norm_units = [nu for _, nu, _, _ in search_units if nu]
    in_structural = False
    in_subst = False
    subst_indent = 0
    in_comment = False
    comment_indent = 0
    for line in source_text.split('\n'):
        s = line.strip()
        # Track substitution definitions and their indented bodies separately
        # from ``_RST_STRUCTURAL_DIRECTIVES``: substitution bodies are not
        # content we expect to see in JSON (the converter expands references,
        # not bodies).
        if re.match(r'^\s*\.\.\s+\|[^|]+\|\s+[a-z_-]+::', line):
            in_subst = True
            subst_indent = len(line) - len(line.lstrip())
            continue
        if in_subst:
            if not s:
                continue
            cur_indent = len(line) - len(line.lstrip())
            if cur_indent > subst_indent:
                continue
            in_subst = False
        # Track RST comment blocks. ``.. <text>`` lines that aren't
        # directives / labels / footnotes / substitutions are comments per
        # RST spec; indented content beneath is the comment body and must be
        # skipped from QC1 residual checking.
        if in_comment:
            if not s:
                continue
            cur_indent = len(line) - len(line.lstrip())
            if cur_indent > comment_indent:
                continue
            in_comment = False
        if s.startswith('..'):
            rest = s[2:]
            is_comment_marker = False
            if not rest.strip():
                is_comment_marker = True
            elif rest.startswith(' ') or rest.startswith('\t'):
                body = rest.lstrip()
                first_line = body.split('\n', 1)[0]
                if (
                    '::' not in first_line
                    and not body.startswith('_')
                    and not body.startswith('[')
                    and not body.startswith('|')
                ):
                    is_comment_marker = True
            if is_comment_marker:
                in_comment = True
                comment_indent = len(line) - len(line.lstrip())
                continue
        if s and re.match(r'\.\.\s+\S', s):
            in_structural = bool(_RST_STRUCTURAL_DIRECTIVES.match(s))
        if not s:
            continue
        if in_structural and re.match(r'^\s+\S', line):
            continue
        if _is_rst_syntax_line(line):
            continue
        norm_line = re.sub(r'\s+', ' ', _normalize_rst_source(line, label_map, rst_substitutions)).strip()
        if not norm_line:
            continue
        found = any(norm_line in nu for nu in all_norm_units)
        if not found:
            issues.append(f"[QC1] source content not captured: {line.strip()[:50]!r}")

    return issues


def _check_md_content_completeness(
    source_text: str, data: dict, issues: list[str]
) -> list[str]:
    """QC1-QC4 for MD sources (verbatim comparison)."""
    top_title = data.get("title", "")
    top_content = data.get("content", "")

    search_units: list[tuple[str, str, bool]] = []
    if top_title:
        search_units.append((top_title, "__top__", False))
    if top_content:
        search_units.append((top_content, "__top__", True))

    for sec in data.get("sections", []):
        title = sec.get("title", "")
        content = sec.get("content", "")
        sid = sec.get("id", "?")
        if title:
            search_units.append((title, sid, False))
        if content:
            search_units.append((content, sid, True))

    if not search_units:
        return issues

    consumed: list[tuple[int, int]] = []
    current_pos = 0

    def _in_consumed(pos: int, length: int) -> bool:
        end = pos + length
        return any(pos < e and end > s for s, e in consumed)

    for unit, sid, is_content in search_units:
        idx = source_text.find(unit, current_pos)
        if idx != -1:
            consumed.append((idx, idx + len(unit)))
            current_pos = idx + len(unit)
        else:
            prev_idx = source_text.find(unit)
            if not is_content:
                if prev_idx == -1:
                    issues.append(f"[QC2] section '{sid}': fabricated title: {unit[:50]!r}")
                elif _in_consumed(prev_idx, len(unit)):
                    issues.append(f"[QC3] section '{sid}': duplicate title: {unit[:50]!r}")
                else:
                    issues.append(f"[QC4] section '{sid}': misplaced title: {unit[:50]!r}")
            elif prev_idx == -1:
                issues.append(f"[QC2] section '{sid}': fabricated content: {unit[:50]!r}")
            elif _in_consumed(prev_idx, len(unit)):
                issues.append(f"[QC3] section '{sid}': duplicate content: {unit[:50]!r}")
            else:
                issues.append(f"[QC4] section '{sid}': misplaced content: {unit[:50]!r}")

    # QC1: residual source check
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
            parts.append(source_text[prev:s])
            prev = e
        parts.append(source_text[prev:])
        remaining = ''.join(parts)
    else:
        remaining = source_text

    has_frontmatter = bool(re.match(r'^---+\s*$', source_text.split('\n')[0])) if source_text else False
    in_frontmatter = False
    frontmatter_seen = False
    for line in remaining.split('\n'):
        s = line.strip()
        if has_frontmatter and not frontmatter_seen and re.match(r'^---+\s*$', s):
            in_frontmatter = True
            frontmatter_seen = True
            continue
        if in_frontmatter:
            if re.match(r'^---+\s*$', s):
                in_frontmatter = False
            continue
        if not _is_md_syntax_line(line):
            issues.append(f"[QC1] source content not captured: {line.strip()[:50]!r}")

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

    residual_plain = _MD_SYNTAX_RE.sub(" ", residual)
    for token in residual_plain.split():
        t = token.strip()
        if t and len(t) >= 2:
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

_RST_REF_DISPLAY_RE = re.compile(r':ref:`([^<`]+?)\s*<([^>]+)>`')
_RST_REF_PLAIN_RE = re.compile(r':ref:`([^`]+)`')
_RST_FIGURE_RE = re.compile(r'^\.\.\s+figure::\s*(\S+)')
_RST_IMAGE_RE = re.compile(r'^\.\.\s+image::\s*(\S+)')
_RST_IMAGE_ALT_RE = re.compile(r':alt:\s*(.+)')
_RST_LITERALINCLUDE_RE = re.compile(r'^\.\.\s+literalinclude::\s*(\S+)')
_MD_INTERNAL_LINK_RE = re.compile(r'\[([^\]]+)\]\((?!https?://)([^)]+)\)')


def _read_rst_block(lines: list[str], start: int) -> list[str]:
    block = []
    for line in lines[start:]:
        if line.strip() == "":
            block.append(line)
        elif line.startswith(" ") or line.startswith("\t"):
            block.append(line)
        else:
            break
    return block


def check_source_links(
    source_text: str,
    fmt: str,
    data: dict,
    label_map: dict,
    source_path=None,
) -> list[str]:
    """QL1: Internal links in source must be reflected in JSON."""
    if fmt == "xlsx" or _no_knowledge(data):
        return []

    json_full = _all_text(data)
    issues: list[str] = []

    if fmt == "rst":
        lines = source_text.splitlines()

        # :ref: display-text form
        seen_display: set[str] = set()
        for m in _RST_REF_DISPLAY_RE.finditer(source_text):
            display_text = m.group(1).strip()
            if display_text and display_text not in seen_display:
                seen_display.add(display_text)
                if display_text not in json_full:
                    issues.append(f"[QL1] :ref: display text missing from JSON: {display_text!r}")

        # :ref:`label` plain form
        seen_labels: set[str] = set()
        for line in lines:
            for m in _RST_REF_PLAIN_RE.finditer(line):
                if "<" in m.group(1):
                    continue
                label = m.group(1).strip()
                if label in seen_labels:
                    continue
                seen_labels.add(label)
                title = label_map.get(label)
                if title is None:
                    continue
                if title not in json_full:
                    issues.append(f"[QL1] :ref:`{label}` target title missing from JSON: {title!r}")

        # figure / image / literalinclude
        i = 0
        while i < len(lines):
            line = lines[i]
            fm = _RST_FIGURE_RE.match(line.strip())
            if fm:
                block = _read_rst_block(lines, i + 1)
                caption = ""
                for bl in block:
                    s = bl.strip()
                    if s and not s.startswith(":") and not s.startswith(".."):
                        caption = s
                        break
                check_text = caption if caption else Path(fm.group(1)).name
                if check_text and check_text not in json_full:
                    issues.append(f"[QL1] figure caption/filename missing from JSON: {check_text!r}")
                i += 1
                continue

            im = _RST_IMAGE_RE.match(line.strip())
            if im:
                block = _read_rst_block(lines, i + 1)
                alt = ""
                for bl in block:
                    am = _RST_IMAGE_ALT_RE.match(bl.strip())
                    if am:
                        alt = am.group(1).strip()
                        break
                check_text = alt if alt else Path(im.group(1)).name
                if check_text and check_text not in json_full:
                    issues.append(f"[QL1] image alt/filename missing from JSON: {check_text!r}")
                i += 1
                continue

            lm = _RST_LITERALINCLUDE_RE.match(line.strip())
            if lm:
                path = lm.group(1)
                placeholder = f"# (literalinclude: {path})"
                if placeholder not in json_full:
                    issues.append(f"[QL1] literalinclude placeholder missing from JSON: {path!r}")
                i += 1
                continue

            i += 1

    elif fmt == "md":
        seen_link_texts: set[str] = set()
        for m in _MD_INTERNAL_LINK_RE.finditer(source_text):
            link_text = m.group(1).strip()
            if not link_text or link_text in seen_link_texts:
                continue
            seen_link_texts.add(link_text)
            if link_text not in json_full:
                issues.append(f"[QL1] internal link text missing from JSON: {link_text!r}")

    return issues
