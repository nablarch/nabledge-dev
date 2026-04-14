"""Hints — KC cache mapping (Phase 1) + Stage 1 mechanical extraction (Phase 3)."""
import json
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Stage 1: mechanical extraction from Markdown content
# ---------------------------------------------------------------------------

# PascalCase class/interface names (≥3 chars, starts uppercase, has at least one more uppercase)
_PASCAL_RE = re.compile(r"\b([A-Z][a-z]+(?:[A-Z][a-zA-Z0-9]*)+)\b")

# Annotation names: @Foo, @FooBar
_ANNOTATION_RE = re.compile(r"(@[A-Z][a-zA-Z0-9]+)\b")

# Fully qualified class names: nablarch.common.dao.UniversalDao
_FQN_RE = re.compile(r"\b([a-z][a-z0-9]*(?:\.[a-z][a-z0-9]*)+\.[A-Z][a-zA-Z0-9]+)\b")

# Bold text: **keyword**
_BOLD_RE = re.compile(r"\*\*([^*\n]+?)\*\*")

# Heading text in content (h4+ kept as #### inside sections)
_HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)

# Method reference: ClassName#methodName → extract ClassName
_METHOD_REF_RE = re.compile(r"`([A-Z][a-zA-Z0-9]+)#[a-zA-Z0-9_]+`")


def extract_hints(content: str) -> list[str]:
    """Stage 1: extract hints from Markdown content using regex patterns.

    Extracts:
    - PascalCase class/interface names (≥3 chars)
    - Annotation names (@Foo)
    - Fully qualified class names (a.b.ClassName)
    - Bold text (**keyword**)
    - Sub-heading text (#### heading)
    - Class names from method references (ClassName#method)

    Returns a deduplicated list (insertion order preserved).
    """
    found: list[str] = []
    seen: set[str] = set()

    def _add(token: str) -> None:
        token = token.strip()
        if token and token not in seen:
            seen.add(token)
            found.append(token)

    # Method references first (before backtick content is consumed)
    for m in _METHOD_REF_RE.finditer(content):
        _add(m.group(1))

    # FQN (includes trailing class name)
    for m in _FQN_RE.finditer(content):
        _add(m.group(1))

    # Annotations
    for m in _ANNOTATION_RE.finditer(content):
        _add(m.group(1))

    # PascalCase (skip single-word short tokens handled by method refs)
    for m in _PASCAL_RE.finditer(content):
        _add(m.group(1))

    # Bold text
    for m in _BOLD_RE.finditer(content):
        _add(m.group(1))

    # Sub-headings
    for m in _HEADING_RE.finditer(content):
        _add(m.group(1).strip())

    return found


def merge_hints(stage1: list[str], stage2: list[str]) -> list[str]:
    """Merge Stage 1 and Stage 2 hints: deduplicate and sort.

    Args:
        stage1: Mechanically extracted hints from content.
        stage2: Hints from KC cache lookup.

    Returns:
        Sorted, deduplicated list of all hints.
    """
    combined = dict.fromkeys(stage1 + stage2)  # preserves insertion order, deduplicates
    return sorted(combined.keys())


_SPLIT_SUFFIX_RE = re.compile(r"--s\d+$")


def _base_file_id(file_id: str) -> str:
    """Strip KC split suffix (--s1, --s2, …) to get the base RST file id."""
    return _SPLIT_SUFFIX_RE.sub("", file_id)


def build_hints_index(cache_dir: Path) -> dict[str, dict[str, list[str]]]:
    """Load KC cache and return ``{base_file_id: {section_title: hints}}``.

    Args:
        cache_dir: Root of the KC cache, e.g. ``.cache/v6/``.
                   Expects a ``knowledge/`` subdirectory containing ``*.json`` files.

    Returns:
        Nested dict.  Outer key is the base RST file id (KC split suffix
        stripped).  Inner key is the section title from ``index[].title``.
        Value is the list of hints strings.

    Raises:
        FileNotFoundError: ``cache_dir/knowledge/`` does not exist.
    """
    knowledge_dir = cache_dir / "knowledge"
    if not knowledge_dir.is_dir():
        raise FileNotFoundError(f"Knowledge cache directory not found: {knowledge_dir}")

    result: dict[str, dict[str, list[str]]] = {}

    for json_path in knowledge_dir.rglob("*.json"):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        base_id = _base_file_id(data["id"])

        if base_id not in result:
            result[base_id] = {}

        for entry in data.get("index", []):
            title: str = entry["title"]
            hints: list[str] = entry.get("hints", [])
            result[base_id][title] = hints

    return result


def lookup_hints(
    hints_map: dict[str, dict[str, list[str]]],
    file_id: str,
    section_title: str,
) -> list[str]:
    """Return hints for a given file_id and section_title.

    Returns an empty list if not found — never raises.
    """
    return hints_map.get(file_id, {}).get(section_title, [])
