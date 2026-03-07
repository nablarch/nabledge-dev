"""Phase-specific artifact cleaner.

Removes intermediate artifacts for specified phases,
optionally filtered by target file IDs.
"""
import os
import glob
import shutil
from common import load_json


def clean_phase_artifacts(ctx, phases: str, target_ids: list = None, yes: bool = False):
    """Remove intermediate artifacts for specified phases.

    Args:
        ctx: Context object with path properties
        phases: Phase letters to clean (e.g. "D", "BD")
        target_ids: File IDs to clean (None = all files)
        yes: Skip confirmation prompt if True
    """
    targets = []

    if "B" in phases:
        targets.extend(_list_phase_b_artifacts(ctx, target_ids))
    if "D" in phases:
        targets.extend(_list_phase_d_artifacts(ctx, target_ids))

    if not targets:
        print("   削除対象なし")
        return

    print(f"\n   ⚠️ 以下の {len(targets)} ファイルを削除します:")
    for t in targets[:10]:
        print(f"     - {os.path.relpath(t, ctx.repo)}")
    if len(targets) > 10:
        print(f"     ... 他 {len(targets) - 10} ファイル")

    if not yes:
        answer = input("\n   続行しますか？ [y/N]: ")
        if answer.lower() != "y":
            print("   中止しました")
            return

    for t in targets:
        if os.path.isfile(t):
            os.remove(t)
        elif os.path.isdir(t):
            shutil.rmtree(t)

    print(f"   ✅ {len(targets)} ファイル削除完了")


def _list_phase_b_artifacts(ctx, target_ids):
    """List Phase B artifacts (knowledge JSON + trace).

    When target_ids is None, uses classified.json to find all output files.
    When target_ids is specified, uses glob to find matching files.
    """
    paths = []
    if target_ids:
        for file_id in target_ids:
            pattern = f"{ctx.knowledge_dir}/**/{file_id}.json"
            paths.extend(glob.glob(pattern, recursive=True))
            trace = f"{ctx.trace_dir}/{file_id}.json"
            if os.path.exists(trace):
                paths.append(trace)
    else:
        if os.path.exists(ctx.classified_list_path):
            classified = load_json(ctx.classified_list_path)
            for f in classified["files"]:
                p = f"{ctx.knowledge_dir}/{f['output_path']}"
                if os.path.exists(p):
                    paths.append(p)
        if os.path.isdir(ctx.trace_dir):
            paths.append(ctx.trace_dir)
    return paths


def _list_phase_d_artifacts(ctx, target_ids):
    """List Phase D artifacts (findings JSON).

    When target_ids is None, returns the findings directory itself.
    When target_ids is specified, returns individual finding files.
    """
    paths = []
    if target_ids:
        for file_id in target_ids:
            p = f"{ctx.findings_dir}/{file_id}.json"
            if os.path.exists(p):
                paths.append(p)
    else:
        if os.path.isdir(ctx.findings_dir):
            paths.append(ctx.findings_dir)
    return paths
