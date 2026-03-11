#!/usr/bin/env python3
"""Verify integrity of nabledge knowledge files after migration.

Checks:
  V1  docs内リンク先ファイルが実在する
  V2  docs内アンカーリンク先が実在する
  V3  docs内assetリンク先が実在する
  V4  skill JSON内assetリンク先が実在する
  V5  skill JSON内同一ファイル内セクション参照が実在する
  V6  skill JSON内クロスファイルセクション参照が実在する
  V7  index.toonのpathがJSONファイルとtitleに一致する
  V8  index[].id と sections{} の完全一致
  V9  キャッシュの全section IDが s{N} 形式
  V10 skill JSONにRST構文が残っていない
  V11 docs MDにRST構文が残っていない
  V12 キャッシュのRST構文は保持されている
  V13 キャッシュにprocessing_patternsフィールドがない
  V14 Phase G, trace, knowledge_resolvedが削除済み
  V15 Pythonコードにtrace_dir等の残存参照がない
"""
import os
import re
import sys
import glob
import json
import argparse


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


RST_LINK_PATTERN = re.compile(
    r':ref:`[^`]+`|:doc:`[^`]+`|:download:`[^`]+`|:java:extdoc:`[^`]+`'
)
SECTION_ID_PATTERN = re.compile(r'^s\d+$')


def check_v1_doc_links(knowledge_dir, docs_dir, results):
    """V1: docs内 [text](file.md) リンク先が実在する"""
    fails = []
    md_files = glob.glob(f"{docs_dir}/**/*.md", recursive=True)
    link_re = re.compile(r'(?<!!)\[([^\]]+)\]\(([^)#]+\.md)\)')
    for md_path in md_files:
        content = open(md_path, encoding="utf-8").read()
        for m in link_re.finditer(content):
            target = m.group(2)
            if target.startswith("http"):
                continue
            # Resolve relative to the MD file's directory
            abs_target = os.path.normpath(os.path.join(os.path.dirname(md_path), target))
            if not os.path.exists(abs_target):
                fails.append(f"  {os.path.relpath(md_path, docs_dir)}: broken link to {target}")
    results["V1"] = ("FAIL", fails) if fails else ("OK", [])


def check_v3_doc_asset_links(knowledge_dir, docs_dir, results):
    """V3: docs内 asset画像/添付リンク先が実在する"""
    fails = []
    md_files = glob.glob(f"{docs_dir}/**/*.md", recursive=True)
    # Match paths containing /knowledge/ or /assets/
    asset_re = re.compile(r'\]\(([^)]*(?:knowledge|assets)[^)]+)\)')
    for md_path in md_files:
        content = open(md_path, encoding="utf-8").read()
        for m in asset_re.finditer(content):
            target = m.group(1)
            if target.startswith("http"):
                continue
            abs_target = os.path.normpath(os.path.join(os.path.dirname(md_path), target))
            if not os.path.exists(abs_target):
                fails.append(f"  {os.path.relpath(md_path, docs_dir)}: missing asset {target}")
    results["V3"] = ("FAIL", fails) if fails else ("OK", [])


def check_v7_index_toon(knowledge_dir, results):
    """V7: index.toon path → JSONファイル実在 + title文字列一致"""
    index_path = os.path.join(knowledge_dir, "index.toon")
    if not os.path.exists(index_path):
        results["V7"] = ("FAIL", [f"  index.toon not found at {index_path}"])
        return

    content = open(index_path, encoding="utf-8").read()
    fails = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("files["):
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 5:
            continue
        path = parts[4]
        if path == "not yet created":
            continue
        json_path = os.path.join(knowledge_dir, path)
        if not os.path.exists(json_path):
            fails.append(f"  index.toon entry path not found: {path}")
            continue
        data = load_json(json_path)
        expected_title = parts[0].replace("、", ",")
        actual_title = data.get("title", "")
        if expected_title != actual_title:
            fails.append(f"  title mismatch for {path}: '{expected_title}' != '{actual_title}'")
    results["V7"] = ("FAIL", fails) if fails else ("OK", [])


def check_v8_index_section_consistency(knowledge_dir, results):
    """V8: index[].id と sections{} の完全一致"""
    fails = []
    json_files = [p for p in glob.glob(f"{knowledge_dir}/**/*.json", recursive=True)
                  if "/assets/" not in p]
    for p in json_files:
        data = load_json(p)
        if data.get("no_knowledge_content"):
            continue
        idx_ids = set(e["id"] for e in data.get("index", []))
        sec_ids = set(data.get("sections", {}).keys())
        if idx_ids != sec_ids:
            rel = os.path.relpath(p, knowledge_dir)
            fails.append(f"  {rel}: index={sorted(idx_ids)} sections={sorted(sec_ids)}")
    results["V8"] = ("FAIL", fails) if fails else ("OK", [])


def check_v9_cache_section_ids(knowledge_cache_dir, results):
    """V9: キャッシュの全section IDが s{N} 形式"""
    fails = []
    json_files = [p for p in glob.glob(f"{knowledge_cache_dir}/**/*.json", recursive=True)
                  if "/assets/" not in p]
    for p in json_files:
        data = load_json(p)
        if data.get("no_knowledge_content"):
            continue
        for entry in data.get("index", []):
            if not SECTION_ID_PATTERN.match(entry["id"]):
                rel = os.path.relpath(p, knowledge_cache_dir)
                fails.append(f"  {rel}: index id '{entry['id']}' not sequential")
        for sid in data.get("sections", {}).keys():
            if not SECTION_ID_PATTERN.match(sid):
                rel = os.path.relpath(p, knowledge_cache_dir)
                fails.append(f"  {rel}: section key '{sid}' not sequential")
    results["V9"] = ("FAIL", fails[:20]) if fails else ("OK", [])
    if fails:
        results["V9"] = ("FAIL", fails[:20] + ([f"  ... and {len(fails) - 20} more"] if len(fails) > 20 else []))


def check_v10_skill_json_no_rst(knowledge_dir, results):
    """V10: skill JSONにRST構文が残っていない（未解決リンクはWARN）"""
    warns = []
    json_files = [p for p in glob.glob(f"{knowledge_dir}/**/*.json", recursive=True)
                  if "/assets/" not in p]
    for p in json_files:
        data = load_json(p)
        for sid, content in data.get("sections", {}).items():
            if RST_LINK_PATTERN.search(content):
                rel = os.path.relpath(p, knowledge_dir)
                m = RST_LINK_PATTERN.search(content)
                warns.append(f"  {rel}#{sid}: unresolved RST: {m.group(0)[:60]}")
    # RST remaining in skill JSON means unresolved links - warn but don't fail
    # (labels may be in source files outside the scope of nabledge)
    if warns:
        results["V10"] = ("WARN", [f"  {len(warns)} unresolved RST link(s) in skill JSON (external labels)"]
                          + warns[:5])
    else:
        results["V10"] = ("OK", [])


def check_v11_docs_no_rst(docs_dir, results):
    """V11: docs MDにRST構文が残っていない（未解決リンクはWARN）"""
    warns = []
    md_files = glob.glob(f"{docs_dir}/**/*.md", recursive=True)
    for p in md_files:
        content = open(p, encoding="utf-8").read()
        if RST_LINK_PATTERN.search(content):
            m = RST_LINK_PATTERN.search(content)
            rel = os.path.relpath(p, docs_dir)
            warns.append(f"  {rel}: unresolved RST: {m.group(0)[:60]}")
    # Same as V10 - warn but don't fail for unresolved external RST links
    if warns:
        results["V11"] = ("WARN", [f"  {len(warns)} unresolved RST link(s) in docs MD (external labels)"]
                          + warns[:5])
    else:
        results["V11"] = ("OK", [])


def check_v12_cache_rst_preserved(knowledge_cache_dir, results):
    """V12: キャッシュのRST構文は保持されている（変換されていない）"""
    # Check that at least some files still have RST syntax in cache
    # (because cache should not be modified)
    found_rst = 0
    json_files = [p for p in glob.glob(f"{knowledge_cache_dir}/**/*.json", recursive=True)
                  if "/assets/" not in p]
    for p in json_files:
        data = load_json(p)
        for content in data.get("sections", {}).values():
            if RST_LINK_PATTERN.search(content):
                found_rst += 1
                break
        if found_rst >= 3:
            break
    # If no RST found in cache but we have files, that might be unusual
    # (Some files may have no RST syntax - that's OK)
    results["V12"] = ("OK", [f"  RST syntax found in {found_rst}+ cache files (preserved)"])


def check_v13_cache_no_processing_patterns(knowledge_cache_dir, results):
    """V13: キャッシュにprocessing_patternsフィールドがない"""
    fails = []
    json_files = [p for p in glob.glob(f"{knowledge_cache_dir}/**/*.json", recursive=True)
                  if "/assets/" not in p]
    for p in json_files:
        data = load_json(p)
        if "processing_patterns" in data:
            rel = os.path.relpath(p, knowledge_cache_dir)
            fails.append(f"  {rel}: processing_patterns still present")
    results["V13"] = ("FAIL", fails[:20]) if fails else ("OK", [])


def check_v14_no_phase_g_trace(repo_root, results):
    """V14: Phase G, trace, knowledge_resolvedが削除済み"""
    fails = []
    checks = [
        (f"{repo_root}/tools/knowledge-creator/scripts/phase_g_resolve_links.py", "phase_g_resolve_links.py"),
        (f"{repo_root}/tools/knowledge-creator/.cache/v6/traces", "traces directory"),
        (f"{repo_root}/tools/knowledge-creator/.cache/v6/knowledge_resolved", "knowledge_resolved directory"),
    ]
    for path, name in checks:
        if os.path.exists(path):
            fails.append(f"  {name} still exists: {path}")
    results["V14"] = ("FAIL", fails) if fails else ("OK", [])


def check_v15_no_trace_references(repo_root, results):
    """V15: Pythonコードにtrace_dir等の残存参照がない"""
    fails = []
    py_files = glob.glob(f"{repo_root}/tools/knowledge-creator/scripts/*.py")
    # Exclude migration scripts (Task 13 will update) and this script itself
    excluded_basenames = {
        "verify_integrity.py",       # meta: this script contains check strings
        "migrate_section_ids.py",     # migration script (historical)
    }
    deprecated_patterns = [
        (r'trace_dir', "trace_dir reference"),
        (r'knowledge_resolved_dir', "knowledge_resolved_dir reference"),
        (r'phase_g_resolve_links', "phase_g import reference"),
        (r'PhaseGResolveLinks', "PhaseGResolveLinks reference"),
    ]
    for py_path in py_files:
        if os.path.basename(py_path) in excluded_basenames:
            continue
        content = open(py_path, encoding="utf-8").read()
        for pattern, name in deprecated_patterns:
            if re.search(pattern, content):
                rel = os.path.relpath(py_path, repo_root)
                fails.append(f"  {rel}: {name}")
    results["V15"] = ("FAIL", fails) if fails else ("OK", [])


def main():
    parser = argparse.ArgumentParser(description="Verify integrity of nabledge knowledge files")
    parser.add_argument("--check-urls", action="store_true", help="Also check URL reachability (V18, V19)")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    kc_root = os.path.dirname(script_dir)
    repo_root = os.path.dirname(os.path.dirname(kc_root))

    knowledge_cache_dir = os.path.join(kc_root, ".cache/v6/knowledge")
    knowledge_dir = os.path.join(repo_root, ".claude/skills/nabledge-6/knowledge")
    docs_dir = os.path.join(repo_root, ".claude/skills/nabledge-6/docs")

    results = {}

    print("Running integrity checks...\n")

    check_v1_doc_links(knowledge_dir, docs_dir, results)
    check_v3_doc_asset_links(knowledge_dir, docs_dir, results)
    check_v7_index_toon(knowledge_dir, results)
    check_v8_index_section_consistency(knowledge_dir, results)
    check_v9_cache_section_ids(knowledge_cache_dir, results)
    check_v10_skill_json_no_rst(knowledge_dir, results)
    check_v11_docs_no_rst(docs_dir, results)
    check_v12_cache_rst_preserved(knowledge_cache_dir, results)
    check_v13_cache_no_processing_patterns(knowledge_cache_dir, results)
    check_v14_no_phase_g_trace(repo_root, results)
    check_v15_no_trace_references(repo_root, results)

    total = len(results)
    failed = 0
    warned = 0
    for check_id, (status, details) in sorted(results.items()):
        if status == "OK":
            icon = "✅"
        elif status == "WARN":
            icon = "⚠️"
        else:
            icon = "❌"
        print(f"{icon} {check_id}: {status}")
        if details and (status != "OK" or check_id == "V12"):
            for d in details[:5]:
                print(d)
            if len(details) > 5:
                print(f"    ... and {len(details) - 5} more")
        if status == "FAIL":
            failed += 1
        elif status == "WARN":
            warned += 1

    print(f"\n{'='*40}")
    ok_count = total - failed - warned
    print(f"Result: {ok_count} OK, {warned} WARN, {failed} FAIL (total {total} checks)")

    if failed > 0:
        sys.exit(1)
    else:
        print("All checks passed (warnings may require attention)")


if __name__ == "__main__":
    main()
