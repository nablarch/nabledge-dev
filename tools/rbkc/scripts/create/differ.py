"""Snapshot-based differ for RBKC.

Tracks SHA-256 hashes of source files to detect changes between runs,
enabling incremental updates.

Snapshot format:
    {
        "version": "6",
        "files": {
            "relative/path/to/source.rst": {
                "sha256": "abc123...",
                "output_path": "component/libraries/libraries-universal_dao.json"
            }
        }
    }

Public API:
    compute_sha256(path: Path) -> str
    make_snapshot(file_infos, repo_root, version) -> dict
    diff_snapshot(old, new) -> tuple[list, list, list]   # added, modified, deleted
    save_snapshot(data, path)
    load_snapshot(path) -> dict
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.create.classify import FileInfo


def compute_sha256(path: Path) -> str:
    """Return hex SHA-256 of the file at *path*."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def make_snapshot(
    file_infos: list[FileInfo],
    repo_root: Path,
    version: str,
) -> dict:
    """Build a snapshot dict from a list of :class:`FileInfo` objects.

    Source paths are stored relative to *repo_root*.
    """
    files = {}
    for fi in file_infos:
        rel = str(fi.source_path.relative_to(repo_root)).replace("\\", "/")
        files[rel] = {
            "sha256": compute_sha256(fi.source_path),
            "output_path": fi.output_path,
        }
    return {"version": version, "files": files}


def diff_snapshot(
    old: dict,
    new: dict,
) -> tuple[list[str], list[str], list[str]]:
    """Compare old and new snapshots.

    Returns:
        (added, modified, deleted) — each is a list of source-relative paths.
    """
    old_files = old.get("files", {})
    new_files = new.get("files", {})

    added = [k for k in new_files if k not in old_files]
    modified = [
        k for k in new_files
        if k in old_files and new_files[k]["sha256"] != old_files[k]["sha256"]
    ]
    deleted = [k for k in old_files if k not in new_files]

    return added, modified, deleted


def save_snapshot(data: dict, path: Path) -> None:
    """Write snapshot to *path*, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_snapshot(path: Path) -> dict:
    """Load snapshot from *path*.  Returns empty snapshot if file not found."""
    if not path.exists():
        return {"files": {}}
    return json.loads(path.read_text(encoding="utf-8"))
