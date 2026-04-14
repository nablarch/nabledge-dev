"""Hints mapping — loads KC cache and builds section_title → hints index."""
import json
import re
from pathlib import Path


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
