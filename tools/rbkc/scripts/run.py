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
from scripts.create.hints import build_hints_index, lookup_hints as _lookup_hints_kc
from scripts.create.index import generate_index
from scripts.create.resolver import collect_asset_refs, copy_assets
from scripts.create.scan import scan_sources
from scripts.common.labels import build_label_map
from scripts.verify.verify import (
    verify_file,
    verify_docs_md,
    check_index_coverage,
    check_docs_coverage,
    check_source_links,
    check_json_docs_md_consistency,
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


def load_existing_hints(output_dir: Path) -> dict[str, dict[str, list[str]]]:
    """Load hints from existing RBKC-format knowledge JSON files.

    Reads all JSON files under *output_dir* that use RBKC format (sections as
    a list of dicts). KC-format files (sections as a dict) are skipped.

    Returns:
        {file_id: {section_title: hints}} — empty dict if directory is absent
        or contains no RBKC-format files.
    """
    if not output_dir.exists():
        return {}

    result: dict[str, dict[str, list[str]]] = {}
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

        section_hints: dict[str, list[str]] = {}
        for sec in sections:
            if not isinstance(sec, dict):
                continue
            title = sec.get("title", "")
            hints = sec.get("hints", [])
            if isinstance(hints, list):
                section_hints[title] = hints

        if file_id:
            result[file_id] = section_hints

    return result


def lookup_hints_with_fallback(
    existing_hints: dict[str, dict[str, list[str]]],
    kc_hints_idx: dict[str, dict[str, list[str]]],
    file_id: str,
    section_title: str,
) -> list[str]:
    """Return hints for a section, preferring existing RBKC hints over KC index.

    Args:
        existing_hints: From load_existing_hints() — hints from prior RBKC run.
        kc_hints_idx: From _hints_index() — hints derived from KC cache.
        file_id: Knowledge file identifier.
        section_title: Section title to look up.

    Returns:
        List of hints. Prefers existing_hints if the file_id is present there.
        Falls back to kc_hints_idx otherwise.
    """
    if file_id in existing_hints:
        return existing_hints[file_id].get(section_title, [])
    return _lookup_hints_kc(kc_hints_idx, file_id, section_title)


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
) -> None:
    """Convert one source file and write its knowledge JSON to *output_dir*.

    Args:
        fi: FileInfo for the source file.
        output_dir: Output directory for knowledge JSON files.
        hints_idx: KC cache hints index from _hints_index().
        existing_hints: Existing RBKC hints from load_existing_hints().
                        When provided, hints are looked up with carry-over
                        semantics (existing_hints preferred over hints_idx).
    """
    convert = _converter_for(fi.format, fi.source_path.name)

    if fi.format in ("rst", "md"):
        result = convert(fi.source_path.read_text(encoding="utf-8", errors="replace"), fi.file_id)
    else:
        result = convert(fi.source_path, fi.file_id)

    sections = []
    for idx, sec in enumerate(result.sections, start=1):
        sid = f"s{idx}"
        if existing_hints is not None:
            hints = lookup_hints_with_fallback(existing_hints, hints_idx, fi.file_id, sec.title)
        else:
            hints = _lookup_hints_kc(hints_idx, fi.file_id, sec.title)
        sections.append({
            "id": sid,
            "title": sec.title,
            "content": sec.content,
            "hints": hints,
        })

    data = {
        "id": fi.file_id,
        "title": result.title,
        "no_knowledge_content": result.no_knowledge_content,
        "sections": sections,
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
    hints_idx = _hints_index(repo_root, version)

    all_asset_refs = []
    for fi in file_infos:
        _convert_and_write(fi, output_dir, hints_idx, existing_hints)
        if fi.format == "rst":
            all_asset_refs.extend(collect_asset_refs(fi.source_path, fi.file_id))

    copy_assets(all_asset_refs, output_dir)
    generate_index(output_dir, version, index_path)
    generate_docs(output_dir, docs_dir)

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
    hints_idx = _hints_index(repo_root, version)
    # Load existing hints before reconverting so carry-over is preserved for
    # files whose source changed (same as create() semantics).
    existing_hints = load_existing_hints(output_dir)

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
            _convert_and_write(fi, output_dir, hints_idx, existing_hints)
            if fi.format == "rst":
                changed_asset_refs.extend(collect_asset_refs(fi.source_path, fi.file_id))
            count += 1

    copy_assets(changed_asset_refs, output_dir)
    generate_index(output_dir, version, output_dir / "index.toon")
    generate_docs(output_dir, output_dir.parent / "docs")

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
    generate_docs(output_dir, output_dir.parent / "docs")

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
        for issue in verify_file(fi.source_path, json_path, fi.format, knowledge_dir=output_dir):
            print(f"FAIL {source_rel}: {issue}", file=sys.stderr)
            all_ok = False

        json_data = json.loads(json_path.read_text(encoding="utf-8")) if json_path.exists() else {}

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
            for issue in verify_docs_md(fi.source_path, docs_md_path, fi.format):
                print(f"FAIL {source_rel}: [docs MD] {issue}", file=sys.stderr)
                all_ok = False

            # Check E: JSON ↔ docs MD consistency
            if docs_md_path.exists():
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
