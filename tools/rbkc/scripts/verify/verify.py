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

def _normalize_rst_source(text: str, label_map: dict | None = None) -> str:
    """Normalize RST markup to plain text for comparison with JSON content.

    Applies the inverse of common RST-to-Markdown conversions so that
    JSON units (already in MD form) can be found in the normalized source.
    Uses ``[^\\S\\n]`` (non-newline whitespace) to avoid swallowing newlines before
    the final whitespace collapse step.
    """
    # RST substitution reference |name| -> "" (the converter expands it into a
    # different token, so stripping it from the source keeps normalise lossy
    # but non-mismatching; substitution-body URLs are handled by QL2).
    text = re.sub(r'\|[^|\n]+\|_?', '', text)
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
    # `link text <url>`_ -> link text  (RST external hyperlink, inline form)
    text = re.sub(r'`([^`<]+?)[^\S\n]*<https?://[^>]+>`_?', r'\1', text)
    # `text`_  -> text (named-reference form; resolved URL is separate target def)
    text = re.sub(r'`([^`<]+?)`_+', r'\1', text)
    # General RST role :role:`text` -> text
    text = re.sub(r':[a-zA-Z][a-zA-Z0-9_.:-]*:`([^`]*)`', r'\1', text)
    # `single-backtick interpreted text` — RST treats this as an interpreted
    # text role; the converter passes it through as a single-backtick MD code
    # span, but ``_normalize_md_unit`` strips those backticks, so match here.
    # Must run AFTER all role-based regexes so it only fires on bare backticks.
    text = re.sub(r'(?<![`])`([^`\n]+)`(?![`])', r'\1', text)
    # RST directive lines: .. directive:: args -> remove line (keep body content)
    text = re.sub(r'^[^\S\n]*\.\.[^\S\n]+\S[^\n]*\n', '', text, flags=re.MULTILINE)
    # RST option lines inside directives: :option: value -> remove line
    text = re.sub(r'^[^\S\n]*:[a-zA-Z][a-zA-Z0-9_-]*:[^\n]*\n', '', text, flags=re.MULTILINE)
    # RST list-table item markers: "* - " or "  - " -> just content (use [^\S\n]* not \s*)
    text = re.sub(r'^[^\S\n]{0,6}\*?[^\S\n]*-[^\S\n]*', '', text, flags=re.MULTILINE)
    # Remove leading indentation from directive bodies (1-8 non-newline spaces)
    text = re.sub(r'^[^\S\n]{1,8}', '', text, flags=re.MULTILINE)
    # RST heading underlines: ====, ----, ~~~~, etc. (4+ same chars on own line)
    text = re.sub(r'^[=\-~^"\'`#*+<>]{4,}[^\S\n]*$', '', text, flags=re.MULTILINE)
    # Collapse all whitespace (including newlines) for multi-line comparison
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _normalize_md_unit(text: str) -> str:
    """Normalize MD content (JSON field) to plain text for RST source comparison.

    Strips code fences, headings, inline code markers, links, table syntax, and
    blockquote/admonition prefixes, then collapses whitespace so multi-line content
    can be found in the normalized RST source.
    """
    # Code fences: ```lang\n...\n``` -> content only
    text = re.sub(r'```[a-zA-Z0-9]*\n', '', text)
    text = re.sub(r'```', '', text)
    # MD headings: #### Heading -> Heading
    text = re.sub(r'^#{1,6}[^\S\n]+', '', text, flags=re.MULTILINE)
    # `inline code` -> inline code
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # [link text](url) -> link text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Admonition header line: > **Type:** ... -> content only
    text = re.sub(r'>[^\S\n]*\*\*[^*]+\*\*:?[^\S\n]*', '', text)
    # Remaining blockquote prefix: > text -> text
    text = re.sub(r'^>[^\S\n]*', '', text, flags=re.MULTILINE)
    # MD table separator rows: |---|---| -> remove line
    text = re.sub(r'^\|[-:| ]+\|[^\S\n]*$', '', text, flags=re.MULTILINE)
    # MD table cell borders: | -> space
    text = re.sub(r'\|', ' ', text)
    # Collapse whitespace (handles multi-line content merged into one line)
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
    if re.match(r'^:[a-zA-Z][a-zA-Z0-9_.-]*:`', s):
        return True
    if re.match(r'^\s+:[a-zA-Z]', line):
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

    if top_title:
        units.append((top_title, top_title, "__top__", False))
    if top_content:
        norm = _normalize_md_unit(top_content)
        if norm:
            units.append((top_content, norm, "__top__", True))

    for sec in data.get("sections", []):
        title = sec.get("title", "")
        content = sec.get("content", "")
        sid = sec.get("id", "?")
        if title:
            units.append((title, title, sid, False))
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
    norm_source = _normalize_rst_source(source_text, label_map)
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
    for line in source_text.split('\n'):
        s = line.strip()
        if s and re.match(r'\.\.\s+\S', s):
            in_structural = bool(_RST_STRUCTURAL_DIRECTIVES.match(s))
        if not s:
            continue
        if in_structural and re.match(r'^\s+\S', line):
            continue
        if _is_rst_syntax_line(line):
            continue
        norm_line = re.sub(r'\s+', ' ', _normalize_rst_source(line, label_map)).strip()
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
