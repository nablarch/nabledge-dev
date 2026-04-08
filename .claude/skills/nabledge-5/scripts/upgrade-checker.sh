#!/bin/bash
# upgrade-checker.sh - Rule-based Nablarch upgrade impact checker
#
# Scans release note JSON files between two Nablarch versions and checks
# whether the changes affect the target project.
#
# Rules implemented:
#   R1: Sections with "システムへの影響あり" in index[].hints
#   R2: Sections with "影響がある変更" in index[].title (supplement to R1)
#   R3: Warning/important blocks in section body (> **警告**: / > **重要**:)
#   R4: Table rows where the "影響" column value is "あり"
#   R5: FQCNs extracted from backticks (com.nablarch.*)
#   R6: Config keys extracted from backticks (nablarch.*)
#   R7: Artifact IDs extracted from table "修正バージョン"/"アーティファクトID" columns
#   R8: Project grep for R5/R6/R7 extracted items
#
# Usage:
#   upgrade-checker.sh --release-notes-dir DIR --project-dir DIR --from VERSION --to VERSION
#
# Example:
#   upgrade-checker.sh \
#     --release-notes-dir ~/nabledge-dev/tools/knowledge-creator/.cache/v5/knowledge/releases/releases \
#     --project-dir ~/my-nablarch-project \
#     --from 5u13 \
#     --to 5u18

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
RELEASE_NOTES_DIR=""
PROJECT_DIR=""
FROM_VERSION=""
TO_VERSION=""

usage() {
  cat >&2 <<EOF
Usage: $0 --release-notes-dir DIR --project-dir DIR --from VERSION --to VERSION

Options:
  --release-notes-dir DIR  Directory containing release note JSON files
  --project-dir DIR        Root directory of the target Nablarch project
  --from VERSION           Source version (e.g. 5u13)
  --to VERSION             Target version (e.g. 5u18)

Examples:
  $0 --release-notes-dir /path/to/releases --project-dir /path/to/project --from 5u13 --to 5u18
  $0 --release-notes-dir /path/to/releases --project-dir /path/to/project --from 6 --to 6u3
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --release-notes-dir) RELEASE_NOTES_DIR="$2"; shift 2 ;;
    --project-dir)       PROJECT_DIR="$2";       shift 2 ;;
    --from)              FROM_VERSION="$2";       shift 2 ;;
    --to)                TO_VERSION="$2";         shift 2 ;;
    -h|--help)           usage ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
done

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
if [[ -z "$RELEASE_NOTES_DIR" || -z "$PROJECT_DIR" || -z "$FROM_VERSION" || -z "$TO_VERSION" ]]; then
  echo "Error: All four arguments are required." >&2
  usage
fi

if [[ ! -d "$RELEASE_NOTES_DIR" ]]; then
  echo "Error: --release-notes-dir does not exist: $RELEASE_NOTES_DIR" >&2
  exit 1
fi

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "Error: --project-dir does not exist: $PROJECT_DIR" >&2
  exit 1
fi

# Validate version format: digits optionally followed by 'u' + digits (e.g. 5, 5u13, 6u3)
if ! echo "$FROM_VERSION" | grep -qE '^[0-9]+(u[0-9]+)?$'; then
  echo "Error: Invalid --from version format: $FROM_VERSION (expected e.g. 5u13, 6, 6u3)" >&2
  usage
fi

if ! echo "$TO_VERSION" | grep -qE '^[0-9]+(u[0-9]+)?$'; then
  echo "Error: Invalid --to version format: $TO_VERSION (expected e.g. 5u13, 6, 6u3)" >&2
  usage
fi

# Check jq availability
if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not found. Install jq or ensure it is on PATH." >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Version utilities (implemented in Python for robust comparison)
# ---------------------------------------------------------------------------

# Convert version string "5u13" -> sortable integer 5013, "6" -> 6000, "6u3" -> 6003
version_to_int() {
  python3 -c "
import sys, re
v = sys.argv[1]
m = re.match(r'^(\d+)(?:u(\d+))?$', v)
if not m:
    sys.exit(1)
major = int(m.group(1))
minor = int(m.group(2)) if m.group(2) else 0
print(major * 1000 + minor)
" "$1"
}

FROM_INT=$(version_to_int "$FROM_VERSION")
TO_INT=$(version_to_int "$TO_VERSION")

if [[ "$FROM_INT" -ge "$TO_INT" ]]; then
  echo "Error: --from ($FROM_VERSION) must be less than --to ($TO_VERSION)" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Phase 1: Filter JSON files by version range (exclusive from, inclusive to)
# Files naming pattern: releases-nablarch{major}(u{minor})?-releasenote.json
# We include files where: FROM_INT < file_version_int <= TO_INT
# ---------------------------------------------------------------------------

SELECTED_FILES=()

while IFS= read -r -d '' filepath; do
  filename="$(basename "$filepath")"
  file_ver=$(python3 -c "
import re, sys
m = re.match(r'releases-nablarch(\d+)(u(\d+))?-releasenote\.json', sys.argv[1])
if not m:
    sys.exit(0)
major = int(m.group(1))
minor = int(m.group(3)) if m.group(3) else 0
print(major * 1000 + minor)
" "$filename" 2>/dev/null || true)

  if [[ -z "$file_ver" ]]; then
    continue  # filename does not match the pattern
  fi

  if [[ "$file_ver" -gt "$FROM_INT" && "$file_ver" -le "$TO_INT" ]]; then
    SELECTED_FILES+=("$filepath")
  fi
done < <(find "$RELEASE_NOTES_DIR" -maxdepth 1 -name "releases-nablarch*-releasenote.json" -print0 | sort -z)

if [[ ${#SELECTED_FILES[@]} -eq 0 ]]; then
  echo "# Upgrade Check Results: Nablarch ${FROM_VERSION} → ${TO_VERSION}"
  echo ""
  echo "No release note JSON files found in the specified version range."
  echo "Directory: $RELEASE_NOTES_DIR"
  exit 0
fi

# ---------------------------------------------------------------------------
# Phase 2 & 3: Apply R1-R8 rules using Python for robust text processing
# ---------------------------------------------------------------------------

python3 - "$RELEASE_NOTES_DIR" "$PROJECT_DIR" "$FROM_VERSION" "$TO_VERSION" "${SELECTED_FILES[@]}" <<'PYEOF'
import sys
import os
import re
import json
import subprocess

_, release_notes_dir, project_dir, from_ver, to_ver, *selected_files = sys.argv

# Sort files by version
def file_to_ver(path):
    m = re.search(r'nablarch(\d+)(u(\d+))?-releasenote', os.path.basename(path))
    if not m:
        return 0
    return int(m.group(1)) * 1000 + (int(m.group(3)) if m.group(3) else 0)

selected_files = sorted(selected_files, key=file_to_ver)

# ---------------------------------------------------------------------------
# Rule implementations
# ---------------------------------------------------------------------------

def extract_file_version(path):
    """Extract version string from filename, e.g. '5u13' or '6u3'."""
    m = re.search(r'nablarch(\d+)(u(\d+))?-releasenote', os.path.basename(path))
    if not m:
        return "unknown"
    major = m.group(1)
    minor = m.group(3)
    return f"{major}u{minor}" if minor else major

def r1_hints_match(index_entries):
    """R1: Find section IDs where hints contain 'システムへの影響あり'."""
    matched = []
    for entry in index_entries:
        hints = entry.get("hints", [])
        if any("システムへの影響あり" in h for h in hints):
            matched.append(entry["id"])
    return matched

def r2_title_match(index_entries):
    """R2: Find section IDs where title contains '影響がある変更'."""
    matched = []
    for entry in index_entries:
        title = entry.get("title", "")
        if "影響がある変更" in title:
            matched.append(entry["id"])
    return matched

def r3_warning_blocks(section_text):
    """R3: Extract warning/important blocks from section body.
    Pattern: lines starting with '> **警告**:' or '> **重要**:' etc.
    Returns list of full matched lines.
    """
    pattern = re.compile(r'^> \*\*(警告|重要|Warning|Important)\*\*:.*', re.MULTILINE)
    return [m.group(0) for m in pattern.finditer(section_text)]

def r4_affected_table_rows(section_text):
    """R4: Extract rows from Markdown tables where the 影響 column is 'あり'.
    Column names: 'システムへの影響', '影響', 'システム影響'
    Values matching: 'あり' (including 'あり（開発）', 'あり（本番）')
    Returns list of matched row strings.
    """
    results = []
    lines = section_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Look for a table header row containing an 影響 column
        if "|" in line:
            # Find header
            header_match = re.match(r'\|(.+)\|', line)
            if header_match:
                headers = [h.strip() for h in line.split("|")[1:-1]]
                # Check if any header matches 影響 column pattern
                impact_col_idx = None
                for idx, h in enumerate(headers):
                    # Strip markdown bold/other formatting
                    h_clean = re.sub(r'\*+', '', h).strip()
                    if re.search(r'システムへの影響|^影響$|システム影響', h_clean):
                        impact_col_idx = idx
                        break

                if impact_col_idx is not None:
                    # Skip separator row (---|---|...)
                    i += 1
                    if i < len(lines) and re.match(r'\|[\s\-:|]+\|', lines[i]):
                        i += 1
                    # Process data rows
                    while i < len(lines):
                        row = lines[i].strip()
                        if not row.startswith("|"):
                            break
                        cells = [c.strip() for c in row.split("|")[1:-1]]
                        if impact_col_idx < len(cells):
                            cell = cells[impact_col_idx]
                            # Remove markdown formatting
                            cell_clean = re.sub(r'\*+', '', cell).strip()
                            # Match 'あり' but not 'なし'
                            if re.match(r'あり', cell_clean):
                                results.append(row)
                        i += 1
                    continue
        i += 1
    return results

def r5_extract_fqcns(section_text):
    """R5: Extract FQCNs from backticks in section body.
    Pattern: `com.nablarch.[A-Za-z][A-Za-z0-9._$]*`
    """
    pattern = re.compile(r'`(com\.nablarch\.[A-Za-z][A-Za-z0-9._$]*)`')
    return list(dict.fromkeys(pattern.findall(section_text)))

def r6_extract_config_keys(section_text):
    """R6: Extract config keys from backticks in section body.
    Pattern: `nablarch.[a-z][a-zA-Z0-9._-]*`
    """
    pattern = re.compile(r'`(nablarch\.[a-z][a-zA-Z0-9._-]*)`')
    return list(dict.fromkeys(pattern.findall(section_text)))

def r7_extract_artifact_ids(section_text):
    """R7: Extract Nablarch artifact IDs from table cells.
    Pattern: nablarch-[a-z-]+
    """
    pattern = re.compile(r'\bnablarch-[a-z][a-z-]+\b')
    matches = pattern.findall(section_text)
    return list(dict.fromkeys(matches))

def r8_project_grep(items, project_dir, file_extensions=None):
    """R8: Grep the project directory for each item.
    Returns dict: {item: [matching_file_paths]} or {item: None} on error.
    """
    if file_extensions is None:
        file_extensions = [".java", ".xml", ".properties", ".yaml", ".yml"]

    results = {}
    for item in items:
        try:
            cmd = ["grep", "-rl", "--include=" + ",".join(f"*{ext}" for ext in file_extensions),
                   item, project_dir]
            # Use find + xargs approach for better glob handling
            find_cmd = ["grep", "-rl", item, project_dir,
                        "--include=*.java", "--include=*.xml",
                        "--include=*.properties", "--include=*.yaml",
                        "--include=*.yml"]
            proc = subprocess.run(find_cmd, capture_output=True, text=True, timeout=30)
            if proc.returncode == 0:
                hits = [h.strip() for h in proc.stdout.strip().split("\n") if h.strip()]
                results[item] = hits
            elif proc.returncode == 1:
                results[item] = []  # no match (not an error)
            else:
                results[item] = None  # grep error
        except subprocess.TimeoutExpired:
            results[item] = None
        except Exception:
            results[item] = None
    return results

def r8_pom_grep(artifact_ids, project_dir):
    """R8: Grep pom.xml files for artifact IDs."""
    results = {}
    for aid in artifact_ids:
        try:
            find_cmd = ["grep", "-rl", aid, project_dir, "--include=*.xml"]
            proc = subprocess.run(find_cmd, capture_output=True, text=True, timeout=30)
            if proc.returncode == 0:
                hits = [h.strip() for h in proc.stdout.strip().split("\n") if h.strip()]
                results[aid] = hits
            elif proc.returncode == 1:
                results[aid] = []
            else:
                results[aid] = None
        except subprocess.TimeoutExpired:
            results[aid] = None
        except Exception:
            results[aid] = None
    return results

# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

affected_items = []      # {file_ver, file, section_id, rule, pattern, project_hit}
undecidable_items = []   # {file_ver, file, section_id, reason}
not_affected_count = 0

all_fqcns = []
all_config_keys = []
all_artifact_ids = []

# Store per-file, per-section data for final output
file_section_data = {}  # (file_ver, section_id) -> {fqcns, config_keys, artifact_ids, ...}

for filepath in selected_files:
    file_ver = extract_file_version(filepath)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        undecidable_items.append({
            "file_ver": file_ver,
            "file": os.path.basename(filepath),
            "section_id": "*",
            "reason": f"JSON parse error: {e}"
        })
        continue

    index_entries = data.get("index", [])
    sections = data.get("sections", {})

    # Apply R1 and R2 to find affected section IDs
    r1_sections = set(r1_hints_match(index_entries))
    r2_sections = set(r2_title_match(index_entries))
    candidate_sections = r1_sections | r2_sections

    # Process each section
    for entry in index_entries:
        section_id = entry["id"]
        section_text = sections.get(section_id, "")

        section_key = (file_ver, section_id)
        is_affected_section = section_id in candidate_sections

        # Per-section extracted items
        fqcns = r5_extract_fqcns(section_text)
        config_keys = r6_extract_config_keys(section_text)
        artifact_ids = r7_extract_artifact_ids(section_text)

        all_fqcns.extend(fqcns)
        all_config_keys.extend(config_keys)
        all_artifact_ids.extend(artifact_ids)

        file_section_data[section_key] = {
            "file": os.path.basename(filepath),
            "file_ver": file_ver,
            "section_id": section_id,
            "section_title": entry.get("title", ""),
            "fqcns": fqcns,
            "config_keys": config_keys,
            "artifact_ids": artifact_ids,
        }

        if is_affected_section:
            # R1 match
            if section_id in r1_sections:
                affected_items.append({
                    "file_ver": file_ver,
                    "file": os.path.basename(filepath),
                    "section_id": section_id,
                    "section_title": entry.get("title", ""),
                    "rule": "R1 (hints: システムへの影響あり)",
                    "pattern": "hints contains 'システムへの影響あり'",
                    "project_hit": "",
                    "fqcns": fqcns,
                    "config_keys": config_keys,
                    "artifact_ids": artifact_ids,
                })
            elif section_id in r2_sections:
                affected_items.append({
                    "file_ver": file_ver,
                    "file": os.path.basename(filepath),
                    "section_id": section_id,
                    "section_title": entry.get("title", ""),
                    "rule": "R2 (title: 影響がある変更)",
                    "pattern": "title contains '影響がある変更'",
                    "project_hit": "",
                    "fqcns": fqcns,
                    "config_keys": config_keys,
                    "artifact_ids": artifact_ids,
                })
        else:
            # For non-candidate sections, still check R3 and R4
            r3_matches = r3_warning_blocks(section_text)
            r4_matches = r4_affected_table_rows(section_text)

            if r3_matches:
                affected_items.append({
                    "file_ver": file_ver,
                    "file": os.path.basename(filepath),
                    "section_id": section_id,
                    "section_title": entry.get("title", ""),
                    "rule": "R3 (警告/重要ブロック)",
                    "pattern": r3_matches[0][:80] if r3_matches else "",
                    "project_hit": "",
                    "fqcns": fqcns,
                    "config_keys": config_keys,
                    "artifact_ids": artifact_ids,
                })
            elif r4_matches:
                affected_items.append({
                    "file_ver": file_ver,
                    "file": os.path.basename(filepath),
                    "section_id": section_id,
                    "section_title": entry.get("title", ""),
                    "rule": "R4 (テーブル影響列: あり)",
                    "pattern": r4_matches[0][:80] if r4_matches else "",
                    "project_hit": "",
                    "fqcns": fqcns,
                    "config_keys": config_keys,
                    "artifact_ids": artifact_ids,
                })
            else:
                not_affected_count += 1

    # Also apply R3/R4 to candidate sections (for completeness)
    for section_id in candidate_sections:
        section_text = sections.get(section_id, "")
        # These are already marked as affected; R3/R4 add detail but don't create new entries

# Deduplicate all extracted items
all_fqcns = list(dict.fromkeys(all_fqcns))
all_config_keys = list(dict.fromkeys(all_config_keys))
all_artifact_ids = list(dict.fromkeys(all_artifact_ids))

# ---------------------------------------------------------------------------
# Phase 3: R8 - Project grep
# ---------------------------------------------------------------------------
fqcn_hits = r8_project_grep(all_fqcns, project_dir) if all_fqcns else {}
config_hits = r8_project_grep(all_config_keys, project_dir) if all_config_keys else {}
artifact_hits = r8_pom_grep(all_artifact_ids, project_dir) if all_artifact_ids else {}

def format_project_hits(item, hits_dict):
    """Format project grep results as short paths."""
    hits = hits_dict.get(item)
    if hits is None:
        return "⚠ grep error"
    if not hits:
        return "(no match)"
    # Shorten paths relative to project_dir
    short = []
    for h in hits[:3]:  # limit to 3 for readability
        try:
            rel = os.path.relpath(h, project_dir)
        except ValueError:
            rel = h
        short.append(rel)
    suffix = f" (+{len(hits)-3} more)" if len(hits) > 3 else ""
    return ", ".join(short) + suffix

# Enrich affected_items with R8 project hit info
for item in affected_items:
    hit_parts = []

    # Check FQCNs
    for fqcn in item.get("fqcns", []):
        hits = fqcn_hits.get(fqcn)
        if hits:
            hit_parts.append(f"{fqcn}: {format_project_hits(fqcn, fqcn_hits)}")

    # Check config keys
    for key in item.get("config_keys", []):
        hits = config_hits.get(key)
        if hits:
            hit_parts.append(f"{key}: {format_project_hits(key, config_hits)}")

    # Check artifact IDs
    for aid in item.get("artifact_ids", []):
        hits = artifact_hits.get(aid)
        if hits:
            hit_parts.append(f"{aid}: {format_project_hits(aid, artifact_hits)}")

    if hit_parts:
        item["project_hit"] = "; ".join(hit_parts[:2])  # limit for table width
        if len(hit_parts) > 2:
            item["project_hit"] += f" (+{len(hit_parts)-2} more)"
    else:
        item["project_hit"] = "(no project match)"

# ---------------------------------------------------------------------------
# Phase 4: Output Markdown report
# ---------------------------------------------------------------------------
total_sections = len(affected_items) + len(undecidable_items) + not_affected_count

print(f"# Upgrade Check Results: Nablarch {from_ver} → {to_ver}")
print()
print(f"**Release notes analyzed**: {len(selected_files)} file(s)")
print()
print("## Summary")
print()
print(f"- Affected items (rule-based): {len(affected_items)}")
print(f"- Undecidable items: {len(undecidable_items)}")
print(f"- Not affected: {not_affected_count}")
print(f"- Total sections analyzed: {total_sections}")
print()

# --- Affected Items ---
print("## Affected Items")
print()
if affected_items:
    print("| # | Version | Section | Detection Rule | Matched Pattern | Project Hit |")
    print("|---|---------|---------|----------------|-----------------|-------------|")
    for i, item in enumerate(affected_items, 1):
        section_label = f"{item['section_id']} ({item['section_title'][:30]})" if item.get('section_title') else item['section_id']
        pattern_short = item['pattern'][:60] if item['pattern'] else ""
        print(f"| {i} | {item['file_ver']} | {section_label} | {item['rule']} | {pattern_short} | {item['project_hit']} |")
else:
    print("(No affected items detected by rule-based analysis)")
print()

# --- R5/R6/R7 Extracted Items ---
if all_fqcns or all_config_keys or all_artifact_ids:
    print("## Extracted Technical Items")
    print()

    if all_fqcns:
        print("### FQCNs (R5)")
        print()
        print("| FQCN | Project Hit |")
        print("|------|-------------|")
        for fqcn in all_fqcns:
            print(f"| `{fqcn}` | {format_project_hits(fqcn, fqcn_hits)} |")
        print()

    if all_config_keys:
        print("### Config Keys (R6)")
        print()
        print("| Config Key | Project Hit |")
        print("|------------|-------------|")
        for key in all_config_keys:
            print(f"| `{key}` | {format_project_hits(key, config_hits)} |")
        print()

    if all_artifact_ids:
        print("### Artifact IDs (R7 → pom.xml grep)")
        print()
        print("| Artifact ID | Project Hit |")
        print("|-------------|-------------|")
        for aid in all_artifact_ids:
            print(f"| `{aid}` | {format_project_hits(aid, artifact_hits)} |")
        print()

# --- Undecidable Items ---
print("## Undecidable Items (requires LLM evaluation)")
print()
if undecidable_items:
    print("| # | Version | Section | Reason |")
    print("|---|---------|---------|--------|")
    for i, item in enumerate(undecidable_items, 1):
        print(f"| {i} | {item['file_ver']} | {item['section_id']} | {item['reason']} |")
else:
    print("(No undecidable items)")
print()

# --- Not Affected ---
print("## Not Affected")
print()
if not_affected_count > 0:
    print(f"{not_affected_count} section(s) had no rule-based matches and are considered not affected.")
else:
    print("(All sections were classified by rule-based analysis)")
print()

# --- Footer ---
print("---")
print()
print("**Notes**:")
print("- 'Affected Items' are sections where R1-R4 detected impact signals.")
print("- 'Project Hit' shows whether R5/R6/R7 extracted items were found in the project source.")
print("- Sections with no R1-R4 signal and no project hits are marked as 'Not Affected'.")
print("- Items requiring human/LLM review (e.g. implicit impacts, conditional changes) are listed under 'Undecidable'.")

PYEOF
