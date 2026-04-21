"""RBKC CLI operations: create, update, delete, verify.

Orchestrates the full pipeline:
    scan → classify → convert → write JSON → save snapshot

Knowledge JSON schema:
    {
        "id": "file-id",
        "title": "Document Title",
        "no_knowledge_content": false,
        "sections": [
            {
                "id": "s1",
                "title": "Section Title",
                "content": "Markdown content",
                "hints": ["keyword1", "keyword2"]
            }
        ]
    }

Public API:
    create(version, repo_root, output_dir, state_dir, files=None) -> int
    update(version, repo_root, output_dir, state_dir, files=None) -> int
    delete(version, repo_root, output_dir, state_dir, files=None) -> int
    verify(version, repo_root, output_dir, files=None) -> bool
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from scripts.create.classify import FileInfo, classify_sources
from scripts.create.differ import diff_snapshot, load_snapshot, make_snapshot, save_snapshot
from scripts.create.docs import generate_docs
from scripts.create.hints import build_hints_index
from scripts.create.index import generate_index
from scripts.create.resolver import collect_asset_refs, copy_assets
from scripts.create.scan import scan_sources
from scripts.common.constants import FILE_SENTINEL
from scripts.common.labels import build_label_map
from scripts.verify.verify import (
    verify_file,
    verify_docs_md,
    check_index_coverage,
    check_docs_coverage,
    check_source_links,
    check_json_docs_md_consistency,
    check_hints_file_consistency,
)


# ---------------------------------------------------------------------------
# Converter dispatch
# ---------------------------------------------------------------------------

def _converter_for(fmt: str, filename: str):
    """Return the appropriate convert() function for the given format/filename."""
    if fmt == "rst":
        from scripts.create.converters.rst import convert
        return convert
    if fmt == "md":
        from scripts.create.converters.md import convert
        return convert
    if fmt == "xlsx":
        if filename.endswith("-releasenote.xlsx") or "releasenote" in filename:
            from scripts.create.converters.xlsx_releasenote import convert
            return convert
        # Default xlsx: security table
        from scripts.create.converters.xlsx_security import convert
        return convert
    raise ValueError(f"Unknown format: {fmt!r}")


def load_existing_hints(output_dir: Path) -> dict[str, list[dict]]:
    """Load hints from existing RBKC-format knowledge JSON files (array form).

    Reads all JSON files under *output_dir* that use RBKC format (sections as
    a list of dicts). KC-format files (sections as a dict) are skipped.  The
    returned form matches the hints-file schema so both sources feed the same
    positional pop() pipeline.

    Returns:
        {file_id: [{"title", "hints"}, ...]} preserving section order.  Empty
        dict if directory is absent or contains no RBKC-format files.
    """
    if not output_dir.exists():
        return {}

    result: dict[str, list[dict]] = {}
    for json_path in output_dir.rglob("*.json"):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        file_id = data.get("id", "")
        sections = data.get("sections", [])

        # Skip KC-format files (sections is a dict, not a list)
        if not isinstance(sections, list):
            continue

        entries: list[dict] = []
        for sec in sections:
            if not isinstance(sec, dict):
                continue
            title = sec.get("title", "")
            hints = sec.get("hints", [])
            if isinstance(hints, list):
                entries.append({"title": title, "hints": hints})

        if file_id:
            result[file_id] = entries

    return result


def _pop_hints_for_title(pending: list[dict], section_title: str) -> list[str]:
    """Pop the head entry of *pending* if its title matches *section_title*.

    Hints files use array form (`[{"title", "hints"}, ...]`) so that same-title
    sections (e.g. h2 `使用方法` and h3 `使用方法`) can have independent hints
    aligned to source-appearance order.  Callers iterate sections in order and
    consume the head entry when its title matches.

    Returns:
        The hints list of the consumed entry, or [] when pending is empty or
        the head title differs.  A mismatch leaves *pending* untouched so the
        positional alignment between source sections and hints entries is
        preserved — surfacing drift instead of silently skipping.
    """
    if not pending:
        return []
    head = pending[0]
    if head.get("title", "") != section_title:
        return []
    pending.pop(0)
    hints = head.get("hints", [])
    return hints if isinstance(hints, list) else []


def _pop_top_level_hints(pending: list[dict], top_title: str) -> list[str]:
    """Pop the head entry when it represents the file-level hint entry.

    The head entry is the file-level entry if either:
    - its ``title`` is the literal ``"__file__"`` sentinel (xlsx: JSON title
      is empty, so the hints file uses the sentinel to mark file-level hints);
    - its ``title`` equals the JSON top-level title (rst/md h1).

    Returns:
        The popped hints list, or [] when no file-level entry is present.
    """
    if not pending:
        return []
    head_title = pending[0].get("title", "")
    if head_title == FILE_SENTINEL or head_title == top_title:
        head = pending.pop(0)
        hints = head.get("hints", [])
        return hints if isinstance(hints, list) else []
    return []


def _normalize_kc_to_array(
    kc_hints: dict[str, dict[str, list[str]]],
) -> dict[str, list[dict]]:
    """Convert legacy KC-cache dict form to array form used by the hints file.

    KC cache yields `{file_id: {title: hints}}` because it indexes by section
    title (no same-title support).  We wrap each entry as `{"title", "hints"}`
    to match the hints file's array schema, preserving the dict insertion order.
    """
    result: dict[str, list[dict]] = {}
    for file_id, title_map in kc_hints.items():
        entries = [{"title": t, "hints": list(h)} for t, h in title_map.items()]
        result[file_id] = entries
    return result


def hints_path(repo_root: Path, version: str) -> Path:
    """Return the path to the persistent hints file for the given version."""
    return repo_root / "tools/rbkc/hints" / f"v{version}.json"


def load_hints_file(repo_root: Path, version: str) -> dict[str, list[dict]]:
    """Load hints from hints/v{version}.json (array form).

    The file schema is `{"version", "hints": {file_id: [{"title", "hints"}, ...]}}`.
    Returns an empty dict when the file does not exist.
    """
    path = hints_path(repo_root, version)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("hints", {})


def _hints_index(repo_root: Path, version: str):
    """Load hints index for the given version.

    Returns an empty dict when the KC cache does not exist (expected in
    fresh setups).  Re-raises unexpected errors (e.g. corrupt JSON) after
    printing a warning so the caller can decide how to proceed.
    """
    try:
        cache_dir = repo_root / "tools/knowledge-creator/.cache" / f"v{version}"
        catalog_path = repo_root / "tools/knowledge-creator/.cache" / f"v{version}" / "catalog.json"
        return build_hints_index(cache_dir, catalog_path, repo_root)
    except FileNotFoundError:
        return {}
    except Exception as exc:
        print(f"Warning: hints index failed for v{version}: {exc}", file=sys.stderr)
        raise


# ---------------------------------------------------------------------------
# JSON writer
# ---------------------------------------------------------------------------

def _convert_and_write(
    fi: FileInfo,
    output_dir: Path,
    hints_idx: dict,
    existing_hints: dict | None = None,
    label_map: dict | None = None,
) -> None:
    """Convert one source file and write its knowledge JSON to *output_dir*.

    Args:
        fi: FileInfo for the source file.
        output_dir: Output directory for knowledge JSON files.
        hints_idx: Array-form hints index — either hints/v{version}.json or
                   KC cache normalized via _normalize_kc_to_array().
        existing_hints: Array-form existing RBKC hints from load_existing_hints().
                        Used as a fallback when hints_idx has no entry.
        label_map: RST label→title map for :ref: resolution.
    """
    convert = _converter_for(fi.format, fi.source_path.name)

    if fi.format == "rst":
        result = convert(
            fi.source_path.read_text(encoding="utf-8", errors="replace"),
            fi.file_id,
            label_map=label_map,
        )
    elif fi.format == "md":
        result = convert(fi.source_path.read_text(encoding="utf-8", errors="replace"), fi.file_id)
    else:
        result = convert(fi.source_path, fi.file_id)

    # Pick primary hints source (hints file / KC cache) per file_id, falling
    # back to prior-run hints only when the primary has nothing for this file.
    primary_pending = list(hints_idx.get(fi.file_id, [])) if hints_idx else []
    fallback_pending: list[dict] = []
    if not primary_pending and existing_hints is not None:
        fallback_pending = list(existing_hints.get(fi.file_id, []))

    # Phase 21-D (session 37): the head entry is the file-level hint entry
    # when its title matches the JSON top-level title OR equals the "__file__"
    # sentinel (used for xlsx where JSON title is "").  Pop it into top-level
    # `hints`.  Otherwise top-level `hints` = [].
    top_hints = _pop_top_level_hints(primary_pending, result.title)
    if not top_hints and fallback_pending:
        top_hints = _pop_top_level_hints(fallback_pending, result.title)

    sections = []
    for idx, sec in enumerate(result.sections, start=1):
        sid = f"s{idx}"
        hints = _pop_hints_for_title(primary_pending, sec.title)
        if not hints and fallback_pending:
            hints = _pop_hints_for_title(fallback_pending, sec.title)
        sections.append({
            "id": sid,
            "title": sec.title,
            "content": sec.content,
            "hints": hints,
        })

    # index[] is deterministically derived from top-level hints + sections[]
    # (see rbkc-json-schema-design.md §2-2 / §2-3). __file__ entry is prepended
    # only when the file has top-level hints, since it represents the file-level
    # search unit.
    index_entries: list[dict] = []
    if top_hints:
        index_entries.append({
            "id": "__file__",
            "title": result.title,
            "hints": top_hints,
        })
    for sec in sections:
        index_entries.append({
            "id": sec["id"],
            "title": sec["title"],
            "hints": sec["hints"],
        })

    data = {
        "id": fi.file_id,
        "title": result.title,
        "content": getattr(result, "content", ""),
        "hints": top_hints,
        "no_knowledge_content": result.no_knowledge_content,
        "sections": sections,
        "index": index_entries,
    }

    out_path = output_dir / fi.output_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Snapshot path helper
# ---------------------------------------------------------------------------

def _snapshot_path(state_dir: Path, version: str) -> Path:
    return state_dir / version / "snapshot.json"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create(
    version: str,
    repo_root: Path,
    output_dir: Path,
    state_dir: Path,
    files: list[str] | None = None,
) -> int:
    """Create all knowledge JSON files for the given version.

    Pre-cleans output/docs/assets directories, converts all sources, copies
    assets, generates index.toon, generates browsable docs, and saves a
    snapshot.

    Args:
        version: Nablarch version string.
        repo_root: Repository root.
        output_dir: Output directory for knowledge JSON files.
        state_dir: Directory for snapshot files.
        files: Optional list of specific source file paths (relative to repo_root).

    Returns:
        Number of files created.
    """
    import shutil

    docs_dir = output_dir.parent / "docs"
    index_path = output_dir / "index.toon"

    # Load existing hints BEFORE cleaning output directory.
    # create() pre-cleans output_dir with rmtree, so hints must be captured first.
    existing_hints = load_existing_hints(output_dir)

    # Pre-clean: remove all previous output so stale files don't persist.
    # This also removes assets/ (output_dir/assets/) as a subdirectory of
    # output_dir.  update() and delete() do NOT pre-clean, so stale assets
    # can accumulate there; a subsequent create() will clear them.
    if output_dir.exists():
        shutil.rmtree(output_dir)
    if docs_dir.exists():
        shutil.rmtree(docs_dir)

    sources = scan_sources(version, repo_root, files)
    file_infos = classify_sources(sources, version, repo_root)
    # Prefer persistent hints file (array form) over KC cache (normalized to array form)
    hints_idx = load_hints_file(repo_root, version) or _normalize_kc_to_array(_hints_index(repo_root, version))

    # Build RST label map for :ref: resolution in converters
    from scripts.create.scan import _source_roots
    label_map: dict = {}
    for src_root in _source_roots(version, repo_root):
        if src_root.exists():
            label_map.update(build_label_map(src_root))

    all_asset_refs = []
    for fi in file_infos:
        _convert_and_write(fi, output_dir, hints_idx, existing_hints, label_map)
        if fi.format == "rst":
            all_asset_refs.extend(collect_asset_refs(fi.source_path, fi.file_id))

    copy_assets(all_asset_refs, output_dir)
    generate_index(output_dir, version, index_path)
    generate_docs(output_dir, docs_dir, version)

    snap = make_snapshot(file_infos, repo_root, version)
    save_snapshot(snap, _snapshot_path(state_dir, version))
    return len(file_infos)


def update(
    version: str,
    repo_root: Path,
    output_dir: Path,
    state_dir: Path,
    files: list[str] | None = None,
) -> int:
    """Update knowledge JSON files for changed source files only.

    Compares current source hashes against saved snapshot to identify
    changes, then re-converts only the changed files.

    Returns:
        Number of files re-converted.
    """
    sources = scan_sources(version, repo_root, files)
    file_infos = classify_sources(sources, version, repo_root)
    # Prefer persistent hints file over KC cache (KC cache may not exist at update time)
    hints_idx = load_hints_file(repo_root, version) or _hints_index(repo_root, version)
    # Load existing hints before reconverting so carry-over is preserved for
    # files whose source changed (same as create() semantics).
    existing_hints = load_existing_hints(output_dir)

    # Build RST label map for :ref: resolution in converters
    from scripts.create.scan import _source_roots
    label_map: dict = {}
    for src_root in _source_roots(version, repo_root):
        if src_root.exists():
            label_map.update(build_label_map(src_root))

    snap_path = _snapshot_path(state_dir, version)
    old_snap = load_snapshot(snap_path)
    new_snap = make_snapshot(file_infos, repo_root, version)

    added, modified, _deleted = diff_snapshot(old_snap, new_snap)
    changed_keys = set(added + modified)

    changed_asset_refs = []
    count = 0
    for fi in file_infos:
        rel = str(fi.source_path.relative_to(repo_root)).replace("\\", "/")
        if rel in changed_keys:
            _convert_and_write(fi, output_dir, hints_idx, existing_hints, label_map)
            if fi.format == "rst":
                changed_asset_refs.extend(collect_asset_refs(fi.source_path, fi.file_id))
            count += 1

    copy_assets(changed_asset_refs, output_dir)
    generate_index(output_dir, version, output_dir / "index.toon")
    generate_docs(output_dir, output_dir.parent / "docs", version)

    # Update snapshot to reflect current state
    save_snapshot(new_snap, snap_path)
    return count


def delete(
    version: str,
    repo_root: Path,
    output_dir: Path,
    state_dir: Path,
    files: list[str] | None = None,
) -> int:
    """Delete knowledge JSON files for source files that no longer exist.

    Compares the current file list against the saved snapshot to identify
    source files that have been removed, then deletes the corresponding JSON.

    Returns:
        Number of JSON files deleted.
    """
    sources = scan_sources(version, repo_root, files)
    file_infos = classify_sources(sources, version, repo_root)

    snap_path = _snapshot_path(state_dir, version)
    old_snap = load_snapshot(snap_path)
    new_snap = make_snapshot(file_infos, repo_root, version)

    _added, _modified, deleted_keys = diff_snapshot(old_snap, new_snap)

    count = 0
    for key in deleted_keys:
        entry = old_snap["files"].get(key, {})
        out_rel = entry.get("output_path", "")
        if out_rel:
            json_path = output_dir / out_rel
            if json_path.exists():
                json_path.unlink()
                count += 1

    generate_index(output_dir, version, output_dir / "index.toon")
    generate_docs(output_dir, output_dir.parent / "docs", version)

    # Update snapshot
    save_snapshot(new_snap, snap_path)
    return count


def verify(
    version: str,
    repo_root: Path,
    output_dir: Path,
    files: list[str] | None = None,
) -> bool:
    """Verify that knowledge JSON files match their source documents.

    Runs per-file checks (A, B, C, D) for each source file and the
    corresponding docs MD, and global coverage checks (F, H) when
    verifying all files (files is None).

    Returns:
        True if all files pass verification, False if any issues found.
    """
    sources = scan_sources(version, repo_root, files)
    file_infos = classify_sources(sources, version, repo_root)

    docs_dir = output_dir.parent / "docs"
    all_ok = True

    # Build global RST label map once for Check C source-driven link verification
    from scripts.create.scan import _source_roots
    label_map: dict = {}
    for src_root in _source_roots(version, repo_root):
        if src_root.exists():
            label_map.update(build_label_map(src_root))

    for fi in file_infos:
        # B3: use repo-relative source path in FAIL lines
        source_rel = str(fi.source_path.relative_to(repo_root))
        json_path = output_dir / fi.output_path

        # Per-file JSON checks (A, B, C, D)
        if not json_path.exists():
            print(f"FAIL {source_rel}: JSON output missing: {json_path}", file=sys.stderr)
            all_ok = False
            continue

        for issue in verify_file(fi.source_path, json_path, fi.format, knowledge_dir=output_dir):
            print(f"FAIL {source_rel}: {issue}", file=sys.stderr)
            all_ok = False

        json_data = json.loads(json_path.read_text(encoding="utf-8"))

        # Check C (new): source-driven link verification
        if not json_data.get("no_knowledge_content"):
            source_text = fi.source_path.read_text(encoding="utf-8", errors="replace")
            for issue in check_source_links(
                source_text, fi.format, json_data, label_map, source_path=fi.source_path
            ):
                print(f"FAIL {source_rel}: [Check C] {issue}", file=sys.stderr)
                all_ok = False

        # Per-file docs MD checks (A, B, C, D)
        # Skip docs MD content checks for no_knowledge_content files: their
        # docs MD is a stub title header — toctree paths would inflate token count.
        if not json_data.get("no_knowledge_content"):
            docs_md_path = docs_dir / Path(fi.output_path).with_suffix(".md")

            if not docs_md_path.exists():
                print(f"FAIL {source_rel}: docs MD missing: {docs_md_path}", file=sys.stderr)
                all_ok = False
            else:
                for issue in verify_docs_md(fi.source_path, docs_md_path, fi.format):
                    print(f"FAIL {source_rel}: [docs MD] {issue}", file=sys.stderr)
                    all_ok = False

                # Check E: JSON ↔ docs MD consistency
                docs_md_text = docs_md_path.read_text(encoding="utf-8")
                for issue in check_json_docs_md_consistency(json_data, docs_md_text):
                    print(f"FAIL {source_rel}: [JSON↔MD] {issue}", file=sys.stderr)
                    all_ok = False

    # Coverage checks (F, H) — only when verifying all files
    if files is None:
        index_path = output_dir / "index.toon"
        for issue in check_index_coverage(output_dir, index_path):
            print(f"FAIL index.toon: {issue}", file=sys.stderr)
            all_ok = False

        for issue in check_docs_coverage(output_dir, docs_dir):
            print(f"FAIL docs: {issue}", file=sys.stderr)
            all_ok = False

        for issue in check_hints_file_consistency(output_dir, docs_dir, hints_path(repo_root, version)):
            print(f"FAIL hints: {issue}", file=sys.stderr)
            all_ok = False

    return all_ok


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="RBKC — Rule-Based Knowledge Creator")
    parser.add_argument("command", choices=["create", "update", "delete", "verify"])
    parser.add_argument("version", help="Nablarch version (e.g. 6, 5, 1.4)")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).parents[3])
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--state-dir", type=Path)
    args = parser.parse_args()

    repo_root = args.repo_root
    version = args.version

    # Default output/state dirs
    skill_dir = repo_root / f".claude/skills/nabledge-{version}"
    output_dir = args.output_dir or skill_dir / "knowledge"
    state_dir = args.state_dir or repo_root / ".state"

    if args.command == "create":
        n = create(version, repo_root, output_dir, state_dir)
        print(f"Created {n} knowledge files")
    elif args.command == "update":
        n = update(version, repo_root, output_dir, state_dir)
        print(f"Updated {n} knowledge files")
    elif args.command == "delete":
        n = delete(version, repo_root, output_dir, state_dir)
        print(f"Deleted {n} knowledge files")
    elif args.command == "verify":
        ok = verify(version, repo_root, output_dir)
        if not ok:
            sys.exit(1)
        print("All files verified OK")


if __name__ == "__main__":
    main()
