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

    # Parse index paths from index.toon (tab-separated, path is last column)
    lines = idx.read_text(encoding="utf-8").splitlines()
    indexed_paths: set[str] = set()
    for line in lines[1:]:  # skip header
        parts = line.split("\t")
        if parts:
            indexed_paths.add(parts[-1].strip())

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

_URL_RE = re.compile(r'https?://[^\s\'"<>)\]]+')
_URL_TRAILING_PUNCT_RE = re.compile(r'[.,;:]+$')
_RST_TARGET_LINE_RE = re.compile(r'^(?:\.\.?\s+_|__\s+https?://)')


def _clean_url(url: str) -> str:
    return _URL_TRAILING_PUNCT_RE.sub('', url)


def _source_urls(source_text: str, fmt: str) -> list[str]:
    urls = []
    for line in source_text.splitlines():
        if fmt == "rst" and _RST_TARGET_LINE_RE.match(line.strip()):
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

def _strip_md_to_plain_lines(text: str) -> list[str]:
    """Strip Markdown syntax from JSON content; return non-empty searchable lines."""
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
    if re.match(r'^\.\.\s*(\S.*::|$)', s):
        return True
    if re.match(r'^\.\.\s+_[a-zA-Z0-9_-]+:', s):
        return True
    if re.match(r'^\.\.\s+\|', s):
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


def check_content_completeness(source_text: str, data: dict, fmt: str) -> list[str]:
    """QC1/QC2/QC3/QC4: sequential-delete algorithm."""
    if _no_knowledge(data):
        return []

    sections = data.get("sections", [])
    top_title = data.get("title", "")
    top_content = data.get("content", "")

    if not sections and not top_title and not top_content:
        return []

    # Build search units: (text, section_id, is_content)
    search_units: list[tuple[str, str, bool]] = []

    if top_title:
        search_units.append((top_title, "__top__", False))
    if top_content and fmt == "rst":
        # RST→JSON converts RST to MD; strip MD syntax to find plain text in RST source
        for line in _strip_md_to_plain_lines(top_content):
            search_units.append((line, "__top__", True))
    elif top_content:
        # MD source: JSON content is MD verbatim; xlsx: content is plain
        search_units.append((top_content, "__top__", True))

    for sec in sections:
        title = sec.get("title", "")
        content = sec.get("content", "")
        sid = sec.get("id", "?")
        if title:
            search_units.append((title, sid, False))
        if content and fmt == "rst":
            for line in _strip_md_to_plain_lines(content):
                search_units.append((line, sid, True))
        elif content:
            search_units.append((content, sid, True))

    if not search_units:
        return []

    issues: list[str] = []
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

    if fmt == "rst":
        in_structural = False
        for line in remaining.split('\n'):
            s = line.strip()
            if s and re.match(r'\.\.\s+\S', s):
                in_structural = bool(_RST_STRUCTURAL_DIRECTIVES.match(s))
            if not s:
                continue
            if in_structural and re.match(r'^\s+\S', line):
                continue
            if not _is_rst_syntax_line(line):
                issues.append(f"[QC1] source content not captured: {line.strip()[:50]!r}")
    else:
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

def verify_file(source_path, json_path, fmt, knowledge_dir=None) -> list[str]:
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
        issues.extend(check_content_completeness(source_text, data, fmt))
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
