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

from scripts.classify import FileInfo, classify_sources
from scripts.differ import diff_snapshot, load_snapshot, make_snapshot, save_snapshot
from scripts.docs import generate_docs
from scripts.hints import build_hints_index, lookup_hints
from scripts.index import generate_index
from scripts.resolver import collect_asset_refs, copy_assets
from scripts.scan import scan_sources
from scripts.verify import (
    verify_file,
    verify_docs_md,
    check_index_coverage,
    check_docs_coverage,
)


# ---------------------------------------------------------------------------
# Converter dispatch
# ---------------------------------------------------------------------------

def _converter_for(fmt: str, filename: str):
    """Return the appropriate convert() function for the given format/filename."""
    if fmt == "rst":
        from scripts.converters.rst import convert
        return convert
    if fmt == "md":
        from scripts.converters.md import convert
        return convert
    if fmt == "xlsx":
        if filename.endswith("-releasenote.xlsx") or "releasenote" in filename:
            from scripts.converters.xlsx_releasenote import convert
            return convert
        # Default xlsx: security table
        from scripts.converters.xlsx_security import convert
        return convert
    raise ValueError(f"Unknown format: {fmt!r}")


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

def _convert_and_write(fi: FileInfo, output_dir: Path, hints_idx: dict) -> None:
    """Convert one source file and write its knowledge JSON to *output_dir*."""
    convert = _converter_for(fi.format, fi.source_path.name)

    if fi.format in ("rst", "md"):
        result = convert(fi.source_path.read_text(encoding="utf-8", errors="replace"), fi.file_id)
    else:
        result = convert(fi.source_path, fi.file_id)

    sections = []
    for idx, sec in enumerate(result.sections, start=1):
        sid = f"s{idx}"
        hints = lookup_hints(hints_idx, fi.file_id, sec.title)
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
        _convert_and_write(fi, output_dir, hints_idx)
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
            _convert_and_write(fi, output_dir, hints_idx)
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

    for fi in file_infos:
        # B3: use repo-relative source path in FAIL lines
        source_rel = str(fi.source_path.relative_to(repo_root))
        json_path = output_dir / fi.output_path

        # Per-file JSON checks (A, B, C, D)
        for issue in verify_file(fi.source_path, json_path, fi.format, knowledge_dir=output_dir):
            print(f"FAIL {source_rel}: {issue}", file=sys.stderr)
            all_ok = False

        # Per-file docs MD checks (A, B, C, D)
        docs_md_path = docs_dir / Path(fi.output_path).with_suffix(".md")
        for issue in verify_docs_md(fi.source_path, docs_md_path, fi.format):
            print(f"FAIL {source_rel}: [docs MD] {issue}", file=sys.stderr)
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
