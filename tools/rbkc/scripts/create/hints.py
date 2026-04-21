"""Hints — KC cache mapping (Phase 1) + Step A/B catalog-based mapping (Phase 10-6)."""
import json
import re
from pathlib import Path


_SPLIT_SUFFIX_RE = re.compile(r"--s\d+$")


def _base_file_id(file_id: str) -> str:
    """Strip KC split suffix (--s1, --s2, …) to get the base RST file id."""
    return _SPLIT_SUFFIX_RE.sub("", file_id)


# ---------------------------------------------------------------------------
# Step A: catalog Expected Sections → KC index mapping
# ---------------------------------------------------------------------------

def _map_step_a(
    kc_index: list[dict],
    expected: list[str],
) -> dict[str, list[str]]:
    """Map KC index entries to RST expected section headings (Step A).

    Args:
        kc_index: List of KC index dicts with 'title' and 'hints'.
        expected: Non-empty RST h2 headings from catalog section_range.sections.

    Returns:
        {rst_heading: [hints]}
    """
    result: dict[str, list[str]] = {sec: [] for sec in expected}
    pointer = 0

    for entry in kc_index:
        kc_title: str = entry.get("title", "")
        hints: list[str] = entry.get("hints", [])

        if pointer >= len(expected):
            # Overflow → append to last expected
            result[expected[-1]].extend(hints)
            continue

        # 1. Direct match
        if kc_title in expected:
            target = kc_title
            # Advance pointer to next expected after matched
            try:
                idx = expected.index(kc_title, pointer)
                pointer = idx + 1
            except ValueError:
                pass
        else:
            # 2. Substring match: find longest Expected (from pointer onward) that is
            # a substring of kc_title.  Searching from pointer prevents re-using
            # sections that have already been consumed.
            matches = [e for e in expected[pointer:] if e and e in kc_title]
            if matches:
                target = max(matches, key=len)
                # Advance pointer past matched expected
                try:
                    idx = expected.index(target, pointer)
                    pointer = idx + 1
                except ValueError:
                    pass
            else:
                # 3. Fallback: use current pointer (do not advance)
                target = expected[pointer]

        result[target].extend(hints)

    return result


# ---------------------------------------------------------------------------
# Step B: content overlap mapping
# ---------------------------------------------------------------------------

def _extract_rst_sections(rst_text: str) -> list[tuple[str, str]]:
    """Extract (heading, content) pairs from RST source.

    Detects underline-only headings (not overline). Returns list of
    (heading_text, section_body_text) in document order.
    """
    lines = rst_text.splitlines()
    sections: list[tuple[str, str]] = []
    underline_chars = set("=-~^+#*_.:`!\"'")
    i = 0
    current_heading: str | None = None
    current_body: list[str] = []
    in_heading_detection = False

    def is_underline(s: str) -> bool:
        if len(s) < 3:
            return False
        return len(set(s.strip())) == 1 and s.strip()[0] in underline_chars

    while i < len(lines):
        line = lines[i]
        # Underline-only heading detection
        if (
            i + 1 < len(lines)
            and line.strip()
            and not is_underline(line)
            and is_underline(lines[i + 1])
            and not (i > 0 and is_underline(lines[i - 1])
                     and lines[i - 1].rstrip() and lines[i + 1].rstrip()
                     and lines[i - 1].rstrip()[0] == lines[i + 1].rstrip()[0])
        ):
            # Save previous section
            if current_heading is not None:
                sections.append((current_heading, "\n".join(current_body)))
            current_heading = line.strip()
            current_body = []
            i += 2
            continue

        if current_heading is not None:
            current_body.append(line)
        i += 1

    if current_heading is not None:
        sections.append((current_heading, "\n".join(current_body)))

    return sections


def _keyword_overlap(text_a: str, text_b: str) -> float:
    """Keyword overlap ratio: fraction of words in text_a that appear in text_b."""
    words_a = set(re.findall(r"[^\s、。「」【】\[\]()（）,;：:!?！？]+", text_a))
    if not words_a:
        return 0.0
    words_b = set(re.findall(r"[^\s、。「」【】\[\]()（）,;：:!?！？]+", text_b))
    overlap = sum(1 for w in words_a if w in words_b)
    return overlap / len(words_a)


def _map_step_b(
    kc_index: list[dict],
    kc_sections: dict[str, str],
    rst_sections: list[tuple[str, str]],
    threshold: float = 0.25,
) -> dict[str, list[str]]:
    """Map KC index entries to RST section headings using content overlap (Step B).

    Args:
        kc_index: KC index entries (id, title, hints).
        kc_sections: {section_id: content_text} from KC knowledge file.
        rst_sections: [(heading, body_text)] from RST source.
        threshold: Minimum overlap ratio to accept a match.

    Returns:
        {rst_heading: [hints]}
    """
    result: dict[str, list[str]] = {}

    for entry in kc_index:
        sec_id: str = entry.get("id", "")
        hints: list[str] = entry.get("hints", [])
        kc_content = kc_sections.get(sec_id, "")
        if not kc_content or not rst_sections:
            continue

        best_heading = None
        best_score = 0.0
        for heading, body in rst_sections:
            score = _keyword_overlap(kc_content, body)
            if score > best_score:
                best_score = score
                best_heading = heading

        if best_heading and best_score >= threshold:
            if best_heading not in result:
                result[best_heading] = []
            result[best_heading].extend(hints)

    return result


# ---------------------------------------------------------------------------
# Main index builder
# ---------------------------------------------------------------------------

def build_hints_index(
    cache_dir: Path,
    catalog_path: Path | None = None,
    repo_root: Path | None = None,
) -> dict[str, dict[str, list[str]]]:
    """Load KC cache and return ``{base_file_id: {rst_heading: hints}}``.

    When *catalog_path* is provided, uses catalog Expected Sections for Step A
    mapping (or content overlap for Step B when sections list is empty).
    When *catalog_path* is not provided, falls back to KC section title keys.

    Args:
        cache_dir: Root of the KC cache (contains knowledge/ subdirectory).
        catalog_path: Path to catalog.json.  Enables Step A/B mapping.
        repo_root: Repository root for resolving RST source_path in catalog
            (required for Step B; ignored if catalog has Expected Sections).

    Returns:
        Nested dict.  Outer key is the base RST file id.
        Inner key is the RST section heading (or KC section title when no catalog).
        Value is the list of hints.

    Raises:
        FileNotFoundError: ``cache_dir/knowledge/`` does not exist.
    """
    knowledge_dir = cache_dir / "knowledge"
    if not knowledge_dir.is_dir():
        raise FileNotFoundError(f"Knowledge cache directory not found: {knowledge_dir}")

    # Load catalog index if provided
    catalog_index: dict[str, dict] = {}  # base_name → catalog entry (part-1 only)
    if catalog_path and catalog_path.exists():
        catalog_data = json.loads(catalog_path.read_text(encoding="utf-8"))
        for entry in catalog_data.get("files", []):
            base_name = entry.get("base_name") or _base_file_id(entry.get("id", ""))
            if base_name and base_name not in catalog_index:
                # Keep only the first (part-1) entry per base_name.
                # Part-1 holds the RST-aligned section_range.sections; later parts
                # carry KC-level titles that must not become hint index keys.
                catalog_index[base_name] = entry

    # Collect all KC knowledge files, grouped by base_id
    # raw_kc: {base_id: {kc_entries}} where kc_entries accumulates index + sections
    raw_kc: dict[str, dict] = {}

    for json_path in knowledge_dir.rglob("*.json"):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        file_id: str = data.get("id", "")
        base_id = _base_file_id(file_id)

        if base_id not in raw_kc:
            raw_kc[base_id] = {"index": [], "sections": {}}

        raw_kc[base_id]["index"].extend(data.get("index", []))
        raw_kc[base_id]["sections"].update(data.get("sections", {}))

    result: dict[str, dict[str, list[str]]] = {}

    for base_id, kc_data in raw_kc.items():
        kc_index = kc_data["index"]
        kc_sections = kc_data["sections"]

        # Normalize KC base_id to RBKC file_id format: replace _ with -
        # KC filenames preserve underscores; RBKC _generate_id() replaces _ with -.
        out_id = base_id.replace("_", "-")

        cat_entry = catalog_index.get(base_id)

        if cat_entry is None:
            # No catalog entry → KC title keys (fallback)
            section_map: dict[str, list[str]] = {}
            for entry in kc_index:
                title = entry.get("title", "")
                hints = entry.get("hints", [])
                if title not in section_map:
                    section_map[title] = []
                section_map[title].extend(hints)
            result[out_id] = section_map
            continue

        expected_raw = cat_entry.get("section_range", {}).get("sections", [])
        expected = [s for s in expected_raw if s]  # filter empty strings

        if expected:
            # Step A: catalog Expected Sections → KC index mapping
            result[out_id] = _map_step_a(kc_index, expected)
        elif repo_root is not None:
            # Step B: content overlap with RST source
            source_path_str = cat_entry.get("source_path", "")
            rst_path = repo_root / source_path_str if source_path_str else None
            if rst_path and rst_path.exists():
                rst_sections = _extract_rst_sections(
                    rst_path.read_text(encoding="utf-8", errors="replace")
                )
                result[out_id] = _map_step_b(kc_index, kc_sections, rst_sections)
            else:
                # RST not found → KC title fallback
                section_map = {}
                for entry in kc_index:
                    title = entry.get("title", "")
                    if title not in section_map:
                        section_map[title] = []
                    section_map[title].extend(entry.get("hints", []))
                result[out_id] = section_map
        else:
            # No repo_root → KC title fallback
            section_map = {}
            for entry in kc_index:
                title = entry.get("title", "")
                if title not in section_map:
                    section_map[title] = []
                section_map[title].extend(entry.get("hints", []))
            result[out_id] = section_map

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
