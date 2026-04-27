"""RBKC CLI operations: create, update, delete, verify.

Orchestrates the full pipeline:
    scan → classify → convert → write JSON → save snapshot

Knowledge JSON schema (content only; hints are out of RBKC scope):
    {
        "id": "file-id",
        "title": "Document Title",
        "content": "Top-level preamble body",
        "no_knowledge_content": false,
        "sections": [
            {
                "id": "s1",
                "title": "Section Title",
                "content": "Markdown content"
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
from scripts.create.index import generate_index
from scripts.create.resolver import collect_asset_refs, copy_assets
from scripts.create.scan import scan_sources
from scripts.common.labels import build_label_doc_map, build_label_map  # noqa: F401
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


# ---------------------------------------------------------------------------
# JSON writer
# ---------------------------------------------------------------------------

def _convert_and_write(
    fi: FileInfo,
    output_dir: Path,
    label_map: dict | None = None,
    doc_map: dict | None = None,
) -> None:
    """Convert one source file and write its knowledge JSON to *output_dir*.

    Args:
        fi: FileInfo for the source file.
        output_dir: Output directory for knowledge JSON files.
        label_map: RST label→LabelTarget map (legacy bare-str values still
            accepted for backward compat).
        doc_map: rst_relpath→LabelTarget map for :doc: resolution.
    """
    convert = _converter_for(fi.format, fi.source_path.name)

    if fi.format == "rst":
        result = convert(
            fi.source_path.read_text(encoding="utf-8", errors="replace"),
            fi.file_id,
            source_path=fi.source_path,
            label_map=label_map,
            doc_map=doc_map,
        )
    elif fi.format == "md":
        result = convert(
            fi.source_path.read_text(encoding="utf-8", errors="replace"),
            fi.file_id,
            source_path=fi.source_path,
            doc_map=doc_map,
        )
    else:
        # xlsx: sheet_name is set by classify; pass it through.
        result = convert(fi.source_path, fi.file_id, sheet_name=fi.sheet_name)

    sections = []
    for idx, sec in enumerate(result.sections, start=1):
        sid = f"s{idx}"
        section_out = {
            "id": sid,
            "title": sec.title,
            "content": sec.content,
        }
        # Phase 22-B-16a: emit heading depth for RST/MD (not xlsx — xlsx
        # sections are Excel rows, not heading-nested).  docs.py uses
        # `level` to emit `##`/`###`/`####`; verify QO1 uses it for
        # JSON↔docs-MD heading-level alignment.
        if fi.format in ("rst", "md"):
            section_out["level"] = getattr(sec, "level", 2)
        sections.append(section_out)

    data = {
        "id": fi.file_id,
        "title": result.title,
        "content": getattr(result, "content", ""),
        "no_knowledge_content": result.no_knowledge_content,
        "sections": sections,
    }
    # Phase 22-B: xlsx results carry sheet_type + (for P1) the reconstructed
    # column/row matrix.  sheet_type flows through to JSON (verify reads it
    # for QO2 P1 一方向 containment).  Table data is used by docs.py only;
    # verify does not need it, but serialising it keeps docs-MD generation
    # idempotent w.r.t. the JSON file alone.
    meta = getattr(result, "meta", None)
    if meta:
        if "sheet_type" in meta:
            data["sheet_type"] = meta["sheet_type"]
        if meta.get("sheet_type") == "P1":
            data["columns"] = meta.get("columns", [])
            data["data_rows"] = meta.get("data_rows", [])

    out_path = output_dir / fi.output_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # Phase 22-B-16b step 2b F1: surface dangling-link WARNINGs so spec
    # §3-2-2 "silent skip 禁止" is honoured across both create and verify.
    for w in getattr(result, "warnings", []) or []:
        print(f"WARN {fi.source_path}: {w}", file=sys.stderr)


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

    # Phase 22-B-16b: single call replaces per-source-root walks, and
    # also returns doc_map for :doc: resolution.
    label_map, doc_map = build_label_doc_map(version, repo_root)

    all_asset_refs = []
    for fi in file_infos:
        _convert_and_write(fi, output_dir, label_map, doc_map)
        if fi.format == "rst":
            all_asset_refs.extend(collect_asset_refs(fi.source_path, fi.file_id))

    copy_assets(all_asset_refs, output_dir)
    generate_index(file_infos, output_dir, version, index_path)
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

    # Phase 22-B-16b: see create().
    label_map, doc_map = build_label_doc_map(version, repo_root)

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
            _convert_and_write(fi, output_dir, label_map, doc_map)
            if fi.format == "rst":
                changed_asset_refs.extend(collect_asset_refs(fi.source_path, fi.file_id))
            count += 1

    copy_assets(changed_asset_refs, output_dir)
    generate_index(file_infos, output_dir, version, output_dir / "index.toon")
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

    generate_index(file_infos, output_dir, version, output_dir / "index.toon")
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

    # Phase 22-B-16b: single call for QL1 link verification.  Both maps
    # are threaded through to verify_file so the source-side AST
    # normalisation emits the same MD-link strings as the create side.
    label_map, doc_map = build_label_doc_map(version, repo_root)

    for fi in file_infos:
        # B3: use repo-relative source path in FAIL lines
        source_rel = str(fi.source_path.relative_to(repo_root))
        json_path = output_dir / fi.output_path

        # Per-file JSON checks (A, B, C, D)
        if not json_path.exists():
            print(f"FAIL {source_rel}: JSON output missing: {json_path}", file=sys.stderr)
            all_ok = False
            continue

        for issue in verify_file(fi.source_path, json_path, fi.format, knowledge_dir=output_dir, label_map=label_map, sheet_name=fi.sheet_name, doc_map=doc_map, file_id=fi.file_id):
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
                for issue in check_json_docs_md_consistency(
                    json_data, docs_md_text,
                    docs_md_path=docs_md_path, knowledge_dir=output_dir,
                ):
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
