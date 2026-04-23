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

    Per §3-2 AST-only principle: for RST, walk the doctree and collect
    `reference.refuri` values that are http(s) URLs. For MD, fall back to
    regex (MD AST not yet available in verify).
    """
    urls: list[str] = []
    if fmt == "rst":
        from docutils import nodes
        from scripts.common import rst_ast

        try:
            doctree, _ = rst_ast.parse(source_text)
        except Exception:
            return urls
        for ref in doctree.findall(nodes.reference):
            refuri = ref.get("refuri", "")
            if refuri.startswith(("http://", "https://")):
                urls.append(refuri)
        return urls

    # Markdown (or other) — keep the legacy regex until MD side is AST-ified
    for line in source_text.splitlines():
        for url in _URL_RE.findall(line):
            u = _clean_url(url)
            if u:
                urls.append(u)
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
    return normalise_rst(text, label_map=label_map or {}, strict_unknown=False)


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

    Per the tokenizer-based design (rbkc-verify-quality-design.md §3-1 手順
    0), the normalised source is already in MD-equivalent form, so JSON
    content can be matched against it after only whitespace normalisation.
    """
    units: list[tuple[str, str, str, bool]] = []
    top_title = data.get("title", "")
    top_content = data.get("content", "")

    def _norm(t: str) -> str:
        # Strip MD image syntax entirely — alt text may contain brackets,
        # so use a loop to handle nested brackets like ![[1]_](url).
        # URL may contain one level of balanced parens (common in Javadoc
        # anchors like ``#findAll(java.lang.Class)``).
        prev = None
        while prev != t:
            prev = t
            t = re.sub(r'!\[[^\n]*?\]\((?:[^()\n]|\([^)\n]*\))+\)', '', t, count=1)
        # Strip URL bodies from [text](url), keep visible text.
        t = re.sub(r'\[([^\]\n]+)\]\((?:[^()\n]|\([^)\n]*\))+\)', r'\1', t)
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
    norm_source_raw = _normalize_rst_source(source_text, label_map)
    # Apply the same URL-stripping normalisation as _build_rst_search_units.
    prev = None
    norm_source = norm_source_raw
    while prev != norm_source:
        prev = norm_source
        norm_source = re.sub(r'!\[[^\n]*?\]\((?:[^()\n]|\([^)\n]*\))+\)', '', norm_source, count=1)
    norm_source = re.sub(r'\[([^\]\n]+)\]\((?:[^()\n]|\([^)\n]*\))+\)', r'\1', norm_source)
    norm_source = re.sub(r'\s+', ' ', norm_source).strip()
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

    # QC1: delete JSON units from normalised source in JSON order, then
    # check the residue. Per design spec §3-1 手順 3, residue must match the
    # allowed-syntax list (post-tokenizer MD residue: fences, table pipes,
    # blockquote markers, etc.).
    residue = norm_source
    for _orig, norm_unit, _sid, _is_c in search_units:
        if not norm_unit:
            continue
        idx = residue.find(norm_unit)
        if idx == -1:
            continue
        residue = residue[:idx] + residue[idx + len(norm_unit):]

    # Check residue against allowed-syntax list. Allowed residue is pure
    # whitespace and converter-emitted MD markup tokens.
    cleaned = _strip_allowed_residue(residue)
    if cleaned.strip():
        # Trim long residue for readability in the issue message.
        snippet = cleaned.strip()[:80]
        issues.append(f"[QC1] residue not captured in JSON: {snippet!r}")

    return issues


# Allowed residue tokens in the normalised RST source after JSON unit
# deletion. Per rbkc-verify-quality-design.md §3-1 "許容構文要素リスト".
# These are the MD markup tokens the converter emits but that appear in the
# normalised source with slightly different surrounding whitespace than the
# JSON content has.
_ADMONITION_RESIDUE_LABELS = (
    "Note", "Tip", "Warning", "Important", "Attention", "Hint",
    "Caution", "Danger", "Error", "See Also",
    "Deprecated", "Version Added", "Version Changed",
)
_ALLOWED_RESIDUE_PATTERNS = [
    # Admonition header residues (e.g. "Note" left after ">" and "**" were stripped)
    re.compile(r"\b(?:" + "|".join(re.escape(l) for l in _ADMONITION_RESIDUE_LABELS) + r")\b"),
    # MD fence markers (code-block output)
    re.compile(r"```[A-Za-z0-9_+-]*"),
    # MD table separator rows
    re.compile(r"\|\s*-+\s*(?:\|\s*-+\s*)+\|"),
    # Bare MD list markers (bullets, enumerators)
    re.compile(r"(?m)^\s*[*+\-]\s*$"),
    re.compile(r"(?m)^\s*\d+\.\s*$"),
    # MD blockquote markers
    re.compile(r"(?m)^\s*>\s*"),
    # Bold/italic leftovers
    re.compile(r"\*\*"),
    # Inline code tick leftovers
    re.compile(r"`"),
    # Table pipe residue
    re.compile(r"\|"),
    # Bracket residue from removed [text](url)
    re.compile(r"[\[\]()]"),
    # Punctuation / whitespace (ASCII + common Japanese punctuation)
    re.compile(r"[\s、。,\.:!?;()（）【】「」『』\-—#*+~\^]+"),
    # Stray directive/comment markers
    re.compile(r"\.\.+"),
    # Stray heading marker hashes (if MD heading got partially consumed)
    re.compile(r"#+"),
]


def _strip_allowed_residue(text: str) -> str:
    """Remove all allowed syntax residue tokens; return what's left."""
    out = text
    # Apply each pattern iteratively until stable.
    prev = None
    while prev != out:
        prev = out
        for pat in _ALLOWED_RESIDUE_PATTERNS:
            out = pat.sub(" ", out)
        out = re.sub(r"\s+", " ", out)
    return out


def _check_md_content_completeness(
    source_text: str, data: dict, issues: list[str]
) -> list[str]:
    """QC1-QC4 for MD sources (verbatim comparison)."""
    # Strip HTML comments: converter elides these; verify should too.
    source_text = re.sub(r"<!--.*?-->", "", source_text, flags=re.DOTALL)

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

# MD internal link regex retained for the MD format path below (QL1 for MD
# sources is still regex-based until md.py is AST-ified).
_MD_INTERNAL_LINK_RE = re.compile(r'\[([^\]]+)\]\((?!https?://)([^)]+)\)')


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

        # :ref: / named references
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

        # figure nodes
        for fig in doctree.findall(nodes.figure):
            caption_text = ""
            uri = ""
            for ch in fig.children:
                if isinstance(ch, nodes.caption):
                    caption_text = ch.astext().strip()
                elif isinstance(ch, nodes.image):
                    uri = ch.get("uri", "")
            # Caption that is only an RST inline construct (e.g. "[1]_")
            # yields no visible text after docutils rendering; fall back to
            # filename.
            caption_for_check = caption_text if _has_visible_text(caption_text) else ""
            check_text = caption_for_check or (_Path(uri).name if uri else "")
            if check_text and check_text not in json_full:
                issues.append(
                    f"[QL1] figure caption/filename missing from JSON: {check_text!r}"
                )

        # image nodes outside figures
        for img in doctree.findall(nodes.image):
            if isinstance(img.parent, nodes.figure):
                continue
            alt = (img.get("alt") or "").strip()
            uri = img.get("uri", "")
            check_text = alt or (_Path(uri).name if uri else "")
            if check_text and check_text not in json_full:
                issues.append(
                    f"[QL1] image alt/filename missing from JSON: {check_text!r}"
                )

        # literalinclude is rendered as literal_block; the body text is
        # expected in JSON. docutils embeds the included text verbatim when
        # file_insertion_enabled=True; the converter emits it as a fenced
        # code block, so JSON should contain the body.
        for lb in doctree.findall(nodes.literal_block):
            body = lb.astext().strip()
            if not body:
                continue
            # A short non-empty literal_block must at least share its first
            # non-blank line with the JSON to be considered reflected.
            first_line = next(
                (ln.strip() for ln in body.splitlines() if ln.strip()), ""
            )
            if first_line and first_line not in json_full:
                # Literal content missing from JSON is QC1/QC2 territory —
                # skip here to avoid double-reporting.
                continue

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
