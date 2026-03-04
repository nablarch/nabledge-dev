"""Source change tracker for --regen option.

Records SHA256 hashes of source files after generation.
Detects changed files by comparing current hashes with recorded ones.
"""
import os
import hashlib
from .common import load_json, write_json

HASH_FILE = "source_hashes.json"


def _compute_hash(filepath: str) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def save_hashes(ctx):
    """Save current source file hashes. Call after Phase B completes."""
    classified = load_json(ctx.classified_list_path)
    hashes = {}
    for fi in classified["files"]:
        src = f"{ctx.repo}/{fi['source_path']}"
        if os.path.exists(src):
            hashes[fi["id"]] = {
                "source_path": fi["source_path"],
                "hash": _compute_hash(src)
            }
    write_json(f"{ctx.log_dir}/{HASH_FILE}", hashes)
    print(f"   💾 ハッシュ保存: {len(hashes)} ファイル")


def detect_changed(ctx) -> list:
    """Compare current source hashes with saved ones.

    Returns:
        list of changed file IDs, or None if no previous hashes exist.
    """
    hash_path = f"{ctx.log_dir}/{HASH_FILE}"
    if not os.path.exists(hash_path):
        print("   ⚠️ 前回のハッシュファイルなし。全ファイル再生成対象になります")
        return None

    old_hashes = load_json(hash_path)
    classified = load_json(ctx.classified_list_path)
    changed = []

    for fi in classified["files"]:
        file_id = fi["id"]
        src = f"{ctx.repo}/{fi['source_path']}"
        if not os.path.exists(src):
            continue
        current_hash = _compute_hash(src)
        old_entry = old_hashes.get(file_id)
        if old_entry is None or old_entry["hash"] != current_hash:
            changed.append(file_id)

    return changed


def detect_and_clean_changed(ctx, yes=False):
    """Detect source changes and clean artifacts for changed files."""
    changed = detect_changed(ctx)

    if changed is None:
        return
    if not changed:
        print("   ✨ ソース変更なし")
        return

    print(f"\n   🔄 ソース変更検知: {len(changed)} ファイル")
    for fid in changed[:10]:
        print(f"     - {fid}")
    if len(changed) > 10:
        print(f"     ... 他 {len(changed) - 10} ファイル")

    from .cleaner import clean_phase_artifacts
    clean_phase_artifacts(ctx, "BD", target_ids=changed, yes=yes)
