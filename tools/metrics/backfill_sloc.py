#!/usr/bin/env python3
"""
Backfill SLOC history in sloc-snapshot.json from git history.

Usage:
    python tools/metrics/backfill_sloc.py [--dry-run]

For each complete ISO week since the first commit, checks out the tree
at end-of-week (Sunday) and counts SLOC. Writes history into
tools/metrics/sloc-snapshot.json so that collect.py can render trend charts.
"""

import fnmatch
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone


# File patterns per category (same as collect.py)
PATTERNS = {
    "nabledge_scripts": [
        ".claude/skills/nabledge-6/scripts/**/*.sh",
        ".claude/skills/nabledge-5/scripts/**/*.sh",
        "tools/setup/setup-*.sh",
    ],
    "nabledge_prompts": [
        ".claude/skills/nabledge-6/SKILL.md",
        ".claude/skills/nabledge-6/workflows/**/*.md",
        ".claude/skills/nabledge-5/SKILL.md",
        ".claude/skills/nabledge-5/workflows/**/*.md",
        ".claude/commands/n6.md",
        ".claude/commands/n5.md",
    ],
    "kc_prod": [
        "tools/knowledge-creator/scripts/**/*.py",
        "tools/knowledge-creator/scripts/**/*.sh",
    ],
    "kc_test": [
        "tools/knowledge-creator/tests/**/*.py",
    ],
    "kc_prompts": [
        "tools/knowledge-creator/**/*.md",
    ],
}

KC_PROMPT_EXCLUDE = ["/reports/", "README.md", "readme.md"]


def run(cmd: list[str], repo_root: str) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_root)
    return result.stdout


def get_commit_at(repo_root: str, date_str: str) -> str | None:
    """Return the last commit on main before end of date_str (YYYY-MM-DD)."""
    before = f"{date_str} 23:59:59"
    # Try origin/main first, fall back to main, then HEAD
    for ref in ["origin/main", "main", "HEAD"]:
        out = run(["git", "log", "--format=%H", f"--before={before}", "-1", ref], repo_root)
        h = out.strip()
        if h:
            return h
    return None


def list_files_at(repo_root: str, commit: str) -> list[str]:
    """List all tracked files at a given commit."""
    out = run(["git", "ls-tree", "-r", "--name-only", commit], repo_root)
    return [line.strip() for line in out.splitlines() if line.strip()]


def match_patterns(filepath: str, patterns: list[str]) -> bool:
    """Match filepath against glob-style patterns, supporting ** for any depth."""
    for pat in patterns:
        # Expand ** by trying both direct match and nested match
        expanded = [pat]
        if "**/" in pat:
            # Also try without the **/ (matches files directly in parent dir)
            expanded.append(pat.replace("**/", ""))
        for p in expanded:
            if fnmatch.fnmatch(filepath, p):
                return True
    return False


def get_file_content(repo_root: str, commit: str, filepath: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit}:{filepath}"],
        capture_output=True, text=True, errors="replace", cwd=repo_root
    )
    return result.stdout if result.returncode == 0 else ""


def count_sloc(content: str, is_prompt: bool) -> int:
    count = 0
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if not is_prompt and stripped.startswith("#"):
            continue
        count += 1
    return count


def collect_sloc_at(repo_root: str, commit: str) -> dict:
    all_files = list_files_at(repo_root, commit)

    def sum_for(category: str, is_prompt: bool) -> int:
        patterns = PATTERNS[category]
        total = 0
        for f in all_files:
            if not match_patterns(f, patterns):
                continue
            if "__pycache__" in f:
                continue
            if category == "kc_prompts":
                if any(ex in f for ex in KC_PROMPT_EXCLUDE):
                    continue
            content = get_file_content(repo_root, commit, f)
            total += count_sloc(content, is_prompt=is_prompt)
        return total

    ns = sum_for("nabledge_scripts", False)
    np_ = sum_for("nabledge_prompts", True)
    kp = sum_for("kc_prod", False)
    kt = sum_for("kc_test", False)
    kpr = sum_for("kc_prompts", True)

    return {
        "nabledge_scripts": ns,
        "nabledge_prompts": np_,
        "kc_prod": kp,
        "kc_test": kt,
        "kc_prompts": kpr,
        "total": ns + np_ + kp + kt + kpr,
    }


def iso_week_monday(dt: datetime) -> datetime:
    day = dt.date()
    monday = day - timedelta(days=day.weekday())
    return datetime(monday.year, monday.month, monday.day, tzinfo=timezone.utc)


def weeks_since(first_commit_date: datetime) -> list[datetime]:
    """Return list of Mondays for all complete ISO weeks from first_commit_date to last week."""
    now = datetime.now(tz=timezone.utc)
    current_monday = iso_week_monday(now)
    start_monday = iso_week_monday(first_commit_date)
    weeks = []
    monday = start_monday
    while monday < current_monday:
        weeks.append(monday)
        monday += timedelta(weeks=1)
    return weeks


def get_first_commit_date(repo_root: str) -> datetime:
    # Get all commit dates from origin/main and take the oldest
    for ref in ["origin/main", "main"]:
        out = run(["git", "log", ref, "--format=%aI"], repo_root)
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        if lines:
            oldest = lines[-1]  # git log is newest-first, so last = oldest
            return datetime.fromisoformat(oldest.replace("Z", "+00:00"))
    raise RuntimeError("Cannot determine first commit date")


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    snapshot_path = os.path.join(script_dir, "sloc-snapshot.json")

    # Get all complete ISO weeks from first commit
    first_date = get_first_commit_date(repo_root)
    weeks = weeks_since(first_date)
    print(f"[info] Backfilling {len(weeks)} weeks from {first_date.date()} to present", file=sys.stderr)

    history = []
    for monday in weeks:
        sunday = monday + timedelta(days=6)
        date_str = sunday.strftime("%Y-%m-%d")
        commit = get_commit_at(repo_root, date_str)
        if not commit:
            print(f"[skip] {date_str}: no commit found", file=sys.stderr)
            continue

        print(f"[info] {monday.strftime('%Y-%m-%d')} (week ending {date_str}): {commit[:8]}...", file=sys.stderr)
        entry = collect_sloc_at(repo_root, commit)
        entry["date"] = monday.strftime("%Y-%m-%d")
        history.append(entry)
        print(f"       total={entry['total']:,}  ns={entry['nabledge_scripts']}  np={entry['nabledge_prompts']}  kp={entry['kc_prod']}  kt={entry['kc_test']}  kpr={entry['kc_prompts']}", file=sys.stderr)

    if dry_run:
        print("\n[dry-run] Would write history:")
        print(json.dumps(history, indent=2))
        return

    # Load existing snapshot, replace history
    try:
        with open(snapshot_path, encoding="utf-8") as f:
            snapshot = json.load(f)
    except (OSError, json.JSONDecodeError):
        snapshot = {}

    snapshot["history"] = history[-8:]  # keep last 8 for charts, but store all for reference
    # Store full history separately for reference
    snapshot["full_history"] = history

    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    print(f"\n[info] Written {len(history)} weeks of history to {snapshot_path}", file=sys.stderr)
    print("[info] Run 'python tools/metrics/collect.py' to regenerate docs/metrics.md", file=sys.stderr)


if __name__ == "__main__":
    main()
