#!/usr/bin/env python3
"""
Collect development productivity metrics from GitHub and write docs/metrics.md.

Usage:
    python tools/metrics/collect.py [--token NABLEDGE_SYNC_TOKEN]

The script uses `gh api` (GitHub CLI) for API calls.
GH_TOKEN env var is used automatically by gh CLI in GitHub Actions.
"""

import argparse
import glob as glob_module
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def gh_api(path: str, token: str | None = None) -> dict | list | None:
    """Call gh api and return parsed JSON, or None on error."""
    env = os.environ.copy()
    if token:
        env["GH_TOKEN"] = token
    try:
        result = subprocess.run(
            ["gh", "api", path],
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"[warn] gh api {path} failed: {e.stderr.strip()}", file=sys.stderr)
        return None


def gh_api_paginated(path: str, token: str | None = None) -> list:
    """Call gh api with --paginate and return a flat list of items."""
    env = os.environ.copy()
    if token:
        env["GH_TOKEN"] = token
    try:
        result = subprocess.run(
            ["gh", "api", "--paginate", path],
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        # gh --paginate outputs multiple JSON arrays; join them
        items = []
        for chunk in result.stdout.strip().split("\n"):
            chunk = chunk.strip()
            if not chunk:
                continue
            parsed = json.loads(chunk)
            if isinstance(parsed, list):
                items.extend(parsed)
            else:
                items.append(parsed)
        return items
    except subprocess.CalledProcessError as e:
        print(f"[warn] gh api --paginate {path} failed: {e.stderr.strip()}", file=sys.stderr)
        return []


def iso_week_monday(dt: datetime) -> datetime:
    """Return the Monday of the ISO week containing dt (UTC, midnight)."""
    day = dt.date()
    monday = day - timedelta(days=day.weekday())
    return datetime(monday.year, monday.month, monday.day, tzinfo=timezone.utc)


def week_label(monday: datetime) -> str:
    """Format a Monday datetime as MM/DD."""
    return monday.strftime("%m/%d")


def parse_gh_datetime(s: str) -> datetime | None:
    """Parse GitHub API datetime string (ISO 8601) to UTC datetime."""
    if not s:
        return None
    try:
        # Python 3.11+ handles Z; for older versions replace manually
        s = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def y_axis_max(values: list[float], default_max: int = 5) -> int:
    """Compute Mermaid y-axis max: ceil(max * 1.2), minimum default_max."""
    if not values or max(values) == 0:
        return default_max
    return math.ceil(max(values) * 1.2)


def mermaid_xychart_bar(title: str, x_labels: list[str], y_label: str, values: list[float]) -> str:
    """Render a Mermaid xychart-beta bar chart."""
    ymax = y_axis_max(values)
    x_str = "[" + ", ".join(f'"{lbl}"' for lbl in x_labels) + "]"
    vals_str = "[" + ", ".join(str(int(v)) if v == int(v) else str(round(v, 1)) for v in values) + "]"
    return (
        "```mermaid\n"
        "xychart-beta\n"
        f'  title "{title}"\n'
        f"  x-axis {x_str}\n"
        f'  y-axis "{y_label}" 0 --> {ymax}\n'
        f"  bar {vals_str}\n"
        "```"
    )


def mermaid_xychart_line(title: str, x_labels: list[str], y_label: str, values: list[float]) -> str:
    """Render a Mermaid xychart-beta line chart."""
    ymax = y_axis_max(values)
    x_str = "[" + ", ".join(f'"{lbl}"' for lbl in x_labels) + "]"
    vals_str = "[" + ", ".join(str(int(v)) if v == int(v) else str(round(v, 1)) for v in values) + "]"
    return (
        "```mermaid\n"
        "xychart-beta\n"
        f'  title "{title}"\n'
        f"  x-axis {x_str}\n"
        f'  y-axis "{y_label}" 0 --> {ymax}\n'
        f"  line {vals_str}\n"
        "```"
    )


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------

def get_weeks_since_first_commit(repo_root: str) -> list[datetime]:
    """Return all complete ISO weeks from the first commit on main to last week."""
    # Use git log to find the oldest commit on origin/main (same as backfill_sloc.py)
    for ref in ["origin/main", "main"]:
        result = subprocess.run(
            ["git", "log", ref, "--format=%aI"],
            capture_output=True, text=True, cwd=repo_root,
        )
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        if lines:
            oldest_str = lines[-1].replace("Z", "+00:00")
            try:
                first_date = datetime.fromisoformat(oldest_str)
            except ValueError:
                continue
            now = datetime.now(tz=timezone.utc)
            current_monday = iso_week_monday(now)
            start_monday = iso_week_monday(first_date)
            weeks = []
            monday = start_monday
            while monday < current_monday:
                weeks.append(monday)
                monday += timedelta(weeks=1)
            return weeks
    # Fallback: last 8 weeks
    now = datetime.now(tz=timezone.utc)
    current_monday = iso_week_monday(now)
    return [current_monday - timedelta(weeks=i) for i in range(8, 0, -1)]


def collect_merged_prs(repo: str, since: datetime, token: str | None) -> list[dict]:
    """Fetch all closed PRs merged to main since `since`."""
    print(f"[info] Fetching merged PRs for {repo} since {since.date()}...", file=sys.stderr)
    since_str = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    path = f"repos/{repo}/pulls?state=closed&base=main&per_page=100&sort=updated&direction=desc"
    items = gh_api_paginated(path, token)
    merged = []
    for pr in items:
        merged_at = parse_gh_datetime(pr.get("merged_at"))
        if merged_at and merged_at >= since:
            merged.append(pr)
    return merged


def get_first_commit_date(repo: str, pr_number: int, token: str | None) -> datetime | None:
    """Get the date of the first commit in a PR."""
    path = f"repos/{repo}/pulls/{pr_number}/commits?per_page=100"
    commits = gh_api_paginated(path, token)
    if not commits:
        return None
    dates = []
    for c in commits:
        date_str = c.get("commit", {}).get("author", {}).get("date")
        dt = parse_gh_datetime(date_str)
        if dt:
            dates.append(dt)
    return min(dates) if dates else None


def collect_issues(repo: str, since: datetime, token: str | None) -> list[dict]:
    """Fetch all issues (not PRs) updated since `since`."""
    print(f"[info] Fetching issues for {repo} since {since.date()}...", file=sys.stderr)
    since_str = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    path = f"repos/{repo}/issues?state=all&per_page=100&sort=updated&direction=desc&since={since_str}"
    items = gh_api_paginated(path, token)
    # Filter out PRs (GitHub issues API returns both)
    return [i for i in items if "pull_request" not in i]


def collect_repo_stats(repo: str, token: str | None) -> dict:
    """Fetch stars, forks, watchers from repo info."""
    print(f"[info] Fetching repo stats for {repo}...", file=sys.stderr)
    data = gh_api(f"repos/{repo}", token)
    if not data:
        return {}
    return {
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "watchers": data.get("subscribers_count", 0),
    }


def collect_traffic_views(repo: str, token: str | None) -> dict:
    """Fetch page views traffic data."""
    print(f"[info] Fetching traffic views for {repo}...", file=sys.stderr)
    data = gh_api(f"repos/{repo}/traffic/views", token)
    return data or {}


def collect_traffic_clones(repo: str, token: str | None) -> dict:
    """Fetch git clones traffic data."""
    print(f"[info] Fetching traffic clones for {repo}...", file=sys.stderr)
    data = gh_api(f"repos/{repo}/traffic/clones", token)
    return data or {}


# ---------------------------------------------------------------------------
# Metric calculation
# ---------------------------------------------------------------------------

def compute_weekly_metrics(weeks: list[datetime], merged_prs: list[dict], issues: list[dict], repo: str, token: str | None) -> list[dict]:
    """
    For each week, compute:
      - deployment_frequency: merged PRs count
      - lead_time_hours: avg hours from first commit to merge
      - change_failure_rate: % of PRs with bug/fix label
      - mttr_hours: avg hours from bug issue open to close
      - issues_opened, issues_closed, prs_opened, prs_merged, contributors
    """
    results = []

    for monday in weeks:
        week_end = monday + timedelta(weeks=1)
        label = week_label(monday)

        # PRs merged this week
        week_prs = [
            pr for pr in merged_prs
            if (dt := parse_gh_datetime(pr.get("merged_at"))) and monday <= dt < week_end
        ]

        # Deployment frequency
        dep_freq = len(week_prs)

        # Lead time: avg hours from first commit to merge
        lead_times = []
        for pr in week_prs:
            merged_at = parse_gh_datetime(pr.get("merged_at"))
            pr_number = pr.get("number")
            first_commit = get_first_commit_date(repo, pr_number, token) if pr_number else None
            if first_commit and merged_at:
                hours = (merged_at - first_commit).total_seconds() / 3600
                lead_times.append(hours)
        avg_lead_time = sum(lead_times) / len(lead_times) if lead_times else 0.0

        # Change failure rate: PRs with bug or fix label
        def has_failure_label(pr: dict) -> bool:
            labels = [lbl.get("name", "").lower() for lbl in pr.get("labels", [])]
            return any(l in ("bug", "fix") for l in labels)

        failure_prs = [pr for pr in week_prs if has_failure_label(pr)]
        cfr = (len(failure_prs) / dep_freq * 100) if dep_freq > 0 else 0.0

        # MTTR: bug-labeled issues opened and closed this week
        bug_issues_closed = []
        for issue in issues:
            labels = [lbl.get("name", "").lower() for lbl in issue.get("labels", [])]
            if "bug" not in labels:
                continue
            closed_at = parse_gh_datetime(issue.get("closed_at"))
            created_at = parse_gh_datetime(issue.get("created_at"))
            if closed_at and monday <= closed_at < week_end and created_at:
                hours = (closed_at - created_at).total_seconds() / 3600
                bug_issues_closed.append(hours)
        avg_mttr = sum(bug_issues_closed) / len(bug_issues_closed) if bug_issues_closed else 0.0

        # Activity: issues opened/closed
        issues_opened = sum(
            1 for i in issues
            if (dt := parse_gh_datetime(i.get("created_at"))) and monday <= dt < week_end
        )
        issues_closed = sum(
            1 for i in issues
            if (dt := parse_gh_datetime(i.get("closed_at"))) and monday <= dt < week_end
        )

        # PRs opened this week (use created_at from merged_prs list as approximation;
        # fetch separately for accuracy)
        prs_opened = 0  # computed below via separate fetch if needed

        # Contributors: unique PR authors
        contributors = len({pr.get("user", {}).get("login") for pr in week_prs if pr.get("user")})

        results.append({
            "label": label,
            "monday": monday,
            "deployment_frequency": dep_freq,
            "lead_time_hours": round(avg_lead_time, 1),
            "change_failure_rate": round(cfr, 1),
            "mttr_hours": round(avg_mttr, 1),
            "issues_opened": issues_opened,
            "issues_closed": issues_closed,
            "prs_opened": prs_opened,
            "prs_merged": dep_freq,
            "contributors": contributors,
        })

    return results


def collect_prs_opened(repo: str, weeks: list[datetime], token: str | None) -> dict[str, int]:
    """Fetch all PRs created in the period and bucket by week."""
    since = weeks[0]
    print(f"[info] Fetching opened PRs for {repo} since {since.date()}...", file=sys.stderr)
    path = f"repos/{repo}/pulls?state=all&per_page=100&sort=created&direction=desc"
    items = gh_api_paginated(path, token)
    bucket: dict[str, int] = {}
    week_end = weeks[-1] + timedelta(weeks=1)
    for pr in items:
        created_at = parse_gh_datetime(pr.get("created_at"))
        if not created_at or created_at < since or created_at >= week_end:
            continue
        monday = iso_week_monday(created_at)
        label = week_label(monday)
        bucket[label] = bucket.get(label, 0) + 1
    return bucket


# ---------------------------------------------------------------------------
# SLOC collection
# ---------------------------------------------------------------------------

def count_sloc(filepath: str, is_prompt: bool = False) -> int:
    """Count significant lines in a file.

    Scripts (.py, .sh): exclude blank lines and comment lines (starting with #).
    Prompts (.md): exclude blank lines only.
    """
    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return 0
    count = 0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if not is_prompt and stripped.startswith("#"):
            continue
        count += 1
    return count


def _glob_files(repo_root: str, patterns: list[str]) -> list[str]:
    files = []
    for pattern in patterns:
        files.extend(glob_module.glob(os.path.join(repo_root, pattern), recursive=True))
    return sorted({f for f in files if os.path.isfile(f)})


def _sloc_by_ext(files: list[str], is_prompt: bool = False) -> dict[str, int]:
    by_ext: dict[str, int] = {}
    for f in files:
        ext = os.path.splitext(f)[1] or "(no ext)"
        by_ext[ext] = by_ext.get(ext, 0) + count_sloc(f, is_prompt=is_prompt)
    return by_ext


def collect_sloc(repo_root: str) -> dict:
    """Collect SLOC for all tracked categories."""

    # --- Nabledge scripts (v6 only; v5 is a copy) ---
    nabledge_script_files = _glob_files(repo_root, [
        ".claude/skills/nabledge-6/scripts/**/*.sh",
        "tools/setup/setup-*.sh",
    ])
    nabledge_scripts = _sloc_by_ext(nabledge_script_files, is_prompt=False)

    # --- Nabledge prompts (v6 only) ---
    nabledge_prompt_files = _glob_files(repo_root, [
        ".claude/skills/nabledge-6/SKILL.md",
        ".claude/skills/nabledge-6/workflows/**/*.md",
        ".claude/commands/n6.md",
    ])
    nabledge_prompts = sum(count_sloc(f, is_prompt=True) for f in nabledge_prompt_files)

    # --- KC scripts (production) ---
    kc_prod_files = [
        f for f in _glob_files(repo_root, ["tools/knowledge-creator/scripts/**/*.py",
                                             "tools/knowledge-creator/scripts/**/*.sh"])
        if "__pycache__" not in f
        and os.path.basename(f) != "__init__.py"
        and not os.path.basename(f).startswith("migrate_")
    ]
    kc_scripts_prod = _sloc_by_ext(kc_prod_files, is_prompt=False)

    # --- KC scripts (test) ---
    kc_test_files = [
        f for f in _glob_files(repo_root, ["tools/knowledge-creator/tests/**/*.py"])
        if "__pycache__" not in f
        and os.path.basename(f) != "__init__.py"
    ]
    kc_scripts_test = _sloc_by_ext(kc_test_files, is_prompt=False)

    # --- KC prompts (.md files, excluding reports/ and README.md) ---
    kc_md_files = [
        f for f in _glob_files(repo_root, ["tools/knowledge-creator/**/*.md"])
        if "/reports/" not in f and os.path.basename(f).upper() != "README.MD"
    ]
    kc_prompts = sum(count_sloc(f, is_prompt=True) for f in kc_md_files)

    return {
        "nabledge": {
            "scripts": nabledge_scripts,
            "prompts": nabledge_prompts,
        },
        "kc": {
            "scripts_prod": kc_scripts_prod,
            "scripts_test": kc_scripts_test,
            "prompts": kc_prompts,
        },
    }


def load_sloc_snapshot(snapshot_path: str) -> dict:
    try:
        with open(snapshot_path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def save_sloc_snapshot(snapshot_path: str, data: dict) -> None:
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def sloc_flat(s: dict, date: str) -> dict:
    """Flatten SLOC data to a single dict for history storage."""
    def t(d: dict | int) -> int:
        return sum(d.values()) if isinstance(d, dict) else (d or 0)
    ns = t(s["nabledge"]["scripts"])
    np_ = s["nabledge"]["prompts"]
    kp = t(s["kc"]["scripts_prod"])
    kt = t(s["kc"]["scripts_test"])
    kpr = s["kc"]["prompts"]
    return {"date": date, "nabledge_scripts": ns, "nabledge_prompts": np_,
            "kc_prod": kp, "kc_test": kt, "kc_prompts": kpr,
            "total": ns + np_ + kp + kt + kpr}


def _delta_str(current: int, previous: int) -> str:
    diff = current - previous
    if diff > 0:
        return f"+{diff:,}"
    if diff < 0:
        return f"{diff:,}"
    return "—"


def _pie_chart(title: str, slices: list[tuple[str, int]]) -> str:
    """Render a Mermaid pie chart. slices = [(label, value), ...]"""
    inner = "\n".join(f'  "{label}" : {value}' for label, value in slices if value > 0)
    return f"```mermaid\npie title \"{title}\"\n{inner}\n```"


def render_sloc_section(current: dict, previous: dict, history: list[dict]) -> list[str]:
    """Render SLOC charts (no tables)."""
    lines = []
    lines.append("## Code Size (SLOC)")
    lines.append("")
    lines.append("> Scripts: statement lines (blank and comment lines excluded) / Prompts: non-blank lines")
    lines.append("")

    def total(d: dict | int) -> int:
        return sum(d.values()) if isinstance(d, dict) else (d or 0)

    cur_ns = total(current["nabledge"]["scripts"])
    cur_np = current["nabledge"]["prompts"]
    cur_kp = total(current["kc"]["scripts_prod"])
    cur_kt = total(current["kc"]["scripts_test"])
    cur_kpr = current["kc"]["prompts"]

    # --- Total SLOC trend ---
    if len(history) >= 2:
        hist_labels = [h["date"][5:] for h in history]
        lines.append(mermaid_xychart_line("Total SLOC Trend (all categories)", hist_labels, "Lines", [h["total"] for h in history]))
        lines.append("")

    # --- Nabledge v6 ---
    lines.append("### Nabledge v6")
    lines.append("")
    lines.append(_pie_chart("Nabledge v6 SLOC (Scripts vs Prompts)", [
        ("Scripts (.sh)", cur_ns),
        ("Prompts (.md)", cur_np),
    ]))
    lines.append("")

    # --- Knowledge Creator ---
    lines.append("### Knowledge Creator")
    lines.append("")
    lines.append(_pie_chart("Knowledge Creator SLOC (Production / Test / Prompts)", [
        ("Production (.py)", cur_kp),
        ("Test (.py)", cur_kt),
        ("Prompts (.md)", cur_kpr),
    ]))
    lines.append("")

    # KC trend (prod vs test)
    if len(history) >= 2:
        hist_labels = [h["date"][5:] for h in history]
        kc_prod_hist = [h["kc_prod"] for h in history]
        kc_test_hist = [h["kc_test"] for h in history]
        ymax = y_axis_max(kc_prod_hist + kc_test_hist)
        x_str = "[" + ", ".join(f'"{l}"' for l in hist_labels) + "]"
        lines.append("```mermaid")
        lines.append("xychart-beta")
        lines.append('  title "KC Scripts Trend (upper=Production  lower=Test)"')
        lines.append(f"  x-axis {x_str}")
        lines.append(f'  y-axis "Lines" 0 --> {ymax}')
        lines.append(f"  line {kc_prod_hist}")
        lines.append(f"  line {kc_test_hist}")
        lines.append("```")
        lines.append("")

    return lines


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

DORA_BENCHMARKS = {
    "deployment_frequency": [
        # (threshold_per_week, level)  — threshold = minimum PRs/week for this level
        (7, "Elite"),   # ~once/day or more
        (1, "High"),    # once/week or more
        (0.25, "Medium"),  # once/month or more
    ],
    "lead_time_hours": [
        # threshold = maximum hours for this level
        (1, "Elite"),
        (168, "High"),     # 1 week
        (720, "Medium"),   # ~1 month
    ],
    "change_failure_rate": [
        # threshold = maximum % for this level
        (5, "Elite"),
        (10, "High"),
        (15, "Medium"),
    ],
    "mttr_hours": [
        # threshold = maximum hours for this level
        (1, "Elite"),
        (24, "High"),
        (168, "Medium"),   # 1 week
    ],
}

LEVEL_BADGE = {
    "Elite": "**Elite**",
    "High": "High",
    "Medium": "Medium",
    "Low": "Low",
    "N/A": "N/A",
}


def dora_level(metric: str, value: float, has_data: bool = True) -> str:
    """Return DORA performance level for a given metric value."""
    if not has_data:
        return "N/A"
    benchmarks = DORA_BENCHMARKS[metric]
    if metric == "deployment_frequency":
        if value == 0:
            return "Low"
        for threshold, level in benchmarks:
            if value >= threshold:
                return level
        return "Low"
    else:
        # Lower is better; 0 is valid (e.g., 0% CFR = Elite, 0h MTTR = no bugs = N/A)
        if metric == "mttr_hours" and value == 0:
            return "N/A"  # No bug issues closed — no data
        for threshold, level in benchmarks:
            if value <= threshold:
                return level
        return "Low"


LEVEL_SCORE = {"Elite": 4, "High": 3, "Medium": 2, "Low": 1, "N/A": 0}


def render_scorecard(weekly: list[dict]) -> str:
    """Render DORA scorecard: metric/level table + benchmark reference."""
    def latest_nonzero(vals: list[float]) -> float:
        for v in reversed(vals):
            if v > 0:
                return v
        return 0.0

    dep = latest_nonzero([w["deployment_frequency"] for w in weekly])
    lt = latest_nonzero([w["lead_time_hours"] for w in weekly])
    cfr = 0.0
    for w in reversed(weekly):
        if w["deployment_frequency"] > 0:
            cfr = w["change_failure_rate"]
            break
    mttr = latest_nonzero([w["mttr_hours"] for w in weekly])

    dep_lvl = dora_level("deployment_frequency", dep)
    lt_lvl = dora_level("lead_time_hours", lt)
    cfr_lvl = dora_level("change_failure_rate", cfr, has_data=dep > 0)
    mttr_lvl = dora_level("mttr_hours", mttr)

    rows = [
        ("Deployment Frequency", f"{dep:.0f} PRs/week" if dep > 0 else "—", dep_lvl),
        ("Lead Time for Changes", f"{lt:.1f}h" if lt > 0 else "—", lt_lvl),
        ("Change Failure Rate", f"{cfr:.0f}%" if dep > 0 else "—", cfr_lvl),
        ("MTTR", f"{mttr:.1f}h" if mttr > 0 else "—", mttr_lvl),
    ]

    lines = []
    # Score table
    lines += ["| Metric | Latest | Level |",
              "|--------|-------:|:-----:|"]
    for name, val, level in rows:
        lines.append(f"| {name} | {val} | {LEVEL_BADGE[level]} |")
    lines.append("")

    # Benchmark reference (small text via HTML)
    lines.append("<details><summary>Benchmark criteria</summary>")
    lines.append("")
    lines.append("- **Deployment Frequency** — Elite: ≥7/week · High: ≥1/week · Medium: ≥1/month · Low: <1/month")
    lines.append("- **Lead Time for Changes** — Elite: <1h · High: <1 week · Medium: <1 month · Low: ≥1 month")
    lines.append("- **Change Failure Rate** — Elite: ≤5% · High: ≤10% · Medium: ≤15% · Low: >15%")
    lines.append("- **MTTR** — Elite: <1h · High: <1 day · Medium: <1 week · Low: ≥1 week")
    lines.append("")
    lines.append("</details>")
    return "\n".join(lines)


def render_metrics_md(
    dev_repo: str,
    weekly: list[dict],
    nabledge_stats: dict | None,
    traffic_views: dict | None,
    traffic_clones: dict | None,
    today: str,
    sloc_current: dict | None = None,
    sloc_previous: dict | None = None,
    sloc_history: list[dict] | None = None,
) -> str:
    labels = [w["label"] for w in weekly]

    dep_freq_vals = [w["deployment_frequency"] for w in weekly]
    lead_time_vals = [w["lead_time_hours"] for w in weekly]
    cfr_vals = [w["change_failure_rate"] for w in weekly]
    mttr_vals = [w["mttr_hours"] for w in weekly]

    lines = []

    # Header
    lines.append("# Nabledge Dev Metrics")
    lines.append("")
    lines.append(f"> Last updated: {today} (auto-generated weekly — [view source](tools/metrics/collect.py))")
    lines.append("")

    # --- DORA Scorecard ---
    lines.append("## DORA Scorecard")
    lines.append("")
    lines.append(render_scorecard(weekly))
    lines.append("")

    # --- Development Productivity ---
    lines.append("## Development Productivity")
    lines.append("")

    lines.append(mermaid_xychart_bar("Deployment Frequency (PRs merged to main per week)", labels, "PRs / week", dep_freq_vals))
    lines.append("")
    lines.append(mermaid_xychart_line("Lead Time for Changes (avg hours: first commit to merge)", labels, "Hours", lead_time_vals))
    lines.append("")
    lines.append(mermaid_xychart_bar("Change Failure Rate (bug or fix labeled PRs / all merged PRs %)", labels, "% of PRs", cfr_vals))
    lines.append("")
    lines.append("> **Change Failure Rate**: bug/fix ラベル付き PR 数 ÷ mainへマージされた全 PR 数 × 100")
    lines.append("")
    lines.append(mermaid_xychart_line("Mean Time to Recovery (avg hours: bug issue opened to closed)", labels, "Hours", mttr_vals))
    lines.append("")
    lines.append("> **Mean Time to Recovery**: bug ラベル付き Issue の closed_at − created_at の平均（時間）")
    lines.append("")

    # --- Activity ---
    lines.append("## Activity")
    lines.append("")
    lines.append("> Issues/PRs の開閉ペース・コントリビューター数を週次で追跡します。")
    lines.append("> 開いた数と閉じた数のバランスが崩れていると、未解決の積み残しが増えているサインです。")
    lines.append("")

    x_str = "[" + ", ".join(f'"{l}"' for l in labels) + "]"

    lines.append(mermaid_xychart_bar("Issues Opened (count per week)", labels, "Count", [w["issues_opened"] for w in weekly]))
    lines.append("")
    lines.append(mermaid_xychart_bar("Issues Closed (count per week)", labels, "Count", [w["issues_closed"] for w in weekly]))
    lines.append("")
    lines.append(mermaid_xychart_bar("PRs Opened (count per week)", labels, "Count", [w["prs_opened"] for w in weekly]))
    lines.append("")
    lines.append(mermaid_xychart_bar("PRs Merged (count per week)", labels, "Count", [w["prs_merged"] for w in weekly]))
    lines.append("")
    lines.append(mermaid_xychart_bar("Active Contributors (unique PR authors per week)", labels, "Contributors", [w["contributors"] for w in weekly]))
    lines.append("")

    # --- SLOC ---
    if sloc_current:
        lines.extend(render_sloc_section(sloc_current, sloc_previous or {}, sloc_history or []))

    # --- Nabledge Adoption ---
    if nabledge_stats or traffic_views or traffic_clones:
        lines.append("## Nabledge Adoption (nablarch/nabledge)")
        lines.append("")

        # Page views chart
        if traffic_views and traffic_views.get("views"):
            views_data = traffic_views["views"]
            # Sort by timestamp
            views_data = sorted(views_data, key=lambda x: x.get("timestamp", ""))
            view_labels = [d["timestamp"][:10][5:] for d in views_data]  # MM-DD
            view_labels = [lbl.replace("-", "/") for lbl in view_labels]
            view_counts = [d.get("count", 0) for d in views_data]

            lines.append("### Page Views (last 14 days)")
            lines.append("")
            lines.append(mermaid_xychart_bar("Page Views", view_labels, "Views", view_counts))
            lines.append("")

        # Summary table
        total_views = traffic_views.get("count", 0) if traffic_views else 0
        unique_visitors = traffic_views.get("uniques", 0) if traffic_views else 0
        total_clones = traffic_clones.get("count", 0) if traffic_clones else 0
        stars = nabledge_stats.get("stars", 0) if nabledge_stats else 0
        forks = nabledge_stats.get("forks", 0) if nabledge_stats else 0
        watchers = nabledge_stats.get("watchers", 0) if nabledge_stats else 0

        lines.append("| Metric | Value |")
        lines.append("|--------|------:|")
        lines.append(f"| Page views (14 days) | {total_views} |")
        lines.append(f"| Unique visitors (14 days) | {unique_visitors} |")
        lines.append(f"| Git clones (14 days) | {total_clones} |")
        lines.append(f"| Stars | {stars} |")
        lines.append(f"| Forks | {forks} |")
        lines.append(f"| Watchers | {watchers} |")
        lines.append("")
    else:
        lines.append("## Nabledge Adoption (nablarch/nabledge)")
        lines.append("")
        lines.append("_Skipped: NABLEDGE_SYNC_TOKEN not available._")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Collect nabledge-dev metrics and write docs/metrics.md")
    parser.add_argument("--token", metavar="TOKEN", help="NABLEDGE_SYNC_TOKEN for nablarch/nabledge access")
    args = parser.parse_args()

    dev_repo = "nablarch/nabledge-dev"
    nabledge_repo = "nablarch/nabledge"

    # NABLEDGE_SYNC_TOKEN: prefer CLI arg, then env var
    nabledge_token = args.token or os.environ.get("NABLEDGE_SYNC_TOKEN")

    # Determine repo root early (needed for git log and SLOC)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))

    # All complete ISO weeks since first commit on main
    weeks = get_weeks_since_first_commit(repo_root)
    since = weeks[0]

    print(f"[info] Collecting metrics for {dev_repo}, weeks {week_label(weeks[0])} to {week_label(weeks[-1])} ({len(weeks)} weeks)", file=sys.stderr)

    # --- nabledge-dev data ---
    merged_prs = collect_merged_prs(dev_repo, since, token=None)
    issues = collect_issues(dev_repo, since, token=None)
    prs_opened_by_week = collect_prs_opened(dev_repo, weeks, token=None)

    print(f"[info] Computing weekly metrics ({len(merged_prs)} merged PRs, {len(issues)} issues)...", file=sys.stderr)
    weekly = compute_weekly_metrics(weeks, merged_prs, issues, dev_repo, token=None)

    # Patch prs_opened from separate fetch
    for w in weekly:
        w["prs_opened"] = prs_opened_by_week.get(w["label"], 0)

    # --- nablarch/nabledge data (optional) ---
    nabledge_stats = None
    traffic_views = None
    traffic_clones = None

    if nabledge_token:
        print(f"[info] NABLEDGE_SYNC_TOKEN available — collecting adoption metrics...", file=sys.stderr)
        nabledge_stats = collect_repo_stats(nabledge_repo, nabledge_token)
        traffic_views = collect_traffic_views(nabledge_repo, nabledge_token)
        traffic_clones = collect_traffic_clones(nabledge_repo, nabledge_token)
    else:
        print("[info] NABLEDGE_SYNC_TOKEN not set — skipping adoption metrics.", file=sys.stderr)

    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    snapshot_path = os.path.join(script_dir, "sloc-snapshot.json")
    output_path = os.path.join(repo_root, "docs", "metrics.md")

    # --- SLOC ---
    print("[info] Counting SLOC...", file=sys.stderr)
    sloc_current = collect_sloc(repo_root)
    snapshot = load_sloc_snapshot(snapshot_path)
    sloc_previous = {k: v for k, v in snapshot.items() if k != "history"}
    sloc_history = snapshot.get("history", [])
    sloc_history = (sloc_history + [sloc_flat(sloc_current, today)])[-8:]
    save_sloc_snapshot(snapshot_path, {**sloc_current, "history": sloc_history})

    print("[info] Rendering docs/metrics.md...", file=sys.stderr)
    content = render_metrics_md(
        dev_repo, weekly, nabledge_stats, traffic_views, traffic_clones, today,
        sloc_current=sloc_current, sloc_previous=sloc_previous, sloc_history=sloc_history,
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[info] Written to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
